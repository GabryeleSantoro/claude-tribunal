# Tribunal deliberate — reference

Lazy-loaded supporting material for [SKILL.md](SKILL.md). Read a section only when its trigger fires (see SKILL.md top): `--help`/empty → **Help block**; `--multi-agent` → **Multi-agent procedure**; `--full-log` → **Full skeleton**; `--export json|adr` → **Export formats**.

## Help block (`--help` or empty `$ARGUMENTS`)

```text
Tribunal — /tribunal:deliberate

Usage: /tribunal:deliberate [flags...] <topic>

Flags:
  --help                 Show this help
  --depth full|brief     Rich vs condensed deliberation *detail* when full log is on; default full
  --brief                Alias for --depth brief
  --full-log             Full deliberation in the **saved file**—panel, arguments, cross-exam, deliberation, votes (default: compact verdict only in file)
  --verbose              Same as --full-log
  --multi-agent          Delegate openings + cross-exam to persona subagents (if supported)
  --persona "title"      Custom Domain Expert (replaces default expert slot)
  --domain <hint>        Override domain hint for analysis
  --export md|json|adr   Extra block in the saved file (Markdown verdict always in file)
  --min-confidence N     Require weighted consensus strength ≥ N (0–100)

Examples:
  /tribunal:deliberate Should we use PostgreSQL or MongoDB for this project?
  /tribunal:deliberate --brief --persona "Pokemon expert" Is €45 underpriced?
  /tribunal:deliberate --domain ethical --min-confidence 85 Ship with minor bugs?
  /tribunal:deliberate --export adr Should we migrate to Edge Functions?
  /tribunal:deliberate --multi-agent --depth full Pick a regional DB leader
  /tribunal:deliberate --full-log --brief Topic here

Output: verdict is saved under docs/tribunal/ (see Deliverable file). Chat shows only a short confirmation.
```

## Brief vs full

What **full** vs **brief** changes is how much detail goes into the written deliberation—not a checklist you run alongside the model.

| Part of the write-up | Full (`--depth full`, default) | Brief (`--brief` / `--depth brief`) |
|----------------------|----------------------------------|-------------------------------------|
| Topic analysis | Domain paragraph + dimensions + facts vs uncertainties | 3–5 bullets total |
| Roles | Table + tailored role label per archetype | One line per slot: archetype — label |
| Opening statements | ~1 paragraph each persona, no cross-talk | 2–4 sentences per persona |
| Cross-exam | Each challenger → target; challenge then defense | One subsection, five bullets: "A→B: …" merging challenge + reply in one sentence each |
| Deliberation | Prose on tensions and resolution | 3–6 bullets |
| Verdict | Full votes (position, lean if conditional, confidence, rationale) + math | Same as full (keep audit trail) |

Votes, \(\bar{v}\), weighted consensus strength, exports, and `--min-confidence` behavior are **unchanged** in brief mode.

## Token tips

- Prefer **brief** for exploratory questions; use **full** for ADR-worthy or contentious decisions.
- **`--multi-agent`** increases latency and tool use; use for higher-fidelity openings and cross-exam when subagents are available. Claude Code may still show subagent rows in the terminal; omit `--multi-agent` for a quieter UI, or rely on **compact** file mode so the **saved** verdict stays short—add **`--full-log`** when you want the full write-up **in the file**.

## Compact vs full log

- **Default:** The **saved file** under `docs/tribunal/` contains only the **Compact verdict** (see SKILL.md): topic metadata, Final Verdict, Votes, Reasoning Trail, plus a footer pointing to `--full-log`.
- **Full:** `--full-log` or `--verbose` adds Panel, Arguments, Cross-exam, and Deliberation sections **in that file**. Chat stays a short confirmation either way.

## Full skeleton (when `full_log` is true)

Fill all brackets. With **brief** depth, shorten **Arguments Summary** but keep all section headings present.

```markdown
## ⚖️ Tribunal Verdict

**Topic:** …
**Domain:** …
**Session ID:** …
**Depth:** brief | full
**Multi-agent:** yes | no (if yes, note Fallback if used)

### Panel
- 🔬 Domain Expert — …
- 🗡️ Devil's Advocate — …
- 🌐 Systems Thinker — …
- 🧮 Logician — …
- ⚖️ Mediator — …

### Cross-exam map
(permutation: A→B→C→…)

### Arguments Summary
[condensed per-persona positions / openings]

### Cross-Examination Highlights
[key challenges and responses, or condensed subsection if depth brief]

### Votes
[persona → position, lean if conditional, confidence %, rationale — plus each v_i]

### Final Verdict
**Decision:** …
**Confidence:** [weighted consensus strength]%
**Dissent:** [minority opinion, or "None significant"]

### Reasoning Trail
[audit: each v_i, bar(v), weighted strength, tradeoffs]
```

## Export formats (`--export json|adr`)

Append after the main **⚖️ Tribunal Verdict** Markdown inside the file (compact or full):

- **`--export json`:** heading `### Export (JSON)`, then one JSON code fence with: `sessionId`, `topic`, `domain`, `depth`, `fullLog` (boolean), `multiAgentRequested`, `multiAgentDelegationSucceeded` (boolean or null if not requested), `crossExamPermutation` (array of strings, order of challenges), `panel` (array of `{ archetype, label, opening, vote: { position, lean, confidence, rationale, vNumeric } }`), `crossExamination` (array of `{ from, to, challenge, response }`), `verdict` (`decision`, `weightedConsensusStrength`, `minConfidenceGate`, `dissent`, `vBar`), `reasoningTrail` (string). Populate **full** deliberation fields here even when the Markdown verdict above is compact.
- **`--export adr`:** heading `### Export (ADR)`, then a Markdown code fence with mini ADR: `# ADR-…`, `Status` (session id), `Context`, `Decision`, `Consequences`, `Panel metadata`.

## Multi-agent procedure (`--multi-agent`)

When **multi_agent** is true:

1. **Try** to delegate using your **Task / subagent** capability with the plugin agent **`name`** below. Do **not** claim you invoked subagents if you did not. Do **not** narrate delegations in **chat**; the file body receives synthesized content only.
2. **On failure** (no tool, or refusal): if **full_log**, add a line under the verdict in the **file**: `Fallback: multi-agent delegation unavailable; continuing as single-orchestrator simulation.` If **full_log** is false, add `Note: Multi-agent unavailable; single-orchestrator simulation.` In **chat**, don't paste those strings unless the file write failed (then summarize in one line). Then simulate openings + cross-exam yourself.

**Agent `name` values (opening / challenge / defense):**

| Archetype | `name` |
|-----------|--------|
| Domain Expert | `tribunal-persona-domain-expert` |
| Devil's Advocate | `tribunal-persona-devils-advocate` |
| Systems Thinker | `tribunal-persona-systems-thinker` |
| Logician | `tribunal-persona-logician` |
| Mediator | `tribunal-persona-mediator` |

**Procedure:**

- **Steps 1–2** always run in the orchestration thread (topic analysis + role labels + cross-exam permutation: a 5-cycle so each archetype challenges exactly one peer and is challenged once; record `A → B` edges).
- **Step 3 — openings:** run **five parallel** subagent tasks (one per row), **Mode: opening**, payload:

  ```text
  Mode: opening
  Topic: <topic>
  Domain: <detected or hint>
  RoleLabel: <slot label from Step 2>
  CustomExpertContext: <only for Domain Expert: --persona text or "none">
  ```

  Collect each opening verbatim into the final output.
- **Step 4 — cross-examination:** for each directed edge **Challenger → Target** in fixed order (Domain Expert first as challenger, then follow the cycle), run **sequentially**:
  1. Subagent for **Challenger**, **Mode: challenge**, payload: Topic, FromArchetype, ToArchetype, ChallengerOpening, TargetOpening.
  2. Subagent for **Target**, **Mode: defense**, payload: Topic, Archetype=Target, ChallengeText, TargetOpening.
- **Steps 5–6** run **only** in the orchestrator thread (use collected openings + cross-exam). Simulate deliberation and **all final votes** here so consensus math is single-sourced.

## Cross-examination graph

- Each persona challenges exactly one peer and is challenged exactly once (a permutation, no self-edge).
- **Relevance-first:** point each challenger at the opening it **most disagrees with**. Real friction beats ring position.
- **Fallback ring** (use to fill gaps if relevance leaves someone unchallenged or doubled): Domain Expert → Devil's Advocate → Systems Thinker → Logician → Mediator → Domain Expert.

## Lean encoding (conditional votes)

| position | lean | \(v_i\) |
|----------|------|--------|
| support | (n/a) | +1 |
| reject | (n/a) | -1 |
| conditional | toward_support | +0.5 |
| conditional | neutral | 0 |
| conditional | toward_reject | -0.5 |

If `conditional` and `lean` is missing, treat as **neutral** (0) and note the omission in Reasoning Trail.

## Worked example (anchor for format + math)

A complete, realistic **compact** verdict. Use it as a fidelity reference for structure, vote spread, confidence rubric, and the math. (Topic: *"Adopt a 2-week sprint cadence for a 4-person team?"* — illustrative.)

```markdown
## ⚖️ Tribunal Verdict

**Topic:** Adopt a fixed 2-week sprint cadence for our 4-person team?
**Domain:** Strategic / team process
**Session ID:** 5a1f9c30-7e42-4b86-bc11-2d9e0f4a7c63
**Depth:** brief
**Multi-agent:** no

### Final Verdict
**Decision:** Conditional yes — adopt 2-week sprints as a 6-week trial with a fixed retro to decide keep/drop. At 4 people the ceremony overhead is the main risk, so run the lightest version (planning + retro only, skip daily standups in favor of async) and measure whether predictability actually improves.
**Confidence:** 38%
**Dissent:** Devil's Advocate (conf 80) rejects: a 4-person team gets sprint *predictability* from a shared backlog and a weekly check-in without paying the cadence tax; fixed sprints can ossify into theater.

### Votes

| Persona | Position | Lean | Conf | Rationale | vᵢ |
|---------|----------|------|------|-----------|-----|
| 🔬 Domain Expert | conditional | toward_support | 65 | Sprints help predictability but only with disciplined scope-setting; team is small enough to go light | +0.5 |
| 🗡️ Devil's Advocate | reject | — | 80 | At n=4 the cadence cost outweighs benefit; same outcome via backlog + weekly sync | −1 |
| 🌐 Systems Thinker | conditional | neutral | 55 | Second-order risk: cadence can mask priority churn; benefit depends on whether work is interrupt-driven | 0 |
| 🧮 Logician | conditional | toward_support | 60 | "Sprints improve delivery" holds only if the bottleneck is planning, not capacity — unproven here | +0.5 |
| ⚖️ Mediator | conditional | toward_support | 50 | Trial-with-exit respects both camps; avoids premature lock-in | +0.5 |

### Reasoning Trail
v₁=+0.5 (w 0.65), v₂=−1 (w 0.80), v₃=0 (w 0.55), v₄=+0.5 (w 0.60), v₅=+0.5 (w 0.50).
Σ(vᵢ·wᵢ) = 0.325 − 0.80 + 0 + 0.30 + 0.25 = 0.075. Σwᵢ = 3.10. v̄ = 0.075/3.10 = +0.024 → |v̄|×100 = **2%**, well inside the split band (|v̄| < 0.15), so the Decision is framed conditional, not "yes". Self-audit: prose says "conditional yes — trial", math says split → consistent (both non-committal). Devil's Advocate carries the only hard position and a high weight, so dissent is surfaced prominently. No --min-confidence gate.

---
*The full deliberation was produced internally. Use `/tribunal:deliberate --full-log …` (or `--verbose`, or ask for a full log) on a later run to include topic analysis, panel, arguments, cross-examination, and deliberation **in the saved file**.*
```

Note how the example shows **real spread** (one hard reject, one neutral, three conditional), **rubric-anchored confidences** (the strongest evidence-free claim gets the lowest number), and a **decision that matches the math** rather than overstating it.
