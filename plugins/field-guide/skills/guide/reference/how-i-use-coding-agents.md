# How I use coding agents

**Written by Claude, not by Aaron.** Aaron asked Claude (Opus 5.5, running in Claude Code) to write this guide from his own prompt history, session transcripts, settings, hooks, and an earlier internal guide Claude had written for his coworkers. The words and the selection are Claude's. "Aaron" and "he" below mean Aaron Bergman; the quoted prompts are things he actually typed, typos included. Details of his client work (clients, colleagues, internal tools, the people and topics being researched) are generalized or redacted as `[..]`. Nothing here is a secret: no keys, tokens, passwords, or account details. Numbers are measured from his own logs unless marked "about" or "rough". Last updated 2026-10-10.

**How to use this.** Read it, or hand it to an agent. The "Copy as Markdown" button at the top of the web page (abergman.com/ai) puts the whole document on your clipboard, ready to paste into Claude Code, claude.ai, or any other assistant as context ("read this, then help me set up my own version of what's useful in it"). Section 21 is a compact block meant to be pasted straight into a `CLAUDE.md`. Nothing here needs to be downloaded or installed. If you would rather install than paste, most of it also ships as Claude Code plugins (the prompt templates as skills, the verifier agents, the `rm` guard and big-file hooks as hooks, and section 21's rules as an optional session preamble): [github.com/AaronBergman/claude-field-guide](https://github.com/AaronBergman/claude-field-guide).

**Who it's for.** Anyone who uses Claude (or ChatGPT, Codex, Cursor, Gemini) mostly as a chat window and wants to hand it whole jobs instead. The details are Claude-specific because that is what Aaron uses, but most of the ideas carry over to any coding agent. It is one heavy user's practice: opinionated, in places idiosyncratic. Aaron works as a technical consultant for a small research team, which means a lot of internal tools, data pipelines, scraping, and research write-ups, plus personal projects on the side. Take what helps and ignore the rest.

---

## Contents

1. TL;DR: fifteen things worth stealing
2. The mental model: a ladder with four rungs
3. Plans, limits, and what it costs
4. Where it happens: terminal, desktop app, phone, chat, other agents
5. Models and effort
6. The setup: permissions, CLAUDE.md, hooks, skills, memory, secrets
7. Connectors and MCP
8. How to prompt
9. The prompt library (copyable)
10. When and how to step in
11. How ambitious an ask can be
12. Workflows and subagents
13. Long runs, compaction, and continuity
14. Browser and computer control
15. Verification: measured, not instructed
16. What agents can't do (yet), and the workarounds
17. Meetings and transcription: the most underrated input
18. Everyday non-coding uses
19. What this approach has built
20. The on-ramp (with starter CLAUDE.md files)
21. The short version: paste this into your CLAUDE.md
22. Ideas for a team, from safe to reckless
23. Glossary and sources

---

## 1. TL;DR: fifteen things worth stealing

1. **Delegate outcomes, not steps.** The shift that matters is from chatting to handing over whole jobs. Over the summer of 2026, Aaron's typed prompts per month fell by about two-thirds while the amount of work Claude did went up about eight-fold. Short prompts are fine for steering (his median prompt is 177 characters); the big ones describe an end state and what "done" means.
2. **Say what "done" looks like and what must not be touched.** "Live and tested." "Someone who's not me should be able to understand the sheet." "Non-destructive." "Don't make it accessible to anyone but me." The best prompts carry an acceptance test and a guardrail.
3. **Delegate judgment explicitly, with a principle.** "Use your judgement to get basically an 80/20 of usefulness vs invasiveness." "Design decisions I defer to you." The agent makes better calls when it is told what to optimize.
4. **Paste the real ask, and record your meetings.** Slack messages, alert emails, a colleague's bug report, a meeting transcript: paste them verbatim (with the author's or participants' permission when it isn't only yours to share). A pasted 6:47 AM Slack request became a live searchable database the next day. A recorded half-hour meeting plus "/goal accomplish everything we agreed to in this meeting" mostly just works (section 17).
5. **Name the reader.** "A smart high schooler could follow it on first read." "High context on the whole field, zero context on the last million tokens of this conversation." This one sentence fixes most writing output.
6. **Ask for what could not be verified.** Every weekly update Claude drafts for Aaron opens with a list of things it could not check. Research claims get graded VERIFIED, REPORTED, or INFERRED. Readers of his work have caught AI agents fudging quotes even under explicit instructions not to, so verification is the job, not a nicety (section 15).
7. **Interrupt early and cheaply.** Hit Esc and add one line of new context rather than waiting for a bad result ("wait" opens about one in eleven of Aaron's prompts). Give corrections a reason ("bc that folder is actively in use") so the agent can generalize.
8. **Turn repeated corrections into standing rules.** He typed "no command-line arguments" by hand 43 times before putting it in his global `CLAUDE.md`. Now it is never typed. Same for `trash` instead of `rm`, no em dashes, `uv` for Python, progress bars.
9. **Turn repeated chores into automation.** "Ugh, for the nth time" became a runbook, then a cron job, then a daily health-check email, then a one-line "/goal fix everything there is to fix" with that email pasted in.
10. **Put big jobs in multi-agent workflows.** Claude Code can orchestrate dozens to hundreds of parallel subagents from a short script. Aaron's largest run used 752 agents over 8 hours. The patterns that matter are fan-out plus adversarial verification (a second agent tries to refute each finding) and "everything checkpointed to disk so a crash loses nothing".
11. **Keep context in files, not in the chat.** Project `CLAUDE.md` files, per-folder deep-dive docs, handoff notes, and saved transcripts mean any new session (or coworker) starts oriented. Compaction becomes cheap because nothing important lives only in the conversation.
12. **Be stingy with connectors.** Every connector's tool list rides along in every message. One claude.ai chat overflowed at 74,000 tokens before the first message because of loaded skills and connectors. Turn on what the task needs.
13. **Subscriptions for interactive work, API keys for deployed work.** A Max plan subsidizes interactive use roughly 10x versus API list prices. Anything scheduled, deployed, or run over thousands of items goes on a dedicated, cappable API key.
14. **Push back when the agent says it can't.** In a real chat, Claude first concluded a connector wasn't available; one screenshot later it corrected itself and ran a full test. Agents are wrong about their own abilities more often than people expect.
15. **Let it observe the outcome.** Give the agent a way to check its own work: run the script, read the error, hit the URL, count the rows. Almost every success in this guide depends on the agent seeing the result; almost every failure happened somewhere it couldn't (a phone, a CAPTCHA, a home router).

---

## 2. The mental model: a ladder with four rungs

| Rung | What it is | What it's good for |
|---|---|---|
| 1. Chat | claude.ai (or any chat app) with uploads, web search, Projects, Research mode | Questions, explainers, reading documents, drafting |
| 2. Chat + connectors | Chat with MCP connectors (Drive, Slack, Gmail, your own databases) | Questions that need live data from real systems |
| 3. A coding agent | Claude Code (or Codex, Cursor's agent): works on files and runs commands on your machine | Anything involving many files, data, scripts, scraping, building tools, long jobs |
| 4. Autonomous and multi-agent | `/goal`, Workflows, scheduled tasks, background runs, steering from the phone | Jobs that take hours, need many parallel workers, or recur |

Two facts make the top rungs different in kind, not just degree. First, an agent can **observe outcomes** (run the script, read the error, check the HTTP status, count the rows), so it can iterate without you. Second, it can **write things down** (`CLAUDE.md`, docs, handoff notes), so work survives the end of a conversation. Almost every success in this guide depends on one or both. Almost every failure happens where the agent can't observe or where context lived only in a chat.

Most people are on rung 1. The claim of this guide is that rung 3 is not "for programmers": it is for anyone with a folder of files and a chore, and you should start there on a real task, not a tutorial.

---

## 3. Plans, limits, and what it costs

### Plans and limits

- Claude's paid plans (Pro, Max, Team, Enterprise) all include Claude Code. Each Max account has a **rolling 5-hour window** and a **weekly window**; as of this writing there is also a separate weekly window for the top-tier Fable model. Chat-heavy users tend to hit the 5-hour window first; Claude Code users hit the weekly one.
- About 96-100% of Aaron's subscription usage is Claude Code, not chat.
- Check where you stand with `/usage` in Claude Code, or Settings > Usage on claude.ai.

### What the plan is worth

Measured by re-pricing every one of Aaron's Claude Code transcripts at API list prices:

| | Amount |
|---|---|
| API-equivalent value of his interactive Claude Code use, Jan to Sep 2026 | about $25,800 |
| Same, September 2026 alone | about $9,700 |
| What September's subscriptions actually cost | roughly a tenth of that |

Almost all of the API-equivalent cost is re-reading context: across all transcripts, 31 billion cache-read tokens against 77 million output tokens, with 95% of input tokens served from the prompt cache. Long agentic sessions are expensive at API rates and cheap on a plan. As Aaron put it to a colleague, a given job is "either $100 or basically $1,000, depending on how you pay." For scale, one session that ended with a working cloud tool was about 15 million tokens, about $29 at list price.

### Who pays for what

| Surface | Used for | Billed as |
|---|---|---|
| Claude Code (terminal, desktop app) | Nearly all interactive building, research, data work, doc upkeep; long `/goal` runs; Workflows | Subscription |
| claude.ai chat, Cowork | Quick questions, reading documents, Research mode, artifacts | Same subscription |
| Anthropic API (one key per purpose) | Deployed tools, an in-product assistant, batch extraction pipelines | Pay per token |
| OpenRouter | Zero-data-retention routing for one transcription step | Pay per token, small |
| Codex (OpenAI) | A second agent for overflow and for self-contained subcomponents | ChatGPT plan |
| Local models (MLX, llama.cpp) | Offline or private experiments | Free (your hardware) |

Two conventions worth copying for any deployed code:

- **One API key per purpose**, so each can be capped and its spend read separately. An in-product assistant that outside users can talk to gets its own key with its own limit.
- **Pass the key explicitly from a named environment variable** (`api_key=os.environ["MY_PROJECT_ANTHROPIC_KEY"]`), never the SDK's default variable, which can silently bill whatever key happens to be in the environment.

### Advice

- **Long threads are the silent budget killer.** Every turn re-reads the whole thread. Start a fresh chat or session for a new task. Put reusable files in a Project (or a folder) instead of re-uploading them.
- **Keep one coherent corpus per Project.** "Don't keep one giant file containing five unrelated projects; it re-trawls everything on every query."
- **An `ANTHROPIC_API_KEY` in your shell environment makes Claude Code bill the API instead of your subscription.** If you have one exported for scripts, strip it for interactive sessions.

---

## 4. Where it happens: terminal, desktop app, phone, chat, other agents

| Surface | What Aaron uses it for |
|---|---|
| **Claude Code in the terminal** | The default for everything substantial (about 80% of his interactive prompts) |
| Desktop app, Code tab | The same agent with a GUI; scheduled tasks run here |
| Desktop app, Cowork | A sandboxed local agent for lighter tasks |
| Headless (`claude -p`, the Agent SDK) | Memory summarizers, evals, scripted drivers, cron-style jobs |
| Remote Control and the phone | Watching and steering long runs; starting a session on the home Mac from the phone |
| claude.ai chat | A Google replacement: quick questions, estimates, reading an upload, Research mode (most of his chats are two messages long) |
| Codex (OpenAI) | Overflow capacity, and outsourcing self-contained pieces "without exposing context" |

Things worth noting:

- **The terminal runs inside tmux**, so sessions survive a closed window, and a background service keeps a Remote Control server alive so a new session can be started on the home machine from the phone.
- **Parallel sessions are normal.** Two or three sessions on different tasks is common; his peak was six. You can type the next instruction while the agent is still working; it queues.
- **Push notifications** arrive on the phone when a long job finishes or needs input ("Done: site live with 1,972 episodes (was 1,704)... Track total $517").
- **Chat stays the quick-question surface.** The most-used chat tools are Artifacts and web search, then the code sandbox and Research mode. A tiny browser extension turns the address bar into a Claude prompt box (a `claude.ai/new?q=` search keyword plus auto-send).
- **Name claude.ai Projects after a goal** ("Pay quarterly taxes"; "figure out how to vote" on a shareholder ballot, with the proxy PDF attached) or a single-purpose utility ("Rewrite": reformat pasted text as Markdown with exactly the same words).

---

## 5. Models and effort

- **Default to the newest top model, within days of release.** Aaron's model mix over the past year tracks the release history exactly. As of 2026-10-10 that means **Opus 5.5**.
- **As of 2026-09-30, Opus 5.5 beat Fable 5.1 on essentially everything he does, and it is cheaper** (list price $4/$20 per million input/output tokens versus $10/$50 for Fable), so there was roughly no reason to pick Fable. Re-check whenever a new model ships.
- **A pattern worth keeping in spirit: a strong reviewer signs off on worker agents.** Before Opus 5.5, it was "while Opus can do the legwork, you (Fable) must look through each subagent's work and sign off on stuff before it goes live." The idea holds even when the reviewer and the workers are the same model.
- **The smallest models almost never.** A standing rule is "never use Haiku in workflows". His global rules pin workflow agents to Opus explicitly, because some agent types silently default to the smallest model.
- **Effort high, thinking on.** Raise effort with `/effort` for the hardest jobs.
- **Model and budget go in the prompt:** "Opus only, no weaker models", "we don't wanna penny pinch on this", "can be sonnet subagents, don't need opus for this", "keep Opus-medium for all agents".
- **In deployed code the choice is per job:** the top model for extraction and synthesis, the Batches API when half price is worth a longer retention window, zero-data-retention routing for sensitive text, local MLX models for private offline work.
- **Never "correct" a model name.** If a model name in your instructions looks wrong to the agent, it probably post-dates its training data. This is a one-line global rule (section 21).

---

## 6. The setup: permissions, CLAUDE.md, hooks, skills, memory, secrets

What follows is Aaron's setup as a worked example. You don't need all of it; the parts worth copying are marked.

### Permissions

- **Default mode is auto mode.** Claude runs tools without asking unless a safety classifier judges an action risky. This is the single biggest difference from a default install, where every non-read action prompts.
- **The classifier is briefed about the machine** in `settings.json` (`autoMode.environment`): which clouds are in use, that `.env` files are plaintext secret stores to be read only when needed and never echoed, that anything named `prod` is sensitive, that `trash` is preferred over `rm`.
- **Custom soft-denies** for the destructive commands of the tools in use (`railway down`, `rclone delete`, `rclone purge`).
- **An allow list of about 70 read-only commands** (`ls`, `grep`, `rg`, `cat`, `git status/log/diff`, `du`, `df`, `dig`...) so routine inspection never prompts, plus read access to `/tmp/**` (added after workflow agents hung for an hour on a scratch-file permission prompt).
- Aaron's own habit (idiosyncratic) is to skip permission prompts almost entirely and steer by interrupting rather than by approving each step. **What to copy:** auto mode, a read-only allow list, a briefed classifier, and hard rails in hooks rather than in trust. Run with no prompts only in folders you're happy for the agent to change, and keep a finger on Esc.

### The global CLAUDE.md

`~/.claude/CLAUDE.md` is loaded into every session. Aaron's is about 30 short rules plus a few machine-specific notes, and every rule traces back to a repeated real annoyance. The generalizable ones:

- Be earnest and convey true information at both a literal and vibes level. Kind but not sycophantic.
- Do what is best rather than what is easiest.
- Offer out-of-distribution suggestions by inferring the true goal.
- Never change LLM model names, even if they look wrong.
- Don't set random seeds unless asked.
- Use `trash` instead of `rm`. Use `uv` for Python.
- Scripts run with `python script.py`: no command-line arguments or interactive menus; config variables at the top after imports.
- Progress bars for anything that takes more than a few seconds.
- Parallelize when it saves real time, all workers at once, not in batches.
- For tasks with several plausible approaches (scraping, file processing), outline 2-3 approaches with tradeoffs before building.
- Stop any background servers or watchers you started before you finish.
- Keep the project's `CLAUDE.md` current when something substantial changes.
- Surface suggestions to improve the global setup, but don't edit global files unless asked.
- No em dashes in any writing. Don't hard-wrap Markdown.
- Workflows run their agents on Opus explicitly.
- A "transcribe X" recipe: one paragraph that turns a one-line "transcribe this" into a full pipeline (section 17).

The provenance is the lesson. "No command-line arguments" was typed by hand 43 times (first on 2025-10-04) before it was added on 2026-02-05. "Outline 2-3 approaches" came from a suggestion he pasted and then asked to make global. The em-dash rule came from "Plz add to your global memory: no em dashes in any writing unless specifically requested by me or there's an unusual, very compelling need". **Whenever you correct the agent the same way twice, make it a rule.**

Codex gets a near-identical `~/.codex/AGENTS.md`, so both agents follow the same house style.

### Project CLAUDE.md files

- Each project folder can have its own `CLAUDE.md`: how to run things, conventions, footguns, the goal.
- Aaron's largest work repo has one of about 149,000 characters orienting about 30 sub-projects: footguns first (marked with warning symbols), dated facts, "re-derive, never quote" for counts, and a strict VERIFIED / INFERRED grading. It is mirrored byte-for-byte to `AGENTS.md` for Codex.
- It is backed by about 46 per-folder deep-dive docs (about 4.3 million characters in total) that a multi-agent workflow wrote and, for six weeks, refreshed nightly.
- A hook refuses any edit that would push a `CLAUDE.md` past 150,000 characters, forcing "condense and move detail into the per-folder doc; never delete facts".
- **The cost lesson:** every character of `CLAUDE.md` is paid on every turn. An eval agent running inside that repo paid 95,000 cached tokens per turn just for instructions, so evals and bulk agent runs now launch from a neutral folder. **For a normal project, keep it short.**

### Hooks (small scripts that run on events)

| Event | What it does | Why |
|---|---|---|
| Before any shell command | Blocks `rm` in every form and says "use `trash` instead (recoverable)" | The cheapest insurance there is. Origin prompt: "PreToolUse: block rm, force trash, make this a global hook" |
| Stop, session end, before compaction | **Session mirror**: saves every conversation as raw JSON and a readable transcript into `<project>/claude_code/`, gitignored | "What did we decide last Tuesday?" becomes a grep. Most quotes in this guide came from these mirrors |
| Before and after edits | `CLAUDE.md` size guard | Keeps the big project file under a size budget |
| After a file write | Auto-gitignores files over 50 MB | GitHub's file-size limits |
| Session start | Shows which connectors need a fresh sign-in and re-checks in the background | Connector logins expire |
| Session start | Injects current usage and limits | So the agent sizes big jobs to the remaining quota |

**Copy at least the first one.** An `rm` guard costs nothing and makes most mistakes recoverable.

### Plugins, skills, slash commands

- **Plugins on:** context7 (current library documentation), Playwright and Chrome DevTools (browser automation), Railway (deploys), Cloudflare, a cross-session memory plugin. About 33 more are installed but off. Plugins get tried liberally and pruned when their per-session context cost outweighs the value.
- **Skills used most:** the Claude API reference, a data-visualization skill, a custom adversarial-data-collection skill, a custom connector re-sign-in runbook, workflow authoring, brainstorming.
- **Custom slash commands:** `/mcp-reauth` (re-sign in to every connector with a browser; a 39 KB runbook that appends dated "learnings" after each run), `/update` (refresh the project `CLAUDE.md`, or say "CLAUDE.md is current, no changes" and stop).
- **Built-in commands worth learning first:** `/compact`, `/goal`, `/clear`, `/model`, `/context`, `/effort`, `/init`, `/resume`, `/mcp`, `/usage`.

### Memory: four layers

| Layer | Where | What it's for |
|---|---|---|
| Claude Code auto-memory | `~/.claude/projects/<project>/memory/*.md` | Durable facts not derivable from the code: "get explicit go-ahead before standing up paid resources", "desktop-app sessions lack shell secrets", "prefer search API A over B". Injected automatically in that project |
| A memory plugin | `~/.remember/` | Rolling "what did I do today / this week" summaries, injected at session start |
| Session mirror | `<project>/claude_code/` | Full transcripts next to the project they were about |
| Codex memory | `~/.codex/memories/` | Codex's own; distilled into Claude's memory once |

A weekly scheduled "memory gardener" prunes stale memories, merges duplicates, and mines the week's transcripts for durable context. **One setting worth changing today:** Claude Code's settings keep transcripts for a limited number of days by default (`cleanupPeriodDays`); the old 30-day default silently deleted most of Aaron's pre-May history before he raised it.

### Scheduled tasks

Scheduled tasks (in the desktop app) run a saved prompt on a schedule: one rebuilt a model-comparison dashboard every morning for 94 days, one refreshed a big repo's docs nightly for 40 nights, one re-signs connectors daily at 6 AM. The trick: **scheduled prompts are written as self-contained runbooks** (background, hard "never" rules, what to do in each case, the report format), because nobody is there to answer questions. One overnight run began: "This is an automated one-time run. Aaron is probably asleep and cannot answer questions... You must never do passkeys, passwords, or 2FA... leave that tab open for Aaron and say which tab it is."

### API keys and secrets

Keep API keys in the shell environment, never in prompts or in files the agent might echo. Aaron exports his from `~/.zshenv` rather than `~/.zshrc`, so non-interactive shells see them too.

- **Refer to secrets by variable name** ("use my env variables X_USERNAME and X_PASSWORD from zshenv"). A secret pasted into a prompt lives in transcripts and mirrors forever. If you do paste one, rotate it.
- **Desktop-app and scheduled sessions may not see shell secrets** (on a Mac they inherit launchd's environment, not your shell's). Tools that need them look "broken" there; it's an environment artifact, not an auth problem.
- **Treat `.env` files as plaintext secret stores:** read only when needed, never printed, never committed.

---

## 7. Connectors and MCP

"MCP" (Model Context Protocol) is the standard behind connectors: a connector is a server that gives the model tools (search this database, read this file). Connectors added on claude.ai also appear inside Claude Code for the same account.

### What actually gets used

In Aaron's sessions the most-used were web search (Exa), the real browser (Claude in Chrome), Playwright, Chrome DevTools, and Context7. Gmail, Calendar, Drive, and Slack were occasional. **The heavily used tools are search, a real browser, and the file system.** Gmail, Drive, Slack, and Calendar are occasional "go find the context I lost" tools. Infrastructure (Railway, Cloudflare) is mostly driven through command-line tools, not MCP. Of 36 claude.ai connectors connected at some point, about 14 were ever called.

**Connectors are not free.** Every connected server's tool list is sent with every message. On 2026-07-24 a claude.ai chat hit a 74,000-token context overflow before the first message (a skills marketplace with 257 skills plus two connectors). One of Aaron's own connectors is about 26,000 tokens of tool definitions; claude.ai defers large tool lists and loads them on demand, which helps, but keep the list short and turn connectors off per chat when a task doesn't need them.

### Building your own connector

The highest-leverage connector is often one over your own data. Aaron exposed his team's dozen internal tools as a single MCP connector (about 70 tools), so colleagues can ask any Claude chat questions that hit those databases directly. Lessons from building it:

- **One combined connector, not one per tool.** Each connector is a separate sign-in for every person.
- **Reuse the sites' existing sign-in** and re-check authorization on every call; log every call with the caller.
- **Read-only by default.** The few tools that write or spend money say so in their descriptions, and stay on "ask" in the client while the read-only ones are set to "Always allow".
- **Cap result sizes and time per call** (his are 60,000 characters and 60 seconds) and tell the model how to narrow a query.
- **Put your epistemic rules in the connector's own instructions**, so every client follows them: "every figure carries a link to its source filing", "absence of an archive capture is not evidence of deletion", "never cite a bare archive link without the original URL beside it".
- **Test like a user:** a sweep of realistic questions through a real Claude client, plus an agent-level eval, after every tool change.

### Good first prompts for any data connector

They name the source, the output format, and the epistemic standard:

```
Using the <connector> tools, what does each source hold on <subject>? Give one paragraph per source with links, and say plainly where a source has nothing.
```

```
Find every <record type> matching <criteria> in <date range>. List the top ten by <measure> with totals and a link to the underlying record for each. Be precise about what the data covers, and say which totals are complete.
```

---

## 8. How to prompt

Style matters less than you would think. Aaron's is lowercase, fast, warm, and candid ("plz" and "lol" throughout), typed not dictated. What does matter: short prompts for steering and one to three paragraphs for kickoffs; context supplied by reference (`@file` mentions, pasted text, screenshots) rather than retyped; and the agent treated as a capable colleague: "you're almost certainly better than me so you are the authoritative source".

### The moves that do the most work

1. **`/goal` plus an end-state paragraph.** `/goal` (a Claude Code command) sets a condition and installs a session-scoped stop hook, so the agent keeps working until it judges the condition met. Typical shape: what should exist at the end, the quality bar, the guardrails, a model and budget, and "use your judgement beyond this". Gotcha: if you change your mind mid-run, run `/goal clear`, or the hook keeps pushing toward the old goal.
2. **Quote and verdict.** Paste one line of the agent's own output with `>` and add a two-to-five-word verdict: "make it happen", "make this automatic", "fix these two things plz", "figure this out (feel free to spend a few bucks on the api)". The cheapest precise way to accept a proposal.
3. **Explain first, then build.** "Don't actually do anything yet, just answer" or "write but don't run". Then a `/goal` once you understand the options.
4. **Define the reader and the length in human terms.** "Two pages when pasted into Google Docs, tops." "I'm not asking a manager to read 30 pages; can I get a 2-5 page version." "A thin skeleton; the writing is for me to do."
5. **Delegate judgment, with a principle.** "Your call." "I defer to you on how to operationalize this." "Use your best judgement beyond this, since I doubt this prompt is extremely precisely the best way to actually achieve the end goal."
6. **Budget in money or time.** "Stay below like 100k pulled tweets, but don't penny pinch below that." "Target $200, hard cap $250; validate that I have enough API credits first." "Hard cutoff in 15 minutes for subagents, then 5 minutes for you to compile."
7. **Guardrails as sentences.** "Non-destructive." "Without losing any existing data." "Do NOT delete it yourself; write a shell script I can run." "Make it so nothing bad happens if the whole process just fails."
8. **Prompts as files.** Long-lived instructions live in files that later prompts point at: "Read /path/driver_prompt.md and follow it exactly." A 13 KB "exhaustive audio finder" prompt file says in its header which block gets edited per run. The agent often writes the prompt file for another agent (Codex, a scheduled task, a background session).
9. **Paste raw artifacts.** Logs, alert emails, colleagues' messages ("message from colleague re [the tool]; plz help"), screenshots, and the agent's own earlier text. Your own material, work threads you were part of, and automated alerts: just paste. Someone else's private message, a client's material, or anything the sender wouldn't expect to go into an AI tool: get their OK first. Recording a meeting needs everyone's consent before you press Record (several US states require every party's consent).
10. **Side tasks in the same session.** "While that's running...", "side task:", "in the meantime".
11. **Say "continue".** The most common short prompt after `/compact`. Long runs pause on limits, interrupts, and ambiguity; one word restarts them.

### Anti-patterns seen in Aaron's history, and what replaced them

- Pasting a whole 160,000-character log and writing a single swear word (Nov 2025). It worked, but later sessions let the agent pull logs itself through command-line tools.
- Secrets pasted into prompts (a few proxy credentials in 2026). Replaced by referring to environment variable names.
- Under-specified effort. A search job that spent single-digit dollars when he expected about $100 needed "the vibe is intensive entire-internet agentic search... not 'run 5 searches, filter to .mp3 urls, download and we're done'". State the effort level up front.
- Changing your mind after `/goal` without `/goal clear`.

---

## 9. The prompt library (copyable)

Two parts: templates distilled from what works, then real prompts from Aaron's history with what happened next. Redactions are marked `[..]`. The real prompts are lowercase and typo-ridden on purpose: that's how they were typed, and it didn't matter.

### 9A. Templates

**Kick off a build**

```
/goal build <thing> in a new subfolder <name>. It should <what a user can do, described as experience, not implementation>.
Done means: <acceptance test, e.g. "live at a URL, tested with a real sign-in", "someone who isn't me can open the spreadsheet and understand it">.
Constraints: <non-destructive / don't touch X / ask before spending more than $N>.
Priority is <the one quality that matters most, e.g. reliability, speed to a working v1>.
Use your judgement on anything I didn't specify, since I doubt this prompt is exactly the best way to reach the goal. Make it actually good, not a toy demo.
```

**Turn a colleague's request into a tool**

```
/goal complete the following request as <a new tool / an addition to X>: "<paste the message verbatim, with timestamps and links (with the sender's OK if it isn't a work request to you)>". Make it excellent and professional. When done, give me a two-line summary I can reply with.
```

**Research with verification**

```
Please research <question>. For every claim, cite the source and grade it VERIFIED (primary source seen), REPORTED (secondary source), or INFERRED (your reasoning). Quote verbatim, never paraphrase inside quotation marks. Say which sources you searched that turned up nothing. Double-check anything you're not certain of, and end with a list of what you could not verify.
```

**Check a single claim**

```
Please do whatever research is necessary to say whether the following is true or false: "<claim>". See <primary source URL>.
```

**Write for humans who weren't in the conversation**

```
Write a new doc like <reference doc> but focused on clarity without losing detail. The readers are high context on this whole field but zero context on this conversation, including findings that probably don't exist elsewhere. Write like an excellent human memo: no bolding unless it serves a purpose, no fancy phrasing, as straightforward as possible but not simpler. About <N> pages when pasted into Google Docs.
```

**Weekly update**

```
/goal a brief "what I did this week" doc, categorized by project, about 2 pages in Google Docs. Use git history, notes, and files changed since last <day/time>. Here is last week's version for format: <paste>. Start with a list of anything you could not verify from the files, so I can confirm before pasting. Then add a second section: suggested notes for my 1:1.
```

**Meeting recording to notes to done work**

```
transcribe <file> (a <length> meeting between <names and roles>; jargon/spellings: <list>). Then turn it into notes: TL;DR of decisions, numbered sections with approximate timestamps, every action item with owner and date, and verbatim quotes of any guidance worth keeping. The reader may never hear the audio. Then /goal do every action item assigned to me that you can; draft anything that goes to other people, don't send it.
```

**Explain before acting**

```
<question about how to do X>. Don't actually do anything yet, just answer. If there are several approaches, give me 2-3 with tradeoffs and your recommendation.
```

**Audit with adversarial verification (workflow)**

```
/goal use a workflow (up to <N> Opus agents, no weaker models) to audit <codebase / dataset / document set> across these dimensions: <list>. Every finding must cite a file and line (or source) and give a concrete failure scenario. Then have a second agent try to refute each finding, defaulting to "not real" when uncertain. Report only findings that survive, prioritized, with a fix plan. Read-only: don't change anything.
```

**Find everything (census-style workflow)**

```
/goal use a large Opus-based workflow to find every <item type> about <subject> on the internet, then <download / transcribe / add to database X>. The bar is genuine exhaustion, not a good-college-try first page of results. Dedupe against what we already have. Have a critic round look for what's missing. Write progress to disk so a crash loses nothing. Budget: about $<N>; flag before going over.
```

**Scrape a page into a spreadsheet**

```
scrape <URL> by turning the info on that page into a structured data file with <fields> for every <item>. Then make a CSV I can import into Google Sheets. Tell me how many rows you got and anything you couldn't extract.
```

**Handoff before compacting or switching**

```
Before I compact: write a handoff doc with everything a fresh session would need to continue productively (decisions made, what's done, what's left, gotchas, file paths), and update CLAUDE.md with anything durable.
```

**Recurring annoyance to automation**

```
set up a scheduled job that does whatever you just did, daily. It must never delete data. If anything needs my attention, email me (an email API key is in my environment).
```

**Upgrade older AI work**

```
/goal <this site / doc / script> was made by a weaker model. Without changing anything substantive, find UI/UX/quality tune-ups that make it look and work better.
```

**Outsource a piece to another agent without leaking context**

```
I'd like to outsource <task> to <Codex / another agent> in a way that (1) doesn't give it any information about the deeper goals or project context and (2) ends in a state you can easily pick up. Write the self-contained prompt file and the exact output format you want back.
```

**Turn this guide into your own setup**

```
Read the attached guide. Interview me briefly (at most five questions) about how I work, then propose a short global CLAUDE.md for me: only rules that match how I actually work, each one line. Don't write any files until I approve.
```

### 9B. Real prompts from Aaron's history

**Big builds**

1. *2026-09-29, one message, 1 hour 22 minutes, 166 tool calls, ending with a live private analytics dashboard across about 12 apps:*
   > /goal add relatively detailed analytics to all of the [team's internal] tools and ideally the MCP if possible (which I guess would mean catching and logging traffic somewhere), cloud-based storage probably so like hosted alongside [the tools] (if you think that's reasonable; open to other options) for things like usage and how people are using the page/tool (ofc like whatever lower-level things imply/inform that)
   >
   > BUT I want you to use your judgement to get basically an 80/20 of usefulness for improving and understanding usage / invasiveness. So definitely not interested in very specific location, what's on their clipboard, anything like that. For now don't make the analytics themselves accessible by anyone but me (this may change, but for now)

   Why it worked: an end state, a value principle for the judgment calls, and a privacy guardrail. Claude rejected hosted analytics services because they would hand users' search queries to a third party, and was honest that the connector logging had passed a local test but hadn't yet been exercised by a real Claude call.

2. *2026-09-28, desktop app, a meeting recording to three deployed tools the same day:*
   > Goal: transcribe the most recent audio file in my home folder which is a meeting between me Aaron and [..] and then launch a substantial Opus-based workflow/subagents to pick 2-4 projects we discussed and to the extent feasible get their code live on github as private repos and real working online versions (not using fake sample data, like do your best to make them functional out of the box [...])
   >
   > Get everything live through railway or some other system including real functional api keys from my zshenv and gate sites with clerk login [...]
   >
   > Finally, put all links to sites and gh in a google doc (or md if you cant do gdocs) with brief descriptions to send to [..]
   >
   > Make sure to make the tools actually-good, not like "heres a nice toy demo or something that pattern matches with that"

3. *2026-09-23, a pasted Slack message to a live tool with about 11,500 filings by the next day, about $385 of extraction:*
   > /goal complete the following slack message request via a new tool under [our tools domain]: "Can you turn the [..] disclosures into a searchable tool for us? [...] This is the House one [...] This is the Senate one - easiest way at harvesting them all is by year I imagine". make it excellent and professional

   (A work request sent to Aaron, so pasting it was fine; for anyone else's private message, ask first.)

4. *2026-08-20, a sign-in-gated directory site, live the same afternoon:*
   > a google-auth gated website for the [team] emails and [my own email] only that is simply a simple, tasteful directory to each of the pages we have, should look nice on mobile and desktop and open things in a new tab [...] the actual pre-auth landing page should be very sparse and just have "[name]" + signin box + light styling and no other info. Use railway for this, and if you can from command line hook it up to [the domain] which I just bought via Railway Domains (don't try super hard to hook it up, it'll take me two seconds via ui if you do the rest)

   Note the last clause: it tells the agent where not to waste effort.

5. *2026-06-27, database cleanup with a safety net:*
   > /goal start by making a .tar.zst version of [the db] as backup and then get the db file itself into an actually-sensible state. The episodes table is fundamentally a shitshow. [...] You can and are encouraged to make changes to the values not substantively (obv don't change the actual information itself to something just not true) but in order to consolidate (or split up etc) columns when that makes sense. We always have the tar.zst version to return to. [...] if that was turned into eg an excel file, someone who's not me and not intimately familiar with the project should be able to understand the sheet and think it is aesthetically pleasing

   Backup first, explicit permission, explicit limits, and a reader-based acceptance test.

6. *2026-05-26, a desktop app for running local models:*
   > Make it the app you'd actually want to use, whatever that means. Lean into your preferences for function and aesthetics instead of just making a "central example" of the app

7. *2026-02-25, a forum clone for a group chat:* "wait one more thing: insofar as it is helpful, you can literally fork a github repo with any existing code. The goal is to make the thing, not necessarily to write every line from scratch." Telling the agent it may reuse existing code removes a common time sink.

**Research**

8. *2026-07-24:*
   > /goal run a workflow with no more than 10 Opus 5 subagents investigating/exploring the space of possibilities for LLM provision for highly sensitive info [...]

   Then the follow-up that made it useful: "lol this is extremely cool but it's also 30 pages in google docs and I'm not asking a manager to read that - can I get a condensed takeaway version that's like 2-5 pages".

9. *2026-08-25:* "Please do whatever research is necessary to say whether the following is true or false: '[a claim about zero data retention through an API router]' see [the docs URL]". One falsifiable claim plus the primary source.

10. *2026-07-31:* quote a legal claim, then "can you double check anything you're not certain of and give me the lowdown on these cases?"

11. *2026-07-15, personal due diligence:* "/goal use no more than 16 subagents to run a workflow researching and investigating [a business and its owner]... anything relevant to a prospective [customer] like me who might spend almost $40k. End goal = final comprehensive md report", then "can be sonnet subagents, don't need haiku or opus for this". Cap the fan-out, pick the model tier, define the reader. The workflow found a public licensing-board record that an ordinary web search had missed.

**Data and scraping**

12. *2026-09-23, ten minutes, the best first scrape to copy:*
    > /goal scrape https://[a firm's team page] by turning the info latent on that page into a structured data file with all the people there's name, role/title, and short bio [...] actually plz make two files: one json with just text info and one with base64-encodes of the headshots

    Follow-up: "sick, can you also turn the smaller file into a csv that can be imported into google sheets". Result: a 214-row sheet with image formulas for the headshots.

13. *2026-08-02, a budgeted API measurement:* "use a workflow if helpful ([top-model] subagents) to try to figure out actually what % of tweets (ideally by year) do exist in our data but don't exist via [a third-party X API]? Please actually call the api; pricing is $.15/1k tweets so try to stay below like 100k pulled tweets for now but don't penny pinch below that".

14. *2026-07-27, a data norm:* "we want to be writing stuff to disk regularly instead of hoping eg 10GB queries collect fully before flushing [...] I defer to you on how to operationalize this".

**Debugging and ops**

15. *2026-09-08, one message plus a pasted health-check email, 1 hour 18 minutes:*
    > /goal fix everything there is to fix:
    >
    > [Pasted text #1 +28 lines]

    Claude found the real root cause (a server's nightly build was being killed for running out of memory; an earlier "fix" had only deleted a lock file), deployed a self-healing fix and a memory budget, disclosed a mistake it made mid-way and fixed it, and listed what was left for a human.

16. *2026-08-24, the start of that arc:* "ugh for the nth time, plz help me fix browser access to [one of our sites] (I don't control wifi and can't easily contact person who does)", then "set a cronjob to do whatever you just did daily", then "brainstorm any others that could make sense (don't implement yet)", then "plz enact 1, 3, 4, and 8 just tbc: ideally I'd make it very hard or impossible for the jobs to *delete* any data", then "we have resend access right? make it so I get an email if anything needs my attention."

17. *2026-08-20, a mid-run correction during a move to Google sign-in:* "wait we need to make it so that the passwords DON'T work now, like there shouldn't even be an option to enter pw anymore. and actually we should boot everyone who's logged in currently and make them sign in through new method".

18. *2026-07-08:* "No change in characters written for like 30+ mins so I killed, something is wrong" plus the raw output. Symptom, what you did, raw evidence.

**Quality and verification**

19. *2026-09-09, using spare quota before a reset:*
    > /goal usage resets in 23 minutes, deploy a large [..]-based workflow to do whatever you think might be most useful to do (non-destructive, don't rework anything, just create or collect info or something, prob in a new subfolder) [...] hard cutoff in 15 mins for subagents, then hard cutoff 5 mins after that for you to compile anything. Make it so nothing *bad* happens if the whole process just fails bc of time

    Result: 12 finder reports and 11 verifier reports that tried to refute each finding. The top verified finding was a real authorization hole in a live tool (since fixed).

20. *2025-10-18:* "I am slightly suspicious that [the raw data folder] is about 61mb but then [the processed file] is only 8." A concrete quantitative smell is the best bug report.

21. *2026-07-30:* "don't anchor too hard on that skill - it's from my own work so plz feel free to draw inspiration but you're almost certainly better than me so you are the authoritative source".

22. *2026-07-27:* "/goal the whole site was made by a weaker model - without changing anything substantive see if you can find any UI/UX/aesthetic (or potentially other) tune-ups".

**Writing**

23. *2026-07-12:* "can you please write a new doc like [the earlier memo] but focusing on clarity but NOT at the expense of detail? [...] they are high context on this whole world but zero context on the last million tokens (incl pre-compaction) we've spent in this extended convo [...] please do your best to write like an (excellent quality) human memo: no bolding specific terms unless it's really serving a purpose [...] no fancy phrasing."

24. *2026-08-10:* "write up your own prose memo [...] like an excellent New Yorker or The Atlantic piece almost [...] that a smart high schooler could follow on first read. This involves curation/judgement (ie not literally everything we know should get stuffed in) [...] with inline images/graphs/diagrams described in double brackets like '[[headshot from Twitter]]' that can be filled in later". (The draft that came back was about three times too long and contained one fabricated sentence, which is why drafts get verified.)

25. *2026-05-08, tone:* "lmao I appreciate the honesty but tbh I do not consider this a crisis; can you write an adjacent report that's like more descriptive in tone [...] the critical vibe obscures and crowds out information".

26. *2026-08-31, formatting:* "[screenshot] these blocks of text are a little hard on the eyes - can you modify formatting (and tweak wording insofar as is helpful) to write like you're optimizing for attention in terms of formatting (but no randomly bolding phrases or em-dashes plz)".

**Explain first**

27. *2026-08-17:* "is there any good way to use wired ethernet for upload but wifi for download? don't actually do anything yet just answer". Then, once the options were clear: "/goal make it happen with a simple macos app with UI that lets me toggle stuff and test speeds for both directions."

28. *2026-07-23:* "what's the best way to back up the .git in a non-destructive way [...] Don't actually do anything yet I want to understand first".

**Improving the setup itself**

29. *2026-06-24:* "wait can we save this whole workflow as a skill or slash command or something? It shouldn't be unique to this project". It became a reusable documentation skill.

30. *2026-08-30:* "is there a way to automate this? they need renewal all the time and it's hella annoying", then "plz set up a slash command (may turn into a hook later but for now I'll supervise) that uses full computer use to run the oauth sign-in flow thing for everything that needs to be signed in". It became `/mcp-reauth`, which now runs daily on a schedule.

31. *2026-09-27, quote and verdict:*
    > > Suggestion: allowing Read on /tmp/** in your Claude Code settings would stop workflow agents hanging on a permission prompt when they read scratch files.
    >
    > make it happen

32. *2026-03-20, before compaction:* "the context window is getting pretty long [...] I do feel like there's a lot of important context tho - can you write up an md doc with basically any of the info/lessons/things that aren't immediately obvious from the files [...] anything you'd want to have access to to pick up productively with an otherwise minimal context window".

**Multi-agent**

33. *2026-09-24, the shortest big ask (127 characters):* "/goal use a large opus-based workflow to find all audio where [a public figure] speaks and get it live and transcribed into [our transcript database]". Then the same for three more people. One session, 2.5 days, 381 tool calls, zero interrupts. It worked because the search tooling, the transcription pipeline, and publishing were already built and documented. **Big one-liners are the payoff of earlier investment, not a substitute for it.**

34. *2026-07-03, prompt as a file:* "Ok, please run the workflow instructions described at @[..]/media_exhaustive_workflow_prompt.md ! Thanks!" (23 concurrent Opus finders in round one; 449 new episodes transcribed and live).

35. *2026-09-12, an orchestrator that reviews its workers:* "/goal use a workflow (I'll defer to u on size) Opus-based workflow to find every podcast episode and other audio/video source of [a subject] on the internet and get them transcribed and live [...] BUT while Opus can do the legwork, you ([the top model]) must look through each subagent's work and sign off on stuff before it goes live, with the option to eg send a new agent to find more where you suspect more exists, or remove duplicates".

36. *2026-08-22, outsourcing with a context firewall:* "I have way less usage on here than on codex, so I'd like to outsource the very intensive 'scan the whole internet' parallel workflow stuff to codex in such a way that (1) doesn't give codex any info about the deeper goals here or [..] project context and (2) will result in some sort of state that you can easily/best pick up on". Claude wrote a neutral 23 KB brief with a strict output format; Codex found 93 items; Claude verified them one by one and published.

**Course corrections**

37. *2026-09-23, calibrating effort with money:* "wait I'm a bit confused; I'm expecting to be spending something vaguely on the order of $100 [...] if we're spending single digit dollars we need to go way harder somehow. The vibe is 'intensive entire-internet agentic search [...]', not 'run 5 searches, filter to .mp3 urls, download and we're done'". Claude: "You're right, and the gap is structural, not budget." It re-architected the job.

38. *2026-07-27, a supervision norm:* "why don't you substantially monitor any multi-hour run, like waking to see how things are going ever 15 mins or something instead of just trying to one-shot it with no maintanence".

39. *2025-12-01, a hallucination challenge:* quote the agent's claim, then "I think you're hallucinating [this]. try to find a quote?"

40. *2026-06-23, a non-destructive correction:* "no lol the whole point is to include the [..] stuff this time. Now that you've already made this stuff just leave it as is, but plz make *another* that includes [...]". Keep the wrong artifact, make a new one.

---

## 10. When and how to step in

### The shape of it

In Aaron's history, "wait" opens about one prompt in eleven: it is the universal redirect ("wait hold on", "wait actually", "wait I'm confused", "wait also"). The other common moves are quoting the agent's output with `>` plus a verdict, status checks on long runs ("update?", "is it done", "still there?"), double-checks ("let me just confirm..."), and "don't actually do anything yet" to stay in question mode. "Stop" almost never appears, because Esc does it better. After an interrupt, the next message usually changes direction or adds a constraint; only occasionally is it a plain "continue" after an accidental Esc.

### Taxonomy with examples

- **Late-arriving context.** "wait I just got @[new brief].md - please use that as authoritative guidance or flag if anything I've asked for contradicts what is in there." "wait I hate to do this but new slack messages -> for v1 we're NOT gonna use claude processing."
- **Priority change.** "wait this is pretty urgent, just get a working v1 online asap." "this is nuts lol, we can cut off at 10 mins. Nbd. Any findings?"
- **Safety brake before something destructive.** "wait are you sure there's nothing important in there?" "for now don't even touch or do anything with files inside [that folder] bc that stuff is actively being used and changed. Ok, continue!" "can I just confirm that it doesn't *move* anything and only *copies* stuff?"
- **Correcting a fact about the world.** "wait but it's literally on his public linkedin, lol." "lmao you hallucinated, [that person] is NOT [the famous person with the same first name]." Quoting the agent's "The site is genuinely up" and then: "safari can't open the page because the server can't be found".
- **Pushback on overclaiming or tone.** "Lol we gotta tone down and streamline the README and make sure to not overpromise." "can you tone down the confidence a bit in all of these". "lol this is on *me* to be warned about - plz fix" (the agent had treated a bug in his own tool as a caveat to pass on).
- **Understanding check.** "wait I'm still not 100% sure that we are on the same page". "Sorry the names are starting to run together and I'm mostly the tech guy here".
- **Cost calibration, both directions.** Too little ("we need to go way harder") and too much ("lol wait that is a lot of money, I do really want to understand this process").
- **Process norms.** "does the workflow save all intermediate results for analysis/possible reuse? if not can u make that the case".

### What the interventions have in common

1. Early and cheap: Esc plus one line, not waiting for a bad result.
2. They carry a reason, so the agent can generalize.
3. They own a share of the confusion ("probably my fault", "I should have specified this earlier"), which keeps the exchange collaborative.
4. They are non-destructive: keep the wrong artifact, make a new one.

---

## 11. How ambitious an ask can be

### The largest single asks that succeeded

| Date | The ask | What came back |
|---|---|---|
| 2026-09-29 | Analytics on every internal tool plus the connector, private, 80/20 on invasiveness (751 characters) | One message, 1 hour 22 minutes, a live private dashboard wired into about 12 apps |
| 2026-09-28 | Transcribe a meeting, pick 2-4 projects discussed, build real tools, deploy behind sign-in, private repos, a doc of links | Three live, sign-in-gated apps, repos, and a doc the same day |
| 2026-09-24 | "Find all audio where [a public figure] speaks and get it live" (127 characters), then three more people | 2.5 days, 381 tool calls, 7 workflow launches, zero interrupts, published |
| 2026-09-23 | A pasted Slack request for a searchable database of public disclosure filings | About 11,500 filings and 307,000 pages read, every dollar figure checked against the filing text, live the next day |
| 2026-09-15 | "Turn everything under [our tools domain] into MCP connectors my boss can enable" | One connector with about 70 tools, deployed the same day, verified end to end within a week |
| 2026-09-08 | "/goal fix everything there is to fix" plus an alert email | Root cause found on the server, durable fix deployed, docs updated |
| 2026-08-20 | Replace every tool's shared password with Google sign-in, then kill the passwords and boot everyone | Same-day cutover across seven login surfaces |
| 2026-08-03 to 08-21 | One long research-support session | 17 days, 92 user turns, 654 tool calls, 42 agent launches |

### Asks that failed or needed heavy steering

- **Paywalled and bot-protected downloads** (Mar-Apr 2026): many rounds of "infinite loop again". Resolved by building a human-in-the-loop tool: the agent watched the Downloads folder while Aaron clicked the download buttons. When the blocker is a CAPTCHA, build the tool for the human step instead of fighting it.
- **A research question with no good answer** (fine-tuning a model's writing style, Jan-Feb 2026): the agent could run the experiments but not make the models good. "Sunk costs make this annoying but I think it's plausible we've been going for the wrong approach."
- **Device and toolchain bugs the agent can't observe** (an iOS widget, audio devices, home networking): slow, many rounds.
- **Under-specified effort:** a search job that spent cents because each request's tool caps were tiny, fixed only once Aaron stated the expected budget.
- **A `/goal` left armed after a change of plan:** the stop hook kept pushing the agent to build an app Aaron had decided to hand to another agent. Use `/goal clear`.
- **Continuity accidents:** a closed session ("do what you can to recover!!"), two sessions working in one folder, an account hitting its limit mid-run. These drove the session-mirror hook (section 6).

### What distinguished the successes

1. **Existing, documented infrastructure.** The 127-character prompt works because `CLAUDE.md`, the search scripts, transcription, and publishing already existed.
2. **An end state and an acceptance test,** not a list of steps.
3. **Explicit guardrails** ("non-destructive", "write a script I can run instead of deleting", "only me can see it").
4. **Explicit judgment delegation with a principle.**
5. **The agent can observe the outcome** (HTTP status, row counts, logs on a server it can reach).
6. **A budget in money or time.**

**Calibration for a newcomer:** with a current top model in Claude Code, "build me a small internal tool with a login and deploy it" is a one-afternoon, one-prompt job if you can give it deploy access. "Read these 400 PDFs and build a spreadsheet with a source column" is a one-prompt job. "Find everything about X on the internet" is a workflow job. "Make this model good at Y" or "get past this CAPTCHA" is not a prompt-sized problem.

---

## 12. Workflows and subagents

### What a Workflow is

Claude Code's Workflow tool runs a short JavaScript script that orchestrates many subagents in the background (`agent()`, `parallel()`, `pipeline()`, phases, structured JSON outputs, resume by run id) while the main session stays free. Aaron's definition: "by workflow I mean just the orchestration system within claude code for using multiple parallel agents". You rarely write the scripts yourself: you state the goal, roughly how many agents, which model tier, and a budget, and the agent writes the script. Workflows can be expensive, so ask for one explicitly.

### For scale

Runs range from a handful of agents to several hundred. The largest was 752 Opus agents over 8 hours; the median takes about 20 minutes. Plain subagents (the Agent tool) cover smaller fan-outs, mostly 1-4 at a time, including "fork" agents that inherit the current conversation for per-item audits. Parallel writers are kept apart by giving each one exclusive ownership of its files.

### The four patterns

1. **Fan-out finders, then critics, then adversarial verifiers** (research and search). The critic round's only job is to find what's missing; the verifier tries to refute each finding.
2. **N subsystem auditors plus two independent judges per finding, plus a synthesis** (code or document review). In an iOS app audit (204 Opus agents, 38 minutes), 97 raw findings became 74 confirmed after a "refute" judge (told "default to real=false when uncertain") and a "reproduction" judge ("could a real user actually hit this?"). The top finding: a phone call mid-recording silently truncated recordings.
3. **Explore, then one writer per section, then a capstone synthesis** (documentation). 13 read-only explorers, a writer per subfolder that builds its document incrementally (outline first, then section by section, so a dropped connection doesn't lose the file), then a combined synthesis.
4. **A deterministic controller hands tasks to agents, so everything resumes from disk** (long batch jobs). A Python controller decides the next batch from what's on disk and writes each task's prompt to a file; the workflow script has no domain logic. Any run can die and be relaunched with the same arguments.

### Example script (trimmed): an audit with double verification

```js
export const meta = {
  name: 'app-audit',
  description: 'Multi-dimension audit with adversarial verification',
  phases: [{ title: 'Audit' }, { title: 'Verify' }, { title: 'Synthesize' }],
}

const GROUND = `You are auditing a real app at <path>.
RULES:
- READ THE ACTUAL FILES. Never speculate about code you have not read.
- Every finding MUST cite file and line number, and quote the offending code.
- A finding must have a concrete failure scenario: specific user action -> specific wrong behavior.
- If a subsystem is actually fine, say so. Do not manufacture findings.`

const DIMENSIONS = [
  { key: 'audio-session', prompt: 'Audit recording and interruptions (phone call mid-recording) ...' },
  { key: 'data-model',    prompt: 'Audit persistence: anything that can LOSE a user recording.' },
  // ... 7 more subsystems
]

const results = await pipeline(
  DIMENSIONS,
  d => agent(`${GROUND}\n\nYOUR ASSIGNMENT (${d.key}):\n${d.prompt}`,
             { label: `audit:${d.key}`, phase: 'Audit', model: 'opus', schema: FINDINGS }),
  r => parallel(r.findings.map(f => () =>
    parallel([
      () => agent(`${GROUND}\nAdversarially REFUTE this claimed defect. Default to real=false when uncertain.\nCLAIM: ${f.title} ${f.file}:${f.line}`,
                  { phase: 'Verify', model: 'opus', schema: VERDICT }),
      () => agent(`${GROUND}\nYou are a REPRODUCTION judge: could a user realistically hit this?`,
                  { phase: 'Verify', model: 'opus', schema: VERDICT }),
    ]).then(votes => ({ ...f, survived: votes.filter(v => v && v.real).length >= 1 }))
  ))
)

const confirmed = results.flat().filter(f => f && f.survived)
const plan = await agent(`${GROUND}\nVerified defects:\n${JSON.stringify(confirmed)}\nWrite a prioritized fix plan.`,
                         { phase: 'Synthesize', model: 'opus' })
return { confirmedCount: confirmed.length, confirmed, plan }
```

### What went wrong, and the fixes

| Failure | Fix |
|---|---|
| About 16 Opus agents starting cold at once hit a server rate limit | A concurrency cap of about 5, plus retries |
| A usage limit killed every agent at once and nothing was cached | Agents write progress to disk every few dozen items; a relaunch tells them to read partial output first; the job gates itself on measured usage |
| Web search is capped per session across all agents (200 searches) | Agents search through a small command-line tool backed by a search API (about $1 per 1,000 searches) |
| Unattended agents hung for an hour on a permission prompt | Scratch files confined to allowed paths; read access to `/tmp/**` allowed |
| A background driver sat idle for 3.5 hours after a network blip | A watchdog that restarts drivers (at most 6 times a day) |
| A finder silently failed and the result was thin | A dedicated re-run for the gap; critic rounds that look for what's missing |
| Costs blew up | Agent caps and dollar budgets in the prompt; medium effort for bulk agents |
| An agent-written QA step quarantined 1,072 of 1,073 good transcripts (a surname-particle bug) | Print a sanity line after every QA step, and read it |

---

## 13. Long runs, compaction, and continuity

### The mechanics

- **`/goal`** keeps a session working until a condition holds (section 8). This is the main autonomy mechanic.
- **Monitor** streams a background process into the conversation: `tail -f run.log | grep --line-buffered "DONE|FAILED|Traceback"`, polling a server until a build exits, a "brake" that prints a warning at 85% of the usage window. The agent gets woken by events instead of guessing.
- **A scheduled wake-up** as a fallback heartbeat: "check on workflow X and continue the goal", in case a notification doesn't arrive.
- **`/loop`** was tried and found clumsy ("the loop thing was a bit of a pain"); workflows plus Monitor replaced it.
- **Scheduled tasks** (section 6) for anything recurring.
- **Background driver sessions** (`claude --bg ... "Read <prompt file> and follow it exactly."`) with a watchdog, for jobs too big for one session.
- **Remote Control** is on at startup, so every session can be watched and steered from claude.ai or the phone; **push notifications** arrive when a job finishes or needs input.
- **Cloud-side:** anything that must run while the laptop sleeps lives on a cloud host (Railway, a small rented server) or Anthropic's cloud. A daily "follower-trends analyst" is a managed agent on a cron that writes into a memory store and never touches the production database directly.
- **The rule "stop any background servers or watchers you started"** exists because leftovers "keep running old code and can silently consume later jobs".

The supervision norm Aaron set after one unattended failure: "why don't you substantially monitor any multi-hour run, like waking to see how things are going every 15 mins". One overnight build ran on a Monitor that re-armed itself about a dozen times, each time checking fetch progress, batch submissions, and errors.

### Compaction

When a conversation's context fills, Claude Code summarizes it ("compaction") and continues from the summary.

- **Manual first.** Compact on purpose rather than waiting for the automatic one (about four in five of Aaron's compactions were a typed `/compact`).
- **Late.** His median context size before compacting was about 217,000 tokens (on 1M-context models), the maximum 944,000. After compacting, about 20,000.
- **With instructions.** `/compact note that we will be going with option A!`, `/compact please update todo list and anything else... this is just bc we're running out of context`, `/compact also note that I'm renaming ai_screening.py to match_only_ai.py`. Pin decisions and renames in the argument; they are what gets lost.
- **Before a big compaction or a `/clear`:** "write up an md doc with the lessons/things that aren't obvious from the files", and "update CLAUDE.md with anything relevant".
- **After:** "remind me what we've been up to and just done based on the compaction summary".

### Continuity lives in files

Nothing important should live only in a conversation:

- **`CLAUDE.md` and per-folder deep-dive docs** orient any new session in a project.
- **Handoff docs** for "the next agent": a numbered briefing folder so a fresh agent could continue research cold; a one-page "here's what you need to get this live on beta" note for a parallel session; a sanitized handoff so Codex could work on code without seeing any client context.
- **Background drivers write end-of-run notes** for the supervising session.
- **Session mirrors** preserved transcripts that later vanished from Claude Code's own storage.
- **Scheduled prompts point at a runbook file** "(follow it even if earlier context was compacted away)".

Two traps worth knowing: after a restart mid-turn, the old turn can keep running as a background "twin" that overwrites files the resumed session writes (check the running sessions after any resume); and a conversation resumed in a new process waits for typed input, so running work stalls until you say "continue".

### What lives where

Laptop disk is the usual constraint (Aaron's Mac hit 100% full once, mid-job), so bulk data goes to external drives (moved by an idempotent script that leaves symlinks behind) and cloud storage (Backblaze B2, Cloudflare R2). Anything that must run while the laptop sleeps goes to a cloud host. Anything that needs his logins stays in his real browser. Code goes to private GitHub repos as a backup, pushed only when he asks.

---

## 14. Browser and computer control

| Tool | Used for |
|---|---|
| **Claude in Chrome** (an extension in your real Chrome, with your logins) | Logged-in pages, connector consent screens, getting API keys from consoles |
| Playwright (a clean automation browser) | Scraping, screenshots, QA of deployed sites |
| Chrome DevTools | Debugging a site's console and network, screenshots, Lighthouse |
| iOS Simulator | Testing an iPhone app |
| Computer use, AppleScript | Native Mac apps, consent flows |

**Real Chrome wins whenever logins matter.** Playwright and DevTools launch clean profiles with no sessions, so they're for QA of your own sites and for public pages. For pages that need a login and have no API, Aaron often has the agent build **a small Chrome extension** instead (dozens since late 2025: follower lists, group-page captures, a meeting-notes export, a "save as MHTML" button for colleagues).

**The `/mcp-reauth` runbook** is the best example of browser automation with judgment. Its rules, verbatim: "Never type passwords, 2FA codes, or passkeys; if a login wall appears, tell the user to sign in, wait, then resume. Before approving any consent screen, read it: the requesting app must be Claude / Claude Code / Anthropic and the service must be the one you expect. Anything surprising: stop and show the user." It once found an unexpected "rclone wants Gmail access" tab and left it alone. Each run appends dated field notes, so the runbook gets smarter.

**Known limits:** some consent interstitials reject extension-driven clicks (a human click works); the extension only sees tabs in its own tab group; the browser may be logged into a different account than you think; bot walls (Akamai, Cloudflare) refuse headless browsers and datacenter IPs; X throttles logins after a handful of attempts; some archive sites serve CAPTCHAs to automation. `curl_cffi` with browser impersonation gets past many bot walls where plain HTTP libraries fail; if a site's terms forbid automated access, don't.

---

## 15. Verification: measured, not instructed

The most important lesson from Aaron's research work: **quote fidelity and factual accuracy must be measured, never just instructed.** "Quote verbatim" in a prompt reduces errors but does not eliminate them. A second reviewer on a batch of finished deliverables found nine real defects, including a quote silently paraphrased, "held off by request" degraded to "not pursued", and a pending step written in the past tense.

Standing rules for anything factual:

- **Grade every claim.** VERIFIED (the agent saw the primary source), REPORTED (a secondary source says so), INFERRED (the agent's reasoning). Each with a URL or file path.
- **Quotes are verbatim**, copied from the source, with source and date. Never paraphrase inside quotation marks; never stitch two sentences into one quote. When a quote matters, re-open the source and string-match it. Machine transcripts contain recognition errors: before quoting audio, hear the clip.
- **Absence of a result is not evidence of absence.** Say which sources were searched and turned up nothing, and how complete each is. A missing web-archive capture is not evidence a page was deleted. A zero from a source that failed a positive control (a known-present item it should have found) carries no information; when you report a null, name the positive control that worked.
- **End every research deliverable with what could not be verified**, and what a human should check. This list is what makes a draft safe to forward.
- **Don't overclaim.** "The site is genuinely up" is a claim that needs a check the agent actually ran (it wasn't up). "Nothing notable here" is a valid result; don't manufacture findings to seem useful.
- **Verify in a separate pass from drafting:** a second agent told to refute each finding and to default to "not real" when uncertain, or a mechanical string match of every quote against its source, or a human spot-check.
- **Tone:** descriptive rather than alarmed. "The critical vibe obscures and crowds out information."
- **Absolute dates, not relative ones** ("2026-09-22", not "last Tuesday"), and numbers carry their date ("as of 2026-09-29").

---

## 16. What agents can't do (yet), and the workarounds

| Limit | Real instance | What works instead |
|---|---|---|
| Human logins, 2FA, passkeys, CAPTCHAs | Paywalled paper downloads; X logins; archive sites | Never type secrets; stop, leave the tab open, tell the human. Build a human-in-the-loop tool (the agent watches a folder while you click) |
| Consent screens that need a human decision | Choosing a Slack workspace; a hosting provider's permission set | Record the decision in memory or the runbook so the next run knows |
| Seeing things it can't observe | Phones, audio devices, a home router silently intercepting a site | Give it a way to observe (logs, a diagnose script, screenshots), or expect slow iteration |
| Usage limits and credits mid-run | Two workflows died together at "out of usage credits"; an API key hit its spend cap mid-batch | Checkpoint to disk; gate on measured usage; auto-resume; phone alerts |
| Rate limits and bot walls | Cold-starting 16 agents; datacenter IPs refused; a government site that blocks parallel requests | Concurrency caps, retries, politeness rules written into `CLAUDE.md`, sequential requests with delays |
| Permission prompts stall unattended agents | Agents hung an hour on a scratch-file read | Auto mode, allow rules, confined scratch paths |
| Overclaiming and thin outputs | "The site is genuinely up" (it wasn't); a draft memo with a fabricated sentence; a finder that silently failed | Adversarial verifier agents; "default to real=false when uncertain"; "do not manufacture findings"; ask for what couldn't be verified; hand-verify quotes |
| Being wrong about its own tools | The agent said a connector wasn't available; it was | Push back once, with a screenshot |
| Long-context drift | "you forgot about [the earlier dataset]" | Compact with instructions; keep decisions in files |
| Huge project context on every agent | 40,000 of 118,000 fixed tokens per bulk agent came from a big `CLAUDE.md` | Launch bulk agents from a neutral folder |
| Environment surprises | Desktop-app sessions missing shell secrets; an `ANTHROPIC_API_KEY` making Claude Code bill the API | Know the environment; strip the key |
| Logic bugs in agent-built QA | A surname-particle bug quarantined 1,072 of 1,073 transcripts | Print a sanity line after every QA step and read it |
| Judgment calls that are the user's | Whether to rewrite git history; whether to purge a data store | Mark these "no remediation should be improvised" in `CLAUDE.md`; the agent surfaces options, the human decides |

---

## 17. Meetings and transcription: the most underrated input

**Record the meeting, then "/goal accomplish everything".** A recorded meeting is close to a finished spec: every decision and assignment, in everyone's own words. A half-hour meeting, transcribed and dropped into Claude Code with `/goal accomplish everything we agreed to in this meeting`, mostly just works: the agent writes the notes, does the action items that are yours (research, spreadsheets, drafts of follow-up emails, even small tools), and lists what needs a human. Aaron's biggest single day came this way: one meeting recording in, three deployed sign-in-gated tools out, the same day (section 11). No other input packs as much context per minute of your time.

**Consent first, every time.** Tell everyone you're recording and get their OK before you press Record. Several US states require every party's consent, and it's the decent norm regardless. Transcripts of private meetings are confidential: keep them local.

### The pipeline

Aaron's transcription is one self-contained Python script: an audio file, a URL, or a YouTube link goes in; a clean, speaker-named Markdown transcript comes out.

1. **A speech-recognition API** (ElevenLabs Scribe v2) does the recognition, with speaker separation and word timestamps. Note this step is not zero-retention by default: the provider keeps the audio and transcript until deleted, and its terms may allow training use unless the account opts out.
2. **A top Claude model** (routed with zero data retention enforced on every request) rewrites the raw transcript: fixes recognition errors from context ("homophones, e.g. 'UGC' vs 'UDC'"), names speakers from evidence in the audio, adds timestamps, and writes a speaker roster that explains each identification.
3. **Long audio is transcribed whole** (so speaker labels stay consistent) and then polished in overlapping windows of about 75 minutes, in parallel.

Measured over six real runs: **about $1 and about 5 minutes per hour of audio.**

Before (raw recognition):

```
[00:00.70-00:02.34 speaker_0] So I'll wait for you on that.
[00:04.04-00:04.10 speaker_1] Yeah.
[00:04.10-00:13.38 speaker_0] Okay. So the other thing is the thing we had been talking about. So I think we are back to you just making us a thing.
```

After:

```
**[00:00:00] C:** So I'll wait for you on that.
**[00:00:04] Aaron Bergman:** Yeah.
**[00:00:04] C:** Okay. So the other thing is the thing we had been talking about. So I think we are back to you just making us a thing.
```

In his global `CLAUDE.md`, "transcribe X" is a defined verb: one paragraph tells the agent which script and interpreter to run, to write a notes line with speaker names and spellings, and where to file the outputs (only the audio, `transcript.md`, and any notes doc stay next to the recording; everything else is archived with a `WHERE.md` pointer). So the prompt is one line: "please transcribe @recounted_history.m4a... Hints: only one speaker". **Always pass names and jargon:** one early run rendered a person's surname wrong throughout.

### Notes in a house style

A wrapper script reads all new transcripts, decides whether consecutive recordings are one meeting or several, names each meeting, and writes notes in a fixed style: date and attendees, a TL;DR of decisions, numbered topic sections with approximate timestamps capturing "every decision, every assignment (who, what, by when), standing-rule changes, spend authorizations", an action-item checklist, and verbatim quotes of any guidance worth keeping. "Be thorough; these notes are the durable record; the reader may never hear the audio." Every weekly meeting since mid-August 2026 has gone through it.

### Without any scripts

Take any recorder's transcript (Zoom, Meet, Otter, a phone app), upload it (with the participants' permission) to a claude.ai Project whose instructions are the notes style above, and add a cast list with spellings. Chat can write the notes; only an agent like Claude Code can then go do the action items.

---

## 18. Everyday non-coding uses

About 10-15% of Aaron's Claude Code prompts are clearly non-coding work, and more rides along inside coding sessions.

- **Weekly updates.** Each week one `/goal` compiles "what I did this week" from git history, daily notes, meeting notes, and live counts, grouped by project, about two Google Docs pages, plus suggested notes for a 1:1. Every draft opens with what couldn't be verified from the files ("whether the memo actually went out", "whether an invoice was sent"). The format carries forward because the agent reads last week's file. About 5-10 minutes each.
- **Status docs, agendas, 1:1 prep:** "make me a coherent 'projects/things to consider attacking' document, ordered by overall recommendedness"; "a thin but comprehensive skeleton doc for the next meeting: minimal writing (that's for me to do), but enough structure that everything important is gestured at"; "Otter-esque notes about where things stand as of today, focusing on todos".
- **Research memos and briefings,** always with the length set in human terms and the evidence graded.
- **Email:** rare, and the agent gathers while Aaron writes. "Please read the email and help me write a good response. Just dump any relevant info into a new md file and I'll turn that into a human-written email."
- **Personal:** e-card websites for family birthdays, a ticket-availability monitor that alerts only on a fresh fetch, a flight-fare dashboard ("ask before spending more than $5"), a window air conditioner controlled through its vendor's API, housing searches, a forum clone for a group chat. In chat: taxes, benefits, how to vote on a shareholder ballot, device troubleshooting.

---

## 19. What this approach has built

Worked examples of what one person plus Claude Code produced, with Aaron as product owner and QA and the agent writing essentially all of the code. Work tools are described generically.

| What | Scale | How long |
|---|---|---|
| A sign-in-gated directory of a team's internal tools | About a dozen tools behind one Google sign-in | Domain bought to live in an afternoon |
| A podcast and video transcript database with search, SQL, an in-product Claude assistant, and a quote player that plays the exact audio for selected text | About 16,800 transcribed recordings, about 6,400 audio hours | First version in a day; features added from meeting requests over months |
| A searchable database of a public government disclosure set | About 11,500 filings, 307,000 pages read, costs verified against the filing text on 90-94% | Slack message at 6:47 AM to live the next day, about $385 of extraction |
| A Wayback Machine reader: a site or an X handle in, every archived version out as a searchable spreadsheet with deletion flags | One account: 40,809 archived tweets recovered, 4,237 confirmed deleted | Meeting ask to live in two days |
| One MCP connector over all the tools | About 70 tools, 172 tests, a 62-call realistic-question sweep | One `/goal`, verified end to end within a week |
| Google sign-in across every tool | Seven login surfaces cut over; old passwords killed and sessions ended the same day | One morning |
| First-party analytics for every tool | About 12 apps plus the connector | One message, one night |
| The transcription pipeline | About $1 per audio hour | Grew from older scripts over a year |
| [The tweet archive on this site](https://abergman.com/tweets) | Every public tweet, as HTML and Markdown, updated every few hours | One session |
| Weekly updates | Ongoing | 5-10 minutes each |

The pattern: a Slack message or a meeting recording in, a working tool out, usually within a day. That is the payoff of rungs 3 and 4 of the ladder, and of the documented infrastructure that makes short prompts work.

---

## 20. The on-ramp (with starter CLAUDE.md files)

The levels are a map, not a curriculum: install Claude Code and start at level 3 on day one, with a real task.

### Level 1: better chat habits

1. **One Project per goal,** with the goal as the description and the 3-5 key documents uploaded. One coherent corpus per Project.
2. **A short instruction block for the Project:** the register ("Wikipedia-ish, heavy citations"), grade claims VERIFIED / REPORTED / INFERRED, quote verbatim with source and date, say when unsure.
3. **Drop the file, give a verb:** "Summarize in detail", "Explain", "What's odd or missing here?". Use Research mode for anything needing 10 or more sources.
4. **Utility Projects** for repetitive transforms ("reformat as Markdown, same words"; "translate verbatim, keep names in the original script alongside").
5. **Check the model selector,** prune connectors you don't use, and push back once when the model says it can't do something.

### Level 2: connectors

1. Connect only what you'll use this week; turn the rest off.
2. Set read-only tools to "Always allow" so chats don't stall on approvals; leave anything that writes, sends, or spends on "ask".
3. Ask cross-source questions that name the sources, the output format, and the standard of evidence (section 7).

### Level 3: a coding agent on your own machine

Realistic for non-engineers after a half-hour of trying it: point it at a folder of PDFs, CSVs, or exports and get a spreadsheet, a timeline, a cleaned dataset, a chart, or a memo draft that cites file paths; batch-rename or convert files; turn a folder of transcripts into notes. Hold off on deploying things, touching shared servers, and handling credentials until you've watched it work for a while.

1. Install Claude Code, add an `rm`-blocking hook (or at least the rule "use `trash`, never `rm`"), and paste section 21 into `~/.claude/CLAUDE.md`, trimmed to taste.
2. Make a folder for one real job, put the source files in, open it in Claude Code, and add the starter project `CLAUDE.md` below.
3. "Read every file in this folder and build `timeline.md`: one row per dated event, with the file name and a verbatim quote for each."
4. "Turn `exports/*.csv` into one clean spreadsheet with a Sources column; tell me any rows you dropped and why."
5. Record one meeting (with everyone's consent) and run "/goal accomplish everything we agreed to in this meeting" on the transcript.
6. End each session with "update CLAUDE.md with anything a fresh session should know".

**Starter `CLAUDE.md` for a research or document folder:**

```markdown
# Project: <subject>
- Goal: <one sentence>. Deliverable: <memo / spreadsheet / timeline>.
- Every factual claim cites a file path or URL; grade it VERIFIED / REPORTED / INFERRED.
- Quotes are verbatim, copied from the source; never paraphrase inside quotation marks.
- Absence of a result is not evidence of absence; say which sources were searched.
- End every deliverable with a list of what you could not verify.
- Never send licensed data or anything marked no-AI to a model.
- Don't delete files; if something must go, move it to the trash. Ask before any paid action.
- Be earnest and not sycophantic; say so when you're unsure.
- No em dashes. Plain, Wikipedia-ish register. Don't hard-wrap Markdown.
```

**Starter global rules (`~/.claude/CLAUDE.md`)** worth copying from Aaron's:

```markdown
- Please be earnest and try your best to convey true information at both a literal and vibes level. Be kind but not sycophantic.
- Do what is best rather than what is easiest.
- Feel free to offer suggestions beyond the literal question by inferring my actual goal.
- Never change LLM model names, even if you think the name is wrong; it may postdate your training data.
- For tasks with multiple plausible approaches, outline 2-3 approaches with tradeoffs before building.
- Use `trash` instead of `rm`. Use `uv` for Python.
- Scripts should run with `python script.py`: no command-line arguments or interactive menus; config variables at the top after imports.
- Progress bars for anything that takes more than a few seconds.
- Stop any background servers or watchers you started before you finish.
- Keep the project's CLAUDE.md current when you've done something a fresh session would need to know.
- No em dashes. Don't hard-wrap Markdown.
```

### Level 4: workflows and automation

A weekly digest of a topic you track; a saved meeting-notes skill; a scheduled health check that emails you only when something changes; a census-style workflow when you need "everything about X". Write scheduled prompts as runbooks (section 6), cap spend in the code, and make every long job resumable from disk.

### A first-week checklist

- Turn one correction you've made to an AI twice into a written rule.
- Make a Project for your main ongoing work with a five-line instruction block.
- Install Claude Code and add the `rm` guard.
- Give it one real chore in a folder of real files, with an acceptance test.
- Paste one real request from someone else (with permission) and ask for a plan, then a `/goal`.
- Record one meeting with everyone's OK and have the agent do your action items.
- Ask for "what you could not verify" at the end of one research answer, and check two of its links yourself.

---

## 21. The short version: paste this into your CLAUDE.md

A dense distillation of this guide, written for an agent to read rather than a person. Paste it into `~/.claude/CLAUDE.md` (global) or a project's `CLAUDE.md`, and delete whatever doesn't fit how you work. Every character is paid on every turn, so shorter is better.

```markdown
## How to work with me

- Default to doing the task end to end, the way a capable colleague would. Show the result; add at most one short line naming a technique I could reuse.
- Before anything hard to undo, say in one line what you're about to do and why: deleting, overwriting, pushing, deploying, sending messages or email, spending money, touching anything shared. Everything else: just do it.
- Be earnest: convey true information at both a literal and vibes level. Kind, not sycophantic. If something failed, say so with the evidence. If you're unsure, say how unsure. If my plan has a flaw, say so before building it.
- Infer the real goal. If the literal ask is a step toward something bigger, mention the better path in a line or two, then do what was asked unless the better path is obviously what I want.
- When a task has several plausible approaches (scraping, file processing, anything with platform constraints), give 2-3 with tradeoffs and a recommendation before building, unless I said "your call" or used /goal.
- Before saying "I can't access X" or "that tool isn't available", check (list your tools, try the call). You are often wrong about your own capabilities.
- Never "correct" a model name I give you; it probably postdates your training data.

## Hard rules

- Use `trash`, never `rm`. Back up a database or spreadsheet before modifying it in place. Keep a wrong artifact and make a corrected new one rather than overwriting. Never rewrite git history, force-push, or delete cloud resources unless I explicitly ask.
- Secrets: refer to keys by environment variable name; never print, echo, commit, or paste a secret. Read .env files only when needed. In deployed code, pass API keys explicitly from a named env var, never via the SDK's default.
- Logins, 2FA, passkeys, CAPTCHAs, consent screens: never type passwords or codes, never approve something you don't understand. Stop, leave the page open, and tell me exactly what to click.
- Money: ask before any paid action whose cost you can't bound or that is likely to exceed a few dollars. State the expected cost. Put a hard cap in the code for bulk jobs, and report spend.
- Other people's words: recording a meeting requires everyone's consent first. Don't upload private material (meetings, client files, someone else's messages) to paste sites, public repos, or unfamiliar third-party services.
- Respect sites' terms and rate limits; sequential requests with delays for fragile or government sites.

## Facts and research

- Grade factual claims VERIFIED (saw the primary source), REPORTED (a secondary source says so), or INFERRED (your reasoning), each with a URL or file path.
- Quotes are verbatim, with source and date. Never paraphrase inside quotation marks. When a quote matters, re-open the source and string-match it.
- Absence of a result is not evidence of absence: say which sources you searched and how complete they are, and name a positive control that worked.
- End research deliverables with what you could not verify and what a human should check.
- Don't overclaim ("it works", "it's live") without a check you actually ran. "Nothing notable" is a valid result; don't manufacture findings.
- For anything that will leave my hands, verify in a separate pass: a second agent told to refute each finding (default "not real" when uncertain) or a string match of every quote.
- Absolute dates, not relative ones. Numbers carry their date.

## Writing

- Lead with the answer. Write like an excellent human memo: plain, straightforward, no random bolding, no hype, no "In conclusion".
- If I haven't named the reader and length, pick a sensible short default and say so.
- No em dashes; use commas, colons, parentheses, or periods. Don't hard-wrap Markdown.
- When I want to write something myself, gather rather than draft: put the relevant facts in a file.

## Code and data

- Python via uv. Scripts run as `python script.py` with config constants at the top: no command-line arguments or interactive menus unless I ask. Progress bars for anything longer than a few seconds.
- Long or bulk jobs are idempotent and resumable: skip work already on disk, cache per item by a stable id, write to .tmp then rename, flush results regularly. Adding items to an input list and re-running must process only the new items and never re-pay for finished ones.
- Monitor multi-hour runs (check about every 15 minutes and adapt) rather than fire and forget. Stop any servers or watchers you started before you finish.
- Parallelize when it saves real time: all workers at once, not batches. For multi-agent workflows, cap cold-start concurrency, checkpoint to disk, and pin agents to a strong model explicitly.
- Spreadsheets for humans: CSV that imports cleanly into Google Sheets (UTF-8, one header row), always with a source/URL column; tell me the row count and what you couldn't extract.
- Git: commit only when asked; never commit secrets or files over 50 MB.

## Continuity

- Keep context in files, not the chat: decisions, progress, and gotchas go in NOTES.md or a handoff doc as you go.
- Keep this project's CLAUDE.md current when something substantial changes (how to run things, conventions, footguns), and keep it short.
- When I correct you the same way twice, suggest a one-line rule for this file.
```

---

## 22. Ideas for a team, from safe to reckless

A brainstorm on getting colleagues from "I use chat" to handing an agent real jobs with minimum friction. The point is to jump straight into real work, not lessons.

**Probably a good and safe idea**

- **A one-command setup** that installs the agent, a sensible settings file, an `rm` guard, and a shared team-context `CLAUDE.md`, with a one-click undo. The biggest friction is setup, not skill.
- **A first session that is a real task.** The setup ends by starting the agent in a work folder with a prompt that asks what you're working on and then offers to just do it.
- **Context that coaches lightly:** the team `CLAUDE.md` tells the agent to do tasks end to end and add at most one line naming a reusable technique, so people learn the moves by watching them used on their own work.
- **Record internal meetings** (with consent) and run "accomplish everything we agreed to" after each one.
- **A 30-minute "do your real thing" pairing:** the colleague brings a chore they'd otherwise do by hand and types the `/goal` themselves; the experienced person only interrupts.
- **A channel for wins and prompts:** the prompt, the result, what you'd change.
- **Shared team skills** ("verified research", "weekly update", "memo for the boss"), so everyone's agent speaks the house style.

**Ambitious but defensible**

- **Remote Control on by default**, so a job can be started from the phone after a meeting.
- **An opt-in "what I did with the agent today" hook** posting a one-line summary to a team channel.
- **A weekly self-review agent** that reads a person's own session transcripts (locally) and suggests two `CLAUDE.md` rules and one skill, the way Aaron's rules were born from repeated corrections.
- **A cloud dev box per person** where running with no permission prompts is always safe because there's nothing on it to break, and long jobs run while the laptop sleeps.
- **A drop folder** watched by a scheduled agent: drop a PDF, CSV, or recording; get a structured summary and a proposed next step.

**Aggressive (defensible only with real guardrails)**

- **Everyone on no-prompts mode by default**, with hooks and a briefed classifier as the only rails. Faster; also one bad instruction away from a deleted folder that isn't in the Trash (an `rm` hook doesn't cover everything).
- **A meeting bot that joins every call** (announced), transcribes live, and starts on action items before the call ends.
- **Read-only Slack and Drive connectors for everyone**, so "find the context I lost" works team-wide. Many organizations reasonably gate this.

**Reckless and unwise**

- **"/goal do my job" at 6 AM daily, for everyone**, with email, Drive, Slack, and Calendar connectors in write mode and every tool auto-approved. Some days astonishing; eventually it emails a client something it shouldn't.
- **Auto-send every follow-up email from every meeting** the moment the transcript lands, with no review. Removes the last friction and the last chance to catch a hallucinated commitment.
- **Hand the agents logins to licensed or billed services** "because it would be faster", when the license or the provider forbids automation.
- **Put production-server keys on every laptop** so anyone's agent can "fix everything there is to fix" on shared infrastructure.
- **Let findings auto-publish** as soon as verifier agents pass them. Verification catches most errors; defamation law cares about the rest.

**The line between the tiers:** going faster is safe when mistakes stay local and recoverable (your folder, drafts, the Trash, a backup). It becomes reckless when an agent can act irreversibly on other people: sending, publishing, deleting shared data, spending, or touching licensed and legal systems. The first two tiers keep a human at that line.

---

## 23. Glossary and sources

### Glossary

- **Claude Code:** Anthropic's agent that runs on your machine (terminal, desktop app, IDE), reads and writes files, and runs commands.
- **Coding agent:** the general category (Claude Code, Codex, Cursor's agent, and others).
- **CLAUDE.md:** a Markdown file of instructions Claude Code loads into every session (global in `~/.claude/`, per project in the project folder). Codex reads `AGENTS.md`.
- **`/goal`:** sets a condition and keeps the session working until it's met.
- **`/compact`:** summarizes the conversation to free context; add instructions for what to keep.
- **Workflow:** a script that orchestrates many parallel subagents.
- **Subagent:** a separate agent instance a session spawns for a sub-task.
- **MCP / connector:** a server that gives the model tools for an outside system.
- **Hook:** a script that runs automatically on an event (before a command, at session end).
- **Skill:** a packaged set of instructions the agent loads when relevant.
- **Auto mode:** a permission mode where a classifier approves safe actions and blocks risky ones.
- **Remote Control:** controlling a Claude Code session on your computer from claude.ai or the phone.
- **Scheduled task:** a saved prompt that runs on a schedule.
- **ZDR:** zero data retention.

### Sources

Aaron's `~/.claude/history.jsonl` (every typed Claude Code prompt), Claude Code transcripts and the desktop app's session store, session mirrors, a claude.ai export from 2026-07-31, his `settings.json`, hooks, commands, skills, and scheduled tasks, Anthropic cost reports, his work repo's docs and git history, and his transcription script. An earlier, internal version of this guide was compiled on 2026-09-29 by Claude from notes by seven research agents and spot-checked against the files; this public version was adapted from it by Claude on 2026-10-10, with work-specific material generalized or removed. Counts differ slightly between methods (for example, compactions counted by boundary markers versus typed commands); where they differ, the more conservative figure is used.
