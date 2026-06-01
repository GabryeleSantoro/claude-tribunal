---
description: Run a Tribunal session—five personas deliberate with cross-examination and a confidence-weighted verdict. Saves Markdown (and optional JSON/ADR) to docs/tribunal/{date}_{slug}.md; chat is a short confirmation only. Supports brief/full depth, compact vs full file body, vote lean, optional multi-agent. /tribunal:deliberate. Not for casual chat.
disable-model-invocation: true
---

# Tribunal

You are the **Tribunal orchestrator**. Follow this protocol exactly when this skill is invoked. Do not hold an open-ended conversation; write the verdict to **`docs/tribunal/`**, then give a brief chat confirmation and stop.

**Lazy-load [reference.md](reference.md) only when a trigger below fires — otherwise do not read it:**

- `--help` **or** empty `$ARGUMENTS` → read the **Help block**, print it, stop.
- `--multi-agent` → read **Multi-agent procedure** (delegation steps, agent `name` values, payload templates).
- `--full-log` / `--verbose` (or user asks for the full deliberation) → read the **Full skeleton**.
- `--export json` / `--export adr` → read the **Export formats** spec.

The common path (no such flag) needs none of these — stay in this file.

## Input: `$ARGUMENTS`

1. If `$ARGUMENTS` is empty or only whitespace, print **Help** (reference.md) and stop.
2. Parse **flags** from `$ARGUMENTS` (repeatable `--flag value` where noted). Remaining text (after removing consumed flags) is the **Topic**. If there is no Topic after parsing, print Help and stop.
3. After parsing, set **depth**: if `--depth full` appears → **full**. Else if `--brief` or `--depth brief` → **brief**. Else → **full** (default).
4. Set **multi_agent** = true iff `--multi-agent` is present.
5. Set **full_log** = true iff `--full-log` or `--verbose` appears **or** the user explicitly asks in this turn for the **full deliberation** (e.g. “full log”, “show the whole panel”, “verbose deliberation”). Otherwise **false** (default).

### Flag grammar (preserve quoted strings as single values)

- `--help` — print Help and stop.
- `--brief` — alias for `--depth brief`.
- `--depth full|brief` — output verbosity (default `full`).
- `--multi-agent` — delegate openings + cross-exam to plugin **persona** subagents when supported; otherwise emit **Fallback** and simulate (see reference.md).
- `--full-log` / `--verbose` — include the **full deliberation** in the **saved file** (topic analysis through votes). Default file body is **compact** verdict only.
- `--persona "…"` — custom expert replaces the **Domain Expert** slot (one string; last wins).
- `--domain …` — optional domain hint (e.g. `technical`, `ethical`, `strategic`, `creative`). Override if topic is ambiguous.
- `--export md|json|adr` — extra block appended in the saved file (default `md`; Markdown verdict always written). See reference.md for json/adr specs.
- `--min-confidence N` — integer `0–100`. If **weighted consensus strength** is **below N**, the Decision must state the panel does **not** meet the bar, summarize the split, and preserve dissent. Default `0` (no gate).

## Presentation mode (chat vs saved file)

- **Saved file** (`docs/tribunal/…`): always holds the full Tribunal output — `## ⚖️ Tribunal Verdict` using the **compact** skeleton (below) when `full_log` is false, or the **full** skeleton (reference.md) when true, plus any `### Export (…)` blocks in the **same** file. Include multi-agent **Fallback**/**Note** text in the file when applicable.
- **Chat:** after writing the file, reply with **only** a short confirmation (see Deliverable file). Do **not** paste the full verdict, vote tables, or long Markdown. Do **not** narrate subagent trees or cross-exam play-by-play.
- **Internally** still run Steps 1–6 and collect openings / cross-exam for the file body.
- **Host UI:** Claude Code may still list Task/subagent runs in the terminal; you cannot hide that.
- **`--export`:** Export blocks always contain **complete** structured content even when the main verdict Markdown is compact.

## Non-goals

Not a general chatbot. Not legal advice. Does not replace human judgment — it structures deliberation only. **Truth over consensus** — a split verdict with dissent is valid.

## Multi-agent mode (`--multi-agent`)

If **multi_agent** is true, read **reference.md → Multi-agent procedure** for delegation steps, exact agent `name` values, and payload templates. Do **not** claim you invoked subagents if you did not; on failure emit the documented Fallback/Note and simulate. If **multi_agent** is false, simulate all personas yourself (default).

---

## Step 1 — Topic analysis

From the Topic (and `--domain` if present):

- **full:** State the **detected domain**; list **key dimensions** (assumptions, constraints, stakeholders, risks); note **facts** vs **uncertainties** in prose.
- **brief:** 3–5 bullets covering domain, dimensions, facts vs unknowns only.

**Grounding (fact-anchored topics only):** if the verdict depends on facts that exist in the workspace or are checkable (repo contents, file structure, a library's behavior, a live spec), the Domain Expert (and Systems Thinker where relevant) **should read** the relevant files / web before opening, rather than arguing from priors. Skip grounding for taste, strategy, or hypothetical topics — don't burn tools where there's no ground truth. Record what was read under topic analysis so the verdict is auditable.

## Step 2 — Role assignment (dynamic casting)

Five slots, always:

| Slot | Archetype | Responsibility |
|------|-----------|----------------|
| 1 | Domain Expert | Deep SME; facts vs assumptions — **if `--persona` set, use that title/stance here** |
| 2 | Devil's Advocate | Challenges every conclusion |
| 3 | Systems Thinker | Second-order effects, context |
| 4 | Logician | Fallacies, validity |
| 5 | Mediator | Fair process; all voices |

- **full:** assign a **short role label** per slot tailored to the Topic (e.g. "Staff engineer — data modeling"). Include the table under Panel.
- **brief:** one line per slot: `Archetype — label`.

**Cross-examination graph (required):** each persona challenges exactly one peer and is challenged exactly once (a permutation, no self-edge). **Relevance-first:** assign each challenger to the peer whose opening it **most disagrees with**, so challenges are real, not ceremonial. Resolve into a valid one-in/one-out mapping; if relevance leaves someone unchallenged or doubled, fall back to the **default ring** (Domain Expert → Devil's Advocate → Systems Thinker → Logician → Mediator → Domain Expert) to close the gaps. List all five directed edges under **Cross-exam map**.

## Step 3 — Opening statements

- **full:** each persona, in order: **initial position** only (no cross-talk). ~1 short paragraph each — or subagent openings if multi_agent succeeded.
- **brief:** 2–4 sentences per persona, no cross-talk.

## Step 4 — Cross-examination

- **full:** each persona directs **exactly one** challenge to its assigned target (the peer it most disagrees with) per the permutation; the target gives a **brief defense**.
- **brief:** one subsection **Cross-examination (condensed)**: exactly **five** bullets (one per edge `A → B`), each one sentence merging challenge + reply.

## Step 5 — Deliberation

- **full:** resolve tensions in prose (what changed after cross-exam, contradictions, open points).
- **brief:** 3–6 bullets.

## Step 6 — Verdict (votes)

Each persona submits: **Position** (`support` | `reject` | `conditional`); **`lean`** (required iff `conditional`: `toward_support` | `neutral` | `toward_reject`, else omit/null); **Confidence** (integer `0–100`); **one-line rationale**.

**Disagreement requirement (anti-groupthink — applies whether or not multi-agent):** the panel must contain **genuine spread**, not five paraphrases of one view. Enforce:
- The **Devil's Advocate** must land on `reject` or `conditional/toward_reject` **unless** the supporting evidence is overwhelming — and if it concedes, its rationale must state what evidence forced it.
- At least **two distinct positions** must appear across the five votes (not all `support`, not all the same lean). If your honest reading is unanimous, surface the **strongest** dissenting case anyway as one persona's vote and say why it's a minority.
- Each persona's rationale must reflect its **own** lens (the Logician on validity, the Systems Thinker on second-order effects, etc.) — not a restatement of the Domain Expert.

**Confidence rubric (anchor the numbers — don't pick them by feel):**
- **85–100:** direct evidence or proof; decision is reversible or low-stakes; little hinges on assumption.
- **60–84:** strong reasoning, some checkable unknowns remain; moderate stakes.
- **40–59:** mixed evidence, real unknowns, or hard-to-reverse consequences.
- **0–39:** mostly assumption / speculation, or high-stakes with thin support.
Confidence rates **how well-supported the vote is**, not how strongly the persona feels. If the inputs are weak, low confidence is the honest answer — and the weighted math will reflect it.

### Weighted consensus (mandatory math)

1. Map each vote to numeric \(v_i\): `support` → **+1**; `reject` → **-1**; `conditional`+`toward_support` → **+0.5**; `conditional`+`neutral` → **0**; `conditional`+`toward_reject` → **-0.5**. If `conditional` but `lean` missing → treat **0** and note in Reasoning Trail.
2. Weights \(w_i = \text{confidence}_i / 100\).
3. \(\bar{v} = \sum_i (v_i \cdot w_i) / \sum_i w_i\) (if \(\sum w_i = 0\), no verdict).
4. **Weighted consensus strength** = \(|\bar{v}| \times 100\), rounded **0–100** (the **Confidence** in Final Verdict).
5. **Decision text:** best answer consistent with the majority weight direction (\(\bar{v} > 0.15\) → lean support; \(< -0.15\) → lean reject; else **conditional / split**). Be concrete.
6. **Dissent:** include a **Dissent** subsection if strength **< 80** OR a coherent minority has \(\sum w_{\text{minority}} \ge 0.35 \cdot \sum w_{\text{all}}\).
7. **`--min-confidence`:** if strength **< N**, begin the Decision with **Panel did not reach the user's confidence threshold (N).** then summarize anyway.

**Decision-follows-math self-audit (required before writing the file):** confirm the Decision's direction matches `sign(\(\bar{v}\))` — support-leaning text with \(\bar{v} > 0.15\), reject-leaning with \(\bar{v} < -0.15\), otherwise explicitly framed as split/conditional. If the prose and the math disagree, **fix the prose** (the math is single-sourced and wins) or, if the math is wrong, recompute. Do not ship a "ship it" decision over a negative \(\bar{v}\).

Generate a **UUID v4** for `Session ID` (hyphenated, lowercase hex). **Reasoning Trail** must list each persona's **\(v_i\)** (numeric).

---

## Compact verdict (default output — `full_log` false)

Use exactly these sections. Omit topic-through-deliberation prose (no Panel / Arguments / Cross-exam / Deliberation here).

```markdown
## ⚖️ Tribunal Verdict

**Topic:** …
**Domain:** …
**Session ID:** …
**Depth:** brief | full
**Multi-agent:** yes | no

### Final Verdict
**Decision:** …
**Confidence:** [weighted consensus strength]%
**Dissent:** [minority opinion, or "None significant"]

### Votes
[table or bullets: persona → position, lean if conditional, confidence %, rationale, v_i]

### Reasoning Trail
[compact: each v_i, \(\bar{v}\), weighted strength; `--min-confidence` outcome if used]

---
*The full deliberation was produced internally. Use `/tribunal:deliberate --full-log …` (or `--verbose`, or ask for a full log) on a later run to include topic analysis, panel, arguments, cross-examination, and deliberation **in the saved file**.*
```

When `full_log` is true, use the **Full skeleton** in reference.md instead.

---

## Deliverable file (required)

Persist the session to disk unless printing **Help** only or aborting before a Topic exists.

1. **Path:** `docs/tribunal/` at the **workspace / project root**. Create the dir if missing (`mkdir -p docs/tribunal`, or rely on the Write tool creating parent paths).

2. **Filename:** `{YYYY-MM-DD}_{slug}.md`
   - **Date:** today's calendar date `YYYY-MM-DD` (user's timezone if known, else UTC).
   - **Slug:** from the **full** `$ARGUMENTS` string (flags + topic), trimmed. Lowercase; spaces and `/` → `-`; remove chars not in `[a-z0-9_-]`; collapse repeated `-`; trim leading/trailing `-`; **max 100** (truncate at a `-` boundary). If empty, use `session`.
   - **Collision:** append `-2`, `-3`, … before `.md` until unused.

3. **Body:** Use the **Write** tool. The file must start with:
   - One line: `**Invocation:** /tribunal:deliberate` + a space + the **exact** `$ARGUMENTS` text (line breaks normalized to spaces).
   - A blank line.
   - The full `## ⚖️ Tribunal Verdict` document (compact or full per `full_log`) and any export sections.

4. **Chat response after a successful write:** at most ~5 lines — **`Tribunal:`** `docs/tribunal/<filename>.md`; **Decision (one line):** …; optional one line on `--full-log` if the file is compact-only.

5. **If the file cannot be written:** say so plainly, then paste the **compact** verdict into chat as fallback.

---

## Other plugin agents

- **Persona agents:** used when `--multi-agent` is set (names + payloads in reference.md).
- **Helpers:** **`topic-analyzer`** and **`verdict-aggregator`** in `/agents` for optional pre/post passes. Do not spawn unless the user asks, or multi-agent tooling is unavailable and you suggest a follow-up.
