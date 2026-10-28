---
name: optimize-skill
description: Shrink a skill's tokens without changing its output, when the user asks to optimize, trim, or slim a skill.
---

# Optimize a skill

Apply the unslop skill. Target: the skill the user names.

1. Baseline: `wc -l -w` on its SKILL.md and linked files. Pick 1 to 3 prompts that should trigger it and 1 that should not. Run each in a subagent and save the outputs outside the skill folder.
2. Cut in place, in this order:
   - Description: one sentence, what and when; keep the user's trigger words.
   - Body: imperative rules only, under 150 lines. No intro, rationale, or repeats.
   - Delete what Claude already knows.
   - Replace explanatory prose with one short input/output example.
   - Move bulky references, schemas, and examples to `references/<name>.md`, linked with a "read when" cue.
   - Move deterministic logic to `scripts/`; SKILL.md gives the command and output shape.
3. Never cut a rule that changes the output, a hard stop, or a confirmation gate.
4. Re-run the prompts. The skill must still trigger on the first set and not on the negative one, with equivalent outputs. If so, cut further. If not, restore the last cut that broke it and stop.
5. Report before/after lines and words per file, the prompts run, differences found, and what moved out.
