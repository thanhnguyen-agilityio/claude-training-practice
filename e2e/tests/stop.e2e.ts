import { test } from '@e2e-dev/web';
import { expect } from 'e2e';

// Replies come from the real LLM: check shape and meaning, never exact wording.
const REPLY_TIMEOUT = 120_000;

test('stopping a reply keeps the chat usable', async ({ app, screen }) => {
  await app.open('/');
  const input = screen.getByPlaceholder('Give me categories list.');
  await input.fill(
    'Compare "Tapta Fitted Dress with Collared Neck" and "Eclipse Flared Lace Dress" in detail',
  );
  await input.press('Enter');

  await screen.getByRole('button', 'Stop').click();
  await expect(screen.getByTestId('stChatMessage').last()).toContainText('(stopped)', {
    timeout: REPLY_TIMEOUT,
  });
  await expect(screen.getByTestId('stStatusWidget')).toBeHidden({ timeout: REPLY_TIMEOUT });

  // The thread is clean: the next question gets a normal reply.
  await input.fill('Do you offer free shipping?');
  await input.press('Enter');
  await expect(screen.getByTestId('stChatMessage').last()).toContainText(/\w/, {
    timeout: REPLY_TIMEOUT,
  });
});
