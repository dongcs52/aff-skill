# Aff-Skill

Claude Skill สำหรับคนทำ affiliate ตลาดไทย ฝั่ง creator: TikTok Shop, Shopee, Lazada และ CPA network (Involve Asia, Accesstrade) เลือกสินค้า/offer คำนวณค่าคอมและ payout เขียนสคริปต์คลิป/ไลฟ์/โพสต์รีวิว วาง sub_id อ่านรายงาน คำนวณจุดคุ้มทุนยิงแอด ตรวจคำโฆษณาผิดกฎ และวางแผน 30 วัน

## ติดตั้ง

```bash
ln -s "$PWD" ~/.claude/skills/aff-skill
```

เปิด session ใหม่แล้วพิมพ์ `/aff-skill` หรือคุยเรื่อง affiliate ตามปกติ (เช่น "เขียนสคริปต์ปักตะกร้าไม้ถูพื้น 30 วิ")

## โครงสร้าง

| Path | หน้าที่ |
|---|---|
| `SKILL.md` | router: เลือก module ตาม intent + กฎที่ใช้ทุกงาน |
| `modules/` | product-pick, cpa-networks, paid-traffic, short-video, live, written-content, links-tracking, analytics, growth-plan, compliance |
| `reference/platforms.md` | กลไกของแต่ละแพลตฟอร์ม (ตัวเลขที่เปลี่ยนบ่อยติดป้าย `ตรวจสอบใน dashboard`) |
| `config/claims-rules.json` | กฎ lint คำโฆษณา (regex + severity + วิธีแก้) |
| `config/scoring.json` | น้ำหนักคะแนนสินค้า |
| `scripts/aff_tools.py` | `earn` / `ads` / `score` / `lint` / `report` (stdlib, Python 3.8+, `.xlsx` ใช้ openpyxl) |

## ใช้ tool ตรง ๆ

```bash
python3 scripts/aff_tools.py earn --price 399 --rate 10:30 --rate 4 --views 20000 --ctr 1 --cvr 4 --target 30000
python3 scripts/aff_tools.py earn --payout 350 --approval 55 --clicks 2000 --cvr 3      # CPA offer
python3 scripts/aff_tools.py ads  --price 399 --rate 14 --spend 1000 --cpc 2 --cvr 4     # ยิงแอดคุ้มไหม
python3 scripts/aff_tools.py score products.json
python3 scripts/aff_tools.py lint caption.txt
python3 scripts/aff_tools.py report shopee-export.csv --by product
```

## Test

```bash
python3 -m unittest discover -s scripts
```

## ปรับแต่ง

- เจอคำเสี่ยงใหม่: เพิ่ม rule ใน `config/claims-rules.json` แล้วเพิ่ม test ใน `scripts/test_aff_tools.py`
- report map column ผิด: ใช้ `--map field=ชื่อคอลัมน์` และเพิ่ม alias ใน `FIELD_ALIASES` ถ้าเจอซ้ำ
- ตัวเลขแพลตฟอร์ม (ค่าคอม, เกณฑ์ follower, attribution window) อัปเดตใน `reference/platforms.md` พร้อมวันที่ตรวจสอบ
