# rm-guard.awk: reads a Claude Code PreToolUse payload (JSON) on stdin.
# Prints RM, FIND_DELETE or GIT_CLEAN when the Bash command would permanently
# delete files, and prints nothing otherwise. Needs json.awk loaded first.
#
# It is a small, quote-aware shell tokenizer, not a full shell parser:
#   - separators (; & | ( ) newline backtick $( ) split simple commands, but
#     only outside quotes, so `git commit -m "x; rm y"` is not flagged;
#   - quoted text is data, except what a shell will run anyway: the string
#     after `sh -c` / `bash -c`, the arguments of `eval`, and `$(...)` or
#     backticks inside double quotes;
#   - heredoc bodies are data, unless the heredoc feeds a shell (`bash <<EOF`);
#   - wrappers such as sudo, env, xargs, nohup, time, timeout are skipped to
#     find the real command.
# Known gaps (documented in the README): deletes done inside python/perl/node,
# Makefile targets, `| sh` with a piped script, variables used as the command.

function base(t) { sub(/.*\//, "", t); return t }
function isdel(b) { return (b == "rm" || b == "unlink" || b == "shred") }

function addword() {
  if (INWORD) T[++NT] = W
  W = ""; INWORD = 0
}

function endseg(   r) {
  addword()
  r = check()
  NT = 0
  if (r != "" && VERDICT == "") VERDICT = r
}

# Text from position p up to the matching close paren (single quotes skipped).
function paren(s, p,    d, j, n, c, k) {
  d = 1; n = length(s)
  for (j = p; j <= n; j++) {
    c = substr(s, j, 1)
    if (c == "'") { k = index(substr(s, j + 1), "'"); if (k == 0) return substr(s, p); j += k; continue }
    if (c == "(") d++
    else if (c == ")") { d--; if (d == 0) return substr(s, p, j - p) }
  }
  return substr(s, p)
}

# Is the command of the current (partial) simple command a shell?
function seg_is_shell(   i, w) {
  for (i = 1; i <= NT; i++) {
    w = T[i]
    if (w ~ /^[A-Za-z_][A-Za-z0-9_]*=/ || substr(w, 1, 1) == "-") continue
    if ((w in WRAP) && !(w in SHELL)) continue
    return (base(w) in SHELL)
  }
  return 0
}

# Parse a heredoc operator at position i (s[i] == "<", s[i+1] == "<").
function heredoc_op(s, i,    j, dash, d, c) {
  addword()
  j = i + 2; dash = 0
  if (substr(s, j, 1) == "-") { dash = 1; j++ }
  while (substr(s, j, 1) == " " || substr(s, j, 1) == "\t") j++
  d = ""
  while (j <= length(s)) {
    c = substr(s, j, 1)
    if (c ~ /[ \t\r\n;&|()<>]/) break
    if (c != "'" && c != "\"" && c != "\\") d = d c
    j++
  }
  # A numeric "delimiter" is almost always an arithmetic shift ($((1<<2))), not a heredoc.
  if (d != "" && d !~ /^[0-9]+$/) { NH++; HD[NH] = d; HDASH[NH] = dash; HCODE[NH] = seg_is_shell() }
  return j
}

function rx_escape(d) { gsub(/[^A-Za-z0-9_]/, "\\\\&", d); return d }

# At a newline (position i) with pending heredocs: consume their bodies.
function skip_heredocs(s, i,    pos, h, rest, re, body) {
  pos = i + 1
  for (h = 1; h <= NH; h++) {
    rest = substr(s, pos)
    re = "(^|\n)" (HDASH[h] ? "\t*" : "") rx_escape(HD[h]) "(\n|$)"
    if (match(rest, re)) {
      body = substr(rest, 1, RSTART - 1)
      pos = pos + RSTART - 1 + RLENGTH
    } else {
      body = rest
      pos = length(s) + 1
    }
    if (HCODE[h]) Q[++NQ] = body
  }
  NH = 0
  return pos
}

# Decide about the simple command collected in T[1..NT].
function check(   i, w, o, j, k, b, sb, s) {
  i = 1
  while (i <= NT) {
    w = T[i]
    if (w == "") { i++; continue }
    if (w ~ /^[A-Za-z_][A-Za-z0-9_]*=/) { i++; continue }        # VAR=value prefix
    b = base(w)
    if (b in SHELL) {                                             # sh -c '...'
      for (j = i + 1; j <= NT; j++) {
        o = T[j]
        if (substr(o, 1, 1) != "-") break
        if (o ~ /^-[A-Za-z]*c[A-Za-z]*$/ && j < NT) { Q[++NQ] = T[j + 1]; return "" }
      }
      return ""
    }
    if (w == "eval") {
      s = ""
      for (j = i + 1; j <= NT; j++) s = s " " T[j]
      Q[++NQ] = s
      return ""
    }
    if (w in WRAP) {
      i++
      while (i <= NT && substr(T[i], 1, 1) == "-") {
        o = T[i]; i++
        if (w == "command" && (o == "-v" || o == "-V")) return ""
        if ((w == "sudo" || w == "doas") && o ~ /^-[ugCDhprtUT]$/) i++
        else if (w == "xargs" && o ~ /^-[InLPsdEa]$/) i++
        else if ((w == "nice" || w == "ionice") && o ~ /^-[nct]$/) i++
        else if (w == "env" && o ~ /^-[uSCP]$/) i++
        else if (w == "timeout" && o ~ /^-[sk]$/) i++
      }
      if (w == "timeout" && i <= NT && T[i] ~ /^[0-9.]+[smhd]?$/) i++
      continue
    }
    if (isdel(b)) return "RM"
    if (b == "find") {
      for (j = i + 1; j <= NT; j++) {
        o = T[j]
        if (o == "-delete") return "FIND_DELETE"
        if (o ~ /^-(exec|execdir|ok|okdir)$/ && j < NT) {
          if (isdel(base(T[j + 1]))) return "RM"
          if (base(T[j + 1]) in SHELL) {
            for (k = j + 2; k < NT; k++) if (T[k] ~ /^-[A-Za-z]*c[A-Za-z]*$/) { Q[++NQ] = T[k + 1]; break }
          }
        }
      }
      return ""
    }
    if (b == "git") {
      sb = ""
      for (j = i + 1; j <= NT; j++) {
        o = T[j]
        if (o == "-C" || o == "-c" || o == "--git-dir" || o == "--work-tree" || o == "--namespace") { j++; continue }
        if (substr(o, 1, 1) == "-") continue
        sb = o
        break
      }
      if (sb != "clean") return ""
      for (k = j + 1; k <= NT; k++) {
        o = T[k]
        if (o == "--dry-run" || o ~ /^-[A-Za-z]*n[A-Za-z]*$/) return ""
      }
      return "GIT_CLEAN"
    }
    return ""
  }
  return ""
}

function scan(s,    n, i, c, c2, st, k, rest, inner) {
  n = length(s); i = 1; st = 0
  NT = 0; W = ""; INWORD = 0; NH = 0
  while (i <= n) {
    c = substr(s, i, 1)
    if (st == 1) {                                   # inside '...'
      k = index(substr(s, i), "'")
      if (k == 0) { W = W substr(s, i); break }
      W = W substr(s, i, k - 1); i += k; st = 0
      continue
    }
    if (st == 2) {                                   # inside "..."
      rest = substr(s, i)
      if (!match(rest, /["\\$`]/)) { W = W rest; break }
      W = W substr(rest, 1, RSTART - 1); i += RSTART - 1
      c = substr(s, i, 1)
      if (c == "\"") { st = 0; i++; continue }
      if (c == "\\") { W = W substr(s, i + 1, 1); i += 2; continue }
      if (c == "`") {
        k = index(substr(s, i + 1), "`")
        inner = k ? substr(s, i + 1, k - 1) : substr(s, i + 1)
        Q[++NQ] = inner; W = W "`" inner "`"
        i = k ? i + k + 1 : n + 1
        continue
      }
      if (c == "$" && substr(s, i + 1, 1) == "(") {
        inner = paren(s, i + 2)
        Q[++NQ] = inner; W = W "$(" inner ")"
        i += 3 + length(inner)
        continue
      }
      W = W c; i++
      continue
    }
    # unquoted
    if (c == "\\") {
      c2 = substr(s, i + 1, 1)
      if (c2 == "\n") { addword(); i += 2; continue }  # line continuation
      W = W c2; INWORD = 1; i += 2
      continue
    }
    if (c == "'") { st = 1; INWORD = 1; i++; continue }
    if (c == "\"") { st = 2; INWORD = 1; i++; continue }
    if (c == " " || c == "\t" || c == "\r") { addword(); i++; continue }
    if (c == "#" && !INWORD) {                         # comment to end of line
      k = index(substr(s, i), "\n")
      if (k == 0) break
      i += k - 1
      continue
    }
    if (c == "<" && substr(s, i + 1, 1) == "<" && substr(s, i + 2, 1) != "<") { i = heredoc_op(s, i); continue }
    if (c == "$" && substr(s, i + 1, 1) == "(") { endseg(); i += 2; continue }
    if (c == "\n") { endseg(); if (NH > 0) i = skip_heredocs(s, i); else i++; continue }
    if (c == ";" || c == "&" || c == "|" || c == "(" || c == ")" || c == "`") { endseg(); i++; continue }
    W = W c; INWORD = 1; i++
  }
  endseg()
}

{ RAW = RAW $0 "\n" }

END {
  split("sudo doas exec command builtin nohup time nice ionice env xargs timeout stdbuf chronic then do else elif if while until ! { }", L, " ")
  for (x in L) WRAP[L[x]] = 1
  split("sh bash zsh dash ksh mksh fish", L2, " ")
  for (x in L2) { SHELL[L2[x]] = 1; WRAP[L2[x]] = 1 }

  tool = jstr(RAW, "tool_name")
  if (tool != "" && tool != "Bash") exit 0
  cmd = jstr(RAW, "command")
  if (cmd == "") exit 0

  VERDICT = ""
  NQ = 1; Q[1] = cmd
  for (qi = 1; qi <= NQ && qi <= 64 && VERDICT == ""; qi++) scan(Q[qi])
  if (VERDICT != "") print VERDICT
}
