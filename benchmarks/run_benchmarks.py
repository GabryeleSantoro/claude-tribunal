#!/usr/bin/env python3
"""
Local Tribunal benchmarks: token usage, wall time, heuristic quality rubric.

Backends:

  Anthropic (default): needs ANTHROPIC_API_KEY. Model id examples: ``claude-sonnet-4-20250514``.

  OpenRouter: needs OPENROUTER_API_KEY. Use ``--backend openrouter`` and an OpenRouter
  model slug (examples: ``anthropic/claude-sonnet-4``). Chat Completions API via
  https://openrouter.ai/api/v1 .

  cd benchmarks && pip install -r requirements.txt

Optional ``benchmarks/.env`` loads KEY=value lines into the environment if unset.

Outputs go under ``benchmarks/.local/`` (gitignored).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None  # type: ignore

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore

MODEL_DEFAULT_ANTHROPIC = "claude-sonnet-4-20250514"
MODEL_DEFAULT_OPENROUTER = "anthropic/claude-sonnet-4"
BENCH_ROOT = Path(__file__).resolve().parent
REPO_ROOT = BENCH_ROOT.parent
LOCAL_DIR = BENCH_ROOT / ".local"
RESULTS_DIR = LOCAL_DIR / "results"
CASES_PATH = BENCH_ROOT / "cases.json"
SKILL_PATH = REPO_ROOT / "skills" / "deliberate" / "SKILL.md"

USER_WRAP = """Simulate Tribunal as if invoked inside Claude Code with this exact line (treat flags and topic literally):

`/tribunal:deliberate {arguments}`

Rules:
- Produce **only** the Markdown that would go in the tribunal verdict file body (starting with `## ⚖️ Tribunal Verdict`).
- Honor **depth**, **full log** (`--full-log`): if `--full-log` appears, use the **full** skeleton from the skill; otherwise use the **compact** skeleton.
- If `--export json` is present, append `### Export (JSON)` plus a fenced JSON block as specified in the skill.
- Respect `--domain` / `--min-confidence` if present (Decision wording when gate fails).
- Do **not** reference writing to disk paths; omit the file preamble line (**Invocation:**).
- Respond in English unless the topic asks otherwise.

Begin the Markdown verdict now."""

CORRECTNESS_JUDGE_TEMPLATE = """You grade a Tribunal verdict for DECISION CORRECTNESS against a known ground truth (not prose polish or structure).

You are given the topic, the model's verdict, and the ground truth for this case.

Ground truth:
- expected_direction: {expected_direction}  (support | reject | split — the defensible sign of the verdict)
- expected_confidence_band: {expected_confidence_band}  (high>=70 | moderate 40-69 | low<40, for weighted consensus strength)
- must_surface (facts/risks a correct verdict must mention): {must_surface}
- failure_if (red flags that mean the verdict is wrong): {failure_if}
- rationale: {rationale}

Judge strictly:
- direction_match: does the verdict's Decision direction match expected_direction? (a "split"/conditional Decision matches "split")
- confidence_band_ok: is the reported Confidence in the expected band?
- surfaced: how many must_surface items are clearly addressed, as "X/total"
- failure_triggered: did ANY failure_if red flag occur? (true = the verdict is wrong)
- correctness: integer 0-100 overall. If failure_triggered is true, this MUST be <= 30.

Respond with JSON only, no markdown fence:
{{"direction_match": bool, "confidence_band_ok": bool, "surfaced": string, "failure_triggered": bool, "correctness": int, "note": string}}

---

Topic line (truncated invocation):
{arguments}

---

Model verdict:
{output}
"""

JUDGE_USER_TEMPLATE = """You grade a Tribunal markdown output for fidelity to protocol (not factual correctness).

Rubric (0–100 integer each, be strict):
- structure: Required sections present and labeled (compact vs full per instructions)
- verdict_math: Visible votes with confidence + position (and lean when conditional); Reasoning Trail mentions v_i / bar notation or equivalent audit
- topic_fit: Addresses the user's topic with concrete recommendation

Respond with JSON only, no markdown fence:
{{"structure": int, "verdict_math": int, "topic_fit": int, "note": string}}

---

Topic line (truncated invocation):
{arguments}

---

Model output:
{output}
"""


def _load_dotenv_fallback() -> None:
    env_file = BENCH_ROOT / ".env"
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


@dataclass
class BenchmarkResult:
    run_id: str
    case_id: str
    case_description: str
    arguments: str
    provider: str
    model: str
    skill_chars: int
    elapsed_seconds: float
    input_tokens: int | None
    output_tokens: int | None
    quality_score_0_100: float
    quality_breakdown: dict[str, Any]
    judge_scores: dict[str, Any] | None
    judge_input_tokens: int | None
    judge_output_tokens: int | None
    error: str | None


def load_cases(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    # cases.json is a bare list; ground-truth.json wraps cases under a "cases" key.
    if isinstance(data, dict) and isinstance(data.get("cases"), list):
        return data["cases"]
    if not isinstance(data, list):
        raise ValueError("cases file must be a list, or an object with a 'cases' list")
    return data


def load_skill(use_skill_file: bool) -> str:
    if not use_skill_file:
        return (
            "You are the Tribunal orchestrator. Follow a simplified protocol: "
            "five personas, cross-examination ring, weighted votes with v_i mapping, compact or full Markdown skeleton "
            "as specified in the user message."
        )
    if not SKILL_PATH.is_file():
        raise FileNotFoundError(f"Skill not found at {SKILL_PATH}")
    return SKILL_PATH.read_text(encoding="utf-8")


def rubric_quality(text: str, full_log_requested: bool) -> tuple[float, dict[str, Any]]:
    t = text
    lows = t.lower()

    marks: dict[str, bool | float | int | str] = {
        "has_verdict_header": "## ⚖️ tribunal verdict" in lows,
        "has_decision": "**decision:**" in lows,
        "has_confidence_line": bool(re.search(r"\*\*confidence:\*\*\s*\d+", lows)),
        "has_votes_section": "### votes" in lows or lows.count("votes") >= 2,
        "has_reasoning_trail": "reasoning trail" in lows,
        "has_session_marker": "**session id:**" in lows or "**session ID:**".lower() in lows,
        "five_vote_signals": sum(
            1 for s in ["domain expert", "devil", "systems thinker", "logician", "mediator"] if s in lows
        ),
    }
    if full_log_requested:
        marks["has_panel"] = "### panel" in lows
        marks["has_cross_exam"] = "cross-exam" in lows or "cross examination" in lows
    else:
        marks["has_panel"] = True
        marks["has_cross_exam"] = True

    persona_score = min(10, int(marks["five_vote_signals"]) * 2)
    del marks["five_vote_signals"]
    marks["five_personas_coverage"] = persona_score

    score = 0.0
    score += 15 if marks["has_verdict_header"] else 0
    score += 20 if marks["has_decision"] else 0
    score += 15 if marks["has_confidence_line"] else 0
    score += 15 if marks["has_votes_section"] else 0
    score += 15 if marks["has_reasoning_trail"] else 0
    score += 5 if marks["has_session_marker"] else 0
    score += persona_score
    score += 3 if marks["has_panel"] else 0
    score += 2 if marks["has_cross_exam"] else 0

    return round(score, 2), marks


def _resolve_model(explicit_model: str, provider: str) -> str:
    if explicit_model.strip():
        return explicit_model.strip()
    env_any = (
        os.environ.get("TRIBUNAL_BENCHMARK_MODEL", "").strip()
        or os.environ.get("OPENROUTER_BENCHMARK_MODEL", "").strip()
    )
    if env_any:
        return env_any
    return MODEL_DEFAULT_ANTHROPIC if provider == "anthropic" else MODEL_DEFAULT_OPENROUTER


def run_inference_anthropic(
    client: Any,
    model: str,
    skill_body: str,
    user_text: str,
    max_tokens: int,
    use_prompt_cache: bool,
) -> tuple[str | None, str, int | None, int | None]:
    system_arg: Any = skill_body
    if use_prompt_cache:
        system_arg = [
            {"type": "text", "text": skill_body, "cache_control": {"type": "ephemeral"}},
        ]
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_arg,  # type: ignore[arg-type]
        messages=[{"role": "user", "content": user_text}],
    )
    usage_in = getattr(msg.usage, "input_tokens", None)
    usage_out = getattr(msg.usage, "output_tokens", None)
    text_out = "".join(block.text for block in msg.content if getattr(block, "type", None) == "text")
    return None, text_out, usage_in, usage_out


def run_inference_openrouter(
    client: Any,
    model: str,
    skill_body: str,
    user_text: str,
    max_tokens: int,
    temperature: float,
) -> tuple[str | None, str, int | None, int | None]:
    resp = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": skill_body},
            {"role": "user", "content": user_text},
        ],
    )
    choice = resp.choices[0].message.content
    text_out = (choice if isinstance(choice, str) else "") or ""
    usage = getattr(resp, "usage", None)
    usage_in = getattr(usage, "prompt_tokens", None) if usage else None
    usage_out = getattr(usage, "completion_tokens", None) if usage else None
    return None, text_out, usage_in, usage_out


def run_judge_anthropic(
    client: Any,
    model: str,
    arguments: str,
    assistant_text: str,
) -> tuple[dict[str, Any] | None, int | None, int | None]:
    msg = client.messages.create(
        model=model,
        max_tokens=700,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": JUDGE_USER_TEMPLATE.format(arguments=arguments, output=assistant_text[:120_000]),
            }
        ],
    )
    usage_in = getattr(msg.usage, "input_tokens", None)
    usage_out = getattr(msg.usage, "output_tokens", None)
    text = "".join(block.text for block in msg.content if getattr(block, "type", None) == "text")
    return _parse_judge_json(text), usage_in, usage_out


def run_judge_openrouter(
    client: Any,
    model: str,
    arguments: str,
    assistant_text: str,
) -> tuple[dict[str, Any] | None, int | None, int | None]:
    resp = client.chat.completions.create(
        model=model,
        max_tokens=700,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": JUDGE_USER_TEMPLATE.format(arguments=arguments, output=assistant_text[:120_000]),
            }
        ],
    )
    usage = getattr(resp, "usage", None)
    usage_in = getattr(usage, "prompt_tokens", None) if usage else None
    usage_out = getattr(usage, "completion_tokens", None) if usage else None
    raw = resp.choices[0].message.content or ""
    return _parse_judge_json(raw), usage_in, usage_out


def _parse_judge_json(text: str) -> dict[str, Any] | None:
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return {"raw": text[:2000], "parse_error": True}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"raw": text[:2000], "parse_error": True}


def _correctness_prompt(case: dict[str, Any], arguments: str, output: str) -> str:
    gt = case.get("ground_truth", {}) or {}
    return CORRECTNESS_JUDGE_TEMPLATE.format(
        expected_direction=gt.get("expected_direction", "?"),
        expected_confidence_band=gt.get("expected_confidence_band", "?"),
        must_surface="; ".join(gt.get("must_surface", []) or []),
        failure_if="; ".join(gt.get("failure_if", []) or []),
        rationale=gt.get("rationale", ""),
        arguments=arguments,
        output=output[:120_000],
    )


def run_correctness_judge(
    client: Any,
    backend: str,
    model: str,
    case: dict[str, Any],
    arguments: str,
    output: str,
) -> tuple[dict[str, Any] | None, int | None, int | None]:
    prompt = _correctness_prompt(case, arguments, output)
    if backend == "anthropic":
        msg = client.messages.create(
            model=model,
            max_tokens=700,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        usage_in = getattr(msg.usage, "input_tokens", None)
        usage_out = getattr(msg.usage, "output_tokens", None)
        text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
        return _parse_judge_json(text), usage_in, usage_out
    resp = client.chat.completions.create(
        model=model,
        max_tokens=700,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    usage = getattr(resp, "usage", None)
    usage_in = getattr(usage, "prompt_tokens", None) if usage else None
    usage_out = getattr(usage, "completion_tokens", None) if usage else None
    raw = resp.choices[0].message.content or ""
    return _parse_judge_json(raw), usage_in, usage_out


def main() -> int:
    _load_dotenv_fallback()

    _env_backend = os.environ.get("TRIBUNAL_BENCHMARK_BACKEND", "anthropic").strip().lower()
    if _env_backend not in ("anthropic", "openrouter"):
        _env_backend = "anthropic"

    parser = argparse.ArgumentParser(description="Run local Tribunal benchmarks (tokens, latency, rubric score).")
    parser.add_argument(
        "--backend",
        choices=("anthropic", "openrouter"),
        default=_env_backend,
        help="Inference provider (env TRIBUNAL_BENCHMARK_BACKEND).",
    )
    parser.add_argument(
        "--openrouter-base-url",
        default=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").strip(),
        help="Chat Completions base URL for OpenRouter.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=float(os.environ.get("TRIBUNAL_BENCHMARK_TEMPERATURE", "1")),
        help="Sampling temperature (OpenRouter / Chat API; Anthropic ignores this). Default 1.",
    )
    parser.add_argument(
        "--model",
        default="",
        metavar="MODEL",
        help=(
            "Model id: Anthropic Messages id, or OpenRouter slug (provider/model). "
            "Default: env TRIBUNAL_BENCHMARK_MODEL or OPENROUTER_BENCHMARK_MODEL or a built‑in default per backend."
        ),
    )
    parser.add_argument(
        "--judge-model",
        default="",
        help="If set (or env TRIBUNAL_BENCHMARK_JUDGE_MODEL), run a second grading call; use a model id valid for the chosen backend.",
    )
    parser.add_argument(
        "--no-skill-file",
        action="store_true",
        help="Do not load skills/deliberate/SKILL.md (smaller prompt, less realistic token count).",
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=CASES_PATH,
        help="Path to cases.json",
    )
    parser.add_argument(
        "--ground-truth",
        type=Path,
        default=None,
        metavar="PATH",
        help=(
            "Run the ground-truth correctness set instead of --cases. Cases with a 'ground_truth' "
            "block get a correctness judge (needs --judge-model) grading decision direction, confidence "
            "band, surfaced facts, and failure triggers. Try skills/deliberate/evals/ground-truth.json."
        ),
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=int(os.environ.get("TRIBUNAL_BENCHMARK_MAX_TOKENS", "8192")),
        help="Max output tokens per benchmark call.",
    )
    parser.add_argument(
        "--no-prompt-cache",
        action="store_true",
        help="Send system instructions as a plain string (no ephemeral cache_control block).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned calls without invoking the API.",
    )
    args = parser.parse_args()
    backend = args.backend
    resolved_model = _resolve_model(args.model, backend)

    if not args.dry_run:
        if backend == "anthropic" and Anthropic is None:
            print("Install anthropic: pip install -r benchmarks/requirements.txt", file=sys.stderr)
            return 1
        if backend == "openrouter" and OpenAI is None:
            print("Install openai SDK: pip install -r benchmarks/requirements.txt", file=sys.stderr)
            return 1

    anthropic_client: Any = None
    openrouter_client: Any = None

    if not args.dry_run:
        if backend == "anthropic":
            anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
            if not anthropic_api_key:
                print("Set ANTHROPIC_API_KEY (or benchmarks/.env).", file=sys.stderr)
                return 1
            anthropic_client = Anthropic(api_key=anthropic_api_key)
        else:
            openrouter_api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
            if not openrouter_api_key:
                print("Set OPENROUTER_API_KEY (or benchmarks/.env).", file=sys.stderr)
                return 1
            hdrs: dict[str, str] = {}
            referrer = (
                os.environ.get("OPENROUTER_HTTP_REFERRER", "").strip()
                or os.environ.get("OPENROUTER_SITE_URL", "").strip()
            )
            if referrer:
                hdrs["HTTP-Referer"] = referrer
            if app_name := os.environ.get("OPENROUTER_APP_NAME", "").strip():
                hdrs["X-Title"] = app_name
            openrouter_client = OpenAI(
                api_key=openrouter_api_key,
                base_url=args.openrouter_base_url.rstrip("/"),
                default_headers=hdrs or None,  # type: ignore[arg-type]
            )

    cases_path = args.ground_truth or args.cases
    cases = load_cases(cases_path)
    skill_body = load_skill(use_skill_file=not args.no_skill_file)

    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    batch_path = RESULTS_DIR / f"benchmark-{batch_id}.jsonl"

    judge_model = (args.judge_model or "").strip() or os.environ.get(
        "TRIBUNAL_BENCHMARK_JUDGE_MODEL", ""
    ).strip()

    planned: list[BenchmarkResult] = []

    use_anthropic_cache = backend == "anthropic" and not args.no_prompt_cache

    for case in cases:
        cid = case.get("id", "unknown")
        desc = case.get("description", "")
        inv = str(case.get("arguments", "")).strip()
        full_log = "--full-log" in inv or "--verbose" in inv

        user_text = USER_WRAP.format(arguments=inv)

        if args.dry_run:
            print(f"[dry-run][{backend}] {cid}: {resolved_model}: {inv[:80]}…")
            continue

        t0 = time.perf_counter()
        err: str | None = None
        usage_in: int | None = None
        usage_out: int | None = None
        text_out = ""
        try:
            if backend == "anthropic":
                infer_err, text_out, usage_in, usage_out = run_inference_anthropic(
                    anthropic_client,
                    resolved_model,
                    skill_body,
                    user_text,
                    args.max_tokens,
                    use_anthropic_cache,
                )
                err = infer_err
            else:
                infer_err, text_out, usage_in, usage_out = run_inference_openrouter(
                    openrouter_client,
                    resolved_model,
                    skill_body,
                    user_text,
                    args.max_tokens,
                    args.temperature,
                )
                err = infer_err
        except Exception as e:  # noqa: BLE001
            err = str(e)
        elapsed = time.perf_counter() - t0

        judge_scores: dict[str, Any] | None = None
        judge_in: int | None = None
        judge_out: int | None = None
        if err is None and judge_model:
            try:
                if backend == "anthropic":
                    judge_scores, judge_in, judge_out = run_judge_anthropic(
                        anthropic_client, judge_model, inv, text_out
                    )
                else:
                    judge_scores, judge_in, judge_out = run_judge_openrouter(
                        openrouter_client, judge_model, inv, text_out
                    )
            except Exception as e:  # noqa: BLE001
                judge_scores = {"error": str(e)}

        # Correctness judge: only for ground-truth cases, only when a judge model is set.
        if err is None and judge_model and case.get("ground_truth"):
            try:
                client = anthropic_client if backend == "anthropic" else openrouter_client
                corr, corr_in, corr_out = run_correctness_judge(
                    client, backend, judge_model, case, inv, text_out
                )
                judge_scores = dict(judge_scores or {})
                judge_scores["correctness"] = corr
                judge_in = (judge_in or 0) + (corr_in or 0)
                judge_out = (judge_out or 0) + (corr_out or 0)
            except Exception as e:  # noqa: BLE001
                judge_scores = dict(judge_scores or {})
                judge_scores["correctness"] = {"error": str(e)}

        q_score = 0.0
        q_break: dict[str, Any] = {}
        if err is None:
            q_score, q_break = rubric_quality(text_out, full_log_requested=full_log)

        rec = BenchmarkResult(
            run_id=batch_id,
            case_id=str(cid),
            case_description=str(desc),
            arguments=inv,
            provider=backend,
            model=resolved_model,
            skill_chars=len(skill_body),
            elapsed_seconds=round(elapsed, 3),
            input_tokens=usage_in,
            output_tokens=usage_out,
            quality_score_0_100=q_score,
            quality_breakdown=q_break,
            judge_scores=judge_scores,
            judge_input_tokens=judge_in,
            judge_output_tokens=judge_out,
            error=err,
        )
        planned.append(rec)

        line = json.dumps(asdict(rec), ensure_ascii=False)
        with batch_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

        extra = ""
        if usage_in is not None and usage_out is not None:
            extra = f" tokens in={usage_in} out={usage_out}"
        status = "ERR" if err else "OK"
        corr_str = ""
        corr = (judge_scores or {}).get("correctness") if isinstance(judge_scores, dict) else None
        if isinstance(corr, dict) and "correctness" in corr:
            dm = "✓" if corr.get("direction_match") else "✗"
            fail = " FAIL" if corr.get("failure_triggered") else ""
            corr_str = f" correctness={corr.get('correctness')} dir={dm}{fail}"
        print(f"[{status}] {cid}{extra} time={elapsed:.2f}s quality={q_score}{corr_str}")

    if args.dry_run:
        print(f"Would write to {batch_path}")
        return 0

    summary = {
        "batch_id": batch_id,
        "provider": backend,
        "model": resolved_model,
        "openrouter_base_url": args.openrouter_base_url if backend == "openrouter" else None,
        "judge_model": judge_model or None,
        "results_path": str(batch_path),
        "count": len(planned),
        "mean_time_s": round(sum(r.elapsed_seconds for r in planned) / max(1, len(planned)), 3),
        "mean_quality": round(sum(r.quality_score_0_100 for r in planned) / max(1, len(planned)), 2),
        "total_input_tokens": sum((r.input_tokens or 0) for r in planned),
        "total_output_tokens": sum((r.output_tokens or 0) for r in planned),
        "total_judge_input_tokens": sum((r.judge_input_tokens or 0) for r in planned),
        "total_judge_output_tokens": sum((r.judge_output_tokens or 0) for r in planned),
        "errors": sum(1 for r in planned if r.error),
    }

    # Correctness aggregates (ground-truth runs only).
    corr_recs = [
        r.judge_scores["correctness"]
        for r in planned
        if isinstance(r.judge_scores, dict)
        and isinstance(r.judge_scores.get("correctness"), dict)
        and "correctness" in r.judge_scores["correctness"]
    ]
    if corr_recs:
        summary["correctness_cases"] = len(corr_recs)
        summary["mean_correctness"] = round(
            sum(int(c.get("correctness", 0)) for c in corr_recs) / len(corr_recs), 2
        )
        summary["direction_match_rate"] = round(
            sum(1 for c in corr_recs if c.get("direction_match")) / len(corr_recs), 2
        )
        summary["failures_triggered"] = sum(1 for c in corr_recs if c.get("failure_triggered"))
    summary_path = RESULTS_DIR / f"summary-{batch_id}.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["errors"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
