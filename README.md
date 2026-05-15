# Tribunal

> *Five minds. One verdict. Zero bullshit.*

Structured five-persona deliberation with optional **brief** or **full** depth, **compact (default) or full-log replies**, **conditional votes with lean**, cross-examination, confidence-weighted verdicts, optional **multi-agent** persona delegation, and JSON or ADR export. Spec: [TRIBUNAL_BIBLE.md](TRIBUNAL_BIBLE.md).

Extra detail for authors lives in [skills/deliberate/reference.md](skills/deliberate/reference.md).

## Install (local dev)

From this repository root:

```bash
claude --plugin-dir .
```

After editing the plugin, run `/reload-plugins` in Claude Code.

Step-by-step smoke tests: [LOCAL_TESTING.md](LOCAL_TESTING.md).

## Command (namespace)

Canonical invocation:

```text
/tribunal:deliberate [flags...] <topic>
```

### Short `/tribunal` without the namespace

Copy [examples/tribunal-command.md](examples/tribunal-command.md) to **your project’s** `.claude/commands/tribunal.md`. Then **`/tribunal`** forwards to the same protocol as `tribunal:deliberate` (same `$ARGUMENTS`). The plugin must still be loaded.

## Examples

### Without `--multi-agent` (single orchestrator)

Same five personas and verdict math; openings and cross-exam are simulated in one model. Good default when you want speed or fewer Task/subagent rows in the terminal.

```text
/tribunal:deliberate --brief For a new BFF: PostgreSQL + JSONB vs a document DB for messy nested payloads—what fits our ops and query patterns?

/tribunal:deliberate --export adr Adopt strict TypeScript (no implicit any) repo-wide this quarter, including generated and legacy packages?

/tribunal:deliberate --domain technical --min-confidence 85 Replace our in-house job queue with Redis Streams: when is the complexity worth it?

/tribunal:deliberate --brief If CI is green but the bug only reproduces on a leap second and prod is NTP-synced UTC, do we block the release or ship and file "works on my epoch"?
```

### With `--multi-agent` (persona subagents)

Opening statements and cross-examination turns are run by separate **persona** subagents when your environment supports it—you get the same weighted verdict, not a backstage pass to every internal step. Expect more latency; the reply can stay **compact** unless you add `--full-log`.

```text
/tribunal:deliberate --multi-agent --full-log --depth full We run multi-region active-active; AP-style cached reads are fine for most domains but billing settlement must be linearizable against our ledger. How do we roll out a CRDT-ish edge layer without ever double-charging during partition or failover?

/tribunal:deliberate --multi-agent --brief Expose our product API to integrators as GraphQL, OpenAPI REST, or both with a compatibility layer—what breaks at scale?

/tribunal:deliberate --multi-agent --depth full Zero-trust mTLS between every service vs selective auth for internal east-west traffic in a growing k8s estate—which liability do we own first?

/tribunal:deliberate --multi-agent --persona "SRE lead — payment rail outages" Should we split the monolith along bounded contexts now, or harden observability and split later?

/tribunal:deliberate --multi-agent --export json --brief Rewrite the p99-critical pricing path from interpreted JS to Rust vs optimize and profile in place for two quarters—which bets our latency budget better?

/tribunal:deliberate --multi-agent --domain ethical --min-confidence 70 Ship an opt-out telemetry SDK that phones home crash breadcrumbs for unpaid tiers—privacy vs debuggability tradeoff?
```

## Flags

| Flag | Purpose |
|------|---------|
| `--help` | Usage |
| `--depth full\|brief` | **full:** richer detail when `--full-log` is on (default depth). **brief:** tighter deliberation; same vote math. |
| `--brief` | Alias for `--depth brief` |
| `--full-log` / `--verbose` | Print the full write-up (panel, arguments, cross-exam, deliberation) in the reply. Default: **compact** verdict only (votes, decision, consensus strength). |
| `--multi-agent` | Run openings and cross-exam through bundled **persona** subagents when Task/subagent delegation works; otherwise one-line fallback + single-model simulation |
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

Plugin manifest: `.claude-plugin/plugin.json` (**0.5.0** — compact default reply; `--full-log` / `--verbose` for the full deliberation write-up).
