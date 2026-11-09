"""Smoke tests for source validation and generated editorial pages."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_site import SITE, article_page, build, read_articles, validate

class EditorialBuildTests(unittest.TestCase):
    def test_articles_valid(self):
        articles=read_articles()
        self.assertGreaterEqual(len(articles),1)
        self.assertIn("event",{a["category"] for a in articles})
    def test_all_sections_have_provenance(self):
        for a in read_articles():
            self.assertTrue(a["sources"])
            self.assertTrue(a["fact_checks"])
            self.assertTrue(all(m["source_ids"] for m in a["key_numbers"]))
    def test_build_creates_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"site"
            build(out)
            self.assertTrue((out/"index.html").is_file())
            self.assertTrue((out/"data/articles.json").is_file())
            self.assertTrue((out/"sitemap.xml").is_file())
            for a in read_articles():
                target=out/"articles"/a["slug"]/"index.html"
                if a["status"]=="published":
                    self.assertTrue(target.is_file())
                    self.assertIn(a["title"],target.read_text(encoding="utf-8"))
                else:
                    self.assertFalse(target.exists())
    def test_invalid_source_reference_fails(self):
        a=json.loads(json.dumps(read_articles()[0]))
        a["key_numbers"][0]["source_ids"]=["invented"]
        with self.assertRaises(ValueError):
            validate(a,"synthetic.json")
    def test_rebuild_removes_unpublished_article_pages(self):
        # A withdrawn publication must not survive the next static build.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "site"
            build(out)
            old_page = out / "articles" / "retired-story" / "index.html"
            old_page.parent.mkdir(parents=True)
            old_page.write_text("previously published", encoding="utf-8")
            build(out)
            self.assertFalse(old_page.exists())

    def test_comparison_requires_known_sources(self):
        a = json.loads(json.dumps(read_articles()[0]))
        a["comparison"] = {
            "title": "Cash comparison",
            "items": [{"label": "A", "amount": 0, "display": "0"},
                      {"label": "B", "amount": 0, "display": "0"}],
            "note": "illustrative",
            "source_ids": ["missing"],
        }
        with self.assertRaises(ValueError):
            validate(a, "synthetic.json")

    def test_zero_value_comparison_renders(self):
        a = json.loads(json.dumps(read_articles()[0]))
        a["comparison"] = {
            "title": "Zero-value comparison",
            "items": [{"label": "A", "amount": 0, "display": "0"},
                      {"label": "B", "amount": 0, "display": "0"}],
            "note": "illustrative",
            "source_ids": [a["sources"][0]["id"]],
        }
        validate(a, "synthetic.json")
        self.assertIn("width:0.00%", article_page(a))

    def test_no_blank_published_beat(self):
        self.assertTrue(all(b["text"].strip() for a in read_articles() for b in a["voiceover"]))
if __name__=="__main__":
    unittest.main()
