---
name: memo
description: Write a document for humans who weren't in the conversation - answer first, plain memo register, a named reader and length, citations, absolute dates - then check it with a cold reader and a quote check. Use for memos, briefings, reports, write-ups, and condensed versions of long documents.
argument-hint: "[topic or source doc] [reader] [length]"
---

# Write for humans

Task: $ARGUMENTS

## Settle the reader and length first

If they aren't given, pick defaults and state them in one line, for example: "Readers are high context on the field, zero context on this conversation. About two pages when pasted into Google Docs." Other good targets: "a smart high schooler could follow it on first read"; "a 2-5 page condensed version a manager will actually read".

## Write

- Lead with the answer or recommendation, then the support.
- Register: an excellent human memo. Plain and straightforward, as simple as possible but not simpler. No hype, no fancy phrasing, no bolding random phrases, no "In conclusion".
- Curate. Not everything known belongs in the memo; choose what this reader needs.
- Every factual claim has a source (URL or file path). Keep evidence and inference separate. Quotes are verbatim.
- Absolute dates; numbers carry their date.
- No em dashes; use commas, colons, parentheses, or periods. Don't hard-wrap lines in Markdown.
- Tone: descriptive rather than alarmed. A critical vibe crowds out information.
- If the material has gaps, end with a short "What this memo could not verify" section.

## Check before handing over

1. Ask the `field-guide:cold-reader` agent to read the draft as the named reader and report what's unclear, unsupported, or overclaimed. Fix what's real. (Without subagents, re-read it yourself as that reader, in a separate pass.)
2. If the memo quotes anything, verify the quotes against their sources with `/field-guide:verify-quotes`.
3. Compare the length to the target and cut. First drafts usually run long.

Save it as a Markdown file with a clear name and give the user the path. If the user wants to write the piece themselves, gather instead: put the relevant facts, quotes, and sources in a file and let them write.
