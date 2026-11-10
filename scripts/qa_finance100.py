#!/usr/bin/env python3
"""Structural editorial self-review for the Finance 100 video production pipeline.

No publication decisions are made by this program. A green CI run is not
approval of claims, source URLs, recorded duration, or platform compliance.
"""
from __future__ import annotations
import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "content" / "series" / "finance-100"
ARTICLES = ROOT / "content" / "articles"
BEAT = re.compile(
    r"^## (\d{2}):(\d{2})–(\d{2}):(\d{2})｜[^\n]+\n\n"
    r"([\s\S]*?)(?=\n## |\n---|\n\*\*|\Z)", re.M
)
PLANNED = [(0, 15), (15, 45), (45, 105), (105, 150), (150, 180)]
PILOTS = {
    "EP029": "债务流动性核心案例", "EP033": "中国LPR制度与浮动贷款",
    "EP053": "利润与现金三表联动", "EP060": "杜邦公式复核",
    "EP064": "固定利率债券估值", "EP073": "DCF的现金流与终值",
    "EP085": "2026预售新规与过渡条款", "EP086": "城投债务法律主体",
    "EP069": "2025商业不动产REITs试点", "EP098": "家庭应急储备",
    "EP100": "长期购买力与复利假设",
}
RISK = {"EP021", "EP024", "EP029", "EP033", "EP036", "EP038",
        "EP053", "EP055", "EP058", "EP059", "EP064", "EP068",
        "EP069", "EP073", "EP085", "EP086", "EP087", "EP091", "EP100"}

def compact(t: str) -> str:
    return re.sub(r"\s+", "", t)

def suggested_times(lengths: list[int]) -> list[int]:
    total = sum(lengths)
    if not total:
        return [15, 30, 60, 45, 30]
    # Pure text proportion: a cue for trial recording, NOT a verified duration.
    estimate = [round(180 * x / total) for x in lengths]
    estimate[-1] += 180 - sum(estimate)
    return estimate

def evaluate(root: Path = ROOT) -> dict:
    series = root / "content" / "series" / "finance-100"
    articles = root / "content" / "articles"
    manifest = json.loads((series / "manifest.json").read_text(encoding="utf-8"))
    eps = [e for m in manifest["modules"] for e in m["episodes"]]
    all_results = []
    for idx, ep in enumerate(eps, 1):
        eid = ep["id"]
        errors, warnings = [], []
        if eid != f"EP{idx:03d}":
            errors.append("episode_sequence_mismatch")
        folder = series / ep["path"]
        parts = {}
        for name in ("brief.md", "script.md", "research.md", "storyboard.md", "review.md"):
            p = folder / name
            if not p.is_file():
                errors.append("missing_" + name)
                continue
            parts[name] = p.read_text(encoding="utf-8")
            if "status: in_review" not in parts[name]:
                errors.append("frontmatter_status_mismatch_" + name)
        apath = articles / f"finance100-{eid.lower()}.json"
        if not apath.exists():
            errors.append("missing_article_json")
            a = None
        else:
            try:
                a = json.loads(apath.read_text(encoding="utf-8"))
            except (ValueError, UnicodeDecodeError):
                a = None
                errors.append("invalid_article_json")
        times, lengths = [], []
        if "script.md" in parts:
            beats = list(BEAT.finditer(parts["script.md"]))
            if len(beats) != 5:
                errors.append("not_five_script_beats")
            for match in beats:
                start = int(match[1])*60 + int(match[2])
                end = int(match[3])*60 + int(match[4])
                times.append((start, end))
                lengths.append(len(compact(match[5].strip())))
            if times != PLANNED:
                errors.append("script_time_axis_mismatch")
        if a is not None:
            if a.get("status") != "draft":
                errors.append("draft_publication_breach")
            if a.get("category") != "concept" or a.get("video_seconds") != 180:
                errors.append("article_type_or_duration_mismatch")
            if a.get("slug") != f"finance100-{eid.lower()}":
                errors.append("article_slug_mismatch")
            voice = a.get("voiceover", [])
            if len(voice) != 5:
                errors.append("voiceover_count_mismatch")
            elif times and [(v["start"],v["end"]) for v in voice] != times:
                errors.append("voiceover_time_axis_mismatch")
            if "script.md" in parts and len(times) == 5 and len(voice) == 5:
                for j, match in enumerate(BEAT.finditer(parts["script.md"])):
                    if compact(match[5]) != compact(voice[j].get("text", "")):
                        errors.append(f"voiceover_script_mismatch_stage_{j+1}")
                    if "storyboard.md" in parts and compact(voice[j].get("text", "")) not in compact(parts["storyboard.md"]):
                        errors.append(f"storyboard_mismatch_stage_{j+1}")
            sources = a.get("sources", [])
            ids = {s.get("id") for s in sources}
            if not sources or "ED" not in ids:
                warnings.append("sources_need_editorial_review")
            for src in sources:
                url = src.get("url", "")
                if not url.startswith("https://"):
                    errors.append("non_https_source")
                elif src.get("id") != "ED" and "research.md" in parts and url not in parts["research.md"]:
                    errors.append("source_not_in_research_" + str(src.get("id")))
                if src.get("id") != "ED":
                    desc = src.get("type", "")
                    if src.get("published_at") == a.get("as_of") and not any(x in desc for x in ("查阅", "快照", "原始发表日期", "原始发布日")):
                        warnings.append("source_publication_date_provenance")
            for section in a.get("sections", []):
                for paragraph in section.get("paragraphs", []):
                    for sid in paragraph.get("source_ids", []):
                        if sid not in ids:
                            errors.append("unresolved_section_source_id")
            for element in a.get("key_numbers", []) + a.get("fact_checks", []):
                for sid in element.get("source_ids", []):
                    if sid not in ids:
                        errors.append("unresolved_metric_source_id")
        if ep.get("status") != "in_review":
            errors.append("unexpected_editorial_status")
        if "review.md" in parts and "- [ ]" not in parts["review.md"]:
            warnings.append("review_checklist_no_pending_items")
        max_rate = 0
        rates = []
        if len(times) == len(lengths) == 5:
            rates = [round(length*60/(end-start), 1) if end>start else 0
                     for length, (start,end) in zip(lengths,times)]
            max_rate = max(rates)
            if max_rate > 250:
                warnings.append("pacing_over_250_characters_per_minute")
            if min(rates) < 95:
                warnings.append("pacing_under_95_characters_per_minute")
            if sum(lengths) < 500:
                warnings.append("short_total_script")
        # Source verification is ALWAYS a human gate; link strings are not URL checks.
        warnings.append("source_claims_not_independently_verified")
        warnings.append("real_voice_recording_missing")
        warnings.append("human_legal_and_release_signoff_missing")
        result = {
            "episode": eid, "title": ep["title"],
            "module": ep["path"].split("/")[0], "status": ep.get("status"),
            "structural_ok": not errors, "publication_gate": "blocked",
            "production_gate": "requires_editorial_and_recording",
            "total_characters": sum(lengths),
            "stage_characters": lengths, "stage_cpm": rates,
            "proposed_trial_seconds": suggested_times(lengths),
            "errors": sorted(set(errors)),
            "warnings": sorted(set(warnings)),
            "priority": PILOTS.get(eid),
            "high_stakes": eid in RISK
        }
        all_results.append(result)
    count = Counter(w for item in all_results for w in item["warnings"])
    err = Counter(w for item in all_results for w in item["errors"])
    return {
        "schema_version": "1.0", "review_date": "2026-11-10",
        "method": "Static deterministic review. No audio, original link HTTP check, or human approval.",
        "summary": {
            "episodes": len(all_results),
            "structurally_ok": sum(x["structural_ok"] for x in all_results),
            "with_errors": sum(bool(x["errors"]) for x in all_results),
            "pacing_warnings": sum("pacing_over_250_characters_per_minute" in x["warnings"] for x in all_results),
            "human_signoff_complete": 0, "published_authorized": 0,
            "warning_codes": dict(sorted(count.items())),
            "error_codes": dict(sorted(err.items()))
        },
        "episodes": all_results
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail only on structural integrity errors")
    parser.add_argument("--strict-release", action="store_true", help="Always fail until independent human signoff is handled outside this program")
    parser.add_argument("--report", type=Path, help="Write JSON diagnostics")
    args = parser.parse_args()
    report = evaluate()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    summary = report["summary"]
    print(f"Finance100 production preflight: {summary['structurally_ok']}/{summary['episodes']} structurally valid; {summary['pacing_warnings']} pacing warnings; 0 human approvals")
    for code,n in summary["error_codes"].items():
        print(f"ERROR {code}: {n}")
    for code,n in summary["warning_codes"].items():
        print(f"WARNING {code}: {n}")
    if args.strict_release:
        print("RELEASE BLOCKED: independently verified sources, actual audio, and human approval required.")
        return 2
    if args.check and (summary["with_errors"] or summary["episodes"] != 100):
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
