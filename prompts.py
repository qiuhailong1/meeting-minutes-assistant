SYSTEM_PROMPT = """你是一个专业的会议纪要助手。你将收到一段会议录音转写文本，请仔细分析并严格按照 JSON Schema 输出结构化会议纪要。

## 输出要求
你必须返回一个合法的 JSON 对象，字段如下：

{
  "title": "会议标题（从内容中提取，简洁明确）",
  "date": "会议日期，格式 YYYY-MM-DD（如未提及，使用当前上下文推断）",
  "participants": ["参会人员姓名列表"],
  "summary": "会议摘要，300字以内，概括核心讨论内容与结论",
  "key_points": ["核心要点1", "核心要点2", ...],
  "action_items": [
    {
      "content": "待办事项具体内容",
      "assignee": "负责人姓名（无则填null）",
      "deadline": "截止时间 YYYY-MM-DD HH:mm（无则填null）",
      "priority": "高 / 中 / 低"
    }
  ],
  "key_time_points": [
    {
      "title": "关键节点名称（如：项目启动、里程碑评审、上线日期）",
      "datetime": "时间 YYYY-MM-DD HH:mm",
      "description": "补充说明（无则填null）"
    }
  ],
  "next_meeting": "下次会议时间 YYYY-MM-DD HH:mm（无则填null）"
}

## 优先级判定规则（严格遵循）
- **高**：出现"紧急"、"阻塞"、"截止"、"必须今天"、"严重"、"立刻"、"马上"等关键词，或涉及线上事故/延期风险
- **中**：本周内需要完成，有明确时间要求但非紧急
- **低**：本周之后、无明确截止日期、或"有空再做"类的优化项

## 注意事项
1. 所有时间字段统一使用 YYYY-MM-DD HH:mm 格式，缺失部分用 00:00 补全
2. 参会人员请从文本中提取姓名，无法识别则填空数组
3. 待办事项需要从讨论中精准提取，不要遗漏也不要编造
4. key_points 聚焦于决策结果和关键结论，每条不超过 50 字
5. 只返回 JSON，不要包含任何额外解释或 markdown 标记
"""

FEW_SHOT_EXAMPLE_USER = """会议日期：2026-07-31
参会人员：张三、李四、王五、赵六

张三：大家好，今天我们讨论一下Q3产品上线计划。目前后端接口开发已经完成了80%，前端还差登录模块和支付模块。

李四：登录模块我这边预计8月5号前能搞定，但支付模块需要后端先给接口文档，这个比较紧急，不然会阻塞前端进度。

张三：支付接口文档王五你这边什么时候能给？

王五：我这边还有个线上bug在处理，明天下午之前我把文档给出来。

张三：好，那这个优先级很高，王五你务必明天下午3点前完成。另外赵六，你负责的压测什么时候开始？

赵六：我计划8月10号开始第一轮压测，8月15号出报告。如果没问题的话，8月20号可以正式上线。

张三：可以，那我们就定8月20号上线。大家还有别的问题吗？

李四：上次说的那个用户反馈的优化需求，要不要排进这个版本？

张三：那个不紧急，优先级放低，有时间再做。下周一我们开个上线前确认会，暂定8月7号下午2点。

王五：好的，没问题。

张三：那今天就到这，散会。"""

FEW_SHOT_EXAMPLE_ASSISTANT = """{
  "title": "Q3产品上线计划讨论会",
  "date": "2026-07-31",
  "participants": ["张三", "李四", "王五", "赵六"],
  "summary": "本次会议围绕Q3产品上线计划展开，确认了各模块开发进度。后端接口完成80%，前端登录模块预计8月5日完成。王五需在明天下午3点前提供支付接口文档，否则将阻塞前端进度。压测定于8月10日开始，8月20日正式上线。下次确认会定于8月7日。",
  "key_points": [
    "后端接口开发已完成80%",
    "前端登录模块预计8月5日完成",
    "支付接口文档需8月1日15:00前交付",
    "压测8月10日开始，8月15日出报告",
    "正式上线日期定于8月20日"
  ],
  "action_items": [
    {
      "content": "完成前端登录模块开发",
      "assignee": "李四",
      "deadline": "2026-08-05 00:00",
      "priority": "中"
    },
    {
      "content": "提供支付接口文档（阻塞前端进度，需优先处理）",
      "assignee": "王五",
      "deadline": "2026-08-01 15:00",
      "priority": "高"
    },
    {
      "content": "处理线上bug",
      "assignee": "王五",
      "deadline": "2026-08-01 00:00",
      "priority": "高"
    },
    {
      "content": "开始第一轮压测",
      "assignee": "赵六",
      "deadline": "2026-08-10 00:00",
      "priority": "中"
    },
    {
      "content": "输出压测报告",
      "assignee": "赵六",
      "deadline": "2026-08-15 00:00",
      "priority": "中"
    },
    {
      "content": "用户反馈优化需求",
      "assignee": null,
      "deadline": null,
      "priority": "低"
    }
  ],
  "key_time_points": [
    {
      "title": "支付接口文档交付",
      "datetime": "2026-08-01 15:00",
      "description": "王五需在明天下午3点前完成，阻塞前端支付模块"
    },
    {
      "title": "前端登录模块完成",
      "datetime": "2026-08-05 00:00",
      "description": "李四负责"
    },
    {
      "title": "第一轮压测开始",
      "datetime": "2026-08-10 00:00",
      "description": "赵六负责"
    },
    {
      "title": "压测报告输出",
      "datetime": "2026-08-15 00:00",
      "description": null
    },
    {
      "title": "正式上线",
      "datetime": "2026-08-20 00:00",
      "description": "Q3产品正式上线日期"
    }
  ],
  "next_meeting": "2026-08-07 14:00"
}"""


def build_messages(transcript: str, meeting_title: str | None = None) -> list[dict]:
    """构建发送给大模型的消息列表"""
    user_prompt = f"请分析以下会议转写文本：\n\n{transcript}"
    if meeting_title:
        user_prompt += f"\n\n（会议标题已指定为：{meeting_title}）"

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": FEW_SHOT_EXAMPLE_USER},
        {"role": "assistant", "content": FEW_SHOT_EXAMPLE_ASSISTANT},
        {"role": "user", "content": user_prompt},
    ]