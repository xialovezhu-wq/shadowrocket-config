# 规则来源与版本

广告数据来自 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)，固定在提交 `0b6897dc17e0c513d25449c935a9694818e32f0c`。

- 文件：[AdvertisingLite_Domain.list](https://github.com/blackmatrix7/ios_rule_script/blob/0b6897dc17e0c513d25449c935a9694818e32f0c/rule/Shadowrocket/AdvertisingLite/AdvertisingLite_Domain.list)。
- 上游文件内的数据时间仍标注为 2025-12-08；此处将其作为固定基础名单，不声称它在持续更新。
- 仅使用 37,692 条域名项（23,753 条完整域名、13,939 条后缀）。上游总清单中的 IP、关键词和 URL 正则没有引入。
- 修改仅为重写文件头，避免原总清单的 MITM 提示与本域名文件混淆；域名条目保持一致。原始与分发文件的 SHA-256 见 `sources.lock.json`。
- 保留上游 GPL-2.0 许可证。本仓库配置与工具也按同一许可证提供。

基础直连和通用代理规则在用户提供的 Shadowrocket `default.conf` 上整理，保留原有服务例外与规则顺序。设备导出原件、订阅地址、节点连接参数不在仓库中。

AI 专用规则参考同一上游提交的 [OpenAI](https://github.com/blackmatrix7/ios_rule_script/blob/0b6897dc17e0c513d25449c935a9694818e32f0c/rule/Shadowrocket/OpenAI/OpenAI.list)、[Claude](https://github.com/blackmatrix7/ios_rule_script/blob/0b6897dc17e0c513d25449c935a9694818e32f0c/rule/Shadowrocket/Claude/Claude.list)、[Gemini](https://github.com/blackmatrix7/ios_rule_script/blob/0b6897dc17e0c513d25449c935a9694818e32f0c/rule/Shadowrocket/Gemini/Gemini.list) 条目，人工收窄到服务专属域名。Google 通用域名，以及 Auth0、Stripe、Cloudflare、Sentry 等共享服务不归入 AI 专用组。Gemini API 的精确主机名参考 [Google 官方快速入门](https://ai.google.dev/gemini-api/docs/quickstart)。

格式、订阅名称引用、导入链接和更新方式参考 [Shadowrocket 使用手册](https://github.com/LOWERTOP/Shadowrocket) 及其 [原始示例](https://github.com/LOWERTOP/Shadowrocket/blob/main/lazy_group.conf)。手册为社区维护的原始文档；本仓库的静态校验不能代替手机应用的编译与真实联网测试。
