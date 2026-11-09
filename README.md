# 手机稳定分流

节点继续使用手机上名为 `WgetCloud` 的已有订阅。本仓库只维护规则、策略组和公开的通用设置，不含订阅地址、服务器地址、密码、UUID 或私钥。

## 导入

| 文件 | 固定更新链接 | 导入二维码 |
|---|---|---|
| 主配置 | [mobile.conf](https://raw.githubusercontent.com/xialovezhu-wq/shadowrocket-config/main/mobile.conf) | [配置二维码](qr/mobile.png) |
| 可选广告模块 | [adblock.sgmodule](https://raw.githubusercontent.com/xialovezhu-wq/shadowrocket-config/main/adblock.sgmodule) | [模块二维码](qr/adblock.png) |

先保持手机现有连接可用，并保留原来的 `default.conf`。

1. 小火箭 → 配置 → 右上角“＋”，粘贴主配置链接下载。也可以使用小火箭扫描配置二维码。
2. 点击 `mobile.conf` → 使用配置；首页“全局路由”选择“配置”。
3. 在代理分组中，为“通用代理、ChatGPT、Claude、Gemini”分别手动选一个已验证可用的节点。四组均默认选择“美国 01”，不自动按延迟切换。首次仍需验证节点实际可用性；如需长期改用其他节点，应同步修改仓库四组的 `policy-select-name`，因为远程更新会覆盖手机上的临时选择。节点名称必须完整匹配，包括名称中的旗帜符号。节点名称改变后也要更新对应默认值。
4. 先验证国内服务、AI 和境外网站。确认分流正常后，再到“配置 → 模块 → ＋”添加模块链接，或扫描模块二维码，单独开启基础广告过滤。

分组通过订阅名称读取本机节点，所以订阅名称须为 `WgetCloud`。套餐日期、流量提示等条目已排除。没有在这份配置中另建节点订阅。

## 分流与保留项

| 请求 | 处理 |
|---|---|
| 局域网、原配置中的国内常用服务、国内 IP | 直连 |
| Apple 常规服务 | 延续原配置直连；保留原有 Private Relay 代理例外 |
| ChatGPT、Claude、Gemini 专属域名 | 各自的手动策略组 |
| Google 通用服务、GitHub、YouTube 与未匹配请求 | 通用代理 |
| 广告域名 | 仅在独立广告模块开启时拦截 |

系统 DNS、备用 DNS、IPv6 开启且不优先，以及其余原有通用参数均保留；不新增 QUIC 覆写。原 `localhost` 映射和两条 Google CN 跳转也保留。没有新增 HTTPS 解密、证书或脚本。

广告模块使用固定的 37,692 条纯域名数据。列表时间仍为 2025-12-08，作为基础名单使用；不保证每个 App 都没有广告。模块关闭后恢复由主配置决定出口。确认误拦截后，在模块拦截项之前补充精确例外，并为例外指定与主配置一致的出口；不要直接对白名单中的所有境外服务强制直连。

## 更新

在小火箭“设置”的对应项目中设置：节点订阅每 24 小时检查；配置和模块各每天检查。后台 App 刷新要允许小火箭运行，但 iOS 后台任务不保证准时执行。

重要修改发布后，在手机上点击远程 `mobile.conf` → 更新配置，并更新广告模块，再核对版本与四个分组的节点选择。自动更新会覆盖直接写进远程配置的本地修改；需要持久保留的规则应回收到此仓库，私人设置留在手机本地扩展配置。

电脑关机不影响手机使用已下载的配置和规则。节点更新与规则更新各有自己的来源。

## 回退

首次使用若出现问题：在“配置”中选择原来的 `default.conf` → 使用配置；在“配置 → 模块”中关闭“手机基础广告过滤”。这两个动作分别恢复分流和去广告状态。

本仓库的完整版本同时保存主配置、模块和固定规则数据，固定版本地址见 [release.json](release.json)。回退时导入同一版本的两个文件；冻结的配置不含指回主分支的 `update-url`。恢复跟随更新时，重新使用上面的两个固定更新链接。

当前冻结版：[v2026.11.09.2 主配置](https://raw.githubusercontent.com/xialovezhu-wq/shadowrocket-config/e09e7e8e8744f9d7363809a0bcd833f1a2b5dd75/versions/v2026.11.09.2/mobile.conf) · [同版广告模块](https://raw.githubusercontent.com/xialovezhu-wq/shadowrocket-config/e09e7e8e8744f9d7363809a0bcd833f1a2b5dd75/versions/v2026.11.09.2/adblock.sgmodule)。

固定首版：[v2026.11.09.1 主配置](https://raw.githubusercontent.com/xialovezhu-wq/shadowrocket-config/46bf4bb71ceb67db56112210d4b22838112b1755/versions/v2026.11.09.1/mobile.conf) · [同版广告模块](https://raw.githubusercontent.com/xialovezhu-wq/shadowrocket-config/46bf4bb71ceb67db56112210d4b22838112b1755/versions/v2026.11.09.1/adblock.sgmodule)。两个地址都锁定完整提交号。

## 首次手机验收

分别使用 Wi-Fi 和蜂窝网络，查看连接日志，确认国内服务、三个 AI 服务及常用境外网站使用预期分组。再检查视频、登录、支付、推送、锁屏恢复，以及三轮 Wi-Fi／蜂窝切换。广告模块先关闭验证分流，再开启对比；若新旧配置下同一节点都慢，先检查线路或服务本身。

已完成文件静态检查、节点筛选检查、公开内容检查、二维码解码及发布读回。手机已完成配置编译、广告样例拒绝匹配，并实际验证远程更新后四组仍选择“美国 01”；尚未完成全部 Wi-Fi／蜂窝、登录支付与锁屏恢复场景验收。

## 电脑维护

修改前先看 [CHANGELOG.md](CHANGELOG.md) 与 [SOURCES.md](SOURCES.md)，编辑后运行：

```sh
python3 tools/validate.py
git diff --check
git diff
```

确认无订阅链接、节点凭据或私人域名后提交并发布。更新广告源时，新建固定数据提交并修改模块中的完整提交号；不要让模块直接跟随上游主分支。发布新版本时同步保存主配置、广告模块、来源与哈希，保留旧版本及其数据提交。

静态检查验证预期分流与文件结构，不模拟小火箭内核的全部行为。使用 GPL-2.0 许可证；上游来源与修改说明见 [SOURCES.md](SOURCES.md)。
