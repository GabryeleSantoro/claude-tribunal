# Local testing guide

Quick checks that Tribunal loads and runs correctly from your machine.

## Prerequisites

- [Claude Code](https://code.claude.com/docs) installed (`claude --version` works).
- This repo cloned locally.

## 1. Start Claude Code with the plugin

From the **repository root** (the folder that contains `.claude-plugin/` and `skills/`):

```bash
cd /path/to/claude-tribunal
claude --plugin-dir .
```

Or pass an absolute path:

```bash
claude --plugin-dir /path/to/claude-tribunal
```

Use the same project folder you want to deliberate _about_ if you care about repo context; the plugin path is independent of that choice.

## 2. Reload after edits

Whenever you change `SKILL.md`, agents, or `plugin.json`:

```text
/reload-plugins
```

## 3. Smoke tests (in Claude Code)

**Help / parsing**

```text
/tribunal:deliberate --help
```

**Minimal run (fast)**

```text
/tribunal:deliberate --brief Choose tabs or spaces for indentation?
```

**Full depth (longer deliberation detail when you use `--full-log`)**

```text
/tribunal:deliberate --depth full Should we add a nightly CI job?
```

**Export + flags**

```text
/tribunal:deliberate --brief --export json Is this naming convention OK?
```

**Optional subagents** (only if your environment supports Task/subagent delegation)

```text
/tribunal:deliberate --multi-agent --brief Pick a logging library for a small CLI
```

After a successful run, open **`docs/tribunal/*.md`** for the full verdict; the chat reply is only a short confirmation with the path. Use **`--full-log`** for the long deliberation in that file.

If `--multi-agent` cannot delegate, the skill should still complete with its documented fallback.

## 4. Validate the manifest (optional)

From the repo root:

```bash
claude plugin validate .
```

Fix any reported issues in `.claude-plugin/plugin.json`, skill frontmatter, or agent YAML headers.

## 5. Common issues

| Symptom                         | What to try                                                                                         |
| ------------------------------- | --------------------------------------------------------------------------------------------------- |
| Unknown command / skill missing | Confirm you started with `--plugin-dir` pointing at this repo, then `/reload-plugins`.              |
| Old behavior after edits        | Run `/reload-plugins` again; confirm you saved files in the same tree you passed to `--plugin-dir`. |
| Plugin errors in UI             | Open `/plugin` → **Errors** tab for load details.                                                   |

## 6. Optional: project shortcut `/tribunal`

Does not affect loading; only adds a shorter command **inside a project** that forwards to the skill. See [examples/tribunal-command.md](examples/tribunal-command.md).

## 7. Optional: local API benchmarks (tokens, latency, rubric)

Measures **input/output tokens**, **wall time**, and a **heuristic quality score** against the Tribunal Markdown shape (plus an optional LLM judge). Results are written under **`benchmarks/.local/results/`**, which is gitignored.

From the repo root:

```bash
cd benchmarks
python3 -m venv .venv && source .venv/bin/activate   # optional
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...
# Optional: TRIBUNAL_BENCHMARK_MODEL, TRIBUNAL_BENCHMARK_MAX_TOKENS, TRIBUNAL_BENCHMARK_JUDGE_MODEL
python run_benchmarks.py --dry-run    # planned cases only (no API)
python run_benchmarks.py              # runs cases in cases.json
```

Add **`--judge-model claude-haiku-4-20250314`** (or set `TRIBUNAL_BENCHMARK_JUDGE_MODEL`) for a second call that scores structure / verdict math / topic fit (extra tokens and latency).
