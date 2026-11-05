---
description: Draft PR description from current branch diff
---
No ticket in $ARGUMENTS or the branch name → stop and ask for one (or offer to create it with `gh issue create`): every PR links an issue.

Read the log and diff of this branch against the default branch. Write a PR description that stands alone:

- **What** changed
- **Why**, starting with `Closes #<n>` (or `Refs #<n>` for partial work) for ticket: $ARGUMENTS
- **How tested** (commands run + results)
- **Screenshots** (if UI; say if needed)
- **Risks / follow-ups**

Describe the branch's final state (title and body), not its first commit. Test commands and results must be ones you ran, not remembered. Keep it short. Do not open the PR.
