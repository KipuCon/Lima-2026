const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 120_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1, // sequential — each act is a story
  use: {
    baseURL: 'http://localhost:3333',
    // Record video of every test — this is the whole point
    video: {
      mode: 'on',
      size: { width: 1920, height: 1080 }
    },
    screenshot: 'on',
    // Slow down actions so the video looks like a human demo
    actionTimeout: 5000,
    viewport: { width: 1920, height: 1080 },
    launchOptions: {
      slowMo: 400, // 400ms between actions — readable on video
    },
  },
  outputDir: './test-results',
  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: './report' }],
  ],
  projects: [
    {
      name: 'demo-recording',
      use: {
        browserName: 'chromium',
      },
    },
  ],
});
