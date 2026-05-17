# 日本全財団・助成金 悉皆調査プロンプト v2
# Manus / Genspark 用（Deep Research反映版）

**v1からの主な変更点：**
- J-Grants 公開APIをPriority Sとして最優先化
- 内閣府NPOポータル一括DLを追加
- 採択実績データの収集を全財団に展開
- 財団数の見込みを2,539団体・8,091プログラムに更新
- 財団レピュテーション収集ルートを追加

---

## ミッション

日本国内の全助成財団・企業財団・共同募金・行政補助金を網羅的に収集し、以下のJSONスキーマに従って構造化データとして出力してください。

最終成果物：
- `foundations.json` — 財団マスタ（目標2,500件以上）
- `grant_programs.json` — 助成プログラム詳細（目標8,000件以上）
- `adoption_records.json` — 採択実績データ（取得できた分のみ）
- `reputation_signals.json` — 評判・実態データ（公開情報から収集）
- `collection_log.json` — 収集状況ログ

---

## 調査ソース（優先順位順）

### 【Priority S】API・一括DL（最優先・クレジット消費最小）

**必ずここから着手すること。**

**1. J-Grants 公開API（行政補助金）**
```
エンドポイント確認: https://www.jgrants-portal.go.jp/
APIドキュメント: デジタル庁が提供
取得対象: 府省庁・地方自治体の補助金・交付金
取得フィールド: 公募名・交付要綱・申請様式・締め切り・対象
出力: 全件JSON取得後にスキーマに変換
```

**2. 内閣府NPOポータル 一括ダウンロード（NPOマスタ）**
```
URL: https://www.npo-homepage.go.jp/
一括DL機能でNPO法人の事業報告書・財務データを取得
取得対象: 認定NPO法人の助成金収入・寄付収入・財務情報
→ 「どのNPOがどの財団から助成を受けているか」の逆引きデータになる
```

---

### 【Priority A】構造化データベース（全件必須取得）

**3. 助成財団センター「助成・奨学金情報navi」**
```
URL: https://jyosei-navi.jfc.or.jp/
実態: 2,539団体・8,091プログラム（2023年データベース調査値）
  - NPO・市民団体向け: 451団体・727プログラム
  - 研究者・個人向け: 2,539団体・8,091プログラム（全体）
全ページネーションを辿って全件取得すること
会員名簿ページ(https://www.jfc.or.jp/whatis/member/)も取得
```

**4. CANPAN助成制度一覧**
```
URL: https://fields.canpan.info/grant/
特徴: 主に全国規模の制度が中心
全カテゴリ・全地域パターンで全件取得
```

**5. 補助金ポータル（NPO・社会福祉フィルタ）**
```
URL: https://hojyokin-portal.jp/subsidies/list
NPO法人フィルタ・社会福祉法人フィルタで全件取得
```

---

### 【Priority B】採択実績公開財団（高価値・集中取得）

以下の財団は採択実績データを公開しており、マッチング精度向上に直結する。
**優先して詳細データを構造化すること。**

**6. トヨタ財団**
```
URL: https://www.toyotafound.or.jp/
取得対象: 
  - 助成プログラム一覧・要項
  - 「活動紹介」ページの過去採択案件（検索可能）
  - 採択団体名・プロジェクト名・金額・年度・課題領域
```

**7. 住友財団**
```
URL: https://www.sumitomo.or.jp/
取得対象:
  - 募集要項・申請書フォーム
  - 採択者リスト（公開）
  - 年度別・課題別採択パターン
```

**8. パナソニック教育財団**
```
URL: https://www.pef.or.jp/
取得対象:
  - 2026年度: 応募224件・助成69件（採択率30.8%）を含む全年度データ
  - 助成先一覧・助成プロジェクト詳細
  - 採択率推移
```

**9. 三菱財団**
```
URL: https://www.mitsubishi-zaidan.jp/
```

**10. 日本財団**
```
URL: https://nippon-foundation.my.site.com/GrantPrograms/s/
```

**11. 笹川平和財団・笹川スポーツ財団**
**12. 公益財団法人 中央競馬馬主社会福祉財団**
**13. 朝日新聞文化財団**
**14. 読売新聞教育文化財団**

---

### 【Priority C】個別財団HP直接巡回

Priority A・Bで取得した財団リストを元に、各財団の公式HPを個別巡回する。
各財団HPで以下を探す：
- 「助成」「支援」「応募」「公募」「申請」のナビゲーション
- 最新年度の助成要項PDF
- 過去の採択事例・受賞者一覧・年次報告書

---

### 【Priority D】ゲート（マイページ登録必須）サイトの迂回戦略

財団HPでマイページ登録が必要な場合、以下の順で代替情報源を探す：

**迂回ルートA：都道府県・市区町村経由（最重要）**
```
検索クエリ: "[財団名] 助成金 申請 2026 site:pref.*.jp OR site:city.*.jp"
例: "ニッセイ財団 助成金 申請 2026 site:pref.shizuoka.jp"
→ 都道府県が財団の申請窓口・要項転載をしているケースが多い
```

**迂回ルートB：CANPAN・助成財団センターの掲載情報**

**迂回ルートC：NPO支援センター・社会福祉協議会HP**
```
検索クエリ: "[財団名] 助成 募集 要項 NPO支援"
```

**迂回ルートD：プレスリリース・PDF直接検索**
```
検索クエリ: "[財団名] 助成 要項 filetype:pdf 2026"
```

**全ルート失敗時：** `collection_log.json` に記録して次へ

---

### 【Priority E】評判・実態データ収集（差別化の核）

**公開情報から財団の評判・実態シグナルを収集する。**

**15. NPOコミュニティの発信情報**
```
収集対象:
  - note.com での「助成金 申請してみた」「○○財団 採択」記事
  - NPO関係者ブログでの財団評価記事
  - Twitter/X での「○○財団 助成金」の言及
  
収集シグナル:
  - 申請のしやすさ（様式・要件の明確さ）
  - 対応・返答速度
  - 落選時のフィードバックの有無
  - 報告義務の重さ
  - 「また申請したい」「もう申請しない」の感情
```

**16. 採択実績の逆引き（NPO側からの取得）**
```
方法1: 内閣府NPOポータルのNPO事業報告書から「助成金収入」の財団名を抽出
方法2: NPO法人HPの「活動報告」「助成金一覧」ページから取得
  検索クエリ: "○○財団 助成 採択 site:npo法人ドメイン"
方法3: CANPANのNPOプロフィールページに記載された助成実績
方法4: プレスリリース「○○財団より助成金をいただきました」パターン
  検索クエリ: "[財団名] より助成 採択 いただきました"
```

**17. 財団の実態と建前のギャップ検出**
```
手法: 採択実績データ（Priority B・Eで収集）と
      公式の「対象課題」を照合
→ 「環境問題」と言いながら採択の80%が「子ども支援」→ 乖離あり
→ この乖離情報がマッチング精度の差別化になる
```

---

## 出力スキーマ

### foundations.json
```json
[
  {
    "id": "連番",
    "name": "公益財団法人 日本生命財団",
    "name_short": "ニッセイ財団",
    "type": "企業財団",
    "parent_company": "日本生命保険相互会社",
    "url": "https://nihonseimei-zaidan.or.jp/",
    "prefecture": "大阪府",
    "established_year": 1979,
    "annual_grant_total_jpy": 50000000,
    "contact_email": null,
    "contact_form_url": null,
    "access_type": "gated|public|pdf_only|unknown",
    "adoption_data_public": true,
    "data_sources": ["助成財団センター", "CANPAN", "HP直接"],
    "last_scraped": "2026-05-18",
    "notes": ""
  }
]
```

### grant_programs.json
```json
[
  {
    "id": "連番",
    "foundation_id": "財団id",
    "foundation_name": "公益財団法人 日本生命財団",
    "program_name": "児童・少年の健全育成助成（物品助成）",
    "fiscal_year": 2026,
    "description": "内容説明",
    "target_org_types": ["任意団体", "NPO法人"],
    "target_issues": ["子ども・青少年"],
    "target_regions": ["全国"],
    "amount_min_jpy": 300000,
    "amount_max_jpy": 800000,
    "amount_note": "",
    "deadline": "2026-11-12",
    "deadline_type": "annual|rolling|unknown",
    "deadline_month_recurring": 11,
    "application_method": "都道府県窓口経由",
    "requires_registration": false,
    "requires_legal_entity": false,
    "min_operation_years": 1,
    "total_applicants_recent": null,
    "total_adopted_recent": null,
    "adoption_rate_pct": null,
    "grant_url": "https://...",
    "pdf_url": "https://...",
    "status": "active|closed|unknown",
    "data_completeness": "full|partial|minimal",
    "notes": ""
  }
]
```

### adoption_records.json（新規）
```json
[
  {
    "id": "連番",
    "foundation_id": "財団id",
    "program_id": "プログラムid",
    "fiscal_year": 2025,
    "grantee_name": "NPO法人 ○○",
    "grantee_org_type": "NPO法人|任意団体|社会福祉法人|その他",
    "project_title": "プロジェクト名",
    "project_description": "概要",
    "amount_jpy": 1000000,
    "target_issues": ["子ども・青少年"],
    "target_region": "東京都",
    "source_url": "https://...",
    "data_source": "財団HP|年次報告書PDF|CANPAN|NPOポータル",
    "notes": ""
  }
]
```

### reputation_signals.json（新規）
```json
[
  {
    "id": "連番",
    "foundation_id": "財団id",
    "signal_type": "npo_blog|note|twitter|press_release|interview",
    "source_url": "https://...",
    "published_date": "2025-03-01",
    "sentiment": "positive|neutral|negative|mixed",
    "topics": ["申請のしやすさ", "対応速度", "報告負担"],
    "key_quotes": "実際の申請者の言葉（直接引用）",
    "notes": ""
  }
]
```

---

## 社会課題タグ（統一分類）
```
子ども・青少年 / 高齢者・介護 / 障害者支援 / 女性・ジェンダー /
外国人・多文化共生 / 貧困・生活困窮 / 教育・学習支援 / 医療・保健 /
環境・気候変動 / 地域コミュニティ / まちづくり / 農山漁村・地方創生 /
文化・芸術 / スポーツ / 防災・減災 / 国際協力 / 人権・法的支援 /
就労・雇用 / 住まい / 食・フードバンク / 科学技術 / その他
```

---

## 実行順序

```
Step 1: J-Grants API → 行政補助金を全件JSON取得
Step 2: 内閣府NPOポータル一括DL → NPO財務・助成金収入データ取得
Step 3: 助成財団センター 会員名簿 → 全財団URL一覧（骨格構築）
Step 4: CANPAN・補助金ポータル 全件取得
Step 5: Priority B財団（トヨタ・住友・パナソニック等）を個別詳細取得
         → 助成プログラム詳細 + 採択実績データを構造化
Step 6: Priority C 全財団HP個別巡回（Priority A・Bで得たURLリスト）
Step 7: ゲート財団は迂回ルートA→B→C→Dで代替取得
Step 8: Priority E 評判データ収集
         → note/ブログ/X検索で各財団の評判シグナルを収集
         → NPO事業報告書から逆引き採択実績を追加
Step 9: 全データ統合・重複排除・スキーマ変換
Step 10: 4ファイルを出力 + NocoDB用CSV変換
```

---

## 品質基準

| completeness | 条件 | 目標比率 |
|---|---|---|
| full | 財団名・URL・金額・締め切り・対象・要件が全て揃い、採択実績あり | 30%以上 |
| partial | 財団名・URL・概要は取得済み、金額・締め切りは不明 | 50%程度 |
| minimal | 財団名・URLのみ | 20%以下 |

---

## 重要注意事項

1. **J-Grants APIを最初に叩く**（クレジット消費なし・最も確実）
2. **同一財団の重複排除**：複数ソースの情報をマージして1件にする
3. **年度を必ず明記**：2025年度募集中・2026年度予定・不明 を区別
4. **金額は円単位整数**：「100万円」→ `1000000`
5. **締め切りはISO 8601**：`2026-11-30`
6. **評判データは直接引用**：要約ではなく元の言葉をそのまま `key_quotes` に
7. **ゲートサイトに個人情報を登録しない**
8. **採択実績は年度を必ず付記**（古いデータと新しいデータを混在させない）

---

## NocoDB インポート用CSV出力

以下の4ファイルをUTF-8 BOM付きCSVでも出力：
- `foundations_nocodb.csv`
- `grant_programs_nocodb.csv`
- `adoption_records_nocodb.csv`
- `reputation_signals_nocodb.csv`

---

## 期待値

| データ種別 | 目標件数 |
|---|---|
| foundations | 2,500件以上 |
| grant_programs | 8,000件以上 |
| adoption_records | 5,000件以上（公開財団から） |
| reputation_signals | 200件以上 |

---

*作成: 2026-05-18 / YC Grant Platform 悉皆調査 Phase 2*
*前提: deepresearch_prompt_v1.md の調査結果を反映*
