"""对话问答 API — 基于 RAG 的行业知识库问答"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from app.schemas.chat import ChatRequest, ChatResponse, Source
from app.services.ai_provider import (
    ProviderAuthError,
    ProviderError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    get_ai_provider,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _build_context_prompt(context: dict | None) -> str | None:
    """将工件上下文注入 system prompt"""
    if not context:
        return None

    parts = []
    material = context.get("material")
    machine = context.get("machine")
    part_type = context.get("part_type")

    if material:
        parts.append(f"当前加工材料为 {material}")
    if part_type:
        parts.append(f"零件类型为 {part_type}")
    if machine:
        parts.append(f"使用机床为 {machine}")

    if not parts:
        return None

    return "；".join(parts) + "。请基于此上下文回答问题。"


@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest) -> ChatResponse:
    """发送对话消息，返回 AI 回答

    - 支持文字 + 可选图片（base64）
    - 支持从 G 代码 Tab 注入的工件上下文
    - 支持多轮对话历史（最多 50 条）
    - 响应时间目标 ≤ 3s
    """
    provider = get_ai_provider()

    # 构建消息列表
    messages = [{"role": msg.role, "content": msg.content} for msg in request.history]

    # 当前用户消息（可能含图片）
    user_content: str | list[dict] = request.message
    if request.image:
        user_content = [
            {"type": "text", "text": request.message},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{request.image}"},
            },
        ]

    messages.append({"role": "user", "content": user_content})

    # 上下文注入
    system_override = _build_context_prompt(request.context)

    try:
        reply = await provider.chat(messages, system=system_override)
    except ProviderAuthError:
        logger.error("DeepSeek API Key 无效")
        return ChatResponse(
            reply="AI 服务未配置或密钥无效。请联系管理员配置 DeepSeek API Key。",
            sources=[],
        )
    except ProviderRateLimitError:
        logger.warning("DeepSeek API 速率限制")
        return ChatResponse(
            reply="当前使用人数较多，请稍后重试。如频繁遇到此问题，请联系管理员。",
            sources=[],
        )
    except ProviderTimeoutError:
        logger.error("DeepSeek API 超时")
        return ChatResponse(
            reply="AI 服务响应较慢，请稍后重试或简化您的问题。",
            sources=[],
        )
    except ProviderError as exc:
        logger.error("DeepSeek API 错误: %s", exc)
        return ChatResponse(
            reply=f"AI 服务暂时不可用。{exc}",
            sources=[],
        )

    # TODO: Phase 1 — RAG 检索 + 来源引用
    sources: list[Source] = []

    return ChatResponse(reply=reply, sources=sources)
