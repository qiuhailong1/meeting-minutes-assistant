from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class PriorityLevel(str, Enum):
    high = "高"
    medium = "中"
    low = "低"


class ActionItem(BaseModel):
    """待办事项"""
    content: str = Field(..., description="待办内容")
    assignee: Optional[str] = Field(None, description="负责人")
    deadline: Optional[str] = Field(None, description="截止时间，格式 YYYY-MM-DD HH:mm")
    priority: PriorityLevel = Field(..., description="优先级：高/中/低")


class KeyTimePoint(BaseModel):
    """关键时间节点"""
    title: str = Field(..., description="节点名称")
    datetime: str = Field(..., description="时间，格式 YYYY-MM-DD HH:mm")
    description: Optional[str] = Field(None, description="补充说明")


class MeetingMinutes(BaseModel):
    """会议纪要结构化输出 —— 大模型必须返回此 Schema"""
    title: str = Field(..., description="会议标题")
    date: str = Field(..., description="会议日期，格式 YYYY-MM-DD")
    participants: list[str] = Field(default_factory=list, description="参会人员")
    summary: str = Field(..., description="会议摘要，不超过 300 字")
    key_points: list[str] = Field(default_factory=list, description="核心要点")
    action_items: list[ActionItem] = Field(default_factory=list, description="待办事项列表")
    key_time_points: list[KeyTimePoint] = Field(default_factory=list, description="关键时间节点")
    next_meeting: Optional[str] = Field(None, description="下次会议时间，格式 YYYY-MM-DD HH:mm")


class MinutesRequest(BaseModel):
    """API 请求体"""
    transcript: str = Field(..., min_length=10, description="会议录音转写文本")
    meeting_title: Optional[str] = Field(None, description="会议标题（可选，不填则自动提取）")


class MinutesResponse(BaseModel):
    """API 响应体"""
    success: bool
    data: Optional[MeetingMinutes] = None
    error: Optional[str] = None
    ics_url: Optional[str] = Field(None, description="日历文件下载地址")