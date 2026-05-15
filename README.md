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
[![Verdicts](https://img.shields.io/badge/Verdicts→_docs%2Ftribunal%2F-444?style=for-the-badge)](./docs/tribunal/)

<br>

</div>

---

Tribunal convenes a panel of **five adversarial AI personas** and forces them to argue, cross-examine, and converge on a confidence-weighted verdict — then writes it to disk. The chat reply is a one-line confirmation. The heavy work lands in `docs/tribunal/`.

Built for decisions that deserve more than a single model's gut feeling.

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
                    │      Opening Statements    │
                    │   (one position per role)  │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │      Cross-Examination     │
                    │  5-cycle: each challenges  │
                    │  exactly one peer, defends │
                    │  against exactly one       │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    Confidence-Weighted     │
                    │          Verdict           │
                    │  v̄ = Σ(vᵢ · cᵢ) / Σcᵢ    │
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

## ▸ Install

### From marketplace (inside Claude Code)

The repo ships [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json), so others can subscribe to the catalog and install the plugin like any marketplace extension.

1. **Add the marketplace** — registers the catalog (nothing installed yet):

   ```
   /plugin marketplace add GabryeleSantoro/claude-tribunal
   ```

   Or open `/plugin` → **Marketplaces** → add GitHub `GabryeleSantoro/claude-tribunal`.

2. **Install the plugin** — pulls `tribunal` from that catalog (defaults to user scope; use `/plugin` UI to pick project or local scope):

   ```
   /plugin install tribunal@claude-tribunal
   ```

3. **Reload** — pick up skills and commands:

   ```
   /reload-plugins
   ```

4. **Invoke** — skill is namespaced by plugin id:

   ```
   /tribunal:deliberate [flags...] <topic>
   ```

See also: [Discover and install plugins](https://code.claude.com/docs/en/discover-plugins) · [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces).

### Local development (`--plugin-dir`)

```bash
# From the repo root — loads the plugin into Claude Code
claude --plugin-dir .

# After editing the plugin
/reload-plugins
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

| Flag                       | Values                  | Effect                                                                                                                    |
| -------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `--depth`                  | `full` \| `brief`       | **full** (default): rich topic analysis, full opening paragraphs, prose deliberation. **brief**: tighter, same vote math. |
| `--brief`                  | —                       | Shorthand for `--depth brief`.                                                                                            |
| `--full-log` / `--verbose` | —                       | Write the complete deliberation (panel, arguments, cross-exam) to the output file. Default: compact verdict only.         |
| `--multi-agent`            | —                       | Spawn each persona as a real subagent. Same weighted verdict, higher fidelity, more latency.                              |
| `--persona "…"`            | string                  | Replace the Domain Expert slot with a named custom expert.                                                                |
| `--domain …`               | string                  | Domain hint — e.g. `ethical`, `technical`, `legal`. Shapes role labels.                                                   |
| `--export`                 | `md` \| `json` \| `adr` | Append an extra export block to the output file. Markdown verdict is always written.                                      |
| `--min-confidence N`       | `0`–`100`               | Flag weak consensus: warn when weighted confidence falls below N.                                                         |

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

[Releases](https://github.com/GabryeleSantoro/claude-tribunal/releases) &nbsp;·&nbsp; [Local Testing](LOCAL_TESTING.md) &nbsp;·&nbsp; [reference](skills/deliberate/reference.md) &nbsp;·&nbsp; [License](LICENSE)

<br>

_The panel is always in session._

<br>

</div>
