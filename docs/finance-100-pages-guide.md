# 财经100集：课程网站、完整工作稿和审核制作展示

> 更新：2026-11-10。**网站公开的是编辑工作材料，不是100部录制完成的视频，也不是100篇经过独立事实终审的正式财经文章。**

## 网站入口

- [十章100集课程目录](https://1998x-stack.github.io/finance-script-studio/series/finance-100/)：浏览、按章节筛选、搜索EP编号或财经概念。
- [审核与制作中心](https://1998x-stack.github.io/finance-script-studio/production/)：100期制作状态、节奏预警、11期导演卡、全量审核报告、三种签核模板。
- [示例 EP029 完整制作稿](https://1998x-stack.github.io/finance-script-studio/series/finance-100/ep029/)：完整五段口播、全部分镜、研究卡、审稿记录和试录状态。

## 页面构成

| 路径 | 页面内容 | 当前审核性质 |
|---|---|---|
| `/` | 首页、四条财经研究主线、百期入口、审核制作导航 | 站点入口 |
| `/series/finance-100/` | 10章100期索引和搜索 | 课程目录 |
| `/series/finance-100/ep001/` 至 `ep100/` | 课程提纲、完整5段口播、9:16分镜、研究与来源、编辑审稿、静态自检及试录状态 | **公开待审编辑工作稿**，并非正式发布文章 |
| `/production/` | 六道审核门槛、100期排期/优先级、审查报告、审核模板 | 制作与审稿总览 |
| `/production/pilot/ep029/` 等11期 | 原始导演卡和提词稿的网页阅读入口 | 建议试录材料，没有真实录音 |
| `/production/production-queue.csv` | 100期原始制作队列表 | **PENDING/BLOCKED** 状态 |
| `/production/preflight.json` | 100期自动检查的完整结构化结果 | 只证明结构自检，不是独立事实核查 |
| `/data/finance100.json` | 公开课程索引与简要元信息，**不包含**完整逐字稿 | 机器可读课程目录 |
| `/articles/<slug>/` | 仅 `status=published` 的正式财经专题文章 | 独立的正式发布流程 |

所有未审批单集页面和试录卡采用 `noindex,follow`，不计入网站sitemap；审核制作总览和课程目录可通过网页导航访问。页面上可见完整工作稿，但不会因此变更文章的 `draft` 状态。

## 数据与自动更新

- `content/series/finance-100/manifest.json` 提供期号、章节和创作状态；`brief.md` 提供每期选题提纲。
- `content/articles/finance100-epXXX.json` 提供同步的完整五段口播和来源编号；`research.md`、`storyboard.md`、`review.md` 展示全文，`script.md` 原文件及录制备注同样可展开查看。
- `scripts/qa_finance100.py` 计算100期结构问题与语速预警，**不联网逐条查证**；`scripts/prepare_finance100_production.py` 生成CSV和试录包。
- 站点代码：`scripts/build_site.py` 调用 `scripts/series_site.py` 和 `scripts/production_site.py`，前端只用HTML/CSS/JavaScript，搜索和筛选关闭JS后仍保留全部链接。
- 浏览器中可读的审稿Markdown经过HTML转义，避免把仓库稿件中的HTML标签当成可执行网页内容。

## 构建与测试

```bash
python scripts/build_site.py --check
python scripts/sync_skills.py --check
python -m unittest discover -s tests -v
python scripts/qa_finance100.py --check
python scripts/build_site.py --out-dir _site
python -m http.server 8000 --directory _site
```

自检须确认每期网站都有 **完整口播、分镜、研究卡、审稿记录** 五个锚点；总览必须列出100期且能打开11期试录卡；全部稿件依旧未获发布授权，只有独立终审完成后才另行修改 `article.status`。

## 不允许的误导

- 不得把“100期可浏览”写成“100期已录制或已发布”。
- 不得把官网显示原始资料链接视为“每项原始事实都核实通过”。
- 不得通过批量修改文章 `draft` 为 `published` 来实现网站公开展示；本轮**没有修改任何文章发布状态**。
- 若未来须隐藏未审内容，必须调整课程工作区的站点生成策略，而不只是修改搜索索引。
