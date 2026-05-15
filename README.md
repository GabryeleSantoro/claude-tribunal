# Tribunal (Claude Code plugin)

> *Five minds. One verdict. Zero bullshit.*

Structured five-persona deliberation with cross-examination, confidence-weighted verdicts, and optional JSON or ADR export. Spec: [TRIBUNAL_BIBLE.md](TRIBUNAL_BIBLE.md).

## Install (local dev)

From this repository root:

```bash
claude --plugin-dir .
```

After editing the plugin, run `/reload-plugins` in Claude Code.

## Command (namespace)

Claude Code namespaces plugin skills as `/plugin-name:skill-name`. This plugin’s canonical invocation is:

```text
/tribunal:deliberate [flags...] <topic>
```

The bible uses `/tribunal …` as a shorthand; that maps to `tribunal:deliberate` here.

### Optional: short `/tribunal` in one project

Add a project command file (not part of the plugin distribution) that points at the same workflow, for example `.claude/commands/tribunal.md` with body: “Run skill `tribunal:deliberate` with the user’s arguments: …” or paste the skill instructions — see [Claude Code plugins](https://code.claude.com/docs/en/plugins).

## Examples

```text
/tribunal:deliberate Should I use PostgreSQL or MongoDB for this project?

/tribunal:deliberate --persona "Pokemon card market expert" Is this card underpriced at €45?

/tribunal:deliberate --domain ethical Is it justified to ship a product with known minor bugs?

/tribunal:deliberate --export adr Should we migrate our backend to Edge Functions?

/tribunal:deliberate --min-confidence 85 What's the best clustering algorithm for this dataset?
```

## Flags

| Flag | Purpose |
|------|---------|
| `--help` | Usage |
| `--persona "…"` | Replaces the Domain Expert slot |
| `--domain …` | Domain hint (e.g. ethical, technical) |
| `--export md\|json\|adr` | Extra export block (Markdown verdict always shown) |
| `--min-confidence N` | Gate: flag weak consensus (0–100) |

## Bundled agents

Under `/agents` when the plugin is loaded:

- **topic-analyzer** — topic framing before a full session.
- **verdict-aggregator** — merge vote text or partial outputs.

## Non-goals

- Not a general chat assistant.
- Not legal advice.
- Does not replace human judgment.
- Split verdicts with dissent are valid outcomes.

## v0.4+ integrations (spec only)

Future work (not implemented in this repo): optional bundled MCP (e.g. session persistence in **Supabase**), **n8n** webhook triggers, and CI-style runs via **Claude Agent SDK**. Core deliberation stays in `skills/deliberate/SKILL.md` until those land.

## Version

Plugin manifest: `.claude-plugin/plugin.json` (currently **0.3.0** — dynamic roles, cross-examination, weighted verdict, exports, `min-confidence`).
