# NocoDB テーブル設計 — 日本財団・助成金データベース

---

## テーブル構成

```
foundations（財団マスタ）
    └── grant_programs（助成プログラム）1:N
            └── issue_tags（社会課題タグ）M:N
```

---

## Table 1: foundations（財団マスタ）

| フィールド名 | 型 | 説明 | 例 |
|---|---|---|---|
| id | AutoNumber | PK | 1 |
| name | SingleLineText | 正式名称 | 公益財団法人 日本生命財団 |
| name_short | SingleLineText | 通称 | ニッセイ財団 |
| type | SingleSelect | 財団種別 | 企業財団 |
| parent_company | SingleLineText | 親会社（企業財団のみ） | 日本生命保険相互会社 |
| url | URL | 公式HP | https://nihonseimei-zaidan.or.jp/ |
| prefecture | SingleSelect | 所在都道府県 | 大阪府 |
| established_year | Number | 設立年 | 1979 |
| annual_grant_total_jpy | Currency | 年間助成総額（円） | 50000000 |
| contact_email | Email | 問い合わせメール | |
| contact_form_url | URL | 問い合わせフォーム | |
| access_type | SingleSelect | サイトアクセス種別 | gated / public / pdf_only / unknown |
| data_sources | MultiSelect | データ取得元 | 助成財団センター, CANPAN |
| last_scraped | Date | 最終取得日 | 2026-05-18 |
| notes | LongText | 備考 | 都道府県経由で申請受付 |
| action_required | SingleSelect | 要対応 | none / manual_check / phone_inquiry |

**type の選択肢:**
`企業財団` `民間財団` `日本財団系` `共同募金` `社会福祉協議会` `省庁・政府系` `地方自治体系` `その他`

---

## Table 2: grant_programs（助成プログラム）

| フィールド名 | 型 | 説明 | 例 |
|---|---|---|---|
| id | AutoNumber | PK | |
| foundation | LinkToAnotherRecord | foundations FK | |
| foundation_name | SingleLineText | 財団名（検索用） | 公益財団法人 日本生命財団 |
| program_name | SingleLineText | プログラム名 | 児童・少年の健全育成助成 |
| program_name_short | SingleLineText | 略称 | ニッセイ財団 児童健全育成 |
| fiscal_year | Number | 対象年度 | 2026 |
| description | LongText | 内容説明 | |
| target_org_types | MultiSelect | 対象団体種別 | NPO法人, 任意団体 |
| target_issues | MultiSelect | 対象社会課題（統一タグ） | 子ども・青少年 |
| target_regions | MultiSelect | 対象地域 | 全国, 東京都 |
| amount_min_jpy | Currency | 最低助成額 | 300000 |
| amount_max_jpy | Currency | 最高助成額 | 800000 |
| amount_note | SingleLineText | 金額補足 | 物品購入総額の6割以上 |
| deadline | Date | 締め切り | 2026-11-12 |
| deadline_type | SingleSelect | 締め切り種別 | annual / rolling / unknown |
| deadline_month_recurring | Number | 毎年の締め切り月 | 11 |
| application_method | SingleLineText | 申請方法 | 都道府県窓口経由 |
| requires_registration | Checkbox | マイページ登録要否 | false |
| requires_legal_entity | Checkbox | 法人格必須か | false |
| min_operation_years | Number | 最低活動年数 | 1 |
| adoption_rate_pct | Percent | 採択率 | |
| adoption_count_recent | Number | 直近採択件数 | |
| grant_url | URL | 助成ページURL | |
| pdf_url | URL | 要項PDF URL | |
| status | SingleSelect | 募集状況 | active / closed / upcoming / unknown |
| data_completeness | SingleSelect | データ完全性 | full / partial / minimal |
| notes | LongText | 備考 | |

**target_org_types の選択肢:**
`NPO法人` `認定NPO法人` `任意団体` `社会福祉法人` `一般社団法人` `公益社団法人` `学校法人` `医療法人` `個人` `企業` `大学・研究機関`

**target_issues の選択肢（統一タグ）:**
`子ども・青少年` `高齢者・介護` `障害者支援` `女性・ジェンダー` `外国人・多文化共生` `貧困・生活困窮` `教育・学習支援` `医療・保健` `環境・気候変動` `地域コミュニティ` `まちづくり` `農山漁村・地方創生` `文化・芸術` `スポーツ` `防災・減災` `国際協力` `人権・法的支援` `就労・雇用` `住まい` `食・フードバンク` `科学技術` `その他`

---

## Table 3: collection_log（収集ログ）

| フィールド名 | 型 | 説明 |
|---|---|---|
| id | AutoNumber | PK |
| foundation_name | SingleLineText | 財団名 |
| url | URL | 対象URL |
| access_status | SingleSelect | gated / public / error / not_found |
| bypass_result | SingleSelect | success / partial / failed |
| action_required | SingleSelect | none / manual_registration / phone_inquiry |
| partial_info | LongText | 部分取得情報（JSON） |
| scraped_at | DateTime | 取得日時 |

---

## NocoDB作成手順

### 1. 新しいBase作成
Base名: `YC Grant Database`

### 2. テーブル作成順序
1. `foundations` テーブルを作成
2. `grant_programs` テーブルを作成
3. `grant_programs.foundation` フィールドを `foundations` にリンク
4. `collection_log` テーブルを作成

### 3. CSVインポート
Manusの出力した `foundations_nocodb.csv` → foundationsテーブルにインポート
Manusの出力した `grant_programs_nocodb.csv` → grant_programsテーブルにインポート

### 4. ビュー作成（推奨）
- `foundations` — Galleryビュー：財団カード一覧
- `grant_programs` — カレンダービュー：締め切り管理
- `grant_programs` — Gridビュー：フィルタ＋ソート（issue別）
- `collection_log` — Gridビュー：要対応フィルタ

---

## データ量見込み

| テーブル | 見込み件数 |
|---|---|
| foundations | 1,500〜3,000件 |
| grant_programs | 3,000〜8,000件 |
| collection_log | 500〜1,000件（要対応分） |

---

*作成: 2026-05-18 / YC Grant Platform*
