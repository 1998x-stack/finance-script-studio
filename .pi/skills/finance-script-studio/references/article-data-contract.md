# 结构化文章与 GitHub Pages 数据契约

## 单一事实源

每篇稿件在 `content/articles/<slug>.json`。JSON Schema 在 `content/schema/article.schema.json`，严格兼容 v1.0。Python标准库生成器 `scripts/build_site.py` 对常见结构、引用、时间轴、状态进行运行时校验。

## 必填主字段

- `schema_version`: "1.0"；`slug`: 仅小写英数和连字符；`status`: draft/published。
- `category`: event / company / policy / concept，对应四栏目。
- `title`, `subtitle`, `lead`, `summary`, `keywords`：显示内容。
- `published_at`, `updated_at`, `as_of`：ISO日期；`as_of` 为研究截止日。
- `video_seconds`：30—180整数，`reading_minutes` 为估计值。
- `key_numbers`: 每项含 label/value/unit/period/detail/source_ids。
- `takeaways`: 可迁移结论。
- `sections`: heading + paragraphs[{text,source_ids}]，可选 bullets 字符串数组。
- `voiceover`: [{start,end,stage,text,shot}]，秒数从0递增，不能交叠，最后 end=video_seconds。
- `sources`: [{id,title,publisher,published_at,type,url}]，链接用 HTTPS。
- `fact_checks`: [{claim,status,source_ids}]，status 为 verified/attributed/analysis/scenario。
- 可选 `comparison`: {title,items:[{label,amount,display}],note,source_ids}。绘图金额同单位，最高项为100%宽度。

## 内容与页面转换

```text
content/articles/*.json
  └── scripts/build_site.py
       ├── _site/index.html
       ├── _site/articles/<slug>/index.html
       ├── _site/data/articles.json
       ├── _site/assets/site.css / site.js
       ├── _site/sitemap.xml
       └── _site/robots.txt
```

只生成 status=published 的公开文章页。draft仍参与数据合法性检查，但不进入站点索引。

网页正文/口播/分镜/来源来自同一个文稿对象；禁止在HTML模板里为单篇文章硬编码财经数字。这样新增文稿无需改动CSS或生成器。

## 执行

```bash
python3 scripts/build_site.py --check
python3 scripts/build_site.py --out-dir _site
python3 -m unittest discover -s tests -v
```

在 main 推送后，GitHub Actions `.github/workflows/pages.yml` 构建并部署到 Pages。首次需要在 Settings → Pages 选择 GitHub Actions；仓库连接器通常不能代替管理员启用此设置。public site 通过 URL 前缀 https://1998x-stack.github.io/finance-script-studio/ 发布。

## 编辑原则

不要为了对齐示例硬凑未经证实的数字；无 chart 可省略 comparison。首次使用复制 `content/examples/article-template.json`，替换占位内容后再发布。新字段或新卡片类型先升级schema与构建器、写测试，然后增加文稿。
