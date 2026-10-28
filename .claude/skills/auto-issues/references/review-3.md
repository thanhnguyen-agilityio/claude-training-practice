# Review 3: merge checklist

Read the issue and `gh pr diff <pr>` (changed lines plus ~20 lines of context), the PR description, and `gh pr checks <pr>`. Do not trust the PR's evidence: in a temp worktree of the PR head (`git worktree add <scratch>/r3 origin/<branch>`), run the test and lint commands from CLAUDE.md (quiet, `| tail -n 30`), and the new or changed tests against `origin/main` (worktree `<scratch>/r3-main`). Remove both worktrees after.

Answer each item **yes / no** with evidence:
1. Every point of the issue's Expected section is covered by a test or a verified browser step (list the mapping).
2. Your run of the new tests on `origin/main` fails for the issue's reason, not an import or collection error.
3. Your run of tests and lint on the PR head passes; CI checks pass (or none are configured, stated).
4. The diff touches only planned files, and every line is needed for the ticket.
5. No new dependency, no secret, no `.env` change.
6. The branch is up to date with `origin/main`.
7. Nothing is **unverified** for a user-visible change (the diff touches `client/` or changes what a user sees).
8. No remaining risk to data or existing user flows.
9. The change touches the security surface: SQL, auth, secrets, or user input reaching a query or shell. (yes → human gate; not a merge blocker by itself)

Any **no** on 1–8 → verdict **not confident**, with reasons and what would make it mergeable. All **yes** on 1–8 → **confident**. Always report item 9.
