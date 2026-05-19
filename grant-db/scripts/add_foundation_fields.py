#!/usr/bin/env python3
"""
foundations.csv に人件費可否・複数年継続可否を追加し、
grant_programs.csv に財団情報をjoinしてgrant-data.jsonを再生成する。
"""
import csv, json
from pathlib import Path

OUT  = Path(__file__).parent / "output"
DOCS = Path(__file__).parent.parent.parent / "docs"

# ── 財団ごとの調査データ（2026-05-19 各財団HP実調査）─────────────────
# labor_cost : 可 / 不可 / 一部可 / 要確認
# multi_year : 可 / 不可 / 要確認
# max_years  : 最大助成年数（不明は0）
# notes      : 備考（条件・注意事項）
FOUNDATION_INTEL = {
    "トヨタ財団": {
        "labor_cost": "可", "multi_year": "可", "max_years": 3,
        "notes": "人件費・管理費(10%以内)可。国内助成は最大3年、研究助成は2年固定"},
    "住友財団": {
        "labor_cost": "不可", "multi_year": "可", "max_years": 4,
        "notes": "申請者・共同研究者の人件費は対象外。一般研究は通算最大3年、課題研究は最大4年"},
    "パナソニック教育財団": {
        "labor_cost": "要確認", "multi_year": "可", "max_years": 3,
        "notes": "学校対象の教育研究助成。経費規定に人件費の明示なし。一般助成は最大3回連続可"},
    "日本財団": {
        "labor_cost": "一部可", "multi_year": "不可", "max_years": 1,
        "notes": "自法人役職員への謝金は対象外。外部への謝金は可。原則単年度完了"},
    "東急財団": {
        "labor_cost": "一部可", "multi_year": "可", "max_years": 3,
        "notes": "NPO実務担当者の人件費は可。大学所属研究者の人件費は対象外。最大3年（年度ごとに申請）"},
    "セコム科学技術財団": {
        "labor_cost": "可", "multi_year": "可", "max_years": 4,
        "notes": "使用項目の制約なし。人件費費目が前提。準備1年+本格2〜3年=最大4年。ただし大学所属研究者が対象"},
    "ソニー教育財団": {
        "labor_cost": "要確認", "multi_year": "不可", "max_years": 1,
        "notes": "学校・幼稚園向け表彰型助成。使途自由の賞金形式。NPO等は申請対象外"},
    "積水ハウス財団": {
        "labor_cost": "一部可", "multi_year": "要確認", "max_years": 0,
        "notes": "人件費は助成金額の50%以下まで可。原則単年度だが内容次第で複数年の可能性あり。積水ハウス従業員との協働が必須"},
    "三菱UFJ環境財団": {
        "labor_cost": "不可", "multi_year": "可", "max_years": 3,
        "notes": "謝金・賃金は対象外。里山保全活動支援は原則3年（年30万円）。学校ビオトープは実質単年"},
    "花王芸術科学財団": {
        "labor_cost": "不可", "multi_year": "不可", "max_years": 1,
        "notes": "管理運営費・制作活動費は対象外。美術は2年連続不可、音楽は4年連続不可"},
    "三菱財団": {
        "labor_cost": "一部可", "multi_year": "可", "max_years": 2,
        "notes": "代表・協同研究者への謝金は不可。研究補助者謝金は条件付き可（継続雇用・給与的支払いは不可）。最大2年"},
    "笹川平和財団": {
        "labor_cost": "不可", "multi_year": "要確認", "max_years": 0,
        "notes": "給与補助は対象外。現在はIdea Submission方式に移行し公募助成がほぼ終了"},
    "キリン福祉財団": {
        "labor_cost": "一部可", "multi_year": "不可", "max_years": 1,
        "notes": "役員・スタッフ人件費は不可。外部講師・外部ボランティア謝金は可。原則単年度"},
    "イオン環境財団": {
        "labor_cost": "要確認", "multi_year": "不可", "max_years": 1,
        "notes": "募集要項PDFが画像形式で人件費可否確認不可。助成期間は1年間"},
    "セブン記念財団": {
        "labor_cost": "一部可", "multi_year": "要確認", "max_years": 0,
        "notes": "NPO基盤強化助成では常勤専従職員給与が対象。他区分は外部講師謝金のみ。継続年数の明示なし"},
    "野村財団": {
        "labor_cost": "要確認", "multi_year": "可", "max_years": 3,
        "notes": "アルバイト謝金・外部研究者謝金は可。正規スタッフ給与の可否は明示なし。最長3年"},
    "みずほ福祉助成財団": {
        "labor_cost": "不可", "multi_year": "不可", "max_years": 1,
        "notes": "事業・研究に関わる人件費・謝金は対象外（第三者への謝金は除く）。単年度。過去3年受給団体は応募不可"},
    "大和証券財団": {
        "labor_cost": "不可", "multi_year": "可", "max_years": 3,
        "notes": "運営費・人件費は対象外。外部講師謝礼のみ可。子ども支援助成は最大3年（毎年審査）。ボランティア助成は単年"},
    "旭硝子財団": {
        "labor_cost": "不可", "multi_year": "可", "max_years": 4,
        "notes": "給与・社会保険は不可。アルバイト謝金・外注費は可。プログラムにより最大2年または4年"},
    "朝日新聞文化財団": {
        "labor_cost": "要確認", "multi_year": "可", "max_years": 0,
        "notes": "文化財保護助成は複数年対応（毎年再申請）。芸術活動助成は単年。人件費可否の明示なし"},
    "赤い羽根共同募金": {
        "labor_cost": "可", "multi_year": "可", "max_years": 3,
        "notes": "雇用契約があれば人件費可（日報提出必須）。ボランティア謝金は不可。最大3年（年度ごと審査）"},
    "パブリックリソース財団": {
        "labor_cost": "要確認", "multi_year": "可", "max_years": 2,
        "notes": "運営受託機関のため基金ごとに異なる。一部の基金では人件費が対象経費に記載あり。野村G基金は最大2年"},
    "SOMPO福祉財団": {
        "labor_cost": "一部可", "multi_year": "要確認", "max_years": 0,
        "notes": "住民参加型助成では人件費は助成額の50%上限。基盤強化助成では職員給与が対象経費に含まれる可能性あり"},
    "ニッセイ財団": {
        "labor_cost": "要確認", "multi_year": "可", "max_years": 2,
        "notes": "活動助成（A）では人件費が対象経費に列挙。研究助成では代表者人件費は不可。最大2年（400万円上限）"},
    "ドコモ市民活動助成": {
        "labor_cost": "一部可", "multi_year": "可", "max_years": 3,
        "notes": "常勤スタッフ・アルバイト賃金・外部講師謝礼は可（助成額の50%上限）。子ども分野は最大3年、環境テーマ2は最大2年"},
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
