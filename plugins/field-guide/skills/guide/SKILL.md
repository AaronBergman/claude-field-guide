---
name: guide
description: Answer questions about working with coding agents from Aaron Bergman's field guide "How I use coding agents" (abergman.com/ai) - delegating whole jobs, prompting, /goal, CLAUDE.md and hooks, verification, workflows and subagents, long runs and compaction, meetings, plans and costs. Use when the user asks how to set up, prompt, or get more out of Claude Code or a similar agent.
argument-hint: "[question]"
---

# Ask the field guide

Question: $ARGUMENTS

The full guide is bundled with this skill at `${CLAUDE_SKILL_DIR}/reference/how-i-use-coding-agents.md` (the `reference` folder next to this file). It's about 100 KB, so don't read it whole. Use the section map below, grep for the heading (`## 12.`) or for keywords, and read only the sections you need.

**Section map:** 1 TL;DR, fifteen things worth stealing. 2 The four-rung ladder (chat, connectors, a coding agent, autonomous and multi-agent). 3 Plans, limits, and cost. 4 Surfaces: terminal, desktop app, phone, chat. 5 Models and effort. 6 Setup: permissions, CLAUDE.md, hooks, skills, memory, secrets. 7 Connectors and MCP. 8 How to prompt. 9 The prompt library (templates and real prompts). 10 When and how to step in. 11 How ambitious an ask can be. 12 Workflows and subagents. 13 Long runs, compaction, continuity. 14 Browser and computer control. 15 Verification. 16 Limits and workarounds. 17 Meetings and transcription. 18 Non-coding uses. 19 What this approach has built. 20 The on-ramp and starter CLAUDE.md files. 21 The paste-into-CLAUDE.md short version. 22 Ideas for a team. 23 Glossary and sources.

## How to answer

- Answer the actual question directly first, then cite the sections you used ("section 12") and quote short passages verbatim when they help.
- The guide is one heavy user's practice, written by Claude from Aaron's history: opinionated and in places idiosyncratic. Say when a recommendation is a personal preference rather than a general rule, and adapt it to the user's situation.
- Its facts are dated; check the "Last updated" line near the top of the file. For anything about current Claude Code features, prices, or plan limits, check current official documentation instead of relying on the guide.
- If the guide recommends something this plugin set already provides, say so: the prompt templates are skills such as `/field-guide:research`, `/field-guide:brief`, and `/field-guide:meeting`; the `rm` guard is the field-guide-safety plugin; section 21 is the field-guide-house-rules plugin.
- The latest version is always at https://abergman.com/ai (raw Markdown at https://abergman.com/ai.md).
