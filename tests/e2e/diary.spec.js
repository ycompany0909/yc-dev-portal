import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  await page.goto('/diary.html');
  // JS が初期化されるまで月タイトルを待つ
  await page.waitForSelector('#month-title:not(:empty)');
});

// 1: ページタイトル
test('ページタイトルに YC開発年代記 が含まれる', async ({ page }) => {
  await expect(page).toHaveTitle(/YC開発年代記/);
});

// 2: カレンダータブがデフォルトでアクティブ
test('カレンダータブがデフォルトでアクティブ', async ({ page }) => {
  await expect(page.locator('#tab-calendar')).toHaveClass(/active/);
});

// 3: 月タイトルが 2026年 6月 を表示
test('月タイトルが 2026年 6月 を表示', async ({ page }) => {
  await expect(page.locator('#month-title')).toHaveText('2026年 6月');
});

// 4: カレンダーグリッドに 35 本以上のセル
test('カレンダーグリッドに 35 本以上のセル', async ({ page }) => {
  const cells = page.locator('.cal-cell');
  await expect(cells).toHaveCount(await cells.count());
  expect(await cells.count()).toBeGreaterThanOrEqual(35);
});

// 5: 統計バーに stat-card が 3 本
test('統計バーに stat-card が 3 本', async ({ page }) => {
  await expect(page.locator('.stat-card')).toHaveCount(3);
});

// 6: 記録がある日付セル（has-entry）が存在する
test('記録がある日付セルが存在する', async ({ page }) => {
  const entries = page.locator('.cal-cell.has-entry');
  expect(await entries.count()).toBeGreaterThan(0);
});

// 7: 記録ある日をクリック → エントリーパネルが表示される
test('記録ある日をクリックするとエントリーパネルが表示される', async ({ page }) => {
  await page.locator('.cal-cell.has-entry').first().click();
  await expect(page.locator('#entry-panel')).toHaveClass(/visible/);
});

// 8: 詳細パネルにリポジトリタグが表示される
test('詳細パネルにリポジトリタグが表示される', async ({ page }) => {
  await page.locator('.cal-cell.has-entry').first().click();
  await expect(page.locator('.repo-tag').first()).toBeVisible();
  const text = await page.locator('.repo-tag').first().innerText();
  expect(text.length).toBeGreaterThan(0);
});

// 9: 全貌・評価タブに切替できる
test('全貌・評価タブに切替できる', async ({ page }) => {
  await page.click('button.tab-btn:has-text("全貌")');
  await expect(page.locator('#tab-overview')).toHaveClass(/active/);
});

// 10: 戦闘力スコアが 61
test('戦闘力スコアが 61 を表示', async ({ page }) => {
  await page.click('button.tab-btn:has-text("全貌")');
  await expect(page.locator('.combat-num')).toHaveText('61');
});

// 11: 悲観的サブタイトルに「伸び代」が含まれる
test('戦闘力サブタイトルに「伸び代」が含まれる', async ({ page }) => {
  await page.click('button.tab-btn:has-text("全貌")');
  const sub = await page.locator('.combat-sub').innerText();
  expect(sub).toContain('伸び代');
});

// 12: ゲージバーが 6 本以上存在する
test('技術深度ゲージバーが 6 本以上存在する', async ({ page }) => {
  await page.click('button.tab-btn:has-text("全貌")');
  const fills = page.locator('.gauge-fill');
  expect(await fills.count()).toBeGreaterThanOrEqual(6);
});

// 13: 計画タブに切替できる
test('計画タブに切替できる', async ({ page }) => {
  await page.click('button.tab-btn:has-text("計画")');
  await expect(page.locator('#tab-plan')).toHaveClass(/active/);
});

// 14: 計画タブに plan-card が 1 本以上読み込まれる
test('計画タブに plan-card が 1 本以上読み込まれる', async ({ page }) => {
  await page.click('button.tab-btn:has-text("計画")');
  await page.waitForSelector('.plan-card', { timeout: 10000 });
  const cards = page.locator('.plan-card');
  expect(await cards.count()).toBeGreaterThan(0);
});

// 15: 診断タブに切替できる
test('診断タブに切替できる', async ({ page }) => {
  await page.click('button.tab-btn:has-text("診断")');
  await expect(page.locator('#tab-assessment')).toHaveClass(/active/);
});

// 16: 診断タブの markdown コンテンツが空でない
test('診断タブの markdown コンテンツが空でない', async ({ page }) => {
  await page.click('button.tab-btn:has-text("診断")');
  // marked.js が CDN からロードされるため少し待つ
  await page.waitForFunction(
    () => {
      const el = document.getElementById('assessment-content');
      return el && el.textContent && el.textContent.trim().length > 50;
    },
    { timeout: 15000 }
  );
  const content = await page.locator('#assessment-content').innerText();
  expect(content.length).toBeGreaterThan(50);
});

// 17: メモタブに切替できる
test('メモタブに切替できる', async ({ page }) => {
  await page.click('button.tab-btn:has-text("メモ")');
  await expect(page.locator('#tab-memo')).toHaveClass(/active/);
});

// 18: メモタブに textarea が存在し入力できる
test('メモタブに textarea が存在し入力できる', async ({ page }) => {
  await page.click('button.tab-btn:has-text("メモ")');
  const ta = page.locator('#quick-memo-text');
  await expect(ta).toBeVisible();
  await ta.fill('テスト入力');
  await expect(ta).toHaveValue('テスト入力');
});

// 19: 前月ボタンをクリックすると 5 月に切り替わる
test('前月ボタンをクリックすると 5 月に切り替わる', async ({ page }) => {
  await page.click('.month-nav button:first-child');
  await expect(page.locator('#month-title')).toHaveText('2026年 5月');
});

// 20: 全貌タブに Dragon Harness Tier 0 が表示される
test('全貌タブに Dragon Harness Tier 0 が表示される', async ({ page }) => {
  await page.click('button.tab-btn:has-text("全貌")');
  await expect(page.locator('.tier-badge.tier-0')).toBeVisible();
  const text = await page.locator('.tier-badge.tier-0').innerText();
  expect(text).toContain('Tier 0');
});
