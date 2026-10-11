"""Tests for plugins/field-guide/skills/verify-quotes/check_quotes.py.

Uses the bundled guide as the source and a synthetic draft with known-good,
near-miss, and fabricated quotes. Run: python3 tests/test_quotes.py
"""

import subprocess
import sys
import tempfile
from pathlib import Path

# ---- config ----
REPO = Path(__file__).resolve().parent.parent
CHECKER = REPO / "plugins/field-guide/skills/verify-quotes/check_quotes.py"
SOURCE = REPO / "plugins/field-guide/skills/guide/reference/how-i-use-coding-agents.md"
# ----------------

DRAFT = """# A memo

The guide says “quote fidelity and factual accuracy must be measured, never just instructed.”

It also says "Absence of a result is not evidence of absence." which is exact with straight quotes.

Case and punctuation drift: "ABSENCE OF A RESULT IS NOT EVIDENCE OF ABSENCE" should be close.

With a gap: "Every weekly update Claude drafts for Aaron opens with ... things it could not check."

With an editorial insertion: "A pasted 6:47 AM Slack request became [a] live searchable database the next day."

Paraphrased: "Quote accuracy has to be measured, it can never simply be instructed to the model."

Fabricated: "The guide recommends running every agent with root privileges on production."

Stitched: "Interrupt early and cheaply. Delegate outcomes, not steps."

> Long threads are the silent budget killer.

A short "scare quote" is skipped.

```
"This quote is inside a code block and must be ignored entirely."
```
"""

EXPECT = {
    "quote fidelity and factual accuracy": "EXACT",
    "Absence of a result is not evidence of absence.": "EXACT",
    "ABSENCE OF A RESULT": "CLOSE",
    "Every weekly update Claude drafts": "EXACT",
    "A pasted 6:47 AM Slack request": "EXACT",
    "Quote accuracy has to be measured": "NOT FOUND",
    "The guide recommends running every agent": "NOT FOUND",
    "Interrupt early and cheaply. Delegate outcomes": "NOT FOUND",
    "Long threads are the silent budget killer.": "EXACT",
}


def main():
    with tempfile.TemporaryDirectory() as td:
        draft = Path(td) / "draft.md"
        draft.write_text(DRAFT, encoding="utf-8")
        p = subprocess.run([sys.executable, str(CHECKER), str(draft), str(SOURCE)], capture_output=True, text=True)
    out = p.stdout
    fails = []
    for needle, status in EXPECT.items():
        rows = [l for l in out.splitlines() if needle[:30] in l]
        if not rows:
            fails.append(f"missing row for {needle!r}")
        elif f"| {status} |" not in rows[0]:
            fails.append(f"{needle!r}: expected {status}, got {rows[0]}")
    if "code block" in out:
        fails.append("quote inside a code block was checked")
    if "scare quote" in out:
        fails.append("short quote was not skipped")
    if p.returncode != 1:
        fails.append(f"exit code {p.returncode}, expected 1 (some quotes not found)")
    if "how-i-use-coding-agents.md:" not in out:
        fails.append("no line numbers reported")
    print(out)
    print("FAILS:" if fails else "all quote-checker tests passed", *fails, sep="\n  ")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
