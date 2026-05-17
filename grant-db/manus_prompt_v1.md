# 日本全財団・助成金 悉皆調査プロンプト v1
# Manus / Genspark 用

---

## ミッション

日本国内の全ての助成財団・企業財団・共同募金・公益法人が実施する助成プログラムを網羅的に収集し、以下のJSONスキーマに従って構造化データとして出力してください。

最終成果物：
- `foundations.json` — 財団マスタ
- `grant_programs.json` — 助成プログラム詳細
- `collection_log.json` — 収集状況ログ（アクセス不可・要確認を含む）

---

## 調査対象の定義

以下を全て対象とする：
- 公益財団法人（民間財団）
- 企業財団（トヨタ財団・三菱財団・住友財団 等）
- 共同募金（赤い羽根含む）
- 日本財団・笹川系財団
- 省庁・地方自治体が運営する助成基金
- 社会福祉協議会の助成事業
- 労働局・厚生労働省系助成金（雇用・福祉系）

---

## 調査ソース（優先順位順）

### 【Priority 1】構造化データベース（必ず全件取得）

1. **助成財団センター「助成・奨学金情報navi」**
   - URL: https://jyosei-navi.jfc.or.jp/
   - 民間財団向け: https://jyosei-navi.jfc.or.jp/search/search/assist/list
   - 研究者向けも取得する
   - 全ページネーションを辿って全件取得すること

2. **CANPAN 助成制度一覧**
   - URL: https://fields.canpan.info/grant/
   - カテゴリ・地域絞り込みを全パターン試して全件取得

3. **補助金ポータル（NPO・社会福祉法人フィルタ）**
   - URL: https://hojyokin-portal.jp/subsidies/list?core_tag_id[0]=227
   - 全カテゴリを巡回

4. **日本財団助成ポータル**
   - URL: https://nippon-foundation.my.site.com/GrantPrograms/s/

5. **助成財団センター 会員名簿**
   - URL: https://www.jfc.or.jp/whatis/member/
   - 全財団名・URLをリスト化してから個別巡回

### 【Priority 2】個別財団HP直接調査

Priority 1 で取得した財団リストを元に、各財団の公式HPを個別に巡回する。

各財団HPで以下を探す：
- 「助成」「支援」「応募」「公募」「申請」のナビゲーション
- 最新年度の助成要項PDF
- 過去の採択事例・受賞者一覧

### 【Priority 3】ゲート（マイページ登録必須）サイトの迂回戦略

財団HPでマイページ登録が必要な場合、以下の順で代替情報源を探す：

**迂回ルート A：都道府県・市区町村経由**
```
検索クエリ: "[財団名] 助成金 申請 2025 site:pref.*.jp OR site:city.*.jp"
例: "ニッセイ財団 助成金 申請 2025 site:pref.shizuoka.jp"
→ 都道府県が財団の申請窓口になっているケースが多い
→ 要項PDFが自治体HPにアップされている
```

**迂回ルート B：CANPAN・助成財団センターの掲載情報**
```
同財団がCANPANや助成財団センターに登録している場合、
そちらに詳細情報が公開されていることが多い
```

**迂回ルート C：NPO支援センター・社会福祉協議会HP**
```
検索クエリ: "[財団名] 助成 募集 要項"
→ 支援団体が転載していることがある
```

**迂回ルート D：プレスリリース・PDF直接検索**
```
検索クエリ: "[財団名] 助成 要項 filetype:pdf 2025"
→ 申請要項PDFが直接ダウンロード可能な場合がある
```

**上記全て失敗した場合：**
`collection_log.json` に以下を記録して次へ進む：
```json
{
  "foundation_name": "○○財団",
  "url": "https://...",
  "access_status": "gated",
  "bypass_attempted": ["prefecture", "canpan", "npo_center", "pdf"],
  "bypass_result": "failed",
  "action_required": "manual_registration",
  "partial_info": { "取得できた情報があればここに" }
}
```

---

## 出力スキーマ

### foundations.json

```json
[
  {
    "id": "uuid または連番",
    "name": "公益財団法人 日本生命財団",
    "name_short": "ニッセイ財団",
    "type": "企業財団",
    "parent_company": "日本生命保険相互会社",
    "url": "https://nihonseimei-zaidan.or.jp/",
    "prefecture": "大阪府",
    "established_year": 1979,
    "annual_grant_total_jpy": 50000000,
    "annual_grant_total_note": "概算・不明な場合はnull",
    "contact_email": null,
    "contact_form_url": "https://...",
    "access_type": "gated|public|pdf_only|unknown",
    "data_sources": ["助成財団センター", "CANPAN", "HP直接"],
    "last_scraped": "2026-05-18",
    "notes": "都道府県経由で申請受付。マイページ登録不要で要項取得可能"
  }
]
```

### grant_programs.json

```json
[
  {
    "id": "uuid または連番",
    "foundation_id": "財団のid",
    "foundation_name": "公益財団法人 日本生命財団",
    "program_name": "児童・少年の健全育成助成（物品助成）",
    "program_name_short": "ニッセイ財団 児童健全育成",
    "fiscal_year": 2026,
    "description": "18歳未満の児童・少年の健全育成活動に取り組む民間団体への物品購入助成",
    "target_org_types": ["任意団体", "NPO法人", "社会福祉法人"],
    "target_issues": ["子ども・青少年", "地域コミュニティ"],
    "target_regions": ["全国", "都道府県ごとに窓口あり"],
    "amount_min_jpy": 300000,
    "amount_max_jpy": 800000,
    "amount_note": "物品購入総額の6割以上",
    "deadline": "2026-11-12",
    "deadline_type": "annual|rolling|unknown",
    "deadline_month_recurring": 11,
    "application_method": "都道府県窓口経由",
    "requires_registration": false,
    "requires_legal_entity": false,
    "min_operation_years": 1,
    "adoption_rate_pct": null,
    "adoption_count_recent": null,
    "grant_url": "https://nihonseimei-zaidan.or.jp/jidou/index.html",
    "pdf_url": "https://nihonseimei-zaidan.or.jp/jidou/pdf/h30_tetsuduki_youryou.pdf",
    "status": "active|closed|unknown",
    "data_completeness": "full|partial|minimal",
    "notes": ""
  }
]
```

### collection_log.json

```json
[
  {
    "foundation_name": "○○財団",
    "url": "https://...",
    "access_status": "gated|public|error|not_found",
    "bypass_attempted": [],
    "bypass_result": "success|failed|partial",
    "action_required": "none|manual_registration|phone_inquiry",
    "partial_info": {}
  }
]
```

---

## 社会課題タグ（統一分類）

以下のタグを使って `target_issues` を分類する（複数選択可）：

```
子ども・青少年
高齢者・介護
障害者支援
女性・ジェンダー
外国人・多文化共生
貧困・生活困窮
教育・学習支援
医療・保健
環境・気候変動
地域コミュニティ
まちづくり・都市再生
農山漁村・地方創生
文化・芸術
スポーツ・余暇
防災・減災
国際協力・開発
人権・法的支援
就労・雇用
住まい・ホームレス支援
食・フードバンク
科学技術・イノベーション
その他
```

---

## 実行順序

```
Step 1: 助成財団センター 会員名簿 → 全財団名・URL一覧を取得（財団マスタの骨格）
Step 2: CANPAN 全件取得 → 助成プログラム一覧（財団マスタと突合）
Step 3: 補助金ポータル 全件取得 → 政府系・自治体系を補完
Step 4: 日本財団ポータル 全件取得
Step 5: 上記で得た全財団URLを個別巡回（公開ページから詳細取得）
Step 6: ゲート財団は迂回ルートA→B→C→Dで代替取得
Step 7: 全データをスキーマに合わせて構造化・重複排除
Step 8: collection_log に取得状況を記録
Step 9: foundations.json / grant_programs.json / collection_log.json を出力
```

---

## 品質基準

- `data_completeness: "full"` = 財団名・URL・助成金額・締め切り・対象・要件が全て揃っている
- `data_completeness: "partial"` = 財団名・URL・概要は取得済み、金額・締め切りは不明
- `data_completeness: "minimal"` = 財団名・URLのみ

全件のうち `full` が50%以上になることを目標とする。

---

## 重要な注意事項

1. **同一財団の重複排除**：複数ソースに同じ財団が登場した場合、情報をマージして1件にする
2. **年度の明記**：2025年度募集中・2026年度予定・不明 を必ず区別する
3. **金額は円単位の整数**：「100万円」→ `1000000`
4. **締め切りはISO 8601形式**：`2026-11-30`
5. **PDFは可能な限りダウンロードしてテキスト抽出**して構造化する
6. **ゲートサイトに個人情報を登録しない**：迂回ルートで対応する

---

## NocoDB インポート形式

最終出力は NocoDB の CSV インポートに対応する形式でも出力すること：
- `foundations_nocodb.csv`
- `grant_programs_nocodb.csv`

UTF-8 BOM付き、ヘッダー行あり。

---

*作成: 2026-05-18 / YC Grant Platform 悉皆調査 Phase 1*
