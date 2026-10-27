---
description: Take a GitHub issue end to end: plan, build, test, review, open PR
argument-hint: <issue number>
---
Work GitHub issue #$ARGUMENTS end to end. Stop only at the **GATE** or when a rule below says to ask.

## 1. Plan (no code)
- `gh issue view $ARGUMENTS --comments`, then run `/analyze-ticket` on the issue text.
- Read the code the issue touches and trace the real flow before planning. Mark each claim Known (read in code) or Assumed.
- Use the `grilling` skill to settle open questions with me. Decide routine ones yourself and say so.
- Output the plan, max 1 screen: smallest change that meets the issue's Expected section, files to change, tests to add, how to verify. List anything beyond that as follow-ups; do not build it.
- **GATE:** wait for my approval before writing code.

## 2. Build
- `git switch main && git pull --ff-only`, then branch `<fix|feat>/issue-$ARGUMENTS-<short-slug>`.
- Bug: use the `repro-bug` skill, so the failing test is committed first. Feature: add the test with the change.
- Small commits, each with passing tests. Message: conventional prefix + one sentence, max 20 words, no body.
- Every behavior change gets a test that fails without the change.

## 3. Test
- Run the full test suite with the Test command from CLAUDE.md. All must pass. Report the command and result.
- If the change is user-visible, run the app (server + client) and reproduce the issue's scenario. Use Claude in Chrome if it is connected; otherwise give me the exact manual steps and wait for my result.
- Screenshots: save them outside the repo (e.g. `/tmp`); they are attached in step 5.
- Same failure after 3 fix attempts → stop and ask.

## 4. Review
- Run the `review-checklist` skill on `git diff main...HEAD`. Fix every item until the verdict is "merge", then rerun step 3.
- Check the diff is small: if it touches more files than the plan listed, say why.

## 5. Ship
- Push the branch. Run `/pr $ARGUMENTS` for the body (it must include `Closes #$ARGUMENTS`), then `gh pr create`. Never open a PR with a one-line body.
- Screenshots: `gh` cannot attach images, so with Claude in Chrome open the PR on github.com, edit the description, upload each screenshot, and save. If Chrome is not connected, list the paths and I will attach them.
- Reply with the PR link and anything left unverified.

## Rules
- Smallest change that meets the issue's expectation. No unrelated refactors, no new dependencies.
- Ask me on scope, behavior, or trade-off decisions; decide routine ones yourself.
- Never push to main, force-push, or merge the PR.
