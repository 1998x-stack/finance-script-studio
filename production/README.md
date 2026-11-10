# 财经100：制片与人工终审工作区

> **发布保护**：本目录的模板不证明有任何人完成审核。未经逐句事实核查、算术复算、真实试录和总编授权，所有100期仍为 `in_review` / `draft`。

本工作区把已有100期初稿从“文件齐备”推进到“可以排期录制、有人负责审核、可以追溯版本”的流程，但不自动批准任何一期。

## 交接材料在哪里

- [全量自检结果与纠偏记录](../docs/finance-100-production-self-review-2026-11-10.md)
- [制作与终审 Skill Reference](../skill-src/finance-script-studio/references/production-review-and-recording.md)
- `python scripts/qa_finance100.py --check --report _qa/finance100-review.json`：生成静态自检明细，不查外链也不录音。
- `python scripts/prepare_finance100_production.py --out-dir _production`：生成100期排期CSV、11期导演卡与纯口播提词稿。GitHub Actions也保存同样内容为可下载artifact。
- [事实核查记录模板](fact-check-template.md)、[录音试录日志模板](recording-log-template.md)、[发布判定模板](release-decision-template.md)。

## 建议制片流转

1. 从100期排期中选EP，复制三个模板到单期工作目录（例如 `production/episodes/EP029/`），填写审核责任人和文件版本。
2. 编辑核查原始公告与重要计算；研究事实不能仅靠自动程序标为已核实。
3. 主播试读至少一遍，按音频记录真实起止秒数，导演根据时长和停顿调整内容及画面。
4. 对字幕、来源脚注、原画面授权、政策有效性做独立复核。
5. 完成所有签核后，由总编单独提交状态变更PR；现场音频或个人信息不必公开入库，可记录受控链接与内容哈希。

## 从`in_review`到`approved`必须有凭证

- **in_review**：完整初稿，但仍有未完成的事实/录音/版权/合规门槛。
- **approved**：独立编辑及总编批准内容版本，可安排上线；不是CI自动授予的状态。
- **published**：经独立PR在JSON中确认可公开，页面构建后才可称网站已发布。

当前既有静态校验会阻止100期任何一篇草稿被直接改为published。这是防止误发布的安全措施。未来首篇需要正式上线时，必须先设计并审核与人工审批记录匹配的单篇发布门槛，更新相关单元测试，而非直接绕过检查。

## 优先试录

EP029 → EP053 → EP033 → EP064 → EP073 → EP085 → EP086 → EP060 → EP069 → EP098 → EP100。

先让一批覆盖事实、政策、数字、证券与家庭知识的视频通过**真实**录制，再复用成熟制作规范于其余89期。
