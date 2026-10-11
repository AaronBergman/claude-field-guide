# claude-field-guide

The field guide [How I use coding agents](https://abergman.com/ai) (abergman.com/ai), packaged as installable Claude Code plugins: its prompt library as skills, its verification habits as agents, its `rm` guard and big-file rule as hooks, and its "paste this into your CLAUDE.md" rules as an optional, editable session preamble.

The guide was written by Claude from Aaron Bergman's own prompt history and setup, and so was this repo. It is one heavy user's practice: opinionated, in places idiosyncratic. Take what helps.

## Install

In Claude Code (terminal, desktop app Code tab, or IDE extension):

```
/plugin marketplace add AaronBergman/claude-field-guide
/plugin install field-guide@abergman
/plugin install field-guide-safety@abergman
```

Optional and opinionated (it changes how Claude behaves in every session):

```
/plugin install field-guide-house-rules@abergman
```

Or from your shell:

```sh
claude plugin marketplace add AaronBergman/claude-field-guide
claude plugin install field-guide@abergman
claude plugin install field-guide-safety@abergman
claude plugin install field-guide-house-rules@abergman   # optional
```

New sessions pick the plugins up automatically; in a session that is already open, run `/reload-plugins`. To check what loaded: `claude plugin details field-guide`.

**claude.ai and Cowork.** Anthropic's docs say a GitHub marketplace like this one can also be added from **Customize > Plugins > Add > Add marketplace** with the repository URL `https://github.com/AaronBergman/claude-field-guide`. In chat only the skills load; in Cowork, skills, agents, and hooks load. I have not tested those two surfaces, only Claude Code.

## What you get

There are three plugins, so you can take the skills without any change to Claude's behavior.

| Plugin | What it adds | Always-on cost |
|---|---|---|
| `field-guide` | 13 skills and 3 agents. Nothing runs until you (or Claude) invoke one. | About 1,600 tokens of skill descriptions per session |
| `field-guide-safety` | 2 hooks: block permanent deletes, gitignore big files | None (hooks run outside the model's context) |
| `field-guide-house-rules` | Injects the guide's working rules at session start; nudges away from em dashes | About 1,400 tokens per session for the rules |

### field-guide: skills

Run a skill by typing it, or just describe the task and Claude picks the skill when it fits (except the ones marked "manual", which only run when you type them).

| Skill | What it does |
|---|---|
| `/field-guide:research` | Research a question or check one claim. Every claim graded VERIFIED, REPORTED, or INFERRED with a source; verbatim quotes; null results with a positive control; a separate refutation pass; ends with "what I could not verify". |
| `/field-guide:verify-quotes` | Checks every quote in a draft against its sources with a bundled script (Python standard library, no network): exact, close, or not found, with the nearest real wording. |
| `/field-guide:meeting` | A transcript (or recording) in: notes with a TL;DR of decisions, timestamps, owners and dates, verbatim guidance. Then it does your action items and drafts, never sends, anything for other people. |
| `/field-guide:handoff` | Manual. Writes HANDOFF.md and updates CLAUDE.md so a fresh session can continue cold, then suggests a `/compact` line that pins the decisions. |
| `/field-guide:weekly-update` | Manual. "What I did this week" from git history and changed files, grouped by project, opening with what it could not verify. |
| `/field-guide:approaches` | Explain-first mode: 2-3 approaches with tradeoffs and a recommendation, no changes made. |
| `/field-guide:brief` | Turns a rough ask into a strong `/goal` prompt (end state, acceptance test, guardrails, budget, judgment principle), an unattended runbook, or a context-firewalled brief for another agent. |
| `/field-guide:scrape-to-sheet` | A page or site into structured data and a Google-Sheets-ready CSV with a source column, politely, with a row count and a list of gaps. |
| `/field-guide:timeline` | A folder of documents into `timeline.md` and `.csv`: one row per dated event, with source file and a verbatim quote. |
| `/field-guide:audit` | Read-only adversarial audit: finder agents per dimension, refuters that default to "not real", only survivors reported, with a fix plan. |
| `/field-guide:memo` | Writing for people who weren't in the conversation: named reader and length, answer first, citations, then a cold-reader check. |
| `/field-guide:personalize` | Manual. Interviews you briefly and proposes your own global CLAUDE.md rules; writes nothing until you approve, and backs up first. |
| `/field-guide:guide` | Answers "how should I..." questions from the full guide, which is bundled with the skill. |

### field-guide: agents

| Agent | Role |
|---|---|
| `field-guide:refuter` | Given one finding and its evidence, re-checks the sources and tries to prove it wrong. Defaults to NOT REAL when uncertain. |
| `field-guide:quote-checker` | Checks a draft's quotes against sources and returns a table, keeping the source text out of your main conversation. |
| `field-guide:cold-reader` | Reads a draft as its intended reader with no context and lists what's unclear, unsupported, overclaimed, or too long. |

Agents use whatever model your session uses (`model: inherit`). Verification is the kind of work where a weaker model saves little and misses a lot.

### field-guide-safety: hooks

**The `rm` guard** (before every Bash command) blocks commands that permanently delete files and tells Claude to use a recoverable delete instead: `trash` (built into macOS 15 and later), `gio trash` or `trash-put` on Linux, or moving the file into a `.trash/` folder if no trash command exists.

It blocks `rm`, `unlink`, `shred`, `find ... -delete`, `find ... -exec rm`, and `git clean` (unless `-n` / `--dry-run`), including through `sudo`, `env`, `xargs`, `timeout`, `nohup`, `bash -c '...'`, `eval`, command substitution, and heredocs fed to a shell. It reads quotes like a shell does, so `git commit -m "remove x; rm y"`, `echo "rm -rf /"`, `grep "rm" file`, and heredoc text written to a file are not blocked. `git rm`, `rmdir`, and `docker rm` are allowed.

It is a seatbelt, not a sandbox. It does not see deletes done inside other programs (`python -c "os.remove(...)"`, perl, node, Makefile targets), a script piped into a shell (`curl ... | sh`), a command name stored in a variable, or the Windows PowerShell tool. If you explicitly want a permanent delete, Claude will tell you the guard blocked it, and you can run the command yourself.

**Big files out of git** (after Write and Edit, and at the end of each turn): when a file over 50 MB appears in a git repository during the session and isn't tracked, already ignored, or handled by Git LFS, it's appended to that repository's `.gitignore` (anchored to the repo root, glob characters escaped) and you see a one-line notice. GitHub rejects files over 100 MB, and big data files rarely belong in git. It never touches tracked files, and only considers files created or changed since the session started.

Both hooks are POSIX `sh` plus `awk`, `git`, and `find`. They need no Python, Node, or jq, make no network calls, and fail open: if anything unexpected happens, the hook lets the action through rather than breaking your session. They are tested with macOS awk, gawk, mawk, and busybox awk under sh, dash, and bash.

### field-guide-house-rules

At session start (and after `/clear` and compaction), this injects the short rules list from section 21 of the guide: work end to end, say before anything hard to undo, be earnest rather than sycophantic, grade claims, quote verbatim, no em dashes, `trash` not `rm`, keep context in files, and so on. Read the full list in [`rules/house-rules.md`](plugins/field-guide-house-rules/rules/house-rules.md) before installing. Some lines are personal preferences (for example "Python via uv" and "scripts take no command-line arguments").

It's framed to Claude as your preferences, with your own CLAUDE.md files and direct instructions taking precedence where they conflict.

To customize, run `/field-guide-house-rules:edit-rules`. It copies the defaults to `~/.claude/field-guide-house-rules.md`, which then replaces the defaults; you can add or remove single rules (`/field-guide-house-rules:edit-rules add "Always write tests first"`) or edit the file directly. Plugin updates never overwrite your copy. Keep it under about 8,000 characters; longer files are truncated.

It also adds a gentle note to Claude's context when it writes em dashes into prose files (`.md`, `.txt`, `.html`, and similar). It never blocks or edits anything, ignores code files, and goes quiet on its own if your copy of the rules no longer mentions em dashes.

## Turning things off

Disable a whole plugin with `/plugin` (Installed tab) or `claude plugin disable field-guide-safety@abergman`.

Turn off a single hook with an environment variable in the `env` block of `~/.claude/settings.json` (or a project's `.claude/settings.json`), then start a new session:

```json
{
  "env": {
    "FIELD_GUIDE_RM_GUARD": "off",
    "FIELD_GUIDE_GITIGNORE_BIG": "off",
    "FIELD_GUIDE_BIG_FILE_MB": "100",
    "FIELD_GUIDE_HOUSE_RULES": "off",
    "FIELD_GUIDE_EM_DASH_CHECK": "off"
  }
}
```

| Variable | Effect |
|---|---|
| `FIELD_GUIDE_RM_GUARD=off` | Stop blocking `rm` and other permanent deletes |
| `FIELD_GUIDE_GITIGNORE_BIG=off` | Stop adding big files to `.gitignore` |
| `FIELD_GUIDE_BIG_FILE_MB=<n>` | Size threshold in MB for the gitignore hook (default 50) |
| `FIELD_GUIDE_HOUSE_RULES=off` | Stop injecting the house rules (and the em-dash note) |
| `FIELD_GUIDE_EM_DASH_CHECK=off` | Keep the rules but drop the em-dash note |

## Updating and uninstalling

Third-party marketplaces don't auto-update by default. To update, run `/plugin`, open the **Marketplaces** tab, select `abergman`, and choose **Update marketplace** (or turn on auto-update there). From the shell: `claude plugin update field-guide@abergman`, and the same for the other two.

To uninstall:

```
/plugin uninstall field-guide@abergman
/plugin uninstall field-guide-safety@abergman
/plugin uninstall field-guide-house-rules@abergman
/plugin marketplace remove abergman
```

What stays behind: your personal `~/.claude/field-guide-house-rules.md` if you made one (move it to the trash if you don't want it), and any `.gitignore` lines the safety hook added (each block starts with a comment naming the plugin). The hook's session-marker files live in the plugin's data folder, which Claude Code deletes on uninstall.

## Privacy

No telemetry. The hooks make no network calls and read only the hook payload Claude Code passes them, plus file sizes and git metadata in your repositories. The quote checker reads only the files you give it. Skills run in your normal Claude Code session, under your normal permissions, and only when invoked.

## Requirements

- Claude Code with plugin support. Built and tested on Claude Code 2.1.280 on macOS.
- Hooks: macOS or Linux. On Windows they need Git for Windows, because they run under Git Bash; CI runs the hook tests on Windows too, but I haven't tried them in a real Windows Claude Code session. The skills and agents work anywhere Claude Code runs.
- The quote checker needs Python 3 (standard library only). Without it, the skill falls back to `grep`.

## Development

```sh
python3 tests/test_hooks.py      # hook tests under every awk and shell found on PATH
python3 tests/test_quotes.py     # quote checker tests
claude plugin validate --strict .
for p in plugins/*; do claude plugin validate --strict "$p"; done
python3 scripts/sync_from_site.py   # refresh the bundled guide and section 21 from abergman.com/ai.md
```

CI runs the same checks on Ubuntu, macOS, and Windows (Git Bash). To test a change without installing, start Claude Code with `claude --plugin-dir ./plugins/field-guide` (repeat `--plugin-dir` for each plugin).

## License

MIT (see [LICENSE](LICENSE)), covering everything in this repository, including the bundled copy of the guide. The canonical, latest version of the guide lives at [abergman.com/ai](https://abergman.com/ai).
