import { test } from '@e2e-dev/web';
import { expect } from 'e2e';

// Static copy only: no chat message is sent, so no LLM call.
test('sidebar shows the IVY moda contacts', async ({ app, screen }) => {
  await app.open('/');
  const sidebar = screen.getByTestId('stSidebar');
  // One assertion per string: an array would match one element per item.
  for (const text of ['IVY moda', 'CSKH@ivy.com.vn', '0246 662 3434', 'Monday to Friday']) {
    await expect(sidebar).toContainText(text, { timeout: 30_000 });
  }
});

test('About Us is about IVY moda apparel only', async ({ app, screen }) => {
  await app.open('/about');
  const main = screen.getByTestId('stMain');
  await expect(main).toContainText('IVY moda', { timeout: 30_000 });
  await expect(main).not.toContainText('Lingerie');
  await expect(main).not.toContainText('Accessories');
});
