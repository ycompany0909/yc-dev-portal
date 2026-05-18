# YC開発コンテキスト（2026-05-18 夜 更新）

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
| **CF Accessポータル権限** | ✅ 完了 | executive/admin/field/nonfield ロール正常稼働 |
| **統合ポータル (yc-manual-v13)** | ✅ 稼働 | 経営コーナー表示バグ修正済（CSS !important対応）|
| **文化資本夜話ページ** | ✅ 追加 | /文化資本夜話.html 作成・social-cornerにカード追加済 |
| **一日店長ミートアップページ** | ✅ 追加 | /一日店長ミートアップ.html 作成・social-cornerにカード追加済 |
| **店休日プリセット** | ✅ 完了 | gin=日曜, shim=土日 + お盆・年末年始 2026-2027 D1投入済み |
| **Plaud議事録パイプライン** | ✅ 稼働 | 要約4項目フォーマット稼働中・500件一括再生成完了 |
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
- **YC Accounting 2026年売上データ入力** — 新橋・銀座・イベント 2026/1〜現在分
- **ICJデモデイ 6/11 本番準備** — 最終確認
- **コミュニティ参加者管理 色分け確認** — community-performance.html の色が正しいか
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

- **経営コーナー非表示バグ修正**: `[data-role="executive"]`要素に`style="display:none"`があるとCSSクラスベースの制御が効かない。`body.role-effective-executive [data-role="executive"] { display: block !important; }` で解決
- **permission-badge.jsにapplyDataRole()追加**: JSでも`[data-role]`要素のインラインstyleをクリアするよう修正（CSS修正と二重対策）
- **議事録要約4項目フォーマット**: 【会議の目的・背景】【主な議論・検討内容】【決定事項・合意内容】【アクションアイテム】600〜1200字。VPSのyc_plaud_pipeline.py適用済み
- **議事録500件一括再生成完了**: Claude Haiku使用（Sonnetだと遅すぎる。~6s/件・50分）
- **文化資本夜話・一日店長ミートアップ ページ作成**: /文化資本夜話.html（紫テーマ）、/一日店長ミートアップ.html（茶テーマ）。social-cornerカード追加済
- **NocoDB PATCH/DELETE はarray形式**: `[{Id:n, ...fields}]` でないと保存失敗
- **経営カレンダー0件バグ修正**: `padStart(2,"pad")`→`padStart(2,"0")` (Cloudflare bundle再構築の残骸)
- **ポータルWorkerは routes なし**: portal.ycompany.co.jpは全て `yc-manual-v13` Pages が担当

---

## 主要システムURL

| サービス | URL |
|---|---|
| YCポータル（統合） | portal.ycompany.co.jp |
| 議事録 | portal.ycompany.co.jp/meetings |
| 経営カレンダー | portal.ycompany.co.jp/executive |
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
