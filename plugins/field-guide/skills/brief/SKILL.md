---
name: brief
description: Turn a rough request into a strong delegation prompt - a /goal kickoff with end state, acceptance test, guardrails, budget, and a judgment principle; a self-contained runbook for a scheduled or unattended run; or a context-firewalled brief for another agent. Use when the user wants help writing a prompt for a big job.
argument-hint: "[rough description of the job]"
---

# Write a delegation brief

Rough request: $ARGUMENTS

Big asks work when the prompt carries an end state and an acceptance test, not a list of steps. If something essential is missing (the end state, what must not be touched, a budget), ask at most three short questions in one message. Otherwise make sensible assumptions and list them.

## Pick the shape

### A. Interactive kickoff (`/goal`)

- **What should exist at the end**, described as the user's experience, not the implementation.
- **Done means**: an acceptance test the agent can observe. "Live at a URL and tested with a real sign-in." "Someone who isn't me can open the spreadsheet and understand it." "The script runs clean on the full input."
- **Guardrails as sentences**: "non-destructive", "don't touch X", "ask before spending more than $N", "only I can see it", "write a script I can run instead of deleting anything".
- **The one quality that matters most**: reliability, speed to a working v1, polish.
- **Budget** in money or time, and the model or agent count if it matters ("up to 10 subagents on the strongest model"). If you expect a job to cost about $100, say so; a run that spends 1% of that probably didn't do the job.
- **A judgment principle** for everything unspecified, such as "use your judgement to get the 80/20 of usefulness versus invasiveness", plus "make it actually good, not a toy demo".
- **Where not to spend effort**: "don't try hard on DNS; I can do that in the UI in two minutes".
- **Permission to reuse**: "you can fork an existing repo; the goal is the thing, not writing every line".

### B. Unattended runbook (scheduled task, background run, cron)

Nobody is there to answer questions, so write a self-contained file:

- First line: "This is an automated run. The user is not available and cannot answer questions."
- **Background**: what this is and why, in a paragraph.
- **Hard "never" rules**: never type passwords, 2FA codes, or passkeys (leave the page open and say which); never delete data; never send messages or spend beyond a stated cap.
- **What to do in each expected case**, including failure and "nothing to do".
- **Checkpointing**: write progress to disk so a crash or usage limit loses nothing, and make re-runs skip finished work.
- **The report**: exact format, and where it goes.

### C. Outsourcing brief (another agent or tool)

When work should go to another agent without exposing the deeper project context: state only the task, the inputs, the constraints, and a strict output format that is easy to verify and pick up. Leave out client names, goals, and anything else the other agent doesn't need.

## Output

The prompt in one fenced code block, ready to paste (or saved to a file such as `prompts/<name>.md` if asked), then a short list of the assumptions you made. Don't run it.
