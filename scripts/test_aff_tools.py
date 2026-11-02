"""Run: python3 -m unittest discover -s scripts   (from the skill root)"""
import csv
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import aff_tools as T  # noqa: E402


def run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = T.main(argv)
    return code, buf.getvalue()


class Earn(unittest.TestCase):
    def test_stacked_and_capped_rates(self):
        _, out = run(["earn", "--price", "1000", "--rate", "10:50", "--rate", "5", "--json"])
        d = json.loads(out)
        self.assertEqual(d["commission_per_order_gross"], 100.0)  # min(100, 50) + 50

    def test_funnel_and_returns(self):
        _, out = run(["earn", "--price", "500", "--rate", "10", "--return-rate", "10",
                      "--views", "10000", "--ctr", "1", "--cvr", "5", "--json"])
        d = json.loads(out)
        self.assertEqual(d["commission_per_order_net"], 45.0)
        self.assertEqual(d["funnel"]["clicks"], 100.0)
        self.assertEqual(d["funnel"]["orders"], 5.0)
        self.assertEqual(d["funnel"]["earnings"], 225.0)
        self.assertEqual(d["funnel"]["rpm"], 22.5)

    def test_target(self):
        _, out = run(["earn", "--price", "200", "--rate", "10", "--cvr", "4", "--ctr", "1", "--target", "10000", "--json"])
        t = json.loads(out)["target"]
        self.assertEqual(t["orders"], 500)
        self.assertEqual(t["clicks"], 12500)
        self.assertEqual(t["views"], 1250000)


    def test_cpa_payout_with_approval(self):
        _, out = run(["earn", "--payout", "300", "--approval", "50", "--clicks", "1000", "--cvr", "2", "--json"])
        d = json.loads(out)
        self.assertEqual(d["model"], "cpa")
        self.assertEqual(d["commission_per_order_net"], 150.0)
        self.assertEqual(d["funnel"]["earnings"], 3000.0)
        self.assertIsNone(d["funnel"]["gmv"])

    def test_needs_price_or_payout(self):
        with self.assertRaises(SystemExit):
            run(["earn", "--cvr", "2"])


class Ads(unittest.TestCase):
    def test_cpc_profit_and_break_even(self):
        _, out = run(["ads", "--price", "1000", "--rate", "10", "--spend", "1000", "--cpc", "2", "--cvr", "5", "--json"])
        d = json.loads(out)
        self.assertEqual(d["ad_clicks"], 500)
        self.assertEqual(d["actions"], 25)
        self.assertEqual(d["earnings"], 2500)
        self.assertEqual(d["profit"], 1500)
        self.assertEqual(d["roas"], 2.5)
        self.assertEqual(d["break_even_cpc"], 5)

    def test_cpm_with_prelander(self):
        _, out = run(["ads", "--payout", "200", "--approval", "50", "--spend", "500", "--cpm", "50",
                      "--ad-ctr", "2", "--lp-ctr", "50", "--cvr", "10", "--json"])
        d = json.loads(out)
        self.assertEqual(d["ad_clicks"], 200)       # 10,000 impressions × 2%
        self.assertEqual(d["merchant_clicks"], 100)
        self.assertEqual(d["earnings"], 1000)       # 10 actions × ฿100 net
        self.assertEqual(d["break_even_cpm"], 100)  # ฿5 per ad click × 2% × 1000


class Score(unittest.TestCase):
    cfg = T.load_json("scoring.json")

    def test_compliance_high_is_capped(self):
        r = T.score_product({"name": "x", "price": 500, "rate": 30, "demand": 5, "demo": 5, "competition": 1,
                             "rating": 5, "reviews": 1000, "return_risk": 1, "trend": 5, "compliance": "high"}, self.cfg)
        self.assertLessEqual(r["score"], 40)
        self.assertEqual(r["verdict"], "ข้าม")

    def test_strong_product_goes(self):
        r = T.score_product({"name": "mop", "price": 399, "rate": "15+5", "demand": 5, "demo": 5, "competition": 2,
                             "rating": 4.9, "reviews": 800, "return_risk": 1, "trend": 4}, self.cfg)
        self.assertEqual(r["verdict"], "ทำเลย")
        self.assertEqual(r["assumed"], [])

    def test_missing_fields_are_listed(self):
        r = T.score_product({"name": "bare", "price": 299}, self.cfg)
        self.assertIn("commission", r["assumed"])
        self.assertIn("trust", r["assumed"])
        self.assertEqual(r["verdict"], "ข้อมูลไม่พอ")


class Lint(unittest.TestCase):
    def ids(self, text):
        return {f["id"]: f["severity"] for f in T.lint_text(text)}

    def test_cure_claim_high(self):
        self.assertEqual(self.ids("เซรั่มตัวนี้รักษาสิวหายขาด #โฆษณา")["cure-claim"], "high")

    def test_food_word_not_fda(self):
        ids = self.ids("อร่อยรับรองติดใจ #โฆษณา")
        self.assertNotIn("fda-endorsement", ids)

    def test_fda_endorsement(self):
        self.assertEqual(self.ids("อย.รับรองว่าได้ผล #โฆษณา")["fda-endorsement"], "high")

    def test_pillow_not_doctor(self):
        self.assertNotIn("doctor-endorsement", self.ids("หมอนแนะนำสำหรับคนปวดคอ #โฆษณา"))

    def test_required_disclaimer_not_flagged(self):
        text = ("คอลลาเจนชงง่าย ควรกินอาหารหลากหลาย ครบ 5 หมู่ ในสัดส่วนที่เหมาะสมเป็นประจำ "
                "ไม่มีผลในการป้องกันหรือรักษาโรค #โฆษณา")
        ids = self.ids(text)
        self.assertNotIn("cure-claim", ids)
        self.assertNotIn("missing-supplement-disclaimer", ids)

    def test_missing_disclosure(self):
        self.assertIn("missing-disclosure", self.ids("ไม้ถูพื้นตัวนี้ดีมาก"))

    def test_overlap_deduped(self):
        ids = [f["id"] for f in T.lint_text("ปลอดภัย 100% #โฆษณา")]
        self.assertIn("absolute-safety", ids)
        self.assertNotIn("percent-100", ids)

    def test_credit_offer(self):
        ids = self.ids("สมัครบัตรเครดิตอนุมัติไว ไม่เช็คบูโร #โฆษณา")
        self.assertEqual(ids["finance-easy-approval"], "high")
        self.assertIn("missing-credit-warning", ids)

    def test_compliant_credit_offer(self):
        ids = self.ids("สมัครบัตรเครดิตออนไลน์ ผลอนุมัติเป็นไปตามเงื่อนไขธนาคาร "
                       "ใช้จ่ายเท่าที่จำเป็นและชำระคืนได้เต็มจำนวนตามกำหนด #โฆษณา")
        self.assertEqual(ids, {})

    def test_cancer_insurance_not_disease_claim(self):
        ids = self.ids("ประกันมะเร็งเบี้ยเริ่มต้นหลักร้อย #โฆษณา")
        self.assertNotIn("disease-mention", ids)
        self.assertIn("missing-insurance-warning", ids)

    def test_warranty_is_not_insurance(self):
        self.assertNotIn("missing-insurance-warning", self.ids("รับประกันสินค้า 1 ปี #โฆษณา"))

    def test_hair_claims(self):
        ids = self.ids("แชมพูแฮร์โทนิค ลดผมร่วง เร่งผมยาว #โฆษณา")
        self.assertEqual(ids["hair-growth"], "high")
        self.assertEqual(ids["hair-fall"], "medium")

    def test_hair_conditioning_is_fine(self):
        self.assertEqual(self.ids("สระแล้วผมนุ่ม หวีง่าย ไม่พันกัน #โฆษณา"), {})

    def test_exit_code(self):
        code, _ = run(["lint", "--text", "ขาวใน 7 วัน #โฆษณา"])
        self.assertEqual(code, 2)
        code, _ = run(["lint", "--text", "ไม้ถูพื้นบิดน้ำง่าย #โฆษณา"])
        self.assertEqual(code, 0)


class Report(unittest.TestCase):
    def write_csv(self, rows):
        f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8-sig", newline="")
        csv.writer(f).writerows(rows)
        f.close()
        return f.name

    def test_thai_headers_title_row_and_cancelled(self):
        path = self.write_csv([
            ["รายงาน Affiliate เดือน ต.ค."],
            ["หมายเลขคำสั่งซื้อ", "สถานะคำสั่งซื้อ", "ชื่อสินค้า", "Sub_id1", "ยอดขาย(฿)", "อัตราค่าคอมมิชชั่น", "ค่าคอมมิชชั่นทั้งหมด(฿)"],
            ["A1", "สำเร็จ", "ไม้ถูพื้น", "tt_vid_mop", "399", "10%", "39.9"],
            ["A1", "สำเร็จ", "ผ้าไมโคร", "tt_vid_mop", "100", "10%", "10"],
            ["A2", "สำเร็จ", "ไม้ถูพื้น", "tt_vid_mop", "399", "10%", "39.9"],
            ["A3", "ยกเลิก", "ไม้ถูพื้น", "fb_post_mop", "399", "10%", "0"],
            ["A4", "รอดำเนินการ", "หม้อทอด", "fb_post_af", "1,290", "8%", "103.2"],
        ])
        rep = T.build_report(T.read_table(path), None, {}, min_orders=1)
        self.assertEqual(rep["header_row"], 2)
        self.assertEqual(rep["mapping"]["commission"], "ค่าคอมมิชชั่นทั้งหมด(฿)")
        self.assertEqual(rep["group_by"], "sub_id")
        self.assertEqual(rep["rows_excluded"], 1)
        groups = dict(rep["groups"])
        self.assertEqual(groups["tt_vid_mop"]["orders"], 2)  # unique order ids
        self.assertAlmostEqual(groups["tt_vid_mop"]["commission"], 89.8)
        self.assertAlmostEqual(rep["total"]["gmv"], 2188.0)

    def test_clicks_verdicts(self):
        path = self.write_csv([
            ["sub_id", "clicks", "orders", "commission"],
            ["winner", "1000", "60", "3000"],
            ["average", "1000", "30", "1000"],
            ["loser", "1000", "5", "100"],
            ["tiny", "20", "1", "50"],
        ])
        rep = T.build_report(T.read_table(path), None, {})
        v = {k: g["verdict"] for k, g in rep["groups"]}
        self.assertEqual(v["winner"], "SCALE")
        self.assertEqual(v["loser"], "FIX")
        self.assertEqual(v["tiny"], "ข้อมูลน้อย")


if __name__ == "__main__":
    unittest.main()
