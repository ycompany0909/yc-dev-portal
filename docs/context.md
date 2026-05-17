# YC開発コンテキスト（2026-05-18 06:25 更新）

> このブロック全体をコピーして Claude.ai の最初のメッセージに貼ると、
> Claude Terminal での開発状況をそのまま引き継げます。

---

## 作業者・基本情報

- **担当**: オルズグル（Y COMPANY代表）、佐々生（パートナー / Sasao）
- **スタック**: Cloudflare Workers（素のJS）/ NocoDB / LINE API / GAS / Python / VPS(Ubuntu)
- **店舗**: JIDAI（銀座・日報GAS稼働）/ IAPONIA（新橋）
- **ポータル**: portal.ycompany.co.jp
- **CF Account**: ycompany0909@gmail.com（Account ID: 518cd04ae0a78ab125311da3f2a9da15）
- **マシン**: MacBook Air（外出/自宅兼用）/ iMac（自宅専用 — posta/event-meeting-logはiMacのみ）

### 重要ルール
- Workers は TypeScript不使用・素のJS
- NocoDB token は `env.NOCODB_API_TOKEN || env.NOCODB_TOKEN` の両受け
- 外部メール送信時は ycompany0909@gmail.com をCC必須
- ポータル系URLは portal.ycompany.co.jp（pages.devは内部のみ）
- 「呪文」= Claude Code CLI スラッシュコマンド（~/.claude/commands/に保存）

---

## 進行中プロジェクト

| プロジェクト | 状況 | 次のアクション |
|---|---|---|
| GitHub MCP設定 | 🟡 進行中 | claude mcp addを実行・動作確認 |
| ICJデモデイ運営 | 🟡 進行中 | 6/11本番・河内・大森・平野井で座組み完了 |
| ポスター管理システム | 🔴 設計中 | NocoDB + LINE通知の構築 |
| yc-dev-portal | ✅ 稼働 | スマホ壁打ち体制確立済み |

---

## 残タスク（優先度順）

### 🔴 HIGH
- **VPS Python NOCODB_TOKEN 平文除去** — feedback_server.py/send_report.pyのトークンを環境変数化→rotate。🚧iMacでSSH必要
- **シフトリマインダー終了日 18→15 に戻す** — 🚧2026-05-19以降に実施
- **orzugulポータル DNS移行完了** — お名前.comでNS変更。🚧お名前.comログイン必要
- **ICJデモデイ 6/11 本番準備** — 河内・大森・平野井で座組み完了、最終確認が必要
- **ANTHROPIC_API_KEY を yc-manual-v13 Pages に設定** — hr-bulk-import.htmlが500エラー。🚧iMac必須
- **EM_ADMIN_PASSWORD を実値に更新** — TEMP_PASSWORD_2026のまま。🚧iMac必須

### 🟡 MEDIUM
- **GitHub MCP 動作確認** — claude mcp addを実行
- **ポスター管理システム 設計着手** — NocoDB + LINE通知の構築
- **Notta議事録Todo 運用フォロー** — 承認処理+LINE User ID投入。🚧山川/田貝のLINE ID未取得
- **yc-drink-info 2段階照合実装** — ラベル写真でClaude Vision再判定。🚧iMac必須
- **event-meeting-log データ移行 → 旧Worker廃止** — 🚧iMac必須
- **コミュニティ担当マッピング 次ステップ** — Messengerアカウント名入力・リマインド設計
- **勤怠/日報リマインダー 有効化判断** — フラグを1にするだけ。🚧経営層判断が必要

### 🔵 LOW
- Square 売上インテリジェンス実装（Square Developer登録後）
- MyBridge → NocoDB 名刺DB移行
- Idea C 外販パッケージ化 Week 2〜6（Stripe+パイロット顧客獲得）

---

## 主要システムURL

| サービス | URL |
|---|---|
| YCポータル | portal.ycompany.co.jp/meetings |
| orzugulポータル | orzugul-portal.pages.dev |
| ポス太 | posta-app.pages.dev |
| dev-portal（このサイト） | ycompany0909.github.io/yc-dev-portal/diary.html |
| Operation-Management CF Pages | yc-manual-v13.pages.dev |

---

## 最近の決定・学び（メモリより）

- **スクショ確認**: 「スクショ見て」と言われたら ~/Downloads/ の最新画像を自動確認
- **push方針**: 汎用機能開発（dotfiles/ツール整備）は確認なしでcommit→pushまで一括実行OK
- **Plaudパイプライン**: Plaud→Drive→VPS→NocoDB→portal.ycompany.co.jp/meetings で稼働中。既存データ移管のみ未完了
- **orzugulポータル**: GitHub Actions連携済み・DNS移行（お名前.comのNS変更）のみ残り
- **ICJデモデイ**: 2026-06-11本番。JIDAI(銀座)・IAPONIA(新橋)が店舗
- **開発メモ機能**: diary.htmlの「メモ」タブからスマホで開発アイデアをGitHubへpush可能。Worker: yc-dev-memo.ycompany0909.workers.dev / PW: qMlAUfD8maxxWrqY

---

## 呪文一覧（Claude Code CLI スラッシュコマンド）

| 呪文 | 内容 |
|---|---|
| /sync-context | このファイルを更新してスマホへ同期 |
| /push-tasks | 残タスクをdiary.htmlの残タスクタブへ反映 |
| /env-check | MacBook/iMac 全マシン診断比較 |
| /dev-check | このマシンの開発環境診断 |
| /blockers | 今詰まっていることを整理 |
