"""The hand-off to an AI assistant, run through Node against the real askai.js.

Skipped when Node is not installed.
"""

import json
import unittest
from urllib.parse import parse_qs, unquote, urlsplit

import node_runner
from node_runner import NODE


def evaluate(expression):
    return node_runner.run(f"{node_runner.require('askai.js')} return {expression};")


def prompt(card, place):
    return evaluate(f"AskAi.prompt({json.dumps(card)}, {json.dumps(place)})")


CARD = {
    "title": "Pravljica: Zajec & lisica; 50% popust",
    "day": "Sobota", "date": "10.10.2026", "time": "10:00",
    "age": "3+", "price": "5 EUR", "is_free": False,
    "category": "theatre_puppets", "notes": ["rezervacija", "bring socks"],
    "url": "https://example.org/dogodek?id=1&x=2",
}


@unittest.skipUnless(NODE, "node is not installed")
class AskAiTests(unittest.TestCase):
    def test_prompt_carries_the_stored_facts_and_asks_for_a_web_search(self):
        text = prompt(CARD, "Kino Šiška, Ljubljana")
        self.assertIn("Search the web", text)
        for line in ("Event: Pravljica: Zajec & lisica; 50% popust",
                     "When: Sobota 10.10.2026 at 10:00",
                     "Where: Kino Šiška, Ljubljana",
                     "Age: 3+ years",
                     "Price: 5 EUR",
                     "Category: theatre puppets",
                     "Notes: rezervacija, bring socks",
                     "Source: https://example.org/dogodek?id=1&x=2"):
            with self.subTest(line=line):
                self.assertIn(line, text)

    def test_prompt_leaves_out_what_is_not_known_instead_of_inventing_it(self):
        bare = {"title": "Samo naslov", "date": "", "time": "?", "age": "?", "price": "",
                "category": "", "notes": [], "url": ""}
        body = prompt(bare, "?").split("\n\n", 1)[1]
        self.assertEqual(body, "Event: Samo naslov")

    def test_free_events_say_so(self):
        card = {"title": "T", "price": "Brezplačno", "is_free": True, "notes": []}
        self.assertIn("Price: free", prompt(card, ""))
        self.assertNotIn("Brezplačno", prompt(card, ""))

    def test_intent_url_shares_the_text_to_one_app_and_falls_back_to_the_web(self):
        text = "a=b; c%d\nline two"
        url = evaluate(f"AskAi.intentUrl('claude', {json.dumps(text)})")
        self.assertTrue(url.startswith("intent:#Intent;action=android.intent.action.SEND;type=text/plain;"))
        self.assertTrue(url.endswith(";end"))
        # A `;` or `=` left inside a value would break the link apart.
        parts = url[len("intent:#Intent;"):-len(";end")].split(";")
        fields = dict(part.split("=", 1) for part in parts)
        self.assertEqual(fields["package"], "com.anthropic.claude")
        self.assertEqual(unquote(fields["S.android.intent.extra.TEXT"]), text)
        fallback = unquote(fields["S.browser_fallback_url"])
        self.assertTrue(fallback.startswith("https://claude.ai/new?q="))
        self.assertEqual(parse_qs(urlsplit(fallback).query)["q"], [text])

    def test_each_assistant_has_its_own_package_and_web_page(self):
        found = evaluate("Object.fromEntries(Object.entries(AskAi.TARGETS)"
                         ".map(([k, t]) => [k, [t.pkg, t.web('hi there')]]))")
        self.assertEqual(found["chatgpt"], ["com.openai.chatgpt", "https://chatgpt.com/?hints=search&q=hi%20there"])
        self.assertEqual(found["claude"], ["com.anthropic.claude", "https://claude.ai/new?q=hi%20there"])
        self.assertEqual(found["gemini"], ["com.google.android.apps.bard", "https://gemini.google.com/app"])

    def test_android_is_told_from_the_user_agent(self):
        self.assertTrue(evaluate("AskAi.isAndroid('Mozilla/5.0 (Linux; Android 16; SM-S938B) Chrome/140')"))
        self.assertFalse(evaluate("AskAi.isAndroid('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')"))
        self.assertFalse(evaluate("AskAi.isAndroid(undefined)"))


if __name__ == "__main__":
    unittest.main()
