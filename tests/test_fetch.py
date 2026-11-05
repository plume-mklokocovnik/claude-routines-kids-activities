import email.message
import html
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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


VSI = "https://vsi-eventi.com"
VSI_LISTING = f"{VSI}/?city=2698&categories%5B0%5D=5&start_date=2026-09-28&end_date=2026-12-28"
NEXT = "<button wire:click=\"nextPage('page')\">"


def vsi_card(slug, title, date, venue="", when="", about=""):
    """One vsi-eventi card in the shape the Livewire call returns with details shown."""
    small = '<p class="text-xs md:text-sm line-clamp-2">{}</p>'
    return (f'<div class="max-w-sm bg-white border"><a href="{VSI}/event/{slug}" wire:navigate></a>'
            '<p class="items-center rounded-md bg-purple-50 px-1.5">Za otroke</p>'
            f'<a href="{VSI}/event/{slug}"><h5 class="text-sm"> {title}</h5></a>'
            + (f'<p class="text-xs md:text-base font-normal text-gray-700 line-clamp-2"> {about}</p>' if about else "")
            + f'<a href="{VSI}?city=2698" class="text-sm text-black"> Ljubljana </a><!--[if ENDBLOCK]><![endif]-->'
            + (small.format(venue) if venue else "")
            + f'<p class="text-sm sm:text-base text-black"> {date} </p>'
            + (small.format(when) if when else "") + "</div>")


def vsi_listing(cards, pager=False):
    snapshot = html.escape(json.dumps({"memo": {"name": "events-overview"}, "data": {"hideDetails": True}}))
    return (f'<meta name="csrf-token" content="tok"><div wire:snapshot="{snapshot}">'
            + "".join(cards) + (NEXT if pager else "") + "</div>")


def livewire(listing, replies):
    """GET answers the listing. Each POST answers the next reply and is kept for inspection."""
    posts = []

    def get(url, data=None):
        if data is None:
            return (200, listing, "") if url == VSI_LISTING else (404, "", "HTTP 404")
        posts.append(json.loads(data))
        reply = replies[len(posts) - 1]
        return reply if isinstance(reply, tuple) else (200, json.dumps({"components": [
            {"snapshot": f"s{len(posts)}", "effects": {"html": reply}}]}), "")
    return get, posts


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

    def test_cankarjev_dom_feed_reads_only_youth_pages_up_front(self):
        feed = ("<response>"
                "<item><title>Svet je kakor ringaraja</title><link>https://www.cd-cc.si/a</link>"
                "<category>Za mlade in šole</category><ical_location>Linhartova dvorana</ical_location>"
                "<ical_dtstart>2026-10-20T17:00:00+02:00</ical_dtstart></item>"
                "<item><title>Simfonični večer</title><link>https://www.cd-cc.si/b</link><category>Glasba</category>"
                "<ical_location>Gallusova dvorana</ical_location><ical_dtstart>2026-10-21T19:30:00+02:00</ical_dtstart></item>"
                "<item><title>Lani</title><link>https://www.cd-cc.si/c</link><category>Glasba</category>"
                "<ical_dtstart>2025-10-21T19:30:00+02:00</ical_dtstart></item></response>")
        fetcher = fetch.Fetcher(stub({"https://www.cd-cc.si/feeds/kulturnik": feed,
                                      "https://www.cd-cc.si/a": "<h1>Ringaraja</h1> Od 5. do 10. leta"}))
        rows = fetch.cankarjevdom(fetcher, self.context())
        self.assertEqual([(item["title"], item["venue"], item["start_time"], item["verified"]) for item in rows], [
            ("Svet je kakor ringaraja", "Cankarjev dom, Linhartova dvorana", "2026-10-20T17:00:00+02:00", True),
            ("Simfonični večer", "Cankarjev dom, Gallusova dvorana", "2026-10-21T19:30:00+02:00", False)])
        self.assertEqual(rows[0]["notes"], "Ringaraja Od 5. do 10. leta")
        self.assertEqual(len(fetcher.sources), 2)

    def test_cancelled_rows_are_marked_and_keep_their_stored_twin(self):
        rows = [fetch.row("[ODPOVEDANO] Family workshop", "2026-10-10T10:00:00+02:00", [], "Museum",
                          "https://example.org/event", False)]
        kept, _ = self.context().annotate(rows)
        self.assertEqual((kept[0]["stored"], kept[0]["cancelled"]), ("sample_20261010_1000", True))

    def test_http_falls_back_to_curl_when_python_gets_no_answer(self):
        failure = fetch.urllib.error.URLError("certificate verify failed")
        answer = subprocess.CompletedProcess([], 0, stdout="<h1>SiTi</h1>\n200".encode())
        with patch("fetch.urllib.request.urlopen", side_effect=failure), \
                patch("fetch.shutil.which", return_value="/usr/bin/curl"), \
                patch("fetch.subprocess.run", return_value=answer) as curl:
            self.assertEqual(fetch.http("https://www.sititeater.si/"), (200, "<h1>SiTi</h1>", ""))
        self.assertIn("https://www.sititeater.si/", curl.call_args.args[0])

    def test_http_keeps_cookies_and_sends_json_bodies_as_json(self):
        seen = []

        class Reply(io.BytesIO):
            status = 200

            def info(self):
                message = email.message.Message()
                message["Set-Cookie"] = "session_test=1; Path=/"
                return message

        def answer(request, timeout):
            seen.append(request)
            return Reply(b"ok")
        try:
            with patch("fetch.urllib.request.urlopen", side_effect=answer):
                fetch.http("https://cookies.example.org/")
                fetch.http("https://cookies.example.org/update", '{"a": 1}')
                fetch.http("https://cookies.example.org/form", "a=1")
        finally:
            fetch.COOKIES.clear("cookies.example.org")
        self.assertIsNone(seen[0].get_header("Cookie"))
        self.assertIn("session_test=1", seen[1].get_header("Cookie"))
        self.assertEqual([request.get_header("Content-type") for request in seen[1:]],
                         ["application/json", "application/x-www-form-urlencoded"])

    def test_vsi_eventi_reads_details_through_the_livewire_call_page_by_page(self):
        first = [vsi_card("a-2026-10-03-ljubljana", "Afriško sonce", "Sobota, 3.10.2026", "SiTi Teater BTC",
                          "Dogodek se začne 03. 10. 2026 ob 10:30.", "V afriški savani ..."),
                 vsi_card("b-2026-10-08-ljubljana", "Vrzi žogo", "Četrtek, 8.10.2026", "Supernova Ljubljana Šiška",
                          "Vsak četrtek med 15. oktobrom in 26. novembrom 2026, ob 16:30")]
        second = [vsi_card("c-2026-10-10-ljubljana", "DadaDisko", "Sobota, 10.10.2026", "Katedrala, Kino Šiška",
                           "dogodek poteka od 10.00 do 13.00"),
                  vsi_card("d-2026-12-05-ljubljana", "Miklavžev sprevod", "Sobota, 5.12.2026", when="Od 5.12.2026 do 6.12.2026"),
                  first[0]]
        get, posts = livewire(vsi_listing(first[:1], pager=True), ["".join(first) + NEXT, "".join(second)])
        fetcher = fetch.Fetcher(get)
        rows = fetch.vsieventi(fetcher, self.context())
        self.assertEqual([(item["title"], item["start_time"], item["flags"], item["venue"]) for item in rows], [
            ("Afriško sonce", "2026-10-03T10:30:00+02:00", [], "SiTi Teater BTC"),
            ("Vrzi žogo", "2026-10-08T16:30:00+02:00", [], "Supernova Ljubljana Šiška"),
            ("DadaDisko", "2026-10-10T10:00:00+02:00", [], "Katedrala, Kino Šiška"),
            ("Miklavžev sprevod", "2026-12-05T00:00:00+01:00", ["time_unknown"], "")])
        self.assertEqual((rows[0]["notes"], rows[0]["tags"], rows[0]["city"], rows[0]["verified"], rows[0]["url"]),
                         ("V afriški savani ...", ["Za otroke"], "Ljubljana", False, f"{VSI}/event/a-2026-10-03-ljubljana"))
        self.assertEqual([(post["_token"], post["components"][0]["updates"], post["components"][0]["calls"])
                          for post in posts], [
            ("tok", {"hideDetails": False}, []),
            ("tok", {}, [{"path": "", "method": "nextPage", "params": ["page"]}])])
        self.assertEqual(posts[1]["components"][0]["snapshot"], "s1")
        self.assertEqual([source["status"] for source in fetcher.sources], ["ok"] * 3)
        self.assertEqual(fetcher.notes, [])

    def test_vsi_eventi_falls_back_to_the_plain_listing_and_says_so(self):
        listing = vsi_listing([vsi_card("a-2026-10-03-ljubljana", "Afriško sonce", "Sobota, 3.10.2026")], pager=True)
        get, _ = livewire(listing, [(419, "", "HTTP 419")])
        with tempfile.TemporaryDirectory() as directory:
            summary = fetch.pull(batch(), database(), ["vsieventi"], Path(directory), get)
            written = json.loads((Path(directory) / "vsieventi.json").read_text())
        self.assertEqual([(item["title"], item["flags"], item["venue"]) for item in written["rows"]],
                         [("Afriško sonce", ["time_unknown"], "")])
        self.assertEqual([(source["status"], source.get("reason")) for source in written["sources"]],
                         [("ok", None), ("failed", "HTTP 419")])
        self.assertEqual(written["notes"], summary["vsieventi"]["notes"])
        self.assertIn("Only its first page was read", written["notes"][0])

    def test_vsi_eventi_notes_when_the_listing_reaches_the_page_cap(self):
        def page(number):
            return "".join(vsi_card(f"e{number}-{index}-2026-10-03-ljubljana", f"E {number} {index}", "Sobota, 3.10.2026")
                           for index in range(36)) + (NEXT if number < 5 else "")
        get, posts = livewire(vsi_listing([]), [page(number) for number in range(1, 6)])
        fetcher = fetch.Fetcher(get)
        self.assertEqual((len(fetch.vsieventi(fetcher, self.context())), len(posts)), (180, 5))
        self.assertIn("cap of 5 pages", fetcher.notes[0])

    def test_record_stamps_the_current_time(self):
        with tempfile.TemporaryDirectory() as directory:
            sources = fetch.record("slovenia", ["https://example.org/a"], Path(directory), failed="HTTP 403")
            self.assertEqual((sources[0]["status"], sources[0]["reason"]), ("failed", "HTTP 403"))
            self.assertGreater(state.timestamp(sources[0]["checked_at"]), state.timestamp(batch()["started_at"]))
            with self.assertRaises(ValueError):
                fetch.record("slovenia", ["not a url"], Path(directory))

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
