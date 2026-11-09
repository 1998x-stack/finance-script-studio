"""Validate the 30-episode Finance 100 first-batch draft and editorial workflow."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "content" / "series" / "finance-100"
ARTICLES = ROOT / "content" / "articles"
MANIFEST = SERIES / "manifest.json"


class Finance100Batch01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.episodes = [e for m in cls.manifest["modules"][:3] for e in m["episodes"]]
        cls.remaining = [e for m in cls.manifest["modules"][3:] for e in m["episodes"]]

    def test_first_batch_is_exactly_30_and_no_others_marked_review(self):
        self.assertEqual(len(self.manifest["modules"]), 10)
        self.assertEqual(len(self.episodes), 30)
        self.assertEqual(len(self.remaining), 70)
        self.assertEqual([e["id"] for e in self.episodes],
                         [f"EP{i:03d}" for i in range(1, 31)])
        self.assertTrue(all(e["status"] == "in_review" for e in self.episodes))
        self.assertTrue(all(e["status"] == "planned" for e in self.remaining))

    def test_every_episode_has_source_script_storyboard_review(self):
        for e in self.episodes:
            with self.subTest(episode=e["id"]):
                directory = SERIES / e["path"]
                for filename in ("brief.md", "script.md", "research.md",
                                 "storyboard.md", "review.md"):
                    path = directory / filename
                    self.assertTrue(path.is_file(), str(path))
                    body = path.read_text(encoding="utf-8")
                    self.assertIn("status: in_review", body)
                    self.assertGreater(len(body), 450)
                self.assertEqual(len(e["files"]), 5)

    def test_scripts_are_five_stages_and_provide_substantial_content(self):
        pattern = re.compile(
            r"^## (\\d{2}):(\\d{2})–(\\d{2}):(\\d{2})｜[^\\n]+\\n\\n"
            r"([\\s\\S]*?)(?=\\n## |\\n---)", re.MULTILINE
        )
        expected = [(0, 15), (15, 45), (45, 105), (105, 150), (150, 180)]
        for e in self.episodes:
            with self.subTest(episode=e["id"]):
                text = (SERIES / e["path"] / "script.md").read_text(encoding="utf-8")
                beats = pattern.findall(text)
                self.assertEqual(len(beats), 5, e["id"])
                boundaries = [(int(h1) * 60 + int(m1), int(h2) * 60 + int(m2))
                              for h1, m1, h2, m2, _ in beats]
                self.assertEqual(boundaries, expected, e["id"])
                self.assertGreaterEqual(sum(len(b[-1].strip()) for b in beats), 480)

    def test_article_drafts_schema_references_and_timeline(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from build_site import validate
        for e in self.episodes:
            with self.subTest(episode=e["id"]):
                file = ARTICLES / f"finance100-{e['id'].lower()}.json"
                self.assertTrue(file.is_file(), str(file))
                article = json.loads(file.read_text(encoding="utf-8"))
                self.assertEqual(article["category"], "concept")
                self.assertEqual(article["status"], "draft")
                self.assertEqual(article["video_seconds"], 180)
                self.assertEqual(len(article["voiceover"]), 5)
                self.assertEqual(article["voiceover"][0]["start"], 0)
                self.assertEqual(article["voiceover"][-1]["end"], 180)
                self.assertTrue(all(s["url"].startswith("https://") for s in article["sources"]))
                self.assertTrue(all(b["text"].strip() for b in article["voiceover"]))
                validate(article, file)

    def test_first_batch_never_in_published_public_pages(self):
        from tempfile import TemporaryDirectory
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from build_site import build
        with TemporaryDirectory() as tmp:
            target = Path(tmp) / "site"
            build(target)
            for e in self.episodes:
                self.assertFalse((target / "articles" /
                                  f"finance100-{e['id'].lower()}" / "index.html").exists())


if __name__ == "__main__":
    unittest.main()
