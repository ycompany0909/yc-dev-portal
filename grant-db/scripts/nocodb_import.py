#!/usr/bin/env python3
"""
YC Grant Platform — NocoDB v2 自動インポートスクリプト
output/*.csv を NocoDB API v2 経由で一括登録する。

使い方:
  NOCODB_API_TOKEN=xxx NOCODB_URL=https://db.ycompany.co.jp python3 nocodb_import.py
  python3 nocodb_import.py --base-name "YC Grant DB" --dry-run
"""

import csv, json, os, sys, time, argparse, requests
from pathlib import Path
from datetime import datetime

# ── 設定 ────────────────────────────────────────────────────────
OUTPUT_DIR   = Path(__file__).parent / "output"
NOCODB_URL   = os.environ.get("NOCODB_URL", "http://localhost:8080")
API_TOKEN    = os.environ.get("NOCODB_API_TOKEN") or os.environ.get("NOCODB_TOKEN", "")
WORKSPACE_ID = os.environ.get("NOCODB_WORKSPACE_ID", "wfi4854r")
BASE_NAME    = "YC Grant Database"
DELAY        = 0.15

TABLES = {
    "foundations":      "財団マスタ",
    "grant_programs":   "助成プログラム",
    "adoption_records": "採択実績",
}

def ts(): return datetime.now().strftime("%H:%M:%S")
def log(msg, lv="INFO"): print(f"[{ts()}][{lv}] {msg}", flush=True)

class NocoDBClient:
    def __init__(self, base_url: str, token: str, workspace_id: str):
        self.base = base_url.rstrip("/")
        self.ws   = workspace_id
        self.s = requests.Session()
        self.s.headers.update({
            "xc-token": token,
            "Content-Type": "application/json",
        })

    def _get(self, path, **kw):
        return self.s.get(f"{self.base}/api/v2{path}", **kw)

    def _post(self, path, **kw):
        return self.s.post(f"{self.base}/api/v2{path}", **kw)

    def _delete(self, path, **kw):
        return self.s.delete(f"{self.base}/api/v2{path}", **kw)

    # ── Base ──────────────────────────────────────────────────────
    def list_bases(self):
        r = self._get(f"/meta/workspaces/{self.ws}/bases")
        r.raise_for_status()
        return r.json().get("list", [])

    def find_or_create_base(self, name: str) -> str:
        for b in self.list_bases():
            if b["title"] == name:
                return b["id"]
        r = self._post(f"/meta/workspaces/{self.ws}/bases", json={"title": name})
        r.raise_for_status()
        return r.json()["id"]

    # ── Table ─────────────────────────────────────────────────────
    def list_tables(self, base_id: str):
        r = self._get(f"/meta/bases/{base_id}/tables")
        r.raise_for_status()
        return r.json().get("list", [])

    def find_or_create_table(self, base_id: str, title: str, columns: list) -> str:
        for t in self.list_tables(base_id):
            if t["title"] == title:
                return t["id"]
        r = self._post(f"/meta/bases/{base_id}/tables", json={"title": title, "columns": columns})
        r.raise_for_status()
        return r.json()["id"]

    # ── Records ───────────────────────────────────────────────────
    def insert_records(self, table_id: str, rows: list) -> dict:
        r = self._post(f"/tables/{table_id}/records", json=rows)
        r.raise_for_status()
        return r.json()

def load_csv(fname: str) -> list[dict]:
    p = OUTPUT_DIR / fname
    if not p.exists():
        log(f"{fname} が存在しません。スキップ。", "WARN")
        return []
    with open(p, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        log(f"{fname} が空です。スキップ。", "WARN")
        return []
    clean = []
    for row in rows:
        clean.append({k: (v if v not in ("", "None", "null") else None) for k, v in row.items()})
    return clean

def make_columns(sample_row: dict) -> list:
    NUMERIC = {"id","established_year","annual_grant_total_jpy",
               "amount_min_jpy","amount_max_jpy","deadline_month_recurring",
               "total_applicants_recent","total_adopted_recent","adoption_rate_pct",
               "fiscal_year","amount_jpy","min_operation_years"}
    BOOL    = {"adoption_data_public","requires_registration","requires_legal_entity"}
    cols = []
    for k in sample_row.keys():
        if k == "id": continue
        if k in NUMERIC:
            cols.append({"title": k, "uidt": "Number"})
        elif k in BOOL:
            cols.append({"title": k, "uidt": "Checkbox"})
        else:
            v = sample_row[k] or ""
            cols.append({"title": k, "uidt": "LongText" if len(v) >= 200 else "SingleLineText"})
    return cols

def batch(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def run_import(dry_run=False, base_name=BASE_NAME):
    if not API_TOKEN and not dry_run:
        log("NOCODB_API_TOKEN が未設定です。", "ERROR")
        sys.exit(1)

    client = NocoDBClient(NOCODB_URL, API_TOKEN, WORKSPACE_ID)

    log(f"NocoDB接続: {NOCODB_URL}")
    if not dry_run:
        base_id = client.find_or_create_base(base_name)
        log(f"Base: {base_name} (id={base_id})")
    else:
        base_id = "DRY_RUN"
        log(f"[DRY RUN] Base: {base_name}")

    for csv_key, table_title in TABLES.items():
        rows = load_csv(f"{csv_key}.csv")
        if not rows:
            continue
        log(f"\n--- {table_title} ({len(rows)}件) ---")

        if dry_run:
            log(f"[DRY RUN] {len(rows)}件をインポート予定")
            log(f"  カラム: {list(rows[0].keys())}")
            continue

        cols = make_columns(rows[0])
        table_id = client.find_or_create_table(base_id, table_title, cols)
        log(f"  テーブルID: {table_id}")

        ok = 0
        for chunk in batch(rows, 100):
            try:
                client.insert_records(table_id, chunk)
                ok += len(chunk)
                log(f"  挿入: {ok}/{len(rows)}件")
                time.sleep(DELAY)
            except Exception as e:
                log(f"  挿入エラー: {e}", "WARN")

        log(f"  完了: {ok}件")

    log("\n=== インポート完了 ===")

def main():
    global NOCODB_URL, WORKSPACE_ID
    parser = argparse.ArgumentParser(description="NocoDB v2 CSV Importer for YC Grant DB")
    parser.add_argument("--dry-run",      action="store_true", help="実際に書き込まず内容を確認")
    parser.add_argument("--base-name",    default=BASE_NAME,   help=f"NocoDB Base名（デフォルト: {BASE_NAME}）")
    parser.add_argument("--url",          default=NOCODB_URL,  help="NocoDB URL")
    parser.add_argument("--workspace-id", default=WORKSPACE_ID, help="Workspace ID")
    args = parser.parse_args()
    NOCODB_URL   = args.url
    WORKSPACE_ID = args.workspace_id
    run_import(dry_run=args.dry_run, base_name=args.base_name)

if __name__ == "__main__":
    main()
