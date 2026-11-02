# Aff-Skill

[![CI](https://github.com/dongcs52/aff-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/dongcs52/aff-skill/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/dongcs52/aff-skill)](https://github.com/dongcs52/aff-skill/releases/latest)
[![License: MIT](https://img.shields.io/github/license/dongcs52/aff-skill)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Claude Skill](https://img.shields.io/badge/Claude-Skill-D97757?logo=claude&logoColor=white)](https://claude.com/claude-code)

**English** · [ภาษาไทย](README.th.md)

A Claude Skill for affiliate creators in the Thai market. It covers the creator side of TikTok Shop, Shopee, Lazada, and CPA networks (Involve Asia, Accesstrade): picking products and offers, commission and payout math, short-video / LIVE / review scripts, sub_id tracking, performance reports, paid-traffic break-even, ad-claim compliance, and 30-day growth plans.

The skill answers in Thai and keeps platform and metric terms in English (GMV, CTR, CVR, EPC, sub_id, Showcase).

## What it does

| Task | Example prompt | Output |
|---|---|---|
| Product picking | `ไม้ถูพื้นสเปรย์ 399 บาท ค่าคอม 10% ขายแล้ว 12k คุ้มไหม` | Ranked table with a /100 score, verdict (ทำเลย / ทดสอบ / ข้าม), and earnings estimate |
| Short video | `เขียนสคริปต์คลิป 30 วิ` | 3 variants with different angles: shot table, caption, hashtags, disclosure, CTA |
| LIVE | `สคริปต์ไลฟ์ขายของ 1 ชม.` | Run-of-show, product rotation, admin checklist |
| Written content | Facebook, Pantip, blog, LINE OA | Post templates with tracked link placeholders |
| CPA offers | credit cards, loans, insurance, apps | Net EPC after approval rate, mandatory finance warnings |
| Paid traffic | `ยิงแอดเข้าลิงก์คุ้มไหม` | Go / no-go from break-even CPC/CPM, test plan with kill and scale rules |
| Reports | paste a Shopee / TikTok / Lazada export | KPIs per product or sub_id with SCALE / FIX / CUT verdicts |
| Compliance | `แคปชันนี้ผิดกฎไหม` | Lint findings by severity with safer phrasing |

Every number comes from `scripts/aff_tools.py`, and every piece of selling copy passes the compliance lint before delivery.

## Install

Requires [Claude Code](https://claude.com/claude-code).

```bash
git clone https://github.com/dongcs52/aff-skill.git
cd aff-skill
ln -s "$PWD" ~/.claude/skills/aff-skill
```

Start a new session, then type `/aff-skill` or describe your affiliate task in Thai or English.

## Structure

| Path | Purpose |
|---|---|
| `SKILL.md` | Router: picks a module by intent, plus the rules every task follows |
| `modules/` | product-pick, cpa-networks, paid-traffic, short-video, live, written-content, links-tracking, analytics, growth-plan, compliance |
| `reference/platforms.md` | Mechanics of each platform; figures that change often are labelled `ตรวจสอบใน dashboard` (check in your dashboard) |
| `config/claims-rules.json` | Ad-claim lint rules (regex, severity, fix) |
| `config/scoring.json` | Product scoring weights and thresholds |
| `scripts/aff_tools.py` | CLI: `earn` / `ads` / `score` / `lint` / `report` (Python 3.9+ stdlib; `.xlsx` needs `openpyxl`) |

## Using the tool directly

```bash
python3 scripts/aff_tools.py earn --price 399 --rate 10:30 --rate 4 --views 20000 --ctr 1 --cvr 4 --target 30000  # 10% capped at ฿30/item + 4% seller bonus
python3 scripts/aff_tools.py earn --payout 350 --approval 55 --clicks 2000 --cvr 3      # CPA offer
python3 scripts/aff_tools.py ads  --price 399 --rate 14 --spend 1000 --cpc 2 --cvr 4     # is paid traffic profitable?
python3 scripts/aff_tools.py score products.json                                        # rank candidates /100
python3 scripts/aff_tools.py lint caption.txt                                           # exit code 2 on any high finding
python3 scripts/aff_tools.py report shopee-export.csv --by product                      # CSV / XLSX, Thai or English headers
```

Run any subcommand with `--help` for its fields.

## Tests

```bash
python3 -m unittest discover -s scripts
```

## Tuning

- **New risky phrase**: add a rule to `config/claims-rules.json` and a test to `scripts/test_aff_tools.py`.
- **Report maps a column wrongly**: pass `--map field=column_name`; add the alias to `FIELD_ALIASES` if it recurs.
- **Platform figures** (commission rates, follower thresholds, attribution windows): update `reference/platforms.md` with the date you checked.

## Limits

- The compliance lint is a practical check, not legal advice. It reads text only; images and footage need a human check.
- Commission rates, eligibility rules, and payout terms change often. The skill uses your numbers and labels anything else as unverified.
- Marketplace pages block automated fetching, so the skill asks you for price, sold count, rating, and commission instead of scraping them.

## License

[MIT](LICENSE)
