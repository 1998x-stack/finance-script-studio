# 项目交付审计与 GitHub Pages 上线清单

> 审计日期：2026-11-09。仓库：`1998x-stack/finance-script-studio`。所有「已完成」以仓库文件或 GitHub Actions 记录为准，不能等同于站点已上线。

## 完成交付

- [x] 专业财经口播 Agent Skill，包含主版本 `skill-src/finance-script-studio/SKILL.md`、7份参考资料、2个模板。
- [x] 完整同步到 `.opencode/skills/`、`.codex/skills/`、`.py/skills/`。
- [x] 华发专题结构化稿件：`content/articles/huafa-liquidity-2026.json`，包括公开证据、概念机制、180秒口播与分镜。
- [x] 网页构建器：首页、独立文章页、信息来源索引、JSON数据目录、sitemap、响应式阅读样式。
- [x] Python 结构校验与基本发布回归测试；在静态构建时清除上次遗留的文章页，避免已撤稿文章残留。
- [x] 按10个模块列出100个财经核心概念及各期180秒的唯一主问题：`docs/finance-100-concept-map.md`。

## GitHub Pages 部署状态（2026-11-09 更新）

- [x] **GitHub Pages 已成功执行配置。** 最新 main [Actions 工作流 #42631912986](https://github.com/1998x-stack/finance-script-studio/actions/runs/42631912986) 的 `Configure GitHub Pages` 成功。
- [x] 静态网站成功构建，并通过 `Upload Pages artifact` 上传。
- [x] 同一工作流的 `deploy` job 最终显示 **success**，发布环境记录的页面 URL 是 https://1998x-stack.github.io/finance-script-studio/ 。
- [ ] **外部网页和移动端人工验收**：从非 Actions 网络实际打开并检查以下地址，确认内容显示、证据引用与资源文件正常：
  - https://1998x-stack.github.io/finance-script-studio/
  - https://1998x-stack.github.io/finance-script-studio/articles/huafa-liquidity-2026/
  - https://1998x-stack.github.io/finance-script-studio/data/articles.json
  - https://1998x-stack.github.io/finance-script-studio/sitemap.xml

原先的 `Get Pages site failed ... Not Found` 已被新一轮成功部署消除。**不再要求仓库管理员重复启用 Pages。** 如果未来新仓库复用本模板，首次需要在 [Settings → Pages](https://github.com/1998x-stack/finance-script-studio/settings/pages) 选择 `GitHub Actions`。默认 `GITHUB_TOKEN` 不能单凭 `enablement: true` 初始化一个从未启用 Pages 的新仓库。 

部署成功并不等于已完成真实浏览器、移动端及可访问性人工验收；后者作为编辑发布后的质检项目保留。

## 每次发布的命令

```bash
python3 scripts/build_site.py --check
python3 scripts/sync_skills.py --check
python3 -m unittest discover -s tests -v
python3 scripts/build_site.py --out-dir _site
```

## 不应误判为“已完成”的扩展工作

- **100个概念目前只有课程地图，没有100份已经完成事实核查的口播正文。** 应按优先级逐期制作，`draft` 审核后改为 `published`。
- 网站目前只有华发专题这一篇公开稿件；四个栏目的存在不意味着每个栏目已有内容。
- 华发案例以文中 `as_of` 为研究截止日，不是实时更新的信用风险判断。重大后续变化应复核来源和修订日期。

## 验收定义

“代码完成”＝全部检查和构建通过；“网站上线”＝Pages部署成功且页面外部可访问；“选题完成”＝100期课程地图已整理；“内容完成”＝对应单篇通过事实、法律主体、数字口径、朗读与画面审核。四者不应混用。
