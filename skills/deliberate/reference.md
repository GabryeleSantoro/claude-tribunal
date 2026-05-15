# Tribunal deliberate — reference

Supporting material for [SKILL.md](SKILL.md). Load when the user needs templates, brief vs full limits, or multi-agent agent names.

## Brief vs full

| Phase | Full (`--depth full`, default) | Brief (`--brief` / `--depth brief`) |
|-------|----------------------------------|-------------------------------------|
| 1 Topic | Domain paragraph + dimensions + facts vs uncertainties | 3–5 bullets total |
| 2 Roles | Table + tailored role label per archetype | One line per slot: archetype — label |
| 3 Openings | ~1 paragraph each persona, no cross-talk | 2–4 sentences per persona |
| 4 Cross-exam | Each challenger → target; challenge then defense | One subsection, five bullets: "A→B: …" merging challenge + reply in one sentence each |
| 5 Deliberation | Prose on tensions and resolution | 3–6 bullets |
| 6 Verdict | Full votes (position, lean if conditional, confidence, rationale) + math | Same as full (keep audit trail) |

Votes, \(\bar{v}\), weighted consensus strength, exports, and `--min-confidence` behavior are **unchanged** in brief mode.

## Token tips

- Prefer **brief** for exploratory questions; use **full** for ADR-worthy or contentious decisions.
- **`--multi-agent`** increases latency and tool use; use for higher-fidelity openings and cross-exam when subagents are available. Claude Code may still show subagent rows in the terminal; omit `--multi-agent` for a quieter UI, or rely on **compact** mode (default) so the **reply** stays short—add **`--full-log`** when you want every phase in the message.

## Compact vs full log

- **Default:** Orchestrator prints only the **Compact verdict** (see SKILL.md): topic metadata, Final Verdict, Votes, Reasoning Trail, plus a footer pointing to `--full-log`.
- **Full:** `--full-log` or `--verbose` restores the full Panel, Arguments, Cross-exam, and Deliberation sections in Markdown.

## Verdict Markdown skeleton (when `full_log`)

Use the **full** skeleton in SKILL.md. With **brief** depth, shorten **Arguments Summary** but keep all section headings present.

## Multi-agent: plugin agent `name` values

Use these exact strings when delegating:

| Archetype | Agent `name` |
|-----------|----------------|
| Domain Expert | `tribunal-persona-domain-expert` |
| Devil's Advocate | `tribunal-persona-devils-advocate` |
| Systems Thinker | `tribunal-persona-systems-thinker` |
| Logician | `tribunal-persona-logician` |
| Mediator | `tribunal-persona-mediator` |

## Cross-examination graph

- Use a **5-cycle**: each archetype challenges exactly one peer and is challenged exactly once.
- **Default ring:** Domain Expert → Devil's Advocate → Systems Thinker → Logician → Mediator → Domain Expert.

## Lean encoding (conditional votes)

| position | lean | \(v_i\) |
|----------|------|--------|
| support | (n/a) | +1 |
| reject | (n/a) | -1 |
| conditional | toward_support | +0.5 |
| conditional | neutral | 0 |
| conditional | toward_reject | -0.5 |

If `conditional` and `lean` is missing, treat as **neutral** (0) and note the omission in Reasoning Trail.
