---
name: meeting
description: Turn a meeting transcript (or recording) into durable notes, then do the action items that are yours - decisions, owners, dates, verbatim guidance, and drafts (never sends) of anything that goes to other people. Use for "process this meeting", "notes from this call", or "accomplish everything we agreed to".
argument-hint: "[transcript or recording] [attendees, roles, spellings]"
---

# Meeting to notes to done work

Input: $ARGUMENTS

A recorded meeting is close to a finished spec: every decision and assignment, in everyone's own words. No other input packs as much context per minute of the user's time. This skill writes the notes, then does the work.

## 0. Consent and confidentiality

- Recording a meeting requires telling everyone and getting their OK before recording; several US states require every party's consent. If it's unclear that this happened, finish the job but mention it once.
- Transcripts of private meetings are confidential. Keep the transcript and the notes local. Don't upload them to paste sites, public repositories, or unfamiliar third-party services, and don't send them to extra external APIs without asking.

## 1. Get a usable transcript

- Any transcript works: Zoom, Meet, Teams, Otter, a phone app, or a text file.
- If there is only audio, look for a local transcription tool first (for example `whisper`, `mlx_whisper`, or `whisper-cli`). Ask before installing one or sending the audio to a paid service, and state the expected cost.
- Get the attendees, their roles, and the spelling of names and jargon from the user or from context. Speech recognition mangles names, and one wrong surname repeated through a whole transcript is a common failure.

## 2. Write the notes

Save as `<YYYY-MM-DD>-<short-meeting-name>-notes.md` next to the transcript. The reader may never hear the audio, so be thorough:

- Date, attendees, and a one-line purpose.
- **TL;DR of decisions**, first.
- **Numbered topic sections** with approximate timestamps, capturing every decision, every assignment (who, what, by when), changes to standing rules, and any spending approved.
- **Action items** as a checklist: owner, task, due date (absolute), status.
- **Verbatim quotes** of any guidance worth keeping, with timestamps. Quote exactly. Flag any quote that will be used elsewhere for a check against the audio, since transcripts contain recognition errors.
- **Open questions** and anything ambiguous or inaudible.

## 3. Do the work

- For each action item assigned to the user that can be done here (research, a spreadsheet, a draft, a script, a small tool), do it and link the result from the notes.
- Anything addressed to other people (emails, messages, invites) is **drafted, never sent**. Put drafts in files and say where they are.
- Before anything hard to undo (deleting, deploying, spending money, touching shared systems), say what you're about to do and ask.
- List items owned by other people, with their owners.

## 4. Report

End with: what you did (with paths), what's drafted and waiting for the user, what needs someone else, and anything in the transcript you couldn't make sense of. For next time: with a transcript in the folder, `/goal accomplish everything we agreed to in this meeting` runs this end to end.
