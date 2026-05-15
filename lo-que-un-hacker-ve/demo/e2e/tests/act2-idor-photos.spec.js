const { test, expect } = require('@playwright/test');

test.describe('Acto 2 — IDOR con Fotos (RENIEC)', () => {

  test('Decodifica Base64, consulta foto, y descarga masiva en galeria', async ({ page }) => {
    await page.goto('/?section=foto');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    // --- Type DNI digit by digit, steps appear live ---
    const dniInput = page.locator('#foto-dni-input');
    await dniInput.click();

    for (const char of '44556677') {
      await dniInput.press(char);
      await page.waitForTimeout(180);
    }
    await page.waitForTimeout(2000);

    // Steps 2 and 3 should now be visible showing DNI → Base64 → URL
    await expect(page.locator('#b64-step2')).toBeVisible();
    await expect(page.locator('#b64-from-val')).toContainText('44556677');
    await expect(page.locator('#b64-to-val')).toContainText('NDQ1NTY2Nzc=');
    await expect(page.locator('#b64-step3')).toBeVisible();
    await page.waitForTimeout(2500);

    // Click Obtener Foto
    await page.locator('#section-foto button:has-text("Obtener Foto")').click();
    await page.waitForTimeout(2000);

    // Photo and info should appear
    await expect(page.locator('#foto-result')).toBeVisible();
    await expect(page.locator('#foto-nombre')).toContainText('Miguel Angel Vargas Ramos');
    await page.waitForTimeout(2500);

    // --- Change to a different person — just clear and type new DNI ---
    await dniInput.click();
    await dniInput.fill('');
    for (const char of '44556670') {
      await dniInput.press(char);
      await page.waitForTimeout(120);
    }
    await page.waitForTimeout(1000);
    await page.locator('#section-foto button:has-text("Obtener Foto")').click();
    await page.waitForTimeout(2000);

    await expect(page.locator('#foto-nombre')).toContainText('Maria Elena Gutierrez Flores');
    await page.waitForTimeout(2000);

    // --- Gallery: enumerate all 40 DNIs sequentially ---
    await page.locator('button:has-text("Enumerar DNIs")').click();

    // 40 photos at 250ms each + fetch time
    await page.waitForTimeout(16000);

    const galleryItems = page.locator('.gallery-item');
    await expect(galleryItems.first()).toBeVisible();
    const count = await galleryItems.count();
    expect(count).toBeGreaterThanOrEqual(8);

    // Scroll down slowly to reveal all the faces
    await page.evaluate(() => window.scrollTo({ top: document.body.scrollHeight / 2, behavior: 'smooth' }));
    await page.waitForTimeout(1500);
    await page.evaluate(() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' }));
    await page.waitForTimeout(2000);
    await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
    await page.waitForTimeout(3000);
  });
});
