# Claude Action: "Credit balance is too low"

2026-11-04 · Issue #71

## Problem

Every `claude-code-action` run (both `@claude` and PR review) fails on turn 1 with `is_error:true`, at $0 cost. The branch 404s later in the log are side effects.

## Cause

The API rejects any request carrying `anthropic-beta: claude-code-20250219` with:

> 400 "Your credit balance is too low to access the Anthropic API"

Claude Code sends this header on every request. The same keys work without it. So **Anthropic blocks Claude Code usage for the org** even though the org has credit. The repo, the workflow, the action version, and the GitHub secret are all fine.

## Proof

| Test | Result |
|---|---|
| `curl /v1/messages` | ✅ 200 |
| Same, plus `anthropic-beta: claude-code-20250219` | ❌ credit balance too low |
| Local Claude Code, API key only | ❌ same as CI |
| Old key (ran Claude Code earlier today, $0.15) | Same ✅/❌ pattern |
| New Default-workspace key | Same ✅/❌ pattern |

Org balance: $99.86. Spend limit: $500, 0% used.

## Ruled out

Balance, spend limit, the keys, model access (Opus and Sonnet), action version, and key scope.

## Next

1. **Anthropic support:** send the finding above with request IDs `req_011Cgi3vExM2mSniXkFK1jGT` and `req_011Cgi4tKNKgu35fCyR7GC4j`.
2. **Workaround:** authenticate with `claude_code_oauth_token` (Claude Pro/Max plan) instead of the API key. This is on branch `ci/claude-oauth-token`.
3. Once it works, remove `show_full_output: true` (the repo is public).
