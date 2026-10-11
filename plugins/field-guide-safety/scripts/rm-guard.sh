#!/bin/sh
# field-guide-safety: PreToolUse hook for the Bash tool.
#
# Blocks commands that permanently delete files (rm, unlink, shred,
# find -delete, find -exec rm, git clean without -n) and tells Claude to use a
# recoverable delete instead: the system Trash, or moving the file aside.
# The parsing lives in rm-guard.awk (a small quote-aware shell tokenizer).
#
# Design rules:
#   - Fail open. If anything is unexpected (no awk, bad JSON, a crash), exit 0
#     and let the command through. A safety hook must never brick a session.
#   - Only POSIX sh and awk. No network. Writes no files.
#   - A seatbelt, not a sandbox: python, perl, make targets and similar can
#     still delete things. See the README for the full list of gaps.
#
# Turn it off: set FIELD_GUIDE_RM_GUARD=off, for example in ~/.claude/settings.json:
#   { "env": { "FIELD_GUIDE_RM_GUARD": "off" } }
# or disable the whole plugin with /plugin.

case "$(printf '%s' "${FIELD_GUIDE_RM_GUARD:-on}" | tr 'A-Z' 'a-z')" in
  off|0|false|no|disabled) exit 0 ;;
esac

here=$(dirname "$0")
[ -r "$here/rm-guard.awk" ] && [ -r "$here/json.awk" ] || exit 0

verdict=$(LC_ALL=C awk -f "$here/json.awk" -f "$here/rm-guard.awk" 2>/dev/null) || exit 0
case "$verdict" in
  RM|FIND_DELETE|GIT_CLEAN) ;;
  *) exit 0 ;;
esac

# Suggest the recoverable alternative that exists on this machine.
if command -v trash >/dev/null 2>&1; then
  how='trash <path>        (moves it to the Trash, so it can be recovered)'
elif command -v gio >/dev/null 2>&1; then
  how='gio trash <path>    (moves it to the desktop Trash, so it can be recovered)'
elif command -v trash-put >/dev/null 2>&1; then
  how='trash-put <path>    (trash-cli, so it can be recovered)'
else
  how='mkdir -p .trash && mv <path> .trash/    (no trash command on this machine; this keeps it recoverable)'
fi

case "$verdict" in
  FIND_DELETE)
    what='`find ... -delete` permanently deletes everything it matches.'
    alt="Run the same find without -delete to preview the matches, then move them to the trash one by one or with -exec, using:
  $how" ;;
  GIT_CLEAN)
    what='`git clean` permanently deletes untracked files, and git has no copy of them to restore.'
    alt="Preview with \`git clean -n\` (plus -d or -x as needed), then move the listed paths to the trash with:
  $how" ;;
  *)
    what='`rm` (like unlink and shred) permanently deletes files.'
    alt="Use a recoverable delete instead:
  $how" ;;
esac

cat >&2 <<EOF
Blocked by the field-guide-safety plugin: $what
$alt
Do not work around this with another permanent-delete method (python, perl, find -delete, and so on).
If the user explicitly asked for a permanent delete, tell them this guard blocked it and let them run the command themselves. They can also turn the guard off by setting FIELD_GUIDE_RM_GUARD=off in the "env" block of their Claude Code settings.
EOF
exit 2
