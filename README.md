# AI 会议纪要智能助手

> 上传会议录音转写文本 → AI 自动生成结构化纪要 + 优先级待办 + 一键下载日历文件

## 功能特性

- **结构化输出**：基于 Pydantic 严格 Schema，强制大模型返回标准 JSON，杜绝格式解析错误
- **智能待办分级**：Few-shot Prompt 引导模型按关键词（紧急/阻塞/截止）自动划分高/中/低三级
- **日历文件自动生成**：提取时间节点调用 ics 库生成 `.ics` 文件，支持导入手机/Outlook
- **无状态 API**：每次请求独立处理，不维护对话历史，降低并发风险

## 技术栈

| 层级 | 技术 |
|------|------|
| Web 框架 | FastAPI + Uvicorn |
| 大模型 | OpenAI SDK（兼容通义千问/DeepSeek/OpenAI） |
| 数据校验 | Pydantic v2 |
| 日历生成 | ics |
| 前端 | 原生 HTML/CSS/JS |

## 项目结构

```
meeting-minutes-assistant/
├── main.py              # FastAPI 入口，路由 + LLM 调用
├── schemas.py           # Pydantic 严格 Schema 定义
├── prompts.py           # Few-shot 分级 Prompt + 消息构建
├── calendar_utils.py    # .ics 生成 + Markdown 表格
├── requirements.txt     # 依赖清单
├── .env.example         # 环境变量模板
└── static/
    └── index.html       # 前端测试页面
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

复制 `.env.example` 为 `.env`，填入你的 API Key：

```bash
copy .env.example .env
```

支持三家服务商（任选其一）：

```env
# 通义千问
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus

# DeepSeek
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat

# OpenAI
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

### 3. 启动服务

```bash
python main.py
```

浏览器访问 `http://localhost:8000`，点击「填入示例」→「生成纪要」即可体验。

## API 接口

### POST /api/minutes

生成会议纪要 + 日历文件。

**请求体：**

```json
{
  "transcript": "会议录音转写文本...",
  "meeting_title": "会议标题（可选）"
}
```

**响应体：**

```json
{
  "success": true,
  "data": {
    "title": "会议标题",
    "date": "2026-07-31",
    "participants": ["张三", "李四"],
    "summary": "会议摘要",
    "key_points": ["核心要点1", "核心要点2"],
    "action_items": [
      {
        "content": "待办事项",
        "assignee": "负责人",
        "deadline": "2026-08-01 15:00",
        "priority": "高"
      }
    ],
    "key_time_points": [
      {
        "title": "节点名称",
        "datetime": "2026-08-20 00:00",
        "description": "补充说明"
      }
    ],
    "next_meeting": "2026-08-07 14:00"
  },
  "ics_url": "/static/meeting_xxx.ics"
}
```

### GET /api/download/{filename}

下载 `.ics` 日历文件，可直接导入手机/Outook 日历。

## 优先级判定规则

| 级别 | 关键词 | 场景 |
|------|--------|------|
| 🔴 高 | 紧急、阻塞、截止、立刻、马上 | 线上事故/延期风险 |
| 🟡 中 | 本周内完成 | 有明确时间要求但非紧急 |
| 🟢 低 | 有空再做、优化类 | 无明确截止日期 |

## License

MIT
