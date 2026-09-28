import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def test_local_markdown_links_resolve(self):
        paths = list(ROOT.glob("*.md"))
        for folder in ("docs", "reference", ".claude", ".agents"):
            paths.extend((ROOT / folder).rglob("*.md"))
        for path in paths:
            content = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)
            for target in re.findall(r"\]\(([^\s)]+)\)", content):
                parsed = urlsplit(target)
                if parsed.scheme or not parsed.path:
                    continue
                with self.subTest(file=str(path.relative_to(ROOT)), target=target):
                    self.assertTrue((path.parent / unquote(parsed.path)).exists())

    def test_skills_have_discoverable_frontmatter(self):
        for folder in (".claude", ".agents"):
            for path in (ROOT / folder).rglob("SKILL.md"):
                content = path.read_text(encoding="utf-8")
                with self.subTest(path=path):
                    self.assertTrue(content.startswith("---\n"))
                    header = content.split("---", 2)[1]
                    self.assertIn(f"name: {path.parent.name}\n", header)
                    self.assertRegex(header, r"\ndescription: .+")


if __name__ == "__main__":
    unittest.main()