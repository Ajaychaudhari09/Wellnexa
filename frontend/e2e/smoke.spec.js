import { test, expect } from '@playwright/test';

test('landing page loads', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('WellNexa AI')).toBeVisible();
});

test('notifications can be marked as read individually and in bulk', async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem('wellnexa_token', 'playwright-test-token'));
  const notifications = [
    { id: 'notice-1', title: 'Test reminder one', body: 'First test notification', created_at: new Date().toISOString(), is_read: false, action_url: null },
    { id: 'notice-2', title: 'Test reminder two', body: 'Second test notification', created_at: new Date().toISOString(), is_read: false, action_url: null },
  ];

  await page.route('**/api/v1/notifications**', async route => {
    const request = route.request();
    const pathname = new URL(request.url()).pathname;
    if (request.method() === 'GET' && pathname === '/api/v1/notifications') {
      await route.fulfill({ json: { success: true, data: notifications } });
      return;
    }
    if (request.method() === 'POST' && pathname.endsWith('/mark-all-read')) {
      notifications.forEach(item => { item.is_read = true; });
      await route.fulfill({ json: { success: true, data: { updated_count: notifications.length } } });
      return;
    }
    const match = pathname.match(/\/notifications\/([^/]+)\/read$/);
    if (request.method() === 'POST' && match) {
      const item = notifications.find(row => row.id === match[1]);
      item.is_read = true;
      await route.fulfill({ json: { success: true, data: item } });
      return;
    }
    await route.fulfill({ status: 404, json: { message: 'Unexpected test request' } });
  });

  await page.goto('/notifications');
  const first = page.locator('article').filter({ hasText: 'Test reminder one' });
  await expect(page.getByText('2 unread')).toBeVisible();
  await first.getByRole('button', { name: 'Mark as read' }).click();
  await expect(first.getByText('Read')).toBeVisible();
  await expect(page.getByText('1 unread')).toBeVisible();
  await page.getByRole('button', { name: 'Mark all as read' }).click();
  await expect(page.getByText('0 unread')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Mark all as read' })).toBeDisabled();
});
