<div align="center">

<br>

```
████████╗██████╗ ██╗██████╗ ██╗   ██╗███╗   ██╗ █████╗ ██╗
╚══██╔══╝██╔══██╗██║██╔══██╗██║   ██║████╗  ██║██╔══██╗██║
   ██║   ██████╔╝██║██████╔╝██║   ██║██╔██╗ ██║███████║██║
   ██║   ██╔══██╗██║██╔══██╗██║   ██║██║╚██╗██║██╔══██║██║
        ██║   ██║  ██║██║██████╔╝╚██████╔╝██║ ╚████║██║  ██║███████╗
        ╚═╝   ╚═╝  ╚═╝╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝
```

### _Five minds. One verdict. Zero bullshit._

<br>

[![Version](https://img.shields.io/github/v/release/GabryeleSantoro/claude-tribunal?style=for-the-badge&label=&logo=git&logoColor=white)](https://github.com/GabryeleSantoro/claude-tribunal/releases)&nbsp;
[![Claude Plugin](https://img.shields.io/badge/Claude_Plugin-CC785C?style=for-the-badge&logo=anthropic&logoColor=white)](https://docs.anthropic.com)&nbsp;
[![Verdicts](https://img.shields.io/badge/Verdicts→_docs%2Ftribunal%2F-444?style=for-the-badge)](#-output-files)

<br>

</div>

---

Tribunal convenes a panel of **five adversarial AI personas** — sized to the small-group optimum from organizational psychology — and forces them to argue, cross-examine, and converge on a confidence-weighted verdict — then writes it to disk. The chat reply is a one-line confirmation. The heavy work lands in `docs/tribunal/`.

Built for decisions that deserve more than a single model's gut feeling.

---

<br>

## ▸ Inspiration & Comparison

Tribunal is inspired by [Andrej Karpathy's LLM Council](https://github.com/karpathy/llm-council) — the idea that hard questions deserve more than one pass from one model. Karpathy's project sends a query to several LLMs, has them rank each other's anonymized answers, and lets a Chairman synthesize the final response. It is a clever, minimal demo for comparing vendors side by side.

Tribunal takes that core insight — **collect diverse views, stress-test them, converge on a verdict** — and pushes it into a production-oriented deliberation protocol inside Claude Code. Where LLM Council optimizes for _model comparison_, Tribunal optimizes for _decision quality_.

|                     | [LLM Council](https://github.com/karpathy/llm-council)                       | **Tribunal**                                                                                            |
| ------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Goal**            | Compare answers from different model vendors                                 | Reach a confidence-weighted verdict on a decision                                                       |
| **Integration**     | Standalone web app (FastAPI + React)                                         | Claude Code plugin — `/tribunal:deliberate` in your repo                                                |
| **Panel**           | Same query to N external models (GPT, Gemini, Claude, Grok…)                 | Five fixed **adversarial personas** — [small-group optimum](#-why-five) (~4–5) with distinct cognitive roles |
| **Deliberation**    | Stage 1: opinions → Stage 2: anonymous ranking → Stage 3: Chairman synthesis | Topic analysis → openings → **cross-examination** (each persona challenges one peer) → weighted verdict |
| **Consensus**       | Aggregate rank positions; Chairman prose                                     | Explicit vote math: `v̄ = Σ(vᵢ · cᵢ) / Σcᵢ` with conditional leans and confidence rubric                 |
| **Anti-groupthink** | Anonymized labels reduce vendor bias                                         | Mandated dissent (Devil's Advocate), ≥2 distinct positions, relevance-first challenges                  |
| **Grounding**       | Models answer from priors only                                               | Domain Expert reads repo / web on fact-anchored topics before arguing                                   |
| **Output**          | Chat UI + JSON conversation files                                            | Structured Markdown verdict in `docs/tribunal/` (+ optional JSON / ADR export)                          |
| **Quality gates**   | None                                                                         | `--min-confidence` threshold, decision-follows-math self-audit, benchmark harness                       |
| **Cost / setup**    | OpenRouter API key + credits for every model per query                       | Runs inside Claude Code; single-model default or optional `--multi-agent` subagents                     |
| **Maintenance**     | Explicitly unsupported hack ("vibe coded")                                   | Versioned plugin, evals, benchmarks, local testing guide                                                |

### What Tribunal adds beyond LLM Council

1. **Adversarial roles, not interchangeable models.** Five personas — Domain Expert, Devil's Advocate, Systems Thinker, Logician, Mediator — each have a fixed function. The panel argues; it does not just rank prose paragraphs.

2. **Cross-examination, not just peer review.** Each persona challenges exactly one peer (relevance-first, not ceremonial) and defends against one challenge. Weak arguments get stress-tested before the vote.

3. **Quantified verdicts.** Support / reject / conditional votes, confidence anchored to evidence quality, and weighted consensus you can audit. Split verdicts with dissent are first-class — not smoothed over by a Chairman.

4. **Decision artifacts.** Every run writes a dated, slugged file under `docs/tribunal/` — an audit trail for architecture choices, ADRs, and team review. Chat stays a one-line confirmation.

5. **Guardrails against self-agreement.** Anti-groupthink rules, confidence rubric, grounding on checkable facts, and a self-audit that the written Decision matches the sign of `v̄`.

6. **Measured, not assumed.** Protocol-fidelity benchmarks, decision evals against ground truth, and a skill-vs-baseline harness — so quality is observable, not vibes.

7. **Workflow-native.** Installs from the Claude plugin marketplace, runs in the repo you're deciding about, supports `--persona`, `--domain`, `--export adr`, and `--multi-agent` when you need real subagent isolation.

LLM Council remains excellent inspiration for **multi-vendor model shopping** and seeing how GPT vs Gemini vs Claude answer the same question. Tribunal is built for when the question is not _"which model wrote the best paragraph?"_ but _"what should we actually do, and how confident are we?"_

---

<br>

## ⚖ The Deliberation

```
                              your topic
                                  │
           ┌──────────────────────▼──────────────────────┐
           │                   PANEL                     │
           │                                             │
           │  Domain Expert  ·  Devil's Advocate         │
           │  Systems Thinker  ·  Logician  ·  Mediator  │
           └──────────────────────┬──────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │      Opening Statements   │
                    │   (one position per role) │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │      Cross-Examination    │
                    │  5-cycle: each challenges │
                    │  exactly one peer, defends│
                    │  against exactly one      │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    Confidence-Weighted    │
                    │          Verdict          │
                    │  v̄ = Σ(vᵢ · cᵢ) / Σcᵢ     │
                    └─────────────┬─────────────┘
                                  │
                    docs/tribunal/{date}_{slug}.md
```

<br>

Each role has a fixed adversarial function:

| Persona              | Function                                                              |
| -------------------- | --------------------------------------------------------------------- |
| **Domain Expert**    | Field authority. Facts over assumptions. Replaceable via `--persona`. |
| **Devil's Advocate** | Stress-tests every position. Exists to break weak arguments.          |
| **Systems Thinker**  | Second and third-order effects. What are you not seeing?              |
| **Logician**         | Internal consistency. Surfaces hidden premises and contradictions.    |
| **Mediator**         | Synthesizes tensions into a verdict the panel can live with.          |

Votes are **conditional** — each persona can lean toward support or reject without full commitment. The weighted average decides.

<br>

---

## ▸ Why Five?

The panel is **five personas, always** — not a configurable headcount. That number is a design choice grounded in decades of small-group research on coordination, accountability, and decision quality.

### What the research says

| Finding | Implication for Tribunal |
| --- | --- |
| **[Ringelmann effect](https://en.wikipedia.org/wiki/Ringelmann_effect)** (1913): individual effort drops as group size grows — *social loafing* | More personas → weaker distinct voices; each slot must stay indispensable |
| **[Hackman & Vidmar (1970)](https://ingbrief.wordpress.com/2019/05/08/effect-of-size-on-group-performance/)**: reported satisfaction with team size peaks at **~4–5** on judgment tasks | Five is the empirical sweet spot for interdependent decision work |
| **Communication channels** `n(n−1)/2`: 5 members → **10** links; 8 → **28**; 10 → **45** | Cross-examination stays tractable; every voice can be heard without a Chairman bottleneck |
| **[Mueller (Wharton)](https://knowledge.wharton.upenn.edu/podcast/knowledge-at-wharton-podcast/is-your-team-too-big-too-small-whats-the-right-number-2/)**: on coordination tasks, motivation drops after the **fifth** member; cliques form above that | Tribunal caps the panel before process losses dominate |
| **Perceptual tracking**: humans reliably attend to **~4–5** distinct agents at once ([iScience, 2024](https://www.sciencedirect.com/science/article/pii/S2589004224023307)) | Five roles stay mentally separable in the verdict file |
| **[Two-pizza teams](https://aws.amazon.com/executive-insights/content/amazon-two-pizza-team/)** (Amazon): small teams minimize coordination overhead and preserve ownership | Same principle applied to cognitive roles, not headcount |

### Why not fewer or more?

**Below five** you lose a critical lens. A panel of three (expert + challenger + synthesizer) can decide fast but skips second-order effects and formal validity checks — the failure modes that matter on hard tradeoffs.

**Above five** you reintroduce the pathologies Tribunal is built to avoid:

- **Role blur** — personas paraphrase each other instead of arguing (the LLM equivalent of social loafing)
- **Coordination tax** — cross-exam permutations grow; someone needs a "Chairman" to merge noise back into prose
- **False balance** — extra voices get invented to fill seats, not because the topic needs them

Five maps cleanly onto the minimum **cognitive division of labor** for adversarial deliberation:

```
facts & domain  →  stress-test  →  second-order  →  validity  →  synthesis
     (1)              (2)              (3)            (4)          (5)
```

And onto a **single Hamiltonian cross-exam cycle**: each persona challenges exactly one peer and is challenged exactly once — full coverage with no self-edges and no redundant rounds.

Tribunal is not a general-purpose council of *N* models (see [LLM Council](#-inspiration--comparison)). It is a **small, role-bound work group** sized for the kind of coordinated judgment that human teams do best at four to six members — then formalized into a repeatable protocol.

<br>

---

## ▸ Quality Controls

A single model wearing five hats tends to agree with itself. Tribunal pushes back against that with explicit guardrails:

| Control                     | What it enforces                                                                                                |
| --------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **Anti-groupthink mandate** | The Devil's Advocate must dissent unless evidence is overwhelming; ≥2 distinct positions must appear.           |
| **Confidence rubric**       | Confidence numbers are anchored to evidence quality and reversibility — not picked by feel.                     |
| **Grounding**               | On fact-anchored topics the Domain Expert reads the repo / web before arguing, instead of guessing from priors. |
| **Relevance cross-exam**    | Each persona challenges the peer it _most disagrees with_; the ring is only a fallback to guarantee coverage.   |
| **Decision-follows-math**   | A self-audit confirms the written Decision matches the sign of `v̄` before the file is saved.                    |

These are guardrails, not guarantees — see [Benchmarks](#-benchmarks) for how they're measured.

<br>

---

## ▸ Install

### From marketplace

1. **Add the marketplace** — registers the catalog (nothing installed yet):

   ```bash
   claude plugin marketplace add GabryeleSantoro/claude-tribunal
   ```

2. **Install the plugin** — pulls `tribunal` from that catalog:

   ```bash
   claude plugin install tribunal@claude-tribunal
   ```

3. **Invoke** — restart Claude Code, then:

   ```
   /tribunal:deliberate [flags...] <topic>
   ```

See also: [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins) · [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces).

### Local development (`--plugin-dir`)

```bash
# From the repo root — loads the plugin into Claude Code
claude --plugin-dir .

# After editing the plugin — restart Claude Code to pick up changes
```

> **Shortcut alias** — copy [`examples/tribunal-command.md`](examples/tribunal-command.md) to `.claude/commands/tribunal.md` in any project. Then `/tribunal` works as a bare alias for `/tribunal:deliberate` without typing the namespace.

For step-by-step smoke tests: [LOCAL_TESTING.md](LOCAL_TESTING.md) · For implementation detail: [skills/deliberate/reference.md](skills/deliberate/reference.md)

<br>

---

## ▸ Invoke

```
/tribunal:deliberate [flags...] <topic>
```

<br>

---

## ▸ Flags

<kbd>--help</kbd> — Print usage and exit.

<br>

| Flag                       | Values            | Effect                                                                                                                           |
| -------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `--depth`                  | `full` \| `brief` | **full** (default): rich topic analysis, full opening paragraphs, prose deliberation. **brief**: tighter, same vote math.        |
| `--brief`                  | —                 | Shorthand for `--depth brief`.                                                                                                   |
| `--full-log` / `--verbose` | —                 | Write the complete deliberation (panel, arguments, cross-exam) to the output file. Default: compact verdict only.                |
| `--multi-agent`            | —                 | Spawn each persona as a real subagent. Same weighted verdict, higher fidelity, more latency.                                     |
| `--persona "…"`            | string            | Replace the Domain Expert slot with a named custom expert.                                                                       |
| `--domain …`               | string            | Domain hint — e.g. `ethical`, `technical`, `legal`. Shapes role labels.                                                          |
| `--export`                 | `json` \| `adr`   | Append a structured export block to the output file. Markdown verdict is always written regardless.                              |
| `--min-confidence N`       | `0`–`100`         | Gate weak consensus: if weighted strength `< N`, the Decision opens by stating the threshold wasn't met and preserves the split. |

<br>

---

## ▸ Examples

<details>
<summary><strong>Single-model &nbsp;·&nbsp; fast, no subagents</strong></summary>

<br>

```
/tribunal:deliberate --brief \
  For a new BFF: PostgreSQL + JSONB vs a document DB for messy nested payloads — \
  what fits our ops and query patterns?
```

```
/tribunal:deliberate --export adr \
  Adopt strict TypeScript (no implicit any) repo-wide this quarter, \
  including generated and legacy packages?
```

```
/tribunal:deliberate --domain technical --min-confidence 85 \
  Replace our in-house job queue with Redis Streams: \
  when is the complexity worth it?
```

```
/tribunal:deliberate --brief \
  If CI is green but the bug only reproduces on a leap second and prod is NTP-synced UTC, \
  do we block the release or ship and file "works on my epoch"?
```

</details>

<details>
<summary><strong>Multi-agent &nbsp;·&nbsp; each persona runs as an independent subagent</strong></summary>

<br>

```
/tribunal:deliberate --multi-agent --full-log --depth full \
  We run multi-region active-active; AP-style cached reads are fine for most domains \
  but billing settlement must be linearizable against our ledger. \
  How do we roll out a CRDT-ish edge layer without ever double-charging \
  during partition or failover?
```

```
/tribunal:deliberate --multi-agent --brief \
  Expose our product API to integrators as GraphQL, OpenAPI REST, or both \
  with a compatibility layer — what breaks at scale?
```

```
/tribunal:deliberate --multi-agent --depth full \
  Zero-trust mTLS between every service vs selective auth for internal east-west \
  traffic in a growing k8s estate — which liability do we own first?
```

```
/tribunal:deliberate --multi-agent \
  --persona "SRE lead — payment rail outages" \
  Should we split the monolith along bounded contexts now, \
  or harden observability and split later?
```

```
/tribunal:deliberate --multi-agent --export json --brief \
  Rewrite the p99-critical pricing path from interpreted JS to Rust vs optimize \
  and profile in place for two quarters — which bets our latency budget better?
```

```
/tribunal:deliberate --multi-agent --domain ethical --min-confidence 70 \
  Ship an opt-out telemetry SDK that phones home crash breadcrumbs for unpaid tiers — \
  privacy vs debuggability tradeoff?
```

</details>

<br>

---

## ▸ Output Files

Every run (except `--help` or an empty topic) writes:

```
docs/tribunal/{YYYY-MM-DD}_{slug}.md
```

The **slug** is a sanitized form of your full invocation — flags and topic together. Re-running the same command on the same day appends `-2`, `-3`, and so on.

```
docs/tribunal/
├── 2026-05-15_brief-postgresql-jsonb-vs-document-db.md
├── 2026-05-15_export-adr-adopt-strict-typescript.md
└── 2026-05-15_multi-agent-full-log-crdt-edge-layer.md
```

**Default file:** compact verdict — topic metadata, Final Verdict, Votes, Reasoning Trail, footer.  
**With `--full-log`:** adds Panel, Cross-exam map, Arguments Summary, and Cross-Examination Highlights sections.  
**Chat reply:** always a short confirmation only. The file is the record.

<br>

---

## ▸ Vote Math

Each persona returns a position, optional lean, and confidence score:

| Position    | Lean           | Vote value `vᵢ` |
| ----------- | -------------- | --------------- |
| support     | —              | `+1`            |
| reject      | —              | `−1`            |
| conditional | toward_support | `+0.5`          |
| conditional | neutral        | `0`             |
| conditional | toward_reject  | `−0.5`          |

Weighted consensus:

```
v̄ = Σ(vᵢ · cᵢ) / Σcᵢ      where cᵢ = confidence ∈ [0, 100]
```

`--min-confidence N` flags verdicts where the panel's aggregate confidence is below threshold — weak consensus is surfaced, not suppressed.

<br>

---

## ▸ Benchmarks

Tribunal ships its own measurement harness under [`benchmarks/`](benchmarks/) — token usage, wall time, a heuristic protocol-fidelity rubric, and an optional LLM judge. Results below are from local runs; reproduce them yourself with the commands underneath.

**Protocol fidelity** — single-model, compact verdict, `claude-sonnet-4-20250514` (5 cases):

| Metric                          | Value          |
| ------------------------------- | -------------- |
| Protocol-fidelity rubric        | **97.2 / 100** |
| Errors                          | **0 / 5**      |
| Input tokens / case             | ~5.3k          |
| Output tokens / case            | ~1.3k          |
| Wall time / case (single-model) | ~22 s          |

**Decision evals** — skill vs. no-skill baseline, assertion-graded (3 decisions):

| Configuration | Assertions passed | Token cost       |
| ------------- | ----------------- | ---------------- |
| With skill    | **17 / 17**       | +77% vs baseline |
| Baseline      | 9 / 9             | —                |

The token premium buys what the baseline doesn't quantify: explicit per-persona positions, a weighted consensus number, surfaced dissent, and confidence gating. On the telemetry-SDK eval, the panel rejected at 23% against a 70% gate where the baseline shipped at 72% — the structured split caught tensions the single pass absorbed silently.

> **Honest caveats.** The rubric scores **protocol fidelity, not decision correctness** — for correctness, run the ground-truth set (`skills/deliberate/evals/ground-truth.json`) with a judge model (see [LOCAL_TESTING.md](LOCAL_TESTING.md) §8). `--multi-agent` raises latency substantially (real subagent dispatch). Numbers are `claude-sonnet-4-20250514`; your model and topics will vary.

**Reproduce:**

```bash
cd benchmarks
pip install -r requirements.txt
python run_benchmarks.py --dry-run                          # plan only, no API key
export ANTHROPIC_API_KEY=...
python run_benchmarks.py                                    # protocol-fidelity + tokens + latency
python run_benchmarks.py \
  --ground-truth ../skills/deliberate/evals/ground-truth.json \
  --judge-model claude-sonnet-4-20250514                    # decision-correctness guard
```

<br>

---

## ▸ Non-Goals

- Not a general chat assistant
- Not legal advice
- Does not replace human judgment
- Split verdicts with dissent are valid — and expected on hard questions

<br>

---

## ▸ License

MIT — free to use, modify, and distribute. See [LICENSE](LICENSE).

<br>

---

<div align="center">

<br>

[Releases](https://github.com/GabryeleSantoro/claude-tribunal/releases) &nbsp;·&nbsp; [Benchmarks](benchmarks/) &nbsp;·&nbsp; [Local Testing](LOCAL_TESTING.md) &nbsp;·&nbsp; [reference](skills/deliberate/reference.md) &nbsp;·&nbsp; [License](LICENSE)

<br>

_The panel is always in session._

<br>

</div>
