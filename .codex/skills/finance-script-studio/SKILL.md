---
name: finance-script-studio
description: 用真实财经事件构建证据充分、因果清晰、适合180秒口播的财经稿件，并输出与 GitHub Pages 兼容的结构化文章 JSON、分镜和发布审核记录。当任务涉及财经热点解读、企业研究、政策机制、商业知识科普、财经口播脚本或把稿件发布成财经专题页时使用。
---

# Finance Script Studio — 财经研究、口播与专题页

> 核心承诺：以**一个真实事件**回答**一个关键问题**，让观众记住**一条可迁移的商业规律**。内容追求注意力、理解力和可信度的共同提升，不靠无证据危机感换取停留。

## 触发与使用

用户要求以下任务时启用：财经深度调查、财经热点口播、公司/政策/商业机制拆解、三分钟视频、财经内容策划、财经专题页生成或文稿结构化。若只要求简短财经问答，按必要程度缩减产物，不能为填模板制造事实。

根据任务，渐进式阅读参考文件：

- **研究与证据** → [references/research-and-fact-check.md](references/research-and-fact-check.md)
- **栏目定位、角度与总编审稿** → [references/editorial-playbook.md](references/editorial-playbook.md)
- **3分钟五幕编剧、开头与表达** → [references/narrative-architecture.md](references/narrative-architecture.md)
- **分镜、图表、字幕与视觉风格** → [references/visual-directing.md](references/visual-directing.md)
- **JSON字段与 GitHub Pages 出版** → [references/article-data-contract.md](references/article-data-contract.md)
- **合规、披露与更正机制** → [references/compliance-and-review.md](references/compliance-and-review.md)
- **制作、试录及发布前终审** → [references/production-review-and-recording.md](references/production-review-and-recording.md)
- **示范案例与事实边界** → [references/huafa-case-study.md](references/huafa-case-study.md)

启动工作可复制 [templates/video-brief.md](templates/video-brief.md)，发布前检查 [templates/publishing-checklist.md](templates/publishing-checklist.md)。

## 工作角色

同时担任：财经调查记者、财务与商业分析师、短视频编剧、传播心理编辑、口播导演、事实与合规审校。不得把这些角色变成多个互相重复的长篇输出。

## 标准工作流程（按顺序完成）

### 1. 核查事实

- 锁定**研究截止日、事件主体、法律主体与报表口径**，先查原始公告/财报/交易所披露，再查有出处的专业媒体。
- 按 `verified`（原始来源支持）、`attributed`（媒体/当事方说法）、`analysis`（合理推导）、`scenario`（有条件的未来情景）分类。
- 每个重要数字记录：数值、币种、单位、统计期间、集团/子公司、分子分母、来源标题、URL、披露日期与核查日期。
- 核验不同时间点：不可将6月末现金与9月末债务直接组成“同一时点覆盖率”。
- 有争议的指控要明确归属；无法核实的细节不得进入口播确定事实。信息过时要说清“截至哪天”。

### 2. 选择栏目与核心题眼

必须归入四条主线之一：

1. `event` **财经事件背后的真问题**：债务、流动性、风险传导、重大事件。
2. `company` **一家公司的商业逻辑**：赚钱机制、收入质量、成本、竞争优势与弱点。
3. `policy` **政策背后的经济机制**：政策目标、执行路径、受益/受压主体和限制条件。
4. `concept` **每天一个商业认知**：现金流、杠杆、估值、复利、竞争壁垒等。

先提出3个可选角度，比较吸引力、解释价值、来源充分度、受众门槛及合规风险，再挑选1个。最终要用两句话写明：
- 本期要回答的唯一问题：______。
- 观众看完能迁移到其他事件的认知：______。

### 3. 五幕结构（默认180秒）

- **00–15s 冲突：** 以真实反差或具体问题开场；开头说人话，不做自我介绍。
- **15–45s 事件：** 主体、关键时间、实际发生了什么、哪些尚未发生。
- **45–105s 机制：** 2—4个能互相比较的数字，解释一条主因果链。
- **105–150s 修正：** 新的证据、反方解释、外部支持或限制条件，避免单向叙事。
- **150–180s 回报：** 回答开头，交付金融规律或可验证的观察点。

时间不是机械规定：可按真实语速调整。理性悬念来自信息缺口，不来自编造“内幕”“暴雷”。

### 4. 写成可朗读的口播

- 默认针对成年人非金融背景观众，180秒先拟 **600—750汉字**，再按普通话朗读、专业名词和数字停顿校准。
- 用短句和清晰的转折词；技术名词出现后马上给出解释。
- 采用具体比较，不孤立抛数字。生活类比应明确只是类比，不改变数据含义。
- 每20—30秒产生一个有效信息回报，不强制每几秒“反转”。
- **一条主问题、一条因果链、一次有证据的认知修正、一个结论。**
- 禁止把调查报告原样朗读；切除不服务核心问题的背景。

### 5. 画面与证据

- 为每段提供：起止秒、阶段、**纯口播**、画面建议、屏幕重点字。
- 图表只承载观众在手机上看得清的比较。所有百分比注明分子分母和同一口径。
- 原始公告截图只突出真实标题、日期和必要原文；不得伪造报道或企业商标。
- 镜头切换由信息变化触发，避免无目的花式剪辑。
- 视觉规范详见 [references/visual-directing.md](references/visual-directing.md)。

### 6. 输出结构化稿件

如用户要求网页或仓库存档，输出匹配 `content/schema/article.schema.json` 的**严格 JSON**，写入 `content/articles/<slug>.json`；不能把 Markdown 字符串冒充 JSON。
- `status: draft` 的文稿不公开建页。
- 确认来源与审稿后使用 `status: published`。
- `sources` 中 URL 必须可追溯，正文/数据通过 `source_ids` 关联。
- `voiceover` 按时间顺序，区间不能重叠，最后一段结束时间等于 `video_seconds`。
- 运行 `python3 scripts/build_site.py --check` 验证，再运行构建；若在仓库工作，同步 Skill 并验证副本。

### 7. 双重审核与修订、制作试录和放行

**真实性门槛优先于传播得分。** 审核以下风险：集团与子公司混淆；现金/资产/现金流混淆；静态差额被称为“真实缺口”；拟议支持称为已拨款；评级观察称为实质违约；预测写成事实；未经证实的违法指控；无资质的荐股与营销。

涉及系列批量出片，必须先运行 `scripts/qa_finance100.py`，再通过 `scripts/prepare_finance100_production.py` 生成100期排期与优先试录包，逐期进行独立事实核查、算术复算、真人180秒试录、图表版权与金融合规签核；详见 `references/production-review-and-recording.md`。自动测试通过**不能**替代真人审核或录音，不得自动提升为approved/published。

内部编辑权重（不是播放预测）：事实/证据30、核心问题20、叙事20、通俗15、视觉10、标题一致性5。任何严重事实错误都必须修改，不能用其他分数抵消。

### 8. 交付物

视任务规模交付：①证据简表；②角度比较和核心问题；③3个开头；④完整纯口播；⑤分镜时间表；⑥3个标题/封面建议；⑦来源与事实核查清单；⑧如需发布，完整 article JSON 与构建结果。研究分析和需要朗读的文字**必须分开**，来源引用不插入主播口中。

## 不可妥协的规则

准确、可验证、可更正、平衡且易懂。不从“有争议”推断违法，不从“负面观察”推断违约，不从“有政府支持”推断无风险。不得复制特定博主的个人标志性表达。文稿上线后重大事实变化要增加 `updated_at`、更新来源及文案，不得悄悄把旧稿写成新稿。

## 最短调用示例

```text
请按照 finance-script-studio Skill，研究【事件】，
截至【日期】，面向【受众】制作180秒口播。
先核实3项最关键证据，选一个唯一的核心问题，
给出自然口播、分镜、3个标题及 fact-check。
如需发布，再生成符合 article.schema.json 的结构化稿件。
```
