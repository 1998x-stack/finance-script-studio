"""Render the public Finance 100 editorial and production workspace.

Public review material is not a verified or published article. Never update the
draft/approval status here, and never claim an actual recording exists.
"""
from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

from qa_finance100 import evaluate
from prepare_finance100_production import PILOTS, PILOT_FOCUS, produce

ROOT = Path(__file__).resolve().parents[1]

def esc(value):
    return html.escape(str(value), quote=True)

def markdown_inline(value: str) -> str:
    """Small, HTML-escaped Markdown subset for human review documents."""
    regex = re.compile(r"(\*\*[^*]+\*\*|\[[^\]]+\]\(https://[^) ]+\)|\x60[^\x60]+\x60)")
    result = []
    for fragment in regex.split(value):
        if fragment.startswith("**") and fragment.endswith("**"):
            result.append("<strong>" + esc(fragment[2:-2]) + "</strong>")
        elif fragment.startswith(chr(96)) and fragment.endswith(chr(96)):
            result.append("<code>" + esc(fragment[1:-1]) + "</code>")
        elif fragment.startswith("[") and "](https://" in fragment:
            label, destination = fragment[1:].split("](", 1)
            destination = destination[:-1]
            parsed = urlparse(destination)
            if parsed.scheme == "https" and parsed.netloc:
                result.append(f'<a href="{esc(destination)}" target="_blank" rel="noopener noreferrer">{esc(label)} ↗</a>')
            else:
                result.append(esc(label))
        else:
            result.append(esc(fragment))
    return "".join(result)

def markdown_doc(source: str) -> str:
    """Safe headings, tables, lists and text used in the repository's MD files."""
    lines = source.replace("\r\n", "\n").splitlines()
    if lines and lines[0].strip() == "---":
        try:
            lines = lines[lines.index("---", 1) + 1:]
        except ValueError:
            pass
    result, paragraph, list_tag = [], [], None
    def flush():
        if paragraph:
            result.append("<p>" + "<br>".join(markdown_inline(x) for x in paragraph) + "</p>")
            paragraph.clear()
    def end_list():
        nonlocal list_tag
        if list_tag:
            result.append(f"</{list_tag}>")
            list_tag = None
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            flush()
            end_list()
            i += 1
            continue
        if line.startswith(chr(96) * 3):
            flush()
            end_list()
            raw = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(chr(96) * 3):
                raw.append(lines[i])
                i += 1
            result.append('<pre class="md-code"><code>' + esc("\n".join(raw)) + "</code></pre>")
            i += 1
            continue
        if line.startswith("|") and i+1 < len(lines) and re.match(r"^\|?\s*:?-{3,}",lines[i+1].strip()):
            flush()
            end_list()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?",c) for c in cells):
                    rows.append(cells)
                i += 1
            result.append('<div class="md-table-wrap"><table class="md-table">')
            for k, row in enumerate(rows):
                tag = "th" if k == 0 else "td"
                result.append("<tr>" + "".join(f"<{tag}>{markdown_inline(x)}</{tag}>" for x in row) + "</tr>")
            result.append("</table></div>")
            continue
        heading = re.match(r"^(#{1,5})\s+(.+)$",line)
        if heading:
            flush()
            end_list()
            level = min(len(heading[1])+1, 5)
            result.append(f"<h{level}>{markdown_inline(heading[2])}</h{level}>")
            i += 1
            continue
        if line.startswith(">"):
            flush()
            end_list()
            result.append("<blockquote>" + markdown_inline(line.lstrip("> ")) + "</blockquote>")
            i += 1
            continue
        if line == "---":
            flush()
            end_list()
            result.append("<hr>")
            i += 1
            continue
        li = re.match(r"^(?:[-*]\s+|\d+\.\s+)(.*)$",line)
        if li:
            flush()
            target = "ol" if re.match(r"^\d+\.\s",line) else "ul"
            if list_tag != target:
                end_list()
                result.append(f"<{target}>")
                list_tag = target
            payload = li[1]
            checkbox = re.match(r"^\[([ xX])\]\s*(.*)$",payload)
            if checkbox:
                checked = checkbox[1].lower() == "x"
                result.append('<li class="md-check"><span aria-label="' +
                              ("已勾选" if checked else "待完成") + '">' +
                              ("☑" if checked else "☐") + "</span> " +
                              markdown_inline(checkbox[2]) + "</li>")
            else:
                result.append("<li>" + markdown_inline(payload) + "</li>")
            i += 1
            continue
        end_list()
        paragraph.append(line)
        i += 1
    flush()
    end_list()
    return '<div class="md-content">' + "\n".join(result) + "</div>"

def episode_materials(lesson: dict, qa: dict | None = None, root: Path = ROOT) -> str:
    """Display complete five-beat script plus all four source editorial docs."""
    path = (root / lesson["brief_path"]).parent
    article = json.loads((root / "content" / "articles" /
                          f'finance100-{lesson["id"].lower()}.json').read_text(encoding="utf-8"))
    if article["status"] != lesson["article_status"]:
        raise ValueError("Article status changed during rendering")
    raw = {name: (path / (name+".md")).read_text(encoding="utf-8")
           for name in ("script","research","storyboard","review")}
    beats = []
    for i, beat in enumerate(article["voiceover"], 1):
        stamp = lambda n: f"{n//60:02d}:{n%60:02d}"
        beats.append(
            f'<div class="prod-beat"><div class="prod-beat-clock"><small>{i:02d} · {esc(beat["stage"])}</small>'
            f'<strong>{stamp(beat["start"])}–{stamp(beat["end"])}</strong></div>'
            f'<div class="prod-beat-text"><p>{esc(beat["text"])}</p>'
            f'<small>画面：{esc(beat["shot"])}</small></div></div>')
    sources = "".join(
        f'<li><span>{esc(s["id"])}</span><div>'
        f'<a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(s["title"])} ↗</a>'
        f'<small>{esc(s["publisher"])} · {esc(s["type"])}</small></div></li>'
        for s in article["sources"])
    claims = "".join(
        f'<li><small>{esc(c["status"])}</small>{esc(c["claim"])}</li>'
        for c in article["fact_checks"])
    QA = ""
    if qa is not None:
        warning = any(x.startswith("pacing_") for x in qa["warnings"])
        qa_rates = " / ".join(str(x) for x in qa["stage_cpm"])
        proposed = " / ".join(str(x) for x in qa["proposed_trial_seconds"])
        QA = (
            '<div class="prod-qa-box"><h3>自动审查（非人工终审）</h3>'
            f'<p>结构校验：{"通过" if qa["structural_ok"] else "有错误"}；'
            f'原稿字符数：{qa["total_characters"]}；'
            f'原五幕字符/分钟：{esc(qa_rates)}。</p>'
            f'<p>按文本比例建议的试录秒数：{esc(proposed)}；'
            f'{"存在节奏预警，需重新试读" if warning else "未触发速度阈值，仍需试录"}。</p>'
            '<p>事实核查、口播计时、画面版权、财经合规、总编批准：全部待人工签核。</p></div>'
        )
    return f'''
<nav class="prod-inpage-nav" aria-label="本期完整审核与制作内容">
<a href="#full-script">完整口播稿</a><a href="#storyboard">视频分镜</a>
<a href="#research">研究与来源</a><a href="#editor-review">编辑审稿</a>
<a href="#production-check">试录与放行</a></nav>
<div class="prod-draft-note"><strong>本页展示全部待审材料，不等于已批准发表。</strong>
以下文字、图表方案与来源记录仍需真人事实核查、录音、版权和平台合规审核。</div>
<section class="prod-material" id="full-script">
<div class="lesson-section-label">SCRIPT / 全文口播 · 待试录</div><h2>完整五段口播稿</h2>
<p class="quiet">时间区间是策划目标，尚未通过真人录音计时。</p>
{''.join(beats)}
<details class="prod-raw"><summary>查看脚本源文件、编导备注</summary>{markdown_doc(raw["script"])}</details>
</section>
<section class="prod-material" id="storyboard">
<div class="lesson-section-label">STORYBOARD / 画面</div><h2>完整分镜方案</h2>
{markdown_doc(raw["storyboard"])}</section>
<section class="prod-material" id="research">
<div class="lesson-section-label">EVIDENCE / 来源</div><h2>研究资料与核查记录</h2>
<p class="quiet">资料链接已登记，并不表示全部断言经过人工逐句核实。</p>
<ol class="prod-source-list">{sources}</ol>
{markdown_doc(raw["research"])}
<h3>结构化事实分类</h3><ul class="prod-facts">{claims}</ul></section>
<section class="prod-material" id="editor-review">
<div class="lesson-section-label">EDITOR / 审核</div><h2>编辑审稿记录</h2>
{markdown_doc(raw["review"])}</section>
<section class="prod-material" id="production-check">
<div class="lesson-section-label">PRODUCTION / 进度</div><h2>制作与放行状态</h2>
{QA}
<p>本期稿件状态：<strong>{esc(lesson["status"])}</strong>；
文章发布状态：<strong>{esc(lesson["article_status"])}</strong>。网站允许展示未终审工作稿，但不会自动将文章改为已发布。</p>
<a class="lesson-primary-link" href="../../../production/#review-queue">进入100期审核与制作中心 →</a>
</section>
'''

def dashboard(shell, site: dict, audit: dict) -> str:
    summary = audit["summary"]
    cases = audit["episodes"]
    pilot_ids = set(PILOTS)
    fast = summary["pacing_warnings"]
    slow = sum("pacing_under_95_characters_per_minute" in e["warnings"] for e in cases)
    stats = [
        (summary["episodes"],"期已有创作初稿"),
        (summary["structurally_ok"],"期通过结构检查"),
        (fast,"期快语速预警"),
        (summary["human_signoff_complete"],"期完成真人终审"),
    ]
    stat_html = "".join(f'<div><strong>{n}</strong><span>{esc(label)}</span></div>' for n,label in stats)
    gates = [
        ("01","事实核查","对照原始公告、数字、政策日期和主体"),
        ("02","计算复核","复算公式、口径、币种、单位及假设"),
        ("03","真人试录","保存音频与实际分幕秒数"),
        ("04","素材与版权","图表字幕、镜头及资料授权"),
        ("05","金融合规","按实际平台规则审核风险描述"),
        ("06","总编授权","签核版本、人员和发布决议"),
    ]
    gate_html = "".join(f'<div class="prod-gate"><span>{esc(n)}</span><h3>{esc(t)}</h3>'
                        f'<p>{esc(desc)}</p><small>未签核</small></div>' for n,t,desc in gates)
    queue = []
    for e in cases:
        id = e["episode"]
        priority = "P0" if id in pilot_ids else ("P1" if e["high_stakes"] else "P2")
        warn = "语速需调整" if any(x.startswith("pacing_") for x in e["warnings"]) else "待真人试录"
        queue.append(
            f'<a class="prod-qrow" href="../series/finance-100/{id.lower()}/#production-check" '
            f'data-prod-queue="{priority}" data-prod-search="{esc(id+" "+e["title"]+" "+e["module"])}">'
            f'<span class="prod-qid">{id}</span><span class="prod-qtitle"><strong>{esc(e["title"])}</strong>'
            f'<small>{esc(e["module"])}</small></span><span class="prod-qpriority">'
            f'{priority} · {"优先" if priority=="P0" else "关键" if priority=="P1" else "常规"}</span>'
            f'<span class="prod-qchars">{e["total_characters"]}字 · 最高{max(e["stage_cpm"]):g}/分</span>'
            f'<span class="prod-qwarn">{warn}</span><span aria-hidden="true">↗</span></a>'
        )
    pilot = "".join(f'<a class="prod-pilot-link" href="pilot/{id.lower()}/">'
                    f'<span>{id}</span><strong>{esc(PILOT_FOCUS[id])}</strong>'
                    f'<small>查看导演卡 ↗</small></a>' for id in PILOTS)
    report = (ROOT/"docs"/"finance-100-production-self-review-2026-11-10.md").read_text(encoding="utf-8")
    templates = [
        ("原始事实与计算核对","production/fact-check-template.md"),
        ("真人试录记录","production/recording-log-template.md"),
        ("正式发布判定","production/release-decision-template.md"),
    ]
    forms = "".join(f'<details class="prod-template"><summary>{esc(label)}</summary>'
                    f'{markdown_doc((ROOT/p).read_text(encoding="utf-8"))}</details>'
                    for label,p in templates)
    body = f'''<section class="prod-dashboard-hero"><div class="container">
<a class="course-back" href="../">← 返回首页</a>
<div class="small-kicker">EDITORIAL &amp; PRODUCTION / FINANCE100</div>
<h1>审核与制作<span>.</span></h1>
<p>100期内容与进度全部可查。结构性校验、真人录制、事实终审与批准发布是四件不同的事。</p>
<div class="prod-hero-stats">{stat_html}</div>
<div class="prod-hero-caution"><strong>重要声明：</strong>所有100期仍在审核中。
页面公开不代表真实音频已完成，也不代表通过财经内容终审。</div>
</div></section>
<div class="container prod-dashboard-content">
<section class="prod-dashboard-section"><div class="small-kicker">RELEASE GATES</div>
<h2>六道人工审核门槛</h2><div class="prod-gates">{gate_html}</div></section>
<section class="prod-dashboard-section" id="review-queue"><div class="small-kicker">ALL EPISODES</div>
<h2>100期审核与制作总表</h2>
<p>每分钟字符数按既定分幕目标计算，仅作为排查提醒。当前{fast}期存在快语速预警，{slow}期存在慢语速提示。</p>
<div class="prod-filters"><label for="prod-search">查找EP或关键词</label>
<input id="prod-search" type="search" autocomplete="off" placeholder="EP029、现金流、债务..."/>
<div class="prod-filter-buttons">
<button type="button" data-prod-filter="all" aria-pressed="true" class="current">全部</button>
<button type="button" data-prod-filter="P0" aria-pressed="false">P0 优先</button>
<button type="button" data-prod-filter="P1" aria-pressed="false">P1 重点</button>
<button type="button" data-prod-filter="P2" aria-pressed="false">P2 常规</button>
</div><span id="prod-count" role="status" aria-live="polite">显示100/100期</span></div>
<div class="prod-queue-list">{''.join(queue)}</div>
<p id="prod-no-results" hidden>没有匹配的期数。</p>
<div class="prod-downloads"><a href="production-queue.csv" download>下载制作队列CSV ↗</a>
<a href="preflight.json" download>下载100期审查数据JSON ↗</a></div></section>
<section class="prod-dashboard-section" id="pilot-kit"><div class="small-kicker">REHEARSAL</div>
<h2>11期优先试录材料</h2>
<p>这些导演卡包含五幕提词和建议时长，仍需要真人实际试录。</p>
<div class="prod-pilot-grid">{pilot}</div></section>
<section class="prod-dashboard-section" id="audit-report"><div class="small-kicker">AUDIT REPORT</div>
<h2>全系列自检报告</h2>{markdown_doc(report)}</section>
<section class="prod-dashboard-section" id="release-templates"><div class="small-kicker">TEMPLATES</div>
<h2>终审签核与制片模板</h2>
<p>下列模板完整展示；没有人工签名就不能将其填写为审核通过。</p>{forms}</section>
</div>'''
    url = site["base_url"].rstrip("/") + "/production/"
    return shell("审核与制作 · 财经100期", "完整公开100期制作进度、试录计划、审核报告和签核模板",
                 url, body, "../")

def build_production(out_dir: Path, shell, site: dict, catalog: list[dict]) -> dict:
    target = out_dir/"production"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True,exist_ok=True)
    result = produce(ROOT,target)
    audit = evaluate(ROOT)
    (target/"index.html").write_text(dashboard(shell, site, audit),encoding="utf-8")
    for id in PILOTS:
        raw = (target/"pilot"/f"{id}-director-card.md").read_text(encoding="utf-8")
        folder = target/"pilot"/id.lower()
        folder.mkdir(parents=True,exist_ok=True)
        contents = (
            f'<section class="prod-dashboard-hero"><div class="container">'
            f'<a href="../../" class="course-back">← 返回审核与制作</a>'
            f'<h1>{id} · 试录导演卡</h1>'
            f'<p>尚无真实录音或签核，本页仅供出片前排练与编辑参考。</p></div></section>'
            f'<div class="container prod-pilot-paper">{markdown_doc(raw)}'
            f'<div class="prod-downloads"><a href="../{id}-director-card.md">导演卡原文件 ↗</a>'
            f'<a href="../{id}-teleprompter.txt">纯提词稿 ↗</a>'
            f'<a href="../../../series/finance-100/{id.lower()}/#full-script">查看本集全部资料 ↗</a></div></div>'
        )
        html_page = shell(f"{id}试录导演卡","未审核未试录的制片交接",
                          site["base_url"].rstrip("/") + f"/production/pilot/{id.lower()}/",
                          contents,"../../../")
        html_page = html_page.replace("</head>",'<meta name="robots" content="noindex,follow"></head>',1)
        (folder/"index.html").write_text(html_page,encoding="utf-8")
    return {"episode_count":len(audit["episodes"]),
            "pilot_count":len(PILOTS),"human_signoff_complete":0}
