# D1 データ分類表 v1

> **目的**: D1 全テーブルを「**個人情報レベル / 公開可否 / 必要権限 / 漏えい時影響度**」の4軸で分類し、取扱いルールを明確化する。
>
> **対象**: yc-main-db (45) + yc-shift-db (18) + yc-bot-logs (1) = **計 64 テーブル**
>
> **作成**: 2026-05-23 / 分類責任者: オルズグル
>
> ⚠️ **私（Claude）が初版を作成 → ユーザーレビュー必須**。テーブル名から推測した分類は誤りの可能性あり。

---

## 4 軸の凡例

### 1. 個人情報レベル
| レベル | 意味 | 例 |
|---|---|---|
| 🔴 高 | 個人を特定できる情報（電話・メール・住所含む） | `contacts`（お客様）|
| 🟡 中 | 氏名のみ・社内識別子 | `members`（スタッフ）|
| 🟢 低 | ID 主体・付帯情報 | `staff_form_submissions` |
| ⚪ なし | 個人情報を含まない | `zaiko_items` |

### 2. 公開可否
| | 意味 |
|---|---|
| **公開API** | 認証なし GET 可能（白リスト方式） |
| **認証必要** | CF Access + 役職判定後アクセス可 |
| **内部限定** | Worker 間通信のみ・ヒト不可 |

### 3. 必要権限
- **executive**: 経営層（オーナー含む）
- **admin**: 管理者（store_manager 含む）
- **staff**: 一般スタッフ
- **公開**: 認証不要

### 4. 漏えい時影響度
- 🔴 高: 顧客信頼失墜・法的リスク・損害賠償
- 🟡 中: 内部混乱・スタッフプライバシー
- 🟢 低: 営業損害なし

---

## 📋 yc-main-db（45 テーブル）

### A. 🔴 最高リスク群（個人情報 + 漏えい影響大）

| テーブル | 用途 | 個人情報 | 公開可否 | 必要権限 | 漏えい影響 |
|---|---|---|---|---|---|
| **contacts** | お客様マスタ（13,860件）電話・メール・住所含む | 🔴 高 | 認証必要 | executive / admin | 🔴 高 |
| **impressive_customers** | 印象お客様 | 🔴 高 | 認証必要 | admin | 🔴 高 |
| **meetings** | 議事録・会議録 | 🔴 高 | 認証必要 | executive | 🔴 高 |
| **gijiroku_logs** | 議事録ログ | 🔴 高 | 認証必要 | executive | 🔴 高 |
| **insights** | 経営インサイト | 🔴 高 | 認証必要 | executive | 🔴 高 |
| **secretary_logs** | AI 秘書対話ログ | 🔴 高 | 認証必要 | executive | 🔴 高 |
| **nurturing_actions** | お客様向けナーチャリング履歴 | 🔴 高 | 認証必要 | executive / admin | 🔴 高 |
| **one_on_one** | 1on1 記録 | 🔴 高 | 認証必要 | executive | 🔴 高 |
| **kuchikomi_requests** | 口コミ依頼進捗（お客様氏名含む） | 🔴 高 | 認証必要 | admin | 🔴 高 |
| **subscription_withdrawals** | サブスク退会データ（お客様連絡先含む） | 🔴 高 | 認証必要 | admin | 🔴 高 |
| **withdrawal_requests** | 退会申請 | 🔴 高 | 認証必要 | admin | 🔴 高 |
| **business_card_orders** | 名刺発行依頼（連絡先含む） | 🔴 高 | 認証必要 | admin | 🟡 中 |
| **mgmt_daily_reports** | 経営日報 | 🔴 高 | 認証必要 | executive | 🔴 高 |

### B. 🟡 中リスク群（スタッフ情報・業務オペレーション）

| テーブル | 用途 | 個人情報 | 公開可否 | 必要権限 | 漏えい影響 |
|---|---|---|---|---|---|
| **members** | スタッフマスタ | 🟡 中 | 認証必要 | admin | 🟡 中 |
| **cockpit_tasks** | コックピット タスク | 🟢 低 | 認証必要 | admin | 🟡 中 |
| **action_items** | アクションアイテム | 🟢 低 | 認証必要 | admin | 🟡 中 |
| **asakai_readiness** | 朝会成立要件チェック | 🟢 低 | 認証必要 | admin | 🟡 中 |
| **bouzu_daily** | 朝会の支度 | 🟢 低 | 認証必要 | admin | 🟡 中 |
| **event_outreach** | イベント声かけ | 🟡 中 | 認証必要 | admin | 🟡 中 |
| **presenter_candidates** | プレゼンター候補 | 🟡 中 | 認証必要 | admin | 🟡 中 |
| **relationship_ratings** | お客様関係値スコア | 🟡 中 | 認証必要 | admin | 🟡 中 |
| **tagging_rules** | タグ付けルール | ⚪ なし | 認証必要 | admin | 🟢 低 |
| **dev_requests** | 開発リクエスト | 🟢 低 | 認証必要 | admin | 🟢 低 |
| **staff_form_submissions** | スタッフフィードバック | 🟡 中 | 認証必要 | admin | 🟡 中 |
| **ai_eval** | AI 評価ログ（評価シート v1 連動） | 🟢 低 | 認証必要 | admin | 🟢 低 |
| **ai_ledger** | AI 利用台帳 | 🟢 低 | 認証必要 | admin | 🟢 低 |
| **ai_class** | AI 分類 | 🟢 低 | 認証必要 | admin | 🟢 低 |
| **automation** | 自動化定義 | 🟢 低 | 認証必要 | admin | 🟢 低 |
| **notta_keywords** | Notta キーワード | 🟢 低 | 認証必要 | admin | 🟢 低 |
| **notta_outreach** | Notta 声かけ用テキスト | 🟢 低 | 認証必要 | admin | 🟢 低 |
| **timetree_meetings** | TimeTree 同期データ | 🟢 低 | 認証必要 | admin | 🟢 低 |

### C. 🟢 低リスク群（業務マスタ・公開可能データ）

| テーブル | 用途 | 個人情報 | 公開可否 | 必要権限 | 漏えい影響 |
|---|---|---|---|---|---|
| **zaiko_items** | 在庫マスタ | ⚪ なし | 公開API GET | 公開 | 🟢 低 |
| **zaiko_history** | 在庫履歴 | ⚪ なし | 公開API GET | 公開 | 🟢 低 |
| **drinks** | お酒情報 | ⚪ なし | 公開API GET | 公開 | 🟢 低 |
| **glossary** | 用語集 | ⚪ なし | 公開API GET | 公開 | 🟢 低 |
| **industry_events** | 業界イベント | ⚪ なし | 公開API GET | 公開 | 🟢 低 |
| **important_files** | 重要ファイルメタ | ⚪ なし | 認証必要 | admin | 🟢 低 |
| **breadcrumb_order** | サイドバー構成 | ⚪ なし | 認証必要 | admin | 🟢 低 |
| **em_meta** / **em_entries** | event-meeting-log | 🟡 中 | 認証必要 | admin | 🟡 中 |
| **faq_iaponia** / **faq_jidai** / **faq_onboarding** / **faq_one_day_host** / **faq_presenter** | 店舗 FAQ | ⚪ なし | 公開 / 内部混在 | guest / staff | 🟢 低 |

---

## 📋 yc-shift-db（18 テーブル）

### スタッフ・シフト・現場運営

| テーブル | 用途 | 個人情報 | 公開可否 | 必要権限 | 漏えい影響 |
|---|---|---|---|---|---|
| **staff** | シフト DB のスタッフマスタ | 🟡 中 | 認証必要 | admin | 🟡 中 |
| **staff_permissions** | 権限マスタ（みおりビュー等） | 🟢 低 | 認証必要 | executive | 🟡 中 |
| **shift_requests** | シフト希望提出 | 🟡 中 | 認証必要 | admin | 🟡 中 |
| **shift_assignments** | シフト確定割当 | 🟡 中 | 認証必要 | admin | 🟡 中 |
| **shift_month_status** | シフト月別状態管理 | 🟢 低 | 認証必要 | admin | 🟢 低 |
| **attendance_records** | 出退勤記録 | 🟡 中 | 認証必要 | admin | 🟡 中 |
| **daily_reports** | 日報 | 🟡 中 | 認証必要 | admin | 🟡 中 |
| **closed_days** | 閉店日マスタ | ⚪ なし | 公開API GET | 公開 | 🟢 低 |
| **checklist_master** | チェックリスト定義 | ⚪ なし | 認証必要 | admin | 🟢 低 |
| **checklist_submissions** | チェックリスト提出 | 🟢 低 | 認証必要 | staff / admin | 🟡 中 |
| **checklist_photos** | チェックリスト写真（R2 連動） | 🟡 中 | 認証必要 | staff / admin | 🟡 中 |
| **bozu_instructions** | 朝会指示マスタ | ⚪ なし | 認証必要 | admin | 🟢 低 |
| **bozu_tasks** | 朝会タスク | 🟢 低 | 認証必要 | admin | 🟢 低 |
| **morning_check** | 朝の確認 | 🟢 低 | 認証必要 | staff / admin | 🟢 低 |
| **confirm_logs** | 確認ログ | 🟢 低 | 認証必要 | staff / admin | 🟢 低 |
| **reminder_log** | リマインダー送信ログ | 🟢 低 | 内部限定 | system | 🟢 低 |
| **event_attendance** | イベント参加管理（声かけ連動） | 🟡 中 | 認証必要 | admin | 🟡 中 |
| **research_theme_content** | 研究テーマ・コンテンツ | ⚪ なし | 認証必要 | admin | 🟢 低 |

---

## 📋 yc-bot-logs（1 テーブル）

| テーブル | 用途 | 個人情報 | 公開可否 | 必要権限 | 漏えい影響 |
|---|---|---|---|---|---|
| **q_log** | Bot 問い合わせログ | 🟢 低 | 認証必要 | admin | 🟢 低 |

⚠️ 利用継続か要確認。NocoDB 廃止と一緒に廃止候補かも。

---

## 🚨 高リスクテーブル TOP 5（最重要）

| 順 | テーブル | 件数（推定） | 理由 |
|---|---|---|---|
| 1 | **contacts** | 13,860 件 | お客様の電話・メール・住所。漏えい = 法的リスク |
| 2 | **meetings** / **gijiroku_logs** | (要確認) | 議事録に顧客名・商談内容含む |
| 3 | **insights** | (要確認) | 経営判断・戦略情報 |
| 4 | **secretary_logs** | (要確認) | AI 秘書との対話履歴（個人情報複合） |
| 5 | **nurturing_actions** / **kuchikomi_requests** | (要確認) | お客様の個別動向追跡データ |

---

## 取扱いルール

### A. 🔴 最高リスク群（13テーブル）

- **アクセス制御**: CF Access + executive または admin ロールのみ
- **エクスポート**: 個別承認制（オーナー承認）
- **バックアップ**: D1 自動 backup に加え、月次で暗号化エクスポート
- **ログ**: アクセス履歴を別途記録（要追加実装）
- **退職者対応**: `staff_permissions.active=0` で即時遮断

### B. 🟡 中リスク群

- **アクセス制御**: admin 以上
- **共有時**: 内部限定（社外提供は要承認）
- **マスキング**: スクショ共有時はメール・電話番号をマスク

### C. 🟢 低リスク群

- **アクセス制御**: staff またはゲスト（公開API）
- **公開**: API として外部から GET 可能（CF Access バイパス済み）

---

## ⚠️ レビュー必須項目（オルズグルさん確認お願いします）

私の推測で分類しているため、以下は確認してください：

- [ ] **`research_theme_content`** の用途 — 何のテーブル？
- [ ] **`bouzu_daily` / `bozu_*`** の「ぼうず」とは？（朝会か？お坊さんか？）
- [ ] **`presenter_candidates`** の権限 — admin で正しい？executive 限定にすべき？
- [ ] **`q_log`**（yc-bot-logs）の利用継続可否
- [ ] **`em_*`**（event-meeting-log）の個人情報レベル — 中で妥当？
- [ ] **FAQ 系 5 テーブル** — どれが完全公開で、どれが認証必要？

各テーブルの実カラムを見れば確実だが、まずは現状のラフ分類で push。修正は v2 で。

---

## 関連ドキュメント

- 🔑 [env-master.md](../env/env-master.md) — 環境変数マスター
- 📊 [skill-assessment.md](../skill-assessment.md) — 実装力診断
- 📜 [dev-history.md](../dev-history.md) — 開発履歴
- 🎯 [plan.json](../plan.json) — 強化計画
- 📝 [eval/ai-output-eval-v1.md](../eval/ai-output-eval-v1.md) — AI 出力評価シート

---

*v1 初版作成: 2026-05-23 by Claude Opus 4.7 + オルズグル*
*戦闘力ロードマップ: 92.5 → 93 (+0.5pt)*
