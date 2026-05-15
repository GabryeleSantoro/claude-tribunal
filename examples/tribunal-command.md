---
description: Short alias for Tribunal — forwards to the tribunal plugin skill (requires plugin loaded)
disable-model-invocation: true
---

# /tribunal (project command)

**Install:** Copy this file to your project as:

```text
.claude/commands/tribunal.md
```

Then use **`/tribunal`** from Claude Code the same way you would **`/tribunal:deliberate`** (all flags and topic apply).

---

## Instructions for the assistant

1. **Plugin:** The user must have the **tribunal** plugin enabled (e.g. `claude --plugin-dir /path/to/claude-tribunal` or marketplace install + `/reload-plugins`). If Tribunal is not available, say so and suggest loading the plugin.

2. **Run:** Execute the **`tribunal:deliberate`** skill end-to-end. Pass through the user’s text **verbatim** as if they had run:

   ```text
   /tribunal:deliberate $ARGUMENTS
   ```

   Use the same protocol, phases, outputs, and flags (`--brief`, `--depth`, `--multi-agent`, `--persona`, `--domain`, `--export`, `--min-confidence`, `--help`) defined in that skill.

3. **Output:** Produce the **⚖️ Tribunal Verdict** Markdown (and JSON/ADR appendices if requested). Do not replace the skill with a casual chat response.

If `$ARGUMENTS` is empty, print the skill’s help text from `tribunal:deliberate` (or ask the user to run `/tribunal:deliberate --help`).
