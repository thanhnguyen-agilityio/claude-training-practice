# Review 3: merge checklist

Read the issue, `git diff origin/main...HEAD`, the PR description, the proof log, and `gh pr checks <pr>`. Answer each item **yes / no** with evidence:
1. Every point of the issue's Expected section is covered by a test or a verified browser step (list the mapping).
2. The fail-on-main proof exists and fails for the issue's reason, not an import or collection error.
3. Tests and ruff pass on the final commit; CI checks pass (or none are configured, stated).
4. The diff touches only planned files, and every line is needed for the ticket.
5. No new dependency, no secret, no `.env` change.
6. The branch is up to date with `origin/main`.
7. Nothing is **unverified** for a user-visible change.
8. No remaining risk to security, data, or existing user flows.

Any **no** → verdict **not confident**, with reasons and what would make it mergeable. All **yes** → **confident**.
