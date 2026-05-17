#!/usr/bin/env python3
"""
YC Grant Platform — Playwright 全自動スクレイパー
対象: 公開財団HP / CANPAN / 補助金ポータル / JFC navi（要セッション）
出力: output/foundations.csv / output/grant_programs.csv / output/adoption_records.csv
"""

import csv, json, re, os, time, sys, argparse
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PWTimeout

# ── 設定 ────────────────────────────────────────────────────────
OUTPUT_DIR   = Path(__file__).parent / "output"
SESSION_FILE = Path(__file__).parent / "jfc_session.json"
LOG_FILE     = OUTPUT_DIR / "collection_log.json"

DELAY        = 1.2    # ページ間ウェイト（秒）
TIMEOUT      = 20000  # ms

FOUNDATION_FIELDS = [
    "id","name","name_short","type","parent_company","url","prefecture",
    "established_year","annual_grant_total_jpy","access_type",
    "adoption_data_public","data_sources","last_scraped","notes",
]
PROGRAM_FIELDS = [
    "foundation_name","program_name","fiscal_year","description",
    "target_org_types","target_issues","target_regions",
    "amount_min_jpy","amount_max_jpy","amount_note",
    "deadline","deadline_month_recurring","application_method",
    "requires_registration","requires_legal_entity","min_operation_years",
    "total_applicants_recent","total_adopted_recent","adoption_rate_pct",
    "grant_url","pdf_url","status","data_completeness","data_source",
]
ADOPTION_FIELDS = [
    "foundation_name","program_name","fiscal_year",
    "grantee_name","project_title","amount_jpy",
    "target_issues","target_region","source_url","data_source",
]

foundations, programs, adoptions, logs = [], [], [], []
fid_counter = [1]

def new_id():
    i = fid_counter[0]; fid_counter[0] += 1; return i

def ts(): return datetime.now().strftime("%H:%M:%S")
def log(msg, lv="INFO"): print(f"[{ts()}][{lv}] {msg}", flush=True)

def add_log(name, url, status, notes=""):
    logs.append({"name":name,"url":url,"status":status,
                 "notes":notes,"at":datetime.now().isoformat()})

def save_all():
    OUTPUT_DIR.mkdir(exist_ok=True)
    def save(rows, fname, fields):
        p = OUTPUT_DIR / fname
        with open(p,"w",newline="",encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader(); w.writerows(rows)
        log(f"保存: {fname} ({len(rows)}件)")
    save(foundations, "foundations.csv",     FOUNDATION_FIELDS)
    save(programs,    "grant_programs.csv",  PROGRAM_FIELDS)
    save(adoptions,   "adoption_records.csv",ADOPTION_FIELDS)
    with open(LOG_FILE,"w",encoding="utf-8") as f:
        json.dump(logs,f,ensure_ascii=False,indent=2)

def wait(page: Page, sel: str, t=TIMEOUT):
    try: page.wait_for_selector(sel, timeout=t); return True
    except PWTimeout: return False

def txt(el): return el.inner_text().strip() if el else ""
def attr(el, a): return el.get_attribute(a) or "" if el else ""

# ── パーサーユーティリティ ───────────────────────────────────────

def parse_amount(s):
    if not s: return None, None
    s = s.replace(",","").replace("，","")
    nums = re.findall(r"([\d.]+)\s*万円?", s)
    if nums:
        vals = [int(float(n)*10000) for n in nums]
        if len(vals)==1:
            return (None,vals[0]) if any(k in s for k in ["上限","以内","まで"]) else (vals[0],vals[0])
        return min(vals), max(vals)
    raw = re.findall(r"\d{4,}", s)
    if raw: return int(raw[0]), int(raw[-1])
    return None, None

def parse_deadline(s):
    if not s: return None, None
    m = re.search(r"(20\d{2})[年/\-](\d{1,2})[月/\-](\d{1,2})", s)
    if m: return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}", int(m.group(2))
    m = re.search(r"令和(\d+)年(\d{1,2})月(\d{1,2})日", s)
    if m:
        y=2018+int(m.group(1))
        return f"{y}-{int(m.group(2)):02d}-{int(m.group(3)):02d}", int(m.group(2))
    m = re.search(r"(\d{1,2})月", s)
    if m: return f"2026-{int(m.group(1)):02d}", int(m.group(1))
    return None, None

ISSUE_MAP = {
    "子ども":"子ども・青少年","青少年":"子ども・青少年","児童":"子ども・青少年",
    "高齢":"高齢者・介護","介護":"高齢者・介護","シニア":"高齢者・介護",
    "障害":"障害者支援","障碍":"障害者支援",
    "女性":"女性・ジェンダー","ジェンダー":"女性・ジェンダー",
    "外国人":"外国人・多文化共生","多文化":"外国人・多文化共生",
    "貧困":"貧困・生活困窮","困窮":"貧困・生活困窮",
    "教育":"教育・学習支援","学習":"教育・学習支援",
    "医療":"医療・保健","保健":"医療・保健","健康":"医療・保健",
    "環境":"環境・気候変動","気候":"環境・気候変動",
    "地域":"地域コミュニティ","コミュニティ":"地域コミュニティ",
    "まちづくり":"まちづくり","都市":"まちづくり",
    "農村":"農山漁村・地方創生","農山":"農山漁村・地方創生","地方創生":"農山漁村・地方創生",
    "文化":"文化・芸術","芸術":"文化・芸術",
    "スポーツ":"スポーツ",
    "防災":"防災・減災","減災":"防災・減災",
    "国際":"国際協力","海外":"国際協力",
    "人権":"人権・法的支援",
    "就労":"就労・雇用","雇用":"就労・雇用",
    "住まい":"住まい","ホームレス":"住まい",
    "食":"食・フードバンク","フードバンク":"食・フードバンク",
    "科学":"科学技術","技術":"科学技術",
}
def classify(text):
    seen, out = set(), []
    for k,v in ISSUE_MAP.items():
        if k in text and v not in seen:
            seen.add(v); out.append(v)
    return "|".join(out) if out else "その他"

# ═══════════════════════════════════════════════════════════════
# ── CANPAN ──────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════

def scrape_canpan(page: Page):
    log("=== CANPAN 助成制度一覧 ===")
    page.goto("https://fields.canpan.info/grant/", timeout=TIMEOUT)
    time.sleep(3)
    page.wait_for_load_state("networkidle")

    # 総件数を取得
    body = page.inner_text("body")
    total_m = re.search(r"(\d+)/(\d+)件", body)
    total = int(total_m.group(2)) if total_m else "?"
    log(f"  CANPAN 総件数: {total}件")

    p_num = 1
    while True:
        log(f"  CANPAN p{p_num}")
        # tr[2]=ヘッダー, tr[3]以降=データ行（2列: 概要列 / ステータス列）
        rows = page.query_selector_all("table tr")
        data_rows = [r for r in rows if len(r.query_selector_all("td")) == 2]

        for row in data_rows:
            try:
                tds = row.query_selector_all("td")
                if len(tds) < 2: continue

                left  = tds[0].text_content().strip()   # 助成制度名・団体・対象
                right = tds[1].text_content().strip()   # ステータス・期間

                # 助成制度名
                m_name = re.search(r"助成制度名\s*\n(.+?)(?:\n|実施団体)", left)
                name = m_name.group(1).strip() if m_name else ""
                if not name:
                    # フォールバック: 最初の非空行
                    lines = [l.strip() for l in left.split("\n") if l.strip() and "助成" not in l[:3]]
                    name = lines[0] if lines else ""
                if not name: continue

                # 実施団体
                m_org = re.search(r"実施団体\s*\n(.+?)(?:\n|対象事業|$)", left)
                org = m_org.group(1).strip() if m_org else ""

                # 対象事業
                m_tgt = re.search(r"対象事業\s*\n(.+?)(?:\n|$)", left)
                target = m_tgt.group(1).strip() if m_tgt else ""

                # URL（td内のリンク）
                link_el = tds[0].query_selector("a[href*='/grant/']")
                gurl = attr(link_el, "href") if link_el else ""
                if gurl and not gurl.startswith("http"):
                    gurl = "https://fields.canpan.info" + gurl

                # 募集ステータス
                if "募集中" in right: status = "active"
                elif "募集予定" in right: status = "upcoming"
                elif "終了" in right: status = "closed"
                else: status = "unknown"

                # 募集期間
                dl_m = re.search(r"(\d{4}年\d{1,2}月\d{1,2}日)(?:.*?～.*?(\d{4}年\d{1,2}月\d{1,2}日))?", right)
                deadline_str = dl_m.group(2) or dl_m.group(1) if dl_m else ""
                dl, dlm = parse_deadline(deadline_str)

                issues = classify(name + " " + target)

                programs.append({
                    "foundation_name": org or "(CANPAN)",
                    "program_name": name,
                    "target_org_types": target,
                    "target_issues": issues,
                    "deadline": dl,
                    "deadline_month_recurring": dlm,
                    "grant_url": gurl,
                    "status": status,
                    "data_completeness": "partial",
                    "data_source": "CANPAN",
                    "fiscal_year": 2026,
                })
            except Exception:
                continue

        # 次ページ（「次へ」リンク）
        nxt = page.query_selector("a:has-text('次へ'), a.next, [rel=next]")
        if not nxt:
            log(f"  CANPAN 最終ページ: {p_num}")
            break
        nxt.click()
        time.sleep(DELAY * 1.5)
        page.wait_for_load_state("networkidle")
        p_num += 1
        if p_num > 50: break

    log(f"CANPAN完了: {len([p for p in programs if p['data_source']=='CANPAN'])}件")

# ═══════════════════════════════════════════════════════════════
# ── 補助金ポータル ───────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════

def scrape_hojyokin(page: Page):
    log("=== 補助金ポータル（NPOフィルタ）===")
    url = "https://hojyokin-portal.jp/subsidies/list?core_tag_id%5B0%5D=227"
    page.goto(url, timeout=TIMEOUT)
    time.sleep(5)
    page.wait_for_load_state("networkidle", timeout=TIMEOUT)

    # 403確認
    body_head = page.inner_text("body")[:50]
    if "Forbidden" in body_head or "Access Denied" in body_head:
        log("  補助金ポータル: 403 Blocked. スキップ", "WARN")
        add_log("補助金ポータル", url, "blocked", notes="403 Forbidden")
        return

    p_num = 1
    while True:
        log(f"  補助金ポータル p{p_num}")
        page.wait_for_load_state("networkidle", timeout=TIMEOUT)

        # 実際のDOM構造: a.c-card-hojokin__wrap > div.c-card-hojokin__*
        cards = page.query_selector_all("a.c-card-hojokin__wrap")
        if not cards:
            cards = page.query_selector_all("[class*='c-card-hojokin']")
        if not cards:
            log(f"  補助金ポータル: カード0件（ページ構造変化の可能性）", "WARN")
            break

        for card in cards:
            try:
                href = attr(card, "href")
                if href and not href.startswith("http"):
                    href = "https://hojyokin-portal.jp" + href

                title_el = card.query_selector(".c-card-hojokin__title, h3")
                name = txt(title_el)

                status_el = card.query_selector(".c-card-hojokin__status, .open, .closed")
                status_text = txt(status_el)
                status = "active" if "公募中" in status_text else ("upcoming" if "予定" in status_text else "unknown")

                # カード全テキストから金額・期限を抽出
                card_text = txt(card)
                amin, amax = parse_amount(card_text)
                dl, dlm = parse_deadline(card_text)

                # 都道府県（設置主体）
                place_el = card.query_selector(".c-card-hojokin__place, [class*='place']")
                org = txt(place_el) or "(補助金ポータル)"

                issues = classify(name + " " + card_text)

                if name:
                    programs.append({
                        "foundation_name": org,
                        "program_name": name,
                        "target_issues": issues,
                        "amount_min_jpy": amin,
                        "amount_max_jpy": amax,
                        "deadline": dl,
                        "deadline_month_recurring": dlm,
                        "grant_url": href,
                        "status": status,
                        "data_completeness": "partial",
                        "data_source": "補助金ポータル",
                        "fiscal_year": 2026,
                    })
            except Exception:
                continue

        # Livewire ページネーション（wire:click）。＞ボタンでクリック
        pager = page.query_selector("[class*='c-pager']")
        nxt = None
        if pager:
            for a in pager.query_selector_all("a"):
                if a.inner_text().strip() in ("＞", ">", "次へ") and not a.get_attribute("data-disabled"):
                    nxt = a
                    break
        if not nxt:
            log(f"  補助金ポータル 最終ページ: {p_num}")
            break
        nxt.click()
        time.sleep(DELAY * 2)
        page.wait_for_load_state("networkidle")
        p_num += 1
        if p_num > 20: break   # 4056件 → 最大200件（20p×10）

    log(f"補助金ポータル完了: {len([p for p in programs if p['data_source']=='補助金ポータル'])}件")

# ═══════════════════════════════════════════════════════════════
# ── 個別財団：トヨタ財団 ─────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════

def scrape_toyota(page: Page):
    log("=== トヨタ財団 ===")
    fid = new_id()
    foundations.append({
        "id": fid, "name": "公益財団法人トヨタ財団",
        "name_short": "トヨタ財団", "type": "企業財団",
        "parent_company": "トヨタ自動車株式会社",
        "url": "https://www.toyotafound.or.jp/",
        "prefecture": "東京都", "adoption_data_public": True,
        "data_sources": "HP直接", "last_scraped": datetime.now().strftime("%Y-%m-%d"),
        "access_type": "public",
    })

    # 助成プログラム一覧
    page.goto("https://www.toyotafound.or.jp/grant/", timeout=TIMEOUT)
    time.sleep(2)
    page.wait_for_load_state("networkidle")

    from urllib.parse import urljoin as _urljoin
    _BASE = "https://www.toyotafound.or.jp"
    grant_urls = list(set(
        _urljoin(_BASE, h) for a in page.query_selector_all("a[href]")
        for h in [attr(a, "href")]
        if h and "/grant/" in h and _urljoin(_BASE, h) != f"{_BASE}/grant/"
    ))

    log(f"  トヨタ 助成プログラムURL: {len(grant_urls)}件")

    for gurl in grant_urls[:20]:
        try:
            page.goto(gurl, timeout=TIMEOUT)
            time.sleep(1.5)
            page.wait_for_load_state("networkidle")

            title_el = page.query_selector("h1,h2.grant-title,.program-title")
            title = txt(title_el) if title_el else page.title()

            body_el = page.query_selector(".grant-detail, .program-detail, main, article, .content")
            body = txt(body_el)[:500] if body_el else ""

            amin, amax = parse_amount(body)
            dl, dlm = parse_deadline(body)
            issues = classify(title + " " + body)

            programs.append({
                "foundation_name": "公益財団法人トヨタ財団",
                "program_name": title,
                "description": body[:300],
                "target_issues": issues,
                "amount_min_jpy": amin, "amount_max_jpy": amax,
                "deadline": dl, "deadline_month_recurring": dlm,
                "grant_url": gurl,
                "status": "active",
                "data_completeness": "partial",
                "data_source": "トヨタ財団HP",
                "fiscal_year": 2026,
            })
        except Exception as e:
            log(f"  トヨタ {gurl}: {e}", "WARN")

    # 採択事例
    page.goto("https://www.toyotafound.or.jp/grant/projects/", timeout=TIMEOUT)
    time.sleep(2)
    page.wait_for_load_state("networkidle")

    proj_items = page.query_selector_all(".project-item,.grant-project,article.project,.result-item")
    log(f"  トヨタ 採択事例: {len(proj_items)}件")

    for item in proj_items[:50]:
        try:
            t_el = item.query_selector("h2,h3,h4,.title,a")
            title = txt(t_el)
            org_el = item.query_selector(".organization,.org,.grantee")
            org    = txt(org_el)
            amt_el = item.query_selector(".amount")
            amin, amax = parse_amount(txt(amt_el))
            yr_el = item.query_selector(".year,.fiscal-year,.date")
            yr    = txt(yr_el)
            yr_m  = re.search(r"20\d{2}", yr)
            year  = int(yr_m.group()) if yr_m else 2025
            issues = classify(title)

            adoptions.append({
                "foundation_name": "公益財団法人トヨタ財団",
                "program_name": "",
                "fiscal_year": year,
                "grantee_name": org,
                "project_title": title,
                "amount_jpy": amin or amax,
                "target_issues": issues,
                "source_url": page.url,
                "data_source": "トヨタ財団HP",
            })
        except Exception:
            continue

    log(f"トヨタ財団完了")

# ═══════════════════════════════════════════════════════════════
# ── 個別財団：住友財団 ──────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════

def scrape_sumitomo(page: Page):
    log("=== 住友財団 ===")
    fid = new_id()
    foundations.append({
        "id": fid, "name": "公益財団法人住友財団",
        "name_short": "住友財団", "type": "企業財団",
        "parent_company": "住友グループ",
        "url": "https://www.sumitomo.or.jp/",
        "prefecture": "東京都", "adoption_data_public": True,
        "data_sources": "HP直接", "last_scraped": datetime.now().strftime("%Y-%m-%d"),
        "access_type": "public",
    })

    BASE = "https://www.sumitomo.or.jp"
    page.goto(BASE, timeout=TIMEOUT)
    time.sleep(2)
    page.wait_for_load_state("networkidle")

    from urllib.parse import urljoin as _uj2
    _KWORDS = ["助成","josekin","grant","kiso","kankyo","jare","culja","kaigai","tenji"]
    _NON_HTML2 = ('.pdf', '.docx', '.xlsx', '.zip', '.doc', '.pptx', '.mp4', '.mov', '.avi', '.jpg', '.png')
    _raw = page.query_selector_all("a[href]")
    prog_links = list(dict.fromkeys([
        _uj2(BASE, h)
        for a in _raw
        for h in [a.get_attribute("href") or ""]
        if any(k in h for k in _KWORDS)
        and h not in ("", "/", BASE+"/")
        and not any(h.lower().endswith(ext) for ext in _NON_HTML2)
    ]))

    for gurl in prog_links[:15]:
        if not gurl.startswith("http"):
            gurl = BASE + gurl
        try:
            page.goto(gurl, timeout=TIMEOUT)
            time.sleep(1.5)
            page.wait_for_load_state("networkidle")

            title_el = page.query_selector("h1,h2,h3")
            title = txt(title_el) if title_el else ""
            body_el = page.query_selector("main,.content,article")
            body = txt(body_el)[:600] if body_el else ""

            amin, amax = parse_amount(body)
            dl, dlm = parse_deadline(body)

            # 採択者リストがあれば取得
            grantee_els = page.query_selector_all("table tr, .grantee, .adoptee")
            for g in grantee_els[:30]:
                cells = g.query_selector_all("td,th")
                if len(cells) >= 2:
                    yr_txt = txt(cells[0])
                    org_txt = txt(cells[1])
                    proj_txt = txt(cells[2]) if len(cells)>2 else ""
                    amt_txt = txt(cells[3]) if len(cells)>3 else ""
                    yr_m = re.search(r"20\d{2}", yr_txt)
                    if org_txt and yr_m:
                        amin2, amax2 = parse_amount(amt_txt)
                        adoptions.append({
                            "foundation_name": "公益財団法人住友財団",
                            "program_name": title,
                            "fiscal_year": int(yr_m.group()),
                            "grantee_name": org_txt,
                            "project_title": proj_txt,
                            "amount_jpy": amin2 or amax2,
                            "target_issues": classify(title),
                            "source_url": gurl,
                            "data_source": "住友財団HP",
                        })

            programs.append({
                "foundation_name": "公益財団法人住友財団",
                "program_name": title,
                "description": body[:300],
                "target_issues": classify(title + " " + body),
                "amount_min_jpy": amin, "amount_max_jpy": amax,
                "deadline": dl, "deadline_month_recurring": dlm,
                "grant_url": gurl,
                "status": "active",
                "data_completeness": "partial",
                "data_source": "住友財団HP",
                "fiscal_year": 2026,
            })
        except Exception as e:
            log(f"  住友 {gurl}: {e}", "WARN")

    log("住友財団完了")

# ═══════════════════════════════════════════════════════════════
# ── 個別財団：パナソニック教育財団 ──────────────────────────────
# ═══════════════════════════════════════════════════════════════

def scrape_panasonic(page: Page):
    log("=== パナソニック教育財団 ===")
    fid = new_id()
    foundations.append({
        "id": fid, "name": "公益財団法人パナソニック教育財団",
        "name_short": "パナソニック教育財団", "type": "企業財団",
        "parent_company": "パナソニックホールディングス",
        "url": "https://www.pef.or.jp/",
        "prefecture": "大阪府", "adoption_data_public": True,
        "data_sources": "HP直接", "last_scraped": datetime.now().strftime("%Y-%m-%d"),
        "access_type": "public",
    })

    BASE = "https://www.pef.or.jp"
    page.goto(BASE, timeout=TIMEOUT)
    time.sleep(2)

    # 助成情報ページ
    for path in ["/josei/", "/grant/", "/about/", "/"]:
        page.goto(f"{BASE}{path}", timeout=TIMEOUT)
        time.sleep(1.5)
        body_el = page.query_selector("main,.content,article,body")
        body = txt(body_el)[:800] if body_el else ""
        if any(k in body for k in ["助成","募集","申請"]):
            amin, amax = parse_amount(body)
            dl, dlm = parse_deadline(body)

            # 応募件数・採択件数を探す
            m_app = re.search(r"(\d+)\s*件.*?応募", body)
            m_ado = re.search(r"(\d+)\s*件.*?採択", body)
            total_app = int(m_app.group(1)) if m_app else None
            total_ado = int(m_ado.group(1)) if m_ado else None
            rate = round(total_ado/total_app*100, 1) if (total_app and total_ado) else None

            programs.append({
                "foundation_name": "公益財団法人パナソニック教育財団",
                "program_name": "実践研究助成",
                "description": body[:300],
                "target_org_types": "学校",
                "target_issues": "教育・学習支援",
                "amount_min_jpy": amin, "amount_max_jpy": amax,
                "deadline": dl, "deadline_month_recurring": dlm,
                "total_applicants_recent": total_app,
                "total_adopted_recent": total_ado,
                "adoption_rate_pct": rate,
                "grant_url": f"{BASE}{path}",
                "status": "active",
                "data_completeness": "partial" if not rate else "full",
                "data_source": "パナソニック教育財団HP",
                "fiscal_year": 2026,
            })
            break

    log("パナソニック教育財団完了")

# ═══════════════════════════════════════════════════════════════
# ── 個別財団：日本財団 ──────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════

def scrape_nippon_foundation(page: Page):
    log("=== 日本財団 ===")
    fid = new_id()
    foundations.append({
        "id": fid, "name": "公益財団法人日本財団",
        "name_short": "日本財団", "type": "日本財団系",
        "url": "https://www.nippon-foundation.or.jp/",
        "prefecture": "東京都", "adoption_data_public": True,
        "data_sources": "HP直接+ポータル",
        "last_scraped": datetime.now().strftime("%Y-%m-%d"),
        "access_type": "public",
    })

    PORTAL = "https://nippon-foundation.my.site.com/GrantPrograms/s/"
    page.goto(PORTAL, timeout=TIMEOUT)
    time.sleep(4)
    page.wait_for_load_state("networkidle")

    items = page.query_selector_all(".slds-card,.grant-card,.program-item,article")
    log(f"  日本財団ポータル: {len(items)}件")

    for item in items:
        try:
            t_el = item.query_selector("h1,h2,h3,h4,.title,a")
            title = txt(t_el)
            if not title: continue
            body_el = item.query_selector("p,.description,.summary")
            body = txt(body_el)
            amin, amax = parse_amount(body)
            dl, dlm = parse_deadline(body)
            issues = classify(title + " " + body)

            programs.append({
                "foundation_name": "公益財団法人日本財団",
                "program_name": title,
                "description": body[:300],
                "target_issues": issues,
                "amount_min_jpy": amin, "amount_max_jpy": amax,
                "deadline": dl, "deadline_month_recurring": dlm,
                "grant_url": PORTAL,
                "status": "active",
                "data_completeness": "partial",
                "data_source": "日本財団ポータル",
                "fiscal_year": 2026,
            })
        except Exception:
            continue

    log("日本財団完了")

# ═══════════════════════════════════════════════════════════════
# ── JFC navi（要ログイン / セッション再利用）───────────────────
# ═══════════════════════════════════════════════════════════════

def login_jfc(page: Page):
    """
    JFC naviに手動ログインしてセッションを保存する。
    初回のみ実行。以降は saved session を再利用。
    """
    log("JFC navi ログイン画面を開きます。ブラウザで手動ログインして下さい。")
    log("ログイン完了後、Enterを押してください。")
    page.goto("https://jyosei-navi.jfc.or.jp/my/index.html", timeout=TIMEOUT)
    page.wait_for_load_state("networkidle")
    input(">>> ブラウザでログイン完了したら Enter を押してください: ")
    page.context.storage_state(path=str(SESSION_FILE))
    log(f"セッション保存: {SESSION_FILE}")

def scrape_jfc(page: Page):
    log("=== 助成財団センター（JFC navi）===")

    SEARCH = "https://jyosei-navi.jfc.or.jp/search/org/search"
    page.goto(SEARCH, timeout=TIMEOUT)
    time.sleep(3)
    page.wait_for_load_state("networkidle")

    body_text = page.inner_text("body")[:100]
    if "JavaScript" in body_text or "ログイン" in body_text or "login" in body_text.lower():
        log("JFC: 未ログインまたはJS必要。--login オプションで先にログインしてください", "WARN")
        add_log("JFC navi", SEARCH, "gated", notes="Cognito認証必要。--loginで先に実行")
        return

    # 検索実行（空クエリ = 全件）
    search_btn = page.query_selector("button[type=submit], .search-btn, input[type=submit]")
    if search_btn:
        search_btn.click()
        time.sleep(2)
        page.wait_for_load_state("networkidle")

    p_num = 1
    while True:
        log(f"  JFC p{p_num}")
        items = page.query_selector_all(".search-result-item,.grant-item,.assist-item,li.result")
        if not items:
            log(f"  JFC p{p_num}: 結果なし")
            break

        for item in items:
            try:
                link = item.query_selector("a")
                if not link: continue
                name = txt(link)
                gurl = attr(link,"href")
                if gurl and not gurl.startswith("http"):
                    gurl = "https://jyosei-navi.jfc.or.jp" + gurl

                org_el = item.query_selector(".org,.foundation")
                org    = txt(org_el)
                amt_el = item.query_selector(".amount")
                amin, amax = parse_amount(txt(amt_el))
                dl_el  = item.query_selector(".deadline,.date")
                dl, dlm = parse_deadline(txt(dl_el))
                cat_el = item.query_selector(".category,.tag,.field")
                issues = classify(txt(cat_el) + " " + name)
                tgt_el = item.query_selector(".target,.target-org")
                target = txt(tgt_el)
                reg_el = item.query_selector(".region,.area")
                region = txt(reg_el)

                programs.append({
                    "foundation_name": org,
                    "program_name": name,
                    "target_org_types": target,
                    "target_issues": issues,
                    "target_regions": region,
                    "amount_min_jpy": amin, "amount_max_jpy": amax,
                    "deadline": dl, "deadline_month_recurring": dlm,
                    "grant_url": gurl,
                    "status": "active",
                    "data_completeness": "partial",
                    "data_source": "JFC navi",
                    "fiscal_year": 2026,
                })
            except Exception:
                continue

        nxt = page.query_selector("a[rel=next],.next a,.pagination .next")
        if not nxt: break
        nxt.click()
        time.sleep(DELAY)
        p_num += 1
        if p_num > 200: break

    log(f"JFC完了: {len([p for p in programs if p['data_source']=='JFC navi'])}件")

# ═══════════════════════════════════════════════════════════════
# ── その他の主要財団（一括処理）────────────────────────────────
# ═══════════════════════════════════════════════════════════════

OTHER_FOUNDATIONS = [
    {"name":"公益財団法人三菱財団","short":"三菱財団","parent":"三菱グループ",
     "url":"https://www.mitsubishi-zaidan.jp/support/","pref":"東京都","type":"企業財団"},
    {"name":"公益財団法人笹川平和財団","short":"笹川平和財団","parent":"日本財団グループ",
     "url":"https://www.spf.org/projects/","pref":"東京都","type":"日本財団系"},
    {"name":"公益財団法人キリン福祉財団","short":"キリン福祉財団","parent":"キリンホールディングス",
     "url":"https://foundation.kirinholdings.com/subsidy/","pref":"東京都","type":"企業財団"},
    {"name":"公益財団法人イオン環境財団","short":"イオン環境財団","parent":"イオングループ",
     "url":"https://www.aeonkankyozaidan.or.jp/subsidy/","pref":"千葉県","type":"企業財団"},
    {"name":"公益財団法人セブン-イレブン記念財団","short":"セブン記念財団","parent":"セブン&アイHD",
     "url":"https://www.7midori.org/","pref":"東京都","type":"企業財団"},
    {"name":"公益財団法人野村財団","short":"野村財団","parent":"野村ホールディングス",
     "url":"https://www.nomurafoundation.or.jp/activity/","pref":"東京都","type":"企業財団"},
    {"name":"公益財団法人みずほ福祉助成財団","short":"みずほ福祉助成財団","parent":"みずほフィナンシャルグループ",
     "url":"https://mizuhofukushi.la.coocan.jp/bosyu/bosyu01.html","pref":"東京都","type":"企業財団"},
    {"name":"公益財団法人大和証券財団","short":"大和証券財団","parent":"大和証券グループ",
     "url":"https://www.daiwa-grp.jp/dsz/grant/","pref":"東京都","type":"企業財団"},
    {"name":"公益財団法人旭硝子財団","short":"旭硝子財団","parent":"AGCグループ",
     "url":"https://www.af-info.or.jp/subsidy/","pref":"東京都","type":"企業財団"},
    {"name":"公益財団法人朝日新聞文化財団","short":"朝日新聞文化財団","parent":"朝日新聞社",
     "url":"https://www.asahizaidan.or.jp/grant/","pref":"東京都","type":"企業財団"},
    {"name":"社会福祉法人中央共同募金会","short":"赤い羽根共同募金","parent":"",
     "url":"https://www.akaihane.or.jp/subsidies/","pref":"東京都","type":"共同募金"},
    {"name":"公益財団法人パブリックリソース財団","short":"パブリックリソース財団","parent":"",
     "url":"https://www.public.or.jp/project/","pref":"東京都","type":"民間財団"},
    {"name":"公益財団法人SOMPO福祉財団","short":"SOMPO福祉財団","parent":"SOMPOホールディングス",
     "url":"https://www.sompo-wf.org/","pref":"東京都","type":"企業財団"},
    {"name":"一般財団法人日本生命財団","short":"ニッセイ財団","parent":"日本生命保険",
     "url":"https://nihonseimei-zaidan.or.jp/","pref":"大阪府","type":"企業財団"},
    {"name":"NPO法人モバイル・コミュニケーション・ファンド","short":"ドコモ市民活動助成","parent":"NTTドコモ",
     "url":"https://www.mcfund.or.jp/jyosei/","pref":"東京都","type":"企業財団"},
]

def scrape_other_foundation(page: Page, info: dict):
    log(f"  {info['short']} ...")
    fid = new_id()
    foundations.append({
        "id": fid,
        "name": info["name"], "name_short": info["short"],
        "type": info["type"], "parent_company": info.get("parent",""),
        "url": info["url"], "prefecture": info.get("pref",""),
        "adoption_data_public": False,
        "data_sources": "HP直接", "last_scraped": datetime.now().strftime("%Y-%m-%d"),
        "access_type": "public",
    })

    from urllib.parse import urljoin as _uj, urlparse as _up
    NON_HTML = ('.pdf', '.docx', '.xlsx', '.zip', '.doc', '.pptx', '.csv')
    _KEYWORDS = ["助成","支援","grant","josei","recruit","募集","申請","公募"]
    base_domain = _up(info["url"]).netloc

    def _get_title(pg):
        for sel in ["h1","h2","h3",".page-title",".entry-title","[class*='title']","[class*='heading']"]:
            el = pg.query_selector(sel)
            if el:
                t = el.inner_text().strip()
                if t and len(t) > 3:
                    return t
        # フォールバック: bodyの最初の意味ある行
        body_text = pg.inner_text("body")
        for line in body_text.split("\n"):
            line = line.strip()
            if len(line) > 5 and any(k in line for k in ["助成","支援","募集","申請","公募","財団"]):
                return line[:80]
        return ""

    def _extract_and_append(pg, href):
        body_el = pg.query_selector("main,.content,article,.grant-detail,.post-content,#main")
        body = txt(body_el)[:600] if body_el else pg.inner_text("body")[:400]
        title = _get_title(pg)
        if not title:
            title = href
        grant_kw = ["助成","支援","公募","募集","申請"]
        if not any(k in (title + body) for k in grant_kw):
            return
        amin, amax = parse_amount(body)
        dl, dlm = parse_deadline(body)
        issues = classify(title + " " + body)
        programs.append({
            "foundation_name": info["name"],
            "program_name": title[:100],
            "description": body[:300],
            "target_issues": issues,
            "amount_min_jpy": amin, "amount_max_jpy": amax,
            "deadline": dl, "deadline_month_recurring": dlm,
            "grant_url": href,
            "status": "active",
            "data_completeness": "partial",
            "data_source": f"{info['short']}HP",
            "fiscal_year": 2026,
        })
        for f in foundations:
            if f["id"] == fid:
                f["adoption_data_public"] = any(k in body for k in ["採択","受賞","選定","助成先"])
                break

    try:
        page.goto(info["url"], timeout=TIMEOUT)
        time.sleep(2)
        page.wait_for_load_state("networkidle")

        # hrefs を先に文字列として全取得（race condition 防止）
        _candidate_hrefs = []
        for _a in page.query_selector_all("a[href]"):
            try:
                _h = _a.get_attribute("href") or ""
                _t = _a.inner_text().strip()
                if any(_h.lower().endswith(ext) for ext in NON_HTML):
                    continue
                if "#" in _h:
                    _h = _h.split("#")[0]   # アンカーを除去して重複排除
                if not any(k in (_h + _t) for k in _KEYWORDS):
                    continue
                _h = _uj(info["url"], _h) if _h and not _h.startswith("http") else _h
                if not _h or _h == info["url"]:
                    continue
                if _up(_h).netloc != base_domain:
                    continue    # 同ドメインのみ
                _candidate_hrefs.append(_h)
            except Exception:
                continue

        unique_hrefs = list(dict.fromkeys(_candidate_hrefs))[:5]

        if unique_hrefs:
            for href in unique_hrefs:
                try:
                    page.goto(href, timeout=TIMEOUT)
                    time.sleep(1.5)
                    page.wait_for_load_state("networkidle")
                    _extract_and_append(page, href)
                except Exception:
                    continue
        else:
            # リンクなし → ベースURLそのものから抽出
            _extract_and_append(page, info["url"])

        # ベースURLから直接抽出（リンク先で取れなかった場合の補完）
        if not any(p["foundation_name"] == info["name"] for p in programs):
            try:
                page.goto(info["url"], timeout=TIMEOUT)
                time.sleep(1.5)
                page.wait_for_load_state("networkidle")
                _extract_and_append(page, info["url"])
            except Exception:
                pass

    except Exception as e:
        log(f"  {info['short']} エラー: {e}", "WARN")
        add_log(info["name"], info["url"], "error", notes=str(e))

# ═══════════════════════════════════════════════════════════════
# ── メイン ──────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="YC Grant Scraper")
    parser.add_argument("--login", action="store_true", help="JFC naviに手動ログインしてセッション保存")
    parser.add_argument("--skip-jfc", action="store_true", help="JFC naviをスキップ")
    parser.add_argument("--headless", action="store_true", default=False, help="ヘッドレスモード（デフォルト: 表示あり）")
    parser.add_argument("--sources", default="all",
                        help="実行するソース: all / canpan / hojyokin / toyota / sumitomo / panasonic / nippon / others / jfc")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)
    log(f"YC Grant Scraper 起動 (sources={args.sources}, headless={args.headless})")

    with sync_playwright() as pw:
        # セッションファイルがあればロード
        ctx_kwargs = {"storage_state": str(SESSION_FILE)} if SESSION_FILE.exists() else {}

        browser: Browser = pw.chromium.launch(headless=args.headless)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            **ctx_kwargs,
        )
        page = context.new_page()

        try:
            # JFCログイン（初回のみ）
            if args.login:
                login_jfc(page)
                log("セッション保存完了。次回から --login なしで実行可能。")
                browser.close()
                return

            src = args.sources.lower()

            if src in ("all", "canpan"):
                scrape_canpan(page)
                save_all()

            if src in ("all", "hojyokin"):
                scrape_hojyokin(page)
                save_all()

            if src in ("all", "toyota"):
                scrape_toyota(page)
                save_all()

            if src in ("all", "sumitomo"):
                scrape_sumitomo(page)
                save_all()

            if src in ("all", "panasonic"):
                scrape_panasonic(page)
                save_all()

            if src in ("all", "nippon"):
                scrape_nippon_foundation(page)
                save_all()

            if src in ("all", "others"):
                log("=== その他主要財団 ===")
                for info in OTHER_FOUNDATIONS:
                    scrape_other_foundation(page, info)
                    time.sleep(DELAY)
                save_all()

            if src in ("all", "jfc") and not args.skip_jfc:
                scrape_jfc(page)
                save_all()

        except KeyboardInterrupt:
            log("中断しました。途中経過を保存します。", "WARN")
        finally:
            save_all()
            browser.close()

    # ── 最終サマリー ──
    from collections import Counter
    src_count = Counter(p.get("data_source","") for p in programs)
    log("=" * 55)
    log("収集完了サマリー")
    log(f"  財団マスタ:     {len(foundations):>5,}件")
    log(f"  助成プログラム: {len(programs):>5,}件")
    log(f"  採択実績:       {len(adoptions):>5,}件")
    log(f"  収集ログ:       {len(logs):>5,}件")
    log("  ソース別:")
    for src, cnt in src_count.most_common():
        log(f"    {src:<25} {cnt:>4}件")
    log(f"  出力先: {OUTPUT_DIR}/")
    log("=" * 55)
    log("次: output/*.csv を NocoDB にインポートしてください")

if __name__ == "__main__":
    main()
