#!/usr/bin/env python3
"""Aff-Skill deterministic tools: earnings math (CPS/CPA), paid-traffic math, product scoring, ad-claim lint, report KPIs.

Standard library only (openpyxl used for .xlsx when installed). Python 3.8+.

    python3 aff_tools.py earn   --price 399 --rate 10 --rate 4 --views 20000 --ctr 1 --cvr 4
    python3 aff_tools.py earn   --payout 300 --approval 60 --clicks 1000 --cvr 3        (CPA offer)
    python3 aff_tools.py ads    --price 399 --rate 14 --spend 1000 --cpc 2 --cvr 4
    python3 aff_tools.py score  products.json
    python3 aff_tools.py lint   draft.txt          (or "-" for stdin)
    python3 aff_tools.py report export.csv --by product
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = SKILL_DIR / "config"


def load_json(name: str) -> dict:
    with open(CONFIG_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def to_num(value) -> float | None:
    """Parse '฿1,234.50', '12%', ' 3 ' into a float. Empty/invalid -> None."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip().replace(",", "")
    if not s:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group()) if m else None


def fmt_thb(x: float | None, digits: int = 2) -> str:
    if x is None:
        return "-"
    return f"{'-' if x < 0 else ''}฿{abs(x):,.{digits}f}"


def fmt_pct(x: float | None, digits: int = 2) -> str:
    if x is None:
        return "-"
    return f"{x * 100:.{digits}f}%"


# ---------------------------------------------------------------- commission

def parse_rate(spec) -> tuple[float, float | None]:
    """'8' -> (8, None); '8:50' -> 8% capped at ฿50 per item."""
    s = str(spec).strip().rstrip("%")
    if ":" in s:
        rate, cap = s.split(":", 1)
        return float(rate.rstrip("%")), float(cap)
    return float(s), None


def parse_rates(value) -> list[tuple[float, float | None]]:
    """Accepts a list, a single number, or '8:50+5'."""
    if value is None or value == "":
        return []
    if isinstance(value, (list, tuple)):
        return [parse_rate(v) for v in value]
    if isinstance(value, (int, float)):
        return [(float(value), None)]
    return [parse_rate(part) for part in str(value).split("+") if part.strip()]


def commission_per_order(price: float, rates, qty: float = 1) -> float:
    per_item = 0.0
    for rate, cap in rates:
        c = price * rate / 100
        if cap is not None:
            c = min(c, cap)
        per_item += c
    return per_item * qty


# ---------------------------------------------------------------- earn

def unit_economics(args) -> dict:
    """Net THB per order (CPS: --price/--rate) or per action (CPA: --payout), after returns and approval."""
    approval = (args.approval if args.approval is not None else 100) / 100
    ret = (args.return_rate or 0) / 100
    if args.payout is not None:
        model, rates, gross = "cpa", [], float(args.payout)
    else:
        if args.price is None or not args.rate:
            raise SystemExit("ต้องใส่ --price กับ --rate (CPS) หรือ --payout (CPA)")
        rates = [parse_rate(r) for r in args.rate]
        model, gross = "cps", commission_per_order(args.price, rates, args.qty)
    return {"model": model, "rates": rates, "gross": gross, "net": gross * (1 - ret) * approval,
            "approval": approval, "return": ret}


def describe_unit(args, u: dict) -> list[str]:
    unit = "action" if u["model"] == "cpa" else "ออเดอร์"
    if u["model"] == "cpa":
        head = f"CPA payout {fmt_thb(u['gross'])}/action"
    else:
        rate_txt = " + ".join(f"{r:g}%" + (f" (cap ฿{c:g}/ชิ้น)" if c is not None else "") for r, c in u["rates"])
        eff = u["gross"] / (args.price * args.qty) * 100 if args.price else 0
        head = (f"ราคา {fmt_thb(args.price)} × {args.qty:g} ชิ้น/ออเดอร์ · ค่าคอม {rate_txt} "
                f"→ {fmt_thb(u['gross'])}/ออเดอร์ (effective {eff:.2f}%)")
    return [head, f"net/{unit} หลังคืน {u['return'] * 100:g}% · approval {u['approval'] * 100:g}%: {fmt_thb(u['net'])}"]


def cmd_earn(args) -> int:
    u = unit_economics(args)
    net = u["net"]
    ctr = args.ctr / 100 if args.ctr is not None else None
    cvr = args.cvr / 100 if args.cvr is not None else None

    out: dict = {
        "model": u["model"],
        "price": args.price,
        "qty_per_order": args.qty,
        "rates": [{"rate_pct": r, "cap_per_item_thb": c} for r, c in u["rates"]],
        "payout": args.payout,
        "commission_per_order_gross": round(u["gross"], 2),
        "return_rate_pct": u["return"] * 100,
        "approval_pct": u["approval"] * 100,
        "commission_per_order_net": round(net, 2),
        "effective_rate_pct": round(u["gross"] / (args.price * args.qty) * 100, 2) if u["model"] == "cps" and args.price else None,
    }
    if cvr is not None:
        out["epc"] = round(net * cvr, 4)

    clicks = args.clicks
    if clicks is None and args.views is not None and ctr is not None:
        clicks = args.views * ctr
    if clicks is not None and cvr is not None:
        orders = clicks * cvr
        earnings = orders * net
        out["funnel"] = {
            "views": args.views,
            "clicks": round(clicks, 1),
            "orders": round(orders, 2),
            "gmv": round(orders * args.price * args.qty, 2) if u["model"] == "cps" else None,
            "earnings": round(earnings, 2),
            "rpm": round(earnings / args.views * 1000, 2) if args.views else None,
        }

    if args.target is not None:
        t: dict = {"target_thb": args.target}
        if net > 0:
            orders_needed = math.ceil(args.target / net)
            t["orders"] = orders_needed
            t["orders_per_day_30d"] = round(orders_needed / 30, 1)
            if cvr:
                clicks_needed = math.ceil(orders_needed / cvr)
                t["clicks"] = clicks_needed
                if ctr:
                    t["views"] = math.ceil(clicks_needed / ctr)
                    t["views_per_day_30d"] = math.ceil(t["views"] / 30)
        out["target"] = t

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    unit = "actions" if u["model"] == "cpa" else "orders"
    print("\n".join(describe_unit(args, u)))
    if "epc" in out:
        print(f"EPC (รายได้ต่อคลิก): {fmt_thb(out['epc'], 3)}")
    if "funnel" in out:
        f = out["funnel"]
        views = f"{f['views']:,.0f} views → " if f["views"] else ""
        gmv = f" · GMV {fmt_thb(f['gmv'], 0)}" if f["gmv"] is not None else ""
        print(f"Funnel: {views}{f['clicks']:,.0f} clicks → {f['orders']:,.1f} {unit}{gmv}")
        print(f"รายได้: {fmt_thb(f['earnings'])}" + (f" · RPM {fmt_thb(f['rpm'])}/1,000 views" if f["rpm"] is not None else ""))
    if "target" in out:
        t = out["target"]
        print(f"เป้า {fmt_thb(t['target_thb'], 0)}/เดือน ต้องการ:")
        if "orders" in t:
            print(f"  {unit} {t['orders']:,} ({t['orders_per_day_30d']}/วัน)")
        if "clicks" in t:
            print(f"  clicks {t['clicks']:,}")
        if "views" in t:
            print(f"  views {t['views']:,} ({t['views_per_day_30d']:,}/วัน)")
        if net <= 0:
            print("  net/ออเดอร์เป็น 0 คำนวณเป้าไม่ได้")
    return 0


# ---------------------------------------------------------------- ads

def ads_math(args) -> dict:
    u = unit_economics(args)
    net, spend = u["net"], args.spend
    cvr = args.cvr / 100
    lp = (args.lp_ctr if args.lp_ctr is not None else 100) / 100
    if args.cpc is not None:
        impressions, ad_ctr = None, None
        ad_clicks = spend / args.cpc
    elif args.cpm is not None and args.ad_ctr is not None:
        ad_ctr = args.ad_ctr / 100
        impressions = spend / args.cpm * 1000
        ad_clicks = impressions * ad_ctr
    else:
        raise SystemExit("ต้องใส่ --cpc หรือ --cpm คู่กับ --ad-ctr")
    out_clicks = ad_clicks * lp
    actions = out_clicks * cvr
    earnings = actions * net
    value_per_ad_click = lp * cvr * net
    roas = earnings / spend if spend else None
    if roas is None or roas < 0.8:
        verdict = "ขาดทุน: ลด CPC/CPM หรือเพิ่ม CVR ก่อนเพิ่มงบ"
    elif roas < 1:
        verdict = "ใกล้คุ้ม: ทดสอบ creative/landing ใหม่ ยังไม่ scale"
    elif roas < 1.3:
        verdict = "กำไรบาง: scale ช้า ๆ (+20%/วัน) แล้วดู ROAS ต่อ"
    else:
        verdict = "กำไร: scale ได้ เฝ้า frequency และ CPM"
    return {
        "unit": u, "spend": spend, "impressions": impressions, "ad_clicks": ad_clicks,
        "merchant_clicks": out_clicks, "actions": actions, "earnings": earnings,
        "profit": earnings - spend, "roas": roas,
        "cost_per_action": spend / actions if actions else None,
        "break_even_cpc": value_per_ad_click,
        "break_even_cpm": value_per_ad_click * ad_ctr * 1000 if ad_ctr else None,
        "max_cost_per_action": net,
        "kill_spend_no_conversion": 2 * net,
        "verdict": verdict,
    }


def cmd_ads(args) -> int:
    m = ads_math(args)
    if args.json:
        u = m.pop("unit")
        m.update({"model": u["model"], "net_per_action": u["net"], "gross_per_action": u["gross"]})
        print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in m.items()}, ensure_ascii=False, indent=2))
        return 0
    u = m["unit"]
    unit = "actions" if u["model"] == "cpa" else "orders"
    print("\n".join(describe_unit(args, u)))
    cost = f"CPC {fmt_thb(args.cpc)}" if args.cpc is not None else f"CPM {fmt_thb(args.cpm)} · ad CTR {args.ad_ctr:g}%"
    lp = f" → landing CTR {args.lp_ctr:g}% → {m['merchant_clicks']:,.0f} merchant clicks" if args.lp_ctr is not None else ""
    print(f"งบ {fmt_thb(m['spend'], 0)} · {cost} → {m['ad_clicks']:,.0f} ad clicks{lp} → {m['actions']:,.1f} {unit} (CVR {args.cvr:g}%)")
    print(f"รายได้ {fmt_thb(m['earnings'])} · กำไร {fmt_thb(m['profit'])} · ROAS {m['roas']:.2f}"
          + (f" · ต้นทุน/{unit[:-1]} {fmt_thb(m['cost_per_action'])}" if m["cost_per_action"] else ""))
    be_cpm = f" · break-even CPM {fmt_thb(m['break_even_cpm'])}" if m["break_even_cpm"] is not None else ""
    print(f"break-even CPC {fmt_thb(m['break_even_cpc'], 3)}{be_cpm} · จ่ายต่อ {unit[:-1]} ได้ไม่เกิน {fmt_thb(m['max_cost_per_action'])}")
    print(f"verdict: {m['verdict']}")
    print(f"kill rule: ใช้งบถึง {fmt_thb(m['kill_spend_no_conversion'], 0)} ต่อ ad set แล้วยังไม่มี conversion → ปิด")
    return 0


# ---------------------------------------------------------------- score

SCALE_FIELDS = ("demand", "demo", "competition", "return_risk", "trend")


def _scale(v, invert: bool = False) -> float | None:
    n = to_num(v)
    if n is None:
        return None
    x = max(0.0, min(1.0, (n - 1) / 4))
    return 1 - x if invert else x


def score_product(p: dict, cfg: dict) -> dict:
    w = cfg["weights"]
    assumed: list[str] = []
    parts: dict[str, float] = {}

    price = to_num(p.get("price"))
    comm = to_num(p.get("commission_thb"))
    if comm is None and price is not None:
        rates = parse_rates(p.get("rate"))
        if rates:
            comm = commission_per_order(price, rates, to_num(p.get("qty")) or 1)
    if comm is None:
        parts["commission"] = 0.5
        assumed.append("commission")
    else:
        parts["commission"] = min(comm / cfg["commission_full_thb"], 1.0)

    for field in SCALE_FIELDS:
        v = _scale(p.get(field), invert=field in ("competition", "return_risk"))
        if v is None:
            assumed.append(field)
            v = 0.5
        parts[field] = v

    tc = cfg["trust"]
    rating, reviews = to_num(p.get("rating")), to_num(p.get("reviews"))
    if rating is None and reviews is None:
        parts["trust"] = 0.5
        assumed.append("trust")
    else:
        r = 0.5 if rating is None else max(0.0, min(1.0, (rating - tc["rating_floor"]) / (tc["rating_full"] - tc["rating_floor"])))
        rv = 0.5 if reviews is None else min(reviews / tc["reviews_full"], 1.0)
        parts["trust"] = r * tc["rating_share"] + rv * (1 - tc["rating_share"])

    lo, hi = cfg["price_sweet_spot_thb"]
    if price is None:
        parts["price_fit"] = 0.5
        assumed.append("price")
    elif price < lo:
        parts["price_fit"] = max(price / lo, 0.2)
    elif price > hi:
        parts["price_fit"] = max(hi / price, 0.2)
    else:
        parts["price_fit"] = 1.0

    raw = sum(parts[k] * w[k] for k in w)
    compliance = str(p.get("compliance") or "low").lower()
    flags: list[str] = []
    score = raw
    if compliance == "medium":
        score -= cfg["compliance"]["medium_penalty"]
        flags.append("compliance medium: ตรวจ claim ก่อนทำ")
    elif compliance == "high":
        score = min(score, cfg["compliance"]["high_cap"])
        flags.append("compliance high: เสี่ยงกฎหมาย")
    score = max(0.0, round(score, 1))

    g = cfg["grades"]
    labels = cfg["labels"]
    grade, verdict = ("A", labels["go"]) if score >= g["go"] else (("B", labels["test"]) if score >= g["test"] else ("C", labels["skip"]))
    if len(assumed) >= cfg.get("max_assumed", 3) + 1 and compliance != "high":
        grade, verdict = "?", labels.get("unknown", "ข้อมูลไม่พอ")
    return {
        "name": p.get("name", "(no name)"),
        "price": price,
        "commission_thb": round(comm, 2) if comm is not None else None,
        "score": score,
        "grade": grade,
        "verdict": verdict,
        "parts": {k: round(v, 2) for k, v in parts.items()},
        "assumed": assumed,
        "flags": flags,
    }


def read_products(path: str) -> list[dict]:
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8-sig")
    stripped = text.lstrip()
    if stripped.startswith("[") or stripped.startswith("{"):
        data = json.loads(text)
        return data if isinstance(data, list) else data.get("products", [data])
    return list(csv.DictReader(io.StringIO(text)))


def cmd_score(args) -> int:
    cfg = load_json("scoring.json")
    results = sorted((score_product(p, cfg) for p in read_products(args.file)), key=lambda r: -r["score"])
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0
    print("| # | สินค้า | ราคา | ค่าคอม/ออเดอร์ | score | grade | verdict | หมายเหตุ |")
    print("|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(results, 1):
        notes = list(r["flags"])
        if r["assumed"]:
            notes.append("assumed: " + ", ".join(r["assumed"]))
        print(f"| {i} | {r['name']} | {fmt_thb(r['price'], 0)} | {fmt_thb(r['commission_thb'])} | {r['score']} | {r['grade']} | {r['verdict']} | {'; '.join(notes)} |")
    return 0


# ---------------------------------------------------------------- lint

ZERO_WIDTH = re.compile("[​‌‍⁠﻿]")
SEV_RANK = {"high": 3, "medium": 2, "low": 1}


def lint_text(text: str, rules_cfg: dict | None = None) -> list[dict]:
    cfg = rules_cfg or load_json("claims-rules.json")
    clean = ZERO_WIDTH.sub("", text)
    work = clean
    for sp in cfg.get("safe_phrases", []):
        work = re.sub(sp, lambda m: " " * len(m.group()), work, flags=re.IGNORECASE)

    raw: list[dict] = []
    for rule in cfg["rules"]:
        for m in re.finditer(rule["pattern"], work, flags=re.IGNORECASE):
            raw.append({"rule": rule, "start": m.start(), "end": m.end()})

    raw.sort(key=lambda f: (-SEV_RANK[f["rule"]["severity"]], f["start"]))
    kept: list[dict] = []
    for f in raw:
        inside = any(
            k["start"] <= f["start"] and f["end"] <= k["end"]
            and SEV_RANK[k["rule"]["severity"]] >= SEV_RANK[f["rule"]["severity"]]
            for k in kept
        )
        if not inside:
            kept.append(f)

    findings = []
    for f in kept:
        rule = f["rule"]
        line_no = clean.count("\n", 0, f["start"]) + 1
        findings.append({
            "id": rule["id"],
            "severity": rule["severity"],
            "line": line_no,
            "match": clean[f["start"]:f["end"]],
            "snippet": _snippet(clean, f["start"], f["end"]),
            "reason": rule["reason"],
            "fix": rule["fix"],
            "context": rule.get("context"),
        })

    for req in cfg.get("requires", []):
        if re.search(req["when"], clean, flags=re.IGNORECASE) and not re.search(req["require"], clean, flags=re.IGNORECASE):
            findings.append({
                "id": req["id"], "severity": req["severity"], "line": None, "match": None, "snippet": None,
                "reason": req["reason"], "fix": req["fix"], "context": req.get("context"),
            })

    findings.sort(key=lambda f: (-SEV_RANK[f["severity"]], f["line"] or 0))
    return findings


def _snippet(text: str, start: int, end: int, pad: int = 18) -> str:
    a, b = max(0, start - pad), min(len(text), end + pad)
    s = text[a:start] + "«" + text[start:end] + "»" + text[end:b]
    return ("…" if a > 0 else "") + s.replace("\n", " ⏎ ") + ("…" if b < len(text) else "")


def cmd_lint(args) -> int:
    if args.text is not None:
        text = args.text
    elif args.file == "-" or args.file is None:
        text = sys.stdin.read()
    else:
        text = Path(args.file).read_text(encoding="utf-8-sig")
    findings = lint_text(text)
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in ("high", "medium", "low")}

    if args.json:
        print(json.dumps({"counts": counts, "findings": findings}, ensure_ascii=False, indent=2))
    else:
        print(f"lint: high {counts['high']} · medium {counts['medium']} · low {counts['low']}")
        for f in findings:
            where = f"line {f['line']}: {f['snippet']}" if f["line"] else "(ทั้งข้อความ)"
            print(f"\n[{f['severity'].upper()}] {f['id']} · {where}")
            print(f"  เหตุผล: {f['reason']}")
            print(f"  แก้: {f['fix']}")
            if f.get("context"):
                print(f"  หมายเหตุ: {f['context']}")
        if not findings:
            print("ไม่พบปัญหา (lint ตรวจได้เฉพาะข้อความ ภาพ/คลิปต้องตรวจเอง)")
    return 2 if counts["high"] else 0


# ---------------------------------------------------------------- report

FIELD_ALIASES: dict[str, list[str]] = {
    "commission": ["totalcommission", "netcommission", "estimatedcommission", "estcommission", "affiliatecommission",
                   "ค่าคอมมิชชั่นทั้งหมด", "ค่าคอมมิชชั่นสุทธิ", "ค่าคอมมิชชั่นโดยประมาณ", "ค่าคอมมิชชั่น", "คอมมิชชั่น",
                   "ค่าคอม", "commission", "earnings", "totalpayout", "payout", "รายได้"],
    "gmv": ["gmv", "purchasevalue", "ordervalue", "orderamount", "sales", "revenue", "ยอดขาย", "มูลค่าคำสั่งซื้อ",
            "มูลค่าการซื้อ", "ราคาสินค้า", "price", "ราคา"],
    "orders": ["orders", "ordercount", "orderscount", "conversions", "จำนวนคำสั่งซื้อ", "คำสั่งซื้อ", "ยอดสั่งซื้อ"],
    "order_id": ["orderid", "ordersn", "orderno", "conversionid", "หมายเลขคำสั่งซื้อ", "รหัสคำสั่งซื้อ", "เลขที่คำสั่งซื้อ"],
    "clicks": ["clicks", "productclicks", "click", "จำนวนคลิก", "คลิกสินค้า", "คลิก"],
    "views": ["views", "videoviews", "view", "ยอดวิว", "การดู"],
    "sub_id": ["subid1", "subid", "subaffid", "trackingid", "sub"],
    "content": ["contentid", "videoid", "liveid", "videotitle", "contenttitle", "ชื่อวิดีโอ", "content", "วิดีโอ"],
    "product": ["itemname", "productname", "ชื่อสินค้า", "ชื่อรายการ", "product", "item", "สินค้า"],
    "channel": ["channel", "trafficsource", "contenttype", "ช่องทาง", "แพลตฟอร์ม", "platform", "ประเภทเนื้อหา", "source"],
    "status": ["orderstatus", "conversionstatus", "สถานะคำสั่งซื้อ", "status", "สถานะ"],
    "date": ["orderdate", "ordertime", "purchasetime", "clicktime", "date", "วันที่"],
}
FIELD_ORDER = ["commission", "order_id", "status", "date", "gmv", "orders", "clicks", "views", "sub_id", "content", "product", "channel"]
NUMERIC_FIELDS = {"commission", "gmv", "orders", "clicks", "views"}
CONTAINS_EXCLUDE = re.compile(r"rate|%|อัตรา|avg|เฉลี่ย|per|ต่อ")
EXCLUDED_STATUS = re.compile(r"cancel|ยกเลิก|unpaid|ไม่สำเร็จ|invalid|ไม่ถูกต้อง|refund|คืนเงิน|return|failed|reject", re.IGNORECASE)
DATE_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M",
                "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d")


def norm_header(h) -> str:
    return re.sub(r"[\s_\-.()\[\]฿:/]|thb", "", str(h or "").strip().lower())


def _mostly_numeric(headers: list[str], header: str, sample: list[list[str]]) -> bool:
    i = headers.index(header)
    vals = [r[i] for r in sample if i < len(r) and str(r[i]).strip()]
    return not vals or sum(to_num(v) is not None for v in vals) / len(vals) >= 0.5


def map_columns(headers: list[str], overrides: dict[str, str], sample: list[list[str]] | None = None) -> dict[str, str]:
    """Match export headers to fields: exact alias first, then contains. Numeric fields need numeric data."""
    sample = sample or []
    mapping: dict[str, str] = {}
    used: set[str] = set()
    for field, header in overrides.items():
        if header not in headers:
            raise SystemExit(f"--map {field}={header!r}: column not found. Columns: {headers}")
        mapping[field] = header
        used.add(header)
    normed = {h: norm_header(h) for h in headers}
    for field in FIELD_ORDER:
        if field in mapping:
            continue
        def ok(h: str) -> bool:
            return h not in used and (field not in NUMERIC_FIELDS or _mostly_numeric(headers, h, sample))

        found = None
        for alias in FIELD_ALIASES[field]:  # pass 1: exact
            found = next((h for h in headers if normed[h] == alias and ok(h)), None)
            if found:
                break
        if not found:
            for alias in FIELD_ALIASES[field]:  # pass 2: contains
                if len(alias) < 3:
                    continue
                found = next((h for h in headers if alias in normed[h]
                              and not CONTAINS_EXCLUDE.search(normed[h]) and ok(h)), None)
                if found:
                    break
        if found:
            mapping[field] = found
            used.add(found)
    return mapping


def _decode(data: bytes) -> str:
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16")
    for enc in ("utf-8-sig", "cp874"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def read_table(path: str, sheet: str | None = None) -> list[list[str]]:
    p = Path(path)
    if p.suffix.lower() in (".xlsx", ".xlsm"):
        try:
            import openpyxl  # type: ignore
        except ImportError:
            raise SystemExit("อ่าน .xlsx ต้องมี openpyxl (pip install openpyxl) หรือ export เป็น CSV")
        wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
        ws = wb[sheet] if sheet else wb.worksheets[0]
        return [["" if c is None else str(c) for c in row] for row in ws.iter_rows(values_only=True)]
    text = _decode(p.read_bytes())
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    return [row for row in csv.reader(io.StringIO(text), dialect)]


def find_header_row(rows: list[list[str]]) -> int:
    """Pick the row (within the first 15) whose cells match the most known aliases; exports often have title rows."""
    all_aliases = {a for aliases in FIELD_ALIASES.values() for a in aliases}
    best, best_hits = 0, -1
    for i, row in enumerate(rows[:15]):
        hits = sum(1 for c in row if norm_header(c) in all_aliases or
                   any(len(a) >= 4 and a in norm_header(c) for a in all_aliases))
        if hits > best_hits:
            best, best_hits = i, hits
    return best


def parse_date(s: str):
    s = str(s).strip().replace("T", " ")[:19]
    for f in DATE_FORMATS:
        try:
            return datetime.strptime(s, f)
        except ValueError:
            continue
    return None


def build_report(rows: list[list[str]], by: str | None, overrides: dict[str, str],
                 min_clicks: int = 100, min_orders: int = 5) -> dict:
    h = find_header_row(rows)
    headers = [c.strip() for c in rows[h]]
    data = [r for r in rows[h + 1:] if any(str(c).strip() for c in r)]
    mapping = map_columns(headers, overrides, data[:200])
    idx = {f: headers.index(col) for f, col in mapping.items()}

    def get(row, field):
        i = idx.get(field)
        return row[i] if i is not None and i < len(row) else None

    if by is None:
        by = next((f for f in ("sub_id", "content", "product", "channel") if f in mapping), None)
    elif by not in mapping:
        raise SystemExit(f"--by {by}: no column mapped to '{by}'. Mapped: {mapping}. Use --map {by}=<column>.")

    rows_are_orders = "orders" not in mapping and ("order_id" in mapping or "commission" in mapping or "gmv" in mapping)
    has_clicks = "clicks" in mapping
    groups: dict[str, dict] = {}
    excluded = 0
    dates = []
    for row in data:
        status = get(row, "status")
        if status and EXCLUDED_STATUS.search(str(status)):
            excluded += 1
            continue
        key = (str(get(row, by)).strip() if by else "ทั้งหมด") or "(ไม่ระบุ)"
        g = groups.setdefault(key, {"rows": 0, "orders": 0.0, "order_ids": set(), "clicks": 0.0, "views": 0.0,
                                    "gmv": 0.0, "commission": 0.0})
        g["rows"] += 1
        if "orders" in mapping:
            g["orders"] += to_num(get(row, "orders")) or 0
        elif "order_id" in mapping:
            oid = str(get(row, "order_id") or "").strip()
            if oid:
                g["order_ids"].add(oid)
        for f in ("clicks", "views", "gmv", "commission"):
            if f in mapping:
                g[f] += to_num(get(row, f)) or 0
        if "date" in mapping:
            d = parse_date(get(row, "date") or "")
            if d:
                dates.append(d)

    def finalize(g: dict) -> dict:
        if "orders" in mapping:
            orders = g["orders"]
        elif "order_id" in mapping:
            orders = float(len(g["order_ids"]))
        elif rows_are_orders:
            orders = float(g["rows"])
        else:
            orders = None
        clicks = g["clicks"] if has_clicks else None
        views = g["views"] if "views" in mapping else None
        gmv = g["gmv"] if "gmv" in mapping else None
        comm = g["commission"] if "commission" in mapping else None
        return {
            "orders": orders, "clicks": clicks, "views": views, "gmv": gmv, "commission": comm,
            "cvr": orders / clicks if clicks and orders is not None else None,
            "epc": comm / clicks if clicks and comm is not None else None,
            "aov": gmv / orders if orders and gmv is not None else None,
            "eff_rate": comm / gmv if gmv and comm is not None else None,
            "rpm": comm / views * 1000 if views and comm is not None else None,
        }

    out_groups = {k: finalize(v) for k, v in groups.items()}
    total_raw = {"rows": 0, "orders": 0.0, "order_ids": set(), "clicks": 0.0, "views": 0.0, "gmv": 0.0, "commission": 0.0}
    for v in groups.values():
        for f in ("rows", "orders", "clicks", "views", "gmv", "commission"):
            total_raw[f] += v[f]
        total_raw["order_ids"] |= v["order_ids"]
    total = finalize(total_raw)

    n = len(out_groups) or 1
    mean_comm = (total["commission"] or 0) / n
    for g in out_groups.values():
        g["verdict"] = _verdict(g, total, mean_comm, min_clicks, min_orders)

    ranked = sorted(out_groups.items(), key=lambda kv: -((kv[1]["commission"] if kv[1]["commission"] is not None else kv[1]["orders"]) or 0))
    return {
        "header_row": h + 1,
        "mapping": mapping,
        "group_by": by,
        "rows_used": sum(v["rows"] for v in groups.values()),
        "rows_excluded": excluded,
        "period": [min(dates).strftime("%Y-%m-%d"), max(dates).strftime("%Y-%m-%d")] if dates else None,
        "total": total,
        "groups": ranked,
    }


def _verdict(g: dict, total: dict, mean_comm: float, min_clicks: int, min_orders: int) -> str:
    orders = g["orders"] or 0
    if g["clicks"] is not None:
        if g["clicks"] < min_clicks and orders < min_orders:
            return "ข้อมูลน้อย"
        if total["epc"] and g["epc"] is not None:
            if g["epc"] >= 1.3 * total["epc"]:
                return "SCALE"
            if total["cvr"] and g["cvr"] is not None and g["cvr"] < 0.5 * total["cvr"] and g["clicks"] >= min_clicks:
                return "FIX"
            if g["epc"] < 0.5 * total["epc"]:
                return "CUT"
        return "KEEP"
    if g["orders"] is not None and orders < min_orders:
        return "ข้อมูลน้อย"
    if g["commission"] is not None and mean_comm:
        if g["commission"] >= 1.3 * mean_comm:
            return "SCALE"
        if g["commission"] <= 0.5 * mean_comm:
            return "LOW"
    return "KEEP"


def cmd_report(args) -> int:
    overrides = {}
    for m in args.map or []:
        if "=" not in m:
            raise SystemExit(f"--map expects field=Column, got {m!r}")
        k, v = m.split("=", 1)
        overrides[k.strip()] = v.strip()
    rep = build_report(read_table(args.file, args.sheet), args.by, overrides, args.min_clicks, args.min_orders)

    if args.json:
        rep_json = dict(rep)
        rep_json["groups"] = [{"group": k, **v} for k, v in rep["groups"]]
        print(json.dumps(rep_json, ensure_ascii=False, indent=2, default=str))
        return 0

    print(f"header row {rep['header_row']} · rows used {rep['rows_used']} · excluded (cancel/unpaid) {rep['rows_excluded']}"
          + (f" · period {rep['period'][0]} → {rep['period'][1]}" if rep["period"] else ""))
    print("column mapping: " + ", ".join(f"{k} ← '{v}'" for k, v in rep["mapping"].items()))
    print(f"group by: {rep['group_by'] or '(none: totals only)'}\n")
    cols = [("orders", lambda v: "-" if v is None else f"{v:,.0f}"),
            ("clicks", lambda v: "-" if v is None else f"{v:,.0f}"),
            ("cvr", fmt_pct), ("gmv", lambda v: fmt_thb(v, 0)), ("commission", fmt_thb),
            ("epc", lambda v: fmt_thb(v, 3)), ("aov", lambda v: fmt_thb(v, 0)), ("eff_rate", fmt_pct),
            ("rpm", fmt_thb)]
    present = [(c, f) for c, f in cols if rep["total"].get(c) is not None]
    print("| " + " | ".join([rep["group_by"] or "group"] + [c for c, _ in present] + ["verdict"]) + " |")
    print("|" + "---|" * (len(present) + 2))
    for key, g in rep["groups"][: args.top]:
        print("| " + " | ".join([key] + [f(g[c]) for c, f in present] + [g["verdict"]]) + " |")
    print("| **รวม** | " + " | ".join(f(rep["total"][c]) for c, f in present) + " | |")
    if len(rep["groups"]) > args.top:
        print(f"\n(แสดง {args.top} จาก {len(rep['groups'])} กลุ่ม ใช้ --top เพื่อดูเพิ่ม)")
    return 0


# ---------------------------------------------------------------- cli

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="aff_tools.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add_unit_args(p):
        p.add_argument("--price", type=float, help="CPS: product price THB")
        p.add_argument("--rate", action="append",
                       help="CPS: commission %% (repeatable to stack). '8:50' = 8%% capped at ฿50 per item")
        p.add_argument("--qty", type=float, default=1, help="CPS: items per order (default 1)")
        p.add_argument("--payout", type=float, help="CPA: flat THB per approved action (lead/สมัคร/ติดตั้ง)")
        p.add_argument("--approval", type=float, help="%% of actions/orders the advertiser approves (default 100)")
        p.add_argument("--return-rate", type=float, default=0, help="%% of orders returned/cancelled")

    e = sub.add_parser("earn", help="commission per order/action, EPC, funnel earnings, income target")
    add_unit_args(e)
    e.add_argument("--views", type=float, help="video/post views")
    e.add_argument("--ctr", type=float, help="%% of views that click the product")
    e.add_argument("--clicks", type=float, help="product clicks (instead of views × ctr)")
    e.add_argument("--cvr", type=float, help="%% of clicks that become orders")
    e.add_argument("--target", type=float, help="monthly income target THB")
    e.add_argument("--json", action="store_true")
    e.set_defaults(func=cmd_earn)

    a = sub.add_parser("ads", help="paid traffic: profit, ROAS, break-even CPC/CPM, kill rule")
    add_unit_args(a)
    a.add_argument("--spend", type=float, required=True, help="ad spend THB")
    a.add_argument("--cpc", type=float, help="cost per ad click THB")
    a.add_argument("--cpm", type=float, help="cost per 1,000 impressions THB (with --ad-ctr)")
    a.add_argument("--ad-ctr", type=float, help="%% of impressions that click the ad")
    a.add_argument("--lp-ctr", type=float, help="%% of landing/pre-lander visitors who click through (default 100 = direct link)")
    a.add_argument("--cvr", type=float, required=True, help="%% of merchant clicks that become orders/actions")
    a.add_argument("--json", action="store_true")
    a.set_defaults(func=cmd_ads)

    s = sub.add_parser("score", help="rank products /100 from JSON or CSV",
                       description="Fields: name, price, rate ('8', '8:50+5', or list) or commission_thb, "
                                   "demand 1-5, competition 1-5 (5=crowded), demo 1-5 (5=result visible in seconds), "
                                   "rating 0-5, reviews, return_risk 1-5 (5=high), trend 1-5, compliance low|medium|high. "
                                   "Missing fields score neutral and are listed as assumed.")
    s.add_argument("file", help="JSON list / CSV path, or - for stdin")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_score)

    l = sub.add_parser("lint", help="Thai ad-claim + disclosure check; exit 2 when a high finding exists")
    l.add_argument("file", nargs="?", help="text file, or - for stdin")
    l.add_argument("--text", help="lint this string instead of a file")
    l.add_argument("--json", action="store_true")
    l.set_defaults(func=cmd_lint)

    r = sub.add_parser("report", help="KPIs + SCALE/FIX/CUT verdicts from a CSV/XLSX export")
    r.add_argument("file")
    r.add_argument("--by", help="group field: sub_id, content, product, channel (default: first found)")
    r.add_argument("--map", action="append", help="override mapping: field=Column Header (repeatable)")
    r.add_argument("--sheet", help="xlsx sheet name")
    r.add_argument("--min-clicks", type=int, default=100)
    r.add_argument("--min-orders", type=int, default=5)
    r.add_argument("--top", type=int, default=30)
    r.add_argument("--json", action="store_true")
    r.set_defaults(func=cmd_report)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
