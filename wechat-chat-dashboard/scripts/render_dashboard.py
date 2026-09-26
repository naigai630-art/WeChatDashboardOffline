from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


SKILL_ROOT = Path(__file__).resolve().parent.parent
FONT_REG = str(SKILL_ROOT / 'assets' / 'NotoSansSC-Regular.ttf')
FONT_BOLD = str(SKILL_ROOT / 'assets' / 'NotoSansSC-Bold.ttf')

W, H = 1920, 1080
BG = '#f7f6f9'
SURFACE = '#ffffff'
TEXT = '#272632'
MUTED = '#858391'
LINE = '#ece9ef'
PINK = ['#fcecf3', '#f9cadb', '#f38fb6', '#e94b8b', '#c81f67']
BLUE = '#e8f1ff'
YELLOW = '#fff6cf'
GREEN = '#e6fbef'


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def rounded_card(base: Image.Image, box: tuple[int, int, int, int], radius: int = 24) -> None:
    x1, y1, x2, y2 = box
    shadow = Image.new('RGBA', base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x1, y1 + 5, x2, y2 + 5), radius, fill=(38, 31, 50, 18))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    base.alpha_composite(shadow)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius, fill=SURFACE, outline=LINE, width=2)


def text(d: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int,
         color: str = TEXT, bold: bool = False, anchor: str | None = None) -> None:
    d.text(xy, value, fill=color, font=font(size, bold), anchor=anchor)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Render a Chinese WeChat chat statistics dashboard as PNG.')
    parser.add_argument('--stats', required=True, type=Path, help='Path to stats.json')
    parser.add_argument('--records', type=Path, help='Optional records.jsonl for longest call detection')
    parser.add_argument('--output', required=True, type=Path, help='Output PNG path')
    parser.add_argument('--left-name', default='我', help='Name representing the self sender')
    parser.add_argument('--right-name', default='对方', help='Name representing the other sender')
    return parser.parse_args()


def longest_call(records: Path | None) -> tuple[str, str]:
    best_seconds = 0
    best_label = '未提供逐条记录'
    if not records or not records.exists():
        return '无数据', best_label
    with records.open(encoding='utf-8') as handle:
        for line in handle:
            row = json.loads(line)
            seconds = row.get('duration_seconds') or 0
            if row.get('category') in ('语音通话', '视频通话') and seconds > best_seconds:
                best_seconds = seconds
                kind = row.get('category', '通话')
                day = str(row.get('time', ''))[:10].replace('-', '/')
                best_label = f'{kind} · {day}'
    if not best_seconds:
        return '无数据', best_label
    hours, rest = divmod(best_seconds, 3600)
    minutes, seconds = divmod(rest, 60)
    return f'{hours}:{minutes:02d}:{seconds:02d}', best_label


def main() -> None:
    args = parse_args()
    data = json.loads(args.stats.read_text(encoding='utf-8'))
    daily = Counter()
    for key, value in data['daily'].items():
        daily[key.split('|')[0]] += value

    canvas = Image.new('RGBA', (W, H), BG)
    d = ImageDraw.Draw(canvas)

    margin = 48
    gap = 22
    header = (margin, 38, W - margin, 170)
    rounded_card(canvas, header, 28)

    text(d, (82, 66), '微信 · 私聊量化', 17, MUTED, True)
    text(d, (82, 99), f'{args.left_name} × {args.right_name}', 29, TEXT, True)
    first_day = str(data['first_time'])[:10].replace('-', '/')
    last_day = str(data['last_time'])[:10].replace('-', '/')
    text(d, (82, 139), f'{first_day} 至 {last_day} · {data.get("timezone", "本地时间")}', 15, MUTED)

    top_metrics = [
        (f'{data["total_rows"]:,}', '消息总数'),
        (f'{data["calendar_days"]:,}', '统计天数'),
        (f'{data["human_rows"] / data["calendar_days"]:.0f}', '自然日日均消息'),
        (f'{data["active_days"] / data["calendar_days"] * 100:.1f}%', '聊天活跃率'),
    ]
    mx = 760
    for i, (value, label) in enumerate(top_metrics):
        x = mx + i * 270
        text(d, (x, 88), value, 32, TEXT, True)
        text(d, (x, 129), label, 13, MUTED, True)

    upper_y1, upper_y2 = 193, 548
    left = (margin, upper_y1, 1288, upper_y2)
    right = (1310, upper_y1, W - margin, upper_y2)
    rounded_card(canvas, left, 26)
    rounded_card(canvas, right, 26)

    text(d, (82, 225), '聊天活跃热力图', 18, MUTED, True)
    text(d, (82, 256), '颜色越深表示当天消息越多', 15, MUTED)

    heat_x, heat_y = 118, 323
    cell, cg = 14, 5
    start = date.fromisoformat(str(data['first_time'])[:10])
    end = date.fromisoformat(str(data['last_time'])[:10])
    first_offset = start.weekday()
    current = start
    idx = 0
    last_month = None
    thresholds = [1, 150, 350, 650, 1000]
    while current <= end:
        pos = first_offset + idx
        week, weekday = divmod(pos, 7)
        count = daily[current.isoformat()]
        level = sum(count >= t for t in thresholds)
        fill = LINE if level == 0 else PINK[level - 1]
        x = heat_x + week * (cell + cg)
        y = heat_y + weekday * (cell + cg)
        d.rounded_rectangle((x, y, x + cell, y + cell), 3, fill=fill)
        if current.month != last_month and current.day <= 7:
            last_month = current.month
            text(d, (x, heat_y - 27), f'{current.month:02d}', 12, MUTED)
        current += timedelta(days=1)
        idx += 1

    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    for i, label in enumerate(weekdays):
        text(d, (88, heat_y + i * (cell + cg) + 7), label, 11, MUTED, True, 'mm')

    legend_x = 925
    text(d, (legend_x - 52, 489), '少', 11, MUTED, True)
    for i, color in enumerate(PINK):
        d.rounded_rectangle((legend_x + i * 31, 483, legend_x + 22 + i * 31, 496), 4, fill=color)
    text(d, (legend_x + 164, 489), '多', 11, MUTED, True, 'lm')

    rx = 1342
    text(d, (rx, 225), '消息占比', 17, MUTED, True)
    sender_counts = data.get('sender_counts', {})
    sender_items = sorted(sender_counts.items(), key=lambda item: item[1], reverse=True)
    if args.left_name in sender_counts or args.right_name in sender_counts:
        left_count = sender_counts.get(args.left_name, 0)
        right_count = sender_counts.get(args.right_name, 0)
    elif '我' in sender_counts:
        left_count = sender_counts['我']
        right_count = sender_counts.get(
            '对方', next((value for key, value in sender_items if key != '我'), 0)
        )
    else:
        left_count = sender_items[0][1] if sender_items else 0
        right_count = sender_items[1][1] if len(sender_items) > 1 else 0
    share_total = max(1, left_count + right_count)
    shares = [
        (args.left_name, left_count / share_total * 100, f'{left_count:,}', PINK[3]),
        (args.right_name, right_count / share_total * 100, f'{right_count:,}', PINK[1]),
    ]
    for i, (name, share, count, color) in enumerate(shares):
        y = 269 + i * 52
        text(d, (rx, y), name, 14, TEXT, True)
        d.rounded_rectangle((rx + 106, y + 3, 1795, y + 18), 8, fill=LINE)
        d.rounded_rectangle((rx + 106, y + 3, rx + 106 + int(347 * share / 100), y + 18), 8, fill=color)
        text(d, (1828, y + 10), f'{share:.1f}%', 13, MUTED, True, 'rm')

    d.line((rx, 378, 1838, 378), fill=LINE, width=2)
    text(d, (rx, 402), '通话概览', 17, MUTED, True)
    call_data = data.get('calls', {})
    calls = [
        (f'{call_data.get("total", 0):,}', '总通话次数'),
        (f'{call_data.get("connected", 0):,}', '接通次数'),
        (f'{call_data.get("total_duration_seconds", 0) / 3600:.1f} 小时', '累计接通时长'),
    ]
    for i, (value, label) in enumerate(calls):
        x = rx + i * 166
        text(d, (x, 439), value, 25, TEXT, True)
        text(d, (x, 474), label, 11, MUTED, True)
    text(d, (rx, 510), '最长单次通话', 11, MUTED, True)
    longest_value, longest_label = longest_call(args.records)
    text(d, (rx + 118, 510), longest_value, 21, PINK[4], True, 'lm')
    text(d, (1838, 510), longest_label, 11, MUTED, True, 'rm')

    weekday_totals = Counter()
    for key, value in data.get('weekdays', {}).items():
        weekday_totals[int(key.split('|')[0])] += value
    hour_totals = Counter()
    for key, value in data.get('hourly', {}).items():
        hour_totals[int(key.split('|')[0])] += value
    weekday_names = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    most_weekday = max(weekday_totals, key=weekday_totals.get) if weekday_totals else 0
    weekend_share = ((weekday_totals[5] + weekday_totals[6]) / max(1, data['human_rows']) * 100)
    most_hour = max(hour_totals, key=hour_totals.get) if hour_totals else 0

    cards = [
        ('活跃日日均消息', f'{data["human_rows"] / data["active_days"]:.0f} 条', f'按 {data["active_days"]} 个活跃日计算', BLUE),
        ('图片消息', f'{data["type_counts"].get("图片", 0):,} 条', f'另有 {data["type_counts"].get("视频", 0):,} 条视频消息', PINK[0]),
        ('最活跃星期', weekday_names[most_weekday], f'累计 {weekday_totals[most_weekday]:,} 条消息', YELLOW),
        ('周末活跃度', f'{weekend_share:.1f}%', '周六与周日消息占比', GREEN),
        ('最活跃日期', max(daily, key=daily.get).replace('-', '/'), f'当天共 {max(daily.values()):,} 条消息', PINK[0]),
        ('活跃天数', f'{data["active_days"]} 天', f'统计期共 {data["calendar_days"]} 天', BLUE),
        ('最长连续聊天', f'{data["longest_active_streak_days"]} 天', '连续有聊天记录的天数', YELLOW),
        ('最活跃时段', f'{most_hour:02d}:00', f'该小时累计 {hour_totals[most_hour]:,} 条消息', GREEN),
    ]
    bottom_y = 570
    col_gap = 22
    card_w = (W - 2 * margin - col_gap) // 2
    row_gap = 14
    card_h = 105
    for i, (label, value, note, accent) in enumerate(cards):
        col = i % 2
        row = i // 2
        x1 = margin + col * (card_w + col_gap)
        y1 = bottom_y + row * (card_h + row_gap)
        x2, y2 = x1 + card_w, y1 + card_h
        rounded_card(canvas, (x1, y1, x2, y2), 20)
        d.rounded_rectangle((x1 + 18, y1 + 18, x1 + 52, y1 + 52), 10, fill=accent)
        text(d, (x1 + 72, y1 + 23), label, 13, MUTED, True)
        text(d, (x1 + 72, y1 + 50), value, 23, TEXT, True)
        text(d, (x2 - 20, y1 + 55), note, 12, MUTED, False, 'rm')

    args.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert('RGB').save(args.output, format='PNG', optimize=True)
    print(args.output)


if __name__ == '__main__':
    main()
