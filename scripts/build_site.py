#!/usr/bin/env python3
"""Build a source-backed editorial GitHub Pages site using Python stdlib only."""
from __future__ import annotations
import argparse
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from xml.sax.saxutils import escape as xml_escape
from series_site import build_course, read_curriculum, home_teaser
from production_site import build_production

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "articles"
SITE = json.loads((ROOT / "site.json").read_text(encoding="utf-8"))

def h(value):
    return html.escape(str(value), quote=True)

def read_articles():
    articles = []
    slugs = set()
    for file in sorted(CONTENT.glob("*.json")):
        data = json.loads(file.read_text(encoding="utf-8"))
        validate(data, file)
        if data["slug"] in slugs:
            raise ValueError(f"Duplicate slug: {data['slug']}")
        slugs.add(data["slug"])
        articles.append(data)
    return sorted(articles, key=lambda a: a["published_at"], reverse=True)

def validate(a, file):
    required = ["schema_version","slug","title","subtitle","lead","category","status","published_at","updated_at","as_of","video_seconds","reading_minutes","keywords","summary","key_numbers","takeaways","sections","voiceover","sources","fact_checks"]
    for key in required:
        if key not in a:
            raise ValueError(f"{file}: missing {key}")
    if a["schema_version"] != "1.0":
        raise ValueError(f"{file}: unsupported schema_version")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", a["slug"]):
        raise ValueError(f"{file}: unsafe slug")
    if a["category"] not in SITE["categories"] or a["status"] not in ("published","draft"):
        raise ValueError(f"{file}: invalid category or status")
    for key in ("published_at","updated_at","as_of"):
        date.fromisoformat(a[key])
    if a["updated_at"] < a["published_at"] or not 30 <= a["video_seconds"] <= 180:
        raise ValueError(f"{file}: invalid publication or duration")
    if not isinstance(a["keywords"], list) or not a["sections"] or not a["voiceover"] or not a["sources"]:
        raise ValueError(f"{file}: empty article content")
    source_ids = set()
    for source in a["sources"]:
        if source["id"] in source_ids or not urlparse(source["url"]).scheme == "https":
            raise ValueError(f"{file}: duplicate source or non-HTTPS URL")
        source_ids.add(source["id"])
    def verify_refs(item):
        unknown = set(item.get("source_ids", [])) - source_ids
        if unknown:
            raise ValueError(f"{file}: unresolved citation: {unknown}")
    for metric in a["key_numbers"]:
        verify_refs(metric)
        if not metric["source_ids"]:
            raise ValueError(f"{file}: uncited metric")
    if a.get("comparison"):
        verify_refs(a["comparison"])
        if not a["comparison"]["source_ids"]:
            raise ValueError(f"{file}: uncited comparison")
        if not a["comparison"]["items"] or any(not isinstance(i["amount"], (int, float)) or i["amount"] < 0 for i in a["comparison"]["items"]):
            raise ValueError(f"{file}: invalid comparison amounts")
    for section in a["sections"]:
        if not section.get("heading") or not section.get("paragraphs"):
            raise ValueError(f"{file}: invalid section")
        for para in section["paragraphs"]:
            verify_refs(para)
    last_end = 0
    for beat in a["voiceover"]:
        if beat["start"] < last_end or beat["end"] <= beat["start"] or beat["end"] > a["video_seconds"]:
            raise ValueError(f"{file}: overlapping/out-of-range video beats")
        last_end = beat["end"]
    if last_end != a["video_seconds"]:
        raise ValueError(f"{file}: last beat must end at video_seconds")
    for fc in a["fact_checks"]:
        verify_refs(fc)
        if fc["status"] not in ("verified","attributed","analysis","scenario"):
            raise ValueError(f"{file}: invalid fact-check status")
    if a["status"] == "published" and not a["fact_checks"]:
        raise ValueError(f"{file}: published article needs fact checks")
    return True

def cite(refs, source_map):
    if not refs:
        return ""
    links = " ".join(f'<a href="#source-{h(r)}" aria-label="查看来源 {h(r)}">[{h(r)}]</a>' for r in refs)
    return f'<span class="source-cites">{links}</span>'

def shell(title, description, canonical, body, root_prefix="./", article=False):
    base = SITE["base_url"].rstrip("/") + "/"
    data = json.dumps({"@context":"https://schema.org","@type":"WebSite","name":SITE["name"],"url":base},ensure_ascii=False).replace("<","\\u003c")
    schema = f'<script type="application/ld+json">{data}</script>'
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"><title>{h(title)} · {h(SITE["name"])}</title>
<meta name="description" content="{h(description)}"><meta property="og:type" content="{'article' if article else 'website'}">
<meta property="og:title" content="{h(title)}"><meta property="og:description" content="{h(description)}">
<meta property="og:url" content="{h(canonical)}"><link rel="canonical" href="{h(canonical)}">
<link rel="stylesheet" href="{root_prefix}assets/site.css">{schema}</head>
<body><a class="skip" href="#main">跳到正文</a>
<header class="site-header"><div class="container header-inner">
<a class="brand" href="{root_prefix}" aria-label="财经观察首页"><span class="brand-icon">F<span>·</span></span><span>财经<span class="brand-light">理性观察</span><small>FINANCE SCRIPT STUDIO</small></span></a>
<nav class="nav"><a href="{root_prefix}#topics">研究栏目</a><a href="{root_prefix}series/finance-100/">百期课程</a><a href="{root_prefix}production/">审核与制作</a><a href="{root_prefix}#latest">最新研究</a><a href="https://github.com/1998x-stack/finance-script-studio" target="_blank" rel="noopener noreferrer">GitHub ↗</a></nav>
</div></header><main id="main">{body}</main>
<footer class="footer"><div class="container footer-grid"><div><strong>财经理性观察</strong><p>事实有出处，观点有边界。</p></div><div>基于公开信息的研究与财经科普，不构成任何投资建议。<br>文稿中的时间、数字和判断以各篇标注的研究截止日为准。</div></div></footer>
<script defer src="{root_prefix}assets/site.js"></script><script defer src="{root_prefix}assets/series.js"></script><script defer src="{root_prefix}assets/production.js"></script></body></html>'''

def metric_card(m, compact=False):
    return (f'<div class="metric"><div class="metric-label">{h(m["label"])}</div>'
            f'<div class="metric-value">{h(m["value"])}<em>{h(m["unit"])}</em></div>'
            f'<p class="metric-detail">{h(m["period"])} · {h(m["detail"])}</p></div>')

def article_card(a):
    cat = SITE["categories"][a["category"]]
    return f'''<a class="article-card" data-category="{h(a["category"])}" href="articles/{h(a["slug"])}/">
<div class="card-meta"><span>{h(cat["short"])}</span><span>{h(a["published_at"])}</span></div>
<h3>{h(a["title"])}</h3><p>{h(a["subtitle"])}</p>
<div class="card-bottom"><span>{h(a["reading_minutes"])} 分钟阅读 · {h(a["video_seconds"])} 秒口播</span><b>阅读全文 →</b></div></a>'''

def index_page(articles):
    cats = SITE["categories"]
    nav = "".join(f'<div class="topic"><span class="topic-no">{h(v["number"])}</span><h3>{h(v["label"])}</h3><p>{h(v["description"])}</p></div>' for v in cats.values())
    filters = '<button class="filter active" data-filter="all" type="button" aria-pressed="true">全部研究</button>' + "".join(f'<button class="filter" data-filter="{h(k)}" type="button" aria-pressed="false">{h(v["short"])}</button>' for k,v in cats.items())
    cards = "".join(article_card(a) for a in articles)
    lead = articles[0] if articles else None
    feature = (f'''<section class="feature"><div class="container feature-inner"><div><div class="eyebrow">FOCUS / 深度研究 · {h(lead["as_of"])}</div><h2>{h(lead["title"])}</h2><p>{h(lead["lead"])}</p><a class="feature-link" href="articles/{h(lead["slug"])}/">阅读完整专题 <span>↗</span></a></div><div class="feature-metrics">{''.join(metric_card(m) for m in lead["key_numbers"][:3])}</div></div></section>''' if lead else "")
    body = f'''<section class="home-hero"><div class="container"><div class="eyebrow">INDEPENDENT FINANCIAL EXPLAINERS / ISSUE 001</div>
<h1>从一个财经事件，<br><span>看清一条商业规律。</span></h1>
<p class="home-intro">信息可以很快，理解值得更深。用可追溯的数据、克制的判断和清晰的故事，拆解市场现象背后的因果。</p>
<div class="hero-rule"><span>FACTS</span><span>MECHANISMS</span><span>PERSPECTIVE</span></div>
</div></section>{feature}{home_teaser(h, read_curriculum())}
<section id="topics" class="section container"><div class="section-head"><div><span class="small-kicker">OUR COVERAGE</span><h2>四条研究主线</h2></div><p>不追逐所有信息，只分析值得被理解的问题。</p></div><div class="topic-grid">{nav}</div></section>
<section id="latest" class="section container"><div class="section-head"><div><span class="small-kicker">THE ARCHIVE</span><h2>最新研究</h2></div><p>每篇文章都有对应的来源、分析正文和可直接拍摄的口播。</p></div><div class="filters" role="group" aria-label="按栏目筛选">{filters}</div><div class="articles-grid">{cards or '<p>暂无已发布稿件。</p>'}</div><p id="empty-filter" class="empty-filter" hidden>该栏目尚无已发布稿件。</p></section>'''
    return shell("首页", SITE["description"], SITE["base_url"], body)

def article_page(a):
    smap = {s["id"]:s for s in a["sources"]}
    cat = SITE["categories"][a["category"]]
    numbers = "".join(metric_card(m) for m in a["key_numbers"])
    takeaways = "".join(f'<li>{h(t)}</li>' for t in a["takeaways"])
    sections = []
    for idx,s in enumerate(a["sections"],1):
        paras = "".join(f'<p>{h(p["text"])}{cite(p.get("source_ids",[]),smap)}</p>' for p in s["paragraphs"])
        bullets = '<ul class="body-bullets">' + ''.join(f'<li>{h(x)}</li>' for x in s.get("bullets", [])) + '</ul>' if s.get("bullets") else ""
        sections.append(f'<section class="story-section" id="section-{idx}"><div class="section-index">{idx:02d} / ANALYSIS</div><h2>{h(s["heading"])}</h2>{paras}{bullets}</section>')
    script = "".join(f'''<div class="beat"><div class="beat-time">{b["start"]//60:02d}:{b["start"]%60:02d}—{b["end"]//60:02d}:{b["end"]%60:02d}<span>{h(b["stage"])}</span></div>
<div><p class="beat-text">{h(b["text"])}</p><p class="beat-shot">画面建议 / {h(b["shot"])}</p></div></div>''' for b in a["voiceover"])
    sources = "".join(f'<li id="source-{h(s["id"])}"><span class="source-key">{h(s["id"])}</span><div><a href="{h(s["url"])}" target="_blank" rel="noopener noreferrer">{h(s["title"])} ↗</a><small>{h(s["publisher"])} · {h(s["published_at"])} · {h(s["type"])}</small></div></li>' for s in a["sources"])
    source_notes = "".join(f'<li><span class="status">{h(c["status"])}</span><span>{h(c["claim"])}</span>{cite(c.get("source_ids",[]),smap)}</li>' for c in a["fact_checks"])
    chart = ""
    if a.get("comparison"):
        cmp=a["comparison"]
        peak=max(i["amount"] for i in cmp["items"]) or 1  # all-zero comparisons must still render
        bars="".join(f'<div class="compare-line"><div class="compare-top"><span>{h(i["label"])}</span><strong>{h(i["display"])}</strong></div><div class="track"><div class="bar" style="width:{100*i["amount"]/peak:.2f}%"></div></div></div>' for i in cmp["items"])
        chart=f'<div class="compare"><div class="compare-kicker">DATA / 同期口径对比</div><h3>{h(cmp["title"])}</h3>{bars}<p>{h(cmp["note"])}{cite(cmp.get("source_ids",[]),smap)}</p></div>'
    body=f'''<div class="article-hero"><div class="container article-hero-inner">
<a class="back" href="../../">← 返回全部研究</a><div class="eyebrow">{h(cat["label"])} / RESEARCH NOTE</div>
<h1>{h(a["title"])}</h1><p class="article-subtitle">{h(a["subtitle"])}</p>
<div class="article-meta"><span>研究截止 {h(a["as_of"])}</span><span>发布 {h(a["published_at"])}</span><span>阅读 {h(a["reading_minutes"])} 分钟</span><span>口播 {h(a["video_seconds"])} 秒</span></div>
</div></div><div class="container"><div class="numbers">{numbers}</div>
<div class="article-layout"><article class="article-main">
<div class="lead-block"><span class="small-kicker">THE QUESTION</span><p>{h(a["lead"])}</p></div>
<div class="takeaways"><div class="small-kicker">KEY TAKEAWAYS / 核心结论</div><ol>{takeaways}</ol></div>
{chart}{''.join(sections)}
<section class="script-section" id="script"><div class="section-index">VIDEO / {h(a["video_seconds"])} SEC</div><h2>三分钟口播脚本</h2><p class="quiet">可直接朗读；时间为分镜目标区间。视频上线前，请再次核对数据的最新状态。</p>{script}</section>
<section class="sources-section" id="sources"><div class="section-index">EVIDENCE</div><h2>资料来源与核查记录</h2><p class="quiet">按原始文件优先，兼用有出处的媒体报道；不同统计日期的数据明确分开。研究截止：{h(a["as_of"])}。</p><ol class="sources">{sources}</ol><h3>关键表述检查</h3><ul class="checks">{source_notes}</ul></section>
</article><aside class="article-aside"><div class="sticky-aside"><div class="aside-label">本期观点</div><p>{h(a["summary"])}</p><div class="aside-links"><a href="#script">观看口播脚本 ↓</a><a href="#sources">核查资料来源 ↓</a></div><div class="aside-date">AS OF {h(a["as_of"])}</div></div></aside></div></div>'''
    canonical=SITE["base_url"].rstrip("/")+"/articles/"+a["slug"]+"/"
    return shell(a["title"],a["subtitle"],canonical,body,"../../",True)

def build(out_dir):
    arts=read_articles()
    published=[a for a in arts if a["status"]=="published"]
    out_dir.mkdir(parents=True,exist_ok=True)
    # Prevent previously published pages from surviving when an article becomes a draft.
    previous_articles = out_dir / "articles"
    if previous_articles.exists():
        shutil.rmtree(previous_articles)
    shutil.copytree(ROOT/"web"/"assets",out_dir/"assets",dirs_exist_ok=True)
    (out_dir/"index.html").write_text(index_page(published),encoding="utf-8")
    course=build_course(out_dir, shell, h, SITE)
    production=build_production(out_dir, shell, SITE, course["catalog"])
    urls=[SITE["base_url"], *course["urls"], SITE["base_url"].rstrip("/") + "/production/"]
    summary=[]
    for a in published:
        target=out_dir/"articles"/a["slug"]
        target.mkdir(parents=True,exist_ok=True)
        (target/"index.html").write_text(article_page(a),encoding="utf-8")
        urls.append(SITE["base_url"].rstrip("/")+"/articles/"+a["slug"]+"/")
        summary.append({k:a[k] for k in ["slug","title","subtitle","category","published_at","updated_at","as_of","video_seconds","reading_minutes"]})
    api=out_dir/"data"
    api.mkdir(exist_ok=True)
    (api/"articles.json").write_text(json.dumps({"schema_version":"1.0","articles":summary},ensure_ascii=False,indent=2),encoding="utf-8")
    sitemap=''.join(f'<url><loc>{xml_escape(url)}</loc></url>' for url in urls)
    (out_dir/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+sitemap+'</urlset>',encoding="utf-8")
    (out_dir/"robots.txt").write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE["base_url"]}sitemap.xml\n',encoding="utf-8")
    (out_dir/".nojekyll").touch()
    print(f"Built {len(published)} published article page(s), {course['episodes']} fully browseable editorial pages and {production['pilot_count']} rehearsal cards from {len(arts)} content record(s) at {out_dir}")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check",action="store_true",help="Validate source records only")
    ap.add_argument("--out-dir",default="_site",type=Path)
    args=ap.parse_args()
    arts=read_articles()
    modules=read_curriculum()
    print(f"Validated {len(arts)} article records and {sum(len(m['lessons']) for m in modules)} course previews")
    if not args.check:
        build(args.out_dir)

if __name__=="__main__":
    main()
