import { test } from '@e2e-dev/web';
import { expect } from 'e2e';

// Replies come from the real LLM: check shape and meaning, never exact wording.
const REPLY_TIMEOUT = 120_000;

test('stopping a reply keeps the chat usable', async ({ app, browser, screen }) => {
  await app.open('/');
  const input = screen.getByPlaceholder('Give me categories list.');
  // Unique text so the LLM cache can't finish the reply before Stop is clicked.
  await input.fill(
    `Compare "Tapta Fitted Dress with Collared Neck" and "Eclipse Flared Lace Dress" in detail (${Date.now()})`,
  );
  await input.press('Enter');

  // Stop takes the send arrow's place in the chat input while the reply streams.
  // Not Streamlit's own header "Stop", which shows while any script runs.
  const stop = screen.getByRole('button', /Stop response/);
  await expect(stop).toBeVisible();
  await expect(screen.getByTestId('stChatInputSubmitButton')).toBeHidden();
  await stop.click();
  await expect(screen.getByTestId('stChatMessage').last()).toContainText('(stopped)', {
    timeout: REPLY_TIMEOUT,
  });
  await expect(screen.getByTestId('stStatusWidget')).toBeHidden({ timeout: REPLY_TIMEOUT });

  // The thread is clean: the next question gets a normal reply.
  await input.fill('Do you offer free shipping?');
  await input.press('Enter');
  // welcome, stopped question and its reply, then the follow-up and its answer
  // (the answer mentions shipping; the in-progress bubble only has the Stop button)
  const conversation = [/\S/, /Compare/, /\(stopped\)/, 'Do you offer free shipping?', /shipping/i];
  await expect(screen.getByTestId('stChatMessage')).toContainText(conversation, {
    timeout: REPLY_TIMEOUT,
  });
  await expect(screen.getByTestId('stStatusWidget')).toBeHidden({ timeout: REPLY_TIMEOUT });

  // Saved on the server too: reload the shared link (keeps this thread) and see the same chat.
  await screen.getByRole('button', /Share conversation/).click();
  await browser.reload();
  await expect(screen.getByTestId('stChatMessage')).toContainText(conversation, {
    timeout: 30_000,
  });
});
