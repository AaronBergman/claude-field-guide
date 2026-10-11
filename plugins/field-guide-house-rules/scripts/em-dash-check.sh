#!/bin/sh
# field-guide-house-rules: PostToolUse hook for Write and Edit.
#
# If Claude just wrote em dashes into a prose file (.md, .txt, .html, ...),
# add a short note to Claude's context asking it to rewrite them, because the
# house rules say no em dashes. Never blocks anything and never edits files.
# Code files are ignored. It stays quiet if the active house rules no longer
# mention em dashes (so editing that rule out of your copy turns this off too).
#
# Turn it off: FIELD_GUIDE_EM_DASH_CHECK=off in the "env" block of settings.json.

case "$(printf '%s' "${FIELD_GUIDE_EM_DASH_CHECK:-on}" | tr 'A-Z' 'a-z')" in
  off|0|false|no|disabled) exit 0 ;;
esac
case "$(printf '%s' "${FIELD_GUIDE_HOUSE_RULES:-on}" | tr 'A-Z' 'a-z')" in
  off|0|false|no|disabled) exit 0 ;;
esac

here=$(dirname "$0")
root=${CLAUDE_PLUGIN_ROOT:-$(cd "$here/.." 2>/dev/null && pwd)}
cfg=${CLAUDE_CONFIG_DIR:-$HOME/.claude}
rules="$cfg/field-guide-house-rules.md"
[ -f "$rules" ] || rules="$root/rules/house-rules.md"
grep -qi 'em dash' "$rules" 2>/dev/null || exit 0
[ -r "$here/json.awk" ] && [ -r "$here/em-dash.awk" ] || exit 0

out=$(LC_ALL=C awk -f "$here/json.awk" -f "$here/em-dash.awk" 2>/dev/null) || exit 0
[ -n "$out" ] || exit 0
n=$(printf '%s' "$out" | cut -f1)
path=$(printf '%s' "$out" | cut -f2-)
case "$n" in ''|*[!0-9]*) exit 0 ;; esac

json_escape() {
  printf '%s' "$1" | tr '\t' ' ' | tr -d '\000-\010\013-\037' | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | awk 'BEGIN { ORS = "" } NR > 1 { print "\\n" } { print }'
}

if [ "$n" = 1 ]; then what="1 em dash"; else what="$n em dashes"; fi
msg="Style note (field-guide-house-rules): the text just written to $path adds $what. The user's house rules say no em dashes; rewrite them with commas, colons, parentheses, or periods, unless the dash is inside a verbatim quote or in existing text you were asked to preserve."
printf '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"%s"}}\n' "$(json_escape "$msg")"
exit 0
