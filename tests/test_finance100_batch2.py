"""Regression tests: Finance 100 batch 2 contains 30 complete in-review drafts."""
from __future__ import annotations
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SERIES=ROOT/"content"/"series"/"finance-100"
ARTICLES=ROOT/"content"/"articles"
sys.path.insert(0,str(ROOT/"scripts"))
from build_site import build,validate

class Finance100Batch02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((SERIES/"manifest.json").read_text(encoding="utf-8"))
        cls.episodes=[e for m in cls.manifest["modules"][3:6] for e in m["episodes"]]
        cls.other=[e for m in cls.manifest["modules"][6:] for e in m["episodes"]]

    def test_range_statuses_and_file_names(self):
        self.assertEqual([e["id"] for e in self.episodes],
                         [f"EP{i:03d}" for i in range(31,61)])
        self.assertEqual(len(self.other),40)
        self.assertTrue(all(e["status"]=="in_review" for e in self.episodes))
        self.assertTrue(all(e["status"] in {"planned","drafting","in_review","approved"} for e in self.other))
        self.assertTrue(all("review.md" in e["files"] and len(e["files"])==5 for e in self.episodes))

    def test_every_episode_delivers_full_editorial_package(self):
        for ep in self.episodes:
            with self.subTest(episode=ep["id"]):
                d=SERIES/ep["path"]
                for fn in ("brief.md","script.md","research.md","storyboard.md","review.md"):
                    content=(d/fn).read_text(encoding="utf-8")
                    self.assertIn("status: in_review",content)
                    self.assertGreater(len(content),400)
                research=(d/"research.md").read_text(encoding="utf-8")
                self.assertIn("https://",research)
                self.assertIn("scenario",research)

    def test_five_beats_cover_180_seconds_and_nontrivial_script(self):
        rx=re.compile(r"^## (\d{2}):(\d{2})–(\d{2}):(\d{2})｜[^\n]+\n\n([\s\S]*?)(?=\n## |\n---)",re.M)
        expected=[(0,15),(15,45),(45,105),(105,150),(150,180)]
        for ep in self.episodes:
            with self.subTest(episode=ep["id"]):
                s=(SERIES/ep["path"]/"script.md").read_text(encoding="utf-8")
                beats=rx.findall(s)
                self.assertEqual(len(beats),5)
                self.assertEqual([(int(a)*60+int(b),int(c)*60+int(d)) for a,b,c,d,_ in beats],expected)
                self.assertGreaterEqual(sum(len(t.strip()) for *_,t in beats),480)

    def test_schema_and_sources_and_not_published(self):
        for ep in self.episodes:
            with self.subTest(episode=ep["id"]):
                p=ARTICLES/f"finance100-{ep['id'].lower()}.json"
                a=json.loads(p.read_text(encoding="utf-8"))
                validate(a,p)
                self.assertEqual(a["status"],"draft")
                self.assertEqual(a["category"],"concept")
                self.assertEqual(len(a["voiceover"]),5)
                self.assertTrue(all(src["url"].startswith("https://") for src in a["sources"]))
                self.assertTrue(all(beat["text"] for beat in a["voiceover"]))

    def test_site_does_not_publish_drafts(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"site"
            build(out)
            for ep in self.episodes:
                self.assertFalse((out/"articles"/f"finance100-{ep['id'].lower()}"/"index.html").exists())

if __name__=="__main__":
    unittest.main()
