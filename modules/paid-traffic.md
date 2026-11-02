# Paid traffic

Buying traffic (Meta, TikTok, Google ads) toward affiliate content or links. Goal: a go/no-go backed by break-even math, and if go, a test that caps losses before it scales.

## Steps

1. **Permission check first.** Read the program or offer T&C for paid traffic: is paid advertising allowed, which ad platforms, is direct linking allowed, is brand-keyword bidding banned, is a landing page required. Marketplace programs and many CPA offers restrict paid traffic: `ตรวจสอบใน T&C ของ program`. Not allowed → stop and say so.
2. **Unit economics**: net per order/action from `earn` (CPS: `--price --rate --return-rate`; CPA: `--payout --approval`).
3. **Break-even**: run `ads` with realistic costs for the platform and the CVR the creator has seen organically.
   ```bash
   python3 scripts/aff_tools.py ads --price 399 --rate 14 --return-rate 5 --spend 1000 --cpc 2 --cvr 4
   python3 scripts/aff_tools.py ads --payout 350 --approval 55 --spend 3000 --cpm 80 --ad-ctr 1.2 --lp-ctr 40 --cvr 8
   ```
   When break-even CPC/CPM sits below what the platform typically charges, even with an optimistic CVR: no-go. Recommend organic content or a higher-payout product instead. Low-ticket marketplace items usually land here.
4. **Route**, safest first:
   - **Boost a proven organic winner** (TikTok Promote, Meta boost). The creative already converts; lowest risk.
   - **Pre-lander → affiliate link**: a review/comparison page or LINE OA, then the link. Better ad approval and buyer intent; model with `--lp-ctr`.
   - **Direct link** to the merchant: only when the program allows it and the ad platform accepts the destination.
5. **Test plan**: 3 creatives × 1 audience; per ad set budget ≈ the tool's kill-rule amount (2× net per action) per day; run 3 days. Pause any ad set that spends the kill amount with zero conversions. Judge on cost per action against net per action.
6. **Scale rule**: ROAS ≥ 1.3 holds for 3 days → raise budget about 20%/day, duplicate the winning creative to new audiences. Refresh creative when frequency passes ~3 or CTR drops ~30% from its peak.
7. **Track and reconcile**: one sub_id per ad set (`meta_ads_261102_mop_c1`, convention in `modules/links-tracking.md`). The ad platform cannot see the merchant sale; the affiliate report is the truth. Reconcile weekly with `report --by sub_id`, remembering that pending commissions may still be rejected.
8. **Lint** all ad copy; deliver the output contract. Done when the go/no-go cites tool numbers, and when go, every ad set has a budget, sub_id, kill rule, and scale rule.

## Ad-policy hot spots

- Health and beauty: before/after, body-image shaming, weight-loss promises. Same claim rules as `modules/compliance.md`, enforced harder in ads.
- **Personal attributes**: copy that asserts or implies the viewer's finances, health, or other personal traits ("เป็นหนี้อยู่ใช่ไหม", "อ้วนใช่ไหม") is disallowed on Meta. Write about the situation, not the viewer.
- Financial products: ad platforms may require advertiser verification or special categories for credit, insurance, and investment: `ตรวจสอบนโยบายแพลตฟอร์มล่าสุด`.
- Prohibited categories stay prohibited when paid: vapes, gambling, unlicensed finance.

## Output contract

```
Verdict: GO / NO-GO + reason (tool output: net per action, break-even CPC/CPM, ROAS at expected costs)
Permission check: T&C items confirmed / still to confirm
Route: boost | pre-lander | direct
| ad set | audience | creative | budget/day | sub_id | kill rule | scale rule |
Creative briefs (3) → full scripts via modules/short-video.md
Reconcile plan: weekly report --by sub_id
Lint summary
```
