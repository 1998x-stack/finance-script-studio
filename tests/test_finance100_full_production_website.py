"""Full review-and-production content is public, but article release is blocked."""
from __future__ import annotations
import csv,html,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from build_site import build
from series_site import read_curriculum
from production_site import episode_materials,markdown_doc

class FullProductionWebsiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lessons=[e for m in read_curriculum() for e in m["lessons"]]

    def test_all_100_have_complete_review_materials(self):
        self.assertEqual(len(self.lessons),100)
        for lesson in self.lessons:
            with self.subTest(episode=lesson["id"]):
                output=episode_materials(lesson)
                for anchor in ("full-script","storyboard","research","editor-review","production-check"):
                    self.assertIn(f'id="{anchor}"',output)
                for term in ("完整五段口播稿","完整分镜方案","编辑审稿记录","待审材料","in_review","draft"):
                    self.assertIn(term,output)
                a=json.loads((ROOT/"content"/"articles"/f'finance100-{lesson["id"].lower()}.json').read_text(encoding="utf-8"))
                for beat in a["voiceover"]:
                    self.assertIn(html.escape(beat["text"],quote=True),output)

    def test_website_dashboard_and_100_individual_pages(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/"site"
            build(out)
            self.assertIn('href="./production/"',(out/"index.html").read_text(encoding="utf-8"))
            dash=(out/"production"/"index.html").read_text(encoding="utf-8")
            self.assertEqual(dash.count('data-prod-queue="'),100)
            for term in ("审核与制作","六道人工审核门槛","100期审核与制作总表","11期优先试录材料","全系列自检报告","终审签核与制片模板"):
                self.assertIn(term,dash)
            with (out/"production"/"production-queue.csv").open(encoding="utf-8-sig",newline="") as f:
                rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),100)
            self.assertTrue(all(r["public_release"]=="BLOCKED" for r in rows))
            for lesson in self.lessons:
                ep=lesson["id"].lower()
                page=(out/"series"/"finance-100"/ep/"index.html").read_text(encoding="utf-8")
                self.assertIn("完整五段口播稿",page)
                self.assertIn("完整分镜方案",page)
                self.assertIn("待审核",page)
                self.assertIn('noindex,follow',page)
                self.assertFalse((out/"articles"/("finance100-"+ep)/"index.html").exists())
            for ep in ("EP029","EP033","EP053","EP060","EP064","EP069","EP073","EP085","EP086","EP098","EP100"):
                p=out/"production"/"pilot"/ep.lower()/"index.html"
                self.assertTrue(p.is_file())
                self.assertIn("试录导演卡",p.read_text(encoding="utf-8"))
                self.assertTrue((out/"production"/"pilot"/(ep+"-teleprompter.txt")).exists())
            sitemap=(out/"sitemap.xml").read_text(encoding="utf-8")
            self.assertIn("/production/</loc>",sitemap)
            self.assertNotIn("/production/pilot/ep029/",sitemap)
            self.assertNotIn("/articles/finance100-ep029/",sitemap)

    def test_markdown_is_html_escaped(self):
        content="# <script>alert(1)</script>\n\n- [ ] **待审核**\n\n| X | Y |\n| --- | --- |\n| A | <svg onload=alert(1)> |\n"
        result=markdown_doc(content)
        self.assertNotIn("<script>",result)
        self.assertNotIn("<svg onload=",result)
        self.assertIn("&lt;script&gt;",result)
        self.assertIn("<table",result)
        self.assertIn("待审核",result)

if __name__=="__main__":
    unittest.main()
