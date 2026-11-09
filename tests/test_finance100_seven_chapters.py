"""Verify seven-chapter editorial delivery and 40 new Finance100 scripts."""
from __future__ import annotations
import json,re,sys,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SERIES=ROOT/"content"/"series"/"finance-100"
ARTICLES=ROOT/"content"/"articles"
sys.path.insert(0,str(ROOT/"scripts"))
from build_site import validate,build

class Finance100SevenChapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=json.loads((SERIES/"manifest.json").read_text(encoding="utf-8"))
        cls.all_eps=[e for m in cls.manifest["modules"] for e in m["episodes"]]
        cls.seven=[e for m in cls.manifest["modules"][3:10] for e in m["episodes"]]
        cls.new=[e for m in cls.manifest["modules"][6:10] for e in m["episodes"]]

    def test_100_episodes_and_seven_chapter_delivery(self):
        self.assertEqual(len(self.manifest["modules"]),10)
        self.assertEqual([x["id"] for x in self.all_eps],[f"EP{i:03d}" for i in range(1,101)])
        self.assertEqual(len(self.seven),70)
        self.assertEqual(len(self.new),40)
        self.assertTrue(all(x["status"]=="in_review" for x in self.all_eps))
        self.assertEqual(self.manifest["batches"][-1]["modules"],[f"M{i:02d}" for i in range(4,11)])
        self.assertEqual(self.manifest["batches"][-1]["newly_authored_episodes"],40)

    def test_new_40_episode_folders_and_contents(self):
        pattern=re.compile(r"^## (\d{2}):(\d{2})–(\d{2}):(\d{2})｜[^\n]+\n\n([\s\S]*?)(?=\n## |\n\*\*)",re.M)
        expected=[(0,15),(15,45),(45,105),(105,150),(150,180)]
        for ep in self.new:
            with self.subTest(episode=ep["id"]):
                folder=SERIES/ep["path"]
                self.assertEqual(len(ep["files"]),5)
                for name in ("brief.md","script.md","research.md","storyboard.md","review.md"):
                    content=(folder/name).read_text(encoding="utf-8")
                    self.assertIn("status: in_review",content)
                script=(folder/"script.md").read_text(encoding="utf-8")
                parts=pattern.findall(script)
                self.assertEqual(len(parts),5)
                self.assertEqual([(int(a)*60+int(b),int(c)*60+int(d)) for a,b,c,d,_ in parts],expected)
                total=sum(len(p[-1].strip()) for p in parts)
                self.assertGreaterEqual(total,500,ep["id"])
                article_path=ARTICLES/f"finance100-{ep['id'].lower()}.json"
                article=json.loads(article_path.read_text(encoding="utf-8"))
                validate(article,article_path)
                self.assertEqual(article["status"],"draft")
                self.assertEqual(len(article["voiceover"]),5)
                for i,part in enumerate(parts):
                    self.assertEqual(part[-1].strip(),article["voiceover"][i]["text"])
                board=(folder/"storyboard.md").read_text(encoding="utf-8")
                compact=lambda x:re.sub(r"\s+","",x)
                for beat in article["voiceover"]:
                    self.assertIn(compact(beat["text"]),compact(board))
                self.assertTrue((folder/"research.md").read_text(encoding="utf-8").count("https://")>=1)

    def test_100_drafts_not_public(self):
        for ep in self.all_eps:
            article_path=ARTICLES/f"finance100-{ep['id'].lower()}.json"
            article=json.loads(article_path.read_text(encoding="utf-8"))
            self.assertEqual(article["status"],"draft",ep["id"])
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/"site"
            build(dest)
            self.assertFalse(any((dest/"articles"/f"finance100-{x['id'].lower()}"/"index.html").exists()
                                 for x in self.all_eps))

if __name__=="__main__":
    unittest.main()
