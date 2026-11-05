import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import fetch
import state
from test_run import batch
from test_state import database, event

KINO = "https://www.kino-bezigrad.si"
SHOW = f"{KINO}/predstava/jezeva-hisica/"


def stub(pages):
    def get(url, data=None):
        key = f"{url}?{data}" if data else url
        return (200, pages[key], "") if key in pages else (404, "", "HTTP 404")
    return get


class FetchTests(unittest.TestCase):
    def context(self, db=None):
        return fetch.Context(batch(), db or database())

    def test_kino_bezigrad_reads_times_from_the_booking_call(self):
        ajax = f"{KINO}/wp-admin/admin-ajax.php"
        pages = {
            f"{KINO}/predstave-in-delavnice/": f'<li id="post-75629"><div class="movie_title"><a href="{SHOW}">JEŽEVA HIŠICA</a></div></li>',
            SHOW: '<div class="info event_restriction">3+</div><p>Vstopnice po ceni 8,10 €. </p>'
                  '<script>var movieScreeningDates = ["2026-10-17", "2027-03-01"];</script>',
            f"{ajax}?action=event-filter&date=10.17.2026&post_id=75629&all_tickets=": '<a data-hour="11:00">Nakup</a>',
        }
        fetcher = fetch.Fetcher(stub(pages))
        rows = fetch.kinobezigrad(fetcher, self.context())
        self.assertEqual([(item["start_time"], item["flags"], item["age_min"]) for item in rows],
                         [("2026-10-17T11:00:00+02:00", [], 3)])
        self.assertIn("8,10 €", rows[0]["price_text"])
        self.assertTrue(all(source["status"] == "ok" for source in fetcher.sources))
        self.assertEqual(len(fetcher.sources), 3)

    def test_failed_requests_are_recorded_with_a_reason_and_real_time(self):
        fetcher = fetch.Fetcher(stub({}))
        self.assertIsNone(fetcher.fetch("https://example.org/gone", "slovenia"))
        source = fetcher.sources[0]
        self.assertEqual((source["status"], source["reason"]), ("failed", "HTTP 404"))
        self.assertGreater(state.timestamp(source["checked_at"]), state.timestamp(batch()["started_at"]))

    def test_annotate_drops_window_and_hidden_rows_and_names_stored_ones(self):
        db = database()
        db["events"]["2"] = event(event_id="hidden_one", title="Skrito", status="hidden")
        db["user_rules"]["1"]["exclude_keywords"] = ["Ura pravljic"]
        rows = [
            fetch.row("Family workshop", "2026-10-10T10:00:00+02:00", [], "Museum, Ljubljana", "https://example.org/event", True),
            fetch.row("Ura pravljic", "2026-10-11T10:00:00+02:00", [], "Knjižnica", "https://example.org/a", False),
            fetch.row("Skrito (razprodano)", "2026-10-10T10:00:00+02:00", [], "Museum", "https://example.org/b", True),
            fetch.row("Old", "2026-09-01T10:00:00+02:00", [], "Museum", "https://example.org/c", True),
            fetch.row("Far", "2027-03-01T10:00:00+01:00", [], "Museum", "https://example.org/d", True),
            fetch.row("New", "2026-10-12T10:00:00+02:00", [], "Museum", "https://example.org/e", True),
        ]
        kept, dropped = self.context(db).annotate(rows)
        self.assertEqual([item["title"] for item in kept], ["Family workshop", "New"])
        self.assertEqual(kept[0]["stored"], "sample_20261010_1000")
        self.assertEqual(dropped, {"outside_window": 2, "hidden": 2})

    def test_svamz_reads_firestore_documents_in_the_window(self):
        base = "https://firestore.googleapis.com/v1/projects/p/databases/(default)/documents/"
        document = {"name": f"{base}dogodki/2026-10-20-srecanje",
                    "fields": {"title": {"stringValue": "Srečanje"}, "start": {"stringValue": "2026-10-20"},
                               "place": {"stringValue": "Vrhnika"}}}
        pages = {"https://svamz.com/js/dogodki-data.js": f'var BASE = "{base}"; var KEY = "k";',
                 f"{base}dogodki?pageSize=300&key=k": json.dumps({"documents": [document]}),
                 "https://svamz.com/event.html?id=2026-10-20-srecanje": "<html>shell</html>"}
        rows = fetch.svamz(fetch.Fetcher(stub(pages)), self.context())
        self.assertEqual([(item["title"], item["start_time"], item["flags"], item["venue"], item["verified"])
                          for item in rows],
                         [("Srečanje", "2026-10-20T00:00:00+02:00", ["time_unknown"], "Vrhnika", True)])

    def test_page_text_skips_navigation_and_share_links(self):
        markup = ('<nav>Domov Aktualno</nav><h1>Kuharska delavnica</h1>Deli na: Deli na Facebooku '
                  '(Odpre se v novem oknu) <p>Za otroke od 6. leta.</p><script>x()</script>')
        self.assertEqual(fetch.page(markup)["text"], "Kuharska delavnica Za otroke od 6. leta.")
        self.assertEqual(fetch.slug("Ustvarjalnice z Galerijo C.C.U.: DEŽELA"), "ustvarjalnice-z-galerijo-ccu-dezela")

    def test_pull_and_verify_write_files_with_source_records(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            summary = fetch.pull(batch(), database(), ["zoo"], folder, stub({
                "https://trgovina.zoo.si/wp-json/wp/v2/product?per_page=50": json.dumps([
                    {"title": {"rendered": "Srečanje z Dedkom Mrazom"}, "link": "https://trgovina.zoo.si/a/",
                     "product_cat": [19], "content": {"rendered": "<p>Termini: 12. 12.</p>"}},
                    {"title": {"rendered": "Majica"}, "link": "https://trgovina.zoo.si/b/", "product_cat": [3],
                     "content": {"rendered": ""}}])}))
            self.assertEqual(summary["zoo"]["rows"], 1)
            written = json.loads((folder / "zoo.json").read_text())
            self.assertEqual(written["rows"][0]["notes"], "Termini: 12. 12.")
            pages = fetch.verify("ljubljana", ["https://example.org/x"], folder,
                                 stub({"https://example.org/x": "<h1>X</h1>"}))
            self.assertEqual(pages[0]["text"], "X")
            self.assertEqual(len(list(folder.glob("verify-ljubljana-*.json"))), 1)


if __name__ == "__main__":
    unittest.main()
