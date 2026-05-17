#!/usr/bin/env python3
"""
YC Grant Platform — 日本助成金データ収集スクリプト
Sources: J-Grants API / 助成財団センター(JFC) / CANPAN
Output:  output/foundations.csv / output/grant_programs.csv
"""

import requests
import csv
import time
import json
import re
import os
import sys
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode

# ── 設定 ────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
LOG_FILE   = os.path.join(OUTPUT_DIR, "collection_log.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ja,en-US;q=0.9",
}

DELAY = 1.5   # リクエスト間隔（秒）
MAX_PAGES = 200  # 1ソースあたりの最大ページ数（安全弁）

ISSUE_TAGS = [
    "子ども・青少年", "高齢者・介護", "障害者支援", "女性・ジェンダー",
    "外国人・多文化共生", "貧困・生活困窮", "教育・学習支援", "医療・保健",
    "環境・気候変動", "地域コミュニティ", "まちづくり", "農山漁村・地方創生",
    "文化・芸術", "スポーツ", "防災・減災", "国際協力", "人権・法的支援",
    "就労・雇用", "住まい", "食・フードバンク", "科学技術", "その他",
]

# ── ユーティリティ ───────────────────────────────────
session = requests.Session()
session.headers.update(HEADERS)
log_entries = []

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)

def safe_get(url, params=None, retries=3):
    for i in range(retries):
        try:
            r = session.get(url, params=params, timeout=20)
            r.raise_for_status()
            time.sleep(DELAY)
            return r
        except Exception as e:
            log(f"GET失敗 ({i+1}/{retries}): {url} — {e}", "WARN")
            time.sleep(DELAY * 3)
    log(f"全リトライ失敗: {url}", "ERROR")
    return None

def save_csv(rows, filepath, fieldnames):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    log(f"保存完了: {filepath} ({len(rows)}件)")

def add_log(foundation_name, url, status, bypass="", result="", notes=""):
    log_entries.append({
        "foundation_name": foundation_name,
        "url": url,
        "access_status": status,
        "bypass_attempted": bypass,
        "bypass_result": result,
        "notes": notes,
        "scraped_at": datetime.now().isoformat(),
    })

def save_log():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log_entries, f, ensure_ascii=False, indent=2)

# ── J-Grants API ────────────────────────────────────
# デジタル庁が提供する補助金情報API
# ドキュメント: https://www.jgrants-portal.go.jp/
# 本番エンドポイント: https://api.jgrants-portal.go.jp/exp/v1/public/grants

JGRANTS_BASE = "https://api.jgrants-portal.go.jp/exp/v1/public"

def fetch_jgrants():
    log("=== J-Grants API 収集開始 ===")
    programs = []

    # まずAPIが叩けるか確認
    test_url = f"{JGRANTS_BASE}/grants"
    test_params = {"keyword": "", "acceptance": "0", "limit": 10, "offset": 0}
    r = safe_get(test_url, params=test_params)

    if r is None or r.status_code != 200:
        log("J-Grants APIに接続できません。スキップします。", "WARN")
        add_log("J-Grants", test_url, "error", notes="API接続失敗")
        return programs

    try:
        data = r.json()
    except Exception:
        log("J-Grants APIのレスポンスがJSONではありません。", "WARN")
        return programs

    total = data.get("totalCount", 0)
    log(f"J-Grants 総件数: {total}件")

    limit = 100
    offset = 0
    page = 1

    while offset < total and page <= MAX_PAGES:
        log(f"  J-Grants ページ {page} ({offset+1}〜{min(offset+limit, total)}/{total})")
        params = {"keyword": "", "acceptance": "0", "limit": limit, "offset": offset}
        r = safe_get(test_url, params=params)
        if r is None:
            break

        items = r.json().get("grants", [])
        if not items:
            break

        for item in items:
            programs.append({
                "foundation_name": item.get("subOrganizationName") or item.get("organizationName", ""),
                "program_name": item.get("title", ""),
                "description": item.get("summary", ""),
                "target_org_types": item.get("targetPersonType", ""),
                "target_issues": "",
                "target_regions": item.get("targetArea", ""),
                "amount_note": item.get("subsidy", ""),
                "deadline": item.get("acceptanceEndDate", ""),
                "application_method": "J-Grants電子申請",
                "requires_registration": False,
                "grant_url": f"https://www.jgrants-portal.go.jp/subsidy/{item.get('id', '')}",
                "status": "active" if item.get("acceptance") == "0" else "closed",
                "data_completeness": "partial",
                "data_source": "J-Grants API",
                "fiscal_year": 2026,
                "type": "省庁系",
            })

        offset += limit
        page += 1

    log(f"J-Grants 収集完了: {len(programs)}件")
    return programs

# ── 助成財団センター (JFC) ───────────────────────────
# https://jyosei-navi.jfc.or.jp/

JFC_BASE = "https://jyosei-navi.jfc.or.jp"

def parse_jfc_list_page(soup):
    """助成財団センターの一覧ページから財団情報を抽出"""
    items = []
    # 検索結果のリストアイテムを探す（実際のDOM構造に合わせて調整が必要）
    rows = soup.select(".search-result-item, .grant-item, li.result, .assist-item")
    if not rows:
        # テーブル形式の場合
        rows = soup.select("table.result-table tr")[1:]  # ヘッダー除く

    for row in rows:
        try:
            name_el = row.select_one("a, .foundation-name, .name, h3, h4")
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            url = name_el.get("href", "")
            if url and not url.startswith("http"):
                url = urljoin(JFC_BASE, url)

            items.append({
                "name": name,
                "url": url,
                "data_source": "助成財団センター",
            })
        except Exception:
            continue
    return items

def fetch_jfc_member_list():
    """助成財団センター 会員名簿から財団URLリストを取得"""
    log("=== 助成財団センター 会員名簿 収集 ===")
    foundations = []
    url = f"{JFC_BASE}/whatis/member/"
    r = safe_get(url)
    if r is None:
        add_log("助成財団センター会員名簿", url, "error")
        return foundations

    soup = BeautifulSoup(r.text, "lxml")
    # 会員リストのリンクを全て取得
    links = soup.select("a[href]")
    for link in links:
        href = link.get("href", "")
        text = link.get_text(strip=True)
        if not text or len(text) < 3:
            continue
        # 財団名っぽいもの（「財団」「基金」「協会」「センター」を含む）
        if any(kw in text for kw in ["財団", "基金", "協会", "センター", "振興会", "共済"]):
            full_url = urljoin(JFC_BASE, href) if not href.startswith("http") else href
            foundations.append({
                "name": text,
                "url": full_url,
                "type": "民間財団",
                "data_source": "助成財団センター会員名簿",
            })

    log(f"会員名簿から {len(foundations)}件 取得")
    return foundations

def fetch_jfc_search():
    """助成財団センター 助成プログラム検索から全件取得"""
    log("=== 助成財団センター 助成プログラム検索 ===")
    programs = []

    # 検索URL（NPO・市民団体向け）
    search_url = f"{JFC_BASE}/search/search/assist/list"
    params = {"target": "2", "page": 1}  # target=2 がNPO向けの場合が多い

    page = 1
    while page <= MAX_PAGES:
        log(f"  JFC 検索ページ {page}")
        params["page"] = page
        r = safe_get(search_url, params=params)
        if r is None:
            break

        soup = BeautifulSoup(r.text, "lxml")

        # ページネーションの最終ページを確認
        next_btn = soup.select_one("a.next, .pagination .next, [rel=next]")

        # 結果アイテムを抽出
        items = soup.select(".assist-item, .result-item, .grant-row, article, .search-item")
        if not items:
            # テーブル行を試す
            items = soup.select("table tr")[1:]

        if not items:
            log(f"  ページ {page} に結果なし、終了")
            break

        for item in items:
            try:
                program = parse_jfc_program_item(item)
                if program:
                    programs.append(program)
            except Exception as e:
                continue

        if not next_btn:
            log(f"  最終ページ: {page}")
            break

        page += 1

    log(f"JFC 助成プログラム収集: {len(programs)}件")
    return programs

def parse_jfc_program_item(el):
    """JFC検索結果の個別アイテムをパース"""
    name_el = el.select_one("a, h3, h4, .title, .program-name")
    if not name_el:
        return None

    program_name = name_el.get_text(strip=True)
    url = name_el.get("href", "")
    if url and not url.startswith("http"):
        url = urljoin(JFC_BASE, url)

    # 財団名
    org_el = el.select_one(".org-name, .foundation, .organization, .grant-org")
    foundation_name = org_el.get_text(strip=True) if org_el else ""

    # 金額
    amount_el = el.select_one(".amount, .grant-amount, [class*=amount]")
    amount_text = amount_el.get_text(strip=True) if amount_el else ""
    amount_min, amount_max = parse_amount(amount_text)

    # 締め切り
    deadline_el = el.select_one(".deadline, .date, [class*=deadline], [class*=date]")
    deadline_text = deadline_el.get_text(strip=True) if deadline_el else ""
    deadline = parse_deadline(deadline_text)

    # 対象
    target_el = el.select_one(".target, [class*=target]")
    target_text = target_el.get_text(strip=True) if target_el else ""

    return {
        "foundation_name": foundation_name,
        "program_name": program_name,
        "target_org_types": target_text,
        "amount_min_jpy": amount_min,
        "amount_max_jpy": amount_max,
        "amount_note": amount_text,
        "deadline": deadline,
        "grant_url": url,
        "status": "active",
        "data_completeness": "partial",
        "data_source": "助成財団センター",
        "fiscal_year": 2026,
    }

# ── CANPAN ──────────────────────────────────────────
CANPAN_BASE = "https://fields.canpan.info"

def fetch_canpan():
    log("=== CANPAN 助成制度一覧 収集開始 ===")
    programs = []

    page = 1
    while page <= MAX_PAGES:
        log(f"  CANPAN ページ {page}")
        url = f"{CANPAN_BASE}/grant/"
        params = {"page": page}
        r = safe_get(url, params=params)
        if r is None:
            break

        soup = BeautifulSoup(r.text, "lxml")

        # 結果アイテム
        items = soup.select(".grant-list li, .grant-item, article.grant, .assist-list li")
        if not items:
            items = soup.select("ul.list > li, .list-item")
        if not items:
            log(f"  CANPAN ページ {page} に結果なし")
            break

        for item in items:
            try:
                program = parse_canpan_item(item)
                if program:
                    programs.append(program)
            except Exception:
                continue

        # 次ページ確認
        next_link = soup.select_one("a[rel=next], .next a, .pagination .next")
        if not next_link:
            log(f"  CANPAN 最終ページ: {page}")
            break

        page += 1

    log(f"CANPAN 収集完了: {len(programs)}件")
    return programs

def parse_canpan_item(el):
    name_el = el.select_one("a, h3, h4, .title")
    if not name_el:
        return None

    program_name = name_el.get_text(strip=True)
    url = name_el.get("href", "")
    if url and not url.startswith("http"):
        url = urljoin(CANPAN_BASE, url)

    org_el = el.select_one(".org, .organization, .group")
    foundation_name = org_el.get_text(strip=True) if org_el else ""

    amount_el = el.select_one(".amount, [class*=amount]")
    amount_text = amount_el.get_text(strip=True) if amount_el else ""
    amount_min, amount_max = parse_amount(amount_text)

    deadline_el = el.select_one(".deadline, .date, [class*=date]")
    deadline_text = deadline_el.get_text(strip=True) if deadline_el else ""

    issue_el = el.select_one(".category, .tag, .issue, [class*=category]")
    issue_text = issue_el.get_text(strip=True) if issue_el else ""
    issues = classify_issues(issue_text)

    region_el = el.select_one(".region, .area, [class*=region]")
    region_text = region_el.get_text(strip=True) if region_el else ""

    return {
        "foundation_name": foundation_name,
        "program_name": program_name,
        "target_issues": "|".join(issues),
        "target_regions": region_text,
        "amount_min_jpy": amount_min,
        "amount_max_jpy": amount_max,
        "amount_note": amount_text,
        "deadline": parse_deadline(deadline_text),
        "grant_url": url,
        "status": "active",
        "data_completeness": "partial",
        "data_source": "CANPAN",
        "fiscal_year": 2026,
    }

# ── ユーティリティ関数 ───────────────────────────────

def parse_amount(text):
    """「100万円〜500万円」「上限200万円」等をパース → (min, max)"""
    if not text:
        return None, None
    text = text.replace(",", "").replace("，", "")
    nums = re.findall(r"(\d+(?:\.\d+)?)\s*万円?", text)
    if not nums:
        nums_yen = re.findall(r"(\d{4,})", text)
        if len(nums_yen) == 1:
            return int(nums_yen[0]), int(nums_yen[0])
        if len(nums_yen) >= 2:
            return int(nums_yen[0]), int(nums_yen[-1])
        return None, None
    vals = [int(float(n) * 10000) for n in nums]
    if len(vals) == 1:
        if "上限" in text or "以内" in text or "まで" in text:
            return None, vals[0]
        return vals[0], vals[0]
    return min(vals), max(vals)

def parse_deadline(text):
    """「2026年11月30日」「令和8年3月31日」等をISO形式に変換"""
    if not text:
        return None
    text = text.strip()
    # 西暦
    m = re.search(r"(20\d{2})[年/\-](\d{1,2})[月/\-](\d{1,2})", text)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    # 令和
    m = re.search(r"令和(\d+)年(\d{1,2})月(\d{1,2})日", text)
    if m:
        year = 2018 + int(m.group(1))
        return f"{year}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    # 月のみ
    m = re.search(r"(\d{1,2})月", text)
    if m:
        return f"2026-{int(m.group(1)):02d}"
    return None

def classify_issues(text):
    """テキストから社会課題タグを分類"""
    matched = []
    mapping = {
        "子ども": "子ども・青少年", "青少年": "子ども・青少年", "児童": "子ども・青少年",
        "高齢": "高齢者・介護", "介護": "高齢者・介護", "シニア": "高齢者・介護",
        "障害": "障害者支援", "障碍": "障害者支援",
        "女性": "女性・ジェンダー", "ジェンダー": "女性・ジェンダー",
        "外国人": "外国人・多文化共生", "多文化": "外国人・多文化共生",
        "貧困": "貧困・生活困窮", "困窮": "貧困・生活困窮",
        "教育": "教育・学習支援", "学習": "教育・学習支援",
        "医療": "医療・保健", "保健": "医療・保健", "健康": "医療・保健",
        "環境": "環境・気候変動", "気候": "環境・気候変動",
        "地域": "地域コミュニティ", "コミュニティ": "地域コミュニティ",
        "まちづくり": "まちづくり", "都市": "まちづくり",
        "農村": "農山漁村・地方創生", "農山": "農山漁村・地方創生", "地方創生": "農山漁村・地方創生",
        "文化": "文化・芸術", "芸術": "文化・芸術",
        "スポーツ": "スポーツ",
        "防災": "防災・減災", "減災": "防災・減災",
        "国際": "国際協力", "海外": "国際協力",
        "人権": "人権・法的支援",
        "就労": "就労・雇用", "雇用": "就労・雇用",
        "住まい": "住まい", "ホームレス": "住まい",
        "食": "食・フードバンク", "フードバンク": "食・フードバンク",
        "科学": "科学技術", "技術": "科学技術",
    }
    for kw, tag in mapping.items():
        if kw in text and tag not in matched:
            matched.append(tag)
    return matched if matched else ["その他"]

def deduplicate(rows, key_field):
    """keyフィールドで重複排除"""
    seen = {}
    for row in rows:
        key = row.get(key_field, "").strip()
        if not key:
            continue
        if key not in seen:
            seen[key] = row
        else:
            # 情報量が多い方を残す
            existing = seen[key]
            if sum(1 for v in row.values() if v) > sum(1 for v in existing.values() if v):
                seen[key] = row
    return list(seen.values())

# ── フィールド定義 ───────────────────────────────────

FOUNDATION_FIELDS = [
    "name", "name_short", "type", "parent_company", "url",
    "prefecture", "established_year", "annual_grant_total_jpy",
    "contact_email", "contact_form_url", "access_type",
    "adoption_data_public", "data_sources", "last_scraped", "notes",
]

PROGRAM_FIELDS = [
    "foundation_name", "program_name", "fiscal_year", "description",
    "target_org_types", "target_issues", "target_regions",
    "amount_min_jpy", "amount_max_jpy", "amount_note",
    "deadline", "deadline_type", "deadline_month_recurring",
    "application_method", "requires_registration", "requires_legal_entity",
    "min_operation_years", "adoption_rate_pct",
    "grant_url", "pdf_url", "status", "data_completeness",
    "data_source", "type",
]

# ── メイン ───────────────────────────────────────────

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    log("YC Grant Collector 起動")
    log(f"出力先: {OUTPUT_DIR}")

    all_foundations = []
    all_programs = []

    # ── Source 1: J-Grants API ──
    try:
        jg_programs = fetch_jgrants()
        all_programs.extend(jg_programs)
    except Exception as e:
        log(f"J-Grants 収集エラー: {e}", "ERROR")

    # ── Source 2: 助成財団センター ──
    try:
        jfc_foundations = fetch_jfc_member_list()
        all_foundations.extend(jfc_foundations)
        jfc_programs = fetch_jfc_search()
        all_programs.extend(jfc_programs)
    except Exception as e:
        log(f"JFC 収集エラー: {e}", "ERROR")

    # ── Source 3: CANPAN ──
    try:
        canpan_programs = fetch_canpan()
        all_programs.extend(canpan_programs)
    except Exception as e:
        log(f"CANPAN 収集エラー: {e}", "ERROR")

    # ── 重複排除・後処理 ──
    log("=== 重複排除・後処理 ===")

    for f in all_foundations:
        f.setdefault("access_type", "public")
        f.setdefault("last_scraped", datetime.now().strftime("%Y-%m-%d"))
        f.setdefault("adoption_data_public", False)
        f.setdefault("type", "民間財団")

    for p in all_programs:
        p.setdefault("fiscal_year", 2026)
        p.setdefault("status", "unknown")
        p.setdefault("data_completeness", "partial")
        p.setdefault("deadline_type", "annual")
        if p.get("deadline"):
            m = re.match(r"\d{4}-(\d{2})", str(p["deadline"]))
            if m:
                p["deadline_month_recurring"] = int(m.group(1))

    programs_deduped = deduplicate(all_programs, "program_name")

    # ── CSV出力 ──
    save_csv(
        all_foundations,
        os.path.join(OUTPUT_DIR, "foundations.csv"),
        FOUNDATION_FIELDS,
    )
    save_csv(
        programs_deduped,
        os.path.join(OUTPUT_DIR, "grant_programs.csv"),
        PROGRAM_FIELDS,
    )
    save_log()

    # ── サマリー ──
    log("=" * 50)
    log(f"収集完了サマリー")
    log(f"  財団マスタ:     {len(all_foundations):,}件")
    log(f"  助成プログラム: {len(programs_deduped):,}件 (重複除去後)")
    log(f"  収集ログ:       {len(log_entries):,}件")
    log(f"  出力先:         {OUTPUT_DIR}/")
    log("=" * 50)
    log("次のステップ: output/*.csv を NocoDB にインポートしてください")

if __name__ == "__main__":
    main()
