# WeChat Dashboard Offline

面向 Windows 10/11 x64 的微信聊天记录本地量化工具。项目内置便携 Python 和必要依赖，可以在断网环境中完成本地数据库读取、匿名统计转换和 1920×1080 PNG 看板生成。

## 主要功能

1. 读取本人或已获授权的微信 4.x 本地数据库。
2. 自动生成聊天活跃热力图、双方消息占比和通话概览。
3. 统计最长单次通话、活跃日期、活跃时段和连续聊天天数。
4. 数据处理在本机完成，不主动上传聊天记录或数据库密钥。
5. 内置便携运行环境，无需单独安装 Python。

## 系统要求

1. 64 位 Windows 10 或 Windows 11。
2. 微信 4.x 已登录，且当前登录账号与数据库匹配。
3. 完整下载并解压仓库或 Release ZIP。

如果数据库来自另一台电脑，而当前电脑没有对应登录进程或匹配密钥，本工具无法凭空恢复密钥。

## 快速开始

1. 点击 GitHub 页面右上角的 **Code**，选择 **Download ZIP**。
2. 完整解压 ZIP，不能直接在压缩包预览窗口内运行。
3. 保持微信登录。
4. 双击 `run_offline.bat`。
5. 阅读免责声明，输入双方在看板中显示的昵称。
6. 选择需要统计的会话。
7. 查看 `output\wechat-dashboard.png`。

启动窗口无论成功或失败都会保持打开。遇到问题时，请保留退出代码并按照 [SECURITY.md](SECURITY.md) 的要求隐藏隐私信息。

## 项目结构

```text
.
├── .github/workflows/validate.yml
├── offline/
│   ├── runtime/python/                  便携 Python 与离线依赖
│   ├── third_party/wechatauto-replica/ 上游数据库读取源码
│   ├── BUILD_INFO.md
│   └── README.md
├── tools/
│   ├── export_wechat_offline.py
│   ├── build_stats.py
│   └── offline_launcher.py
├── wechat-chat-dashboard/
│   ├── assets/                          中文字体
│   └── scripts/render_dashboard.py
├── run_offline.bat
├── DISCLAIMER.md
├── THIRD_PARTY_NOTICES.md
└── LICENSE
```

## 隐私说明

运行时可能在 `work/` 中短暂生成含聊天正文的导出文件。PNG 成功生成后程序会自动删除该原始导出。匿名统计保存在 `work/analysis_data/`，生成图片保存在 `output/`。这些目录已被 `.gitignore` 排除，不应提交到 GitHub。

请勿提交或公开以下内容：

1. `keys.json` 或任何数据库密钥。
2. 微信数据库文件、wxid、账号目录和诊断日志。
3. `work/`、`output/` 或包含真实昵称和聊天统计的文件。

## 第三方项目与原创声明

数据库密钥扫描、验证和解密实现来自 [fanyuantaier/wechatauto-replica](https://github.com/fanyuantaier/wechatauto-replica)。原创作者及仓库维护者为 **fanyuantaier**，采用 Apache License 2.0。本项目增加离线封装、匿名统计转换和看板生成流程。

完整归属与组件版本见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 和 [offline/BUILD_INFO.md](offline/BUILD_INFO.md)。

## 安全与责任

仅处理你本人拥有或已获得明确授权的数据。运行前请阅读 [DISCLAIMER.md](DISCLAIMER.md)。安全问题请参阅 [SECURITY.md](SECURITY.md)，不要在公开 Issue 中粘贴密钥、聊天记录或私人路径。

## License

本项目自有代码采用 MIT License。第三方组件继续遵循各自许可证，详见 `THIRD_PARTY_NOTICES.md`。
