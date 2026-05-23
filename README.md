# yc-dev-portal

スマホ壁打ち用 GitHub Pages ダッシュボード + 開発記録・診断・強化計画の中央リポジトリ。

## 🔗 公開

- **ダッシュボード（メイン）**: https://ycompany0909.github.io/yc-dev-portal/diary.html
- **トップ**: https://ycompany0909.github.io/yc-dev-portal/
- **GitHub**: https://github.com/ycompany0909/yc-dev-portal

---

## 何のためのリポジトリ？

1. **スマホからの壁打ち** — 移動中に Claude.ai で開発相談するとき、ここを開けば最新コンテキストが取れる
2. **開発履歴の年表** — git log や session を横断して時系列で記録（dev-history.md）
3. **実装力の自己診断** — 定期的に skill-assessment.md を更新して成長を可視化
4. **エンジニア力強化計画** — plan.json + diary.html の「🎯 強化計画」タブで未来のマイルストーンを管理
5. **環境変数・データ分類のマスター** — 全システムの env / D1 分類を一元管理

---

## ディレクトリ構造

```
yc-dev-portal/
├── docs/                           ← GitHub Pages のソース（main の /docs フォルダ）
│   ├── index.html                  トップダッシュボード（プロジェクト一覧入口）
│   ├── diary.html                  ★ メインの開発日記（4タブ: 📅カレンダー / 📝メモ / 🎯強化計画 / 📊診断）
│   │
│   ├── plan.json                   エンジニア力強化計画のマイルストーン
│   ├── context.md                  /sync-context で生成される Claude.ai 用コンテキスト
│   │
│   ├── dev-history.md              開発履歴年表（4/30〜現在）
│   ├── skill-assessment.md         実装力診断レポート（評価軸ベース）
│   ├── battle-power-report-*.md    戦闘力変化レポート（外部評価）
│   │
│   ├── eval/
│   │   └── ai-output-eval-v1.md    AI 出力評価シート（5 観点 × 5 段階）
│   ├── env/
│   │   └── env-master.md           環境変数マスター（51 secrets + bindings 棚卸し）
│   ├── data/
│   │   └── data-classification-v1.md  D1 64 テーブルの分類表
│   │
│   ├── sessions/                   過去 Claude セッションの引き継ぎ markdown
│   ├── memos.json                  旧メモ機能のデータ（現在は localStorage に移行）
│   ├── tasks.json                  旧残タスク機能のデータ
│   ├── grant-search.html / npo.html / map.html  用途別サブページ
│   └── ...
│
├── CLAUDE.md                       このリポジトリで作業する際の Claude セッション用ルール
└── README.md                       このファイル
```

---

## diary.html の 4 タブ（メイン UI）

| タブ | データソース | 機能 |
|---|---|---|
| 📅 **カレンダー** | `DIARY` ハードコード（過去）+ `plan.json`（未来） | 月単位ナビ、過去履歴と強化計画イベントを併記 |
| 📝 **メモ** | `localStorage` (yc_quick_memos) | クイック雑記。タイムスタンプ付き、端末ローカル保存のみ |
| 🎯 **強化計画** | `plan.json` | エンジニア力強化マイルストーン一覧 |
| 📊 **診断** | `skill-assessment.md` を fetch + marked.js で render | 実装力診断レポート表示 |

---

## メインドキュメント

| ファイル | 用途 |
|---|---|
| 📊 [skill-assessment.md](docs/skill-assessment.md) | 実装力診断レポート — 5 軸スコアと強み・成長余地 |
| 📜 [dev-history.md](docs/dev-history.md) | 開発履歴年表 — 4/30〜現在の時系列記録 |
| 🎯 [plan.json](docs/plan.json) | 強化計画 — 5/24〜7/5 の 19 マイルストーン |
| 🔑 [env-master.md](docs/env/env-master.md) | 環境変数マスター — 全システム横断棚卸し |
| 🛡 [data-classification-v1.md](docs/data/data-classification-v1.md) | D1 データ分類 — 64 テーブル × 4 軸 |
| 📝 [ai-output-eval-v1.md](docs/eval/ai-output-eval-v1.md) | AI 出力評価シート — 5 観点 × 5 段階 |

---

## 更新方法

### diary.html / 静的ドキュメント

```bash
cd ~/Code/yc-dev-portal
vim docs/xxx.md          # 編集
git add docs/xxx.md
git commit -m "..."
git push origin main
# → 数分で GitHub Pages に反映
```

### plan.json への追加（強化計画にマイルストーン追加）

```bash
# docs/plan.json の "plans" 配列に追記
{
  "date": "2026-MM-DD",
  "type": "learning",  # learning / practice / milestone
  "title": "...",
  "detail": "..."
}
git add docs/plan.json && git commit -m "plan: xxx" && git push
# → カレンダー & 強化計画タブに即反映
```

### Claude スキルからの自動更新

| スキル | 効果 |
|---|---|
| `/sync-context` | `docs/context.md` を最新メモリ + CLAUDE.md で再生成 |
| `/push-tasks` | `docs/tasks.json` を更新（廃止予定、現在は plan.json に統合中） |
| `/hikitsugi` | `docs/sessions/` のアーカイブを読み出して引き継ぎ宣言 |

---

## スマホ壁打ちフロー

```
1. スマホで https://ycompany0909.github.io/yc-dev-portal/diary.html を開く
2. 📊 診断タブで現状把握、🎯 強化計画タブで進捗確認
3. Claude.ai を開いて、見たいタブの内容をコピペ → 質問
   (または context.md の内容を貼り付けて全体文脈を共有)
```

---

## 関連リポジトリ

| リポジトリ | 関係 |
|---|---|
| [ycompany-portal](https://github.com/ycompany0909/ycompany-portal) | **本体システム**。yc-dev-portal はその開発状況を記録 |
| [orzugul-portal](https://github.com/ycompany0909/orzugul-portal) | 別ドメイン（政治活動）。開発履歴は dev-history.md に記録 |
| [yc-dotfiles](https://github.com/ycompany0909/yc-dotfiles) | 開発環境セットアップ |

---

## 戦闘力ロードマップ（2026-05-23 開始）

`plan.json` 駆動の 5/24〜7/5 計画:
- Week 1 (5/24-30): 文書化スプリント → **93-94pt**
- Week 2-3 (5/31-6/13): テンプレ＆秘書スプリント → **96-97pt**
- Week 4-6 (6/14-7/5): 外販フェーズ → **100pt 突破**

詳細: [diary.html](https://ycompany0909.github.io/yc-dev-portal/diary.html) の「🎯 強化計画」タブ
