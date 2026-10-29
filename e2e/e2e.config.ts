import type { E2EConfig } from 'e2e';
import { web } from '@e2e-dev/web';
import { openai } from '@ai-sdk/openai';

// Server and client are started by `make e2e`, not here: the client needs the API on :8080.
export default {
  targets: [{ engine: web(), app: { url: process.env.APP_URL ?? 'http://localhost:8501' } }],
  // Chat replies come from the real LLM, so allow slow turns.
  timeout: 300_000,
  agents: {
    // Reads OPENAI_API_KEY, the same key the app uses.
    default: { model: openai('gpt-4o-mini') },
  },
} satisfies E2EConfig;
