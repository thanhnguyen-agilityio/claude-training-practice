import { test } from '@e2e-dev/web';
import { expect, type Screen } from 'e2e';

// Replies come from the real LLM: check shape and meaning, never exact wording.
const REPLY_TIMEOUT = 120_000;

async function waitForReplyDone(screen: Screen) {
  await expect(screen.getByTestId('stStatusWidget')).toBeHidden({ timeout: REPLY_TIMEOUT });
}

test('an invalid ticket email is not saved and the bot asks again', async ({ app, agent, screen }) => {
  await app.open('/');
  const input = screen.getByPlaceholder('Give me categories list.');
  await input.fill(
    'Create a support ticket: name Lan, email lan@@gmail, phone 12ab, ' +
      'subject torn dress, description my dress arrived torn',
  );
  await input.press('Enter');
  // welcome, the request, then a reply with text in it (or the approval card)
  await expect(screen.getByTestId('stChatMessage')).toContainText([/\S/, /lan@@gmail/, /\w/], {
    timeout: REPLY_TIMEOUT,
  });
  await waitForReplyDone(screen);

  // The model may ask again right away, or show the approval card and let the tool reject it.
  const yes = screen.getByRole('button', /Yes$/);
  if (await yes.isVisible()) {
    await yes.click();
    await expect(yes).toBeHidden({ timeout: REPLY_TIMEOUT });
    await expect(screen.getByTestId('stChatMessage').last()).toContainText(/email|phone/i, {
      timeout: REPLY_TIMEOUT,
    });
    await waitForReplyDone(screen);
  }

  await agent.assert(
    'the last assistant message says the email or phone is invalid and asks the user to give it again, ' +
      'and it does not say a support ticket was created',
  );
});
