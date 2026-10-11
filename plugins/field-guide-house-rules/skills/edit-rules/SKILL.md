---
name: edit-rules
description: View or customize the house rules that the field-guide-house-rules plugin loads into every session. Creates a personal copy you can edit, adds or removes single rules, or resets to the defaults.
argument-hint: "[show | add \"rule\" | remove \"text\" | reset]"
disable-model-invocation: true
---

# Edit the house rules

The field-guide-house-rules plugin injects a short list of working preferences at the start of every session (and after `/clear` and compaction). It reads, in order of preference:

1. The user's personal copy: `~/.claude/field-guide-house-rules.md` (or `$CLAUDE_CONFIG_DIR/field-guide-house-rules.md` if they set `CLAUDE_CONFIG_DIR`).
2. Otherwise the plugin's defaults: `${CLAUDE_PLUGIN_ROOT}/rules/house-rules.md`, which is section 21 of https://abergman.com/ai.

The user's request: $ARGUMENTS

## What to do

- **No arguments, or `show`:** say which file is active, print its rules grouped by heading, and give its size in characters. Mention the commands below in one line.
- **`add "<rule>"`:** make sure the personal copy exists (step "Create the personal copy"), then append the rule as one bullet under the heading it fits best (or a new `## My additions` heading). Keep it to one line. Show the diff.
- **`remove "<text>"`:** make sure the personal copy exists, find the bullet(s) matching the text, show them, and remove them once the match is unambiguous. If several bullets match, list them and ask which.
- **`reset`:** move the personal copy to the trash (`trash <path>` if available, otherwise rename it to `field-guide-house-rules.md.bak-<date>`), so the defaults apply again. Never delete it permanently.
- **Anything else** (for example "make it shorter" or "drop the Python rules"): make sure the personal copy exists, propose the edit as a diff, and apply it after the user agrees.

### Create the personal copy

If the personal copy does not exist yet, copy the defaults to it first (`cp "${CLAUDE_PLUGIN_ROOT}/rules/house-rules.md" ~/.claude/field-guide-house-rules.md`, respecting `CLAUDE_CONFIG_DIR`). Never edit the file inside the plugin folder: plugin updates replace it.

## Rules for the file

- Keep it under about 8,000 characters. The hook truncates anything longer, because Claude Code caps hook context at 10,000 characters, and every character is paid for on every turn.
- One rule per bullet, one line each, phrased as a preference ("Use trash, never rm"), not as a system command.
- Changes apply to new sessions, and to this one after `/clear`.
- If the user removes the em-dash rule, the plugin's em-dash nudge goes quiet on its own. Each hook can also be turned off with an env var in the `"env"` block of settings: `FIELD_GUIDE_HOUSE_RULES=off` (stop injecting the rules) or `FIELD_GUIDE_EM_DASH_CHECK=off` (stop the em-dash nudge).
- If the user would rather keep these rules in their own `~/.claude/CLAUDE.md`, offer to append the active rules there between `<!-- field-guide house rules -->` markers (after backing up the file and showing the diff), and suggest disabling this plugin afterwards so the rules are not loaded twice.
