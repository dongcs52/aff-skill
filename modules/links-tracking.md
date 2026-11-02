# Links and tracking

Goal: every click traceable to the piece of content that produced it, so `modules/analytics.md` can say which content earns.

## sub_id convention

One scheme across all platforms, so reports group cleanly:

```
<channel>_<format>_<yymmdd>_<slug>
tt_vid_261102_mop      TikTok video, 2 Nov 2026, mop product
fb_post_261105_airfryer
line_bc_261111_1111sale
```

- `channel`: tt, sp (Shopee Video/Live), lz, fb, ig, yt, line, blog, pantip, x
- `format`: vid, live, post, story, bc (broadcast), art (article), bio
- `slug`: short product or campaign name, lowercase ASCII, no spaces

When a platform offers several Sub_id fields (Shopee custom links do; count and length limits: `ตรวจสอบใน dashboard`), split the same parts across them: sub1 = channel, sub2 = format, sub3 = date+slug, sub4 = campaign (e.g. `1111`). Keep the order fixed forever; reports depend on it.

## Steps

1. List each placement (video, post, broadcast, bio) the user will publish.
2. Assign a sub_id per placement with the convention above.
3. Output a link table the user fills from the affiliate portal:

```
| placement | platform | product | sub_id | affiliate link (paste) |
|---|---|---|---|---|
```

4. Remind the user to keep a **content log** (sheet) with: date, content_id/sub_id, platform, format, product, views, clicks, orders, commission. This is the input `report` reads best.

Done when every placement has a unique sub_id and the user knows where each link goes.

## Placement rules

- TikTok Shop: link through Showcase / product anchor; no external affiliate links needed.
- Instagram / Facebook / Threads / YouTube: one link hub in bio (with a sub_id per hub link) or the link in post/first comment.
- Use the platform's own short link. Third-party shorteners can strip tracking parameters and look spammy; some platforms block them.
- Attribution is last-click: a buyer who clicks another creator's link later credits that creator. Content that converts in the same session wins.
- Test every link once from a logged-out browser before posting: correct product, correct variant, link resolves in the app.
