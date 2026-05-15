# Tribunal

> *Five minds. One verdict. Zero bullshit.*

Structured five-persona deliberation with optional **brief** or **full** depth, **conditional votes with lean**, cross-examination, confidence-weighted verdicts, optional **multi-agent** persona delegation, and JSON or ADR export. Spec: [TRIBUNAL_BIBLE.md](TRIBUNAL_BIBLE.md).

Extra detail for authors lives in [skills/deliberate/reference.md](skills/deliberate/reference.md).

## Install (local dev)

From this repository root:

```bash
claude --plugin-dir .
```

After editing the plugin, run `/reload-plugins` in Claude Code.

## Command (namespace)

Canonical invocation:

```text
/tribunal:deliberate [flags...] <topic>
```

### Short `/tribunal` without the namespace

Copy [examples/tribunal-command.md](examples/tribunal-command.md) to **your project’s** `.claude/commands/tribunal.md`. Then **`/tribunal`** forwards to the same protocol as `tribunal:deliberate` (same `$ARGUMENTS`). The plugin must still be loaded.

## Examples

```text
/tribunal:deliberate Should I use PostgreSQL or MongoDB for this project?

/tribunal:deliberate --brief --persona "Pokemon card market expert" Is this card underpriced at €45?

/tribunal:deliberate --domain ethical Is it justified to ship a product with known minor bugs?

/tribunal:deliberate --export adr Should we migrate our backend to Edge Functions?

/tribunal:deliberate --min-confidence 85 What's the best clustering algorithm for this dataset?

/tribunal:deliberate --multi-agent --depth full Pick a regional DB vendor
```

## Flags

| Flag | Purpose |
|------|---------|
| `--help` | Usage |
| `--depth full\|brief` | **full:** rich phases (default). **brief:** condensed phases; same vote math. |
| `--brief` | Alias for `--depth brief` |
| `--multi-agent` | Delegate Phase 3 openings + Phase 4 challenge/defense to bundled **persona** subagents when Task/subagent delegation works; otherwise one-line fallback + simulation |
| `--persona "…"` | Replaces the Domain Expert slot |
| `--domain …` | Domain hint (e.g. ethical, technical) |
| `--export md\|json\|adr` | Extra export block (Markdown verdict always shown) |
| `--min-confidence N` | Gate: flag weak consensus (0–100) |

## Bundled agents

**Personas** (for `--multi-agent`): `tribunal-persona-domain-expert`, `tribunal-persona-devils-advocate`, `tribunal-persona-systems-thinker`, `tribunal-persona-logician`, `tribunal-persona-mediator`.

**Helpers:** `topic-analyzer`, `verdict-aggregator` (optional pre/post).

## Non-goals

- Not a general chat assistant.
- Not legal advice.
- Does not replace human judgment.
- Split verdicts with dissent are valid outcomes.

## Version

Plugin manifest: `.claude-plugin/plugin.json` (**0.4.0** — depth modes, vote `lean`, example `/tribunal` command, multi-agent personas).
