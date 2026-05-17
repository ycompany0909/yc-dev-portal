# NocoDB テーブル設計 v2 — 日本財団・助成金データベース
# Deep Research反映版

---

## テーブル構成（v1から2テーブル追加）

```
foundations（財団マスタ）
    └── grant_programs（助成プログラム）1:N
            └── adoption_records（採択実績）1:N  ← NEW
foundations
    └── reputation_signals（評判シグナル）1:N    ← NEW
```

---

## Table 1: foundations（財団マスタ）※v1から変更あり

| フィールド名 | 型 | 説明 |
|---|---|---|
| id | AutoNumber | PK |
| name | SingleLineText | 正式名称 |
| name_short | SingleLineText | 通称 |
| type | SingleSelect | 企業財団/民間財団/日本財団系/共同募金/省庁系/自治体系/その他 |
| parent_company | SingleLineText | 親会社（企業財団のみ） |
| url | URL | 公式HP |
| prefecture | SingleSelect | 所在都道府県 |
| established_year | Number | 設立年 |
| annual_grant_total_jpy | Currency | 年間助成総額（円） |
| contact_email | Email | 問い合わせメール |
| contact_form_url | URL | 問い合わせフォーム |
| access_type | SingleSelect | public/gated/pdf_only/unknown |
| adoption_data_public | Checkbox | 採択実績を公開しているか ← NEW |
| reputation_score | Rating | 評判スコア（1-5）← NEW・後から入力 |
| data_sources | MultiSelect | データ取得元 |
| last_scraped | Date | 最終取得日 |
| action_required | SingleSelect | none/manual_check/phone_inquiry |
| notes | LongText | 備考 |

---

## Table 2: grant_programs（助成プログラム）※v1から変更あり

| フィールド名 | 型 | 説明 |
|---|---|---|
| id | AutoNumber | PK |
| foundation | LinkToAnotherRecord | foundations FK |
| foundation_name | SingleLineText | 財団名（検索用） |
| program_name | SingleLineText | プログラム名 |
| program_name_short | SingleLineText | 略称 |
| fiscal_year | Number | 対象年度 |
| description | LongText | 内容説明 |
| target_org_types | MultiSelect | 対象団体種別 |
| target_issues | MultiSelect | 対象社会課題（統一タグ） |
| target_regions | MultiSelect | 対象地域 |
| amount_min_jpy | Currency | 最低助成額 |
| amount_max_jpy | Currency | 最高助成額 |
| amount_note | SingleLineText | 金額補足 |
| deadline | Date | 締め切り |
| deadline_type | SingleSelect | annual/rolling/unknown |
| deadline_month_recurring | Number | 毎年の締め切り月 |
| application_method | SingleLineText | 申請方法 |
| requires_registration | Checkbox | マイページ登録要否 |
| requires_legal_entity | Checkbox | 法人格必須か |
| min_operation_years | Number | 最低活動年数 |
| total_applicants_recent | Number | 直近応募件数 ← NEW |
| total_adopted_recent | Number | 直近採択件数 ← NEW |
| adoption_rate_pct | Percent | 採択率（自動計算 or 入力）← NEW |
| grant_url | URL | 助成ページURL |
| pdf_url | URL | 要項PDF URL |
| status | SingleSelect | active/closed/upcoming/unknown |
| data_completeness | SingleSelect | full/partial/minimal |
| notes | LongText | 備考 |

---

## Table 3: adoption_records（採択実績）← NEW

| フィールド名 | 型 | 説明 | 例 |
|---|---|---|---|
| id | AutoNumber | PK | |
| foundation | LinkToAnotherRecord | foundations FK | |
| grant_program | LinkToAnotherRecord | grant_programs FK | |
| foundation_name | SingleLineText | 財団名（検索用） | トヨタ財団 |
| program_name | SingleLineText | プログラム名 | 国際助成プログラム |
| fiscal_year | Number | 助成年度 | 2025 |
| grantee_name | SingleLineText | 被助成団体名 | NPO法人○○ |
| grantee_org_type | SingleSelect | NPO法人/任意団体/社会福祉法人/大学/個人/その他 | NPO法人 |
| project_title | SingleLineText | プロジェクト名 | |
| project_description | LongText | 概要 | |
| amount_jpy | Currency | 助成額 | |
| target_issues | MultiSelect | 対象課題タグ | |
| target_region | SingleLineText | 対象地域 | 東京都 |
| source_url | URL | 情報源URL | |
| data_source | SingleSelect | 財団HP/年次報告書PDF/CANPAN/NPOポータル/NPO自己発信 | |
| notes | LongText | 備考 | |

**このテーブルの用途：**
- 「○○財団はどんな団体を採択しているか」のパターン分析
- NPOの「どの財団から過去に助成を受けたか」の実績照合
- 建前の対象課題 vs 実際の採択傾向のギャップ検出
- マッチングアルゴリズムの学習データ

---

## Table 4: reputation_signals（評判シグナル）← NEW

| フィールド名 | 型 | 説明 | 例 |
|---|---|---|---|
| id | AutoNumber | PK | |
| foundation | LinkToAnotherRecord | foundations FK | |
| foundation_name | SingleLineText | 財団名（検索用） | |
| signal_type | SingleSelect | npo_blog/note/twitter/press_release/interview/survey | note |
| source_url | URL | 情報源URL | |
| author_type | SingleSelect | npo_staff/researcher/consultant/unknown | npo_staff |
| published_date | Date | 投稿・発行日 | |
| sentiment | SingleSelect | positive/neutral/negative/mixed | negative |
| topics | MultiSelect | 申請難易度/対応速度/報告負担/透明性/採択根拠/金額/その他 | |
| key_quotes | LongText | 直接引用（原文のまま） | 「問い合わせに2週間返答なし」 |
| notes | LongText | 備考 | |

**sentimentの基準：**
- positive: 「申請しやすい」「また使いたい」「フィードバックが丁寧」
- neutral: 事実の記述のみ
- negative: 「返答遅い」「要件不明確」「落選理由不明」「もう申請しない」
- mixed: 良い点と悪い点が混在

---

## Table 5: collection_log（収集ログ）※v1から変更なし

| フィールド名 | 型 | 説明 |
|---|---|---|
| id | AutoNumber | PK |
| foundation_name | SingleLineText | 財団名 |
| url | URL | 対象URL |
| access_status | SingleSelect | gated/public/error/not_found |
| bypass_result | SingleSelect | success/partial/failed |
| action_required | SingleSelect | none/manual_registration/phone_inquiry |
| partial_info | LongText | 部分取得情報（JSON） |
| scraped_at | DateTime | 取得日時 |

---

## ビュー設計（推奨）

### foundationsテーブル
- **Gallery** — 財団カード一覧（logo, name, type, annual_grant_total）
- **Grid（要対応）** — action_required != none でフィルタ
- **Grid（採択公開）** — adoption_data_public = true でフィルタ

### grant_programsテーブル
- **カレンダー** — deadline フィールドで締め切り管理
- **Grid（課題別）** — target_issues でグループ化
- **Grid（採択率順）** — adoption_rate_pct 降順ソート
- **Grid（公開中）** — status = active でフィルタ

### adoption_recordsテーブル
- **Grid（財団別）** — foundation_name でグループ化
- **Grid（団体別）** — grantee_name でグループ化・検索

### reputation_signalsテーブル
- **Grid（ネガティブ）** — sentiment = negative でフィルタ
- **Grid（財団別）** — foundation_name でグループ化

---

## データ量見込み（v2更新版）

| テーブル | 目標件数 | 根拠 |
|---|---|---|
| foundations | 2,500〜3,500件 | JFC調査値2,539 + 未捕捉分 |
| grant_programs | 8,000〜12,000件 | JFC調査値8,091 + 行政系 |
| adoption_records | 5,000〜20,000件 | 公開財団（トヨタ・住友・パナソニック等）の累積 |
| reputation_signals | 200〜500件 | note/ブログ/X公開情報 |
| collection_log | 500〜1,000件 | ゲートサイト・エラー分 |

---

*作成: 2026-05-18 / YC Grant Platform v2*
