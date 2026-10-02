"""Offline tests for the swipe app presenter and the page. Contacts no source."""

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "app"))
import build_static  # noqa: E402
from test_state import database, event  # noqa: E402


class PresentationTests(unittest.TestCase):
    def test_card_shows_stored_text_and_never_a_fictional_midnight(self):
        card = build_static.card(event(start_time="2026-10-10T00:00:00+02:00",
                                       flags=["time_unknown", "travel"], age_min=None,
                                       is_free=True, price_text="Brezplačno, prijava"))
        self.assertEqual(card["time"], "?")
        self.assertEqual(card["day"], "Sobota")
        self.assertEqual(card["date_short"], "10.10.")
        self.assertEqual(card["day_iso"], "2026-10-10")
        self.assertEqual(card["date_long"], "10. oktober 2026")
        self.assertEqual(card["month_long"], "Oktober 2026")
        self.assertEqual(card["age"], "?")
        self.assertTrue(card["is_free"])
        self.assertEqual(card["price"], "Brezplačno, prijava")
        self.assertEqual(card["notes"], ["prijava", "ura ni znana", "daljša pot"])
        self.assertIsNone(card["decision"])

    def test_day_iso_is_the_ljubljana_date_not_the_utc_one(self):
        # 23:30 UTC on the 10th is already 01:30 on the 11th in Ljubljana.
        self.assertEqual(build_static.card(event(start_time="2026-10-10T23:30:00Z"))["day_iso"], "2026-10-11")
        self.assertEqual(build_static.card(event(start_time="2026-10-25T00:30:00+02:00"))["day_iso"], "2026-10-25")

    def test_card_drops_an_unusable_source_link(self):
        self.assertEqual(build_static.card(event(url="javascript:alert(1)"))["url"], "")
        self.assertEqual(build_static.card(event())["url"], "https://example.org/event")

    def test_payload_uses_the_stored_sweep_clock(self):
        data = build_static.payload(database())
        self.assertEqual(data["clock"], {"date": "28.09.2026", "time": "10:00",
                                         "horizon": "28.12.2026"})
        self.assertEqual(data["counts"]["undecided"], 1)
        self.assertEqual(data["undo"], {"available": False})

    def test_labels_cover_the_three_categories_and_the_undecided_list(self):
        self.assertEqual(build_static.payload(database())["labels"],
                         {"interested": "Zanima nas", "maybe": "Mogoče",
                          "rejected": "Zavrnjeno", "undecided": "Neodločeno"})

    def test_card_carries_everything_the_details_dialog_shows(self):
        card = build_static.card(event(url="https://www.example.org/show?id=1",
                                       decision="maybe", decided_at="2026-09-30T08:00:00Z",
                                       first_seen="2026-09-24T07:22:48Z"))
        # Stored instants are UTC. The dialog shows them in Ljubljana time.
        self.assertEqual(card["first_seen"], "24.09.2026 09:22")
        self.assertEqual(card["decided_at"], "30.09.2026 10:00")
        self.assertEqual(card["source"], "example.org")
        self.assertEqual(card["decision"], "maybe")
        self.assertEqual(card["status"], "active")
        self.assertEqual(card["event_id"], "sample_20261010_1000")

    def test_missing_provenance_is_empty_rather_than_invented(self):
        bare = event()
        del bare["first_seen"]
        card = build_static.card(bare)
        self.assertEqual((card["first_seen"], card["decided_at"]), ("", ""))
        self.assertEqual(build_static.source_host("javascript:alert(1)"), "")
        self.assertEqual(build_static.source_host(None), "")
        self.assertEqual(build_static.source_host("https://sub.example.org:8443/x"), "sub.example.org")


class ClientContractTests(unittest.TestCase):
    """The browser code has no test runner here, so pin the parts a typo breaks."""

    def setUp(self):
        static = ROOT / "app" / "static"
        self.script = (static / "app.js").read_text(encoding="utf-8")
        self.scripts = {name: (static / name).read_text(encoding="utf-8")
                        for name in ("app.js", "days.js", "snapshot.js", "askai.js")}
        self.markup = (static / "index.html").read_text(encoding="utf-8")

    def test_every_element_the_script_looks_up_exists(self):
        wanted = set(re.findall(r"\bel\('([\w-]+)'\)", self.script))
        present = set(re.findall(r'\bid="([\w-]+)"', self.markup))
        self.assertTrue(wanted)
        self.assertEqual(sorted(wanted - present), [])

    def test_every_template_field_the_script_fills_exists(self):
        used = set(re.findall(r"""fill\(node, '([\w]+)'""", self.script))
        used |= set(re.findall(r"""data-f="([\w]+)"\]""", self.script))
        present = set(re.findall(r'data-f="([\w]+)"', self.markup))
        self.assertTrue(used)
        self.assertEqual(sorted(used - present), [])

    def test_the_dialog_is_labelled_modal_and_closable(self):
        self.assertIn('role="dialog"', self.markup)
        self.assertIn('aria-modal="true"', self.markup)
        self.assertIn('aria-labelledby="details-title"', self.markup)
        self.assertIn('id="details-close"', self.markup)
        self.assertIn('data-seg="undecided"', self.markup)
        # The modules app.js calls have to load before it does.
        for module in ("days.js", "snapshot.js", "askai.js"):
            with self.subTest(module=module):
                self.assertLess(self.markup.index(f'src="{module}"'), self.markup.index('src="app.js"'))
        for name in ("Days", "Snapshot", "AskAi"):
            with self.subTest(global_name=name):
                self.assertIn(f"{name}.", self.script)
                self.assertIn(f"root.{name} = api", self.scripts[f"{name.lower()}.js"])
        # Escape, the backdrop, the close button and the phone's back gesture.
        for handler in ("'Escape'", "event.target === overlay", "'details-close'", "'popstate'"):
            with self.subTest(handler=handler):
                self.assertIn(handler, self.script)

    def test_source_text_is_never_written_as_html(self):
        # Titles, venues and prices come from third-party pages. Text nodes only.
        for name, source in self.scripts.items():
            for sink in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval("):
                with self.subTest(script=name, sink=sink):
                    self.assertNotIn(sink, source)

    def test_counters_sit_on_the_buttons_and_nothing_else_competes_with_the_card(self):
        for category in ("interested", "maybe", "rejected"):
            with self.subTest(category=category):
                button = re.search(rf'<button[^>]*data-decide="{category}".*?</button>', self.markup, re.S)
                self.assertIsNotNone(button)
                self.assertIn(f'class="act-count" data-count="{category}"', button.group(0))
        # The top counters, the status line and the keys hint are gone from the deck.
        for gone in ('class="tally', 'id="tallies"', 'data-jump', 'id="clock"', 'hint-keys', 'hint-touch'):
            with self.subTest(gone=gone):
                self.assertNotIn(gone, self.markup)
                self.assertNotIn(gone, self.script)

    def test_the_progress_bar_is_directly_under_the_count_of_events_left(self):
        self.assertRegex(self.markup,
                         r'id="hint-count">[^<]*</p>\s*<div class="progress"[^>]*id="progress">')
        # And the bar is not also at the top of the screen.
        self.assertEqual(self.markup.count('class="progress"'), 1)

    def test_pregled_opens_with_statistics_and_there_is_no_stop_button(self):
        stats = re.search(r'<section class="stats".*?</section>', self.markup, re.S)
        self.assertIsNotNone(stats)
        for identifier in ("st-run", "st-window", "st-today", "st-total", "st-free"):
            with self.subTest(identifier=identifier):
                self.assertIn(f'id="{identifier}"', stats.group(0))
        self.assertLess(self.markup.index('id="list"'), self.markup.index('id="rows"'))
        self.assertNotIn('id="quit"', self.markup)
        self.assertNotIn("/api/", self.script)

    def test_the_event_id_is_one_copy_button_on_the_card_and_in_the_dialog(self):
        template = re.search(r'<template id="copy-id-template">.*?</template>', self.markup, re.S)
        self.assertIsNotNone(template)
        self.assertEqual(template.group(0).count("<button"), 1)
        for part in ('class="copy-id-text"', 'class="copy-icon"', 'class="done-icon"'):
            with self.subTest(part=part):
                self.assertIn(part, template.group(0))
        self.assertIn('data-slot="id"', self.markup)
        self.assertIn("idButton(card.event_id)", self.script)
        self.assertEqual(self.script.count("idButton(card.event_id)"), 2)  # the card and the dialog

    def test_the_card_can_be_tapped_open_and_the_title_is_not_a_visible_heading(self):
        self.assertIn("openDetails(card, null)", self.script)
        self.assertIn('class="sr-only">Dogodki za otroke', self.markup)
        self.assertNotIn('<h1>', self.markup)


if __name__ == "__main__":
    unittest.main()
