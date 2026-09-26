#!/usr/bin/env python3
"""在 Windows 本机离线提取本人/获授权的微信 4.x 聊天记录。"""

from __future__ import annotations

import argparse
import json
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VENDOR_ROOT = ROOT / "offline" / "third_party" / "wechatauto-replica"


def load_db_class():
    if sys.platform != "win32":
        raise RuntimeError("密钥提取仅支持 64 位 Windows；统计转换可在其他系统运行。")
    if not VENDOR_ROOT.exists():
        raise RuntimeError(f"缺少内置上游源码：{VENDOR_ROOT}")
    # 跳过上游会加载 GUI/OCR 依赖的 __init__.py，仅启用只读数据库模块。
    package = types.ModuleType("wechatauto")
    package.__path__ = [str(VENDOR_ROOT / "wechatauto")]
    package.__file__ = str(VENDOR_ROOT / "wechatauto" / "__init__.py")
    sys.modules["wechatauto"] = package
    from wechatauto.db import WeChatDB  # type: ignore
    return WeChatDB


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="本机离线导出微信聊天记录。")
    parser.add_argument("--user", help="会话 username；不填时显示列表并交互选择")
    parser.add_argument("--output", type=Path, default=ROOT / "work" / "wechat-export.json")
    parser.add_argument("--db-dir", help="可选：微信数据根目录")
    parser.add_argument("--keys-file", help="可选：已有 keys.json 的路径；不会复制进项目")
    parser.add_argument("--limit", type=int, default=None, help="可选：最多导出最近 N 条")
    return parser.parse_args()


def choose_chat(db, requested: str | None) -> str:
    if requested:
        return requested
    chats = db.list_message_chats()
    if not chats:
        raise RuntimeError("未找到包含消息的会话")
    shown = chats[:100]
    print("\n可用会话（最多显示 100 个）：")
    for index, chat in enumerate(shown, 1):
        print(f"{index:3d}. {chat.get('name') or chat.get('username')}  ({chat.get('message_count', 0)} 条)")
    while True:
        raw = input("\n请输入序号：").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(shown):
            return str(shown[int(raw) - 1]["username"])
        print("序号无效，请重试。")


def main() -> None:
    args = parse_args()
    WeChatDB = load_db_class()
    kwargs = {}
    if args.db_dir:
        kwargs["db_dir"] = args.db_dir
    if args.keys_file:
        kwargs["keys_file"] = args.keys_file
    print("正在读取本机微信数据库。首次提取密钥可能需要数秒，请保持微信已登录。")
    db = WeChatDB(**kwargs)
    user = choose_chat(db, args.user)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = db.export_history(
        str(args.output), fmt="json", users=[user], limit_per_chat=args.limit,
        progress=lambda current, total, name: print(f"正在导出：{name} ({current + 1}/{total})"),
    )
    metadata = {"output": str(args.output), "chat": user, **result}
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
