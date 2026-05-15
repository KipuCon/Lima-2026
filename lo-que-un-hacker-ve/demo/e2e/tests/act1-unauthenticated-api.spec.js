const { test, expect } = require('@playwright/test');

test.describe('Acto 1 — API sin Autenticacion (ONPE/MEF)', () => {

  test('Consulta un ciudadano por DNI y luego enumera varios', async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1500);

    // --- Single lookup ---
    const dniInput = page.locator('#dni-input');
    await dniInput.click();
    await dniInput.fill('');

    // Type the DNI slowly — digit by digit for dramatic effect
    const dni = '44556677';
    for (const char of dni) {
      await dniInput.press(char);
      await page.waitForTimeout(150);
    }
    await page.waitForTimeout(800);

    // Click Consultar
    await page.locator('#section-consulta button:has-text("VALIDAR")').click();
    await page.waitForTimeout(1500);

    // Verify result appeared
    await expect(page.locator('#ciudadano-result')).toBeVisible();
    await expect(page.locator('.result-grid')).toContainText('Miguel Angel');
    await expect(page.locator('.result-grid')).toContainText('Vargas Ramos');
    await expect(page.locator('.result-grid')).toContainText('44556677');
    await page.waitForTimeout(2000);

    // --- Now change the DNI — show how easy it is ---
    await dniInput.click();
    await dniInput.fill('');
    const dni2 = '44556670';
    for (const char of dni2) {
      await dniInput.press(char);
      await page.waitForTimeout(150);
    }
    await page.waitForTimeout(500);
    await page.locator('#section-consulta button:has-text("VALIDAR")').click();
    await page.waitForTimeout(1500);

    // Different person appeared
    await expect(page.locator('.result-grid')).toContainText('Maria Elena');
    await expect(page.locator('.result-grid')).toContainText('Gutierrez Flores');
    await page.waitForTimeout(1500);

    // --- Enumerate: rapidly query multiple DNIs ---
    const dnis = ['44556671', '44556672', '44556673', '44556674', '44556675'];
    for (const d of dnis) {
      await dniInput.click();
      await dniInput.fill(d);
      await page.locator('#section-consulta button:has-text("VALIDAR")').click();
      await page.waitForTimeout(800);
    }

    // Pause on the last result
    await page.waitForTimeout(1500);

    // --- The reveal: what happened behind the form? ---
    const revealBtn = page.locator('#net-reveal-btn');
    if (await revealBtn.isVisible()) {
      await revealBtn.click();
      await page.waitForTimeout(3000); // Let audience read the inspector

      // Curl equivalent appears after 2s automatically
      await page.waitForTimeout(2500);
    }
  });
});
