import { defineConfig, devices } from '@playwright/test'

const PORT = 5173
const API_PORT = 5001

export default defineConfig({
  testDir: 'e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? 'github' : 'list',
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    {
      command: `cd ../backend && python app.py`,
      url: `http://127.0.0.1:${API_PORT}/api/health`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        ...process.env,
        FLASK_ENV: 'testing',
        ADMIN_API_KEY: 'test-admin-key',
        SECRET_KEY: 'ci-secret-key-for-e2e-tests-only',
      },
    },
    {
      command: 'npm run dev -- --host 127.0.0.1',
      url: `http://127.0.0.1:${PORT}`,
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
  ],
})
