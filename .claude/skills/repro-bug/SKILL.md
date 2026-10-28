---
name: repro-bug
description: Reproduce a bug and write a reproduce-ready report with a failing test. Use for bug tickets, stack traces, "can't reproduce".
---
1. Run the project from a clean state; get the failure to happen. Never trust a hypothesis you haven't run.
2. Classify: config, code, or data problem. Name the layer.
3. Write the report:
   - **Steps** (exact, numbered)
   - **Expected** / **Actual**
   - **Env** (versions, config)
   - **Evidence** (trace, log)
4. If possible, add a minimal failing automated test before fixing.
