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

    def test_ids_unknown_time_and_full_price(self):
        db = database()
        db["events"]["1"] = event(flags=["time_unknown"], price_text="Free programme, participants 20 EUR")
        output = render.build(db)
        # Exactly once: the calendar is the only place an active event is listed.
        self.assertEqual(output.count("`sample_20261010_1000`"), 1)
        self.assertIn("Free programme, participants 20 EUR", output)
        self.assertNotIn("10:00 |", output)
        self.assertNotIn("⭐", output)

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

    def test_each_event_appears_in_exactly_one_category_section(self):
        db = database()
        db["events"]["1"]["decision"] = "interested"
        db["events"]["2"] = event(event_id="perhaps", decision="maybe",
                                  start_time="2026-10-11T09:00:00+02:00")
        db["events"]["3"] = event(event_id="nope", decision="rejected",
                                  start_time="2026-10-12T09:00:00+02:00")
        db["events"]["4"] = event(event_id="open", start_time="2026-10-13T09:00:00+02:00")
        output = render.build(db)
        listing = output.split("<details>", 1)[0]
        for identifier in ("sample_20261010_1000", "perhaps", "nope", "open"):
            with self.subTest(identifier=identifier):
                self.assertEqual(listing.count(f"`{identifier}`"), 1)

        # Split on the section anchors in document order. Splitting on any
        # `<a id=` would cut the undecided section at its first month anchor.
        order = ["interested", "maybe", "rejected", "undecided"]
        sections, rest = {}, listing
        for index, name in enumerate(order):
            rest = rest.split(f'<a id="{render.ANCHORS[name]}"></a>', 1)[1]
            following = order[index + 1] if index + 1 < len(order) else None
            sections[name] = (rest.split(f'<a id="{render.ANCHORS[following]}"></a>', 1)[0]
                              if following else rest)
        self.assertIn("`sample_20261010_1000`", sections["interested"])
        self.assertIn("`perhaps`", sections["maybe"])
        self.assertIn("`nope`", sections["rejected"])
        self.assertIn("`open`", sections["undecided"])
        # The counts table links to every section and reports the real sizes.
        self.assertIn("| [👍 Zanima nas](#zanima-nas) | 1 | 10.10.2026 |", output)
        self.assertIn("| [🃏 Neodločeno](#neodloceno) | 1 | 13.10.2026 |", output)

    def test_empty_categories_say_so_without_inventing_rows(self):
        output = render.build(database())
        self.assertEqual(output.count("_Ni dogodkov v tej kategoriji._"), 3)
        self.assertIn("| [👎 Zavrnjeno](#zavrnjeno) | 0 | - |", output)
        self.assertNotIn("Vsi dogodki so razvrščeni", output)

    def test_same_day_rows_form_one_contiguous_table(self):
        db = database()
        db["events"]["2"] = event(event_id="second")
        calendar = render.build(db).split("Neodločeno", 1)[1].split("<details>", 1)[0]
        rows = [line for line in calendar.splitlines() if line.startswith("|")]
        self.assertEqual(len(rows), 4)
        self.assertIn("\n".join(rows), calendar)


if __name__ == "__main__":
    unittest.main()