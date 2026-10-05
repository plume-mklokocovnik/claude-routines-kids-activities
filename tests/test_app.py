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
                        for name in ("app.js", "days.js", "filters.js", "snapshot.js", "dispatch.js", "askai.js")}
        self.markup = (static / "index.html").read_text(encoding="utf-8")
        self.styles = (static / "app.css").read_text(encoding="utf-8")

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
        for module in ("days.js", "filters.js", "snapshot.js", "dispatch.js", "askai.js"):
            with self.subTest(module=module):
                self.assertLess(self.markup.index(f'src="{module}"'), self.markup.index('src="app.js"'))
        for name in ("Days", "Filters", "Snapshot", "Dispatch", "AskAi"):
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

    def test_the_page_can_only_talk_to_itself_and_the_github_api(self):
        # A device token sits in this browser's storage. A policy that allows no
        # other script and no other destination is what keeps a stray script from
        # sending it anywhere.
        policy = re.search(r'http-equiv="Content-Security-Policy" content="([^"]+)"', self.markup)
        self.assertIsNotNone(policy)
        rules = dict(rule.strip().split(" ", 1) for rule in policy.group(1).split(";"))
        self.assertEqual(rules["script-src"] if "script-src" in rules else rules["default-src"], "'self'")
        self.assertEqual(rules["connect-src"], "'self' https://api.github.com")
        self.assertEqual(rules["object-src"], "'none'")
        self.assertEqual(rules["base-uri"], "'none'")
        # Nothing inline for the policy to trip over, and nothing loaded from afar.
        self.assertNotRegex(self.markup, r"<script(?![^>]*\bsrc=)")
        self.assertNotRegex(self.markup, r"\son[a-z]+=")
        self.assertNotRegex(self.markup, r'<(?:script|link|img)[^>]+(?:src|href)="https?://')

    def test_the_token_stays_out_of_urls_logs_and_the_page(self):
        client = self.scripts["dispatch.js"]
        self.assertNotIn("console.", client)
        self.assertNotIn("location", client)
        # It only travels in a header, and the field that takes it is a password field.
        self.assertIn("Authorization: `Bearer ${token}`", client)
        self.assertRegex(self.markup, r'<input[^>]*id="quick-token"[^>]*type="password"|'
                                      r'<input[^>]*type="password"[^>]*id="quick-token"')
        for name, source in self.scripts.items():
            if name != "dispatch.js":
                with self.subTest(script=name):
                    self.assertNotIn("Bearer", source)

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

    def test_the_figures_and_token_settings_live_on_the_info_page_not_in_pregled(self):
        info = re.search(r'<section class="view" id="view-info".*?</main>', self.markup, re.S)
        review = re.search(r'<section class="view" id="view-review".*?<section class="view" id="view-info"',
                           self.markup, re.S)
        self.assertIsNotNone(info)
        self.assertIsNotNone(review)
        identifiers = ("ver-app", "ver-data", "st-run", "st-age", "st-window", "st-today", "st-unsaved", "st-total", "st-free",
                       "st-week", "st-weekend", "st-decided", "st-next", "bars-months",
                       "bars-categories", "bars-sources", "quick", "quick-token", "quick-none")
        for identifier in identifiers:
            with self.subTest(identifier=identifier):
                self.assertEqual(info.group(0).count(f'id="{identifier}"'), 1)
                self.assertNotIn(f'id="{identifier}"', review.group(0))
        self.assertNotIn('class="stats"', review.group(0))
        self.assertNotIn('class="quick', review.group(0))
        # The token settings come after the figures.
        self.assertLess(info.group(0).index('id="st-run"'), info.group(0).index('id="quick-token"'))
        self.assertRegex(info.group(0), r'<input[^>]*id="quick-token"[^>]*type="password"')
        self.assertLess(self.markup.index('id="list"'), self.markup.index('id="rows"'))
        self.assertNotIn('id="quit"', self.markup)
        self.assertNotIn("/api/", self.script)

    def test_the_tab_bar_has_two_lists_and_one_gear_for_info_and_settings(self):
        nav = re.search(r'<nav class="tabs">.*?</nav>', self.markup, re.S)
        self.assertIsNotNone(nav)
        self.assertEqual(re.findall(r'data-view="(\w+)"', nav.group(0)), ["swipe", "review", "info"])
        gear = re.search(r'<button[^>]*data-view="info".*?</button>', nav.group(0), re.S)
        self.assertIsNotNone(gear)
        self.assertIn("tab-icon", gear.group(0))
        self.assertIn('aria-label="Info in nastavitve"', gear.group(0))
        self.assertIn("<svg", gear.group(0))
        self.assertNotIn("tab-done", gear.group(0))
        self.assertIn("el('view-info').hidden = name !== 'info'", self.script)
        self.assertIn("grid-template-columns: 1fr 1fr auto", self.styles)

    def test_the_charts_are_drawn_from_text_nodes_and_handle_an_empty_list(self):
        for part in ("function renderBars", "renderCharts();", "Ni podatkov", "Date.UTC"):
            with self.subTest(part=part):
                self.assertIn(part, self.script)
        # Weekdays and day offsets come from ISO strings, never from the device clock.
        figures = self.script[self.script.index("function isoDay"):self.script.index("function renderCharts")]
        for local in ("Date.now", "new Date()", ".getDay(", ".getDate(", "getTimezoneOffset"):
            with self.subTest(local=local):
                self.assertNotIn(local, figures)

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

    def test_rows_are_display_only_and_the_dialog_holds_the_decision_buttons(self):
        row = re.search(r'<template id="row-template">.*?</template>', self.markup, re.S).group(0)
        self.assertNotIn("data-move", row)
        self.assertNotIn("row-actions", row)
        self.assertNotIn("mini", row)
        self.assertEqual(row.count("<button"), 1)  # the title that opens the dialog
        self.assertIn('class="row-more"', row)
        for gone in ("row-actions", ".mini", "data-move"):
            with self.subTest(gone=gone):
                self.assertNotIn(gone, self.styles)
                self.assertNotIn(gone, self.script)
        group = re.search(r'<div class="sheet-decide" id="d-decide".*?</div>\s*</div>', self.markup, re.S).group(0)
        self.assertEqual(re.findall(r'data-pick="(\w*)"', group), ["interested", "maybe", "rejected", ""])
        self.assertIn("Odločitev", group)
        sheet = self.markup[self.markup.index('id="sheet"'):]
        order = [sheet.index(part) for part in ('id="d-notes"', 'id="d-decide"', 'id="d-source"', 'id="d-maps"')]
        self.assertEqual(order, sorted(order))
        # Only a row of Pregled offers the group. The deck card opens the dialog without it.
        self.assertIn("openDetails(card, opener, { decide: true })", self.script)
        self.assertIn("openDetails(card, null)", self.script)
        self.assertIn("move(card, target)", self.script)

    def test_the_filter_bar_and_selection_bar_sit_between_the_tabs_and_the_list(self):
        review = re.search(r'<section class="view" id="view-review".*?<section class="view" id="view-info"',
                           self.markup, re.S).group(0)
        parts = ('id="segments"', 'id="filterbar"', 'id="list"', 'id="selbar"')
        positions = [review.index(part) for part in parts]
        self.assertEqual(positions, sorted(positions))
        for identifier in ("filter-search", "filter-search-clear", "filters-toggle", "filters-badge",
                           "select-toggle", "filter-panel", "filter-from", "filter-to", "filter-cats",
                           "filter-free", "filter-chips", "filter-result", "filter-clear",
                           "sel-count", "sel-all", "sel-done", "sel-actions"):
            with self.subTest(identifier=identifier):
                self.assertEqual(review.count(f'id="{identifier}"'), 1)
        toggle = re.search(r'<button[^>]*id="filters-toggle"[^>]*>', review).group(0)
        self.assertIn('aria-expanded="false"', toggle)
        self.assertIn('aria-controls="filter-panel"', toggle)
        search = re.search(r'<input[^>]*id="filter-search"[^>]*>', review).group(0)
        self.assertIn('type="search"', search)
        self.assertIn('placeholder="Išči dogodke"', search)
        self.assertEqual(len(re.findall(r'type="date"', review)), 2)
        self.assertIn('id="filter-result" aria-live="polite"', review)
        self.assertIn('role="switch"', review)

    def test_segment_counters_have_their_own_attribute_and_the_true_totals_stay(self):
        segments = re.search(r'<div class="segments".*?</div>', self.markup, re.S).group(0)
        self.assertNotIn("data-count=", segments)
        self.assertEqual(len(re.findall(r'data-seg-count="\w+"', segments)), 4)
        self.assertIn("[data-seg-count]", self.script)
        # The badges on the swipe buttons keep reading the unfiltered counts.
        self.assertIn("document.querySelectorAll('[data-count]')", self.script)

    def test_selection_and_filters_are_reset_and_guarded_where_the_spec_says(self):
        self.assertIn("filters: Filters.empty()", self.script)
        self.assertNotIn("localStorage", self.script[self.script.index("/* --- filters"):
                                                      self.script.index("/* --- swipe mechanics")])
        # The round hide-all button is off while selecting or filtering.
        fab = self.script[self.script.index("function renderFab"):self.script.index("function segmentRows")]
        self.assertIn("!st.selecting", fab)
        self.assertIn("Filters.isActive(st.filters)", fab)
        # Leaving Pregled and Escape both end the selection.
        self.assertIn("if (name !== 'review') setSelecting(false);", self.script)
        self.assertIn("event.key === 'Escape' && st.selecting", self.script)
        self.assertIn("decideMany", self.script)
        self.assertIn("Premaknjeno: ${ids.length}", self.script)
        self.assertIn("Ni zadetkov za izbrane filtre.", self.script)
        # Rows are rows of real checkboxes with an accessible name.
        self.assertIn('<input class="row-check" type="checkbox">', self.markup)
        self.assertIn("aria-label", self.script[self.script.index("function buildRow"):
                                                self.script.index("function renderFab")])

    def test_every_wire_function_is_called(self):
        defined = set(re.findall(r"^function (wire\w*)\(", self.script, re.M))
        called = set(re.findall(r"^\s+(wire\w*)\(\);", self.script, re.M)) | {"wire"}
        self.assertIn("wireFilters", defined)
        self.assertIn("wireSelection", defined)
        self.assertEqual(sorted(defined - called), [])

    def test_filter_code_never_reads_the_wall_clock_or_the_device_calendar(self):
        region = self.script[self.script.index("/* --- filters"):self.script.index("/* --- swipe mechanics")]
        for name, source in (("app.js filters", region), ("filters.js", self.scripts["filters.js"])):
            for local in ("Date.now", "new Date()", ".getDay(", ".getDate(", ".getMonth(", ".getFullYear(",
                          ".getHours(", "getTimezoneOffset", "toLocale", "Days.today"):
                with self.subTest(source=name, local=local):
                    self.assertNotIn(local, source)

    def test_the_interactive_controls_are_touch_sized_and_show_focus(self):
        for selector in (".search-input", ".bar-btn", ".dec", ".sel-link", ".switch"):
            block = re.search(r"(?m)^" + re.escape(selector) + r"(?:, [.\w-]+)* \{[^}]*\}", self.styles)
            with self.subTest(selector=selector):
                self.assertIsNotNone(block)
                self.assertRegex(block.group(0), r"(?:min-)?height: 44px")
        self.assertIn(".dec:focus-visible", self.styles)
        self.assertIn(".row-check:focus-visible + .row-box", self.styles)
        self.assertIn(".dec[hidden]", self.styles)


if __name__ == "__main__":
    unittest.main()
