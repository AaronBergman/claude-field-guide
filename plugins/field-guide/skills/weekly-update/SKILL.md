---
name: weekly-update
description: Draft a "what I did this week" update grouped by project, from git history, notes, and files changed since a date, opening with the claims that could not be verified from the files. Use for weekly updates, status reports, and 1:1 prep.
argument-hint: "[since date] [folders to scan]"
disable-model-invocation: true
---

# Weekly update

Input: $ARGUMENTS (since when, and which folders; default: the last 7 days, the current folder)

## Gather (read-only)

- **Git:** for each repository in scope, `git log --since=<date> --author=<the user's git email> --stat`, plus uncommitted changes. When scanning a parent folder, find the repositories rather than assuming.
- **Files changed** since the date (`find <folder> -newermt <date> -type f`, skipping dependency, cache, and build folders), notes and meeting notes, and last week's update if one exists. Last week's file is the format to follow.
- **Live numbers** only if they can be measured now (rows, users, whether a deployment is up), each with its date.

## Write `weekly-update-<YYYY-MM-DD>.md`

1. **Could not verify from the files**: claims the user must confirm before sending, such as "whether the memo actually went out" or "whether the invoice was sent". This list goes first.
2. **One section per project**: what changed and why it matters, in plain language for the reader (assume a manager with context on the projects but not on the code). Link to artifacts.
3. **Blockers**, then **next week's plan**.
4. **Suggested notes for a 1:1**: decisions needed and things to flag early.

About two pages when pasted into Google Docs. Lead with outcomes, not activity. Absolute dates, no hype, no em dashes. Don't send it anywhere; the user reviews and pastes it.
