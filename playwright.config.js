import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 20000,
  use: {
    baseURL: 'http://localhost:8080',
    headless: true,
  },
  webServer: {
    command: 'python3 -m http.server 8080 --directory docs/',
    port: 8080,
    reuseExistingServer: false,
    timeout: 10000,
  },
});
