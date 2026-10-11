---
name: approaches
description: Answer a "how should I..." question without changing anything yet - 2-3 concrete approaches with tradeoffs and a recommendation. Use when the user says "don't do anything yet", "just answer", or "what are my options", or before a task with several plausible approaches such as scraping, file processing, migrations, or anything with platform constraints.
argument-hint: "[the question or task]"
---

# Explain first, then build

The question: $ARGUMENTS

This is question mode. Don't create, edit, move, or delete files, install anything, or run anything with side effects. Read-only inspection (reading files, listing folders, `git status`, checking versions, reading docs) is fine and usually makes the answer better.

## Answer shape

1. **The goal**, restated in a sentence or two. If the real goal behind the literal ask seems different, say so.
2. **Two or three approaches.** For each: how it works, what it costs (time, money, complexity, upkeep), what can go wrong, and when it's the right choice. Include known platform constraints: rate limits, terms of service, logins and CAPTCHAs, file-size limits, things the agent can't observe.
3. **Your recommendation**, in a short paragraph, and what would change your mind.
4. **The prompt to go ahead**, if useful, for example `/goal <end state>. Done means <test>. Constraints: <...>.`

Keep it readable in a minute or two. If there is one obviously right answer, say so instead of inventing alternatives.
