# Compliance

Thai advertising law treats affiliate content as advertising: the creator who publishes a claim can be liable alongside the seller. Goal: copy that sells with claims the creator can stand behind.

This is practical guidance, not legal advice. For high-stakes cases (a brand deal on supplements, a complaint already received) tell the user to confirm with a lawyer or the regulator.

## Steps

1. Run the lint on the full text (spoken lines, on-screen text, caption, hashtags):
   ```bash
   python3 scripts/aff_tools.py lint draft.txt          # or: echo "<text>" | python3 scripts/aff_tools.py lint -
   ```
2. **high** → rewrite using the safe-phrasing table; re-lint until no high remains.
3. **medium** → decide in context (e.g. "100%" for "ผ้าฝ้าย 100%" is a fact; for results it is a claim) and tell the user the call you made.
4. Check the category rules below; the lint cannot see images or footage.
5. Ensure disclosure is present.
Done when lint shows zero high findings and every medium has a stated decision.

## Category rules

| Category | Law / regulator | Rule of thumb |
|---|---|---|
| Food & dietary supplements | พ.ร.บ.อาหาร, อย. | No cure/prevent/treat claims, no weight-loss, detox, or disease claims. Supplement ads carry the statements "ควรกินอาหารหลากหลาย ครบ 5 หมู่ ในสัดส่วนที่เหมาะสมเป็นประจำ" and "ไม่มีผลในการป้องกันหรือรักษาโรค" (exact current wording: check อย.). |
| Cosmetics | พ.ร.บ.เครื่องสำอาง, อย. | Cosmetics act on the surface: no treating acne/melasma/hair loss as a medical result, no "ขาวใน 7 วัน", no permanent results. Before/after visuals are high risk. |
| Drugs & medical devices | พ.ร.บ.ยา, พ.ร.บ.เครื่องมือแพทย์ | Advertising generally needs prior approval. Default: skip unless the seller supplies approved ad copy. |
| Everything | พ.ร.บ.คุ้มครองผู้บริโภค (สคบ.) | No false or exaggerated claims; prices, discounts, and stock must be true. |
| Credit, insurance, investment | ธปท., คปภ., ก.ล.ต. | No approval/return guarantees; mandatory warnings per product: table in `modules/cpa-networks.md`. Licensed providers only. |
| Alcoholic drinks | พ.ร.บ.ควบคุมเครื่องดื่มแอลกอฮอล์ (ม.32) | Persuasive advertising is prohibited. Default: skip. |
| E-cigarettes / vapes, gambling | illegal in Thailand | Never promote. |

"มีเลข อย." means the product is registered or notified; it does not certify that the product works. Copy saying อย. guarantees results is itself a violation.

## Safe phrasing

| Risky | Safer |
|---|---|
| รักษาสิว / สิวหายขาด | ช่วยทำความสะอาดผิวที่มีแนวโน้มเป็นสิว (describe what the cosmetic does on the surface) |
| ขาวใน 7 วัน | ผิวดูกระจ่างใสขึ้นเมื่อใช้ต่อเนื่อง (no time promise) |
| ลดน้ำหนัก 5 กิโล (supplement) | describe ingredients, taste, how to use; no body-change promise |
| ปลอดภัย 100% / ไม่มีผลข้างเคียง | ผ่านการจดแจ้ง/ขึ้นทะเบียน (only if true) + ควรทดสอบก่อนใช้ |
| ดีที่สุด / อันดับ 1 | ที่ฉันชอบที่สุดในที่ลองมา (personal, verifiable) or cite the source of the ranking |
| แพทย์แนะนำ | remove unless the seller provides documented, permitted endorsement |
| เหลือ 3 ชิ้นสุดท้าย | only with real stock; otherwise "โปรตามร้านกำหนด" |

Personal experience framing ("ฉันใช้แล้วรู้สึกว่า…") does not make a medical claim legal; a testimonial is still an ad claim.

## Disclosure

Every promo piece states the commercial relationship in a way a viewer sees without tapping "more": `#โฆษณา`, `#affiliate`, "มีลิงก์ affiliate ได้ค่าคอมเมื่อซื้อผ่านลิงก์", or "ได้รับสินค้าจากร้าน" for free samples. On TikTok also switch on the platform's commercial content disclosure setting when the post is sponsored.

## Tuning the lint

Rules are regex patterns in `config/claims-rules.json` (`id`, `severity`, `pattern`, `reason`, `fix`). Add a rule when a new risky phrase shows up; add a `context` note when a phrase is only risky in certain categories.
