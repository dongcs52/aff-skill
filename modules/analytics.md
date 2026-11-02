# Performance analysis

Goal: tell the creator which content and products to scale, fix, or cut, from their own export, with numbers that came from the tool.

## Steps

1. Get the data: CSV or XLSX export from the affiliate dashboard (conversion/order report, click report, LIVE stats) or the user's content log. Pasted tables: write them to a CSV in the scratchpad first.
2. Run the report. Grouping defaults to sub_id, then content, then product, whichever exists.
   ```bash
   python3 scripts/aff_tools.py report export.csv
   python3 scripts/aff_tools.py report export.csv --by product
   python3 scripts/aff_tools.py report export.csv --map commission="Est. Commission(฿)" --map sub_id="Sub_id1"
   ```
   The tool prints which column it mapped to each field. When a mapping looks wrong, rerun with `--map`. Cancelled/unpaid rows are excluded and counted.
3. Diagnose with the funnel below; each diagnosis cites the metric that supports it.
4. Deliver the output contract. Done when every SCALE/FIX/CUT group has a concrete next action.

## Funnel diagnosis

| Symptom | Likely cause | Next action |
|---|---|---|
| Low views | hook, first frame, posting time, account health | new hooks on the same product, test 2 posting times |
| Views fine, low CTR | product not visible, weak CTA, link not attached, no price shown | show product + price card earlier, add explicit CTA |
| Clicks fine, low CVR | price above expectation, low shop rating, voucher expired, variant mismatch, out of stock | switch to a better shop for the same product, align video promise with listing |
| Orders fine, low commission | low-ticket product, cancellations/returns, rate changed | move to higher baht-per-order products, check return reasons |
| One sub_id carries everything | winning angle | make 3–5 more variants of that angle (`modules/short-video.md`) |

Key ratios: **EPC** (commission ÷ clicks) compares content across platforms; **RPM** (commission per 1,000 views) compares videos; **effective rate** (commission ÷ GMV) catches capped or changed rates.

## Output contract

```
Period / source file / rows used / rows excluded (cancelled)
KPI table (from the tool, unedited)
Winners (SCALE): why + next 3 pieces of content
Fix: what to change, per group
Cut: stop promoting, reason
3 actions for next week, ranked by expected commission impact
```

Small samples (under ~100 clicks or ~5 orders per group) get the label "ข้อมูลน้อย ยังสรุปไม่ได้" instead of a verdict.
