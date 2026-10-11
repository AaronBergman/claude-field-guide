---
name: verify-quotes
description: Check every quotation in a draft against its sources, verbatim, and report each quote as exact, close (case, punctuation, or whitespace only), or not found with the nearest real wording. Use before sending any document that quotes people, documents, web pages, or transcripts.
argument-hint: "[draft file] [source files or URLs...]"
---

# Verify quotes against their sources

Input: $ARGUMENTS

"Quote verbatim" in a prompt reduces errors but doesn't eliminate them. A mechanical string match does. In one real batch of finished documents, a second check found a quote silently paraphrased, "held off by request" degraded to "not pursued", and a pending step written in the past tense.

## Steps

1. **Collect the sources as local text.** Sources can be files (txt, md, html, csv, srt, vtt, transcripts) or URLs. Download URLs into a scratch folder (for example `curl -sL <url> -o sources/<name>.html`) and convert PDFs to text first (`pdftotext` if installed). Note any source you couldn't retrieve.
2. **Run the bundled checker** (Python 3 standard library only, no network):

   ```
   python3 "${CLAUDE_SKILL_DIR}/check_quotes.py" <draft> <source> [<source> ...]
   ```

   It extracts quotes from the draft (text in curly or straight double quotes of four or more words, and Markdown blockquotes), skips code blocks, and treats `...`, `…`, `[...]`, and bracketed editorial insertions like `[the company]` as gaps. Add `--min-words 1` to include short quotes. It prints a Markdown table and exits with status 1 if any quote is not found.

   If Python isn't available, do it by hand: for each quote, `grep -F` the sources for a distinctive five-to-eight-word fragment, then compare the full text character by character.
3. **Classify every quote that isn't EXACT** by opening the source at the reported line:
   - **CLOSE** (case, punctuation, whitespace, or quote style only): usually fine; fix it to match the source if the user wants strict verbatim.
   - **NOT FOUND**: paraphrased, stitched together, or from a source you don't have. Show the nearest real wording and propose a fix: use the source's actual words, or drop the quotation marks and present it as a paraphrase.
4. **Transcripts are not ground truth.** A quote that matches a machine transcript exactly is only as good as the transcript. Flag quotes from audio for a human to check against the recording before publication.

## Output

A table: quote (first dozen words) | status | source and line | proposed fix. Then totals: N quotes, N exact, N close, N not found, plus any sources you couldn't check. Don't edit the draft unless asked; when asked, keep the original and write the corrected version as a new file.
