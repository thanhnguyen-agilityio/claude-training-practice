# Run report

Write `out/run-reports/<YYYY-MM-DD>-run-<k>.md` (today; `k` = next free number for today, from 1) in the main checkout, whatever branch it is on; do not commit it. Sections:
- **Run info:** date, skill version, issues requested, queue order, preflight results, and on-demand check results from `<scratch>/preflight-checks.md` (or "not needed").
- **Summary:** issue, title, priority, result (merged / open – human gate / open – not confident / draft – failing / draft – over budget / draft – review 2 blocking / skipped), PR link, merge commit.
- **Per issue:** what changed and why, decisions and assumptions, tests with results, review 1/2/3 verdicts, unverified items, follow-ups. Skipped or open: the reason and a link to your comment.
- **Needs my attention:** every skipped or open issue with its question, and every `needs-human-merge` PR.
- **Escapes:** earlier `auto-merged` PRs (`gh pr list --state merged --label auto-merged`) later reverted (a `Revert` commit naming the PR) or whose issue was reopened: the PR and what was missed.
- **Metrics:** one row per issue plus a run total. Skipped issues get Time and AI only.
  - Time: start, end, wall minutes.
  - AI: tokens per model and estimated cost from `uv run python scripts/ai_usage.py --session <id> --since <start> --until <end> --format md` (total row: run start to end). Cost is an API-price estimate.
  - PR: from `gh pr view <pr> --json commits,changedFiles,additions,deletions,comments,reviews,body`: commits, files changed, lines +/-, comments (PR + review), screenshot yes/no (body has `![` or `user-attachments`).
  - Quality: verification level, tests added, fix rounds after review 1 / 2, review 3 verdict.
- **Improvements for next run:** the workers' lessons plus where the run got stuck, retried, guessed, or went over budget; for each, the rule that would have prevented it. Proposed only: I add confirmed ones to `in/auto-issues-lessons.md`.
- **Human review:** an empty table (issue, merge correct? yes/no, what was missed) for me to fill in.
