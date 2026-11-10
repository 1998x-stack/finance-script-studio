"""Ensure produced handoff files are usable and never mark an episode approved."""
from __future__ import annotations
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from prepare_finance100_production import produce, PILOTS

class ProductionHandoffTests(unittest.TestCase):
    def test_queue_and_pilot_cards_are_generated(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/"production"
            info=produce(ROOT,out)
            self.assertEqual(info,{"queue":100,"pilots":len(PILOTS),"published_authorized":0,"structurally_ok":100})
            with (out/"production-queue.csv").open(encoding="utf-8-sig",newline="") as fh:
                rows=list(csv.DictReader(fh))
            self.assertEqual(len(rows),100)
            self.assertEqual({r["episode"] for r in rows},{f"EP{i:03d}" for i in range(1,101)})
            self.assertTrue(all(r["public_release"]=="BLOCKED" for r in rows))
            self.assertTrue(all(r["editor_release_approval"]=="PENDING" for r in rows))
            self.assertEqual(sum(r["queue"]=="P0_pilot" for r in rows),len(PILOTS))
            self.assertTrue(all(sum(map(int,r["suggested_trial_seconds"].split("/")))==180 for r in rows))
            for ep in PILOTS:
                card=(out/"pilot"/f"{ep}-director-card.md").read_text(encoding="utf-8")
                spoken=(out/"pilot"/f"{ep}-teleprompter.txt").read_text(encoding="utf-8")
                self.assertIn("发布",card)
                self.assertIn("BLOCKED",card)
                self.assertIn("总编最终授权",card)
                self.assertIn(ep,spoken)
            report=json.loads((out/"preflight.json").read_text(encoding="utf-8"))
            self.assertEqual(report["summary"]["published_authorized"],0)

if __name__=="__main__":
    unittest.main()
