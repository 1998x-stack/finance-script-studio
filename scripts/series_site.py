"""Generate a public Finance 100 curriculum catalog without publishing draft articles.

The catalog publishes only topic metadata from manifest.json and the five
editorial planning fields in each brief.md. It never copies script.md,
storyboard.md, research.md, private review notes, or draft article bodies.
Draft episodes remain outside /articles, display "待审核", and carry noindex
on their course preview pages. Approved published articles retain their own
regular URL and release workflow.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote

from qa_finance100 import evaluate
from production_site import episode_materials

ROOT = Path(__file__).resolve().parents[1]
SERIES = ROOT / "content" / "series" / "finance-100"
ARTICLE_DIR = ROOT / "content" / "articles"
GITHUB_BLOB = "https://github.com/1998x-stack/finance-script-studio/blob/main/"
FIELDS = ("传播标题", "核心定义", "3分钟机制主线", "案例切口", "误区与边界")


def brief_fields(text: str) -> dict[str, str]:
    fields = {}
    for key in FIELDS:
        match = re.search(r"^\s*-\s*\*\*" + re.escape(key) +
                          r"：\*\*\s*([^\n]+)", text, re.MULTILINE)
        if not match:
            raise ValueError(f"Missing syllabus field: {key}")
        fields[key] = match.group(1).strip()
    return fields


def read_curriculum(root: Path = ROOT) -> list[dict]:
    series = root / "content" / "series" / "finance-100"
    article_dir = root / "content" / "articles"
    manifest = json.loads((series / "manifest.json").read_text(encoding="utf-8"))
    modules = manifest.get("modules", [])
    if len(modules) != 10 or sum(len(m.get("episodes", [])) for m in modules) != 100:
        raise ValueError("Finance 100 must have 10 modules and 100 episodes")
    seen = set()
    catalog = []
    for m_index, module in enumerate(modules, 1):
        if module["id"] != f"M{m_index:02d}" or len(module["episodes"]) != 10:
            raise ValueError(f"Unexpected course module: {module['id']}")
        lessons = []
        for e_index, episode in enumerate(module["episodes"], 1):
            id_number = (m_index - 1) * 10 + e_index
            eid = f"EP{id_number:03d}"
            if episode["id"] != eid or eid in seen:
                raise ValueError(f"Unexpected or duplicate episode: {episode['id']}")
            seen.add(eid)
            if episode["status"] not in ("planned", "drafting", "in_review", "approved"):
                raise ValueError(f"Unknown review status: {eid}")
            brief_path = series / episode["path"] / "brief.md"
            fields = brief_fields(brief_path.read_text(encoding="utf-8"))
            article_path = article_dir / f"finance100-{eid.lower()}.json"
            article = json.loads(article_path.read_text(encoding="utf-8"))
            if article["slug"] != f"finance100-{eid.lower()}":
                raise ValueError(f"Article slug mismatch: {eid}")
            if article["status"] not in ("draft", "published"):
                raise ValueError(f"Invalid release status: {eid}")
            if article["status"] == "published" and episode["status"] != "approved":
                raise ValueError(f"Public article lacks approved manifest status: {eid}")
            lesson = {
                "id": eid,
                "title": episode["title"],
                "number": id_number,
                "module_id": module["id"],
                "module_title": module["title"],
                "status": episode["status"],
                "article_status": article["status"],
                "article_slug": article["slug"],
                "brief_path": f"content/series/finance-100/{episode['path']}/brief.md",
                "script_path": f"content/series/finance-100/{episode['path']}/script.md",
                "research_path": f"content/series/finance-100/{episode['path']}/research.md",
                "fields": fields,
            }
            lessons.append(lesson)
        catalog.append({
            "id": module["id"],
            "title": module["title"],
            "description": module["description"],
            "lessons": lessons,
        })
    return catalog


def src_url(path: str) -> str:
    return GITHUB_BLOB + quote(path, safe="/")


def home_teaser(h, catalog: list[dict]) -> str:
    cards = "".join(
        f'<a href="series/finance-100/#module-{h(m["id"])}" class="series-home-chapter">'
        f'<span>{h(m["id"])}</span><strong>{h(m["title"])}</strong><span aria-hidden="true">↗</span></a>'
        for m in catalog
    )
    return f'''<section class="series-home" id="finance100">
<div class="container">
<div class="series-home-heading"><div>
<span class="small-kicker">STRUCTURED LEARNING / 100 EPISODES</span>
<h2>100个财经核心概念<span class="series-home-dot">.</span></h2>
<p>从经济学底层逻辑到个人财务规划，10个章节、100个独立选题，按知识脉络逐期理解真实世界的经济运行。</p>
<div class="series-note">100期完整创作稿和审核制作材料现已可读 · 均未通过终审</div>
</div><a class="course-main-link" href="series/finance-100/">浏览全部100集 <span aria-hidden="true">↗</span></a></div>
<div class="series-home-chapters">{cards}</div>
</div></section>'''


def course_index(h, shell, base_url: str, catalog: list[dict]) -> str:
    hero = '''<section class="course-hero"><div class="container">
<a href="../../" class="course-back">← 返回首页</a>
<div class="small-kicker">FINANCE 100 / A KNOWLEDGE SERIES</div>
<h1>100个财经核心概念<span>.</span></h1>
<p>用三分钟理解一个经济问题。从基本原理、宏观指标，到企业报表、估值、风险与日常财务。按照十章课程地图，自由选择你感兴趣的一集。</p>
<div class="course-hero-stats"><span><b>10</b>章节</span><span><b>100</b>课程选题</span><span><b>180s</b>每期目标时长</span></div>
<p class="course-disclaimer"><strong>内容状态说明：</strong>课程目录和每集完整口播、研究、分镜与审核工作稿现已全部展示。内容仍未完成真人终审与录制，不进入正式研究文章列表。</p>
</div></section>'''
    links = "".join(
        f'<a href="#module-{h(m["id"])}" class="course-chapter-shortcut"><span>{h(m["id"])}</span>'
        f'<strong>{h(m["title"])}</strong><small>10个选题 ↗</small></a>'
        for m in catalog
    )
    chapter_cards = f'<nav class="course-shortcuts" aria-label="课程章节快捷入口">{links}</nav>'
    sections = []
    for module in catalog:
        entries = []
        for lesson in module["lessons"]:
            search_terms = " ".join([
                lesson["id"], lesson["title"],
                lesson["fields"]["传播标题"],
                lesson["fields"]["核心定义"], module["title"],
            ])
            entries.append(
                f'<a class="course-episode" data-course-module="{h(module["id"])}" '
                f'data-course-search="{h(search_terms)}" '
                f'href="{h(lesson["id"].lower())}/">'
                f'<span class="episode-no">{h(lesson["id"])}</span>'
                f'<span class="episode-main"><strong>{h(lesson["title"])}</strong>'
                f'<small>{h(lesson["fields"]["传播标题"])}</small></span>'
                f'<span class="episode-state">{"已发布" if lesson["article_status"]=="published" else "完整工作稿"}</span>'
                f'<span class="episode-arrow" aria-hidden="true">↗</span></a>'
            )
        sections.append(
            f'<section class="course-module" id="module-{h(module["id"])}" data-course-section="{h(module["id"])}">'
            f'<div class="course-module-top"><span class="course-module-code">{h(module["id"])}</span>'
            f'<div><h2>{h(module["title"])}</h2><p>{h(module["description"])}</p></div>'
            f'<a href="#course-search" class="module-top-link">返回筛选 ↑</a></div>'
            f'<div class="course-episodes">{"".join(entries)}</div></section>'
        )
    body = (hero +
        '<div class="container course-content"><div class="course-intro-heading"><span class="small-kicker">THE CURRICULUM</span>'
        '<h2>十章知识地图</h2><p>建议从M01顺序学习，也可以先从你最关心的话题进入。</p><a class="course-review-cta" href="../../production/">查看100期审核与制作总览 →</a></div>' +
        chapter_cards +
        '<div class="course-search-bar" id="course-search"><label for="episode-search">快速查找课程</label>'
        '<input id="episode-search" type="search" autocomplete="off" placeholder="搜索EP编号、概念或问题，例如现金流、EP053" '
        'aria-controls="course-list" /><button id="course-clear" type="button">清空</button>'
        '<span id="course-match-count" role="status" aria-live="polite">显示100/100集</span></div>' +
        '<nav class="course-filter-bar" aria-label="按章节筛选">'
        '<button class="course-filter current" data-course-filter="all" aria-pressed="true" type="button">全部章节</button>' +
        "".join(f'<button class="course-filter" data-course-filter="{h(m["id"])}" aria-pressed="false" '
                f'type="button">{h(m["id"])}</button>' for m in catalog) + '</nav>' +
        '<div id="course-list">' + "".join(sections) + '</div>'
        '<p id="course-no-results" class="course-no-results" hidden>没有匹配的选题，试试更短的关键词。</p>'
        '<div class="course-final-note"><strong>制作不是发布。</strong>每集可在线阅读完整待审稿、研究资料、分镜和制作记录；仍需独立来源核查、试录与合规审核。'
        '如需查看逐字稿原始编辑版本，可通过单集页面前往GitHub，来源、算例和时间轴均应视为待审。</div></div>')
    url = base_url.rstrip("/") + "/series/finance-100/"
    return shell("100个财经核心概念 · 十章课程地图",
                 "10章100期财经核心概念课程目录，浏览每期学习问题、知识提纲及制作状态。",
                 url, body, "../../")


def lesson_page(h, shell, base_url: str, lesson: dict, previous: dict | None, next_one: dict | None, audit: dict | None = None) -> str:
    fields = lesson["fields"]
    eid = lesson["id"]
    slug = eid.lower()
    module_id = lesson["module_id"]
    is_published = lesson["article_status"] == "published"
    canonical = base_url.rstrip("/") + f"/series/finance-100/{slug}/"
    def source_link(label, path):
        return (f'<a href="{h(src_url(path))}" target="_blank" rel="noopener noreferrer">'
                f'{h(label)} <span aria-hidden="true">↗</span></a>')
    route_steps = [seg.strip() for seg in fields["3分钟机制主线"].split("→") if seg.strip()]
    steps = "".join(f'<li>{h(part)}</li>' for part in route_steps)
    if not steps:
        steps = f'<li>{h(fields["3分钟机制主线"])}</li>'
    if is_published:
        status = '已发布正式文章'
        publication = (f'<a class="lesson-primary-link" href="../../../articles/{h(lesson["article_slug"])}/">'
                       '阅读已审核文章 →</a>')
    else:
        status = '待审核 · 全部创作与制作材料可查'
        publication = ('<p class="lesson-status-text">本集的完整口播稿尚未完成独立事实终审和真人试录，'
                       '本页已展示完整口播、分镜、研究与审稿资料，但仍不构成正式发表文章。</p>')
    previous_link = (
        f'<a href="../{h(previous["id"].lower())}/" class="lesson-neighbor">← 上一集'
        f'<strong>{h(previous["id"])} · {h(previous["title"])}</strong></a>'
        if previous else '<span class="lesson-neighbor lesson-neighbor-empty">这是第一集</span>'
    )
    next_link = (
        f'<a href="../{h(next_one["id"].lower())}/" class="lesson-neighbor lesson-neighbor-next">下一集 →'
        f'<strong>{h(next_one["id"])} · {h(next_one["title"])}</strong></a>'
        if next_one else '<span class="lesson-neighbor lesson-neighbor-empty">已到最后一集</span>'
    )
    body = f'''<section class="lesson-hero"><div class="container">
<div class="lesson-breadcrumb"><a href="../../../">首页</a><span>/</span>
<a href="../">财经100概念</a><span>/</span>
<a href="../#module-{h(module_id)}">{h(module_id)} {h(lesson["module_title"])}</a></div>
<div class="lesson-heading"><div class="lesson-id">{h(eid)} <span> / {h(module_id)} </span></div>
<h1>{h(lesson["title"])}</h1><p>{h(fields["传播标题"])}</p>
<div class="lesson-meta"><span>{h(lesson["module_title"])}</span><span>目标3分钟</span>
<span>{status}</span></div></div>
</div></section>
<div class="container lesson-body"><div class="lesson-grid"><article class="lesson-main">
<div class="lesson-section-label">THE CONCEPT / 核心概念</div>
<h2>这一集要讲清什么？</h2><p class="lesson-definition">{h(fields["核心定义"])}</p>
<div class="lesson-section-label">THE MECHANISM / 思考路径</div>
<h2>从问题走到解释</h2><ol class="lesson-steps">{steps}</ol>
<div class="lesson-note-block"><div><span>EXAMPLE / 案例切口</span>
<h3>用一个生活场景理解</h3><p>{h(fields["案例切口"])}</p></div>
<div><span>BOUNDARY / 常见误区</span><h3>还需要注意什么？</h3>
<p>{h(fields["误区与边界"])}</p></div></div>
<section class="lesson-release"><div class="lesson-section-label">PRODUCTION STATUS / 编辑进度</div>
<h2>审核与制作材料公开查阅</h2>
{publication}
<div class="lesson-source-actions">{source_link("查看原始选题简报",lesson["brief_path"])}
{source_link("查看待审逐字稿（GitHub）",lesson["script_path"])}
{source_link("查看来源与核查记录",lesson["research_path"])}</div>
<p class="lesson-caution">这些创作文件可供追溯，但尚不能作为已审核新闻、投资建议或已录制视频引用；数字情景需标注假设。</p>
</section>{episode_materials(lesson, audit)}</article>
<aside class="lesson-aside"><div class="lesson-side-panel"><div class="small-kicker">LEARNING GUIDE</div>
<strong>{h(module_id)} · {h(lesson["module_title"])}</strong>
<p>本集是10章100集学习路径中的第{lesson["number"]}集。</p>
<div class="lesson-progress"><div style="width:{lesson["number"]}%"></div></div>
<small>{lesson["number"]} / 100 · 课程目录已开放</small>
<a href="../#module-{h(module_id)}">返回本章全部选题 ↗</a>
</div></aside></div><nav class="lesson-pager" aria-label="相邻课程">{previous_link}{next_link}</nav></div>'''
    result = shell(f"{eid} {lesson['title']}", fields["传播标题"],
                   canonical, body, "../../../")
    if not is_published:
        result = result.replace("</head>",
                                '<meta name="robots" content="noindex,follow"></head>', 1)
    return result


def build_course(out_dir: Path, shell, h, site: dict) -> dict:
    catalog = read_curriculum()
    dest = out_dir / "series" / "finance-100"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    base_url = site["base_url"]
    (dest / "index.html").write_text(
        course_index(h, shell, base_url, catalog), encoding="utf-8")
    flat = [lesson for m in catalog for lesson in m["lessons"]]
    audits = {item["episode"]: item for item in evaluate()["episodes"]}
    links = [base_url.rstrip("/") + "/series/finance-100/"]
    for idx, lesson in enumerate(flat):
        folder = dest / lesson["id"].lower()
        folder.mkdir(exist_ok=True)
        (folder / "index.html").write_text(
            lesson_page(h, shell, base_url, lesson,
                        flat[idx-1] if idx else None,
                        flat[idx+1] if idx < len(flat)-1 else None,
                        audits.get(lesson["id"])),
            encoding="utf-8")
        if lesson["article_status"] == "published":
            links.append(base_url.rstrip("/") +
                         f"/series/finance-100/{lesson['id'].lower()}/")
    safe_index = {
        "schema_version": "1.0",
        "title": "财经100个核心概念",
        "description": "课程目录与网站可阅读的待审工作稿；草稿不是已审核文章",
        "modules": [
            {
                "id": m["id"],
                "title": m["title"],
                "description": m["description"],
                "episodes": [
                    {
                        "id": e["id"],
                        "title": e["title"],
                        "number": e["number"],
                        "question": e["fields"]["传播标题"],
                        "definition": e["fields"]["核心定义"],
                        "review_status": e["status"],
                        "public_article": (f"articles/{e['article_slug']}/"
                                           if e["article_status"] == "published" else None),
                        "preview_url": f"series/finance-100/{e['id'].lower()}/",
                    } for e in m["lessons"]
                ],
            } for m in catalog
        ],
    }
    api = out_dir / "data"
    api.mkdir(exist_ok=True)
    (api / "finance100.json").write_text(
        json.dumps(safe_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"modules": len(catalog), "episodes": len(flat),
            "urls": links, "catalog": catalog}
