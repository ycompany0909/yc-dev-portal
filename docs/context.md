# YC開発コンテキスト（2026-05-18 夕方更新）

> このブロック全体をコピーして Claude.ai の最初のメッセージに貼ると、
> Claude Terminal での開発状況をそのまま引き継げます。

---

## 作業者・基本情報

- **担当**: オルズグル（Y COMPANY代表）、佐々生（パートナー / ycompany0909@gmail.com）
- **スタック**: Cloudflare Workers（素のJS）/ NocoDB / LINE API / GAS / Python / VPS(Ubuntu)
- **店舗**: JIDAI（銀座・gin）/ IAPONIA（新橋・shim）
- **ポータル**: portal.ycompany.co.jp
- **CF Account**: ycompany0909@gmail.com（Account ID: 518cd04ae0a78ab125311da3f2a9da15）
- **VPS**: root@162.43.36.173（Xserver）

### 重要ルール
- Workers は TypeScript不使用・素のJS
- NocoDB token は `env.NOCODB_API_TOKEN || env.NOCODB_TOKEN` の両受け
- 外部メール送信時は ycompany0909@gmail.com をCC必須
- ポータル系URLは portal.ycompany.co.jp（pages.devは内部のみ）
- 「スクショ見て」と言われたら ~/Downloads/ の最新画像を必ず確認

---

## 進行中プロジェクト

| プロジェクト | 状況 | 次のアクション |
|---|---|---|
| **CF Accessポータル権限** | ✅ 完了 | ycompany0909/orzugulsetagaya/山川/田貝が正常ログイン可 |
| **統合ポータル (yc-manual-v13)** | ✅ 稼働 | 権限バッジ・ログアウトボタン・ボウズ現場表示・申請フォーム文言修正 済み |
| **店休日プリセット** | ✅ 完了 | gin=日曜, shim=土日 + お盆・年末年始 2026-2027 D1投入済み |
| **Plaud議事録パイプライン** | ✅ 稼働 | 要約4項目フォーマット稼働中 |
| **経営コックピット（/executive）** | ✅ 稼働 | portal.ycompany.co.jp/executive |
| **ICJデモデイ運営** | 🟡 進行中 | 6/11本番・河内・大森・平野井で座組み完了 |
| **ポスター管理システム** | 🔴 設計中 | NocoDB + LINE通知の構築 |
| **YC経理システム** | ✅ 稼働 | accounting.ycompany.co.jp（2026年売上入力が残り） |

---

## 残タスク（優先度順）

### 🔴 HIGH（iMac必須）
- **ANTHROPIC_API_KEY を yc-manual-v13 Pages に設定** — hr-bulk-import.htmlが500エラー。`wrangler pages secret put ANTHROPIC_API_KEY --project-name yc-manual-v13`
- **EM_ADMIN_PASSWORD を実値に更新** — TEMP_PASSWORD_2026のまま
- **VPS Python NOCODB_TOKEN 平文除去** — feedback_server.py/send_report.pyのトークンを環境変数化→rotate

### 🟡 MEDIUM
- **YC Accounting 2026年売上データ入力** — 新橋・銀座・イベント 2026/1〜現在分。accounting.ycompany.co.jpから入力
- **ICJデモデイ 6/11 本番準備** — 最終確認
- **コミュニティ参加者管理 色分け確認** — community-performance.html の色が正しいか（後回し）
- **ポスター管理システム 設計着手** — NocoDB + LINE通知
- **Notta議事録Todo 運用フォロー** — 山川/田貝のLINE ID未取得
- **コミュニティ担当マッピング** — Messengerアカウント名入力・リマインド設計
- **勤怠/日報リマインダー 有効化判断** — 経営層判断が必要

### 🔵 LOW
- GitHub MCP 動作確認
- yc-drink-info 2段階照合実装（iMac必須）
- Square 売上インテリジェンス実装
- MyBridge → NocoDB 名刺DB移行
- event-meeting-log データ移行（iMac必須）

---

## 最近の決定・学び（2026-05-18）

- **ポータル権限の根本修正**: CF Access JWT は `cf-access-jwt-assertion` ヘッダーで届く（`Cf-Access-Authenticated-User-Email` は来ない）。Pages Function で Cookie fallback も追加済み
- **COCKPIT_SECRET 不一致が原因だった**: Pages と yc-line-webhook で別々に設定されていたため 401。新シークレット `d5d03fbf...` で統一済み
- **D1 binding名注意**: yc-line-webhook の staff_permissions は `env.SHIFT_DB`（`env.DB` ではない）
- **D1カラム名注意**: staff_permissions の custom_overrides カラムは `custom_overrides_json`
- **Pages シークレット更新は再デプロイが必要**: `wrangler pages secret put` 後に `wrangler pages deploy` しないと反映されない
- **店休日スキーマ**: D1 `yc-shift-db` の `closed_days` テーブル (year, month, day, store) PRIMARY KEY 4列。gin=銀座JIDAI, shim=新橋IAPONIA
- **シフトリマインダー**: MONTHLY_REMINDER_END を 18→15 に戻した（2026-05 hotfix解除）
- **ポータルWorkerは routes なし**: `yc-portal` Worker（Operation-Management側）のwrangler.tomlにroutesなし。portal.ycompany.co.jpは全て `yc-manual-v13` Pages が担当
- **CF Access スタッフ**: orzugulsetagaya@gmail.com(admin), ycompany0909@gmail.com(executive), masakiyamakawa670@gmail.com(admin), tberith@gmail.com(admin)

---

## 主要システムURL

| サービス | URL |
|---|---|
| YCポータル（統合） | portal.ycompany.co.jp |
| 議事録 | portal.ycompany.co.jp/meetings |
| 経営カレンダー | portal.ycompany.co.jp/executive |
| 経営管理ダッシュボード | portal.ycompany.co.jp/mgmt |
| 経理システム | accounting.ycompany.co.jp |
| orzugulポータル | portal.orzugul.com |
| dev-portal | ycompany0909.github.io/yc-dev-portal/diary.html |

---

## Plaudパイプライン構成

```
Plaud録音 → Zapier(orzugulsetagaya) → Google Drive(YC_Plaud_Transcripts)
  → VPS cron毎時27分 /opt/yc-asakai/yc_plaud_pipeline.py
    → Claude Sonnet: 話者推定・要約（4項目構造）・insights抽出
      → NocoDB meetings(mvl0ebr5efxaa1n) / insights(meuqx3an0r5zg61)
        → portal.ycompany.co.jp/meetings
```
