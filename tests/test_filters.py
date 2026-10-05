"""The review list filters, run through Node against the real filters.js.

Skipped when Node is not installed. Matching, diacritic folding and the date
presets live in the browser code, so this is the only way to exercise them
without a browser.
"""

import json
import unittest

import node_runner
from node_runner import NODE


def evaluate(expression, timezone=None):
    """Evaluate a JavaScript expression against filters.js and return its JSON."""
    return node_runner.run(f"{node_runner.require('filters.js')} return {expression};", timezone)


CARDS = [
    {"event_id": "a", "title": "Čebelica Maja", "venue": "Kino Šiška", "city": "Ljubljana",
     "category": "gledalisce", "notes": ["prijava"], "day_iso": "2026-10-10", "is_free": True},
    {"event_id": "b", "title": "Delavnica keramike", "venue": "Muzej", "city": "Škofja Loka",
     "category": "delavnica", "notes": [], "day_iso": "2026-10-20", "is_free": False},
    {"event_id": "c", "title": "Sprehod", "venue": "Park", "city": "Kranj",
     "category": "narava", "notes": ["daljša pot"], "day_iso": "", "is_free": True},
    {"event_id": "d", "title": "Lutke", "venue": "Mestno gledališče", "city": "Ljubljana",
     "category": "gledalisce", "notes": [], "day_iso": "2026-10-25", "is_free": False},
]


def pick(filters):
    cards = json.dumps(CARDS)
    return evaluate(f"Filters.apply({cards}, Object.assign(Filters.empty(), {json.dumps(filters)}))"
                    ".map((card) => card.event_id)")


@unittest.skipUnless(NODE, "node is not installed")
class FilterTests(unittest.TestCase):
    def test_nothing_is_active_by_default_and_everything_passes(self):
        self.assertFalse(evaluate("Filters.isActive(Filters.empty())"))
        self.assertEqual(pick({}), ["a", "b", "c", "d"])
        self.assertFalse(evaluate("Filters.isActive(Object.assign(Filters.empty(), { text: '   ' }))"))

    def test_search_ignores_case_and_diacritics(self):
        self.assertEqual(pick({"text": "cebelica"}), ["a"])
        self.assertEqual(pick({"text": "ČEBELICA"}), ["a"])
        self.assertEqual(pick({"text": "siska"}), ["a"])
        self.assertEqual(pick({"text": "skofja"}), ["b"])
        self.assertEqual(pick({"text": "gledalisce"}), ["a", "d"])

    def test_search_covers_title_venue_city_notes_and_category(self):
        self.assertEqual(pick({"text": "keramike"}), ["b"])
        self.assertEqual(pick({"text": "park"}), ["c"])
        self.assertEqual(pick({"text": "kranj"}), ["c"])
        self.assertEqual(pick({"text": "daljsa"}), ["c"])
        self.assertEqual(pick({"text": "delavnica"}), ["b"])

    def test_every_word_has_to_match_and_unknown_text_matches_nothing(self):
        self.assertEqual(pick({"text": "lutke ljubljana"}), ["d"])
        self.assertEqual(pick({"text": "lutke kranj"}), [])
        self.assertEqual(pick({"text": "zzz"}), [])

    def test_date_range_is_inclusive_and_skips_cards_without_a_date(self):
        self.assertEqual(pick({"from": "2026-10-10", "to": "2026-10-20"}), ["a", "b"])
        self.assertEqual(pick({"from": "2026-10-11"}), ["b", "d"])
        self.assertEqual(pick({"to": "2026-10-20"}), ["a", "b"])
        self.assertNotIn("c", pick({"from": "2020-01-01"}))
        self.assertNotIn("c", pick({"to": "2099-01-01"}))

    def test_an_inverted_range_is_swapped_and_reported(self):
        self.assertEqual(pick({"from": "2026-10-20", "to": "2026-10-10"}), ["a", "b"])
        got = evaluate("Filters.ordered({ from: '2026-10-20', to: '2026-10-10' })")
        self.assertTrue(got["swapped"])
        self.assertEqual((got["filters"]["from"], got["filters"]["to"]), ("2026-10-10", "2026-10-20"))
        self.assertFalse(evaluate("Filters.ordered({ from: '2026-10-10', to: '2026-10-10' }).swapped"))

    def test_an_unreadable_date_is_ignored_rather_than_hiding_everything(self):
        self.assertEqual(pick({"from": "2026-13-45"}), ["a", "b", "c", "d"])
        self.assertFalse(evaluate("Filters.isActive(Object.assign(Filters.empty(), { from: 'abc' }))"))

    def test_categories_and_free_combine_with_the_other_filters(self):
        self.assertEqual(pick({"categories": ["gledalisce"]}), ["a", "d"])
        self.assertEqual(pick({"categories": ["gledalisce", "narava"]}), ["a", "c", "d"])
        self.assertEqual(pick({"free": True}), ["a", "c"])
        self.assertEqual(pick({"free": True, "categories": ["gledalisce"], "from": "2026-10-01"}), ["a"])

    def test_categories_lists_only_those_in_the_data_in_order(self):
        cards = json.dumps(CARDS + [{"category": "?"}, {"category": ""}])
        self.assertEqual(evaluate(f"Filters.categories({cards})"), ["delavnica", "gledalisce", "narava"])

    def test_toggle_and_remove_return_new_objects(self):
        got = evaluate("""(() => {
          const base = Object.assign(Filters.empty(), { text: 'a', from: '2026-10-01', free: true });
          const on = Filters.toggleCategory(base, 'narava');
          const off = Filters.toggleCategory(on, 'narava');
          return { base: base.categories, on: on.categories, off: off.categories,
                   text: Filters.remove(base, 'text').text, from: Filters.remove(base, 'from').from,
                   free: Filters.remove(base, 'free').free,
                   category: Filters.remove(on, 'category:narava').categories };
        })()""")
        self.assertEqual(got, {"base": [], "on": ["narava"], "off": [], "text": "", "from": "",
                               "free": False, "category": []})

    def test_describe_gives_one_removable_entry_per_active_filter(self):
        got = evaluate("""Filters.describe(Object.assign(Filters.empty(), {
          text: 'lutke', from: '2026-10-05', to: '2026-10-20', categories: ['narava'], free: true }), '2026-10-05')""")
        self.assertEqual([item["id"] for item in got], ["text", "from", "to", "category:narava", "free"])
        self.assertEqual([item["label"] for item in got],
                         ["Iskanje: lutke", "Od 05.10.", "Do 20.10.", "narava", "Brezplačno"])
        other = evaluate("Filters.describe(Object.assign(Filters.empty(), { to: '2027-01-05' }), '2026-10-05')")
        self.assertEqual(other[0]["label"], "Do 05.01.2027")

    def test_presets_follow_the_given_ljubljana_date(self):
        # Monday 5 October 2026.
        got = evaluate("Filters.presets('2026-10-05')")
        self.assertEqual(got["today"], {"from": "2026-10-05", "to": "2026-10-05"})
        self.assertEqual(got["weekend"], {"from": "2026-10-10", "to": "2026-10-11"})
        self.assertEqual(got["week"], {"from": "2026-10-05", "to": "2026-10-11"})

    def test_the_weekend_preset_on_a_saturday_and_a_sunday(self):
        saturday = evaluate("Filters.presets('2026-10-10').weekend")
        self.assertEqual(saturday, {"from": "2026-10-10", "to": "2026-10-11"})
        sunday = evaluate("Filters.presets('2026-10-11').weekend")
        self.assertEqual(sunday, {"from": "2026-10-11", "to": "2026-10-11"})

    def test_presets_cross_month_and_year_ends(self):
        got = evaluate("Filters.presets('2026-12-29')")
        self.assertEqual(got["week"], {"from": "2026-12-29", "to": "2027-01-04"})
        self.assertEqual(got["weekend"], {"from": "2027-01-02", "to": "2027-01-03"})

    def test_dates_do_not_depend_on_the_device_timezone(self):
        expected = {"today": {"from": "2026-10-24", "to": "2026-10-24"},
                    "weekend": {"from": "2026-10-24", "to": "2026-10-25"},
                    "week": {"from": "2026-10-24", "to": "2026-10-30"}}
        # The weekend of 24 and 25 October is when the clocks go back, the worst case for local math.
        for timezone in ("UTC", "Pacific/Auckland", "America/Los_Angeles", "Europe/Ljubljana"):
            with self.subTest(timezone=timezone):
                self.assertEqual(evaluate("Filters.presets('2026-10-24')", timezone), expected)
                self.assertEqual(evaluate("Filters.addDays('2026-10-24', 2)", timezone), "2026-10-26")

    def test_fold_strips_marks_and_case(self):
        self.assertEqual(evaluate("Filters.fold('Čebelica Šiška Žoga Đ')"), "cebelica siska zoga d")
        self.assertEqual(evaluate("Filters.fold(null)"), "")


if __name__ == "__main__":
    unittest.main()
