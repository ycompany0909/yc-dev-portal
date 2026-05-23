# 観測性スタックの副次的改善ロードマップ

> **作成**: 2026-05-24
> **背景**: 法体系 v1.8 Tier 1.12 観測性導入 + staff-permissions Date バグ解決を経て、観測性スタックを「日常運用ツール」に育てるためのロードマップ
>
> **関連**: [LEGAL-SYSTEM-INTEGRATED-v1.8.md](../../../ycompany-portal/docs/LEGAL-SYSTEM-INTEGRATED-v1.8.md) Tier 1.12.5 事例研究

---

## 直近の出来事（一行サマリ）

```
07:08  Tier 1.12 観測性スタック導入
07:10  ユーザーが staff-permissions.html アクセス
07:10:41  unhandled rejection 自動記録
07:11  Claude が SQL で原因特定
07:13  修正完了
```

**3 分**で本物の事故解決。観測性投資の ROI を即実証。

---

## 5 つの副次改善（優先順）

### ① ✅ updated_at 型統一（**即実装済み**）

**問題**: `staff_permissions.updated_at` が **文字列 1 件 + 数値 19 件** で混在。これが Date バグの根源。

**修正**:
```sql
UPDATE staff_permissions
SET updated_at = unixepoch('2026-05-18 14:23:38')
WHERE email = 'orzugulsetagaya@gmail.com' AND typeof(updated_at) = 'text';
```

→ 20 件全部 INTEGER に統一済み。今後 `Date * 1000` が常に正しく動く。

**派生規約**:
- 全 D1 テーブルで「日時カラムは unix epoch 秒 (INTEGER)」を Tier 1.5 D1 スキーマルールに昇格させる
- アプリ側が `Date` / `new Date(v * 1000)` で扱える前提を維持

---

### ② 🔧 render 関数の共通防御パターン化（**中期**）

**問題**: `loadXxx()` の async/await 境界には try/catch を入れているが、その中で呼ぶ `renderXxx()` (同期) が throw すると Promise が reject。catch されないと画面停止。

**改善案**: 共通 `yc-renderer.js` を作る。

```js
// assets/yc-renderer.js
window.YCRenderer = {
  /**
   * 同期 render 関数を安全に呼ぶ。throw した場合は tbody にエラー表示。
   */
  safeRender(tbody, data, rowFn) {
    try {
      tbody.innerHTML = data.map((row, i) => {
        try { return rowFn(row, i); }
        catch (e) {
          // 個別行の失敗：その行だけエラー表示にして他を続行
          return `<tr><td colspan="99" style="color:#c44">row error: ${escapeHtml(e.message)}</td></tr>`;
        }
      }).join('');
    } catch (e) {
      // 全体失敗：tbody 全体をエラー表示に
      tbody.innerHTML = `<tr><td colspan="99" style="color:#c44;padding:20px">render error: ${escapeHtml(e.message)}</td></tr>`;
      window.YCErrorTracker?.log('render failed', { error: e.message, stack: e.stack });
    }
  }
};
```

**使い方**:
```js
YCRenderer.safeRender(tbody, allMembers, (m) => {
  // 既存の row HTML 構築...
  return `<tr>...</tr>`;
});
```

**工数**: 1〜2 時間（ライブラリ作成 + 主要 5 ページ refactor）

---

### ③ 📊 error_log ダッシュボード UI（**中期**）

**問題**: 現状、エラー閲覧は `wrangler d1 execute` で SQL 直叩き。技術的でない人には不可。

**改善案**: `error-log.html` を新規作成（admin/executive 限定）。

機能:
- 直近 100 件のエラーをテーブル表示
- フィルタ: URL / 時間範囲 / type / user
- グルーピング: 同じ message のカウント
- スタックトレースの展開表示

UI スケッチ:
```
┌─ エラーログ ───────────────────────────────────────┐
│ Filter: URL [staff-permissions▼] Last [24h▼]    │
├──────────┬───────────────┬──────────┬───────────┤
│ Time     │ Type          │ Message  │ User      │
├──────────┼───────────────┼──────────┼───────────┤
│ 07:10:41 │ promise (15)  │ Invalid… │ orzugul…  │
│ 06:55:12 │ fetch_fail (8)│ HTTP 500…│ ycompany… │
└──────────┴───────────────┴──────────┴───────────┘
```

**工数**: 2〜3 時間
**配置**: breadcrumb.json の「🛠️ 開発・ツール」カテゴリ

---

### ④ 🧹 error_log 自動削除（**長期、容量問題が顕在化したら**）

**問題**: 蓄積し続けると D1 容量を圧迫。

**改善案**: yc-infra Worker の cron で毎日 1 回:
```sql
DELETE FROM error_log WHERE created_at < unixepoch() - 30 * 86400;
```

**工数**: 30 分（既存 cron に 1 行追加）
**判断基準**: error_log のレコード数が 10,000 件超えたら実装

---

### ⑤ 🚨 致命的エラー時の LINE 通知（**運用充実したら**）

**問題**: 致命的エラー（RangeError、TypeError、認証連続失敗）が発生しても、誰も気付かず放置される可能性。

**改善案**: `/api/log` の中で、特定パターンを検出したら yc-infra → LINE push:
```js
const CRITICAL_PATTERNS = [/RangeError/, /TypeError.*undefined/, /5\d{2}/];
if (CRITICAL_PATTERNS.some(p => p.test(message))) {
  // yc-infra に通知 push
  await env.NOTIFIER.fetch(...);
}
```

**工数**: 1 時間
**判断基準**: error_log で「障害級エラー」のパターンが見えてから

---

## 進捗管理

| # | 改善 | 工数 | 状態 |
|---|---|---|---|
| ① | updated_at 型統一 | 5 分 | ✅ 完了 (2026-05-24) |
| ② | render 共通防御パターン | 1〜2 h | 🔲 plan.json に追加 |
| ③ | error_log ダッシュボード | 2〜3 h | 🔲 plan.json に追加 |
| ④ | 自動削除 cron | 30 m | ⏸ 容量超過時 |
| ⑤ | 致命エラー LINE 通知 | 1 h | ⏸ パターン見えてから |

---

## 既知バグの先回り検出

観測性導入直後だからこそ、**まだ起きてないバグ**を予測的に検出できる：

```sql
-- 既存の RangeError パターンを全リスト
SELECT url, message, COUNT(*) AS occurrence, MAX(created_at) AS last_seen
FROM error_log
WHERE message LIKE '%RangeError%' OR message LIKE '%Invalid time%' OR message LIKE '%toISOString%'
GROUP BY url, message
ORDER BY occurrence DESC;

-- 過去 1 時間の全エラーサマリ
SELECT type, COUNT(*) AS n FROM error_log
WHERE created_at > unixepoch() - 3600
GROUP BY type;
```

定期 (毎週金曜) に上記クエリを実行する運用ルールを Tier 3 に追加候補。

---

## 関連ドキュメント

- ⚖️ [LEGAL-SYSTEM-INTEGRATED-v1.8.md](https://github.com/ycompany0909/ycompany-portal/blob/main/docs/LEGAL-SYSTEM-INTEGRATED-v1.8.md) — 法体系本体
- 📝 [claude-in-chrome-portal.md](https://github.com/ycompany0909/ycompany-portal/blob/main/docs/procedures/claude-in-chrome-portal.md) — L2 運用手順
- 🎯 [plan.json](../plan.json) — 強化計画（②③を組み込む候補）

---

*2026-05-24 by Claude Opus 4.7 + オルズグル*
