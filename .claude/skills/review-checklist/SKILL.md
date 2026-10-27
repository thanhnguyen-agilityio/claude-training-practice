---
name: review-checklist
description: Review a diff or PR in priority order. Use when asked to review code, a PR, or a branch.
---
Review in this order; stop padding when a level is clean.

1. **Correctness** — wrong output, nulls, edge cases, off-by-one.
2. **Tests** — does the change have one that fails without it?
3. **Readability** — naming, size, dead code.
4. **Security basics** — input handling, secrets, permissions.
5. **Scope** — unrelated changes, new deps.

Comments must be actionable: "returns None when X; guard like Y" — not verdicts. Cite `file:line`. Finish with: merge / fix first / discuss.
