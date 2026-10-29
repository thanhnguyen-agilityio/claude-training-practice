import { test } from '@e2e-dev/web';
import { expect, type Screen } from 'e2e';

// Replies come from the real LLM: check shape and meaning, never exact wording.
const REPLY_TIMEOUT = 120_000;

// Streamlit shows its "Running..." status widget until the script run (and the streamed reply) ends.
async function waitForReplyDone(screen: Screen) {
  await expect(screen.getByTestId('stStatusWidget')).toBeHidden({ timeout: REPLY_TIMEOUT });
}

test('welcome message shows on a new chat', async ({ app, screen }) => {
  await app.open('/');
  // The welcome text is picked at random, so only check that it is the one message.
  await expect(screen.getByTestId('stChatMessage')).toHaveCount(1, { timeout: 30_000 });
});

test('a quick-start click gets a reply', async ({ app, agent, screen }) => {
  await app.open('/');
  await screen.getByRole('button', 'Do you offer free shipping?').click();
  // welcome, the question, then a reply with text in it
  await expect(screen.getByTestId('stChatMessage')).toContainText(
    [/\S/, 'Do you offer free shipping?', /\w/],
    { timeout: REPLY_TIMEOUT },
  );
  await waitForReplyDone(screen);
  await agent.assert('the last assistant message answers the question about free shipping');
});

test('rejecting a support ticket does not create it', async ({ app, agent, screen }) => {
  await app.open('/');
  // Give every field the tool needs in one message, so the agent goes straight to approval.
  const input = screen.getByPlaceholder('Give me categories list.');
  await input.fill(
    'Create a support ticket. Email: e2e@example.test. Subject: Damaged item. Description: My order arrived broken.',
  );
  await input.press('Enter');

  await expect(screen.getByRole('button', /Yes$/)).toBeVisible({ timeout: REPLY_TIMEOUT });
  await expect(screen.getByRole('button', /No$/)).toBeVisible();

  await screen.getByRole('button', /No$/).click();
  await expect(screen.getByRole('button', /Yes$/)).toBeHidden({ timeout: REPLY_TIMEOUT });
  await waitForReplyDone(screen);
  await agent.assert('the last assistant message says the support ticket was not created');
});
