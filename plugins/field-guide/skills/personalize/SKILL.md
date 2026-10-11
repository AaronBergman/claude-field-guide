---
name: personalize
description: Build or extend your own global CLAUDE.md from the field guide's rules - a short interview, then proposed one-line rules that match how you actually work, written only after you approve. Also turns a single correction you keep repeating into a standing rule.
argument-hint: "[optional: a rule to add]"
disable-model-invocation: true
---

# Personalize your CLAUDE.md

Request: $ARGUMENTS

`~/.claude/CLAUDE.md` (or `$CLAUDE_CONFIG_DIR/CLAUDE.md`) is loaded into every session. The best rules come from repeated real annoyances: when you correct an agent the same way twice, make it a rule. Every character is paid for on every turn, so shorter is better.

## If the user passed a rule

Rewrite it as one clear line (a preference, plus the reason if that helps it generalize). Check that it doesn't duplicate or contradict an existing line, show exactly where it would go, and append it once the user says yes.

## Otherwise: a short interview

1. Read the current global CLAUDE.md, if any, and note what it already covers.
2. Ask at most five short questions, all in one message. For example: what they mostly use Claude Code for; what they've had to correct more than once; how much they want it to ask before acting; their writing preferences; their language and tooling preferences (package manager, script style, tests).
3. Propose 8 to 15 one-line rules, drawn from their answers and from the menus in the field guide (sections 6, 20, and 21 of `${CLAUDE_PLUGIN_ROOT}/skills/guide/reference/how-i-use-coding-agents.md`). Only include rules that match how they actually work, and mark which came from their answers.
4. Show the exact text you'd add and where.

## Writing the file (only after approval)

- Back up the existing file first: copy it to `CLAUDE.md.bak-<YYYY-MM-DD>` next to it.
- Put the new rules in one block between `<!-- field-guide rules start -->` and `<!-- field-guide rules end -->`, so they're easy to find and remove. Never rewrite the user's other content.
- If the field-guide-house-rules plugin is enabled, say that it already injects similar rules, and suggest keeping only one of the two.
- Give the path, and note that changes apply to new sessions (or after `/clear`).
