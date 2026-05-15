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

   Use the same protocol, outputs, and flags (`--brief`, `--depth`, `--full-log`, `--verbose`, `--multi-agent`, `--persona`, `--domain`, `--export`, `--min-confidence`, `--help`) defined in that skill.

3. **Output:** Run **`tribunal:deliberate`** so the verdict is **written to** `docs/tribunal/{date}_{slug}.md` per that skill; reply in chat with only the short confirmation (path + one-line decision) unless a write failed. Include JSON/ADR in the same file when requested. Do not replace the skill with a casual chat response or paste the full verdict into chat.

If `$ARGUMENTS` is empty, print the skill’s help text from `tribunal:deliberate` (or ask the user to run `/tribunal:deliberate --help`).
