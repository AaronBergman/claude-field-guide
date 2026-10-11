#!/bin/sh
# field-guide-safety: keep big files out of git.
#
# When a file over FIELD_GUIDE_BIG_FILE_MB megabytes (default 50) appears in a
# git repository during a Claude Code session and is not tracked, ignored, or
# handled by Git LFS, append it to the repository's .gitignore and say so.
# GitHub rejects files over 100 MB, and big data files rarely belong in git.
#
# One script, three events (see hooks.json):
#   SessionStart  records the session start time (an empty marker file), so
#                 later sweeps only consider files from this session.
#   PostToolUse   (Write|Edit) checks the file Claude just wrote.
#   Stop          (end of each turn) checks untracked files in the current
#                 repo that changed since the session started, which catches
#                 downloads and script outputs made through Bash.
#
# Design rules: fail open (exit 0 on anything unexpected), POSIX sh + awk +
# git + find only, no network, and never touch a repository's tracked files.
# The only files written are the repo's .gitignore and the marker files under
# the plugin's data directory.
#
# Turn it off: FIELD_GUIDE_GITIGNORE_BIG=off. Change the threshold:
# FIELD_GUIDE_BIG_FILE_MB=100. Both go in the "env" block of settings.json.

case "$(printf '%s' "${FIELD_GUIDE_GITIGNORE_BIG:-on}" | tr 'A-Z' 'a-z')" in
  off|0|false|no|disabled) exit 0 ;;
esac

MB=${FIELD_GUIDE_BIG_FILE_MB:-50}
case "$MB" in ''|*[!0-9]*) MB=50 ;; esac
[ "$MB" -ge 1 ] 2>/dev/null || MB=50

here=$(dirname "$0")
[ -r "$here/json.awk" ] && [ -r "$here/field.awk" ] || exit 0
command -v git >/dev/null 2>&1 || exit 0

input=$(cat 2>/dev/null) || exit 0
[ -n "$input" ] || exit 0

field() {
  printf '%s\n' "$input" | LC_ALL=C awk -v k="$1" -f "$here/json.awk" -f "$here/field.awk" 2>/dev/null
}

# On Windows, Claude Code sends native paths (C:\Users\...). Git Bash can convert them.
posix_path() {
  case "$1" in
    [A-Za-z]:\\*|[A-Za-z]:/*) command -v cygpath >/dev/null 2>&1 && cygpath -u "$1" && return 0 ;;
  esac
  printf '%s\n' "$1"
}

data=$(posix_path "${CLAUDE_PLUGIN_DATA:-${TMPDIR:-/tmp}/field-guide-safety}")
event=$(field hook_event_name)
sid=$(field session_id | tr -cd 'A-Za-z0-9_-')
marker="$data/sessions/$sid"

json_escape() {
  printf '%s' "$1" | tr '\t' ' ' | tr -d '\000-\010\013-\037' | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | awk 'BEGIN { ORS = "" } NR > 1 { print "\\n" } { print }'
}

# Escape a repo-relative path as a .gitignore pattern anchored at the repo root.
gi_pattern() {
  printf '/%s' "$(printf '%s' "$1" | sed -e 's/[][*?\\]/\\&/g' -e 's/ $/\\ /')"
}

ADDED=""   # newline-separated "path (N MB)" entries

# add_one ROOT REL: ignore REL (relative to ROOT) if it qualifies.
add_one() {
  root=$1; rel=$2
  case "$rel" in ''|.git|.git/*) return 0 ;; esac
  git -C "$root" ls-files --error-unmatch -- "$rel" >/dev/null 2>&1 && return 0   # tracked: leave it alone
  git -C "$root" check-ignore -q -- "$rel" 2>/dev/null && return 0                 # already ignored
  case "$(git -C "$root" check-attr filter -- "$rel" 2>/dev/null)" in *": lfs") return 0 ;; esac
  gi="$root/.gitignore"
  if [ -s "$gi" ] && [ -n "$(tail -c 1 "$gi" 2>/dev/null)" ]; then printf '\n' >> "$gi" || return 0; fi
  if [ -z "$ADDED" ]; then
    printf '# Files over %s MB, added by the field-guide-safety Claude Code plugin\n' "$MB" >> "$gi" || return 0
  fi
  printf '%s\n' "$(gi_pattern "$rel")" >> "$gi" || return 0
  bytes=$(wc -c < "$root/$rel" 2>/dev/null | tr -d ' ')
  size=$(awk -v b="${bytes:-0}" 'BEGIN { printf "%d", b / 1048576 }')
  ADDED="$ADDED$rel ($size MB)
"
}

report() {
  [ -n "$ADDED" ] || exit 0
  list=$(printf '%s' "$ADDED" | awk 'NF { printf "%s%s", (n++ ? ", " : ""), $0 }')
  msg="Added to .gitignore because they are over $MB MB (field-guide-safety): $list"
  if [ "$1" = context ]; then
    printf '{"systemMessage":"%s","hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"%s. The file itself was not changed."}}\n' "$(json_escape "$msg")" "$(json_escape "$msg")"
  else
    printf '{"systemMessage":"%s"}\n' "$(json_escape "$msg")"
  fi
  exit 0
}

case "$event" in
  SessionStart)
    [ -n "$sid" ] || exit 0
    mkdir -p "$data/sessions" 2>/dev/null || exit 0
    [ -f "$marker" ] || : > "$marker" 2>/dev/null
    # Markers are empty files; drop ones older than two weeks.
    find "$data/sessions" -type f -mtime +14 -exec rm -f {} + 2>/dev/null
    exit 0
    ;;

  PostToolUse)
    path=$(posix_path "$(field file_path)")
    [ -n "$path" ] && [ -f "$path" ] || exit 0
    [ -n "$(find "$path" -prune -type f -size +"$MB"M -print 2>/dev/null)" ] || exit 0
    dir=$(dirname "$path")
    root=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null) || exit 0
    [ -n "$root" ] || exit 0
    rootp=$(cd "$root" 2>/dev/null && pwd -P) || exit 0
    full="$(cd "$dir" 2>/dev/null && pwd -P)/$(basename "$path")"
    case "$full" in "$rootp"/*) rel=${full#"$rootp"/} ;; *) exit 0 ;; esac
    add_one "$rootp" "$rel"
    report context
    ;;

  Stop)
    [ -n "$sid" ] && [ -f "$marker" ] || exit 0
    cwd=$(posix_path "$(field cwd)")
    [ -n "$cwd" ] && [ -d "$cwd" ] || exit 0
    root=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null) || exit 0
    [ -n "$root" ] || exit 0
    rootp=$(cd "$root" 2>/dev/null && pwd -P) || exit 0
    big=$(cd "$rootp" && git -c core.quotePath=false ls-files -o --exclude-standard 2>/dev/null \
      | head -n 5000 | grep -v '^"' | sed 's|^|./|' | tr '\n' '\000' \
      | xargs -0 sh -c '[ $# -gt 0 ] && find "$@" -prune -type f -newer "$0" -size +'"$MB"'M -print' "$marker" 2>/dev/null)
    [ -n "$big" ] || exit 0
    while IFS= read -r f; do
      f=${f#./}
      [ -n "$f" ] && add_one "$rootp" "$f"
    done <<EOF
$big
EOF
    report
    ;;
esac
exit 0
