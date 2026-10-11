# em-dash.awk: reads a PostToolUse payload for Write or Edit (needs json.awk).
# Prints "<count>\t<path>" when the text Claude just wrote to a prose file adds
# em dashes (U+2014), and nothing otherwise. Run under LC_ALL=C.

# Count em dashes in a raw (still JSON-escaped) string: raw UTF-8 bytes, plus
# \u2014 escapes. Escaped backslashes are removed first so that a literal
# backslash followed by "u2014" in the text is not miscounted.
function count(s,    n) {
  n = gsub(/\342\200\224/, "", s)
  gsub(/\\\\/, "", s)
  n += gsub(/\\u2014/, "", s)
  return n
}

{ RAW = RAW $0 "\n" }

END {
  tool = jstr(RAW, "tool_name")
  path = jstr(RAW, "file_path")
  lp = tolower(path)
  if (lp !~ /\.(md|markdown|mdx|txt|text|rst|adoc|asciidoc|org|tex|html|htm)$/) exit 0
  if (tool == "Write") n = count(jraw(RAW, "content"))
  else if (tool == "Edit") n = count(jraw(RAW, "new_string")) - count(jraw(RAW, "old_string"))
  else exit 0
  if (n > 0) printf "%d\t%s", n, path
}
