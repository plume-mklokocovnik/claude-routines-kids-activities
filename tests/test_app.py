"""Offline tests for the swipe app. Binds a loopback socket, contacts no source."""

import contextlib
import io
import json
import re
import sys
import tempfile
import threading
import unittest
from functools import partial
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "app"))
import server  # noqa: E402
import state  # noqa: E402
from test_state import database, event  # noqa: E402


class PresentationTests(unittest.TestCase):
    def test_card_shows_stored_text_and_never_a_fictional_midnight(self):
        card = server.card(event(start_time="2026-10-10T00:00:00+02:00",
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
        self.assertEqual(server.card(event(start_time="2026-10-10T23:30:00Z"))["day_iso"], "2026-10-11")
        self.assertEqual(server.card(event(start_time="2026-10-25T00:30:00+02:00"))["day_iso"], "2026-10-25")

    def test_card_drops_an_unusable_source_link(self):
        self.assertEqual(server.card(event(url="javascript:alert(1)"))["url"], "")
        self.assertEqual(server.card(event())["url"], "https://example.org/event")

    def test_payload_uses_the_stored_sweep_clock(self):
        data = server.payload(database())
        self.assertEqual(data["clock"], {"date": "28.09.2026", "time": "10:00",
                                         "horizon": "28.12.2026"})
        self.assertEqual(data["counts"]["undecided"], 1)
        self.assertEqual(data["undo"], {"available": False})

    def test_labels_cover_the_three_categories_and_the_undecided_list(self):
        self.assertEqual(server.payload(database())["labels"],
                         {"interested": "Zanima nas", "maybe": "Mogoče",
                          "rejected": "Zavrnjeno", "undecided": "Neodločeno"})

    def test_card_carries_everything_the_details_dialog_shows(self):
        card = server.card(event(url="https://www.example.org/show?id=1",
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
        card = server.card(bare)
        self.assertEqual((card["first_seen"], card["decided_at"]), ("", ""))
        self.assertEqual(server.source_host("javascript:alert(1)"), "")
        self.assertEqual(server.source_host(None), "")
        self.assertEqual(server.source_host("https://sub.example.org:8443/x"), "sub.example.org")


class ClientContractTests(unittest.TestCase):
    """The browser code has no test runner here, so pin the parts a typo breaks."""

    def setUp(self):
        static = ROOT / "app" / "static"
        self.script = (static / "app.js").read_text(encoding="utf-8")
        self.scripts = {name: (static / name).read_text(encoding="utf-8")
                        for name in ("app.js", "days.js", "snapshot.js")}
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
        for module in ("days.js", "snapshot.js"):
            with self.subTest(module=module):
                self.assertLess(self.markup.index(f'src="{module}"'), self.markup.index('src="app.js"'))
        for name in ("Days", "Snapshot"):
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

    def test_the_card_can_be_tapped_open_and_the_title_is_not_a_visible_heading(self):
        self.assertIn("openDetails(card, null)", self.script)
        self.assertIn('class="sr-only">Dogodki za otroke', self.markup)
        self.assertNotIn('<h1>', self.markup)


class ApiTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "db.json"
        db = database()
        db["events"]["2"] = event(event_id="second", title="Puppet show",
                                  start_time="2026-10-11T09:00:00+02:00", category="lutke")
        state.save(self.path, db)

        output = contextlib.redirect_stdout(io.StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)

        app = server.App(str(self.path))
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), partial(server.Handler, app=app))
        app.server = self.httpd
        self.port = self.httpd.server_address[1]
        thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 5)
        self.addCleanup(self.httpd.server_close)
        self.addCleanup(self.httpd.shutdown)

    def call(self, method, path, body=None, headers=None):
        connection = HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            payload = None if body is None else json.dumps(body)
            sent = {"Content-Type": "application/json"} if payload else {}
            sent.update(headers or {})
            connection.request(method, path, body=payload, headers=sent)
            response = connection.getresponse()
            raw = response.read().decode("utf-8")
            kind = response.getheader("Content-Type") or ""
            return response.status, (json.loads(raw) if kind.startswith("application/json") else raw)
        finally:
            connection.close()

    def test_state_serves_the_deck_and_the_page(self):
        status, body = self.call("GET", "/api/state")
        self.assertEqual(status, 200)
        self.assertTrue(body["ok"])
        self.assertEqual([card["event_id"] for card in body["state"]["deck"]],
                         ["sample_20261010_1000", "second"])
        status, page = self.call("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn("card-template", page)
        self.assertEqual(self.call("GET", "/app.js")[0], 200)
        self.assertEqual(self.call("GET", "/app.css")[0], 200)
        status, mode = self.call("GET", "/mode.js")
        self.assertEqual(status, 200)
        self.assertIn("window.SWIPE_MODE = 'server'", mode)
        status, days = self.call("GET", "/days.js")
        self.assertEqual(status, 200)
        self.assertIn("Europe/Ljubljana", days)
        status, snapshot = self.call("GET", "/snapshot.js")
        self.assertEqual(status, 200)
        self.assertIn("createStaticStore", snapshot)

    def test_decide_clear_and_undo_are_written_to_the_database(self):
        status, body = self.call("POST", "/api/decide",
                                 {"event_id": "second", "category": "rejected"})
        self.assertEqual(status, 200)
        self.assertEqual(body["state"]["counts"]["rejected"], 1)
        self.assertEqual([card["event_id"] for card in body["state"]["deck"]],
                         ["sample_20261010_1000"])
        self.assertEqual(state.load(self.path)["events"]["2"]["decision"], "rejected")

        status, body = self.call("POST", "/api/clear", {"event_id": "second"})
        self.assertEqual(status, 200)
        self.assertNotIn("decision", state.load(self.path)["events"]["2"])

        status, body = self.call("POST", "/api/undo", {})
        self.assertEqual(status, 200)
        self.assertEqual(state.load(self.path)["events"]["2"]["decision"], "rejected")
        self.assertEqual(body["state"]["undo"]["restores"], "brez kategorije")

    def test_review_groups_keep_decided_events(self):
        self.call("POST", "/api/decide", {"event_id": "second", "category": "maybe"})
        body = self.call("GET", "/api/state")[1]
        self.assertEqual([card["event_id"] for card in body["state"]["groups"]["maybe"]],
                         ["second"])
        self.assertEqual(body["state"]["groups"]["maybe"][0]["decision"], "maybe")

    def test_bad_requests_are_refused_without_changing_anything(self):
        before = self.path.read_bytes()
        cases = [
            ("POST", "/api/decide", {"event_id": "second", "category": "hmm"}, None, 400),
            ("POST", "/api/decide", {"category": "maybe"}, None, 400),
            ("POST", "/api/clear", {"event_id": "missing"}, None, 404),
            ("POST", "/api/nowhere", {}, None, 404),
            ("GET", "/api/nowhere", None, None, 404),
            ("GET", "/../db.json", None, None, 404),
            ("POST", "/api/undo", {}, {"Origin": "https://evil.example"}, 403),
        ]
        for method, path, body, headers, expected in cases:
            with self.subTest(path=path, headers=headers):
                status, payload = self.call(method, path, body, headers)
                self.assertEqual(status, expected)
                self.assertFalse(payload["ok"])
                self.assertTrue(payload["error"])
        self.assertEqual(self.path.read_bytes(), before)

    def test_same_origin_write_is_accepted(self):
        status, _ = self.call("POST", "/api/decide",
                              {"event_id": "second", "category": "interested"},
                              {"Origin": f"http://127.0.0.1:{self.port}"})
        self.assertEqual(status, 200)

    def test_undo_with_an_empty_log_reports_no_change(self):
        status, body = self.call("POST", "/api/undo", {})
        self.assertEqual(status, 200)
        self.assertEqual(body["message"], "")
        self.assertFalse(body["state"]["undo"]["available"])


if __name__ == "__main__":
    unittest.main()
