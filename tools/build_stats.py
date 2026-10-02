#!/usr/bin/env python3
"""把 wechatauto 的 JSON 历史导出转换为看板所需的匿名统计文件。"""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable


CALL_TYPE_CODES = {50, 52, 53}
HUMAN_TYPE_NAMES = {
    "文本", "图片", "语音", "视频", "动画表情", "位置", "文件/链接/卡片", "红包",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="将 wechatauto JSON 导出转换为匿名看板统计。")
    parser.add_argument("--input", required=True, type=Path, help="wechatauto export_history 生成的 JSON")
    parser.add_argument("--out-dir", required=True, type=Path, help="输出目录")
    parser.add_argument("--self-name", default="参与者A", help="看板中自己的显示名")
    parser.add_argument("--other-name", default="参与者B", help="看板中对方的显示名")
    return parser.parse_args()


def load_messages(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return {}, [row for row in payload if isinstance(row, dict)]
    if not isinstance(payload, dict):
        raise ValueError("输入必须是 JSON 对象或消息数组")
    messages = payload.get("messages", [])
    if not isinstance(messages, list):
        raise ValueError("输入中的 messages 必须是数组")
    return payload, [row for row in messages if isinstance(row, dict)]


def to_datetime(value: Any) -> datetime | None:
    if isinstance(value, (int, float)):
        timestamp = float(value)
        if timestamp > 10_000_000_000:
            timestamp /= 1000
        try:
            return datetime.fromtimestamp(timestamp)
        except (OSError, OverflowError, ValueError):
            return None
    text = str(value or "").strip()
    if not text:
        return None
    if text.isdigit():
        return to_datetime(int(text))
    text = text.replace("T", " ").replace("Z", "")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[:19], fmt)
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _clock_seconds(value: str) -> int:
    parts = [int(part) for part in value.split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return 0


def duration_seconds(content: Any) -> int:
    """解析微信不同版本中的通话时长，无法确认时返回 0。"""
    text = str(content or "").replace("\\x00", "")
    # compress_content 有时保存 HTML 转义后的 XML，最多展开两层。
    for _ in range(2):
        expanded = html.unescape(text)
        if expanded == text:
            break
        text = expanded

    # 微信 4.x 的 <duration> 标签实测可能恒为 0，真实时长在 CDATA 文本中，
    # 所以必须优先解析“通话时长/通话中断 MM:SS”。
    clock = re.search(
        r"(?:通话时长|通话时间|通话中断|持续时间|时长|duration)\s*[：:=]?\s*((?:\d{1,3}:)?\d{1,2}:\d{2})",
        text,
        re.I,
    )
    if clock:
        return _clock_seconds(clock.group(1))

    chinese = re.search(
        r"(?:通话时长|通话时间|持续时间|时长)\s*[：:]?\s*"
        r"(?:(\d+)\s*(?:小时|时))?\s*(?:(\d+)\s*分)?\s*(?:(\d+)\s*秒)?",
        text,
    )
    if chinese and any(chinese.groups()):
        hours, minutes, seconds = (int(value or 0) for value in chinese.groups())
        return hours * 3600 + minutes * 60 + seconds

    field = r"(?:duration|callDuration|voipDuration|voipduration|call_time|calltime|time_len|timelen)"
    patterns = (
        rf"<{field}[^>]*>\s*(\d{{1,10}})\s*</(?:duration|callDuration|voipDuration|voipduration|call_time|calltime|time_len|timelen)>",
        rf"\b{field}\b\s*=\s*[\"'](\d{{1,10}})[\"']",
        rf"[\"']{field}[\"']\s*:\s*[\"']?(\d{{1,10}})",
        rf"\b{field}\b\s*[=:：>\s]+(\d{{1,10}})",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            value = int(match.group(1))
            if value <= 0:
                continue
            # 明显是毫秒时转换为秒，普通长通话秒数不会达到一百万。
            return value // 1000 if value >= 1_000_000 else value
    return 0


def base_type_code(value: Any) -> int | None:
    try:
        code = int(value)
    except (TypeError, ValueError):
        return None
    if code in CALL_TYPE_CODES:
        return code
    if code > 0xFFFF:
        low32 = code & 0xFFFFFFFF
        if low32 in CALL_TYPE_CODES:
            return low32
        low8 = low32 & 0xFF
        if low8 in CALL_TYPE_CODES:
            return low8
    return code


def call_category(content: Any) -> str:
    text = html.unescape(str(content or "")).lower()
    if "视频" in text or "video" in text or "videomsg" in text:
        return "视频通话"
    return "语音通话"


def message_type(row: dict[str, Any]) -> str:
    name = str(row.get("type") or row.get("category") or "其他")
    aliases = {"文本": "文字", "文件/链接/卡片": "文件", "音视频通话": "通话"}
    return aliases.get(name, name)


def is_self(row: dict[str, Any], payload: dict[str, Any]) -> bool:
    sender_id = row.get("sender_id")
    if sender_id in (2, "2"):
        return True
    self_nick = str(payload.get("nick_name") or "")
    return bool(self_nick and str(row.get("sender_name") or "") == self_nick)


def longest_streak(days: Iterable[str]) -> int:
    parsed = sorted({datetime.strptime(day, "%Y-%m-%d").date() for day in days})
    best = current = 0
    previous = None
    for day in parsed:
        current = current + 1 if previous and day == previous + timedelta(days=1) else 1
        best = max(best, current)
        previous = day
    return best


def build(payload: dict[str, Any], messages: list[dict[str, Any]], self_name: str, other_name: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    dated: list[tuple[dict[str, Any], datetime]] = []
    for row in messages:
        when = to_datetime(row.get("create_time", row.get("time")))
        if when:
            dated.append((row, when))
    if not dated:
        raise ValueError("没有找到可识别时间的消息记录")

    dated.sort(key=lambda item: item[1])
    sender_counts: Counter[str] = Counter()
    type_counts: Counter[str] = Counter()
    daily: Counter[str] = Counter()
    hourly: Counter[str] = Counter()
    weekdays: Counter[str] = Counter()
    call_records: list[dict[str, Any]] = []
    human_rows = 0

    for row, when in dated:
        sender = self_name if is_self(row, payload) else other_name
        kind = message_type(row)
        type_code = base_type_code(row.get("type_code"))
        is_call = type_code in CALL_TYPE_CODES or "通话" in kind or "voip" in kind.lower()
        if is_call:
            seconds = duration_seconds(row.get("content"))
            call_records.append({
                "time": when.strftime("%Y-%m-%d %H:%M:%S"),
                "category": call_category(row.get("content")),
                "duration_seconds": seconds,
            })
            continue
        sender_counts[sender] += 1
        type_counts[kind] += 1
        daily[f"{when:%Y-%m-%d}|{sender}"] += 1
        hourly[f"{when.hour}|{sender}"] += 1
        weekdays[f"{when.weekday()}|{sender}"] += 1
        if str(row.get("type") or "") in HUMAN_TYPE_NAMES or kind not in {"系统消息", "其他"}:
            human_rows += 1

    active_dates = sorted({key.split("|", 1)[0] for key in daily})
    first_time = dated[0][1]
    last_time = dated[-1][1]
    connected = [item for item in call_records if item["duration_seconds"] > 0]
    total_call_seconds = sum(item["duration_seconds"] for item in connected)
    average_call_seconds = round(total_call_seconds / len(connected)) if connected else 0
    stats = {
        "total_rows": len(dated),
        "human_rows": human_rows,
        "first_time": first_time.strftime("%Y-%m-%d %H:%M:%S"),
        "last_time": last_time.strftime("%Y-%m-%d %H:%M:%S"),
        "active_days": len(active_dates),
        "calendar_days": (last_time.date() - first_time.date()).days + 1,
        "longest_active_streak_days": longest_streak(active_dates),
        "timezone": "本地时间",
        "sender_counts": dict(sender_counts),
        "type_counts": dict(type_counts),
        "daily": dict(daily),
        "hourly": dict(hourly),
        "weekdays": dict(weekdays),
        "calls": {
            "total": len(call_records),
            "connected": len(connected),
            "total_duration_seconds": total_call_seconds,
            "average_duration_seconds": average_call_seconds,
        },
    }
    return stats, call_records


def write_outputs(out_dir: Path, stats: dict[str, Any], call_records: list[dict[str, Any]]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    with (out_dir / "records.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for row in call_records:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    args = parse_args()
    payload, messages = load_messages(args.input)
    stats, calls = build(payload, messages, args.self_name, args.other_name)
    write_outputs(args.out_dir, stats, calls)
    call_stats = stats["calls"]
    print(
        "通话统计："
        f"总计 {call_stats['total']}，"
        f"接通 {call_stats['connected']}，"
        f"累计 {call_stats['total_duration_seconds']} 秒"
    )
    if call_stats["total"] and not call_stats["connected"]:
        print("[提示] 已找到通话消息，但没有解析到正数时长；这些记录可能均未接通，或当前微信版本使用了新的时长字段。")
    print(args.out_dir / "stats.json")
    print(args.out_dir / "records.jsonl")


if __name__ == "__main__":
    main()
