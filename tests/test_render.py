"""The formatting helpers shared by the sweep report and the swipe app."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import render
from test_state import event


class HelperTests(unittest.TestCase):
    def test_links_and_cells_escape_untrusted_source_text(self):
        item = event(title="[Title] | <script>x</script>", url="https://example.org/(show)")
        rendered = render.title_text(item)
        self.assertIn("%28show%29", rendered)
        self.assertIn("\\|", rendered)
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("javascript:", render.link("Title", "javascript:alert(1)"))
        self.assertEqual(render.link("Title", "not a url"), "Title")

    def test_code_cannot_break_out_of_a_table_cell(self):
        self.assertEqual(render.code("a|b"), "`a&#124;b`")
        self.assertEqual(render.code("has`tick"), "<code>has`tick</code>")
        self.assertEqual(render.code(None), "`?`")

    def test_unknown_time_is_a_question_mark_never_a_fictional_midnight(self):
        start = render.parse_dt("2026-10-10T00:00:00+02:00")
        self.assertEqual(render.hour_text(event(flags=["time_unknown"]), start), "?")
        self.assertEqual(render.hour_text(event(), None), "?")
        self.assertEqual(render.hour_text(event(), render.parse_dt("2026-10-10T10:05:00+02:00")), "10:05")

    def test_timestamps_are_read_in_local_time_and_bad_ones_are_dropped(self):
        local = render.parse_dt("2026-10-10T23:30:00Z")
        self.assertEqual((local.day, local.hour, local.minute), (11, 1, 30))
        self.assertEqual(render.si_date(local), "11. oktober 2026")
        for value in (None, "", "bad", "2026-10-10T10:00:00"):
            with self.subTest(value=value):
                self.assertIsNone(render.parse_dt(value))

    def test_full_price_text_is_kept_and_a_free_marker_needs_is_free(self):
        mixed = event(price_text="Free programme, participants 20 EUR")
        self.assertEqual(render.price_text(mixed), "Free programme, participants 20 EUR")
        self.assertEqual(render.price_text(event(is_free=True, price_text="Brezplačno")), "🆓")
        self.assertEqual(render.price_text(event(is_free=True, price_text="Brezplačno, prijava")),
                         "🆓 Brezplačno, prijava")
        self.assertEqual(render.price_text(event(price_text="")), "`?`")

    def test_age_is_shown_only_when_published(self):
        self.assertEqual(render.age_text(event(age_min=4)), "`4+`")
        self.assertEqual(render.age_text(event(age_min=None)), "`?`")

    def test_notes_come_from_price_wording_and_flags(self):
        item = event(price_text="Razprodano, prijava obvezna",
                     flags=["age_stretch", "outside_ljubljana", "custom_flag"])
        self.assertEqual(render.notes_text(item), "razprodano, prijava, starost?, custom_flag")
        self.assertEqual(render.notes_text(event()), "")

    def test_place_names_the_town_only_when_it_is_not_ljubljana(self):
        self.assertIn("[Museum]", render.place_text(event(venue="Museum", city="Ljubljana")))
        self.assertIn("[Museum, Kranj]", render.place_text(event(venue="Museum", city="Kranj")))
        self.assertEqual(render.maps_link("Muzej Šiška", "Kranj"),
                         "https://maps.google.com/?q=Muzej%20%C5%A0i%C5%A1ka%20Kranj")


if __name__ == "__main__":
    unittest.main()
