# 发布检查清单

- [ ] 标题、开头与结论回答同一个核心问题
- [ ] 基本事实来自原始公告或注明媒体归属
- [ ] 核对数据单位、日期、集团/子公司主体与计算比例
- [ ] 重要数字均有 source_ids，URL 可打开且与断言相关
- [ ] 未来兑付与交易只使用“拟/计划/截至”而非先验完成
- [ ] 区分事实、媒体说法、分析与情景
- [ ] 口播能在规定时长内自然朗读，镜头建议没有混入朗读文案
- [ ] 分镜依信息变化切换，重点数字在手机屏幕可读
- [ ] 已核查发布平台财经认证、商业合作及AI标注要求
- [ ] article JSON 验证通过，发布状态经过人工确认
- [ ] python3 scripts/build_site.py --check
- [ ] python3 scripts/sync_skills.py --check
- [ ] python3 -m unittest discover -s tests -v
- [ ] 若为发布更新，updated_at与修改来源已同步
- [ ] GitHub Actions成功，Pages可实际访问（首次启用需Settings→Pages）
