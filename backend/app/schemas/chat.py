"""对话问答 API — Pydantic schemas"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class Source(BaseModel):
    """知识库来源引用"""

    document: str = Field(..., description="文档名，如 '45#钢切削参数手册'")
    section: str | None = Field(None, description="段落/章节")
    snippet: str | None = Field(None, description="引用的原文片段")


class ChatMessage(BaseModel):
    """单条对话消息"""

    role: str = Field(..., pattern=r"^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    """对话请求"""

    message: str = Field(..., min_length=1, description="用户输入的消息")
    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=50,
        description="最近的对话历史（最多50条）",
    )
    image: str | None = Field(
        None,
        description="可选：base64 编码的图片，用于工件表面/切屑/机床面板等视觉分析",
    )
    context: dict[str, Any] | None = Field(
        None,
        description="可选的工件上下文，从G代码Tab注入（材料/机床/零件类型）",
    )


class ChatResponse(BaseModel):
    """对话响应"""

    reply: str = Field(..., description="AI 回答文本")
    sources: list[Source] = Field(
        default_factory=list,
        description="RAG 知识库引用列表（MVP阶段为空，Phase 1 实现）",
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
