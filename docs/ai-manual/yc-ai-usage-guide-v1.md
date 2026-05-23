# YC AI 利用マニュアル v1（前半）

> **対象**: YC 社内全員（オルズグル / 佐々生 / 山川 / 田貝 / みおり 等）
>
> **目的**: Claude を業務で使うときの **「うまく使い倒すための共通ルール」**
>
> **作成**: 2026-05-23 / 後半 (5/30) で具体例・落とし穴・テンプレ集を追加予定

---

## なぜ Claude？

YC では **「人間が判断・意思決定」+「Claude が実装・整理・調査」** の役割分担で動いている。
2026-04-23 〜 05-23 の 30 日間で **414 コミット中 414 件全部が Claude 協働**（実装力診断レポートより）。
これは「Claude なしの開発はもう非効率」というレベルに達している証拠。

ただし、**Claude を使えば自動的に成果が出る、ではない**。
使い方次第で「2 倍速」にも「2 倍遅い」にもなる。
このマニュアルはその差を埋めるためのガイド。

---

## Claude の 3 つの形態（YC で使っているもの）

| 形態 | 用途 | アクセス先 |
|---|---|---|
| **Claude.ai** | スマホ / ブラウザでの壁打ち・調査・文章作成 | claude.ai |
| **Claude Code (CLI)** | ターミナルでのコーディング・運用作業 | Mac の `claude` コマンド |
| **Claude API** | yc-bot / yc-line-webhook / Plaud パイプライン等の自動処理 | 各 Worker に組み込み |

このマニュアルは **主に Claude Code (CLI)** の使い方が中心。
スマホ Claude.ai のコツは [yc-dev-portal/diary.html](https://ycompany0909.github.io/yc-dev-portal/diary.html) の📊診断タブを参照。

---

## 1. 基本ルール

### 1-1. 最初に CLAUDE.md を読ませる

Claude Code は **セッション開始時に自動で CLAUDE.md を読む**:

- `~/.claude/CLAUDE.md` — グローバル（全リポジトリ共通）
- リポジトリ直下の `CLAUDE.md` — そのリポジトリ専用ルール

ユーザーが「CLAUDE.md を読んで」と言わなくても、Claude が起動時に自動で読む仕組み。
だから **CLAUDE.md にルールを書けば、次回以降の Claude セッションが自動で守る**。

⚠️ **逆に**: CLAUDE.md に書いてないルールは、Claude は知らない。「いつも『お客様』って言ってるじゃん」と思っても、CLAUDE.md に書いてなければ次のセッションでは「顧客」と言うかも。**ルールは文書化する**。

### 1-2. 「やってほしいこと」と「やってほしくないこと」を最初に言う

良い指示の例:
```
お客様の連絡先 CSV を D1 にインポートする処理を書いて。
ただし:
- 重複は (電話番号 + 氏名) でユニーク判定
- 既存レコードは上書きせず skip
- インポート結果を ✅ N件 / ❌ M件 で報告
```

悪い指示の例:
```
お客様の CSV インポート
```

→ Claude が「どう判定するの？上書きする？」を推測で進めて事故るリスク高い。
**最初に 3 行で要件を明示**するだけで品質激変。

### 1-3. 1 セッション 1 スコープ

同じセッションで「お客様 DB → シフト管理 → 朝会 → スタッフ給与」と話題を切り替えると、Claude が **過去の文脈を引きずって変な判断**をする。
**話題が変わるなら別セッション**を立ち上げる。

例外: 関連する作業（「シフト管理の続きで日報も触る」）は同セッションで OK。

### 1-4. 同じファイルを 2 セッションで触らない（並行セッション禁則）

ファイル単位で被ると事故る（2026-05-23 の preview バイパス混入事件）。
**「これから何を触る」を最初に明示**して、別セッションと被ったらどちらかが退く。

詳細: グローバル CLAUDE.md の「並行 Claude セッションの運用ルール」セクション。

---

## 2. スラッシュコマンド（slash skills）

`/` から始まる「呪文」で、よく使う操作を 1 アクションで起動できる。

### 2-1. 開発フロー系

| コマンド | 効果 |
|---|---|
| `/dev-check` | 開発環境を S/A/B/C/D 評価で診断（このマシン何点？） |
| `/env-check` | iCloud 経由で全マシン診断結果を比較 |
| `/loop` | 自律的反復タスク（指定条件まで Claude が繰り返す） |

### 2-2. コンテキスト系

| コマンド | 効果 |
|---|---|
| `/sync-context` | `yc-dev-portal/docs/context.md` を最新メモリ + CLAUDE.md で再生成 |
| `/hikitsugi` | 過去 Claude セッションの引き継ぎ宣言を読み上げ（番号・日付指定可） |
| `/push-tasks` | yc-dev-portal に残タスク push（旧仕様、plan.json に移行中） |

### 2-3. デプロイ系

`bash scripts/deploy-pages-with-smoke.sh` のような **スクリプト直叩きはもう不要**。
2026-05-23 以降は git push origin main で全自動デプロイ。詳細は ycompany-portal の CLAUDE.md。

### 2-4. 新しいコマンドを作る

`~/.claude/commands/your-command.md` を置けば即追加。Markdown で書いた手順を Claude が忠実に実行する。

例: `~/.claude/commands/jidai-daily.md`
```markdown
# JIDAI 日報サマリを取得する

1. wrangler d1 execute yc-shift-db --command "SELECT * FROM daily_reports WHERE store='JIDAI' ORDER BY date DESC LIMIT 7"
2. 過去 7 日の売上を集計
3. 前週との比較を表で示す
```

これで `/jidai-daily` と打てば毎日同じ手順を Claude が走らせる。

---

## 3. メモリ運用

### 3-1. メモリって何？

Claude Code はセッションを超えて記憶を持つ **「auto memory」** を持っている。
保存先: `~/.claude/projects/-Users-yosukesasaki/memory/`

### 3-2. 4 種類のメモリ

| 種類 | 内容 | 例 |
|---|---|---|
| **user** | ユーザーの役割・好み | 「オルズグルは Y COMPANY 代表」 |
| **feedback** | やめてくれ / 続けてくれ系のフィードバック | 「ユーザーに作業させない」 |
| **project** | 進行中プロジェクトの状態 | 「YC ポータルは D1 移行完了」 |
| **reference** | 外部システムへのポインタ | 「Linear の INGEST project にバグ管理」 |

### 3-3. メモリに刻むタイミング

- **ユーザーが「覚えておいて」と明示** → 即保存
- **失敗から学んだとき** → incident_*.md として保存
- **新しいプロジェクトを始めたとき** → project_*.md として保存
- **「これ毎回繰り返すな」と思うルール** → feedback_*.md として保存

### 3-4. メモリ vs CLAUDE.md の使い分け

| | メモリ | CLAUDE.md |
|---|---|---|
| **対象** | Claude 個人（私 = Opus 4.7）のセッション横断記憶 | 全 Claude セッション共通ルール |
| **編集** | Claude が自動で書く | 人間が手動で書く（Claude も提案する） |
| **配布** | Mac ローカル | git 管理・GitHub 経由で共有 |
| **何を書く** | 「失敗事例・好みの傾向」 | 「禁止事項・運用ルール・構成情報」 |

**新しいルールが見つかったら CLAUDE.md に書くのが正解**。
メモリだけだと別マシン・別 Claude では効かない。

---

## 4. コンテキストの渡し方

Claude.ai（スマホ）に質問するとき、**前提を一切共有せず話しかけても精度が出ない**。
コンテキストを渡す 3 つの方法:

### 4-1. yc-dev-portal の diary.html → コピペ

```
1. https://ycompany0909.github.io/yc-dev-portal/diary.html を開く
2. 📊 診断タブ or 📜 履歴 を眺める
3. 必要部分をコピー → Claude.ai に貼って質問
```

### 4-2. context.md を貼る（網羅型）

```
1. Claude Code で /sync-context を唱える
2. yc-dev-portal/docs/context.md が最新化される
3. Claude.ai の最初のメッセージに context.md 全文を貼る
4. その下に質問
```

### 4-3. 最小限テンプレ（軽量）

```
私は Y COMPANY 代表のオルズグル。
スタック: Cloudflare Workers (素のJS), D1, LINE API, GAS, Python
本番ポータル: portal.ycompany.co.jp
顧客呼称: お客様
---
[ここに質問]
```

これだけでも、ゼロから話すより 10 倍質が上がる。

---

## 5. 「これはやめて」リスト（よくある失敗）

| やめて | 理由 | 代わりに |
|---|---|---|
| 「いい感じで」「うまくやって」 | Claude が推測で進めて事故 | 要件を 3 行で明示 |
| 「とりあえず動くようにして」 | 動くだけの不安定コードが本番に | 「動く + テストパス + ログ出力」まで指定 |
| ファイルを全部見せずに「直して」 | Claude が知らない箇所を勝手に書き換え | Read で開いてから「ここを直して」と指示 |
| 同じことを 2 セッションで並行 | 競合事故（preview バイパス事件） | スコープ分けて開始時に明示 |
| 「お客様」じゃなく「顧客」と言う | YC 文化と乖離 | CLAUDE.md で統一済み・Claude も従う |
| ハードコードしたまま push | secret 漏えい | env.XXX 経由、env-master.md に登録 |

---

## 6. このマニュアルを更新するときは

- 新しい失敗事例があれば「5. これはやめて」リストに追加
- 新しいスラッシュコマンドが増えたら「2-1〜2-3」に追記
- 別バージョン (v2) が必要なほど大きく変わったら新ファイル

---

## 関連ドキュメント

- 🌐 [`~/.claude/CLAUDE.md`](https://github.com/ycompany0909/yc-dotfiles/blob/main/.claude/CLAUDE.md) — Claude グローバル指示（外部システム連携 / 並行セッション運用含む）
- 🔴 [ycompany-portal/CLAUDE.md](https://github.com/ycompany0909/ycompany-portal/blob/main/CLAUDE.md) — ycompany-portal 専用ルール
- 📊 [skill-assessment.md](../skill-assessment.md) — 実装力診断
- 📝 [eval/ai-output-eval-v1.md](../eval/ai-output-eval-v1.md) — AI 出力評価シート
- 🔑 [env/env-master.md](../env/env-master.md) — 環境変数マスター

---

*v1 前半 (1/2): 2026-05-23 作成. 後半 (5/30): 具体例・落とし穴・テンプレ集を追加予定*
*戦闘力ロードマップ: 94 → 94.5*
