# YC 開発履歴 — 2026年

> 「いつ何を作ったか」の時系列記録。
> **診断・評価**は [skill-assessment.md](skill-assessment.md) を、**インタラクティブ表示**は [diary.html](diary.html) を参照。

---

## TL;DR — 主要マイルストーン

| 日付 | マイルストーン | 規模 |
|---|---|---|
| **5/12** | Operation-Management 統合ポータル開始 | 中 |
| **5/14** | yc-workers 18本を1リポジトリに統合 | 大 |
| **5/17** | orzugul-portal v1 / yc-dev-portal 公開 | 大 |
| **5/18-19** | メディアダッシュボード（X 19,260人 / ポスター 379件） | 中 |
| **5/20** | **NocoDB → Cloudflare D1 大移行** | 特大 |
| **5/22** | みおりビュー（個人別 hide_features）+ 在庫管理改善 | 中 |
| **5/23** | **CI/CD 基盤完成（自動デプロイ・スモーク 43件・PR運用）** | 特大 |

---

## 📅 時系列タイムライン

### 2026年4月

#### 4/30 — demoday-backend 初期化
- `demoday-backend` リポジトリ作成
- Google Sheets 連携・Resend 設定
- 個人情報ファイルを `.gitignore`

### 2026年5月

#### Week 1（5/1〜5/7）
- 5/1 demoday-backend メールデザイン更新、テスト用重複チェックスキップ

#### Week 2（5/12〜5/16）

##### 5/12 — Operation-Management スタート
- 運用マニュアルを Notion → GitHub へ移行（v1.1〜v1.3）
- AI 壁打ち分析レポート作成

##### 5/13 — 統合ポータル新設
- `manual_v1.3_html/index.html` — 統合ポータル基盤
- 個人別マニュアル + インタラクティブヒアリング UI
- 議事録 → タスク化テンプレート（meeting.html + Worker 連携）
- AI 業務変革パッケージ営業資料

##### 5/14 — シフト管理 v2 + Worker 統合
- シフト管理 v2（3 Worker 構成）
- FAQ Bot / お酒情報 / 運用ダッシュボード
- YC 用語集 + ガイド内ホバーツールチップ
- CF Access カスタムドメイン URL 統一
- event-meeting-log を iMac 版から MacBook/ポータル本体へ移植
- マルチテナント基盤（Idea C Week 1）
- **🪄 yc-workers リポジトリ作成 — 18本の Workers を1箇所に統合**

##### 5/15 — 現場運用の中核機能群
- 開店/閉店チェックリスト + 提出状況コックピット
- 日報拡張 v2（8 フィールド追加 + イベント集客バッジ）
- 1on1 記録アプリ + AI 再要約ボタン
- Notta 議事録 → Todo 承認パイプライン（能動化）
- attendance-form: 認証成功後 appContent 非表示バグ修正
- 山川さん FB 対応（検索 UX / QR カード / 日報・勤怠 cockpit 連動）

##### 5/16 — AI 連携 + 経理コックピット開始
- 名刺スキャン（LINE 画像 → Claude Vision → NocoDB）
- NocoDB → Todoist sync（`yc_noco_to_todoist.py`）
- daily brief に D1 店舗データ追加
- 通知マスターページ追加
- yc-notta-webhook で山川さん担当 Todo の承認メール自動送信
- **🪄 yc-accounting 構築開始**

#### Week 3（5/17〜5/19）

##### 5/17 — URL 統一 + 3 リポジトリ開設の日
- シフト承認フロー: 田貝 → 山川 LINE プッシュ承認
- `portal.ycompany.co.jp` URL 正規化（全 Worker 統一）
- event-meeting-log カレンダービュー追加
- 管理 UI 機能追加（todo-approval / 権限フィルタ / me API）
- 名刺発行プロフィール統合 + permission-badge 追加
- Square 連携サブスク管理 + 顧客向け LINE Bot
- **🪄 yc-dotfiles 開設**: `/dev-check` + `yc-check` TUI + SSS tier
- **🪄 orzugul-portal v1 開設**: 統合政治活動ポータル
- **🪄 yc-dev-portal 開設**: スマホ壁打ち用 GitHub Pages ダッシュボード

##### 5/18 — メディア・自動化の日
- yc-dev-portal に開発メモ機能（スマホ → Worker → GitHub）
- yc-dev-portal に残タスク表示タブ（`/push-tasks`）
- yc-dev-memo Worker 新設（GitHub API 連携）
- iMac 環境整備: bat / eza / zoxide / fd / lazygit / docker / colima
- `/env-check` 呪文（iCloud 経由で全マシン診断結果比較）
- orzugul-portal メディアダッシュボード `/media` `/twitter` `/map`
- **X フォロワー 19,260 人を属性タグ 12 種で分類**
- **ポスター履歴 379 件の色分け地図プロット**

##### 5/19 — 仕上げ
- orzugul-portal メディア機能の微調整

#### Week 4（5/20〜5/23）

##### 5/20 — **🚨 NocoDB → D1 大移行（特大）**
- Pages Functions 13 個 + Workers 3 個 を D1 バインディングに同時切り替え
- yc-portal Worker: meetings CRUD 完全 D1 化
- yc-notta-webhook / yc-template-meeting D1 化
- Pages: api/asakai / segments / zaiko / impressive-customers / presenter-candidates / nurturing-admin 全 D1 移行
- **13 エンドポイントのスモークテスト整備**
- **🪄 Worker 統合: 旧 22 本 → 新 8 本（yc-ai / content / forms / infra / line-webhook / ops / portal / shortcut）**

##### 5/22 — 機能強化の日
- **🪄 みおりビュー**（個人別 hide_features + View As カスタムビュー）
- 在庫管理 大幅改善（消費量予測・二列アラート・last_checked 修正）
- 大型「朝会を始める」ボタンを index.html トップに配置
- shift-cockpit init() の DOMContentLoaded 待ち / null safety

##### 5/23 — **🚨 CI/CD 基盤完成（本日・特大）**
- 🎯 deploy.yml 修復: Node 22 + wrangler@4（**10 連敗から初の green**）
- 🎯 Workers 8 本の自動デプロイ workflow（matrix 並列）
- 🎯 本番ヘルスチェックの workflow_run 即時実行化
- 🎯 CF Access Service Token 認証経路検証をスモークに統合
- 🎯 main protected branch + PR 運用（GitHub Pro 加入）
- 🛡 preview-pages.dev バイパス全削除（別セッション混入修正）
- 🔧 permissions/me の期待値を guest に修正
- 📊 skill-assessment.md 自動生成（実装力診断レポート初版）
- 📅 diary.html 改造（壁打ち削除・診断タブ追加・強化計画化）

---

## 🚀 プロジェクト辞典（15件）

### A. 経営・店舗運用系

| # | プロジェクト | 開始 | 目的 | URL | 状態 |
|---|---|---|---|---|---|
| 1 | **YC 統合ポータル** | 5/13 | 経営・店舗・朝会の中枢 | portal.ycompany.co.jp | ✅ 本番 |
| 2 | **朝会管理** | 5/15 | 朝会成立要件・日報・チェックリスト | /asakai.html | ✅ 完了 |
| 3 | **お客様ポータル** | 〜5/20 | 顧客 CRM・ナーチャリング | /customer-search | ✅ 完了 (13,860件) |
| 4 | **店舗情報** | — | JIDAI(銀座)/IAPONIA(新橋) | /jidai /iaponia | ✅ 完了 |
| 12 | **カスタムビュー** | 5/22 | みおりビュー等の個人別機能制御 | data-feature + permission-badge | ✅ 完了 |

### B. 政治活動・地域系

| # | プロジェクト | 開始 | 目的 | URL | 状態 |
|---|---|---|---|---|---|
| 4 | **オルズグル事務所ポータル** | 5/17 | 支持者 CRM・政策・地図・広報 | orzugul-portal.pages.dev | ✅ 完了 |
| — | **ポス太** | 4月以前 | 政治活動ポスター管理 | posta-app.pages.dev | ✅ 本番 |

### C. 自動化パイプライン

| # | プロジェクト | 開始 | 目的 | 技術 | 状態 |
|---|---|---|---|---|---|
| 5 | **Plaud パイプライン** | 4月以前 | 録音 → 要約 → insights 自動化 | VPS Python + Claude API + D1 | ✅ 完了 |
| 8 | **TimeTree 統合** | 5/23 | イベント打ち合わせ日マッピング | TimeTree API + Notta + D1 | ✅ 完了 |

### D. インフラ・運用基盤

| # | プロジェクト | 開始 | 目的 | URL | 状態 |
|---|---|---|---|---|---|
| 9 | **YC Workers 統合** | 5/14 | 18本 → 8本に集約・NocoDB 廃止 | yc-workers/ | ✅ 完了 |
| 10 | **YC CI/CD** | 5/23 | 自動デプロイ・スモーク・PR 運用 | GitHub Actions | ✅ 完了 |
| — | **yc-dotfiles** | 5/17 | 開発環境構築 dotfiles + TUI | yc-dotfiles/ | ✅ 完了 |

### E. ドキュメント・知識系

| # | プロジェクト | 開始 | 目的 | URL | 状態 |
|---|---|---|---|---|---|
| 6 | **用語集一元化** | 5/14 | 事業体用語のマスタ化 | /glossary | 🟡 進行中 |
| 7 | **IKIZAMA データソース定義** | — | 会員種別・ふりがな正式化 | Excel + Notion | ✅ 完了 |

### F. 経理・会計

| # | プロジェクト | 開始 | 目的 | URL | 状態 |
|---|---|---|---|---|---|
| 11 | **YC Accounting** | 5/16 | カスタム会計システム | VPS FastAPI + SQLite | ✅ 本番 |

### G. 開発支援

| # | プロジェクト | 開始 | 目的 | URL | 状態 |
|---|---|---|---|---|---|
| — | **yc-dev-portal** | 5/17 | スマホ壁打ち用ダッシュボード | ycompany0909.github.io/yc-dev-portal | ✅ 完了 |
| 15 | **ポータル景観マップ** | — | 4ポータル構成マップ | 運用ドキュメント | ✅ 完了 |

### H. 構想中

| # | プロジェクト | 開始 | 目的 | 状態 |
|---|---|---|---|---|
| 13 | **AI 秘書（政宗・凛）** | — | 各ポータルの AI 応答 | 🟡 企画中 |

---

## 🛠 技術スタック早見表

### コア技術（全プロジェクトで頻出）

| 技術 | 用途 | 出現回数 |
|---|---|---|
| **Cloudflare D1** | メインDB（NocoDBから移行済み） | 9 |
| **Cloudflare Pages + Functions** | フロント + API | 7 |
| **Cloudflare Workers** | バックエンド（LINE / cron / Webhook） | 8 (本) |
| **Cloudflare Access** | 認証（3層 + Service Token） | 1 |

### 周辺技術

| 技術 | 用途 |
|---|---|
| **Python (VPS cron)** | 自動化（Plaud / TimeTree / 名刺マッチング） |
| **LINE Messaging API** | 日報・通知・Bot |
| **Claude API** | 議事録要約・朝会アジェンダ生成 |
| **GAS** | JIDAI 日報・売上アラート（clasp 経由で CLI 編集） |
| **Vue 3** | オルズグルポータルのみ |
| **FastAPI + SQLite** | YC Accounting |
| **TimeTree API / Notta** | 議事録・カレンダー連携 |

### CI/CD（2026-05-23 完成）

| 仕組み | 役割 |
|---|---|
| **GitHub Actions deploy.yml** | Pages 自動デプロイ + スモーク 43 件 |
| **GitHub Actions workers-deploy.yml** | Workers 8 本の matrix 並列デプロイ |
| **GitHub Actions healthcheck.yml** | 本番ヘルスチェック（deploy 後即時 + 毎日 5:00 JST） |
| **CF Access Service Token** | 認証経路の自動生存確認 |

---

## 📊 数字で見る成果

| 指標 | 値 |
|---|---|
| 過去30日のコミット | **414** |
| Claude 協働率 | **100%** |
| 同時並行プロジェクト | **15** |
| 同時並行ドメイン | **5** (経営・顧客・政治・会計・イベント) |
| お客様 DB レコード | **13,860 件** |
| Workers 統合 | **22 → 8 本** |
| Pages Functions | **13 個** |
| 自動デプロイ成功率 | 10連敗 → **42/42 件 pass** |
| スモークテスト | 0 件 → **43 件** |

---

## 🪄 使った武器（Tools & Skills）

### Claude Code (Mac CLI)
- iMac: 主要開発環境（24時間稼働）
- MacBook Air: リモートアクセス・補助

### Slash Skills
- `/push-tasks` — 残タスクを yc-dev-portal に push
- `/sync-context` — context.md を更新（メモリ + CLAUDE.md 統合）
- `/hikitsugi` — 過去セッションの引き継ぎ宣言を読み上げ
- `/dev-check` / `/env-check` — 開発環境の診断
- `/loop` — 自律的反復タスク

### コマンドラインツール
- `wrangler` (Cloudflare CLI)
- `gh` (GitHub CLI)
- `clasp` (GAS CLI)
- `bat` / `eza` / `zoxide` / `fd` / `lazygit` / `docker` / `colima`

### 外部 API
- Cloudflare API（D1 / Access / Service Tokens / Pages / Workers）
- GitHub API
- LINE Messaging API
- Claude API
- TimeTree API
- Notta API
- Square API
- Resend API

### VPS（162.43.36.173）
- Ubuntu / Python cron jobs
- TimeTree 同期（Playwright）
- Plaud 議事録パイプライン
- daily_brief

---

## 📚 過去セッション履歴（archive）

`docs/sessions/` 配下のセッションアーカイブ:

| ファイル | 内容 |
|---|---|
| `20260518-1712-2732.md` | オルズグルポータル メディアダッシュボード実装 |
| `20260519-0854-75969.md` | 5/18 の継続 |
| `20260520-1051-D1final.md` | NocoDB → D1 大移行 |

新しいセッションは `/hikitsugi` で読み出し可能。

---

## 関連ドキュメント

- 📊 [skill-assessment.md](skill-assessment.md) — 実装力診断レポート
- 📅 [diary.html](diary.html) — インタラクティブ開発日記
- 🎯 [plan.json](plan.json) — 今後の強化計画データ

---

*このドキュメントは Claude Code が git log・メモリ・セッション履歴を横断的に分析して生成しました。
更新する場合: Claude セッションで「開発履歴をアップデート」と依頼してください。*
