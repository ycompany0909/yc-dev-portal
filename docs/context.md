# YC開発コンテキスト（2026-05-18 深夜更新）

> このブロック全体をコピーして Claude.ai の最初のメッセージに貼ると、
> Claude Terminal での開発状況をそのまま引き継げます。
>
> **受け取ったClaudeへ**: まず下記「📢 引き継ぎ宣言」を読み上げてから作業を開始してください。

---

## 📢 引き継ぎ宣言

> こちらは **MacBook Air、セッション #2732** からの引き継ぎです。
>
> **今回やったこと**:
> - orzugul-portal にメディアダッシュボード（`/media`）を新設 — SNS指標手動入力 + 世田谷モーニングニュース一覧（Googleカレンダーリンク付き）
> - 世田谷モーニングニュース自動保存 — setagaya-morning GitHub Actionsワークフローにポータル保存ステップを追加
> - Xフォロワー分析ページ（`/twitter`）— 19,260人全件 D1 インポート、世田谷465人・12属性分類・戦略セグメント
> - ポスター履歴379件インポート（2019〜2023年）— color_class別フィルタ + 地図プロット（色分けピン）
> - ファビコンを @orzugulsetagaya Xプロフィール画像に変更、タブ「オルズグル ポータル」
> - 統合マップのポスターレイヤー color_class 色分け対応
>
> **残課題**:
> - 🔴 setagaya-morning リポジトリに `PORTAL_NEWS_SECRET` を GitHub Secret として追加（しないと朝ニュースがDBに保存されない）
> - 🟡 世田谷モーニングニュース 過去メールのバックフィル
> - 🟡 orzugul.com Slimstat Analytics → アクセス数自動取得
> - 🟡 Facebook Graph API（facebook.com/orzugul）フォロワー数自動取得
> - 🟡 LINE公式フォロワー数自動取得（Channel Access Token 必要）
> - 🔵 Instagram Graph API 連携
>
> 以上を受けて作業を継続してください。

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
| **統合ポータル (yc-manual-v13)** | ✅ 稼働 | 権限バッジ・ログアウトボタン・経理マニュアルカード追加済 |
| **店休日プリセット** | ✅ 完了 | gin=日曜, shim=土日 + お盆・年末年始 2026-2027 D1投入済み |
| **Plaud議事録パイプライン** | ✅ 稼働 | 要約4項目フォーマット稼働中 |
| **経営コックピット（/executive）** | ✅ 稼働 | portal.ycompany.co.jp/executive |
| **YC経理システム** | ✅ 稼働 | accounting.ycompany.co.jp（銀座1-5月・新橋1-4月完了。新橋5月のみ残り） |
| **経理 自動化マニュアル** | ✅ 完了 | accounting.ycompany.co.jp/manual・ポータル経営コーナーカード追加済 |
| **ICJデモデイ運営** | 🟡 進行中 | 6/11本番・河内・大森・平野井で座組み完了 |
| **ポスター管理システム** | 🔴 設計中 | NocoDB + LINE通知の構築 |

---

## 残タスク（優先度順）

### 🔴 HIGH（iMac必須）
- **ANTHROPIC_API_KEY を yc-manual-v13 Pages に設定** — hr-bulk-import.htmlが500エラー。`wrangler pages secret put ANTHROPIC_API_KEY --project-name yc-manual-v13`
- **EM_ADMIN_PASSWORD を実値に更新** — TEMP_PASSWORD_2026のまま
- **VPS Python NOCODB_TOKEN 平文除去** — feedback_server.py/send_report.pyのトークンを環境変数化→rotate

### 🟡 MEDIUM
- **YC Accounting 新橋5月売上データ入力** — 速報値 ¥265,234(通常+イベント)+¥474,000(サブスク)確認済み。`import_iaponia_2026.py` RECORDS追記→実行→rsync
- **ICJデモデイ 6/11 本番準備** — 最終確認
- **ポスター管理システム 設計着手** — NocoDB + LINE通知
- **Notta議事録Todo 運用フォロー** — 山川/田貝のLINE ID未取得
- **コミュニティ担当マッピング** — Messengerアカウント名入力・リマインド設計
- **勤怠/日報リマインダー 有効化判断** — 経営層判断が必要

### 🔵 LOW
- GitHub MCP 動作確認
- yc-drink-info 2段階照合実装（iMac必須）
- Square 売上インテリジェンス実装（`services/square_importer.py` 実装済み。Square Production Tokenのみ未取得）
- MyBridge → NocoDB 名刺DB移行
- event-meeting-log データ移行（iMac必須）

---

## 最近の決定・学び（2026-05-18）

- **経理 2026年売上インポート完了**:
  - 銀座(JIDAI) 1-5月: `scripts/import_jidai_2026.py` で5件追加（Jan¥1,376,750〜May¥436,100速報）
  - 新橋(IAPONIA) 1-4月: `scripts/import_iaponia_2026.py` で16件追加（通常/イベント/サブスク/IAPONIAサブスク4分類）
  - ソース: Google Drive `JIDAI_MM.YYYY売上`（0135_銀座売上表/2026/）・`売上実績26/1-4`（0131_売上速報・予想/）
- **自動化マニュアル**: `accounting.ycompany.co.jp/manual` 作成。月次チェックリスト・VPS rsync手順・Square API将来計画収録
- **ポータル財務経理カード**: yc-manual-v13 の経営コックピットに「📘 経理 自動化マニュアル」カード追加・pushデプロイ済み
- **経理アカウント対応**:
  - 1=新橋店頭売上(BU1)、2=新橋サブスク(BU1)、3=新橋IAPONIAサブスク(BU1)
  - 4=銀座売上(BU2)、5=イベント売上(BU3)
  - dedup key: `jidai:YYYY-MM` / `iaponia:YYYY-MM` / `iaponia_event:YYYY-MM` / `iaponia_sub:YYYY-MM` / `iaponia_subsriap:YYYY-MM`
- **新橋サブスク内訳（月次基本額）**: YAMATO ¥60k + AKITSUSHIMA ¥340k + MIZUHO ¥21k = ¥421k（＋IAPONIA新橋分 ¥60k）
- **VPS rsync手順**: `rsync -avz ~/yc-accounting/data/yc_accounting.db root@162.43.36.173:/opt/yc-accounting/data/` → `ssh root@162.43.36.173 "systemctl restart yc-accounting"`

---

## 主要システムURL

| サービス | URL |
|---|---|
| YCポータル（統合） | portal.ycompany.co.jp |
| 議事録 | portal.ycompany.co.jp/meetings |
| 経営カレンダー | portal.ycompany.co.jp/executive |
| 経理システム | accounting.ycompany.co.jp |
| 経理 自動化マニュアル | accounting.ycompany.co.jp/manual |
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

---

## orzugulポータル（2026-05-18 大型実装）

**ローカル**: `~/orzugul-portal/`（client/ + server/ + worker/）
**本番**: https://portal.orzugul.com（= orzugul-portal.pages.dev）
**Worker API**: https://orzugul-api.ycompany0909.workers.dev
**D1**: orzugul-db（ID: 7c0dc592-adc7-45b4-855b-16a307915a94）

### 本日実装済み ✅
1. **ポスター履歴379件インポート** — color_class別（オルズグル110/NG42/現在なし17/長妻10/未入力200）
2. **Xフォロワー分析 /twitter** — 19,260人、世田谷465人、12属性タグ分類
3. **メディアダッシュボード /media** — SNS指標手動更新 + 世田谷モーニングニュース一覧（カレンダーリンク）
4. **世田谷モーニングニュース自動保存** — setagaya-morning GitHub Actionsに保存ステップ追加済み
   - PORTAL_NEWS_SECRET: `8272b7eb91c54ee7d9e36ac41800020c9aef528f1f72d71d`
5. **ファビコン** — @orzugulsetagaya Xプロフィール画像、タブ「オルズグル ポータル」
6. **統合マップ /map ポスターレイヤー** — color_class別色分けプロット（緑/赤/グレー/青/黄）

### 残タスク（orzugul-portal）
- 🔴 **setagaya-morning repoにGitHub Secret追加**（`PORTAL_NEWS_SECRET`）← 最優先、しないと朝ニュースが保存されない
- 🟡 世田谷モーニングニュース 過去メール バックフィル
- 🟡 orzugul.com Slimstat Analytics → アクセス数自動取得
- 🟡 Facebook Graph API（facebook.com/orzugul Page Access Token）
- 🟡 LINE公式フォロワー数自動取得（Channel Access Token）
- 🔵 Instagram Graph API

### DBテーブル（D1: orzugul-db）
| テーブル | 概要 |
|---|---|
| `poster_spots` | 379件、color_class/permission/poster_count/contact |
| `twitter_followers` | 19,260件、location_class/attr_tags/is_setagaya |
| `morning_news` | date UNIQUE, subject, body |
| `media_metrics` | recorded_date/platform/metric_name/value UNIQUE |
