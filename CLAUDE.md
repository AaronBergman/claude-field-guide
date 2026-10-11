# claude-field-guide: maintainer notes

A Claude Code plugin marketplace (`abergman`) with three plugins built from the public guide "How I use coding agents" at https://abergman.com/ai. Users install with `/plugin marketplace add AaronBergman/claude-field-guide`.

## Layout

- `.claude-plugin/marketplace.json`: the marketplace. Entry names must match each plugin's `plugin.json` name.
- `plugins/field-guide/`: 13 skills (`skills/<name>/SKILL.md`) and 3 agents (`agents/*.md`). No hooks. `skills/verify-quotes/check_quotes.py` is stdlib-only Python. `skills/guide/reference/how-i-use-coding-agents.md` is a generated copy of the guide.
- `plugins/field-guide-safety/`: `hooks/hooks.json` plus `scripts/` (rm guard: `rm-guard.sh` + `rm-guard.awk`; big-file gitignore: `gitignore-big-files.sh` + `field.awk`; shared `json.awk`).
- `plugins/field-guide-house-rules/`: `hooks/hooks.json`, `scripts/` (`inject-rules.sh`, `em-dash-check.sh` + `em-dash.awk`, a copy of `json.awk`), `rules/house-rules.md` (generated from section 21), and the `edit-rules` skill.
- `tests/`: `test_hooks.py` (pipes real hook payloads into every hook under every awk and shell on PATH) and `test_quotes.py`.
- `scripts/sync_from_site.py`: regenerates the two generated files from https://abergman.com/ai.md.

## Rules

- **Content comes only from the public page** (abergman.com/ai) and generic best practice. Nothing from any private or work source, no names of clients, colleagues, internal tools, or infrastructure. Before every release, grep the repo for anything that isn't on the public page.
- No em dashes anywhere (the house rules forbid them; `grep -rn $'\xe2\x80\x94' .` before releasing, ignoring the generated guide copy if the page itself ever gains one). Don't hard-wrap Markdown.
- Hooks must stay POSIX sh + awk (+ git/find), fail open on any surprise, make no network calls, and stay fast. `json.awk` is duplicated in two plugins (each plugin installs separately); keep the copies identical.
- Skill frontmatter: `name`, `description`, `argument-hint`, and `disable-model-invocation` only (the last only for skills with side effects or user-timed workflows). Keep descriptions short: they cost context in every session.
- Don't use Claude Code features newer than the version the README says it was tested on without re-testing.

## Testing

```sh
python3 tests/test_hooks.py && python3 tests/test_quotes.py
claude plugin validate --strict . && for p in plugins/*; do claude plugin validate --strict "$p"; done
```

For an install test that doesn't touch your real config, use a throwaway config dir with the real `claude` binary (not a shell wrapper): `CLAUDE_CONFIG_DIR=$(mktemp -d) claude plugin marketplace add AaronBergman/claude-field-guide`, then `claude plugin install ...`, `claude plugin details ...`. For a live session test in that sandbox, `claude -p` needs an API key in the environment and costs a little.

## Releasing

1. If the page changed: `python3 scripts/sync_from_site.py`, review the diff.
2. Bump `version` in all three `plugins/*/.claude-plugin/plugin.json` (they share one number; installed copies only update when it changes) and add a CHANGELOG entry.
3. Run the tests and validation above; grep for em dashes and for anything private.
4. Commit, push, then tag: `git tag vX.Y.Z && git push origin vX.Y.Z`, plus per-plugin tags with `claude plugin tag plugins/<name> --push`.
5. `gh release create vX.Y.Z --title "vX.Y.Z" --notes-file <notes>` with the CHANGELOG entry.
