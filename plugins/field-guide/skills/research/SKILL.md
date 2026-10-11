---
name: research
description: Research a question, or check whether one claim is true, with every claim graded VERIFIED, REPORTED, or INFERRED, verbatim quotes, honest null results, a separate verification pass, and a closing list of what could not be verified. Use for fact-finding, due diligence, background research, and "is this true?" questions.
argument-hint: "[question, or a claim to check plus its source]"
---

# Research with graded evidence

Question or claim: $ARGUMENTS

The standard here is "measured, not instructed". Telling an agent to be careful reduces errors; only checking catches them. Readers have caught AI agents fudging quotes even under explicit instructions not to.

## Before you start

- If the reader and length aren't stated, pick a sensible default (for example "one page, for a smart reader with no context on this conversation") and say so in one line.
- If the user gave one falsifiable claim plus a primary source, treat it as a claim check: read the primary source first.
- Decide which sources you'll check. Prefer primary sources (the filing, the paper, the docs, the original post, the dataset) over coverage of them.

## While researching

- Grade every factual claim, and give each a URL or file path:
  - **VERIFIED**: you saw the primary source yourself.
  - **REPORTED**: a secondary source says so (name it).
  - **INFERRED**: your own reasoning from the evidence (say from what).
- Quotes are verbatim: copied from the source, with the source and date. Never paraphrase inside quotation marks, and never stitch two sentences into one quote. Mark cuts with `[...]`.
- Absence of a result is not evidence of absence. For each null, say which sources you searched and how complete each one is, and name a positive control: something you know is there that the same search did find. A search that fails its positive control tells you nothing.
- Use absolute dates ("2026-09-22", not "last Tuesday"), and date any number that can change ("as of 2026-10-10").
- Don't overclaim and don't manufacture findings. "Nothing notable here" is a valid result.
- Keep evidence and inference visibly separate, especially about motives, payments, or who coordinated with whom.
- Respect sites' terms and rate limits. Never automate logins, CAPTCHAs, or paywalls; ask the user instead.

## Verify in a separate pass

Drafting and checking are different jobs. Before handing anything over:

- For each key finding, ask the `field-guide:refuter` agent to try to refute it (it defaults to "not real" when uncertain). Drop or downgrade what doesn't survive. If subagents aren't available, do the refutation pass yourself, one finding at a time, re-opening each source.
- Re-open the source for every quote that matters and string-match it. `/field-guide:verify-quotes` automates this for local files and downloaded pages.

## Output

1. **The answer first**, in two or three sentences. For a claim check, a verdict (TRUE, FALSE, PARTLY TRUE, or CAN'T TELL) with the decisive evidence.
2. **Findings**, each with its grade and source. A table works well: claim | grade | source | date.
3. **Searched, found nothing**: the sources, how complete each is, and the positive control.
4. **What I could not verify**, and what a human should check before relying on this. Always include this section, even if it says "nothing material".
