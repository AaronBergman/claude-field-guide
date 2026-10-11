#!/usr/bin/env python3
"""Check that every quotation in a draft appears verbatim in its sources.

Usage (normally run by Claude from the verify-quotes skill):
    python3 check_quotes.py DRAFT SOURCE [SOURCE ...] [--min-words N]

What counts as a quote in the draft:
  - text inside curly double quotes, or inside straight double quotes on one line
  - Markdown blockquotes (consecutive lines starting with ">")
Fenced code blocks and `inline code` are skipped. Quotes shorter than
MIN_WORDS words are skipped (scare quotes, titles).

Inside a quote, "...", the ellipsis character, "[...]" and bracketed editorial
insertions such as "[the company]" are treated as gaps: each piece must appear
in the same source, in order.

Statuses:
  EXACT      every piece found after normalizing whitespace, quote style,
             dashes, and Unicode compatibility forms
  CLOSE      found only after also ignoring case and punctuation
  NOT FOUND  not found; the closest passage and its similarity are shown

Standard library only, no network. Exit status 1 if any quote is NOT FOUND.
"""

import difflib
import html
import re
import sys
import unicodedata
from pathlib import Path

# ---- config (defaults; --min-words overrides MIN_WORDS) ----
MIN_WORDS = 4
SNIPPET_CHARS = 90
# -------------------------------------------------------------

GAP_RE = re.compile(r"\s*(?:\.\.\.|\u2026|\[\s*(?:\.\.\.|\u2026)\s*\]|\[[^\]]{1,60}\])\s*")
TRANSLATE = str.maketrans({
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u2033": '"',
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u2032": "'",
    "\u2014": "-", "\u2013": "-", "\u2012": "-", "\u2010": "-", "\u2011": "-", "\u2212": "-",
    "\u00a0": " ", "\u2009": " ", "\u202f": " ",
})


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).translate(TRANSLATE)
    return re.sub(r"\s+", " ", s).strip()


def fold(s: str) -> str:
    s = norm(s).casefold()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def strip_code(md: str) -> str:
    md = re.sub(r"^(```|~~~).*?^\1[^\n]*$", lambda m: "\n" * m.group(0).count("\n"), md, flags=re.S | re.M)
    return re.sub(r"`[^`\n]*`", " ", md)


def extract_quotes(md: str, min_words: int):
    """Return [(line_number, quote_text)] in document order."""
    text = strip_code(md)
    found = []
    lines = text.split("\n")
    # Markdown blockquotes: consecutive ">" lines form one quote.
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith(">"):
            start, buf = i, []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                buf.append(re.sub(r"^\s*(>\s?)+", "", lines[i]))
                i += 1
            q = " ".join(b for b in buf if b.strip())
            if q.strip():
                found.append((start + 1, q))
        else:
            i += 1
    # Curly quotes (may span lines within a paragraph) and straight quotes (one line).
    for m in re.finditer(r"\u201c([^\u201c\u201d]{1,2000}?)\u201d", text):
        if "\n\n" not in m.group(1):
            found.append((text.count("\n", 0, m.start()) + 1, m.group(1)))
    for ln, line in enumerate(lines, 1):
        if line.lstrip().startswith(">"):
            continue
        for m in re.finditer(r'"([^"\n]{2,1000})"', line):
            found.append((ln, m.group(1)))
    out, seen = [], set()
    for ln, q in sorted(found):
        q = q.strip()
        words = len(GAP_RE.sub(" ", q).split())
        if words < min_words:
            continue
        key = norm(q)
        if key in seen:
            continue
        seen.add(key)
        out.append((ln, q))
    return out


def read_source(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() in (".html", ".htm", ".xhtml") or raw.lstrip()[:15].lower().startswith(("<!doctype", "<html")):
        raw = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", raw)
        raw = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h[1-6]|tr|blockquote)>", "\n", raw)
        raw = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    if path.suffix.lower() in (".srt", ".vtt"):
        raw = re.sub(r"(?m)^\d+\s*$|^\d\d:\d\d[:.\d]*\s*-->.*$|^WEBVTT.*$", " ", raw)
    return raw


def pieces(quote: str):
    return [p for p in (s.strip() for s in GAP_RE.split(quote)) if p]


def find_in_order(hay: str, parts):
    """Position of the first part if all parts occur in order, else -1."""
    pos, first = 0, -1
    for p in parts:
        k = hay.find(p, pos)
        if k < 0:
            return -1
        if first < 0:
            first = k
        pos = k + len(p)
    return first


def indexed(raw: str, normalizer):
    """Normalize line by line; return (text, line_starts) so offsets map back to lines."""
    parts, starts, pos = [], [], 0
    for i, line in enumerate(raw.split("\n"), 1):
        n = normalizer(line)
        if not n:
            continue
        starts.append((pos, i))
        parts.append(n)
        pos += len(n) + 1
    return " ".join(parts), starts


def line_at(starts, offset: int) -> int:
    lo, hi, best = 0, len(starts) - 1, 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if starts[mid][0] <= offset:
            best = starts[mid][1]
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def closest(quote_f: str, src_f: str):
    """Most similar window of the folded source to the folded quote."""
    words = quote_f.split()
    if not words or not src_f:
        return 0.0, "", 0
    anchors = sorted(set(words), key=len, reverse=True)[:4]
    starts = set()
    for a in anchors:
        for m in re.finditer(r"\b" + re.escape(a) + r"\b", src_f):
            starts.add(max(0, m.start() - len(quote_f)))
            if len(starts) > 400:
                break
    if not starts:
        starts = set(range(0, max(1, len(src_f) - len(quote_f)), max(1, len(quote_f) // 2)))
    best, best_s, best_pos = 0.0, "", 0
    for s in sorted(starts)[:2000]:
        window = src_f[s:s + 2 * len(quote_f) + 20]
        sm = difflib.SequenceMatcher(None, quote_f, window, autojunk=False)
        blocks = sm.get_matching_blocks()
        if not blocks:
            continue
        lo = max(0, blocks[0].b - 5)
        hi = min(len(window), blocks[-2].b + blocks[-2].size + 5) if len(blocks) > 1 else len(window)
        cand = window[lo:hi]
        r = difflib.SequenceMatcher(None, quote_f, cand, autojunk=False).ratio()
        if r > best:
            best, best_s, best_pos = r, cand, s + lo
    return best, best_s, best_pos


def short(s: str, n: int = SNIPPET_CHARS) -> str:
    s = s.replace("|", "\\|")
    return s if len(s) <= n else s[: n - 3] + "..."


def main(argv):
    min_words = MIN_WORDS
    if "--min-words" in argv:
        k = argv.index("--min-words")
        min_words = int(argv[k + 1])
        del argv[k:k + 2]
    if len(argv) < 2:
        print(__doc__)
        return 2
    draft, sources = Path(argv[0]), [Path(a) for a in argv[1:]]
    quotes = extract_quotes(draft.read_text(encoding="utf-8", errors="replace"), min_words)
    srcs = []
    for p in sources:
        try:
            raw = read_source(p)
        except OSError as e:
            print(f"warning: could not read {p}: {e}", file=sys.stderr)
            continue
        srcs.append((p, indexed(raw, norm), indexed(raw, fold)))
    if not srcs:
        print("No readable sources.", file=sys.stderr)
        return 2

    rows, counts = [], {"EXACT": 0, "CLOSE": 0, "NOT FOUND": 0}
    for ln, q in quotes:
        parts_n = [norm(x) for x in pieces(q)]
        parts_f = [fold(x) for x in pieces(q)]
        status, where, note = "NOT FOUND", "", ""
        for p, (n_text, n_starts), _ in srcs:
            k = find_in_order(n_text, parts_n) if parts_n else -1
            if k >= 0:
                status, where = "EXACT", f"{p.name}:{line_at(n_starts, k)}"
                break
        if status != "EXACT":
            for p, _, (f_text, f_starts) in srcs:
                k = find_in_order(f_text, parts_f) if parts_f else -1
                if k >= 0:
                    status, where = "CLOSE", f"{p.name}:{line_at(f_starts, k)}"
                    note = "differs only in case, punctuation, or spacing"
                    break
        if status == "NOT FOUND":
            best = (0.0, "", 0, None, None)
            for p, _, (f_text, f_starts) in srcs:
                r, snip, pos = closest(fold(q), f_text)
                if r > best[0]:
                    best = (r, snip, pos, p, f_starts)
            if best[3] is not None and best[0] > 0.3:
                where = f"{best[3].name}:{line_at(best[4], best[2])}"
                note = f"closest ({best[0]:.0%} similar): \"{short(best[1])}\""
            else:
                note = "nothing similar in the sources"
        counts[status] += 1
        rows.append((ln, q, status, where, note))

    print(f"# Quote check: {draft.name}\n")
    print(f"Sources: {', '.join(p.name for p, *_ in srcs)}\n")
    print("| Draft line | Quote | Status | Found in | Note |")
    print("|---|---|---|---|---|")
    for ln, q, status, where, note in rows:
        print(f"| {ln} | \"{short(norm(q), 70)}\" | {status} | {where} | {note} |")
    total = len(rows)
    print(f"\n{total} quotes: {counts['EXACT']} exact, {counts['CLOSE']} close, {counts['NOT FOUND']} not found.")
    if total == 0:
        print(f"(No quotes of {min_words}+ words found. Try --min-words 1.)")
    return 1 if counts["NOT FOUND"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
