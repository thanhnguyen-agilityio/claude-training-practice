# Worker: one issue

You cannot start subagents: write code and run commands yourself. Reply only with: result (ready / skipped / draft), branch, PR or comment link, plan files, tests added, test commands with result lines, proof log path, unverified items, one line per decision. Follow the Rules in `../SKILL.md`.

## 1. Plan
- `gh issue view <n> --comments`, then run `/analyze-ticket` on it.
- Read the code the issue touches and trace the real flow. Mark each claim Known (read in code) or Assumed.
- Decide open questions yourself: the smallest change that meets the Expected section. Record decisions and assumptions for the PR body.
- Plan: files to change, tests to add, how to verify. List anything beyond Expected as a follow-up; do not build it.
- **Skip** when the ticket is wrong (contradicts code or docs, already behaves as expected, duplicate), the bug cannot be reproduced, or it needs a decision you cannot make (product or scope with no safe default, a new dependency, more than ~5 files). Comment on the issue: which case, the evidence, the question for me. No branch, no PR. Reply `skipped`.

## 2. Build
- `git switch main && git pull --ff-only`; branch `<fix|feat>/issue-<n>-<short-slug>`.
- Bug: use the `repro-bug` skill; commit its failing test first, then the fix; its report goes in the PR body. Cannot reproduce → skip with the report in the comment. Feature: add the test with the change.
- Small commits, each with passing tests. Message: conventional prefix + one sentence, max 20 words, no body.
- Every behavior change gets a test that fails without it.
- **Fail-on-main proof:** `git worktree add <scratch>/proof origin/main`, copy in only the new or changed test files, run them, save the full output to `<scratch>/proof-<n>.log`, `git worktree remove <scratch>/proof`. They must fail on an assertion about the issue's behavior, not an import or collection error. If they pass, rewrite the test.

## 3. Test
- All suites from CLAUDE.md plus `uv run ruff check .` must pass. Record commands and result lines.
- User-visible change: run the app and reproduce the scenario in the browser named in `.claude/preflight.md` Notes, save screenshots outside the repo, then stop the app. Cannot verify → mark **unverified**. Not user-visible → no browser check.
- Keep every failure's output: test name, assertion or error, traceback. A failure without its log does not count.
- Same failure after 3 fix attempts → push, open a **draft** PR with a `## Failure log` section (command, failing tests, trimmed traceback). Reply `draft`.

## 4. Review 1
- Run the `review-checklist` skill on `git diff main...HEAD`. Fix every item, rerun step 3. Reply `ready`.

## 6. Ship (only when told "do step 6")
- Scope: the diff touches only planned files, or the PR body explains why.
- Push. Run `/pr <n>` for the body: `Closes #<n>`, decisions and assumptions, review 1 and 2 results, unverified items. `gh pr create`. Never a one-line body.
- CI: `gh pr checks <pr> --watch`; none configured → rely on local tests. Failed → `gh run view <run-id> --log-failed`, fix (max 3 attempts), else comment the failing log tail on the PR and reply `draft`.
- Add `## Test evidence` to the PR body with `gh api -X PATCH repos/{owner}/{repo}/pulls/<pr> -F body=@<file>`. Only results from commands you ran:
  - each test command on the final commit with its result line (e.g. `42 passed in 3.1s`), and the ruff result;
  - new or changed tests, and the fail-on-main proof (command and failing output) in a `<details>` block;
  - CI check names and results;
  - review 1 and 2 verdicts and what was fixed;
  - browser check: steps and what you saw, or **unverified** and why.
- Upload screenshots under `## Test evidence` by editing the PR on github.com in that browser; if that fails, list their paths in a PR comment.
