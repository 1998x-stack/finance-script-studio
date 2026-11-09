# 财经100概念｜分批撰写与发布指南

> 权威选题体系：[2026-11-09总纲](./finance-100-production-blueprint.md)。本目录与 [100期工作区](../content/series/finance-100/README.md) 保持一致。

## 一、逐期制作顺序

1. **定稿选题**：从模块 README 选择待撰写期号，查看 `brief.md` 中的传播标题、定义、讲解主线、案例切口和误区边界。
2. **研究与求证**：把定义、政策口径和案例原始链接写入 `research.md`；日期、统计范围、数字与图表分别记录。
3. **写逐字稿**：在 `script.md` 的五个时间段完成约180秒正文，按约500–650汉字初稿试录，而非机械凑字数。
4. **做分镜**：在 `storyboard.md` 标注可拍镜头、数据图示、屏幕文案及版权状态。
5. **事实审稿**：对事实、分析和假设作区分；出现失效数据或无法核实的传闻就修改或删除；按项目Skill的审稿清单执行。
6. **如需公开发布**：按 `content/examples/article-template.json` 和 `content/schema/article.schema.json` 生成 `content/articles/<slug>.json`，先保持 `draft`，通过检查后再改为 `published`。

## 二、状态管理

- `planned`：只有简报及占位文件；
- `drafting`：正在补资料、写逐字稿；
- `in_review`：进入事实和表达复核；
- `approved`：达到拍摄/转正式发布记录的质量要求。

同步更新各期文件头与 `manifest.json` 的状态，确保持续分批迭代时能够按期号定位，不覆盖已完成的其他稿件。完整100期的占位文件不应当被视为100篇已发表文章。

## 三、与原有仓库的边界

- 原有的 `content/articles/` 是公开站点的结构化文章目录，不能放未核实的概念占位文章。
- 本次新增的 `content/series/finance-100/` 是内部创作工作区，现有 `scripts/build_site.py` 不会将其自动公开。
- 仓库旧版 `docs/finance-100-concept-map.md` 使用另一套期号映射，保留作早期课程地图参考。现在以新总纲及 `manifest.json` 为准。

## 四、每期必备交付

- 一份经核查的口播逐字稿；
- 一份来源与事实核查记录；
- 一份五段式分镜；
- 需要网站发布时，再加一份符合schema的结构化文章JSON。
