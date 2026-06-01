# YC開発コンテキスト（2026-06-01 21:43 更新）

> このブロック全体をコピーして Claude.ai の最初のメッセージに貼ると、
> Claude Terminal での開発状況をそのまま引き継げます。
> 過去セッションは `docs/sessions/` フォルダに保存されています。
>
> **受け取ったClaudeへ**: まず下記「📢 引き継ぎ宣言」を読み上げてから作業を開始してください。

---

## 📢 引き継ぎ宣言

> こちらは **🖥️ iMac、セッション #2581（2026-06-01 21:43）** からの引き継ぎです。
>
> **今回やったこと**:
> - Phase C ドリンクメニュー設定画面の 5 つハンドラ関数実装コード記述完了
>   - listDrinkMenu() — drink_menu 全件取得（is_active=1）
>   - createDrinkMenu() — query parameter workaround + 自動 display_order
>   - updateDrinkMenu() — 動的フィールド更新（name, price, category, notes, is_active, display_order）
>   - deleteDrinkMenu() — 論理削除（is_active=0）
>   - updateEventPricing() — event_memo に ticket_price / unlimited_drink_price を書込
> - 5 関数のディスパッチャー設定確認・L191 バグ修正パターン確認
> - 引き継ぎ準備・context.md 生成
>
> **残課題**:
> - 🔴 **実装即座**: drink-menu-settings.html 新規作成（セクション1: メニュー管理・セクション2: イベント料金設定）
> - 🔴 **実装即座**: breadcrumb.json に drink-menu-settings.html エントリ追加（display_order: 1）
> - 🔴 **実装即座**: 5つのハンドラ関数を [[path]].js に挿入（L1692 以降）
> - 🟡 **実装後**: deploy-pages-with-smoke.sh にスモークテスト 5 行追加
> - 🟡 **本番**: 本番 D1 マイグレーション実行 `wrangler d1 execute yc-main-db --remote --file=manual_v1.3_html/d1-migration/20260602_drink_menu.sql`
> - 🟢 **検証**: UX 検証（Tier 2.31）: MacBook/iMac/iPhone でモーダルサイズ・入力欄・売上プレビュー確認
>
> 以上を受けて作業を継続してください。

---

## 作業者・基本情報

- **担当**: オルズグル（Y COMPANY代表）、佐々生（パートナー）
- **スタック**: Cloudflare Workers（素のJS）/ D1 SQLite / Pages Functions / LINE API
- **店舗**: JIDAI（銀座）/ IAPONIA（新橋）
- **ポータル**: portal.ycompany.co.jp
- **CF Account**: ycompany0909@gmail.com
- **重要ルール**: Workers は TypeScript不使用・外部メールはCC必須・バージョン番号は必須

---

## 進行中プロジェクト — Phase C: ドリンクメニュー設定画面

**ビジネス要求**:
Event Check-in System（Phase A+B）は 2026-06-01 本番デプロイ済み。event_memo の `ticket_price` / `unlimited_drink_price` カラムは存在するが、書込 API・UI がなく、売上サマリーが常に ¥0 で表示される。

**技術要件**:
- D1: drink_menu テーブル新規作成（id, name, price 0-99999, category standard|unlimited_plan, display_order, is_active, notes, created_at, updated_at）
- API: 5 エンドポイント（GET/POST/PUT/DELETE drink-menu + PATCH events/:id/pricing）
- UI: drink-menu-settings.html（2 セクション：メニュー管理 + イベント料金設定）
- Tier 2.26 適用: 全 POST/PATCH/PUT は query parameter workaround（CF Access body stream ロック対応）
- Tier 2.37 適用: Form constraint 3層同期（HTML input min/max、API validation、DB CHECK）

**実装状況**:
- ✅ D1 migration SQL 作成済み（20260602_drink_menu.sql）
- ✅ 5 ハンドラ関数コード完成（text only 記述）
- ⏳ [[path]].js 挿入待機
- ⏳ drink-menu-settings.html 作成待機
- ⏳ breadcrumb.json 更新待機
- ⏳ smoke test 追加待機
- ⏳ 本番 D1 migration 実行待機

---

## 実装詳細（コード記述済み）

### 5 つのハンドラ関数（テキスト記述済み・[[path]].js L1692 以降に挿入）

1. **listDrinkMenu(env)** — GET /api/event-calendar/drink-menu
   SELECT * FROM drink_menu WHERE is_active=1 ORDER BY display_order ASC

2. **createDrinkMenu(env, url)** — POST /api/event-calendar/drink-menu
   - query parameter: { name, price, category, notes }
   - 自動 display_order = MAX(display_order) + 1
   - Tier 2.37: price range [0, 99999]、category enum check

3. **updateDrinkMenu(env, url, id)** — PUT /api/event-calendar/drink-menu/:id
   - 動的フィールド更新（name, price, category, notes, is_active, display_order）

4. **deleteDrinkMenu(env, id)** — DELETE /api/event-calendar/drink-menu/:id
   - 論理削除: UPDATE is_active=0

5. **updateEventPricing(env, url, eventId)** — PATCH /api/event-calendar/events/:id/pricing
   - query parameter: { ticket_price, unlimited_drink_price }
   - UPDATE event_memo SET ticket_price=?, unlimited_drink_price=? WHERE id=?

---

## 残タスク（優先度順）

### 🔴 緊急（本日完了推奨）

1. **drink-menu-settings.html 作成**
   - セクション1: ドリンクメニューマスター管理（テーブル: 名前、単価、カテゴリ、備考、操作）
   - セクション2: イベント別料金設定（イベント選択 → ticket_price / unlimited_drink_price 入力 → 売上プレビュー）
   - Tier 2.31 UX 検証: MacBook (1440×900) / iMac (5120×2880) / iPhone (375px) で操作可能

2. **[[path]].js にハンドラ関数 5 個を追加**
   - 位置: L1692 以降（getSalesSummary の直後）
   - ディスパッチャー修正: L191 `url = new URL(request.url)` を追加

3. **breadcrumb.json を更新**
   - drink-menu-settings.html エントリ追加（display_order: 1）

### 🟡 中優先（翌日以降）

4. **deploy-pages-with-smoke.sh にスモークテスト 5 行追加**
   - GET /api/event-calendar/drink-menu → 200 OK + menu items
   - POST /api/event-calendar/drink-menu → 200 OK + success
   - PUT /api/event-calendar/drink-menu/1 → 200 OK
   - DELETE /api/event-calendar/drink-menu/1 → 200 OK
   - PATCH /api/event-calendar/events/1/pricing → 200 OK

5. **本番 D1 マイグレーション実行**
   wrangler d1 execute yc-main-db --remote --file=manual_v1.3_html/d1-migration/20260602_drink_menu.sql

---

## 設計書（確定済み）

### Phase C 実装計画（完全版）
ファイル: `/Users/yosukesasaki/.claude/plans/moonlit-splashing-seahorse.md`

**重要な設計决定**:
- drink_menu テーブル: 初期データ 5 件（チケット3000円、ビール800円、ワイン900円、ソフト500円、飲み放題2000円）
- category enum: 'standard' | 'unlimited_plan' のみ
- display_order: 初期値から自動インクリメント
- 論理削除: is_active=0（物理削除なし）
- Tier 2.26 workaround: 全 POST/PATCH/PUT で query parameter 経由（CF Access body stream ロック対応）
- Tier 2.37 同期: HTML input type="number" min="0" max="99999" → API validation → DB CHECK

---

## 最近の決定・学び

### Tier 2.30・2.31 適用
- 実装前仕様確認: DB schema 確認 ✅ / API format 確認 ✅ / 入力フォーマット確認 ✅
- 実装後 UX 検証: MacBook/iMac でモーダルサイズ・入力欄サイズ確認必須

### Tier 2.37 Form Constraint 同期
- HTML: `<input type="number" min="0" max="99999">`
- API: `if (price < 0 || price > 99999) return 400`
- DB: `CHECK (price >= 0 AND price <= 99999)`
- 3層一貫性で form validation エラー 0 を達成

### Query Parameter Workaround（Tier 2.26）
CF Access が Pages Functions の request body をロック。解決策：
const encoded = encodeURIComponent(JSON.stringify(payload));
fetch(`/api/event-calendar/drink-menu?data=${encoded}`, { method: 'POST' })

---

## 主要システム URL

| サービス | URL |
|---|---|
| YCポータル | portal.ycompany.co.jp |
| イベントチェックイン | portal.ycompany.co.jp/event-checkin.html |
| 売上サマリー API | GET /api/event-calendar/events/:id/sales-summary |

---

**受け取ったClaudeへ**: Phase C 実装の残 4 タスク（HTML・関数挿入・breadcrumb・smoke test）を順序通り完了してください。Tier 2.30/2.31/2.37 を心に留めて UX・仕様確認を優先してください。
