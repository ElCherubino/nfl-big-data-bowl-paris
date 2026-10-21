import {defineConfig} from '@playwright/test';
export default defineConfig({
  testDir:'./tests/browser', timeout:30000, fullyParallel:false, workers:1,
  reporter:'list', use:{baseURL:process.env.RB_BROWSER_URL || 'http://127.0.0.1:4173', headless:true},
  webServer:process.env.RB_BROWSER_URL?undefined:{command:'npm run dev -- --host 127.0.0.1 --port 4173 --strictPort', url:'http://127.0.0.1:4173', reuseExistingServer:!process.env.CI},
});
