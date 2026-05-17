# YC開発 現在地（更新: 2026-05-17）

## 作業者
- オルズグル（Y COMPANY代表）
- MacBook Air: 外出時 + 自宅兼用
- iMac: 自宅専用（posta / event-meeting-log はiMacのみ）

## 進行中プロジェクト

| プロジェクト | 状況 | 次のアクション |
|---|---|---|
| GitHub MCP設定 | 🟡 進行中 | claude mcp addを実行・動作確認 |
| ICJデモデイ運営 | 🟡 進行中 | 6/11本番・河内・大森・平野井で座組み完了 |
| ポスター管理システム | 🔴 設計中 | NocoDB + LINE通知の構築 |
| yc-dev-portal（本システム） | 🟡 進行中 | GitHub Pages公開・スマホ壁打ち体制確立 |

## 完了済みプロジェクト

| プロジェクト | 詳細 |
|---|---|
| JIDAI日報GAS | 銀座店。19時/21時/23時 売上アラート稼働中 |
| Plaudパイプライン | Plaud→Drive→VPS→NocoDB→portal.ycompany.co.jp/meetings |
| orzugulポータル | orzugul-portal.pages.dev（DNS移行のみ残: お名前.comのNS変更） |
| ポス太 | posta-app.pages.dev（orzugulポータルにiframe埋め込み済み） |

## 店舗・事業体

| 名称 | エリア | 備考 |
|---|---|---|
| JIDAI | 銀座 | 日報GAS・売上アラート稼働中 |
| IAPONIA | 新橋 | |

## 重要な前提

- Cloudflareアカウント: ycompany0909@gmail.com（Account ID: 518cd04ae0a78ab125311da3f2a9da15）
- GAS管理: ycompany0909@gmail.com
- Workers: TypeScript不使用・素のJS
- NocoDB token: env.NOCODB_API_TOKEN || env.NOCODB_TOKEN の両受け
- 外部メール送信時: ycompany0909@gmail.com をCC必須
- ポータル系URL: portal.ycompany.co.jp（pages.devは内部のみ）

## 主要システム

| サービス | URL | 状態 |
|---|---|---|
| YCポータル | portal.ycompany.co.jp/meetings | ✅ 稼働 |
| orzugulポータル | orzugul-portal.pages.dev | ✅ 稼働 |
| orzugul API Worker | orzugul-api.ycompany0909.workers.dev | ✅ 稼働 |
| ポス太 | posta-app.pages.dev | ✅ 稼働 |

## スタック・ツール

- Cloudflare Workers / Pages / D1 / KV
- NocoDB（Cloudflare D1併用）
- LINE Messaging API
- GAS (Google Apps Script)
- Python（VPS cron）
- GitHub / GitHub Pages
- Claude Code（Mac）

## 今週の最優先タスク

1. GitHub MCP動作確認
2. ICJデモデイ 6/11本番準備
3. orzugulポータル DNS移行完了（お名前.comのNS変更）
4. ポスター管理システム 設計着手

## スマホ壁打ち用クイックコンテキスト

```
私はY COMPANYの代表です。
主なスタック: Cloudflare Workers(素のJS), NocoDB, LINE API, GAS, Python
進行中: GitHub MCP設定, ICJデモデイ(6/11本番), ポスター管理システム設計
店舗: JIDAI(銀座), IAPONIA(新橋)
ポータル: portal.ycompany.co.jp
---
[ここに質問を書く]
```
