# Architecture decision records

One short file per decision that outlives its ticket. Routine picks stay in the issue's work log (`.claude/decisions.md`).

## When to write one
- It sets or changes a convention other code should follow.
- It moves where something lives (e.g. where validation runs, which layer owns a check).
- It is a deliberate trade-off someone may later want to undo, and the reason isn't obvious from the code.

Not for: bug fixes, wording, picks that only matter inside one ticket.

## How
- File: `docs/adr/NNNN-<slug>.md`, next free number, added in the same PR as the change.
- Never edit an accepted ADR's decision; write a new one that supersedes it and set the old one's status to `Superseded by NNNN`.

## Template
```markdown
# NNNN. <Decision in a few words>

- Status: Accepted | Superseded by NNNN
- Date: YYYY-MM-DD
- Issue: #<n> · PR: #<pr>

## Context
What forced a decision; constraints; options considered (one line each).

## Decision
What we chose, in one or two sentences.

## Consequences
What gets easier, what gets harder, what would make us revisit it.
```
