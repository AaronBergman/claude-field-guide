---
name: audit
description: Run a read-only adversarial audit of a codebase, dataset, or document set - finder agents look for real problems along chosen dimensions, independent refuters try to knock down each finding, and only survivors are reported with a fix plan. Use for code reviews, security or data-quality audits, and "find everything wrong with X".
argument-hint: "[what to audit] [dimensions] [optional: max agents]"
---

# Adversarial audit

Target, dimensions, budget: $ARGUMENTS

Read-only: don't change any file or system during the audit.

## 1. Plan

- **Dimensions.** Use the user's list if given. Otherwise propose a few. For an app: data loss, security, error handling, concurrency, the main user flows. For a dataset: completeness, duplicates, bad joins, units, provenance. For documents: factual claims, quotes, internal consistency.
- **Size.** One finder per dimension. Start at most about five agents at once, since many agents cold-starting together hit rate limits. Respect any agent cap or budget the user gave.

## 2. Find

Launch one finder subagent per dimension, in parallel, each with these rules:

- Read the actual files. Never speculate about code or data you haven't read.
- Every finding cites a file and line (or a source and location) and quotes the offending text.
- Every finding has a concrete failure scenario: a specific action leads to a specific wrong result.
- If a subsystem is fine, say so. Do not manufacture findings.
- Return a list: title, location, quote, scenario, severity guess.

## 3. Refute

For each finding, launch the `field-guide:refuter` agent with the claim and its evidence. It re-reads the sources and tries to show the finding is wrong, defaulting to "not real" when uncertain. For the most important findings, add a second, independent judge with a different question: "could a real user, or real data, actually hit this?" Keep a finding only if it survives.

If the Workflow tool is available and the user asked for a workflow, these phases can run as a workflow script instead (pin the agents to a strong model explicitly). If subagents aren't available at all, do the refutation yourself in a separate pass, one finding at a time.

## 4. Report

- Surviving findings, most severe first: what, where (file:line), the quote, the failure scenario, a proposed fix.
- Counts: raw findings, survived, refuted, with a one-line reason for each refuted one so the user can disagree.
- What the audit did not cover.
- A prioritized fix plan. Don't apply fixes unless asked.
