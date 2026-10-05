"""Saving by starting a workflow, run through Node against the real dispatch.js.

The page keeps one fine-grained token per device and calls GitHub's Actions API
with it. These cover what is sent, how a refused token is told apart from a dead
network, and that tokens stay separate between devices. Skipped when Node is not
installed.
"""

import unittest

import node_runner
from node_runner import NODE

TOKEN = "github_pat_" + "A1b2C3d4E5" * 4
OTHER = "github_pat_" + "Z9y8X7w6V5" * 4

PRELUDE = node_runner.require("dispatch.js") + f"""
const TOKEN = {TOKEN!r};
const OTHER = {OTHER!r};
const memory = (initial) => {{
  const data = new Map(initial === undefined ? [] : [[Dispatch.KEY, initial]]);
  return {{ data,
           getItem: (key) => (data.has(key) ? data.get(key) : null),
           setItem: (key, value) => {{ data.set(key, value); }},
           removeItem: (key) => {{ data.delete(key); }} }};
}};
// A stand-in for api.github.com that answers with whatever status it is told to.
const github = (status) => {{
  const server = {{ status, calls: [], down: false }};
  server.fetch = async (url, options) => {{
    server.calls.push({{ url, method: options.method, headers: options.headers,
                        body: options.body ? JSON.parse(options.body) : null }});
    if (server.down) throw new TypeError('Failed to fetch');
    return {{ ok: server.status >= 200 && server.status < 300, status: server.status }};
  }};
  return server;
}};
const REPO = {{ owner: 'me', repo: 'kids', branch: 'main' }};
const make = (storage, server, repo) => Dispatch.createClient({{
  fetch: (...args) => server.fetch(...args), storage, repo: repo === undefined ? REPO : repo }});
"""


def evaluate(body):
    return node_runner.run(PRELUDE + body)


@unittest.skipUnless(NODE, "node is not installed")
class DispatchTests(unittest.TestCase):
    def test_a_decision_patch_starts_the_apply_workflow(self):
        got = evaluate("""
          const server = github(204);
          const client = make(memory(TOKEN), server);
          const result = await client.send('decisions', 'i:a\\nr:b\\n');
          return { result, call: server.calls[0] };""")
        self.assertEqual(got["result"], {"ok": True})
        call = got["call"]
        self.assertEqual(call["url"], "https://api.github.com/repos/me/kids/actions/workflows/apply-decisions.yml/dispatches")
        self.assertEqual(call["method"], "POST")
        self.assertEqual(call["body"], {"ref": "main", "inputs": {"patch": "i:a\nr:b\n"}})
        self.assertEqual(call["headers"]["Authorization"], f"Bearer {TOKEN}")
        self.assertEqual(call["headers"]["X-GitHub-Api-Version"], "2022-11-28")

    def test_a_hide_list_starts_the_hide_workflow_with_its_own_input(self):
        got = evaluate("""
          const server = github(204);
          await make(memory(TOKEN), server).send('hide', 'x\\ny\\n');
          return server.calls[0];""")
        self.assertTrue(got["url"].endswith("/actions/workflows/hide-events.yml/dispatches"))
        self.assertEqual(got["body"]["inputs"], {"ids": "x\ny\n"})

    def test_the_branch_comes_from_the_page(self):
        got = evaluate("""
          const server = github(204);
          const client = make(memory(TOKEN), server, { owner: 'me', repo: 'kids', branch: 'trunk' });
          await client.send('decisions', 'i:a\\n');
          return server.calls[0].body.ref;""")
        self.assertEqual(got, "trunk")

    def test_without_a_token_nothing_is_sent(self):
        got = evaluate("""
          const server = github(204);
          const client = make(memory(), server);
          return { enabled: client.enabled(), result: await client.send('decisions', 'i:a\\n'),
                   calls: server.calls.length };""")
        self.assertFalse(got["enabled"])
        self.assertEqual(got["result"]["reason"], "disabled")
        self.assertEqual(got["calls"], 0)

    def test_an_unknown_repository_sends_nothing_even_with_a_token(self):
        got = evaluate("""
          const server = github(204);
          const client = make(memory(TOKEN), server, {});
          return { available: client.available(), enabled: client.enabled(),
                   result: await client.send('decisions', 'i:a\\n'), calls: server.calls.length };""")
        self.assertFalse(got["available"])
        self.assertFalse(got["enabled"])
        self.assertEqual(got["result"]["reason"], "unknown")
        self.assertEqual(got["calls"], 0)

    def test_a_patch_over_the_workflow_limit_is_not_sent(self):
        got = evaluate("""
          const server = github(204);
          const client = make(memory(TOKEN), server);
          return { result: await client.send('decisions', 'i:a\\n'.repeat(Dispatch.MAX_CHARS)),
                   calls: server.calls.length };""")
        self.assertEqual(got["result"]["reason"], "tooBig")
        self.assertEqual(got["calls"], 0)

    def test_every_refusal_has_a_reason_the_page_can_show(self):
        got = evaluate("""
          const out = {};
          for (const status of [401, 403, 404, 422, 500]) {
            const client = make(memory(TOKEN), github(status));
            const result = await client.send('decisions', 'i:a\\n');
            out[status] = { ok: result.ok, reason: result.reason, said: result.message.length > 0 };
          }
          const down = github(204);
          down.down = true;
          const offline = await make(memory(TOKEN), down).send('decisions', 'i:a\\n');
          out.offline = { ok: offline.ok, reason: offline.reason };
          return out;""")
        self.assertEqual({key: value["reason"] for key, value in got.items()},
                         {"401": "rejected", "403": "forbidden", "404": "missing",
                          "422": "refused", "500": "failed", "offline": "offline"})
        for key, value in got.items():
            with self.subTest(status=key):
                self.assertFalse(value["ok"])

    def test_a_revoked_token_is_noticed_and_a_new_one_clears_it(self):
        got = evaluate("""
          const server = github(401);
          const storage = memory(TOKEN);
          const client = make(storage, server);
          await client.send('decisions', 'i:a\\n');
          const noticed = client.rejected();
          const stillStored = client.enabled();
          server.status = 200;
          const replaced = await client.remember(OTHER);
          return { noticed, stillStored, replaced, after: client.rejected() };""")
        self.assertTrue(got["noticed"])
        self.assertTrue(got["stillStored"])  # forgetting is the person's choice
        self.assertEqual(got["replaced"], {"ok": True})
        self.assertFalse(got["after"])

    def test_remembering_checks_the_token_with_a_read_and_keeps_only_a_good_one(self):
        got = evaluate("""
          const good = github(200);
          const storage = memory();
          const client = make(storage, good);
          const ok = await client.remember('  ' + TOKEN + '\\n');
          const stored = storage.getItem(Dispatch.KEY);
          const bad = github(401);
          const other = memory();
          const refused = await make(other, bad).remember(TOKEN);
          return { ok, stored, read: good.calls[0], refused, kept: other.getItem(Dispatch.KEY) };""")
        self.assertEqual(got["ok"], {"ok": True})
        self.assertEqual(got["stored"], TOKEN)
        self.assertEqual(got["read"]["method"], "GET")
        self.assertIsNone(got["read"]["body"])
        self.assertEqual(got["refused"]["reason"], "rejected")
        self.assertIsNone(got["kept"])

    def test_only_fine_grained_tokens_are_taken(self):
        got = evaluate("""
          const server = github(200);
          const client = make(memory(), server);
          const out = [];
          for (const value of ['', 'ghp_' + 'a'.repeat(36), 'github_pat_short', 'password', 'a b']) {
            out.push((await client.remember(value)).reason);
          }
          return { out, calls: server.calls.length };""")
        self.assertEqual(got["out"], ["format"] * 5)
        self.assertEqual(got["calls"], 0)

    def test_forgetting_removes_only_this_devices_copy(self):
        got = evaluate("""
          const phone = memory(TOKEN);
          const tablet = memory(OTHER);
          const a = make(phone, github(204));
          const b = make(tablet, github(204));
          a.forget();
          return { phone: a.enabled(), tablet: b.enabled(), kept: tablet.getItem(Dispatch.KEY) };""")
        self.assertFalse(got["phone"])
        self.assertTrue(got["tablet"])
        self.assertEqual(got["kept"], OTHER)

    def test_two_devices_use_their_own_tokens_at_once(self):
        got = evaluate("""
          const server = github(204);
          const phone = make(memory(TOKEN), server);
          const tablet = make(memory(OTHER), server);
          await Promise.all([phone.send('decisions', 'i:a\\n'), tablet.send('decisions', 'r:b\\n')]);
          return server.calls.map((call) => call.headers.Authorization);""")
        self.assertEqual(sorted(got), sorted([f"Bearer {TOKEN}", f"Bearer {OTHER}"]))

    def test_storage_that_refuses_is_reported_and_never_throws(self):
        got = evaluate("""
          const broken = { getItem() { throw new Error('blocked'); }, setItem() { throw new Error('blocked'); },
                           removeItem() { throw new Error('blocked'); } };
          const client = make(broken, github(200));
          return { enabled: client.enabled(), remembered: (await client.remember(TOKEN)).reason,
                   forgot: client.forget() };""")
        self.assertFalse(got["enabled"])
        self.assertEqual(got["remembered"], "storage")
        self.assertFalse(got["forgot"])

    def test_the_token_form_link_asks_for_the_actions_permission_only(self):
        got = evaluate("""
          const url = new URL(make(memory(), github(200)).templateUrl());
          return { origin: url.origin + url.pathname, params: Object.fromEntries(url.searchParams) };""")
        self.assertEqual(got["origin"], "https://github.com/settings/personal-access-tokens/new")
        self.assertEqual(got["params"]["actions"], "write")
        self.assertEqual(got["params"]["target_name"], "me")
        self.assertEqual(got["params"]["expires_in"], "365")
        permissions = set(got["params"]) - {"name", "description", "target_name", "expires_in"}
        self.assertEqual(permissions, {"actions"})


if __name__ == "__main__":
    unittest.main()
