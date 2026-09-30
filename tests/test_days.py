"""The app's past-event rule, run through Node against the real days.js.

Skipped when Node is not installed. The rule lives in the browser code, so this
is the only way to exercise it without a browser.
"""

import json
import unittest

import node_runner
from node_runner import NODE


def evaluate(expression, timezone=None):
    """Evaluate a JavaScript expression against days.js and return its JSON."""
    return node_runner.run(f"{node_runner.require('days.js')} return {expression};", timezone)


# Each pair is a UTC instant and the calendar date it is in Ljubljana.
BOUNDARIES = [
    ("2026-09-30T21:59:59Z", "2026-09-30"),  # 23:59:59 in summer time
    ("2026-09-30T22:00:00Z", "2026-10-01"),  # midnight
    ("2026-10-24T21:59:59Z", "2026-10-24"),
    ("2026-10-24T22:00:00Z", "2026-10-25"),  # the day the clocks go back
    ("2026-10-25T22:59:59Z", "2026-10-25"),  # 23:59:59 in winter time, an hour later
    ("2026-10-25T23:00:00Z", "2026-10-26"),
    ("2026-12-31T22:59:59Z", "2026-12-31"),
    ("2026-12-31T23:00:00Z", "2027-01-01"),  # new year
    ("2026-03-28T22:59:59Z", "2026-03-28"),
    ("2026-03-28T23:00:00Z", "2026-03-29"),  # the day the clocks go forward
]


def card(day, free=False):
    return {"event_id": f"e_{day}", "day_iso": day, "is_free": free}


@unittest.skipUnless(NODE, "node is not installed")
class DaysTests(unittest.TestCase):
    def test_today_follows_the_ljubljana_calendar_across_midnight_and_dst(self):
        instants = json.dumps([instant for instant, _ in BOUNDARIES])
        got = evaluate(f"{instants}.map((value) => Days.today(new Date(value)))")
        self.assertEqual(got, [expected for _, expected in BOUNDARIES])

    def test_today_does_not_depend_on_the_device_timezone(self):
        instants = json.dumps([instant for instant, _ in BOUNDARIES])
        expected = [date for _, date in BOUNDARIES]
        for timezone in ("UTC", "Pacific/Auckland", "America/Los_Angeles", "Asia/Kolkata"):
            with self.subTest(timezone=timezone):
                got = evaluate(f"{instants}.map((value) => Days.today(new Date(value)))", timezone)
                self.assertEqual(got, expected)

    def test_only_earlier_dates_are_past_and_the_same_day_stays(self):
        cases = {"2026-09-29": True, "2026-09-30": False, "2026-10-01": False, "2027-01-01": False}
        got = evaluate(f"Object.fromEntries({json.dumps(list(cases))}"
                       ".map((day) => [day, Days.isPast({ day_iso: day }, '2026-09-30')]))")
        self.assertEqual(got, cases)

    def test_a_card_without_a_date_is_never_past(self):
        for shaped in ("{ day_iso: '' }", "{}", "{ day_iso: null }"):
            with self.subTest(card=shaped):
                self.assertFalse(evaluate(f"Days.isPast({shaped}, '2099-01-01')"))

    def test_upcoming_drops_past_events_everywhere_and_recounts(self):
        data = {
            "deck": [card("2026-09-29", True), card("2026-09-30"), card("2026-10-02", True)],
            "groups": {"interested": [card("2026-09-29"), card("2026-09-30", True)],
                       "maybe": [], "rejected": [card("2026-09-28", True)]},
            "counts": {"interested": 2, "maybe": 0, "rejected": 1, "undecided": 3,
                       "decided": 3, "total": 6},
            "undo": {"available": True}, "labels": {"interested": "Zanima nas"},
        }
        got = evaluate(f"Days.upcoming({json.dumps(data)}, '2026-09-30')")
        self.assertEqual([c["day_iso"] for c in got["deck"]], ["2026-09-30", "2026-10-02"])
        self.assertEqual([c["day_iso"] for c in got["groups"]["interested"]], ["2026-09-30"])
        self.assertEqual(got["groups"]["rejected"], [])
        self.assertEqual(got["counts"], {"interested": 1, "maybe": 0, "rejected": 0,
                                         "undecided": 2, "decided": 1, "total": 3})
        self.assertEqual(got["today"], "2026-09-30")
        # Three of the six were before today. Of the three left, two are free.
        self.assertEqual((got["past"], got["free"]), (3, 2))
        # Everything else is passed through untouched.
        self.assertEqual(got["undo"], data["undo"])
        self.assertEqual(got["labels"], data["labels"])

    def test_upcoming_leaves_its_input_alone_so_it_can_be_filtered_again_tomorrow(self):
        data = {"deck": [card("2026-09-29")], "groups": {"interested": [], "maybe": [], "rejected": []},
                "counts": {}}
        got = evaluate(f"(() => {{ const input = {json.dumps(data)};"
                       "const before = JSON.stringify(input);"
                       "Days.upcoming(input, '2026-09-30');"
                       "const next = Days.upcoming(input, '2026-09-28');"
                       "return { unchanged: JSON.stringify(input) === before, later: next.deck.length }; })()")
        self.assertEqual(got, {"unchanged": True, "later": 1})


if __name__ == "__main__":
    unittest.main()
