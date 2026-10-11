---
name: scrape-to-sheet
description: Scrape web pages into a structured data file plus a CSV that imports cleanly into Google Sheets or Excel, with a source URL on every row, a row count, and a list of what could not be extracted. Use for "scrape this page", "turn this site into a spreadsheet", and directory or listing pages.
argument-hint: "[URL(s)] [fields wanted]"
---

# Scrape to a spreadsheet

Target and fields: $ARGUMENTS

## 1. Check before scraping

- Read the site's terms and `robots.txt` for the pages involved. If the site forbids automated access, say so and stop, and offer alternatives: an official API, an export button, or a human-in-the-loop version.
- Never automate logins, CAPTCHAs, or paywalls. If the data needs a login, build the human-in-the-loop version: the user signs in and saves or downloads the pages, and you process what lands in a folder.
- Look at one page first. Choose between static HTML (fetch and parse), a JSON API the page itself calls (often cleaner), and a JavaScript-rendered page (needs a headless browser). If more than one approach is plausible and they differ in cost or reliability, give the options with tradeoffs before building, unless the user said "your call".

## 2. Scrape politely

- Sequential requests with a delay of one to two seconds, longer for government or small sites. A sensible User-Agent. Back off on 429s.
- Cache raw pages to disk (`raw/<slug>.html`) so re-runs don't re-fetch and parsing can be fixed without scraping again.
- For more than a few dozen pages, make it resumable and show a progress bar.
- If a public page that permits access refuses plain HTTP clients, a client with browser impersonation (such as `curl_cffi`) often works. Don't use it to get around a site's explicit refusal.

## 3. Output

- A structured file with every field (`<name>.json` or `.jsonl`), including `source_url` on every row.
- A CSV for humans: UTF-8, one header row in plain words a stranger understands, no merged cells, a Source column, dates as YYYY-MM-DD. Images as URLs (Google Sheets shows them with `=IMAGE(url)`).
- Spot-check three random rows against the live page and say that you did.
- Tell the user: rows extracted, pages fetched, what couldn't be extracted and why, and the file paths.
