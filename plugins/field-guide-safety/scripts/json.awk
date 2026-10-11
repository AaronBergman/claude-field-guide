# json.awk: tiny helpers for reading a Claude Code hook payload in POSIX awk.
# Loaded with `awk -f json.awk -f <main>.awk`. Run under LC_ALL=C (byte semantics).
#
# jstr(s, key): decoded value of the first JSON string field named `key`.
# jraw(s, key): the same field's raw (still escaped) text, for cheap counting.
#
# A quote-key-quote-colon sequence can only be an object key in valid JSON,
# because quote characters inside string values are always escaped. Keys that
# appear in both tool_input and tool_response are taken from the first
# occurrence, which is tool_input in Claude Code's payloads.

function jraw(s, key,    re, m) {
  re = "\"" key "\"[ \t\r\n]*:[ \t\r\n]*\"([^\"\\\\]|\\\\.)*\""
  if (!match(s, re)) return ""
  m = substr(s, RSTART, RLENGTH)
  sub("^\"" key "\"[ \t\r\n]*:[ \t\r\n]*\"", "", m)
  return substr(m, 1, length(m) - 1)
}

function jstr(s, key,    m, out, p, c) {
  m = jraw(s, key)
  out = ""
  while ((p = index(m, "\\")) > 0) {
    out = out substr(m, 1, p - 1)
    c = substr(m, p + 1, 1)
    if (c == "n") { out = out "\n"; m = substr(m, p + 2) }
    else if (c == "r" || c == "t" || c == "b" || c == "f") { out = out " "; m = substr(m, p + 2) }
    else if (c == "u") { out = out " "; m = substr(m, p + 6) }
    else { out = out c; m = substr(m, p + 2) }
  }
  return out m
}
