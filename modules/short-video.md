# Short video scripts

TikTok, Shopee Video, Reels, and YouTube Shorts. Goal: scripts a creator can shoot today, each built on a different angle so the batch doubles as an A/B test.

## Steps

1. Pin down product, platform, length (15 / 30 / 60s; default 30s), on-camera or faceless, and what footage the creator can actually shoot (own product? sample coming?). Read `reference/platforms.md` for the platform.
2. Find the **one buyer problem or desire** the product resolves and the **proof moment**: the 2–3 seconds where the result is visible.
3. Write **3 variants with different angles** (pick from the format bank). Same product, different hook and structure.
4. Run lint on all spoken lines, on-screen text, and captions together; fix every `high`.
   ```bash
   python3 scripts/aff_tools.py lint script.txt
   ```
5. Deliver using the output contract. Done when each variant is shootable without asking a follow-up question.

## Structure

`Hook (0–3s) → Problem / desire → Demo / proof → Offer → CTA`

- **Hook**: spoken line and on-screen text land together in the first second. The product or the problem is on screen immediately.
- **Demo / proof**: show, don't claim. Real use, real result, real texture, real size next to a hand.
- **Offer**: price, voucher, bundle, or free shipping, only if true at posting time. Add "ราคา/โปรอาจเปลี่ยนตามร้าน" when it may change.
- **CTA**: platform-native. TikTok: "กดตะกร้าเหลือง" / "จิ้มตะกร้าด้านล่าง". Shopee Video: "กดสินค้าที่แท็กไว้". Reels/Shorts: "ลิงก์อยู่ในไบโอ/คอมเมนต์แรก".

## Format bank

| Format | Fits | Note |
|---|---|---|
| Problem → solution demo | cleaning, kitchen, gadgets, organisers | strongest default |
| Talking-head honest review | anything, higher ticket | include one real downside; it raises trust |
| Comparison A vs B | crowded categories | fair test on camera |
| List "3 ของที่…" | discovery, mixed basket | one product per beat, all linked |
| POV / skit | lifestyle, gifts | product solves the punchline |
| Unboxing / ASMR | aesthetic, beauty tools, food | sound design carries it |
| Price shock | dupes, bundles, mega-sale deals | price must be verifiable |
| Slideshow / photo mode | faceless accounts | 5–8 slides, text-led, music |
| Hands-only + voiceover | faceless, AI voice | own footage still required |
| Green-screen on reviews/comments | social proof | use real reviews only |

## Hook bank (Thai)

Adapt, never copy verbatim twice on one account.

- Pain: "ใครเจอปัญหา___แบบนี้ทุกวัน ดูอันนี้"
- Curiosity: "ของชิ้นนี้ทำให้___ของฉันเปลี่ยนไปเลย"
- Contrarian: "เลิกซื้อ___แบบเดิมได้แล้ว"
- Price: "ราคาไม่ถึง___บาท แต่ทำได้แบบนี้"
- POV: "POV: เพิ่งรู้ว่ามีของแบบนี้ขายด้วย"
- Proof first: open on the result, then "ทำยังไง? ดูต่อ"
- Comparison: "ของแพง vs ของถูก ต่างกันจริงไหม"
- Social proof: "ขายไปหลักหมื่นชิ้น ลองเองแล้วเป็นแบบนี้" (only with real sold count)
- Question: "รู้ไหมว่า___ ต้องทำแบบนี้"
- List: "3 ของในบ้านที่ซื้อแล้วไม่เสียใจ"

## Output contract (per variant)

```
### Variant A — <angle> · <length>s · <on-camera|faceless>
Hook: "<spoken line>"  |  On-screen: "<text>"

| เวลา | ภาพ (shot) | พูด (VO) | Text on screen |
|---|---|---|---|
| 0–3s | ... | ... | ... |
| ... | ... | ... | ... |

Caption: <1–2 lines, hook restated + benefit>
Hashtags: <3–5: niche + product type + one broad>   e.g. #ของใช้ในบ้าน #ไม้ถูพื้น #tiktokshopครีเอเตอร์
Disclosure: #โฆษณา / มีลิงก์ affiliate
CTA: <platform-native>
Shoot notes: <props, lighting, B-roll, sound>
```

Then: lint result summary, and which variant to post first and why.

## Craft rules

- One product, one promise per video.
- Text on screen readable on a phone: ≤ 8 words per card, high contrast, away from the bottom UI zone.
- Cut every 1–2 seconds in the first 5 seconds.
- Show the price card and the product link moment on screen; viewers buy what they can find.
- Batch shooting: one setup, three variants, different hooks.
