# YC開発コンテキスト（2026-05-18 07:25 更新）

> このブロック全体をコピーして Claude.ai の最初のメッセージに貼ると、
> Claude Terminal での開発状況をそのまま引き継げます。

---

## 作業者・基本情報

- **担当**: オルズグル（Y COMPANY代表）、佐々生（パートナー / Sasao）
- **スタック**: Cloudflare Workers（素のJS）/ NocoDB / LINE API / GAS / Python / VPS(Ubuntu)
- **店舗**: JIDAI（銀座・日報GAS稼働）/ IAPONIA（新橋）
- **ポータル**: portal.ycompany.co.jp
- **CF Account**: ycompany0909@gmail.com（Account ID: 518cd04ae0a78ab125311da3f2a9da15）
- **VPS**: root@162.43.36.173（Xserver）
- **マシン**: MacBook Air（外出/自宅兼用）/ iMac（自宅専用 — posta/event-meeting-logはiMacのみ）

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
| **Plaud議事録パイプライン** | ✅ 稼働中 | 要約フォーマット改善バッチ実行中（500件・2026-05-18） |
| **経営コックピット（/executive）** | ✅ 稼働 | タグルール管理UI追加済み。カレンダー表示正常化済み |
| ICJデモデイ運営 | 🟡 進行中 | 6/11本番・河内・大森・平野井で座組み完了 |
| ポスター管理システム | 🔴 設計中 | NocoDB + LINE通知の構築 |
| orzugulポータル | ✅ 稼働 | portal.orzugul.com（DNS移行完了） |
| yc-dev-portal | ✅ 稼働 | スマホ壁打ち体制確立済み |

---

## 残タスク（優先度順）

### 🔴 HIGH
- **議事録要約 品質向上** — 500件の要約を新4項目フォーマットで一括再生成中（VPS バックグラウンド実行中）
- **VPS Python NOCODB_TOKEN 平文除去** — feedback_server.py/send_report.pyのトークンを環境変数化→rotate。🚧iMacでSSH必要
- **シフトリマインダー終了日 18→15 に戻す** — 🚧2026-05-19以降に実施
- **ICJデモデイ 6/11 本番準備** — 最終確認が必要

### 🟡 MEDIUM
- **GitHub MCP 動作確認** — claude mcp addを実行
- **ポスター管理システム 設計着手** — NocoDB + LINE通知の構築
- **Notta議事録Todo 運用フォロー** — 承認処理+LINE User ID投入。🚧山川/田貝のLINE ID未取得
- **yc-drink-info 2段階照合実装** — ラベル写真でClaude Vision再判定。🚧iMac必須
- **event-meeting-log データ移行 → 旧Worker廃止** — 🚧iMac必須
- **勤怠/日報リマインダー 有効化判断** — 🚧経営層判断が必要
- **ANTHROPIC_API_KEY を yc-manual-v13 Pages に設定** — hr-bulk-import.htmlが500エラー。🚧iMac必須

### 🔵 LOW
- Square 売上インテリジェンス実装（Square Developer登録後）
- MyBridge → NocoDB 名刺DB移行
- Idea C 外販パッケージ化

---

## 最近の決定・学び

- **議事録要約フォーマット変更（2026-05-18）**: 旧「3〜5行200字」→ 新「4項目構造（目的・議論・決定・アクション）600〜1200字」。VPS `/opt/yc-asakai/yc_plaud_pipeline.py` 更新済み
- **タグルール管理**: NocoDB `tagging_rules` テーブル（ID: m9i4xs724u75tm8）。portal.ycompany.co.jp/executive/rules から編集可能
- **自動タグ付け**: VPS `/opt/yc-asakai/auto_tagger.py` が毎朝7時実行。IKIZAMA/Y COMPANY/政治/店舗/行政/ICJをタグ付け
- **経営カレンダーpadバグ修正**: padStart(2,"pad") → padStart(2,"0")（Cloudflareバンドル展開時の残骸）
- **push方針**: 汎用機能開発は確認なしでcommit→pushまで一括実行OK

---

## 主要システムURL

| サービス | URL |
|---|---|
| YCポータル（議事録） | portal.ycompany.co.jp/meetings |
| 経営カレンダー | portal.ycompany.co.jp/executive |
| タグルール管理 | portal.ycompany.co.jp/executive/rules |
| orzugulポータル | portal.orzugul.com |
| ポス太 | posta-app.pages.dev |
| dev-portal | ycompany0909.github.io/yc-dev-portal/diary.html |
| Operation-Management CF Pages | yc-manual-v13.pages.dev |

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

## 呪文一覧（Claude Code CLI スラッシュコマンド）

| 呪文 | 内容 |
|---|---|
| /sync-context | このファイルを更新してスマホへ同期 |
| /push-tasks | 残タスクをdiary.htmlの残タスクタブへ反映 |
| /env-check | MacBook/iMac 全マシン診断比較 |
| /dev-check | このマシンの開発環境診断 |
| /blockers | 今詰まっていることを整理 |
