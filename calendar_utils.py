import os
from datetime import datetime
from ics import Calendar, Event
from schemas import MeetingMinutes, ActionItem, KeyTimePoint


def generate_ics(minutes: MeetingMinutes, output_dir: str = "static") -> str:
    """根据会议纪要生成 .ics 日历文件，返回文件路径"""
    cal = Calendar()

    def make_event(title: str, dt_str: str, description: str | None, uid_suffix: str) -> Event:
        event = Event()
        event.name = title
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        except ValueError:
            dt = datetime.strptime(dt_str, "%Y-%m-%d")
        event.begin = dt
        event.description = description or ""
        event.uid = f"{uid_suffix}@meeting-assistant"
        return event

    # 待办事项截止时间
    for item in minutes.action_items:
        if item.deadline:
            desc = f"负责人: {item.assignee or '未指定'}\n优先级: {item.priority.value}"
            cal.events.add(make_event(
                f"[待办] {item.content}",
                item.deadline,
                desc,
                f"action-{hash(item.content) & 0x7FFFFFFF}"
            ))

    # 关键时间节点
    for tp in minutes.key_time_points:
        cal.events.add(make_event(
            f"[节点] {tp.title}",
            tp.datetime,
            tp.description,
            f"timepoint-{hash(tp.title) & 0x7FFFFFFF}"
        ))

    # 下次会议
    if minutes.next_meeting:
        cal.events.add(make_event(
            f"[下次会议] {minutes.title}",
            minutes.next_meeting,
            f"参会人员: {', '.join(minutes.participants)}",
            f"nextmeeting-{hash(minutes.title) & 0x7FFFFFFF}"
        ))

    os.makedirs(output_dir, exist_ok=True)
    filename = f"meeting_{minutes.date.replace('-', '')}_{hash(minutes.title) & 0x7FFFFFFF}.ics"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(cal.serialize())

    return filepath


def generate_markdown_table(minutes: MeetingMinutes) -> str:
    """生成待办事项的 Markdown 表格"""

    def priority_emoji(p):
        return {"高": "🔴", "中": "🟡", "低": "🟢"}.get(p.value, "⚪")

    rows = [
        "| 优先级 | 待办事项 | 负责人 | 截止时间 |",
        "|--------|---------|--------|----------|",
    ]
    for item in sorted(
        minutes.action_items,
        key=lambda x: {"高": 0, "中": 1, "低": 2}[x.priority.value]
    ):
        rows.append(
            f"| {priority_emoji(item.priority)} {item.priority.value} "
            f"| {item.content} "
            f"| {item.assignee or '-'} "
            f"| {item.deadline or '-'} |"
        )
    return "\n".join(rows)