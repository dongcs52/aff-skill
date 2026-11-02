# LIVE commerce

TikTok LIVE, Shopee Live, Lazada LIVE. Goal: a run-of-show the host and an admin can execute minute by minute.

## Steps

1. Collect: platform, duration (default 2 hours), product list with price/commission/stock/voucher, host count (solo or host + admin), audience (existing followers or cold).
2. Classify products: **traffic product** (cheap, broad appeal, pulls viewers and first orders), **hero product** (best commission per order), **add-on** (bundle-able, low price). Use `scripts/aff_tools.py score` if the list is long.
3. Build the run-of-show with the structure below. Rotate products every 8–12 minutes; repeat the hero every 30–40 minutes for new arrivals.
4. Write the host lines per segment and lint them all.
5. Deliver the output contract. Done when every minute block has a product, a host line, and an admin action.

## Segment structure

| Block | Length | Content |
|---|---|---|
| Opening | 0–5 min | greet, state the best deal of the session, pin the traffic product, ask viewers to comment a keyword |
| Rotation | 8–12 min per product | demo → price → voucher → answer comments → call to buy |
| Recap | every ~15 min | "ใครเพิ่งเข้ามา วันนี้มี___" list the deals again |
| Engagement loop | every ~20 min | like/share target unlocks a deal or giveaway that the seller has actually agreed to |
| Hero repeat | every 30–40 min | full demo of the hero product again |
| Closing | last 5–10 min | final recap, remaining real stock, thank viewers, announce next LIVE time |

## Host line patterns (Thai)

- Hook a newcomer: "เพิ่งเข้ามาใช่ไหม พิมพ์ 1 ในคอมเมนต์ เดี๋ยวบอกโปรของวันนี้"
- Demo: "ดูชัด ๆ นะ ___ (show the result on camera)"
- Answer: read the commenter's name, answer, then tie back to the product.
- Buy call: "กดตะกร้า สินค้าที่ปักหมุดไว้ อันที่___"
- Scarcity: only real stock numbers from the seller.

## Admin checklist

- Before: products added to the LIVE cart, vouchers confirmed with the seller and tested, lighting, stable internet and backup hotspot, phone on charge, banned-word list from lint at hand.
- During: pin the current product, answer price/size questions in comments, flag rude/spam comments, track which product spikes.
- After: export LIVE stats (peak viewers, average watch time, product clicks, orders, GMV per hour) and run `modules/analytics.md`.

## Output contract

```
LIVE plan — <platform> · <duration> · <date/time>
Product roles: traffic: ... | hero: ... | add-on: ...

| เวลา | สินค้า | Host พูด (key lines) | Admin action | Engagement |
|---|---|---|---|---|

Opening script (word for word, ~60s)
Closing script (word for word, ~60s)
Disclosure line said on air + in LIVE title
Lint summary
```

## Rules

- Keep the sale on-platform: buying happens through the pinned product.
- Urgency and giveaways only when real and agreed with the seller.
- Same claim rules as any ad; spoken claims count.
