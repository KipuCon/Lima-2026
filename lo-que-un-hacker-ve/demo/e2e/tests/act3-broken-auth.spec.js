const { test, expect } = require('@playwright/test');

test.describe('Acto 3 — Broken Auth "lalalala" (MercadoPago)', () => {

  test('Autentica con "lalalala", ve transacciones, prueba otros secrets', async ({ page }) => {
    await page.goto('/?section=pagafacil');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    // --- First attempt: "lalalala" ---
    const clientIdInput = page.locator('#client-id-input');
    const secretInput = page.locator('#secret-input');

    await clientIdInput.click();
    for (const char of '8872') {
      await clientIdInput.press(char);
      await page.waitForTimeout(150);
    }
    await page.waitForTimeout(500);

    await secretInput.click();
    // Type "lalalala" slowly for dramatic effect
    for (const char of 'lalalala') {
      await secretInput.press(char);
      await page.waitForTimeout(200);
    }
    await page.waitForTimeout(1000);

    // Click Obtener Token
    await page.locator('button:has-text("Obtener Token")').click();
    await page.waitForTimeout(2000);

    // Token should appear
    await expect(page.locator('#token-display')).toBeVisible();
    await expect(page.locator('#token-value')).toContainText('eyJ');
    await expect(page.locator('#token-comercio')).toContainText('ElectroMax Peru SAC');
    await page.waitForTimeout(2500);

    // Transactions should have loaded automatically
    await expect(page.locator('#txn-panel')).toBeVisible();
    await expect(page.locator('#txn-count')).toContainText('6 transacciones');
    await page.waitForTimeout(2000);

    // --- Expand a transaction to show sensitive data ---
    const expandButtons = page.locator('button:has-text("Ver datos")');
    await expandButtons.first().click();
    await page.waitForTimeout(2000);

    // Should show DNI, email, phone — the sensitive stuff
    await expect(page.locator('.txn-details.visible')).toBeVisible();
    await page.waitForTimeout(2000);

    // Expand another one
    await expandButtons.nth(1).click();
    await page.waitForTimeout(1500);
    await expandButtons.nth(2).click();
    await page.waitForTimeout(2500);

    // --- Now try other secrets to prove ANY string works ---
    // Scroll back up to the auth form
    await page.locator('#client-id-input').scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);

    // Try "abc123"
    await secretInput.click();
    await secretInput.fill('');
    for (const char of 'abc123') {
      await secretInput.press(char);
      await page.waitForTimeout(150);
    }
    await page.waitForTimeout(500);
    await page.locator('button:has-text("Obtener Token")').click();
    await page.waitForTimeout(1500);

    // Still works
    await expect(page.locator('#token-display')).toBeVisible();
    await page.waitForTimeout(1500);

    // Try just "x"
    await secretInput.click();
    await secretInput.fill('');
    await secretInput.press('x');
    await page.waitForTimeout(500);
    await page.locator('button:has-text("Obtener Token")').click();
    await page.waitForTimeout(1500);
    await expect(page.locator('#token-display')).toBeVisible();
    await page.waitForTimeout(1500);

    // Try "password123" — still works
    await secretInput.click();
    await secretInput.fill('');
    for (const char of 'password123') {
      await secretInput.press(char);
      await page.waitForTimeout(100);
    }
    await page.waitForTimeout(500);
    await page.locator('button:has-text("Obtener Token")').click();
    await page.waitForTimeout(2000);
    await expect(page.locator('#token-display')).toBeVisible();

    await page.waitForTimeout(1500);

    // --- Now enumerate OTHER merchants — sequential client IDs ---
    // Shows that client_ids are public and sequential
    const otherMerchants = [
      { id: '8870', label: 'Restaurante' },
      { id: '8871', label: 'Clinica' },
      { id: '8873', label: 'Farmacia' },
      { id: '8874', label: 'Viajes' },
      { id: '8875', label: 'Supermercado' },
    ];

    await clientIdInput.scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);

    for (const merchant of otherMerchants) {
      await clientIdInput.fill('');
      for (const char of merchant.id) {
        await clientIdInput.press(char);
        await page.waitForTimeout(100);
      }
      await secretInput.fill('lalalala');
      await page.waitForTimeout(300);
      await page.locator('button:has-text("Obtener Token")').click();
      await page.waitForTimeout(1500);

      // Expand first transaction to show sensitive data
      const expandBtns = page.locator('button:has-text("Ver datos")');
      if (await expandBtns.count() > 0) {
        await expandBtns.first().click();
        await page.waitForTimeout(800);
      }
    }

    // Scroll down to show the sensitive data table
    await page.evaluate(() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }));

    // Final hold
    await page.waitForTimeout(4000);
  });
});
