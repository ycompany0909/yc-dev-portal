# 読み込み系事故の構造的解消 — 4 案

> **作成**: 2026-05-24（佐々生 / Claude Opus 4.7）
>
> **背景**: 2026-05-23〜24 に「読み込み中のまま停止」事故が連発（ロゴ反映遅延 / permissions/me 500 / staff-permissions リスト読み込み無限スピン）。
>
> **目的**: 単発のバグ修正ではなく **構造的な再発防止** を施す。本ドキュメントは 4 つの改善案を整理したアイディア集（実装は別 PR で）。

---

## 共通の根本原因 5 つ（再掲）

| # | 原因 | 影響 |
|---|---|---|
| 1 | 「env 1 個無いと即死」型コード（`if (!env.X) throw`） | 設定漏れ 1 つで全システム停止 |
| 2 | エラー隠蔽（「読み込み中…」のまま放置） | 何が壊れたか開発者にもユーザーにも見えない |
| 3 | スモークテストが preview URL + Service Token 経由のみ | 本番（ブラウザ + CF Access JWT）の挙動と乖離 |
| 4 | 多段依存（Pages Function → Worker → 環境変数 → D1） | どこか 1 つで全停止 |
| 5 | キャッシュ 4 層（ブラウザ / SW / CF Edge / DNS） | 「デプロイ済みなのに古い表示」 |

---

## 案 1: 🔑 Pages env に `COCKPIT_SECRET` を実際に設定（根本解決）

### 問題
Cloudflare Pages の本番 env に `COCKPIT_SECRET` が**空**（env-master.md で判明済）。
これが原因で `fetchMe()` / `fetchList()` 等が即 throw し、20 個の Pages Function が連鎖死亡。

### 解決
**yc-line-webhook の `COCKPIT_SECRET` と同じ値を Pages の Production env に複写**するだけ。

### 設定方法

**A. wrangler CLI**:
```bash
wrangler pages secret put COCKPIT_SECRET --project-name yc-manual-v13
# 入力待ち → yc-line-webhook と同じ値をペースト
```

**B. Cloudflare Dashboard**:
1. https://dash.cloudflare.com/518cd04ae0a78ab125311da3f2a9da15/pages/view/yc-manual-v13/settings/environment-variables
2. Production の Environment variables に `COCKPIT_SECRET` を追加
3. 値は yc-line-webhook の同名 secret と同じ
4. Save → 次のデプロイで反映

### コスト・効果

| | |
|---|---|
| 工数 | 3〜5 分 |
| 影響範囲 | 20 Pages Function 全部が一斉に正常化 |
| 副作用 | なし（既存 yc-line-webhook と同じ値なので動作変わらず） |
| リスク | 値の取得元（VPS `/opt/yc-asakai/.env` 等）を確認する必要 |

### 注意
- `~/.local-secrets/` か yc-line-webhook の secret 一覧から値を取得
- `wrangler secret list` は名前だけで値は出ないので、VPS 側の .env を SSH で確認するのが現実的

---

## 案 2: 📝 「読み込み中…」一斉撲滅 PR

### 問題
25 個の HTML に `<tbody><tr><td>読み込み中...</td></tr></tbody>` がハードコード。
`fetch` が失敗しても catch せず、画面が「読み込み中」のまま固まる。**何が壊れたか永遠に分からない**。

### 解決
共通パターンを置換：
- 初期表示: `「—」` or 空テーブル（読み込み中 ≠ エラー）
- JS で fetch 後、成功なら render、失敗なら **エラー内容を tbody に直接表示**

### コード例（共通パターン）

```javascript
async function loadList() {
  let r, data;
  try {
    r = await fetch('/api/xxx');
    data = await r.json();
  } catch (e) {
    showError('ネットワークエラー: ' + e.message);
    return;
  }
  if (!r.ok) {
    showError(`HTTP ${r.status}: ${data?.error || JSON.stringify(data).slice(0,200)}`);
    return;
  }
  renderList(data.list);
}

function showError(msg) {
  $('tbody').innerHTML = `<tr><td colspan="6" style="text-align:center;color:#c44;padding:20px">❌ ${escapeHtml(msg)}</td></tr>`;
}
```

### 対象 HTML（25 件、要確認）

- ナーチャリングハブ / お客様カルテ / checklist-detail / asakai / cockpit-review
- dev-request / faq-escapes / hr-workflow / event-calendar / industry-events
- business-card-order / sales-report / event-meeting-log / staff-forms / zaiko-kanri
- community-performance / todo-approval / photos-gallery / onboarding-approve / shift-cockpit
- 他 5 件

### コスト・効果

| | |
|---|---|
| 工数 | 1〜2 時間（一括 sed + 各 HTML の loadXxx 関数調整） |
| 影響範囲 | 全 25 HTML の UX 改善 |
| 副作用 | なし（エラー表示は失敗時のみ追加） |
| リスク | 一部 HTML で複雑な loadXxx パターンあり、丁寧な置換必要 |

### 将来的に
`assets/yc-loader.js` のような共通ライブラリを 1 個作って、全 HTML が `YCLoader.fetchAndRender(url, tbody, renderRow)` だけ呼べばよい形に DRY 化（案 3 と関連）。

---

## 案 3: 🛠 共通 fallback ユーティリティ抽出（Pages Function DRY 化）

### 問題
20 個の Pages Function が各々 `readEmail()` / `fetchMe()` を独自実装（コピペ）。
- セキュリティ修正したら 20 ファイル直す
- fallback 入れたら 20 ファイル直す
- 統一性なくバージョン乖離

### 解決
`functions/_shared/auth.js` を作成し、全 Pages Function が import：

```javascript
// functions/_shared/auth.js
export const ROLE_LABELS = { /* ... */ };

export async function readAccessEmail(request) { /* ... */ }

export async function fetchMeWithFallback(env, email) {
  try { return await fetchMe(env, email); }
  catch { return await d1DirectFallback(env, email); }
}

// 共通: D1 直引き + オーナーハードコード
async function d1DirectFallback(env, email) { /* ... */ }
```

各 Pages Function:
```javascript
import { readAccessEmail, fetchMeWithFallback, ROLE_LABELS } from '../_shared/auth.js';

export async function onRequest({ request, env }) {
  const email = await readAccessEmail(request);
  const me = await fetchMeWithFallback(env, email);
  // ...
}
```

### コスト・効果

| | |
|---|---|
| 工数 | 3〜4 時間（共通モジュール作成 + 20 ファイル refactor） |
| 影響範囲 | 全 Pages Function の保守性向上 |
| 副作用 | スモークテスト全件 pass を維持して push が必須 |
| リスク | 20 ファイル一括変更 = 競合・回帰リスク |

### 推奨アプローチ
1. `_shared/auth.js` を先に commit（既存コードは触らず）
2. 1〜2 ファイルだけ先に import に切り替え → スモーク確認
3. 問題なければ残り 18 ファイル一括 refactor
4. 全部終わったら、コピペコードを削除

---

## 案 4: 🌐 本番URL ヘルスチェック（CF Access JWT 経由）

### 問題
現在のヘルスチェック (`workflows/healthcheck.yml`) は：
- 本番 URL を curl で叩く
- **CF Access JWT 無し**でアクセス
- だから「公開 API」と「認証必須 API（401 期待）」しか検証できない
- 結果、`{"error":"COCKPIT_SECRET not set"}` のような **認証後の本物のエラー** を検知できない

### 解決
**CF Access の service token** を使ってブラウザ視点の認証付きヘルスチェック追加：

```yaml
# .github/workflows/healthcheck-authenticated.yml
- name: 認証付き本番ヘルスチェック
  env:
    CF_ID: ${{ secrets.CF_ACCESS_CLIENT_ID }}
    CF_SECRET: ${{ secrets.CF_ACCESS_CLIENT_SECRET }}
  run: |
    BASE="https://yc-manual-v13.pages.dev"  # CF Access bypass policy ある preview URL
    HEAD="-H 'CF-Access-Client-Id: $CF_ID' -H 'CF-Access-Client-Secret: $CF_SECRET'"

    # 200 を返すべき認証必須 API
    check_200() {
      local url="$1" key="$2"
      body=$(curl -sS $HEAD "$url")
      if echo "$body" | grep -q "\"error\""; then
        echo "❌ $url: $body" >&2
        exit 1
      fi
      echo "✅ $url"
    }

    check_200 "$BASE/api/permissions/me"      "role"
    check_200 "$BASE/api/permissions/list"    "list"
    check_200 "$BASE/api/asakai/dashboard"    "ok"
    check_200 "$BASE/api/zaiko/items"         "ok"
    # ...
```

### 既存スモークとの違い

| | 既存 (deploy.yml) | 本案 (新規) |
|---|---|---|
| アクセス先 | preview hash URL | 本番 (yc-manual-v13.pages.dev) |
| 認証 | 401 期待（未認証） | **200 期待（CF Access 認証通過）** |
| 検知できる | ルーティング崩壊 | **認証後の env 未設定 / DB 接続失敗** |
| 実行タイミング | deploy 直後 | deploy 直後 + 1日3回 cron |

### コスト・効果

| | |
|---|---|
| 工数 | 1 時間（workflow 作成 + 5〜10 endpoint チェック追加） |
| 影響範囲 | 「Actions 緑なのに本番壊れてる」事故の早期検知 |
| 副作用 | なし（read-only） |
| リスク | Service Token 経由でアクセスするので、その権限範囲内で動作（既存 Service Token 流用可） |

### 連動アラート
失敗時に LINE 通知 or yc-infra Worker 経由でメール送信。
失敗 endpoint 一覧と HTTP status / レスポンス body を含める。

---

## 推奨実行順序

```
① 案 1: COCKPIT_SECRET 設定          ←  3〜5 分・最大効果
   ↓
② 案 4: 認証付きヘルスチェック       ← 1 時間・再発防止
   ↓
③ 案 2: 「読み込み中」エラー化       ← 1〜2 時間・UX 改善
   ↓
④ 案 3: 共通ユーティリティ DRY 化    ← 3〜4 時間・中長期の保守性
```

**①だけで今日の事故 80% は消える**。残り 3 つは「次に同じことが起きないようにする」ための保険。

---

## 関連ドキュメント

- 📊 [skill-assessment.md](../skill-assessment.md) — 実装力診断
- 🔑 [env/env-master.md](../env/env-master.md) — 環境変数マスター（COCKPIT_SECRET 空の件）
- 🛡 [feedback_cf_pages_cdn_cache メモリ](https://github.com/ycompany0909/yc-dev-portal/) — キャッシュ事故予防
- 🎯 [plan.json](../plan.json) — 強化計画（本案を組み込む候補）
- ⚖️ ycompany-portal の CLAUDE.md「法の序列」— Tier 1 (キャッシュ運用) と本案の位置づけ

---

*作成: 2026-05-24 by Claude Opus 4.7 + 佐々生*
