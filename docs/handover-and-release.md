# 项目交付审计与 GitHub Pages 上线清单

> 审计日期：2026-11-09。仓库：`1998x-stack/finance-script-studio`。所有「已完成」以仓库文件或 GitHub Actions 记录为准，不能等同于站点已上线。

## 完成交付

- [x] 专业财经口播 Agent Skill，包含主版本 `skill-src/finance-script-studio/SKILL.md`、7份参考资料、2个模板。
- [x] 完整同步到 `.opencode/skills/`、`.codex/skills/`、`.py/skills/`。
- [x] 华发专题结构化稿件：`content/articles/huafa-liquidity-2026.json`，包括公开证据、概念机制、180秒口播与分镜。
- [x] 网页构建器：首页、独立文章页、信息来源索引、JSON数据目录、sitemap、响应式阅读样式。
- [x] Python 结构校验与基本发布回归测试；在静态构建时清除上次遗留的文章页，避免已撤稿文章残留。
- [x] 按10个模块列出100个财经核心概念及各期180秒的唯一主问题：`docs/finance-100-concept-map.md`。

## 发布前阻塞（需要仓库管理界面操作）

- [ ] **首次启用 GitHub Pages。** 当前曾有一次 main 部署在 `Configure GitHub Pages` 返回 404，说明尚未成功配置 Pages。请打开 [Settings → Pages](https://github.com/1998x-stack/finance-script-studio/settings/pages)，在 **Build and deployment → Source** 选择 **GitHub Actions**。
- [ ] 在设置完成后，去 [Actions](https://github.com/1998x-stack/finance-script-studio/actions/workflows/pages.yml) 重跑失败的 main workflow，或推送新的 main 提交。
- [ ] 确认部署 job 为 **success**，并实测以下页面与资源：
  - https://1998x-stack.github.io/finance-script-studio/
  - https://1998x-stack.github.io/finance-script-studio/articles/huafa-liquidity-2026/
  - https://1998x-stack.github.io/finance-script-studio/data/articles.json
  - https://1998x-stack.github.io/finance-script-studio/sitemap.xml
- [ ] 手机上复查首屏、文章证据链接、数字可读性与分镜时间表。
- [ ] 确认上线后关闭 [Issue #2](https://github.com/1998x-stack/finance-script-studio/issues/2)。

**重要：** `actions/configure-pages` 的 `enablement: true` 不能仅凭默认 `GITHUB_TOKEN` 自行启用新站点；不要为了绕过一次性设置而引入高权限长期 Token。GitHub Actions 工作流已经具备构建和部署逻辑，缺的是仓库 Pages 的首次激活。

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
