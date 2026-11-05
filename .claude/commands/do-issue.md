---
description: Take a GitHub issue end to end: plan, build, test, review, open PR
argument-hint: <issue number> [--auto]
---
Work a GitHub issue end to end. Arguments: `$ARGUMENTS`. `<n>` is the issue number (first word). **Auto mode** is on when the arguments contain `--auto`.

- **Interactive** (default): stop at the **GATE** and when a rule below says to ask.
- **Auto:** no GATE and no questions. Apply the suggested picks, post them on the issue, and keep going. Stop only on a hard stop from `.claude/decisions.md`. Running with `--auto` is my approval to post the decisions comment on the issue (one comment, nothing else outward-facing before the PR).

## 1. Plan (no code)
- `gh issue view <n> --comments`, then run `/analyze-ticket` on the issue text.
- Read the code the issue touches and trace the real flow before planning. Mark each claim Known (read in code) or Assumed.
- Give every open question a suggested pick and confidence (`.claude/decisions.md`).
  - Interactive: use the `grilling` skill, leading each question with its suggested pick so I can confirm or override. Decide routine (high) ones yourself and say so.
  - Auto: take every pick. A hard stop → comment the question on the issue (evidence, options, your suggested pick, ending with `<!-- do-issue:blocked -->`), reply with the link, and stop. Otherwise post the decisions comment (marker `do-issue:decisions`) before step 2.
- Output the plan, max 1 screen: smallest change that meets the issue's Expected section, files to change, tests to add, how to verify, decisions with confidence. List anything beyond that as follow-ups; do not build it.
- **GATE** (interactive only): wait for my approval before writing code. Auto: continue.

## 2. Build
- `git switch main && git pull --ff-only`, then branch `<fix|feat>/issue-<n>-<short-slug>`.
- Bug: use the `repro-bug` skill, so the failing test is committed first. Feature: add the test with the change.
- Small commits, each with passing tests. Message: conventional prefix + one sentence, max 20 words, no body.
- Every behavior change gets a test that fails without the change.

## 3. Test
- Run the full test suite with the Test command from CLAUDE.md. All must pass. Report the command and result.
- If the change is user-visible, add or extend a test in `e2e/tests/` for the changed UI path and run `make e2e`. Only if it can't run: run the app (server + client) and reproduce the scenario with Claude in Chrome if it is connected; otherwise give me the exact manual steps and wait for my result (auto: mark it **unverified** in the PR and continue).
- Screenshots: save them outside the repo (e.g. `/tmp`); they are attached in step 5.
- Same failure after 3 fix attempts → stop and ask (auto: open a draft PR with a `## Failure log` and stop).

## 4. Review
- Start a fresh `Agent` (`model: sonnet`) as the reviewer. Give it only the issue number, the branch name and "Read the issue with `gh issue view <n> --comments`, then run the `review-checklist` skill on `git diff main...HEAD`. Do not edit files. Reply with the findings and a verdict." Do not pass it the plan, decisions, or your reasoning: it checks the code against the ticket, not against our thinking.
- Fix every finding yourself, rerun step 3, then send the reviewer "re-review" (`SendMessage`) until the verdict is "merge". A finding you disagree with: say why in the PR body instead of fixing it.
- Check the diff is small: if it touches more files than the plan listed, say why.

## 5. Ship
- Push the branch. Run `/pr <n>` for the body (it must include `Closes #<n>`; in auto mode also a `## Decisions` section with the table and a link to the decisions comment), then `gh pr create`. Never open a PR with a one-line body.
- Screenshots: `gh` cannot attach images, so with Claude in Chrome open the PR on github.com, edit the description, upload each screenshot, and save. If Chrome is not connected, list the paths and I will attach them.
- Reply with the PR link, anything left unverified, and (auto) every **med** decision I should double-check.

## Rules
- Smallest change that meets the issue's expectation. No unrelated refactors, no new dependencies.
- Interactive: ask me on scope, behavior, or trade-off decisions; decide routine ones yourself. Auto: follow `.claude/decisions.md`.
- Never push to main, force-push, or merge the PR (also in auto mode: the PR review is my gate).
