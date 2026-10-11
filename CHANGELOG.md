# Changelog

All three plugins share one version number and are released together. Dates are YYYY-MM-DD.

## 1.0.0 (2026-10-10)

First release.

- **field-guide**: 13 skills (research, verify-quotes, meeting, handoff, weekly-update, approaches, brief, scrape-to-sheet, timeline, audit, memo, personalize, guide) and 3 agents (refuter, quote-checker, cold-reader). Bundles the guide as of its 2026-10-10 version and a standard-library quote checker.
- **field-guide-safety**: a quote-aware `rm` guard (also `unlink`, `shred`, `find -delete`, `find -exec rm`, `git clean` without `-n`), and a hook that adds untracked files over 50 MB to `.gitignore`. POSIX sh and awk, fail open, no network.
- **field-guide-house-rules**: injects section 21 of the guide (or your edited copy at `~/.claude/field-guide-house-rules.md`) at session start, plus an em-dash note for prose files, and an `edit-rules` skill.
