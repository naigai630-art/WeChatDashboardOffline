#!/usr/bin/env python3
"""微信记录 → 匿名统计 → PNG 的一键离线入口。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
WORK = ROOT / "work"
EXPORT = WORK / "wechat-export.json"
ANALYSIS = WORK / "analysis_data"
PNG = ROOT / "output" / "wechat-dashboard.png"


def run(*args: object) -> None:
    command = [str(PYTHON), *(str(arg) for arg in args)]
    subprocess.run(command, cwd=ROOT, check=True)


def ask(prompt: str, default: str) -> str:
    value = input(f"{prompt} [{default}]：").strip()
    return value or default


def main() -> None:
    print("微信聊天量化看板 · 完全离线版")
    print("# 请仔细阅读免责声明：")
    print("本工具仅用于处理使用者本人拥有、或已获得数据所有者明确授权的微信聊天记录。使用者应自行确认其数据来源、处理行为及使用目的符合所在地法律法规、平台规则和隐私要求。严禁将本工具用于未经授权的数据访问、隐私侵犯、监控、骚扰、商业窃取或其他违法用途。")
    print("本工具所有数据处理均设计为在使用者本地设备完成，不主动上传聊天记录、数据库密钥、微信账号信息或统计结果。使用者仍应自行妥善保管原始数据库、keys.json、导出记录、统计文件及生成图片，避免将敏感内容上传至公开平台或交给无关人员。")
    print("本工具不能保证兼容所有微信版本、数据库格式、Windows 环境或设备配置。微信客户端升级、数据库结构变化、安全软件拦截、密钥不匹配或文件损坏均可能导致程序无法运行、统计不完整或结果存在误差。生成的数据和图表仅供参考，不应作为司法、医疗、财务或其他专业决策的唯一依据。")
    print("数据库密钥扫描、验证及解密相关实现来自第三方开源项目 fanyuantaier/wechatauto-replica，原创作者及仓库维护者为 fanyuantaier，采用 Apache License 2.0。本项目仅提供离线封装、数据转换和可视化功能，不声称拥有上述第三方实现的原创权。相关版权、商标及其他权利归其各自权利人所有。")
    print("下载、运行或使用本工具，即表示使用者理解并同意自行承担数据备份、隐私保护、授权确认、软件兼容性及使用后果。开发者不对因使用、误用、无法使用本工具，或因数据丢失、泄露、损坏、统计偏差所产生的直接或间接损失承担责任。")
    self_name = ask("请输入你的昵称","")
    other_name = ask("请输入对方的昵称","")
    run(ROOT / "tools" / "export_wechat_offline.py", "--output", EXPORT)
    run(
        ROOT / "tools" / "build_stats.py", "--input", EXPORT, "--out-dir", ANALYSIS,
        "--self-name", self_name, "--other-name", other_name,
    )
    run(
        ROOT / "wechat-chat-dashboard" / "scripts" / "render_dashboard.py",
        "--stats", ANALYSIS / "stats.json", "--records", ANALYSIS / "records.jsonl",
        "--output", PNG, "--left-name", self_name, "--right-name", other_name,
    )
    EXPORT.unlink(missing_ok=True)
    print("临时原始导出已删除；匿名统计保留在 work\\analysis_data。")
    print(f"\n完成：{PNG}")
    if sys.platform == "win32":
        subprocess.run(["explorer", "/select,", str(PNG)], check=False)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\n运行失败：{exc}", file=sys.stderr)
        print("请查看 offline/README.md 的排错说明。", file=sys.stderr)
        input("按回车键退出……")
        raise SystemExit(1)
