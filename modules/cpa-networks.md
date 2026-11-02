# CPA networks

Offers from affiliate networks (Involve Asia, Accesstrade, and similar) that pay per **action** rather than marketplace commission: a sale on a brand's own site, a lead (insurance quote, loan or credit-card application), an app install or registration, an approved application. Goal: pick offers with the best net EPC that the creator's audience actually fits, then promote them without voiding the commission.

## Steps

1. **Offer intake**, per offer (from the network dashboard; ask the user for what they can see):
   - payout and model: CPS %, CPL, CPI, CPA (registration / KYC complete / approved)
   - **conversion event**: exactly what counts (submitted form? approved card? first deposit?)
   - **approval rate** and **validation period**: how many actions the advertiser accepts, and when
   - allowed and prohibited traffic sources, geo, cookie duration, required creatives or wording
2. **Evaluate**: for each offer run
   ```bash
   python3 scripts/aff_tools.py earn --payout 350 --approval 55 --clicks 1000 --cvr 3
   ```
   Rank offers on net EPC, not headline payout. When the network shows its own EPC, use it as a sanity check on your CVR assumption.
3. **Fit**: match offer to audience and channel. Finance offers fit money tips, first-jobber, salary, and comparison content; travel fits travel content; apps fit tutorial content. An offer the audience has no reason to want is a low-CVR offer at any payout.
4. **Content**: route to `modules/short-video.md` or `modules/written-content.md` with these CPA angles:
   - **Walkthrough**: screen recording of the signup or application, step by step, with what documents to prepare. Converts best for apps, cards, accounts.
   - **Comparison**: table of fees, interest, cashback, coverage, conditions across 2–4 offers; honest pick per persona.
   - **Problem first**: the situation the product solves ("เงินเดือนออกแล้วหมดไว ใช้บัตรแบบไหนดี").
   Use the advertiser's approved creatives and mandatory wording when supplied.
5. **Links**: tracking link or deeplink per placement with sub-parameters following `modules/links-tracking.md`. Parameter names per network: `ตรวจสอบใน dashboard`.
6. **Lint** everything; finance offers trigger the finance rules and required warnings in `config/claims-rules.json`. Fix every `high`.
7. **Deliver** the output contract. Done when each offer has a verdict backed by tool numbers and every promo piece passed lint.

## Rules that protect the payout

- **Approval rate is the hidden variable.** ฿500 at 30% approval nets less than ฿250 at 90%. Missing approval data → assume conservatively and say so.
- **Validation lag**: actions confirm weeks to months after the click (`ตรวจสอบใน dashboard` per offer). Plan cash flow around confirmed, not pending, earnings.
- **Traffic restrictions are contractual.** Brand-keyword bidding, incentivised signups (paying users to apply), coupon/cashback sites, spam, and self-conversion are commonly prohibited; a breach voids commission and gets the account banned. Read the offer T&C before promoting.
- **Honest copy is the profitable copy.** "อนุมัติง่าย" brings applicants who get rejected; approval rate falls, and the network may cut the payout.
- **Licensed advertisers only**: lending (ธปท.), insurance (คปภ.), investment and digital-asset exchanges (ก.ล.ต.). Offshore forex/binary options and unlicensed loan apps: skip.
- **Leads go to the advertiser's form.** Collecting personal data yourself brings PDPA obligations (consent, privacy notice, security).

## Required wording (finance)

| Offer | Include (check the advertiser's current wording) |
|---|---|
| Personal loan / cash card | กู้เท่าที่จำเป็นและชำระคืนไหว + interest rate range per year |
| Credit card | ใช้จ่ายเท่าที่จำเป็นและชำระคืนได้เต็มจำนวนตามกำหนด + interest rate per year |
| Insurance | ผู้ซื้อควรทำความเข้าใจในรายละเอียดความคุ้มครองและเงื่อนไขก่อนตัดสินใจทำประกันภัยทุกครั้ง |
| Investment / crypto | การลงทุนมีความเสี่ยง ผู้ลงทุนควรศึกษาข้อมูลก่อนตัดสินใจลงทุน (crypto: the higher-risk warning the exchange specifies) |

## Output contract

```
| offer | network | model | payout | event | approval | est. CVR | net EPC | allowed traffic | risk | verdict |
Tool commands + assumptions (สมมติฐาน) listed
Top offer: audience fit + 3 content angles + channel
Links: placement → sub_id table
Compliance: lint summary + required wording included
```
