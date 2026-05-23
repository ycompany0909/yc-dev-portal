# 環境変数マスター一覧

> **目的**: 全システムの環境変数・secrets・bindings を 1 ファイルで把握できる状態にする。
>
> **対象**: ycompany-portal / yc-workers (8本) / yc-dev-portal / VPS / ローカル
>
> **作成**: 2026-05-23 / 棚卸し責任者: オルズグル
>
> ⚠️ **このファイルに値を書かない** — 名前・用途・場所・漏えい影響度のみ。値は CF Dashboard / GitHub Secrets / `~/.local-secrets/` で管理。

---

## 漏えい影響度の凡例

| レベル | 意味 | 例 |
|---|---|---|
| 🔴 高 | サービス乗っ取り・全データアクセス・課金影響 | LINE Bot Token / CF API Token / SSH Key |
| 🟡 中 | 一部リソースアクセス・推測しづらいID | Service Token / Drive Folder ID |
| 🟢 低 | 公開情報レベル・実害なし | 各種 URL / Email アドレス / 状態文字列 |

---

## 1. GitHub Secrets

### 1.1 リポジトリ: ycompany-portal

| 名前 | 影響度 | 用途 | 設定先 |
|---|---|---|---|
| `CLOUDFLARE_API_TOKEN` | 🔴 高 | wrangler pages/workers deploy 用 | GitHub Actions 全 workflow |
| `CF_ACCESS_CLIENT_ID` | 🟡 中 | スモークテストの CF Access bypass | deploy.yml |
| `CF_ACCESS_CLIENT_SECRET` | 🔴 高 | 同上の secret 側 | deploy.yml |
| `VPS_SSH_KEY` | 🔴 高 | VPS 162.43.36.173 への SSH | (用途未確認) |

### 1.2 リポジトリ: yc-dev-portal

| 名前 | 影響度 | 用途 |
|---|---|---|
| `ANTHROPIC_API_KEY` | 🔴 高 | yc-dev-memo Worker 等で Claude API 呼び出し |
| `GH_PAT` | 🔴 高 | yc-dev-memo Worker から GitHub への push |

---

## 2. Cloudflare Workers（8本）

### 2.1 plaintext vars（wrangler.toml / jsonc に記載）

#### yc-ai
| 名前 | 影響度 | 値の性質 |
|---|---|---|
| `NOTIFIER_URL` | 🟢 低 | yc-infra の URL |
| `NOTIFY_LINE_USER_ID` | 🟡 中 | LINE ユーザー ID |
| `APPROVAL_UI_URL` | 🟢 低 | portal の todo-approval ページ |
| `INITIAL_STATUS` | 🟢 低 | "承認待ち" |
| `SOURCE_TAG` | 🟢 低 | "notta" |

#### yc-content
| 名前 | 影響度 | 値の性質 |
|---|---|---|
| `ADMIN_EMAILS` | 🟢 低 | 管理者メール 2 件をカンマ区切り |

#### yc-forms
| 名前 | 影響度 | 値の性質 |
|---|---|---|
| `API_BASE` | 🟢 低 | yc-line-webhook の URL |
| `GITHUB_REPO` | 🟢 低 | `ycompany0909/ycompany-portal` |
| `FEEDBACK_DIR` | 🟢 低 | `field_feedback` |

#### yc-infra
| 名前 | 影響度 | 値の性質 |
|---|---|---|
| `DIGEST_TO_EMAIL` | 🟢 低 | digest 送信先 |
| `DIGEST_FROM_EMAIL` | 🟢 低 | Resend onboarding |
| `SELF_URL` | 🟢 低 | self の URL |
| `WATCHDOG_URL` | 🟢 低 | yc-ops watchdog |
| `EM_REMIND_URL` | 🟢 低 | Pages の em/cv-remind |

#### yc-ops
| 名前 | 影響度 | 値の性質 |
|---|---|---|
| `PENDING_STATUS` / `APPROVED_STATUS` / `REJECTED_STATUS` | 🟢 低 | 状態文字列 3 種 |
| `STALE_DAYS` | 🟢 低 | `3` |
| `NOTIFIER_URL` | 🟢 低 | yc-infra URL |
| `APPROVAL_UI_URL` | 🟢 低 | portal URL |
| `FALLBACK_LINE_USER_ID` | 🟡 中 | 不明時のフォールバック LINE ID |
| `DRIVE_ROOT_FOLDER_ID` | 🟡 中 | Google Drive root |
| `SCAN_FROM_DATE` | 🟢 低 | `2026-05-01` |

#### yc-portal
| 名前 | 影響度 | 値の性質 |
|---|---|---|
| `NOCODB_HOST` | 🟢 低 | ⚠️ NocoDB廃止済み (5/20)。削除候補 |
| `MEMBERS_TABLE_ID` | 🟢 低 | ⚠️ NocoDB廃止済み。削除候補 |

#### yc-shortcut
| 名前 | 影響度 | 値の性質 |
|---|---|---|
| `ALLOWED_APPS` | 🟢 低 | `drink-form,faq-editor,members-editor,portal` |
| `APP_DOMAIN_SUFFIX` | 🟢 低 | `.ycompany.co.jp` |

#### yc-line-webhook
| 名前 | 影響度 | 値の性質 |
|---|---|---|
| `SHIFT_FORM_URL` 他 4 種 | 🟢 低 | yc-forms 配下の URL |
| `NOTIFIER_URL` | 🟢 低 | yc-infra URL |
| `ATTENDANCE_REMINDER_ENABLED` / `DAILY_REPORT_REMINDER_ENABLED` | 🟢 低 | 機能フラグ "0"/"1" |
| `COCKPIT_EMAIL_TO_STAFF` | 🟡 中 | 経営層 4 名のメール/氏名 JSON |

### 2.2 secrets (wrangler secret put で設定)

🔴 **値は wrangler dashboard / Worker 個別 secret 経由でのみ確認可能。コードからは見えない。**
**2026-05-23 `wrangler secret list` で 8 Worker 全部の secret 名を取得済み (51 件)。**

#### yc-ai (5)
| 名前 | 影響度 | 用途 |
|---|---|---|
| `ADMIN_SECRET` | 🔴 高 | 管理 API 保護 |
| `ANTHROPIC_API_KEY` | 🔴 高 | Claude API |
| `ANTHROPIC_API_KEY_PRESENTER` | 🔴 高 | プレゼンター用 Claude API (別キー) |
| `NOTIFY_API_SECRET` | 🔴 高 | yc-infra 経由通知の認証 |
| `NOTTA_WEBHOOK_SECRET` | 🔴 高 | Notta Webhook 署名検証 |

#### yc-content (2)
| 名前 | 影響度 | 用途 |
|---|---|---|
| `ANTHROPIC_API_KEY` | 🔴 高 | Claude API |
| `ONEN_SYNC_SECRET` | 🔴 高 | 1on1 sync 認証 |

#### yc-forms (4)
| 名前 | 影響度 | 用途 |
|---|---|---|
| `ANTHROPIC_API_KEY` | 🔴 高 | Claude API |
| `GITHUB_TOKEN` | 🔴 高 | フォーム feedback の GitHub commit |
| `LINE_CHANNEL_ACCESS_TOKEN` | 🔴 高 | LINE Bot 通知 |
| `SASAKI_LINE_USER_ID` | 🟡 中 | 佐々生さんの LINE User ID |

#### yc-infra (11)
| 名前 | 影響度 | 用途 |
|---|---|---|
| `EMAIL_RELAY_SECRET` | 🔴 高 | メール送信 relay 認証 |
| `EM_RUN_KEY` | 🔴 高 | event-meeting-log cron 認証 |
| `EVENT_SCANNER_SECRET` | 🔴 高 | イベントスキャナー認証 |
| `LINE_CHANNEL_ACCESS_TOKEN` | 🔴 高 | LINE Bot 通知 |
| `MORNING_TOKEN_SECRET` | 🔴 高 | 朝会トークン生成 |
| `NOTIFY_API_SECRET` | 🔴 高 | 通知 API 認証 |
| `RESEND_API_KEY` | 🔴 高 | Resend メール送信 |
| `SASAKI_LINE_USER_ID` | 🟡 中 | 佐々生さんの LINE User ID |
| `TODOIST_API_TOKEN` | 🔴 高 | Todoist 同期 |
| `WATCHDOG_RUN_KEY` | 🔴 高 | watchdog cron 認証 |
| `WEBHOOK_PUSH_SECRET` | 🔴 高 | webhook push 認証 |

#### yc-line-webhook (14)
| 名前 | 影響度 | 用途 |
|---|---|---|
| `ANTHROPIC_API_KEY` | 🔴 高 | Claude API |
| `COCKPIT_SECRET` | 🔴 高 | Pages Function との共有シークレット |
| `CONTACT_SCORING_KEY` | 🔴 高 | お客様関係値スコアリング cron 認証 |
| `DAILY_TOKEN_KEY` | 🔴 高 | 日報トークン生成 |
| `GAS_WEBAPP_URL` | 🟡 中 | JIDAI 売上 GAS WebApp URL |
| `HEALTHCHECK_CRON_SECRET` | 🔴 高 | ヘルスチェック cron 認証 |
| `IMPRESSIVE_CUSTOMERS_TID` | 🟡 中 | 印象お客様 NocoDB table ID (廃止候補?) |
| `LINE_CHANNEL_ACCESS_TOKEN` | 🔴 高 | LINE Messaging API |
| `NOCODB_TOKEN` | — | ⚠️ 廃止済み。secret 削除推奨 |
| `NOTIFY_API_SECRET` | 🔴 高 | 通知 API 認証 |
| `PUSH_API_SECRET` | 🔴 高 | 外部 push / cron キック保護 |
| `SHIFT_TOKEN_SECRET` | 🔴 高 | シフトトークン生成 |
| `SQUARE_TOKEN` | 🔴 高 | Square 決済 API |
| `SYNC_SECRET` | 🔴 高 | 各種 sync API 認証 |

⚠️ **`LINE_CHANNEL_SECRET` がリストに無い** — Webhook 署名検証に必要だが現状未設定の可能性。要確認。

#### yc-ops (7)
| 名前 | 影響度 | 用途 |
|---|---|---|
| `ANTHROPIC_API_KEY` | 🔴 高 | Claude API |
| `APPROVAL_API_KEY` | 🔴 高 | 承認 API 認証 |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | 🔴 高 | Google Drive アクセス用 SA JSON |
| `NOTIFY_API_SECRET` | 🔴 高 | 通知 API 認証 |
| `NOTTA_SYNC_SECRET` | 🔴 高 | Notta sync 認証 |
| `SCAN_SECRET` | 🔴 高 | スキャナー認証 |
| `WATCHDOG_RUN_KEY` | 🔴 高 | watchdog cron 認証 |

#### yc-portal (4)
| 名前 | 影響度 | 用途 |
|---|---|---|
| `ANTHROPIC_API_KEY` | 🔴 高 | Claude API |
| `NOCODB_API_TOKEN` | — | ⚠️ 廃止済み。削除推奨 |
| `NOCODB_TOKEN` | — | ⚠️ 廃止済み (重複)。削除推奨 |
| `PIPELINE_TRIGGER_SECRET` | 🔴 高 | パイプラインキック認証 |

#### yc-shortcut (4)
| 名前 | 影響度 | 用途 |
|---|---|---|
| `CF_ACCESS_CLIENT_ID` | 🟡 中 | CF Access Service Token (旧用途) |
| `CF_ACCESS_CLIENT_SECRET` | 🔴 高 | 同上の secret 側 |
| `NURTURING_ADMIN_SECRET` | 🔴 高 | ナーチャリング管理画面認証 |
| `SHORTCUT_TOKEN` | 🔴 高 | OTP バイパストークン |

### 2.3 集約候補・観察

- **`ANTHROPIC_API_KEY` が 5 Worker に散在** (yc-ai, content, forms, line-webhook, ops, portal の 6 つ)
  → Service Binding 経由で 1 Worker に集約すれば管理コスト削減
- **`LINE_CHANNEL_ACCESS_TOKEN` が 3 Worker に散在** (yc-forms, infra, line-webhook)
  → 同じ Channel を共有しているなら集約候補
- **`NOTIFY_API_SECRET` が 5 Worker に散在** (yc-ai, infra, line-webhook, ops, portal)
  → 通知共通 secret として運用ルール化
- **`SASAKI_LINE_USER_ID` が 2 Worker に散在** → plaintext vars 化を検討
- **NocoDB 残骸** (`NOCODB_API_TOKEN`, `NOCODB_TOKEN`) が **yc-line-webhook, yc-portal** に残存
  → 2026-05-20 移行完了済み、即削除可能
- **`LINE_CHANNEL_SECRET` 未設定？** yc-line-webhook で発見できず。Webhook 署名検証が動いているか要確認

---

## 3. Cloudflare Pages (yc-manual-v13)

### 3.1 環境変数 (production)

| 名前 | 影響度 | 用途 | 状態 |
|---|---|---|---|
| (CF Dashboard 上に何も無し) | — | — | API 経由で確認: `env_vars: []` |

⚠️ **2026-05-23 確認時点で Pages の Environment Variables は空**。
これが原因で `permissions/me` API が `{"error":"COCKPIT_SECRET not set"}` を返している。
→ 必要な secret は CF Pages の Dashboard で個別設定が必要：
- `COCKPIT_SECRET` (Pages Functions 経由で executive 権限判定に使用)
- `OWNER_EMAIL` (一部 fallback 用)

### 3.2 D1 Bindings (wrangler.toml 経由で設定済み)

| binding | database | 用途 |
|---|---|---|
| `DB` | `yc-main-db` | メイン DB (お客様 13,860 件等) |
| `SHIFT_DB` | `yc-shift-db` | シフト・event_attendance |

---

## 4. D1 データベース全体

| database_name | 用途 | 利用元 |
|---|---|---|
| **yc-main-db** | お客様 / メンバー / breadcrumb / 朝会等 | Pages, yc-ai, yc-content, yc-ops, yc-portal, yc-line-webhook |
| **yc-shift-db** | シフト / event_attendance / 日報 | yc-infra, yc-ops, yc-line-webhook, Pages |
| **yc-bot-logs** | Bot 履歴 (廃止候補?) | yc-ai, yc-content, yc-portal |

⚠️ `yc-bot-logs` は使用継続か要確認。

---

## 5. KV / R2

| binding | type | 用途 | 利用元 |
|---|---|---|---|
| `USER_IDS` | KV (734f8db8...) | LINE ユーザー ID 管理 | yc-line-webhook |
| `LOW_EVENTS` | KV | 低頻度イベント記録 | yc-infra |
| `CHECKLIST_PHOTOS` | R2 `yc-checklist-photos` | 開閉店チェックリスト写真 | yc-line-webhook |

---

## 6. Service Bindings (Worker → Worker)

| from | to | binding |
|---|---|---|
| yc-ops | yc-infra | `NOTIFIER` |
| yc-line-webhook | yc-insight-bot | `INSIGHT_BOT` |

---

## 7. VPS (162.43.36.173) ⚠️ 棚卸し未完了

VPS 上の `/opt/yc-*/` 配下の `.env` ファイルを SSH で確認する必要あり：

```bash
ssh root@162.43.36.173 'for d in /opt/yc-*/; do echo "=== $d ==="; cat "$d.env" 2>/dev/null | grep -oE "^[A-Z_]+="  | head -20; done'
```

### 想定される env (要確認)

| 場所 | 想定される env |
|---|---|
| `/opt/yc-asakai/.env` | `COCKPIT_SECRET`, `LINE_*`, `OPENAI_API_KEY` |
| `/opt/yc-timetree-sync/.env` | `TIMETREE_EMAIL`, `TIMETREE_PASSWORD`, `PIPELINE_TRIGGER_SECRET` |
| `/opt/yc-plaud/.env` | `PLAUD_USER`, `ANTHROPIC_API_KEY`, `GOOGLE_DRIVE_CREDS` |

**棚卸しタスク**: 上記コマンドを実行し、このファイルの「7. VPS」セクションに追記する（次回作業）。

---

## 8. ローカル開発環境 (Mac)

| ファイル | 影響度 | 用途 |
|---|---|---|
| `~/.cf-access-admin-token` | 🔴 高 | CF Access service token 管理用 API token (2026-05-23 作成) |
| `~/yc-ip-auto-update.py` 内ハードコード | 🔴 高 | ⚠️ `CF_API_TOKEN` (cfut_h66...) と `ACCOUNT_ID` がハードコード。リファクタ候補 |
| `~/.wrangler/config/default.toml` | 🔴 高 | wrangler OAuth トークン (scope: workers/pages/d1/kv 等) |
| `~/.claude/projects/.../memory/` | 🟡 中 | Claude メモリ（個人情報含む可能性） |

---

## 9. 棚卸し漏れチェックリスト

- [x] **各 Worker で `wrangler secret list` 実行 (8本)** ✅ 2026-05-23
- [ ] CF Pages Dashboard で「Environment Variables」を確認 (API では空判定)
- [ ] VPS の `/opt/yc-*/.env` を全部確認
- [ ] GAS の Script Properties（clasp 経由）を確認
- [ ] LINE Developers Console の Channel Secret/Token 一覧と突き合わせ
- [ ] **`LINE_CHANNEL_SECRET` が yc-line-webhook に未設定 → Webhook 署名検証が動いているか確認**
- [ ] 廃止済み env (`NOCODB_API_TOKEN` x2, `NOCODB_TOKEN`, `NOCODB_HOST`, `MEMBERS_TABLE_ID`, `IMPRESSIVE_CUSTOMERS_TID`) を実際に削除
- [ ] **集約候補**: ANTHROPIC_API_KEY (5箇所) / LINE_CHANNEL_ACCESS_TOKEN (3箇所) / NOTIFY_API_SECRET (5箇所)
- [ ] `~/yc-ip-auto-update.py` の hardcode を環境変数化

---

## 10. 運用ルール

### 新しい secret を追加するとき

1. **このファイルに追加**（名前・影響度・用途のみ。値は書かない）
2. 追加先（GitHub Secrets / wrangler secret / CF Pages env）に設定
3. コード側で `env.XXX` 経由で参照（ハードコード禁止）
4. commit message にこのファイルへの追記を含める

### Secret を rotate するとき

1. 新しい値を生成・設定（旧と並行運用）
2. コード/CI を新値で動作確認
3. 旧値を削除
4. このファイルに「rotate 履歴」を追記（年月日のみ、値は書かない）

### このファイルを更新するとき

毎月末に棚卸し（30分）：
- 廃止された secret が残っていないか
- 新規 secret がここに記録されているか
- 影響度の評価が変わっていないか

---

## 関連ドキュメント

- 📊 [skill-assessment.md](../skill-assessment.md) — 実装力診断
- 📜 [dev-history.md](../dev-history.md) — 開発履歴
- 🎯 [plan.json](../plan.json) — 強化計画
- 📝 [eval/ai-output-eval-v1.md](../eval/ai-output-eval-v1.md) — AI 出力評価シート

---

*v1 初版作成: 2026-05-23 by Claude Opus 4.7 + オルズグル*
*戦闘力ロードマップ: 92 → 92.5 (+0.5pt)*
