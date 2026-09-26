# Windows x64 完全离线包

本目录让 `run_offline.bat` 在不安装 Python、不联网的 Windows 10/11 x64 电脑上运行。它包含便携 Python、所需二进制依赖，以及上游只读数据库工具的固定源码快照。

## 使用条件

1. 数据属于你本人，或你已获得明确授权。
2. 电脑为 64 位 Windows 10/11。
3. 微信 4.x 已登录，且加密数据库与当前登录账号匹配；或者你已经有与该数据库完全匹配的 `keys.json`。
4. 解压完整 ZIP 后再运行，不要直接在压缩包预览器内双击。

如果数据库来自另一台电脑，而本机没有对应的登录进程或已缓存密钥，单靠加密数据库无法生成密钥。本项目不会猜测、破解或上传密钥。

## 一键运行

1. 保持 Windows 微信登录。
2. 双击项目根目录的 `run_offline.bat`。
3. 输入看板使用的匿名昵称。
4. 从本机会话列表选择一个聊天。
5. 完成后查看 `output/wechat-dashboard.png`。

过程中会在 `work/` 生成临时导出和匿名统计。`wechat-export.json` 可能含聊天正文，一键流程会在 PNG 成功生成后自动删除它；如果流程中途失败，请自行妥善删除。`analysis_data/records.jsonl` 只保留通话时间、类型和时长。

## 已有密钥或自定义路径

```bat
offline\runtime\python\python.exe tools\export_wechat_offline.py --keys-file "D:\安全目录\keys.json" --db-dir "D:\微信数据" --output work\wechat-export.json
offline\runtime\python\python.exe tools\build_stats.py --input work\wechat-export.json --out-dir work\analysis_data --self-name "奶盖" --other-name "芄兰"
```

密钥文件只按你给出的路径读取，不会被复制进项目或 ZIP。

## 离线边界

- 运行阶段没有下载、更新、遥测或上传代码。
- HTML 看板同样可断网打开。
- 当前包固定兼容上游 `wechatauto-replica` 1.2.4、提交 `01eb06ef464d23bb651040ff76413f7183adf7e3a`。
- 微信升级后若内存结构或数据库格式变化，固定版本可能失效；需要在联网环境重新审核和更新离线包。
- Linux 构建环境无法连接 Windows 微信进程；密钥扫描仍需在真实 Windows 机器上验证。

## 排错

- “未找到微信数据库目录”：确认微信 4.x 已登录，或传入 `--db-dir`。
- “未找到 Weixin.exe”：确认桌面微信正在运行且已登录。
- 权限错误：以与你运行微信相同的 Windows 用户启动；一般不需要管理员权限。
- 密钥不匹配：数据库、账号和登录进程必须属于同一来源。
- 安全软件拦截：该功能会只读扫描本机 `Weixin.exe` 内存。请先审阅 `offline/third_party/wechatauto-replica/wechatauto/db.py`；不要为不信任的程序关闭安全软件。

组件版本和校验值见 [BUILD_INFO.md](BUILD_INFO.md)，许可与原创归属见项目根目录的 `THIRD_PARTY_NOTICES.md`。上游项目与作者：`fanyuantaier/wechatauto-replica`，作者/维护者 **fanyuantaier**，Apache-2.0。
