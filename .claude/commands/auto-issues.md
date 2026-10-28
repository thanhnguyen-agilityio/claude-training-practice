---
description: Fully automated: take selected GitHub issues end to end (plan, build, test, 3 reviews, PR, merge) with no stops
argument-hint: <issue numbers, e.g. 6 20 8>
model: sonnet
---
Work GitHub issues $ARGUMENTS end to end with **no approval stops**. You plan, build, test, review three times, open the PR and merge it yourself when you are confident. I review the run report afterwards.

## Roles (keeps context small: each issue starts clean)
- **Orchestrator** (you, this session, on Sonnet): preflight, queue, start agents, review 2 and 3 agents, merge, run report. Never read the issue's code or diffs yourself; keep only each agent's short summary.
- **Worker:** one fresh `Agent` (`model: sonnet`) per issue. Give it this file's path, the issue number, the scratch dir, and its job: steps 1–4, then stop and reply. After review 2 passes, the orchestrator sends it "do step 6"; it replies again when the evidence is in the PR. Subagents cannot start subagents, so it writes code and runs commands itself. It replies with only: result (ready / skipped / draft), branch, PR link, plan files, tests added, proof log path, unverified items, and one line per decision. Keep its id: review findings go back to it with `SendMessage`, so it keeps its context.
- **Reviewers:** a fresh agent each time, given only what its step lists.

## Preflight
Check the setup before touching any issue. If any check fails, stop the whole run: do not start an issue, write the run report with only a **Preflight** section (each check, pass/fail, the error, how to fix), and reply with what I need to fix.
1. **Repo:** on `main`, working tree clean, `git pull --ff-only` works.
2. **GitHub:** `gh auth status` passes; `gh repo view --json viewerPermission` shows `WRITE`, `MAINTAIN` or `ADMIN` (needed to push and merge).
3. **Env:** `.env` exists and has every key in `.env.example` (compare key names only; never print values). `uv sync` succeeds.
4. **Baseline:** all test suites from CLAUDE.md and `uv run ruff check .` pass on `main`. If `main` is already red, stop: failures would be blamed on the wrong issue.
5. **App runs:** start `make run_server` and `make run_client` in the background. `curl -sf http://localhost:8080/health` succeeds and the client answers on `http://localhost:8501`. Keep them running for check 7.
6. **Labels:** `auto-merged` and `needs-human-merge` exist; create any that is missing (`gh label create <name> --description ...`).
7. **Claude in Chrome:** load the Chrome tools (one `ToolSearch`), `tabs_context_mcp` returns a connected browser, and a new tab opens `http://localhost:8501` and `https://github.com` signed in (needed to upload screenshots to the PR). Then stop the server and client; per-issue step 3 starts them fresh.

Record each check's result; it goes in the run report.

Metrics setup: note the run start time (`date -u +%Y-%m-%dT%H:%M:%SZ`) and this session's id, the newest transcript: `ls -t ~/.claude/projects/$(pwd | tr '/.' '--')/*.jsonl | head -1` (file name without `.jsonl`).

## Queue
- `gh issue view <n> --json number,title,labels,state` for each number. Drop closed issues and issues that already have an open PR (`gh pr list --search "<n> in:body" --state open`).
- Order: critical → high → medium → low → no priority; ties by lowest number.
- Do one issue at a time. Each issue starts from the latest `main`, so it includes the previous merges.

## Per issue
Record the issue's start time (`date -u +%Y-%m-%dT%H:%M:%SZ`) before step 1 and its end time when it is merged, left open, drafted or skipped.

### 1. Plan (no gate)
- `gh issue view <n> --comments`, then run `/analyze-ticket` on the issue text.
- Read the code the issue touches and trace the real flow. Mark each claim Known (read in code) or Assumed.
- Decide open questions yourself, picking the option with the smallest change that meets the issue's Expected section. Record each decision and assumption; they go in the PR body.
- Write the plan: files to change, tests to add, how to verify. Anything beyond the Expected section is a follow-up: list it, do not build it.
- **Skip the issue** (go to the next one) when:
  - the ticket is wrong: it contradicts the code or docs, the behavior is already as expected, or it is a duplicate;
  - the bug cannot be reproduced (step 2);
  - you cannot decide by yourself: a product or scope decision with no safe default, a new dependency, or changes across more than ~5 files.
- When you skip, comment on the issue: which case it is, the evidence (what you read or ran), and the question I need to answer. Do not branch or open a PR.

### 2. Build
- `git switch main && git pull --ff-only`, then branch `<fix|feat>/issue-<n>-<short-slug>`.
- Bug: use the `repro-bug` skill and commit its failing test first, then the fix. Its report goes in the PR body. Cannot reproduce → skip (step 1) and put the report in the comment. Feature: add the test with the change.
- Small commits, each with passing tests. Message: conventional prefix + one sentence, max 20 words, no body.
- Every behavior change gets a test that fails without the change.
- **Fail-on-main proof** (bugs and features): `git worktree add <scratch>/proof origin/main`, copy in only the new or changed test files, run them, save the full output to `<scratch>/proof-<n>.log`, then `git worktree remove <scratch>/proof`. The tests must fail **for the reason in the issue** (an assertion about the behavior), not an import or collection error. If they pass on `main`, the test does not catch the bug: rewrite it.

### 3. Test
- Run all suites with the Test command from CLAUDE.md, plus `uv run ruff check .`. All must pass. Record the commands and results.
- User-visible change: run the app (server + client) and reproduce the issue's scenario in Claude in Chrome. Save screenshots outside the repo (e.g. `/tmp`). If it cannot be verified in the browser, mark it **unverified**.
- Same failure after 3 fix attempts → stop this issue: push the branch, open the PR as **draft** with a `## Failure log` section (the command, the failing test names, and the error with its traceback, trimmed to the relevant lines), do not merge, move on.
- Whenever a test or check fails, keep its output: the failing test name, the assertion or error message, and the traceback. A failure reported without its log does not count.

### 4. Review 1: self review
- Run the `review-checklist` skill on `git diff main...HEAD`. Fix every item, then rerun step 3.

### 5. Review 2: independent review
- The orchestrator starts a fresh `Agent` (`model: sonnet`) that has not seen the plan or reasoning. Give it only the issue text and the branch name; it reads `git diff main...HEAD` itself. Ask it to check: (a) the diff meets the issue's Expected section, (b) it is the **minimum** change — flag any line not needed for the ticket, (c) bugs, security, missing tests.
- Send the findings to the worker (`SendMessage`). It fixes every real finding and removes every unneeded line, then reruns step 3. If you changed code, rerun review 2 once more. Still blocking findings after that → draft PR with the findings, do not merge, move on.

### 6. Ship (worker, after review 2 passes)
- Scope check: the diff touches only files from the plan. If not, either revert the extra files or explain why in the PR body.
- Push the branch. Run `/pr <n>` for the body; it must include `Closes #<n>`, the decisions/assumptions from step 1, review 1 and 2 results, and anything unverified. Then `gh pr create`. Never open a PR with a one-line body.
- Wait for CI: `gh pr checks <pr> --watch`. If no checks are configured, rely on the local test run. Failed checks → read the log (`gh run view <run-id> --log-failed`), fix (max 3 attempts), else leave the PR open with the failing log tail in a PR comment, do not merge, move on.
- Update the PR description with the evidence, under a `## Test evidence` section (`gh api -X PATCH repos/{owner}/{repo}/pulls/<pr> -F body=@<file>`; `gh pr edit` fails on this repo with a Projects-classic error). It must show:
  - each test command you ran on the final commit, with its result line (e.g. `42 passed in 3.1s`) and the ruff result;
  - the new or changed tests, and the fail-on-main proof: the command and the failing output (test name, assertion, traceback) inside a `<details>` block;
  - CI check names and results from `gh pr checks <pr>`;
  - review 1 and review 2 verdicts, with what was fixed;
  - the browser check: steps followed and what you saw, or **unverified** and why.
  Use only results from commands you ran in this session, never remembered ones.
- Attach screenshots in Claude in Chrome by editing the PR description on github.com, under `## Test evidence`; if that fails, list the paths in a PR comment.

### 7. Review 3: merge decision (orchestrator)
- Sync first: `git fetch origin && git merge origin/main`, rerun step 3 if anything came in, push.
- Start a fresh `Agent` (`model: opus`) that has not seen your reasoning. Give it the issue number, the PR number and the proof log path; it reads the issue, `git diff origin/main...HEAD`, the PR description and `gh pr checks <pr>` itself. It answers each item **yes / no** with the evidence:
  1. Every point of the issue's Expected section is covered by a test or a verified browser step (list the mapping).
  2. The fail-on-main proof exists and fails for the issue's reason, not an import or collection error.
  3. Tests and ruff pass on the final commit; CI checks pass (or none are configured, stated).
  4. The diff touches only planned files, and every line is needed for the ticket.
  5. No new dependency, no secret, no `.env` change.
  6. The branch is up to date with `origin/main`.
  7. Nothing is **unverified** for a user-visible change.
  8. No remaining risk to security, data, or existing user flows.
  Any **no** → **not confident**. All **yes** → **confident**.
- **Human gate:** the issue has the `critical priority` label, or the change touches security (SQL, auth, secrets, user input reaching a query or shell) → do not merge, even if confident. Comment the checklist on the PR, add the `needs-human-merge` label, keep the PR open and synced. Result: **open – human gate**.
- **Confident** (and no human gate) → comment the checklist on the PR, add the `auto-merged` label, then `gh pr merge <pr> --squash --delete-branch`, then `git switch main && git pull --ff-only`.
- Add labels with `gh api -X POST repos/{owner}/{repo}/issues/<pr>/labels -f "labels[]=<name>"` (`gh pr edit` fails on this repo).
- **Not confident** → do not merge. Comment on the PR with the checklist, the reasons and what would make it mergeable. Keep the PR open, with the branch synced to the latest `main` and checks passing. Move on.

## Run report
After the last issue, write `docs/out/run-reports/<YYYY-MM-DD>-run-<k>.md` (today's date; `k` = next free number for today, starting at 1). Write it on `main` locally; do not commit it. It contains:
- Run info: date, issues requested, queue order, preflight results.
- Summary table: issue, title, priority, result (**merged** / **open – human gate** / **open – not confident** / **draft – failing** / **skipped**), PR link, merge commit.
- Per issue: what changed and why, decisions and assumptions, tests run with results, review 1/2/3 verdicts, unverified items, follow-ups. For skipped and open issues: the reason and a link to the comment you left.
- Needs my attention: every skipped or open issue with the question to answer, and every `needs-human-merge` PR.
- **Escapes:** earlier `auto-merged` PRs (`gh pr list --state merged --label auto-merged`) that were later reverted (a `Revert` commit naming the PR) or whose issue was reopened. Each one is a correctness failure of this command: name the PR and what was missed.
- **Metrics** table, one row per issue plus a run total row:
  - **Time:** start, end, wall minutes.
  - **AI:** tokens per model and estimated cost, from `uv run python scripts/ai_usage.py --session <id> --since <start> --until <end> --format md` (the total row uses the run start and end). The cost is an API-price estimate.
  - **PR:** from `gh pr view <pr> --json commits,changedFiles,additions,deletions,comments,reviews,body`: commits, files changed, lines +/-, comments (PR comments + review comments), screenshot yes/no (the body has an image, `![` or `user-attachments`).
  - **Quality:** tests added, fix rounds after review 1 / 2, review 3 verdict.
  Skipped issues get time and AI only.

Reply with the report path and the summary table.

## Rules
- Smallest change that meets the issue's Expected section. No unrelated refactors, no new dependencies, no formatting churn in untouched code.
- Never push to main, force-push, use `--admin` or bypass branch protection or failing checks.
- Never merge with failing tests, unresolved review 2 findings, a review 3 checklist with any **no**, or a human-gate issue.
- Never commit or print secrets / `.env`.
