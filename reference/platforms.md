# Platform mechanics

Stable mechanics only. Numbers that move (commission %, follower thresholds, attribution windows, payout minimums) are marked `ตรวจสอบใน dashboard`: ask the user or tell them where to check, and never state them as fact.

## TikTok Shop

**How the creator earns**
- Add products to **Showcase** (ตะกร้าในโปรไฟล์) from the affiliate product marketplace, then attach the product to a video (ตะกร้าเหลือง / anchor link) or pin it in LIVE.
- Commission rate is set by the seller per product. Paid on settled orders after the return window; returns and cancellations reverse commission.
- **Open collaboration**: any eligible creator can promote at the seller's public rate. **Targeted collaboration**: the seller invites specific creators, often at a higher rate. Worth pitching once the creator has proof (a video with sales).
- **Free samples**: request through the affiliate marketplace; sellers approve based on creator metrics (followers, GMV, category fit). Cheapest way to get product for real footage.
- **Ad authorization (Spark Ads / video code)**: a creator can let the seller boost a winning video as an ad. A bargaining chip for a higher rate or a flat fee.

**Eligibility**: age, follower count, and account-standing requirements for affiliate/Showcase: `ตรวจสอบใน dashboard` (they change).

**Content that the algorithm and policy favour**
- Original footage. Reposted or stitched-without-value clips get "unoriginal content" limits and copyright strikes.
- The product shown and the product linked must match exactly (variant, size, bundle).
- Claims inside the video count as advertising; the same compliance rules as captions apply.
- LIVE: keep the sale on-platform. Pushing viewers to LINE, bank transfer, or another shop breaks policy.

## Shopee

**How the creator earns**
- Join the **Shopee Affiliate Program** (affiliate portal / app), generate links per product, shop, or campaign page.
- Commission typically stacks a **Shopee platform rate** (by category, may be capped per item) with an optional **seller extra commission** (ค่าคอมพิเศษจากร้าน / XTRA-type programs). Exact rates and caps: `ตรวจสอบใน dashboard`. Use `earn --rate 8:50 --rate 5` style to model a capped + extra stack.
- Attribution is last-click within a window after the click; another affiliate's later click overwrites yours. Window length and which items in the cart qualify: `ตรวจสอบใน dashboard`.
- **Custom links accept Sub_id fields** for tracking; use them on every link (`modules/links-tracking.md`).
- **Shopee Video** and **Shopee Live** let creators tag products in-app; buyer intent inside the Shopee app is high, so show price, voucher, and shop rating on screen.

**Payout**: monthly cycle with a minimum threshold and order-validation delay: `ตรวจสอบใน dashboard`.

## Lazada

**How the creator earns**
- Join the **Lazada Affiliate Program**, generate tracked links per product or campaign page.
- Commission by category plus occasional campaign bonuses: `ตรวจสอบใน dashboard`.
- Tracking parameters (sub ID support), attribution window, payout schedule: `ตรวจสอบใน dashboard`.
- Lazada runs in-app LIVE and video surfaces; tagging and eligibility rules: `ตรวจสอบใน dashboard`.

## Shared calendar

Traffic and conversion spike on **double-date mega sales** (9.9, 10.10, 11.11, 12.12, and the smaller monthly double dates) and **payday campaigns** around the 25th to month-end. Plan content to land 1–3 days before, then on the day. Also seasonal: Songkran (April), back-to-school (May), year-end gifting (December).

## Off-platform channels

Facebook, Instagram, YouTube, X, Threads, LINE OA, Pantip, and blogs carry the same Shopee/Lazada affiliate links (TikTok Shop products sell inside TikTok). There the link lives in the post, comment, bio, or a link hub; see `modules/written-content.md` and `modules/links-tracking.md`.
