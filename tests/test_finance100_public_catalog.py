"""Finance 100 is browseable without publishing unapproved research articles."""
from __future__ import annotations
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_site import build
from series_site import read_curriculum, brief_fields


class Finance100PublicCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = read_curriculum()
        cls.lessons = [e for module in cls.catalog for e in module["lessons"]]

    def test_manifest_populates_all_ten_chapters_in_order(self):
        self.assertEqual(len(self.catalog), 10)
        self.assertEqual([m["id"] for m in self.catalog],
                         [f"M{i:02d}" for i in range(1,11)])
        self.assertEqual(len(self.lessons), 100)
        self.assertEqual([e["id"] for e in self.lessons],
                         [f"EP{i:03d}" for i in range(1,101)])
        for module in self.catalog:
            self.assertEqual(len(module["lessons"]), 10)
        self.assertTrue(all(e["article_status"] == "draft" for e in self.lessons))

    def test_each_episode_comes_from_real_source_brief(self):
        for lesson in self.lessons:
            with self.subTest(ep=lesson["id"]):
                brief = (ROOT / lesson["brief_path"]).read_text(encoding="utf-8")
                self.assertEqual(brief_fields(brief), lesson["fields"])
                for field in ("传播标题","核心定义","3分钟机制主线","案例切口","误区与边界"):
                    self.assertGreater(len(lesson["fields"][field]), 5)

    def test_html_build_has_home_nav_course_index_and_100_previews(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"_site"
            build(out)
            home=(out/"index.html").read_text(encoding="utf-8")
            course=(out/"series"/"finance-100"/"index.html").read_text(encoding="utf-8")
            self.assertIn("100个财经核心概念",home)
            self.assertIn('href="series/finance-100/"',home)
            self.assertIn("十章知识地图",course)
            self.assertIn('id="episode-search"',course)
            self.assertIn("提纲预览",course)
            for module in self.catalog:
                self.assertIn(f'id="module-{module["id"]}"',course)
            for lesson in self.lessons:
                self.assertIn(f'href="{lesson["id"].lower()}/"',course)
                page=(out/"series"/"finance-100"/lesson["id"].lower()/"index.html")
                self.assertTrue(page.exists(),str(page))
                rendered=page.read_text(encoding="utf-8")
                self.assertIn(lesson["title"],rendered)
                self.assertIn(lesson["fields"]["核心定义"],rendered)
                self.assertIn(lesson["fields"]["案例切口"],rendered)
                self.assertIn(lesson["fields"]["误区与边界"],rendered)
                self.assertIn('name="robots" content="noindex,follow"',rendered)
                self.assertIn("待审核",rendered)
                self.assertIn("查看待审逐字稿（GitHub）",rendered)
                self.assertNotIn("已审核文章 →",rendered)
                self.assertFalse((out/"articles"/f"finance100-{lesson['id'].lower()}"/"index.html").exists())
            self.assertTrue((out/"assets"/"series.js").is_file())
            sitemap=(out/"sitemap.xml").read_text(encoding="utf-8")
            self.assertIn("/series/finance-100/</loc>",sitemap)
            self.assertNotIn("/series/finance-100/ep001/",sitemap)
            self.assertNotIn("/articles/finance100-ep001/",sitemap)

    def test_public_course_api_contains_no_draft_script_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"_site"
            build(out)
            data=json.loads((out/"data"/"finance100.json").read_text(encoding="utf-8"))
            self.assertEqual(len(data["modules"]),10)
            lessons=[e for m in data["modules"] for e in m["episodes"]]
            self.assertEqual(len(lessons),100)
            self.assertTrue(all(e["public_article"] is None for e in lessons))
            sample=json.loads((ROOT/"content"/"articles"/"finance100-ep085.json").read_text(encoding="utf-8"))
            serialized=json.dumps(data,ensure_ascii=False)
            self.assertNotIn(sample["voiceover"][2]["text"],serialized)
            self.assertNotIn(sample["voiceover"][3]["text"],serialized)
            self.assertNotIn("voiceover",serialized)
            self.assertNotIn("sources",serialized)
            self.assertNotIn("fact_checks",serialized)
            self.assertNotIn("sections",serialized)

    def test_build_replaces_stale_course_preview_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"_site"
            build(out)
            stale=out/"series"/"finance-100"/"ep999"
            stale.mkdir()
            (stale/"index.html").write_text("UNREVIEWED STALE",encoding="utf-8")
            build(out)
            self.assertFalse(stale.exists())
            self.assertTrue((out/"series"/"finance-100"/"ep100"/"index.html").exists())


if __name__=="__main__":
    unittest.main()
