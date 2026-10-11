#!/bin/sh
# field-guide-house-rules: SessionStart hook.
#
# Prints the house rules (section 21 of abergman.com/ai, or the user's own
# edited copy) so Claude Code adds them to the session's context, the same
# way a CLAUDE.md would be. Runs on startup, /clear and after compaction.
#
# Which rules: $CLAUDE_CONFIG_DIR/field-guide-house-rules.md (normally
# ~/.claude/field-guide-house-rules.md) if it exists, otherwise the plugin's
# default rules/house-rules.md. /field-guide-house-rules:edit-rules creates
# and edits the personal copy.
#
# Fail open, no network, writes nothing. Output is capped below Claude Code's
# 10,000-character limit for hook context.
#
# Turn it off: FIELD_GUIDE_HOUSE_RULES=off in the "env" block of settings.json,
# or disable the plugin.

case "$(printf '%s' "${FIELD_GUIDE_HOUSE_RULES:-on}" | tr 'A-Z' 'a-z')" in
  off|0|false|no|disabled) exit 0 ;;
esac

root=${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)}
cfg=${CLAUDE_CONFIG_DIR:-$HOME/.claude}
custom="$cfg/field-guide-house-rules.md"

if [ -f "$custom" ] && [ -r "$custom" ]; then
  src=$custom
  origin="the user's own copy at $custom"
else
  src="$root/rules/house-rules.md"
  origin="the plugin's default rules; the user can make a personal copy with /field-guide-house-rules:edit-rules"
fi
[ -r "$src" ] || exit 0

limit=8500
size=$(wc -c < "$src" 2>/dev/null | tr -d ' ')
case "$size" in ''|*[!0-9]*) exit 0 ;; esac
[ "$size" -gt 0 ] || exit 0

printf 'The user installed the field-guide-house-rules plugin. These are their standing working preferences (source: %s). Treat them like their own CLAUDE.md; where they conflict, the user'"'"'s CLAUDE.md files and direct instructions take precedence.\n\n' "$origin"

if [ "$size" -gt "$limit" ]; then
  # Cut at the last complete line inside the limit.
  head -c "$limit" "$src" | sed '$d'
  printf '\n[The house rules file is %s bytes, so it was truncated at about %s. Suggest the user shorten %s.]\n' "$size" "$limit" "$src"
else
  cat "$src"
fi
exit 0
