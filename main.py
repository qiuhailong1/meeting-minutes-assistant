import json
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
import httpx

from schemas import MinutesRequest, MinutesResponse, MeetingMinutes
from prompts import build_messages
from calendar_utils import generate_ics, generate_markdown_table

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

app = FastAPI(title="AI会议纪要智能助手", version="1.0.0")

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

_API_KEY = os.getenv("LLM_API_KEY", "").strip()
_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com").strip()
MODEL = os.getenv("LLM_MODEL", "deepseek-chat").strip()
_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))

if not _API_KEY:
    import warnings
    warnings.warn("LLM_API_KEY 未配置，请在 .env 文件中填入有效的 API Key")

_http_client = httpx.Client(transport=httpx.HTTPTransport(proxy=None), timeout=_TIMEOUT, follow_redirects=True)
client = OpenAI(
    api_key=_API_KEY,
    base_url=_BASE_URL,
    timeout=_TIMEOUT,
    http_client=_http_client,
)


@app.post("/api/minutes", response_model=MinutesResponse)
async def generate_minutes(req: MinutesRequest):
    """生成会议纪要 + 日历文件"""
    try:
        # 1. 调用大模型
        messages = build_messages(req.transcript, req.meeting_title)
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content.strip()
        data = json.loads(raw)

        # 2. Pydantic 校验
        minutes = MeetingMinutes(**data)

        # 3. 生成 .ics 日历文件
        ics_path = generate_ics(minutes)
        ics_url = f"/static/{os.path.basename(ics_path)}"

        return MinutesResponse(
            success=True,
            data=minutes,
            ics_url=ics_url,
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="大模型返回格式异常，请重试")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/{filename}")
async def download_ics(filename: str):
    """下载 .ics 日历文件"""
    filepath = os.path.join("static", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(
        filepath,
        media_type="text/calendar",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.get("/", response_class=HTMLResponse)
async def index():
    """前端测试页面"""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)