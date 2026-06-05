"""AI Provider 抽象层 — 支持 DeepSeek + 本地模型切换"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class VisionResult:
    """图纸解析结果"""

    raw_text: str
    structured_data: dict[str, Any]
    confidence_scores: dict[str, float]


@dataclass
class ChatResult:
    """对话结果 — 除了回复文本外，也可携带 token 用量"""

    reply: str
    token_usage: dict[str, int] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ProviderError(Exception):
    """AI Provider 通用异常"""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ProviderAuthError(ProviderError):
    """401 — API Key 无效或未配置"""


class ProviderRateLimitError(ProviderError):
    """429 — 速率限制"""


class ProviderTimeoutError(ProviderError):
    """请求超时"""


# ---------------------------------------------------------------------------
# Abstract provider
# ---------------------------------------------------------------------------


class AIProvider(ABC):
    """AI Provider 抽象接口 — 支持 DeepSeek + 本地模型切换"""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, Any]],
        system: str | None = None,
    ) -> str:
        """发送对话消息，返回回答文本"""
        ...

    @abstractmethod
    async def vision_analyze(self, image_bytes: bytes, prompt: str) -> VisionResult:
        """分析图片（图纸），返回结构化解析结果"""
        ...


# ---------------------------------------------------------------------------
# DeepSeek provider (OpenAI-compatible)
# ---------------------------------------------------------------------------


class DeepSeekProvider(AIProvider):
    """DeepSeek API — OpenAI 兼容接口"""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    # -- helpers -------------------------------------------------------------

    @property
    def client(self) -> httpx.AsyncClient:
        """延迟初始化 httpx client（复用连接池）"""
        if self._client is None:
            if not settings.DEEPSEEK_API_KEY:
                raise ProviderAuthError(
                    "DEEPSEEK_API_KEY 未配置。请在 .env 文件中设置 "
                    "DEEPSEEK_API_KEY=sk-...",
                    status_code=401,
                )

            self._client = httpx.AsyncClient(
                base_url=settings.DEEPSEEK_API_BASE,
                headers={
                    "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(30.0, connect=10.0),
            )

        return self._client

    async def close(self) -> None:
        """关闭连接池（应用退出时调用）"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def _build_system_message(self, system: str | None) -> str:
        """构造系统提示词 — 设定数控 AI 助理的领域知识边界"""
        base = (
            "你是简用数控AI大师，一个专为汽摩配、精密部件加工行业打造的数控编程助手。"
            "你的用户是22-26岁、有机床操作基础但缺乏编程经验的大专/本科毕业生。"
            "请用通俗易懂的中文回答，必要时给出具体的参数建议（进给、转速、切深等）。"
            "如果你不确定某个参数，请诚实告知并建议用户向有经验的老师傅确认。"
            "永远不要在回答中给出可能造成撞刀或人身伤害的代码。"
        )

        if system:
            return f"{base}\n\n{system}"

        return base

    @staticmethod
    def _convert_messages(
        messages: list[dict[str, Any]],
        system_prompt: str,
    ) -> list[dict[str, str]]:
        """将对话历史转换为 OpenAI 兼容格式"""
        converted: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if isinstance(content, list):
                # 多模态消息（文字 + 图片）
                converted.append({"role": role, "content": content})
            else:
                converted.append({"role": role, "content": str(content)})

        return converted

    # -- public API ----------------------------------------------------------

    async def chat(
        self,
        messages: list[dict[str, Any]],
        system: str | None = None,
    ) -> str:
        """调用 DeepSeek Chat Completion

        Raises:
            ProviderAuthError: API Key 无效
            ProviderRateLimitError: 速率限制
            ProviderTimeoutError: 请求超时
            ProviderError: 其他 API 错误
        """
        system_prompt = self._build_system_message(system)
        body = {
            "model": settings.DEEPSEEK_MODEL,
            "messages": self._convert_messages(messages, system_prompt),
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream": False,
        }

        try:
            response = await self.client.post(
                f"{settings.DEEPSEEK_API_BASE}/chat/completions",
                json=body,
            )
        except httpx.TimeoutException:
            raise ProviderTimeoutError("DeepSeek API 响应超时，请重试") from None
        except httpx.ConnectError:
            raise ProviderError("无法连接到 DeepSeek API，请检查网络") from None

        # -- HTTP 错误处理 ----------------------------------------------------
        if response.status_code == 401:
            raise ProviderAuthError(
                "DeepSeek API Key 无效或已过期，请检查 .env 文件中的 DEEPSEEK_API_KEY",
                status_code=401,
            )
        if response.status_code == 429:
            raise ProviderRateLimitError(
                "DeepSeek API 请求频率过高，请稍后重试",
                status_code=429,
            )
        if response.status_code >= 500:
            raise ProviderError(
                f"DeepSeek 服务暂时不可用 (HTTP {response.status_code})",
                status_code=response.status_code,
            )
        if not response.is_success:
            raise ProviderError(
                f"DeepSeek API 返回错误 (HTTP {response.status_code}): "
                f"{response.text[:500]}",
                status_code=response.status_code,
            )

        # -- 解析响应 ---------------------------------------------------------
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise ProviderError("DeepSeek API 返回了无法解析的响应")

        choices: list[dict[str, Any]] = data.get("choices", [])
        if not choices:
            raise ProviderError("DeepSeek API 未返回任何内容")

        message: dict[str, Any] = choices[0].get("message", {})
        content: str = message.get("content", "")

        if not content:
            raise ProviderError("DeepSeek API 返回了空回复")

        # 记录 token 用量（方便后续计费）
        usage = data.get("usage", {})
        if usage:
            logger.info(
                "DeepSeek token usage: prompt=%s, completion=%s, total=%s",
                usage.get("prompt_tokens"),
                usage.get("completion_tokens"),
                usage.get("total_tokens"),
            )

        return content

    async def chat_with_result(
        self,
        messages: list[dict[str, Any]],
        system: str | None = None,
    ) -> ChatResult:
        """调用 chat 并返回含 token 用量的结构化结果"""
        reply = await self.chat(messages, system)

        return ChatResult(reply=reply)

    # -- vision --------------------------------------------------------------

    async def vision_analyze(self, image_bytes: bytes, prompt: str) -> VisionResult:
        # TODO: Phase 1 实现 DeepSeek Vision 调用
        raise NotImplementedError("DeepSeek Vision 待实现")


# ---------------------------------------------------------------------------
# Local fallback
# ---------------------------------------------------------------------------


class LocalProvider(AIProvider):
    """本地模型（ollama / Qwen），支持离线/内网场景"""

    async def chat(
        self,
        messages: list[dict[str, Any]],
        system: str | None = None,
    ) -> str:
        raise NotImplementedError("本地模型待实现")

    async def vision_analyze(self, image_bytes: bytes, prompt: str) -> VisionResult:
        raise NotImplementedError("本地视觉模型待实现")


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_provider: AIProvider | None = None


def get_ai_provider() -> AIProvider:
    """工厂函数 — 按配置返回 AIProvider 单例"""
    global _provider

    if _provider is not None:
        return _provider

    match settings.AI_PROVIDER:
        case "deepseek":
            _provider = DeepSeekProvider()
        case "local":
            _provider = LocalProvider()
        case _:
            raise ValueError(f"Unknown AI_PROVIDER: {settings.AI_PROVIDER}")

    return _provider
