# 100期财经口播：制作、试录与终审交接

> 本参考属于 finance-script-studio Skill。**“文稿齐全/校验通过”≠“来源事实已逐句核实”≠“180秒真人录制通过”≠“获准公开发布”。** 除非人工留有签署记录，不得自行提升审核状态。

## 输入与工作空间

- 用 `content/series/finance-100/manifest.json` 决定EP期号、模块和进度，以 `script.md`/ `storyboard.md`/ `research.md`/ `review.md` 为源，`content/articles/finance100-epXXX.json` 为网站结构化稿。
- 按 `python scripts/qa_finance100.py --check --report _qa/finance100-review.json` 校验目录、五段时间轴、JSON与分镜口播一致、引用ID是否存在、`draft`状态。
- 按 `python scripts/prepare_finance100_production.py --out-dir _production` 生成排期CSV、11期优先试录导演卡及提词文稿。这是**试录方案**，非计时事实。
- 本系列已有稿件默认按180秒五幕目标书写。自动分配试录秒数只按字数比例调整，不是实际语速或字幕最终时间码。

## 通过门槛：六道不可替代的独立检查

| 门槛 | 谁来证明 | 必须留下什么 | 失败时 |
|---|---|---|---|
| 1. 内容与事实 | 事实核查编辑 | 原文URL、章节/页码、所核原句、适用日期、异议记录 | 删除或纠正断言 |
| 2. 计算与口径 | 财务分析审核 | 算式、分子分母、币种单位、统计期、主体及复核人 | 修正三套稿并重新试录 |
| 3. 台词可录 | 主播 + 导演 | 带版本信息的录音、实际每幕入出秒、总秒数、口播难词/停顿 | 调整五幕和内容密度 |
| 4. 画面与版权 | 制片/视觉 | 图卡终稿、9:16字幕样片、图文来源/授权、示意标注 | 换原创画面或补授权 |
| 5. 金融合规 | 平台/合规审核 | 内容资质、平台最新规则、观点与AI披露、无荐股/收益承诺 | 停发并修订 |
| 6. 发布决定 | 总编 | 所有前项通过、最终文件Git SHA、审核人及日期、发布方式 | 保持 draft / in_review |

不得因为链接可点击就填写“已查证”，不得因为CI通过就填写“已试录”。未核实的现实数字不能仅把来源URL放进research.md后就算通过。

## 台词和分镜时间轴重校

1. 先按每段文字长度找到难以在当前预设时间自然读完的段落。250字符/分钟是**排查阈值**，不代表所有主播的上限。
2. 优先删去重复或非主线的内容，适度把推导移到可读数字图卡，但**不得删掉限定条件**。其次通过录音真实记录每段秒数，再同步修改 `script.md` 标题、`storyboard.md` 逐段时间及JSON `voiceover.start/end`。
3. 如果尚未试录，不改变原180秒区间以冒充拍摄已完成。系统推荐的“试读建议秒数”写在导演卡旁，原五幕仍是策划区间。
4. 调整文本需同时同步三份：稿、分镜、结构化JSON，确保字幕拿的是当前同一版本。

## 来源自检的准确结论

- 静态工具只判断JSON与文稿结构、来源ID、HTTPS字符串是否存在；**不请求外网原文、不校验网页是否仍可访问、不替代人工核查每条断言**。
- 对法律/政策、银行负债与地产融资、公司财报、复杂金融工具，应逐字区分全国规则与地方细则、境内与境外会计体系、实际发生与模拟情景。
- 真实数据必须标明披露主体、统计期、来源、币种、数字用途；对没有原始发表日期的来源，schema中的 `published_at` 仅可明确说明为核查快照日。
- 若发现事实性误导，先将稿件退回修订，逐项更新研究卡、台词、分镜与JSON，并保留Git差异记录。

## 正式发布是一个单独的PR

- 审稿结论在 `production/release-decision-template.md` 填写；未全部签署者留空，不得虚构通过。
- 仅签核后、经独立复核确认，才在发布PR中同步更新 manifest EP状态、各.md frontmatter、JSON `status` 和 `published_at`，并执行构建检查。
- 发布PR必须提供音频实录时长、正确的项目/政策来源、画面授权信息和总编决议。流程建议一篇一PR，逐期公开以方便审计和纠错。
- `python scripts/qa_finance100.py --strict-release` 是**故意始终返回非零**的禁止误发布命令，用于确认没有任何无人工证据的自动放行途径；不要把它加入普通CI。

## 可复现自检

```bash
python scripts/build_site.py --check
python scripts/sync_skills.py --check
python -m unittest discover -s tests -v
python scripts/qa_finance100.py --check --report _qa/finance100-review.json
python scripts/prepare_finance100_production.py --out-dir _production
```

总编可先安排优先试录：EP029、033、053、060、064、069、073、085、086、098、100。
