#!/usr/bin/env python3
"""
foundations.csv に人件費可否・複数年継続可否を追加し、
grant_programs.csv に財団情報をjoinしてgrant-data.jsonを再生成する。
"""
import csv, json
from pathlib import Path

OUT  = Path(__file__).parent / "output"
DOCS = Path(__file__).parent.parent.parent / "docs"

# ── 財団ごとの調査データ ─────────────────────────────────────────────
# labor_cost : 可 / 不可 / 一部可 / 要確認
# multi_year : 可 / 不可 / 要確認
# max_years  : 最大助成年数（不明は0）
FOUNDATION_INTEL = {
    "トヨタ財団":           {"labor_cost": "可",    "multi_year": "可",   "max_years": 3},
    "住友財団":             {"labor_cost": "一部可", "multi_year": "可",   "max_years": 3},
    "パナソニック教育財団": {"labor_cost": "不可",  "multi_year": "可",   "max_years": 2},
    "日本財団":             {"labor_cost": "可",    "multi_year": "可",   "max_years": 3},
    "東急財団":             {"labor_cost": "要確認","multi_year": "不可", "max_years": 1},
    "セコム科学技術財団":   {"labor_cost": "可",    "multi_year": "可",   "max_years": 3},
    "ソニー教育財団":       {"labor_cost": "不可",  "multi_year": "不可", "max_years": 1},
    "積水ハウス財団":       {"labor_cost": "要確認","multi_year": "可",   "max_years": 3},
    "三菱UFJ環境財団":      {"labor_cost": "不可",  "multi_year": "不可", "max_years": 1},
    "花王芸術科学財団":     {"labor_cost": "要確認","multi_year": "不可", "max_years": 1},
    "三菱財団":             {"labor_cost": "可",    "multi_year": "可",   "max_years": 3},
    "笹川平和財団":         {"labor_cost": "可",    "multi_year": "可",   "max_years": 3},
    "キリン福祉財団":       {"labor_cost": "不可",  "multi_year": "不可", "max_years": 1},
    "イオン環境財団":       {"labor_cost": "不可",  "multi_year": "不可", "max_years": 1},
    "セブン記念財団":       {"labor_cost": "不可",  "multi_year": "不可", "max_years": 1},
    "野村財団":             {"labor_cost": "可",    "multi_year": "可",   "max_years": 2},
    "みずほ福祉助成財団":   {"labor_cost": "不可",  "multi_year": "不可", "max_years": 1},
    "大和証券財団":         {"labor_cost": "不可",  "multi_year": "不可", "max_years": 1},
    "旭硝子財団":           {"labor_cost": "可",    "multi_year": "可",   "max_years": 3},
    "朝日新聞文化財団":     {"labor_cost": "要確認","multi_year": "不可", "max_years": 1},
    "赤い羽根共同募金":     {"labor_cost": "一部可","multi_year": "可",   "max_years": 3},
    "パブリックリソース財団":{"labor_cost":"可",    "multi_year": "可",   "max_years": 3},
    "SOMPO福祉財団":        {"labor_cost": "不可",  "multi_year": "不可", "max_years": 1},
    "ニッセイ財団":         {"labor_cost": "不可",  "multi_year": "可",   "max_years": 3},
    "ドコモ市民活動助成":   {"labor_cost": "一部可","multi_year": "不可", "max_years": 1},
}

# ── 1. foundations.csv 更新 ──────────────────────────────────────────
def update_foundations():
    p = OUT / "foundations.csv"
    with open(p, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    new_fields = ["labor_cost_eligible", "multi_year_eligible", "max_grant_years"]
    for row in rows:
        short = row.get("name_short", "")
        intel = FOUNDATION_INTEL.get(short, {})
        row["labor_cost_eligible"] = intel.get("labor_cost", "要確認")
        row["multi_year_eligible"] = intel.get("multi_year", "要確認")
        row["max_grant_years"]     = str(intel.get("max_years", 0))

    fieldnames = list(rows[0].keys())
    with open(p, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"✅ foundations.csv 更新 ({len(rows)}件)")
    return {r["name_short"]: r for r in rows}

# ── 2. grant-data.json 再生成（財団フィールドjoin）───────────────────
def regen_json(foundation_map):
    p = OUT / "grant_programs.csv"
    with open(p, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    # name_short → foundation row のマップ（foundation_nameで前方一致）
    def find_foundation(fname):
        for short, frow in foundation_map.items():
            if short in fname or fname in frow.get("name", ""):
                return frow
        return {}

    out = []
    for row in rows:
        fname = row.get("foundation_name", "")
        frow  = find_foundation(fname)
        row["labor_cost_eligible"] = frow.get("labor_cost_eligible", "要確認")
        row["multi_year_eligible"] = frow.get("multi_year_eligible", "要確認")
        row["max_grant_years"]     = frow.get("max_grant_years", "0")
        out.append(row)

    dest = DOCS / "grant-data.json"
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"✅ grant-data.json 再生成 ({len(out)}件, {dest.stat().st_size//1024}KB)")

if __name__ == "__main__":
    fmap = update_foundations()
    regen_json(fmap)
    print("完了")
