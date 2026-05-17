# YC開発コンテキスト（2026-05-18 更新）

> このブロック全体をコピーして Claude.ai の最初のメッセージに貼ると、
> Claude Code Terminal での開発状況をそのまま引き継げます。

---

## 作業者・基本情報

- **担当**: オルズグル（Y COMPANY代表）
- **スタック**: Cloudflare Workers（素のJS）/ D1 / KV / NocoDB / LINE API / GAS / Python / VPS(Ubuntu)
- **店舗**: JIDAI（銀座・日報GAS稼働）/ IAPONIA（新橋）
- **ポータル**: portal.ycompany.co.jp
- **CF Account**: ycompany0909@gmail.com
- **重要ルール**:
  - Workers は TypeScript不使用（素のJS）
  - NocoDB API token は `(env.NOCODB_API_TOKEN || env.NOCODB_TOKEN)` の両受け
  - 外部メール送信時は ycompany0909@gmail.com を CC 必須
  - 顧客呼称は必ず「お客様」
  - 「スクショ見て」と言われたら `~/Downloads/` の最新PNGを必ず確認する

---

## 進行中プロジェクト

### オルズグル事務所ポータル（orzugul-portal）
- **本番URL**: https://portal.orzugul.com（DNS移行完了 2026-05-18）
- **リポジトリ**: ~/orzugul-portal/ （GitHub: ycompany0909/Setagaya-seiji）
- **スタック**: Vue3 + Vite + Tailwind / Cloudflare Workers (JS) + D1
- **DB**: D1 `orzugul-db`（ローカルは `server/data/orzugul.db`）
- **Worker**: orzugul-api.ycompany0909.workers.dev
- **Python venv**: `server/.venv/`（anthropic パッケージ入り）

#### 今セッションで完了した作業
1. **議事録ページ（Gijiroku.vue）**
   - ソースフィルタ（すべて / 📄議事録 / ⚡速報）バッジ追加
   - カードに要約表示（`summary || body.slice(0,120)`）
2. **データクリーンアップ（D1・ローカルDB両方完了）**
   - VOICESデータ(議事録)とCSVデータ(速報)の混在を解消
   - 重複CSV 5件削除、残CSV 14件を「速報」に再ラベル
   - 最終: 議事録93件 / 速報46件
3. **要約自動生成**
   - `server/generate_summaries.py`：全139件に要約生成（Claude Haiku）
   - プロンプト: 「〇〇について、〜課題を指摘し、〜求めた」形式（主語不要）
   - D1に同期済み
4. **タイトル全件再生成**
   - `server/generate_titles.py`：全139件を「〇〇について」形式に統一
   - D1に同期済み
5. **答弁補完**
   - `server/fix_missing_answers.py`：委員会セッションの答弁取得ロジック修正
   - 22件中13件の答弁を補完（残9件は採決発言のため答弁なしが正常）
   - D1に同期済み
6. **scrape_voices.py 改善**
   - 新規INSERTと同時に Claude Haiku で要約生成（ANTHROPIC_API_KEY があれば）
   - `source_type='議事録'` を明示的にセット

### Plaud ミーティングメモ パイプライン
- **状態**: 稼働中（VPS cron 毎時27分）
- **閲覧**: portal.ycompany.co.jp/meetings
- **残タスク**: 既存データ移管のみ未完了
- VPS: `/opt/yc-asakai/yc_plaud_pipeline.py`

### YC会計システム
- **状態**: データインポート・補正作業中（2026-05-16時点）

### ICJデモデイ
- **本番**: 2026-06-11
- **座組み**: 河内・大森・平野井

---

## 残タスク（orzugul-portal）

- [ ] VOICES令和8年データ掲載後にスクレイパーを再実行（速報46件の答弁補完）
- [ ] scrape_voices.py の答弁検出ロジック（last_idx以降も境界まで探索）を本体にもマージ

---

## 最近の決定・学び

- **VOICES vs CSV**: VOICESが常に正。日付フォーマットが異なるため自動dedup不可→手動整理
- **要約フォーマット**: 「オルズグル議員は〜」形式は不要。「〇〇について、〜」で統一
- **委員会答弁のバグ**: extract_qa_pairs がオルズグルの最後発言より後の答弁を取れていなかった。fix_missing_answers.py で修正
- **API Key**: ANTHROPIC_API_KEY はどのAnthropicキーでも可

---

## 主要システムURL

| サービス | URL |
|---|---|
| YCポータル（ミーティング） | portal.ycompany.co.jp/meetings |
| オルズグルポータル | portal.orzugul.com |
| orzugul-api Worker | orzugul-api.ycompany0909.workers.dev |
| dev-portal | ycompany0909.github.io/yc-dev-portal |

---

## ファイルパス早見表

| 用途 | パス |
|---|---|
| orzugul-portal ローカル | ~/orzugul-portal/ |
| Vue ポータル | ~/orzugul-portal/client/src/views/ |
| Worker | ~/orzugul-portal/worker/src/index.js |
| ローカルDB | ~/orzugul-portal/server/data/orzugul.db |
| 要約生成スクリプト | ~/orzugul-portal/server/generate_summaries.py |
| タイトル生成スクリプト | ~/orzugul-portal/server/generate_titles.py |
| 答弁補完スクリプト | ~/orzugul-portal/server/fix_missing_answers.py |
| VOICESスクレイパー | ~/orzugul-portal/server/scrape_voices.py |
| Python venv | ~/orzugul-portal/server/.venv/ |
