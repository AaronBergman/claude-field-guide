---
name: handoff
description: Write a handoff doc so a fresh session (or a colleague) can continue this work cold, and record durable lessons in the project's CLAUDE.md. Use before /compact or /clear, at the end of a long session, or when handing work to another agent.
argument-hint: "[optional: what the next session should focus on]"
disable-model-invocation: true
---

# Handoff before compacting or switching

Focus for the next session (optional): $ARGUMENTS

Nothing important should live only in the conversation. Write it down so that compaction, a crash, a usage limit, or a new session loses nothing.

## 1. Write `HANDOFF.md` in the project root

Update it if it exists. Keep each section as short as it can be while complete:

- **Goal**: the end state and what "done" means.
- **Status**: done, in progress, not started. Say plainly what failed or is still unverified.
- **Decisions, each with its reason.** The reasons are what get lost in compaction.
- **Gotchas**: anything surprising, with the fix or workaround.
- **Where things are**: file paths, commands to run, URLs, branches, and any running processes (and whether you stopped them).
- **Next steps**, in order, specific enough to start on immediately.
- **Open questions for the user.**

Use absolute dates. Never put secrets in it; refer to keys by environment variable name.

## 2. Update the project's CLAUDE.md

Add only durable facts a future session needs: how to run and test things, conventions, footguns, and pointers to longer docs. Keep it short, since every character is paid for on every turn; move detail into separate files and link them. If there is no CLAUDE.md yet, ask before creating one.

## 3. Tidy up

- If the folder is a git repository, check whether HANDOFF.md should be committed or added to `.gitignore` (it often holds local paths). Don't commit unless asked.
- Stop any background servers, watchers, or jobs you started, or list them in the handoff if they must keep running.

## 4. Tell the user

Give the paths, then suggest a compact command that pins the key decisions, for example `/compact keep: we chose option A; renamed foo.py to bar.py; see HANDOFF.md`. In the next session (or after compacting), the first prompt can be "read HANDOFF.md and continue".
