---
name: timeline
description: Read every document in a folder and build a timeline - one row per dated event with an absolute date, the source file, and a verbatim supporting quote - plus lists of undated items, conflicts, and unreadable files. Use for "build a timeline", chronologies, case files, and "what happened when".
argument-hint: "[folder] [optional focus]"
---

# Folder to timeline

Folder and focus: $ARGUMENTS (default: the current folder)

## Steps

1. **Inventory** the folder: every file with type and size. Convert what you can to text (PDFs with `pdftotext` if installed; Word and HTML files to text). List files you couldn't read and why. For more than a few hundred files, say how you'll batch them and checkpoint progress to disk.
2. **Read every readable file.** For each dated event, record the date (absolute YYYY-MM-DD, keeping the precision the source supports, such as `2024-03` or `circa 2019`), the event in one plain sentence, the source file with page or line, and a verbatim quote that supports it.
3. **Relative dates** ("last Tuesday", "the following month") are resolved only when the document's own date makes them unambiguous, and you say you did. Otherwise they go in the undated list.
4. **Conflicts**: when sources disagree about a date or a fact, keep both rows and flag the conflict. Don't pick a winner silently.

## Output

- `timeline.md`: a table sorted by date: date | event | source | quote. Group by year if it's long.
- `timeline.csv` with the same columns, for spreadsheets.
- At the end of `timeline.md`: undated or ambiguous items, conflicts, unreadable files, and what a human should double-check.
- Before finishing, string-match a sample of the quotes against the files (`/field-guide:verify-quotes` does this) and say how many you checked.
