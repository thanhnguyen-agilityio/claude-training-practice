---
name: auto-issues
description: Take selected GitHub issues end to end with no approval stops (plan, build, test, 3 reviews, PR, merge), when the user runs /auto-issues with issue numbers.
argument-hint: <issue numbers, e.g. 6 20 8>
model: sonnet
disable-model-invocation: true
---
Skill version: 3. Work GitHub issues $ARGUMENTS end to end with no approval stops. Merge only when review 3 is confident. I review the run report afterwards.

Paths below are relative to `.claude/skills/auto-issues/`. `<scratch>` is your scratchpad dir.

## Roles
- **Orchestrator** (you): preflight, queue, start agents, run reviews 2 and 3, merge, write the report. Never read issue code or diffs; keep only agent summaries.
- **Worker:** one fresh `Agent` (`model: sonnet`) per issue. Prompt: issue number, `<scratch>`, session id, issue start time, "Follow `references/worker.md` steps 1–4, then stop and reply." Keep its id; send review findings, "do step 6" and "sync" with `SendMessage`.
- **Reviewers:** a fresh agent each time, given only what its step lists. They read the PR's diff (`gh pr diff <pr>`, or `git diff origin/main...origin/<branch>` before a PR exists), never the local checkout, and open only changed lines plus ~20 lines of context unless a finding needs more.

## Preflight
If any check fails, stop the run: stop anything you started, start no issue, write the report with only a Preflight section (check, pass/fail, error, fix), reply with what I must fix.
1. On `main`, clean tree outside `out/` (`git status --porcelain -- . ':!out'` is empty), `git pull --ff-only` works.
2. `gh auth status` passes; `gh repo view --json viewerPermission` is `WRITE`, `MAINTAIN` or `ADMIN`.
3. All test and lint commands from CLAUDE.md pass on `main`.
4. Labels `auto-merged` and `needs-human-merge` exist; create missing ones with `gh label create`.
5. `.claude/preflight.md` exists (missing → fail: this repo's setup is unverified). Run every check in it.

Record each result for the report. Note the run start (`date -u +%Y-%m-%dT%H:%M:%SZ`) and the session id: `basename "$(ls -t ~/.claude/projects/$(pwd | tr '/.' '--')/*.jsonl | head -1)" .jsonl`.

## Queue
- `gh issue view <n> --json number,title,labels,state` each. Drop closed issues and those with an open PR (`gh pr list --search "<n> in:body" --state open`).
- Order by label: `critical priority` → `high priority` → `medium priority` → `low priority` → none; ties by lowest number. One issue at a time, each from the latest `main`.

## Per issue
Record start and end time (`date -u +%Y-%m-%dT%H:%M:%SZ`). **Budget:** 45 minutes or $5 per issue (`uv run python scripts/ai_usage.py --session <id> --since <start> --format json`; issues run one at a time, so this window covers every agent working on the issue); the worker checks it, and over budget it opens a draft PR with what is done and replies `draft`.
1. **Worker, steps 1–4.** It replies `skipped` (done: it commented on the issue), `draft` (done: draft PR with failure log), or `ready`.
2. **Review 2** (on `ready`): fresh `Agent` (`model: sonnet`) gets only the issue number and branch; it reads the issue and the branch diff and flags: (a) Expected section not met, (b) any line not needed for the ticket, (c) bugs, security, missing tests. Send findings to the worker; it fixes, removes unneeded lines, reruns tests, pushes. If code changed, run review 2 once more. Still blocking → worker opens a draft PR with the findings; move on.
3. **Worker, step 6:** send "do step 6"; it replies with the PR link when the evidence is in.
4. **Sync** (worker): send "sync"; it runs `git fetch origin && git merge origin/main` on the branch and, if anything came in, reruns tests and pushes.
5. **Review 3:** fresh `Agent` (`model: opus`) gets the issue number, PR number, and `references/review-3.md`; it reruns the checks itself and returns the checklist and a verdict.
6. **Decide**, first match wins (add labels with `gh api -X POST repos/{owner}/{repo}/issues/<pr>/labels -f "labels[]=<name>"`):
   - **Human gate** — `critical priority` label, or review 3 item 9 is **yes**, whatever the verdict: comment the checklist (and the reasons if not confident), add `needs-human-merge`, keep open and synced. Result: open – human gate.
   - **Confident**: comment the checklist, add `auto-merged`, `gh pr merge <pr> --squash --delete-branch` (if `gh` fails with a Projects-classic error: `gh api -X PUT repos/{owner}/{repo}/pulls/<pr>/merge -f merge_method=squash`, then `gh api -X DELETE repos/{owner}/{repo}/git/refs/heads/<branch>`), `git switch main && git pull --ff-only`.
   - **Not confident**: comment the checklist, reasons, and what would make it mergeable; keep open, synced, checks passing.

## Run report
After the last issue, read `references/run-report.md` and write the report it describes. Reply with the report path and the summary table.

## Rules
- Smallest change that meets the issue's Expected section. No unrelated refactors, new dependencies, or formatting churn in untouched code.
- Never push to main, force-push, use `--admin`, or bypass branch protection or failing checks.
- Never merge with failing tests, unresolved review 2 findings, any review 3 **no** on items 1–8, or a human-gate issue.
- Never commit or print secrets or `.env`.
