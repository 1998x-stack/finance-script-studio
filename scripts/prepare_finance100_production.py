#!/usr/bin/env python3
"""Make editable production handoff material, never grant editorial approval.

Reads the existing Finance100 JSON/manifest, and uses qa_finance100.evaluate
for deterministic checks. Generated files are rehearsal plans and checklists,
not recordings, legal signoffs, published articles, or verified facts.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from qa_finance100 import ROOT, evaluate

PILOTS = [
    "EP029", "EP033", "EP053", "EP060", "EP064", "EP069",
    "EP073", "EP085", "EP086", "EP098", "EP100",
]
# These are editorial questions, not a claim of full fact verification.
PILOT_FOCUS = {
    "EP029": "公司流动性与偿付能力区分；Basel LCR只属于银行监管框架；核算现金/到期债时间口径",
    "EP033": "2026-10-20官方LPR报价与合同重定价分开；历史报价不得称为当前永远有效利率",
    "EP053": "经营/投资/筹资现金流及收入确认时点；经营400－600＝－200万元的教学算例",
    "EP060": "ROE=净利率×资产周转率×权益乘数；平均资产/权益与归母口径检查",
    "EP064": "105/1.05=100 与105/1.10≈95.45；一年单一现金流不等于真实付息债",
    "EP069": "中国证监会商业不动产REITs试点日期2025-12-31；基金份额≠直接拥有楼宇；特殊期限",
    "EP073": "100/1.1+100/1.1²≈173.55；DCF现金流与折现率对象匹配；终值风险",
    "EP085": "国家2026-08-28预售规定与北京地方在途项目过渡细则分开；监管账户不可混作集团现金",
    "EP086": "法定政府债、隐性债、企业平台债的主体与法律责任分开；别推定无条件兜底",
    "EP098": "6个月仅是家庭应急金假设；保险以合同免赔额、等待期、除外责任为准",
    "EP100": "100万元/1.02^30≈55.21万元的实际购买力；通胀是假设而非预测",
}

STAGES = ("反差钩子", "定义与背景", "机制/案例", "反例和限制", "迁移结论")

def to_times(seconds: list[int]) -> list[tuple[int,int]]:
    starts, cursor = [], 0
    for val in seconds:
        starts.append((cursor, cursor+val))
        cursor += val
    if cursor != 180:
        raise ValueError(f"Expected 180 proposed seconds, got {cursor}")
    return starts

def stamp(secs: int) -> str:
    return f"{secs//60:02d}:{secs%60:02d}"

def produce(root: Path = ROOT, out_dir: Path | None = None) -> dict:
    if out_dir is None:
        out_dir = root / "_production"
    report = evaluate(root)
    if report["summary"]["episodes"] != 100 or report["summary"]["with_errors"]:
        raise ValueError("Production source has structural errors; fix before generating handoff.")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir/"pilot").mkdir(parents=True, exist_ok=True)
    manifest_root = root/"content"/"articles"
    priority = set(PILOTS)
    entries = sorted(report["episodes"],key=lambda x:(0 if x["episode"] in priority else 1,
                      0 if x["high_stakes"] else 1,-max(x["stage_cpm"]),x["episode"]))
    rows = []
    for item in entries:
        episode = item["episode"]
        rows.append({
            "episode":episode,
            "module":item["module"],
            "title":item["title"],
            "queue": "P0_pilot" if episode in priority else ("P1_high_stakes" if item["high_stakes"] else "P2_standard"),
            "current_status":item["status"],
            "script_chars":item["total_characters"],
            "maximum_stage_char_per_min":max(item["stage_cpm"]),
            "fastest_stage":item["stage_cpm"].index(max(item["stage_cpm"]))+1,
            "pacing_warning":"yes" if any(x.startswith("pacing_") for x in item["warnings"]) else "no",
            "suggested_trial_seconds":"/".join(map(str,item["proposed_trial_seconds"])),
            "sources_checked":"NOT_YET_INDEPENDENTLY_VERIFIED",
            "arithmetic_checked":"PENDING",
            "actual_voice_recording":"PENDING",
            "storyboard_footage_rights":"PENDING",
            "financial_compliance":"PENDING",
            "editor_release_approval":"PENDING",
            "public_release":"BLOCKED",
        })
    with (out_dir/"production-queue.csv").open("w",encoding="utf-8-sig",newline="") as fh:
        writer = csv.DictWriter(fh,fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    for eid in PILOTS:
        item = next(x for x in report["episodes"] if x["episode"]==eid)
        a = json.loads((manifest_root/f"finance100-{eid.lower()}.json").read_text(encoding="utf-8"))
        timings = to_times(item["proposed_trial_seconds"])
        source_lines = "\n".join(f"- [{s['id']}] {s['title']}: {s['url']}"+
                                 (" （课程编辑的假设来源）" if s["id"]=="ED" else " （待独立逐句对照）")
                                 for s in a["sources"])
        stage_lines = []
        teleprompter = []
        for k,(beat,(start,end)) in enumerate(zip(a["voiceover"],timings),1):
            cpm=item["stage_cpm"][k-1]
            stage_lines.append(
                f"### {k}. {STAGES[k-1]}｜试录建议 {stamp(start)}–{stamp(end)}（{end-start}秒；原稿预设"
                f"{beat['start']}–{beat['end']}秒；原预设负担约{cpm}字符/分钟）\n\n"
                f"**口播原文**：{beat['text']}\n\n"
                f"**画面初步提示**：{beat['shot']}\n\n"
                "**录后填写**：实际入点____秒，实际出点____秒，是否自然____，画面需要补充的来源____。\n")
            teleprompter.append(beat["text"].strip())
        director = (
            f"# {eid}｜{a['title']} — 试录导演卡（自动生成，未审批）\n\n"
            "> 本卡是文本比例计算出的**试录起点**，不是已经录成180秒。不要为了数字卡点删掉重要的限定条件。\n\n"
            f"- 版本：研究/稿件截至 {a['as_of']}；此导演卡由2026-11-10静态自检生成。\n"
            "- 机位：9:16真人主持，数据与机制示意由原创卡片承担。\n"
            "- 发布：**BLOCKED**。所有来源、真实时长、版权与合规审批均待人工签核。\n"
            f"- **本期首要核查点**：{PILOT_FOCUS[eid]}。\n"
            f"- 原五段字数：{', '.join(map(str,item['stage_characters']))}；总计 {item['total_characters']} 字符。\n"
            f"- 原五段每分钟字符：{', '.join(map(str,item['stage_cpm']))}（机械计算，非实测语速）。\n"
            f"- 建议试录分配：{', '.join(map(str,item['proposed_trial_seconds']))} 秒（总计180秒）。\n\n"
            "## 五段逐字稿与机位交接\n\n"
            +"\n".join(stage_lines)
            +"\n## 资料卡（每项真实论断需另核到具体段落）\n\n"+source_lines+
            "\n\n## 录制验收和终审签字（全部未完成）\n\n"
            "- [ ] 事实审核编辑：姓名____ 日期____ 逐条原始来源核对____\n"
            "- [ ] 公式/例子复核编辑：姓名____ 日期____ 计算与边界说明____\n"
            "- [ ] 主播：真实录音文件或受控链接____ 版本哈希____ 时长____秒\n"
            "- [ ] 导演：阶段实录秒数____/____/____/____/____，错词及超时处理____\n"
            "- [ ] 视觉编辑：素材来源/授权____ 字幕与数据单位____\n"
            "- [ ] 平台/金融合规：负责人____ 日期____ 审核意见____\n"
            "- [ ] 总编最终授权：负责人____ 日期____ 发布版本SHA____\n"
            "- [ ] 仅经上述全部批准，方可另发PR变更manifest与JSON；本卡不自动授权。\n"
        )
        (out_dir/"pilot"/f"{eid}-director-card.md").write_text(director,encoding="utf-8")
        (out_dir/"pilot"/f"{eid}-teleprompter.txt").write_text(
            f"{eid}｜{a['title']}\n\n"+"\n\n".join(teleprompter)+"\n",encoding="utf-8")
    overview = [
        "# 财经100｜制作队列与试录交接（自动生成）",
        "",
        "> 此包供编辑排期和试录使用。**没有任何稿件获得真人终审或公开发布授权。**",
        "",
        f"- 结构校验：{report['summary']['structurally_ok']}/{report['summary']['episodes']}。",
        f"- 单段超过250字符/分钟提示的期数：{report['summary']['pacing_warnings']}。",
        f"- 本轮试录先导期数：{len(PILOTS)}；输出每期导演卡和纯口播提词器。",
        "- `production-queue.csv`：100期优先级与全部制作阻断状态。请勿将PENDING自动改为通过。",
        "- 导演卡中试录建议秒数按文本比例分配；正式脚本时间轴仍是原稿占位，需记录实录。",
        "- 资料链接未经该程序发起HTTP验证；不应声称机器核验意味着事实正确。",
        "",
        "## P0优先试录",
        "",
    ]
    overview += [f"- {eid}：{PILOT_FOCUS[eid]}" for eid in PILOTS]
    overview += [
        "", "## 执行流程",
        "", "1. 先查证据资料、政策效力与算例，必要时修订script/storyboard/article并重新运行测试。",
        "2. 根据导演卡进行真人试录，记录每幕实际秒数；再调整稿件时间轴而非机械挤压语速。",
        "3. 逐项完成字幕、素材授权、图形数字、风险提示与平台资质审核。",
        "4. 将已完成的证据、算术、音频与审批写入可追溯审稿PR；授权后才可能发布。",
        "",
    ]
    (out_dir/"README.md").write_text("\n".join(overview),encoding="utf-8")
    (out_dir/"preflight.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"queue":len(rows),"pilots":len(PILOTS),
            "published_authorized":0,"structurally_ok":report["summary"]["structurally_ok"]}

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--out-dir",type=Path,default=ROOT/"_production")
    args=parser.parse_args()
    data=produce(ROOT,args.out_dir)
    print("Finance100 production handoff generated:",data)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
