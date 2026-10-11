"""Refresh the plugin's copies of the public guide from abergman.com/ai.

Writes two files, then prints a short diff summary:
  1. plugins/field-guide/skills/guide/reference/how-i-use-coding-agents.md
     (the whole guide, which the /field-guide:guide skill searches)
  2. plugins/field-guide-house-rules/rules/house-rules.md
     (the fenced block in section 21, "paste this into your CLAUDE.md")

Only the public page is used as a source, on purpose: nothing in this repo
should come from anywhere else. Run it after the page changes, review the git
diff, bump versions (see CLAUDE.md), and release.

Run:  python3 scripts/sync_from_site.py      (stdlib only)
"""

import re
import subprocess
import sys
import urllib.request
from pathlib import Path

# ---- config ----
SOURCE_URL = "https://abergman.com/ai.md"
LOCAL_SOURCE = None   # e.g. Path("path/to/ai_guide.md") to sync from a local copy instead of the URL
REPO = Path(__file__).resolve().parent.parent
GUIDE_OUT = REPO / "plugins/field-guide/skills/guide/reference/how-i-use-coding-agents.md"
RULES_OUT = REPO / "plugins/field-guide-house-rules/rules/house-rules.md"
SECTION_HEADING = "## 21."
MAX_RULES_CHARS = 8000   # the SessionStart hook injects at most ~8.5 KB
# ----------------


def fetch() -> str:
    if LOCAL_SOURCE:
        return Path(LOCAL_SOURCE).read_text(encoding="utf-8")
    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "claude-field-guide-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def extract_rules(md: str) -> str:
    start = md.find(SECTION_HEADING)
    if start < 0:
        sys.exit(f"Could not find the section heading {SECTION_HEADING!r}")
    m = re.search(r"```markdown\n(.*?)\n```", md[start:], re.S)
    if not m:
        sys.exit("Could not find the fenced markdown block in section 21")
    return m.group(1).strip() + "\n"


def main():
    md = fetch()
    if "How I use coding agents" not in md[:200]:
        sys.exit("Unexpected source content; refusing to write")
    rules = extract_rules(md)
    if len(rules) > MAX_RULES_CHARS:
        sys.exit(f"Section 21 block is {len(rules)} chars, over the {MAX_RULES_CHARS} budget for the SessionStart hook")
    for bad in ("\u2014", "\u2013"):
        if bad in rules:
            print(f"warning: the rules block contains {bad!r}")
    GUIDE_OUT.parent.mkdir(parents=True, exist_ok=True)
    RULES_OUT.parent.mkdir(parents=True, exist_ok=True)
    GUIDE_OUT.write_text(md if md.endswith("\n") else md + "\n", encoding="utf-8")
    RULES_OUT.write_text(rules, encoding="utf-8")
    print(f"guide: {len(md):,} chars -> {GUIDE_OUT.relative_to(REPO)}")
    print(f"rules: {len(rules):,} chars -> {RULES_OUT.relative_to(REPO)}")
    subprocess.run(["git", "-C", str(REPO), "diff", "--stat", "--", str(GUIDE_OUT), str(RULES_OUT)])


if __name__ == "__main__":
    main()
