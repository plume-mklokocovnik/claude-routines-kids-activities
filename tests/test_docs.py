import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def test_local_markdown_links_resolve(self):
        paths = list(ROOT.glob("*.md"))
        for folder in ("docs", "reference", "app", "inbox", ".claude", ".agents"):
            paths.extend((ROOT / folder).rglob("*.md"))
        for path in paths:
            content = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
            for target in re.findall(r"\]\(([^\s)]+)\)", content):
                parsed = urlsplit(target)
                if parsed.scheme or not parsed.path:
                    continue
                with self.subTest(file=str(path.relative_to(ROOT)), target=target):
                    self.assertTrue((path.parent / unquote(parsed.path)).exists())

    def test_no_api_keys_are_committed(self):
        for folder in ("scripts", "reference", "docs", "app", "tests", ".agents"):
            for path in (ROOT / folder).rglob("*"):
                if path.is_file() and path.suffix in {".py", ".md", ".js", ".json", ".yml", ".html"}:
                    with self.subTest(path=str(path.relative_to(ROOT))):
                        self.assertNotRegex(path.read_text(encoding="utf-8", errors="ignore"),
                                            "AIza" + r"[0-9A-Za-z_-]{30,}")

    def test_skills_have_discoverable_frontmatter(self):
        for path in (ROOT / ".agents" / "skills").rglob("SKILL.md"):
            content = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertTrue(content.startswith("---\n"))
                header = content.split("---", 2)[1]
                self.assertIn(f"name: {path.parent.name}\n", header)
                self.assertRegex(header, r"\ndescription: .+")

    def test_claude_skills_point_at_agents_skills(self):
        for folder in ("skills", "agents"):
            link = ROOT / ".claude" / folder
            with self.subTest(folder=folder):
                self.assertTrue(link.is_symlink())
                self.assertEqual(link.resolve(), (ROOT / ".agents" / folder).resolve())

    def test_subagents_have_name_model_and_no_nested_agents(self):
        for path in (ROOT / ".agents" / "agents").glob("*.md"):
            header = path.read_text(encoding="utf-8").split("---", 2)[1]
            with self.subTest(path=path.name):
                self.assertIn(f"name: {path.stem}\n", header)
                self.assertRegex(header, r"\ndescription: .+")
                self.assertRegex(header, r"\nmodel: \w+")
                self.assertNotRegex(header, r"tools:.*\bAgent\b")


if __name__ == "__main__":
    unittest.main()