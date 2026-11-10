# Finance Script Studio

> 财经事实调查 × 三分钟口播 × 结构化财经专题页面

一个可持续发布的财经编辑系统。每篇稿件都是一个版本化 JSON 数据文件；Python 标准库生成严肃、专业、适合移动端阅读的 GitHub Pages 页面，同时保存可拍摄的 180 秒口播脚本、事实来源和分镜建议。

## 快速开始

```bash
python3 scripts/build_site.py --check
python3 scripts/build_site.py --out-dir _site
python3 -m unittest discover -s tests -v
python3 -m http.server 8000 --directory _site
```

本地访问 http://localhost:8000 。构建过程**无需第三方 Python 包、npm 或外部 API**。

## 发布一篇新稿

1. 复制 `content/examples/article-template.json` 到 `content/articles/<slug>.json`。
2. 按 `content/schema/article.schema.json` 填写标题、分类、统计日期、正文、视频分镜、每条数据的来源 ID 和参考链接。
3. 只在证据检查完成后把 `status` 改为 `published`；`draft` 不会生成公开页面。
4. 执行 `python3 scripts/build_site.py --check`，提交至 main。Pages workflow 自动构建索引、独立文章页、JSON 数据索引和 sitemap。

**四个栏目：** `event` 财经事件背后的真问题 / `company` 一家公司的商业逻辑 / `policy` 政策背后的经济机制 / `concept` 每天一个商业认知。

## 100 个核心财经概念（现行制作版）

**10 个模块 × 100 期、每期目标约180秒，100期均已有独立口播初稿、来源卡、分镜及审稿文件与100份 draft JSON。所有期号仍待人工终审及试录；本轮按七章范围 M04–M10 交付，其中 M04–M06 沿用前批内容，M07–M10 新增40期：**

- [2026-11-09 完整选题总纲](docs/finance-100-production-blueprint.md)（当前制作依据）
- [100期分模块工作区与进度索引](content/series/finance-100/README.md)
- [100期机器可读清单（manifest）](content/series/finance-100/manifest.json)
- [第一批30期内容交付与审核报告](docs/finance-100-batch-01-report.md)
- [第二批30期内容交付与审核报告](docs/finance-100-batch-02-report.md)
- [七章合并交付 M04–M10 与40期新增内容审稿报告](docs/finance-100-batch-03-seven-chapters.md)
- [分批写稿/审稿/发布指南](docs/finance-100-workflow.md)
- [2026-11-10全系列静态自检与制作交接审查](docs/finance-100-production-self-review-2026-11-10.md)
- [制作签核模板与试录操作说明](production/README.md)
- [早期100概念课程地图](docs/finance-100-concept-map.md)（历史参考，期号与现行方案不一致）

**进度口径：100期全部已有初稿，100期均为 `in_review`；已生成的100份 article JSON 均为 `draft`，不是已经发表的页面。** 正式公开稿件依旧由 `content/articles/` 的 `draft/published` 机制控制。

## Skill 部署

主版本在 `skill-src/finance-script-studio/`，包括 `SKILL.md` 与完整 `references/`、`templates/`。运行：

```bash
python3 scripts/sync_skills.py
python3 scripts/sync_skills.py --check
```

脚本会自包含地同步至三个目录：
- `.opencode/skills/finance-script-studio/`
- `.codex/skills/finance-script-studio/`
- `.pi/skills/finance-script-studio/`

各位置均有独立 SKILL.md 和 references，不依赖软链接。修改主版本后重新同步。Pi Coding Agent 支持在项目的 `.pi/skills/` 中自动发现 Skill；原先误写的 `.py/` 目录已迁移删除。

## GitHub Pages

工作流 `.github/workflows/pages.yml` 在推送 main 时自动校验并部署 `_site`，使用仓库名作为 GitHub Pages 的路径前缀。首次使用需在仓库 **Settings → Pages → Build and deployment → GitHub Actions** 选定 Actions 来源，确保 Actions 和 Pages 权限已开启。预期站点地址为：

https://1998x-stack.github.io/finance-script-studio/

仅有工作流文件不代表 Pages 已在仓库设置中启用。请查看 Actions 和 Settings → Pages 的实际部署状态。

## 内容边界

文稿含事实/计算/媒体报道/分析/情景的明确区别；统计时点、单位和可点击出处。历史研究按 `as_of` 标注，**不会随页面自动更新**。网页与脚本均不构成投资建议，禁止把负面观察写作债券实质违约。

本项目不依赖特定财经博主的个人台词，不复制第三方作品。