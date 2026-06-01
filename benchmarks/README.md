# Tribunal benchmarks

Local measurement harness for the `tribunal:deliberate` skill: **token usage**, **wall time**, a **heuristic protocol-fidelity rubric**, and an optional **LLM judge** (protocol fidelity *or* decision correctness).

Results write to `benchmarks/.local/results/` (gitignored). The harness itself is public so the numbers in the project [README](../README.md#-benchmarks) are reproducible.

## Setup

```bash
cd benchmarks
python3 -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
python run_benchmarks.py --dry-run                   # plan cases only, no API key
```

## Run

```bash
# Protocol fidelity + tokens + latency (Anthropic Messages API)
export ANTHROPIC_API_KEY=...
python run_benchmarks.py

# OpenRouter (OpenAI-compatible) backend
export OPENROUTER_API_KEY=...
python run_benchmarks.py --backend openrouter --model anthropic/claude-sonnet-4
```

Add a judge model for a second grading pass:

```bash
python run_benchmarks.py --judge-model claude-sonnet-4-20250514
```

## Two case sets, two questions

| File | Question it answers | Judge |
| ---- | ------------------- | ----- |
| [`cases.json`](cases.json) | Does the output follow the **protocol** (sections, vote math, depth/flags)? | structure rubric + optional protocol judge |
| [`../skills/deliberate/evals/ground-truth.json`](../skills/deliberate/evals/ground-truth.json) | Is the **decision correct** against a known answer? | correctness judge (requires `--judge-model`) |

```bash
# Decision-correctness guard (each case targets one quality lever)
python run_benchmarks.py \
  --ground-truth ../skills/deliberate/evals/ground-truth.json \
  --judge-model claude-sonnet-4-20250514
```

The correctness judge grades **direction match**, **confidence band**, **surfaced facts**, and **failure triggers** per case; the summary adds `mean_correctness`, `direction_match_rate`, and `failures_triggered`. Any `failures_triggered > 0` is a regression to investigate.

## Key env knobs

`TRIBUNAL_BENCHMARK_BACKEND` (`anthropic`|`openrouter`) · `TRIBUNAL_BENCHMARK_MODEL` · `TRIBUNAL_BENCHMARK_JUDGE_MODEL` · `TRIBUNAL_BENCHMARK_MAX_TOKENS` · `TRIBUNAL_BENCHMARK_TEMPERATURE` · `--no-skill-file` (smaller prompt, less realistic) · `--no-prompt-cache`.

> The rubric measures **protocol fidelity, not factual correctness** — use the ground-truth set for correctness. Latency under `--multi-agent` is dominated by real subagent dispatch.
