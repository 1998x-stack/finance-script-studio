# 财经100集课程：GitHub Pages 展示与内容发布边界

> 2026-11-10。课程入口现在是 [财经100个核心概念](https://1998x-stack.github.io/finance-script-studio/series/finance-100/)。这里向读者开放课程结构与各集知识提纲；**这不是100集录制完成，也不是100篇稿件通过事实终审。**

## 为什么之前没有展示

原站的 \`scripts/build_site.py\` 只扫描 \`content/articles/*.json\`，校验后生成 \`status=published\` 的文章页。财经100期的 JSON 从创建至今均为 \`draft\`；这是刻意设置的发布门槛，而不是数据丢失。

## 现在新增什么

| URL | 内容 | 是否正式发表 |
|---|---|---|
| \`/\` | 首页新增“100个财经核心概念”专题，展示10章与进入课程的按钮 | 网站导航 |
| \`/series/finance-100/\` | 10章100期索引、课程描述、EP/概念搜索及章节筛选 | 公开课程目录 |
| \`/series/finance-100/ep001/\` … \`ep100/\` | 每集的题目、开场问题、概念定义、机制主线、案例方向、误区及原始创作稿链接 | **待审提纲预览** |
| \`/data/finance100.json\` | 机器可读的公开课程元信息（不包括完整口播稿） | 公开索引 |
| \`/articles/<slug>/\` | 原来通过终审并标为 \`published\` 的正式财经文章 | 正式发表 |

课程初稿未经全量人工核实，预览页带有 **noindex,follow**，不加入搜索引擎sitemap；sitemap只收录课程专栏首页及正式文章。预览页是给网站访客直接查看课程路线，并非公开发布的投资研究结论。

原始脚本 \`script.md\`、来源卡 \`research.md\` 和审核记录仍在公开GitHub仓库。预览页以“待审”的标签指向GitHub原稿，方便协作查看，**不复制完整逐字稿到官网的正式文章区域**。

## 内容来源及自动同步

该专栏只依赖两个现有数据源：

- \`content/series/finance-100/manifest.json\`：100期的准确编号、10章分组、顺序和制作状态。
- 各期 \`brief.md\`：提取“传播标题”“核心定义”“3分钟机制主线”“案例切口”“误区与边界”。源文本若缺失字段则构建失败，防止空卡。

是否存在正式文章由 \`content/articles/finance100-epXXX.json\` 的 \`status\` 决定。未审核的完整 \`voiceover\`、\`sections\` 和来源核查记录**不进入公共课程 JSON**；未来单期按正式发布流程变为 \`approved / published\` 后，课程详情才会链接到正式文章。

新增构建模块：\`scripts/series_site.py\`。原站仍由 \`scripts/build_site.py\` 调用；不需要Node、前端构建链或外部API。筛选与搜索使用 \`web/assets/series.js\`，不启用JavaScript时100个课程链接仍全部可用。

## 日常更新

修改一集标题或模块时，先更新 \`manifest.json\`、\`brief.md\` 对应字段和系列脚本/JSON保持一致；CI会执行如下检查：

\`\`\`bash
python scripts/build_site.py --check
python scripts/sync_skills.py --check
python -m unittest discover -s tests -v
python scripts/build_site.py --out-dir _site
\`\`\`

提交后，\`.github/workflows/pages.yml\` 自动构建站点并按既有Pages配置部署；不需要直接提交 \`_site/\`。发布后确认：

1. 首页出现“100个财经核心概念”的独立入口。
2. 专栏页显示10章及100条EP选题。
3. 每个EP页可以点击、返回章节、跳转相邻期号。
4. 章节筛选和搜索输入可以工作。
5. 未审核的正式文章 \`/articles/finance100-ep001/\` 不存在；课程提纲页显示“待审核”，并有 \`noindex\`。

### 不应做的事

- 不要为了展示选题而把100份文章JSON批量从 \`draft\` 改成 \`published\`。
- 不要把课程条目数100描述为已制作或已发布视频100集。
- 不要把自动化检查通过描述为已由专业编辑核实过100期事实。
- 不要在搜索结果中把GitHub待审逐字稿标成已经可直接播放的视频。
