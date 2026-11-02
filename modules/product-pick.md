# Product picking and commission math

Goal: a ranked shortlist with a verdict per product (ทำเลย / ทดสอบ / ข้าม) and the earnings it can realistically produce.

## Steps

1. **Collect per product**: name, price (THB), commission rate(s) with any cap, demand signal (sold/month, trending), shop or product rating and review count, competition (how many creators already push it: search the product on TikTok / check Showcase counts), demo-ability, return risk, compliance category. Missing fields: ask once for the batch, then score with what exists; the tool marks unknowns as neutral and lists them. A pasted product URL gives the title (decode it from the URL slug) but marketplace pages and APIs block automated fetching, and commission is only visible in the affiliate app: ask the user to paste price, sold count, rating/reviews, and commission % from the app instead of retrying the fetch.
2. **Score**: write the candidates to a JSON or CSV file in the scratchpad and run
   ```bash
   python3 scripts/aff_tools.py score products.json
   ```
   Field meanings: `score --help`. Weights: `config/scoring.json`. Convert raw signals to the 1–5 scales with this rubric, and tell the user the value you chose for each:

   | Field | 1 | 3 | 5 |
   |---|---|---|---|
   | demand | under ~100 sold, no buzz | ~1k–5k sold | 10k+ sold or visibly trending |
   | competition | few or no creators on it | some videos, none dominant | many creators, top videos with big views |
   | demo | benefit invisible on camera | visible with explanation | result visible within 3 seconds |
   | return_risk | standard, durable goods | some fit/expectation risk | size/colour-sensitive or fragile |
   | trend | declining or off-season | stable | rising, or fits the next mega-sale |
3. **Earnings for the top 3**: run `earn` with a funnel. Use the user's real CTR/CVR when they have history; otherwise label the defaults below as สมมติฐาน.
   ```bash
   python3 scripts/aff_tools.py earn --price 399 --rate 10 --rate 4 --views 20000 --ctr 1 --cvr 4 --return-rate 5
   python3 scripts/aff_tools.py earn --price 399 --rate 10 --cvr 4 --ctr 1 --target 30000   # what it takes to hit 30k/month
   ```
4. **Deliver** (done when every candidate has a verdict and the top picks have an angle):
   - Ranked table: product · score · grade · commission/order · verdict · one-line reason.
   - For each ทำเลย/ทดสอบ product: the content angle that fits it (demo, problem-solution, comparison, price shock) and the format (short video / LIVE / review post).
   - Earnings estimate for the top picks with assumptions listed.
   - Compliance flags (supplement, cosmetic, medical device, prohibited category) pointing to `modules/compliance.md`.

## Selection heuristics

- **Baht per order beats percent.** 8% of ฿1,290 pays more than 20% of ฿149. Rank on commission per order, then on demand.
- **Price sweet spot for short video**: impulse range (default ฿99–699 in `config/scoring.json`). Higher tickets convert better through LIVE, long reviews, and comparison content where trust builds.
- **Demo-able in 3 seconds**: visible result on camera (cleaning, kitchen, gadgets, organisers, car care, pet) beats products whose benefit is invisible or slow.
- **Trust floor**: low shop rating or few reviews turns clicks into abandoned carts and returns. Check the shop before the product.
- **Return-prone categories** (size-sensitive fashion, colour-sensitive cosmetics) erode net commission; model them with `--return-rate`.
- **Crowded products** need a fresh angle; a product every creator pushes rewards the creator with the best hook or the lowest-price shop.
- **Compliance gate**: supplements, cosmetics with treatment positioning, medical devices, and anything implying cure carry legal risk. Prohibited outright: e-cigarettes/vapes, gambling. Alcoholic drinks: advertising is heavily restricted. The tool caps compliance-high products.
- **Samples first**: when the product is a test, request a free sample (TikTok Shop) before buying it.

## Default funnel assumptions (replace with real data)

| Metric | Short video | LIVE | Written post |
|---|---|---|---|
| CTR (views → product clicks) | 0.5–2% | 2–8% | 1–5% |
| CVR (clicks → orders) | 2–6% | 4–12% | 1–4% |

Say these are rough starting points, not benchmarks, whenever you use them.
