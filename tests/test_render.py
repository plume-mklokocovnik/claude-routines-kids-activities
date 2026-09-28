import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import render
from test_state import database, event


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.db = {
            "events": {},
            "system_state": {"1": {"last_run": "2026-09-28T10:00:00+02:00"}},
        }

    def test_same_input_produces_same_output_without_mutation(self):
        before = copy.deepcopy(self.db)
        self.assertEqual(render.build(self.db), render.build(self.db))
        self.assertEqual(self.db, before)

    def test_missing_or_naive_clock_is_rejected(self):
        for value in (None, "bad", "2026-09-28T10:00:00"):
            with self.subTest(value=value):
                self.db["system_state"]["1"]["last_run"] = value
                with self.assertRaisesRegex(ValueError, "last_run"):
                    render.build(self.db)

    def test_shortlist_ids_unknown_time_and_full_price(self):
        db = database()
        db["events"]["1"] = event(flags=["time_unknown"], price_text="Free programme, participants 20 EUR")
        output = render.build(db)
        self.assertEqual(output.count("`sample_20261010_1000`"), 2)
        self.assertIn("Free programme, participants 20 EUR", output)
        self.assertNotIn("10:00 |", output)
        self.assertLess(output.index("## ⭐"), output.index("## Koledar"))

    def test_local_timezone_and_non_active_filtering(self):
        db = database()
        db["events"]["1"]["start_time"] = "2026-10-10T23:30:00Z"
        db["events"]["2"] = event(event_id="expired", status="expired")
        db["events"]["3"] = event(event_id="hidden", status="hidden")
        output = render.build(db)
        self.assertIn("11. oktober 2026", output)
        self.assertIn("01:30", output)
        self.assertNotIn("`expired`", output)
        self.assertNotIn("`hidden`", output)

    def test_links_and_cells_escape_untrusted_source_text(self):
        item = event(title="[Title] | <script>x</script>", url="https://example.org/(show)")
        rendered = render.title_text(item)
        self.assertIn("%28show%29", rendered)
        self.assertIn("\\|", rendered)
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("javascript:", render.link("Title", "javascript:alert(1)"))

    def test_unknown_date_still_has_table_header(self):
        self.db["events"]["1"] = event(start_time=None)
        output = render.build(self.db)
        self.assertIn("### Datum ni znan", output)
        self.assertIn("| Ura | Dogodek / ID |", output)

    def test_same_day_rows_form_one_contiguous_table(self):
        db = database()
        db["events"]["2"] = event(event_id="second", starred=False)
        calendar = render.build(db).split("## Koledar", 1)[1].split("<details>", 1)[0]
        rows = [line for line in calendar.splitlines() if line.startswith("|")]
        self.assertEqual(len(rows), 4)
        self.assertIn("\n".join(rows), calendar)


if __name__ == "__main__":
    unittest.main()