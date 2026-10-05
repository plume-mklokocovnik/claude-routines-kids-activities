"""Offline tests for the GitHub Pages build of the swipe app."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "app"))
import build_static  # noqa: E402
import state  # noqa: E402
import swipe  # noqa: E402
from test_state import database, event  # noqa: E402


class BuildTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.work = Path(directory.name)
        self.path = self.work / "db.json"
        self.out = self.work / "site"
        db = database()
        db["events"]["2"] = event(event_id="decided", title="Puppet show",
                                  start_time="2026-10-09T09:00:00+02:00",
                                  category="lutke", decision="maybe",
                                  decided_at="2026-09-30T08:00:00Z")
        # Either side of the daylight-saving change, where ordering the raw
        # strings would put the later instant first.
        db["events"]["3"] = event(event_id="after_dst", title="Late show",
                                  start_time="2026-10-25T02:30:00+01:00", category="kino")
        db["events"]["4"] = event(event_id="before_dst", title="Early show",
                                  start_time="2026-10-25T03:00:00+02:00", category="kino")
        self.db = db
        state.save(self.path, db)

    def snapshot(self):
        return json.loads((self.out / "state.json").read_text(encoding="utf-8"))

    def test_bundle_holds_the_page_and_a_baked_snapshot(self):
        build_static.build(self.path, self.out, repo="owner/name")
        for name in ("index.html", "app.css", "app.js", "days.js", "snapshot.js", "dispatch.js", "askai.js",
                     "mode.js", "state.json",
                     ".nojekyll",
                     "manifest.webmanifest", "icon-192.png", "icon-512.png"):
            with self.subTest(name=name):
                self.assertTrue((self.out / name).is_file())
        # The copied files are the source ones, so the bundle cannot drift.
        for name in build_static.COPIED:
            if name == "index.html":
                continue
            self.assertEqual((self.out / name).read_bytes(),
                             (build_static.STATIC_DIR / name).read_bytes())
        self.assertIn("card-template", (self.out / "index.html").read_text(encoding="utf-8"))

    def test_page_loads_scripts_by_a_version_that_follows_their_content(self):
        import re
        build_static.build(self.path, self.out, repo="owner/name")
        page = (self.out / "index.html").read_text(encoding="utf-8")
        tags = set(re.findall(r'(?:src|href)="(?:app\.css|mode|days|snapshot|dispatch|askai|app)[.a-z]*\?v=([0-9a-f]{10})"', page))
        self.assertEqual(len(tags), 1)
        for name in build_static.VERSIONED:
            self.assertRegex(page, rf'"{re.escape(name)}\?v=[0-9a-f]{{10}}"')
        # The page without the suffixes is the source page, so nothing else changed.
        plain = re.sub(r"\?v=[0-9a-f]{10}", "", page)
        self.assertEqual(plain, (build_static.STATIC_DIR / "index.html").read_text(encoding="utf-8"))
        # A different repository changes mode.js, so the version moves with it.
        other = self.work / "other"
        build_static.build(self.path, other, repo="someone/else")
        self.assertNotIn(next(iter(tags)), (other / "index.html").read_text(encoding="utf-8"))

    def test_bundle_is_installable_as_a_standalone_app(self):
        build_static.build(self.path, self.out, repo="owner/name")
        manifest = json.loads((self.out / "manifest.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual(manifest["display"], "standalone")
        self.assertEqual(manifest["start_url"], "./")
        self.assertEqual({icon["sizes"] for icon in manifest["icons"]}, {"192x192", "512x512"})
        for icon in manifest["icons"]:
            with self.subTest(icon=icon["src"]):
                self.assertTrue((self.out / icon["src"]).is_file())
        page = (self.out / "index.html").read_text(encoding="utf-8")
        self.assertIn('<link rel="manifest" href="manifest.webmanifest">', page)

    def test_mode_script_names_the_save_target(self):
        build_static.build(self.path, self.out, repo="owner/name", branch="trunk",
                           inbox="inbox/patch.txt")
        text = (self.out / "mode.js").read_text(encoding="utf-8")
        target = json.loads(text.split("window.SWIPE_REPO = ", 1)[1].rstrip(";\n"))
        self.assertEqual(target, {"owner": "owner", "repo": "name", "branch": "trunk",
                                  "inbox": "inbox/patch.txt", "hide_inbox": "inbox/hide"})

    def test_missing_repository_still_builds_a_usable_bundle(self):
        build_static.build(self.path, self.out)
        text = (self.out / "mode.js").read_text(encoding="utf-8")
        self.assertIn('"owner": ""', text)
        self.assertTrue(self.snapshot()["cards"])

    def test_snapshot_is_chronological_and_carries_every_card(self):
        build_static.build(self.path, self.out, repo="owner/name")
        snapshot = self.snapshot()
        self.assertEqual(sorted(snapshot), ["cards", "clock", "labels"])
        self.assertEqual([card["event_id"] for card in snapshot["cards"]],
                         ["decided", "sample_20261010_1000", "before_dst", "after_dst"])
        decided = sum(len(rows) for rows in swipe.decided(self.db).values())
        self.assertEqual(len(snapshot["cards"]), len(swipe.deck(self.db)) + decided)
        self.assertEqual(snapshot["labels"], {**swipe.LABELS, "undecided": "Neodločeno"})

    def test_stored_decisions_are_baked_in(self):
        build_static.build(self.path, self.out, repo="owner/name")
        cards = {card["event_id"]: card for card in self.snapshot()["cards"]}
        self.assertEqual(cards["decided"]["decision"], "maybe")
        self.assertIsNone(cards["sample_20261010_1000"]["decision"])

    def test_snapshot_uses_the_stored_sweep_clock(self):
        build_static.build(self.path, self.out, repo="owner/name")
        self.assertEqual(self.snapshot()["clock"],
                         {"date": "28.09.2026", "time": "10:00", "horizon": "28.12.2026"})

    def test_missing_state_refuses_to_build(self):
        with self.assertRaises(OSError):
            build_static.build(self.work / "absent.json", self.out)
        self.assertFalse(self.out.exists())

    def test_generated_files_are_world_readable(self):
        build_static.build(self.path, self.out, repo="owner/name")
        for name in ("mode.js", "state.json"):
            with self.subTest(name=name):
                self.assertEqual((self.out / name).stat().st_mode & 0o044, 0o044)


if __name__ == "__main__":
    unittest.main()
