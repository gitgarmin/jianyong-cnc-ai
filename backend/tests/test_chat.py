"""对话问答 API 测试 — mock DeepSeek 调用"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.ai_provider import (
    DeepSeekProvider,
    ProviderAuthError,
    ProviderError,
    ProviderRateLimitError,
)


# ---------------------------------------------------------------------------
# Unit tests — DeepSeekProvider
# ---------------------------------------------------------------------------


class TestDeepSeekProvider:
    """DeepSeekProvider 单元测试（mock httpx）"""

    @pytest.fixture
    def provider(self):
        """需要 API Key 才能创建 provider"""
        return DeepSeekProvider()

    @pytest.mark.asyncio
    async def test_chat_success(self, provider: DeepSeekProvider):
        """正常调用返回 AI 回复"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json = lambda: {  # type: ignore[assignment]
            "choices": [
                {"message": {"role": "assistant", "content": "建议将转速调至 S1200"}}
            ],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        }

        provider._client = AsyncMock()
        provider._client.post.return_value = mock_response
        provider._client.headers = {}

        result = await provider.chat(
            messages=[{"role": "user", "content": "工件有振纹怎么调？"}],
        )

        assert "S1200" in result

    @pytest.mark.asyncio
    async def test_chat_auth_error(self, provider: DeepSeekProvider):
        """API Key 无效抛出 ProviderAuthError"""
        mock_response = AsyncMock()
        mock_response.status_code = 401
        mock_response.is_success = False

        provider._client = AsyncMock()
        provider._client.post.return_value = mock_response
        provider._client.headers = {}

        with pytest.raises(ProviderAuthError):
            await provider.chat(messages=[{"role": "user", "content": "test"}])

    @pytest.mark.asyncio
    async def test_chat_rate_limit(self, provider: DeepSeekProvider):
        """速率限制抛出 ProviderRateLimitError"""
        mock_response = AsyncMock()
        mock_response.status_code = 429
        mock_response.is_success = False

        provider._client = AsyncMock()
        provider._client.post.return_value = mock_response
        provider._client.headers = {}

        with pytest.raises(ProviderRateLimitError):
            await provider.chat(messages=[{"role": "user", "content": "test"}])

    @pytest.mark.asyncio
    async def test_chat_server_error(self, provider: DeepSeekProvider):
        """500 错误抛出 ProviderError"""
        mock_response = AsyncMock()
        mock_response.status_code = 500
        mock_response.is_success = False

        provider._client = AsyncMock()
        provider._client.post.return_value = mock_response
        provider._client.headers = {}

        with pytest.raises(ProviderError):
            await provider.chat(messages=[{"role": "user", "content": "test"}])

    @pytest.mark.asyncio
    async def test_chat_empty_choices(self, provider: DeepSeekProvider):
        """空 choices 抛出 ProviderError"""
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json = lambda: {"choices": []}  # type: ignore[assignment]

        provider._client = AsyncMock()
        provider._client.post.return_value = mock_response
        provider._client.headers = {}

        with pytest.raises(ProviderError, match="未返回任何内容"):
            await provider.chat(messages=[{"role": "user", "content": "test"}])

    @pytest.mark.asyncio
    async def test_build_system_message(self, provider: DeepSeekProvider):
        """系统提示词包含数控领域设定"""
        system = provider._build_system_message(None)
        assert "简用数控AI大师" in system
        assert "撞刀" in system

    @pytest.mark.asyncio
    async def test_build_system_message_with_context(self, provider: DeepSeekProvider):
        """自定义 system prompt 追加到基础提示词之后"""
        system = provider._build_system_message("当前材料为 45#钢")
        assert "45#钢" in system
        assert "撞刀" in system  # 基础提示词仍然存在

    @pytest.mark.asyncio
    async def test_convert_messages(self, provider: DeepSeekProvider):
        """消息格式转换为 OpenAI 兼容"""
        converted = DeepSeekProvider._convert_messages(
            messages=[{"role": "user", "content": "hello"}],
            system_prompt="test system",
        )

        assert converted[0] == {"role": "system", "content": "test system"}
        assert converted[1] == {"role": "user", "content": "hello"}


# ---------------------------------------------------------------------------
# Integration tests — /api/chat/send
# ---------------------------------------------------------------------------


class TestChatAPI:
    """端到端 API 测试（mock AIProvider）"""

    @pytest.fixture
    def client(self):
        """Async test client"""
        transport = ASGITransport(app=app)
        return AsyncClient(transport=transport, base_url="http://test")

    @pytest.mark.asyncio
    async def test_send_success(self, client: AsyncClient):
        """正常请求返回 AI 回复"""
        with patch("app.api.chat.get_ai_provider") as mock_get:
            mock_provider = AsyncMock()
            mock_provider.chat.return_value = "建议将转速调整至 S1200"
            mock_get.return_value = mock_provider

            response = await client.post(
                "/api/chat/send",
                json={"message": "45#钢外圆粗车参数"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["reply"] == "建议将转速调整至 S1200"
        assert data["sources"] == []
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_send_with_context(self, client: AsyncClient):
        """G代码跨Tab上下文注入"""
        with patch("app.api.chat.get_ai_provider") as mock_get:
            mock_provider = AsyncMock()
            mock_provider.chat.return_value = "对于 FANUC 0i-TF，建议使用 G71 粗车循环"
            mock_get.return_value = mock_provider

            response = await client.post(
                "/api/chat/send",
                json={
                    "message": "推荐切削参数",
                    "context": {
                        "material": "45#钢",
                        "machine": "FANUC 0i-TF",
                        "part_type": "轴类",
                    },
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "G71" in data["reply"]

    @pytest.mark.asyncio
    async def test_send_empty_message_rejected(self, client: AsyncClient):
        """空消息被 Pydantic 校验拒绝"""
        response = await client.post("/api/chat/send", json={"message": ""})

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_send_auth_error_graceful(self, client: AsyncClient):
        """API Key 错误时返回友好提示而非 500"""
        with patch("app.api.chat.get_ai_provider") as mock_get:
            mock_provider = AsyncMock()
            mock_provider.chat.side_effect = ProviderAuthError("bad key")
            mock_get.return_value = mock_provider

            response = await client.post(
                "/api/chat/send",
                json={"message": "test"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "密钥" in data["reply"]

    @pytest.mark.asyncio
    async def test_send_with_history(self, client: AsyncClient):
        """多轮对话历史传入"""
        with patch("app.api.chat.get_ai_provider") as mock_get:
            mock_provider = AsyncMock()
            mock_provider.chat.return_value = "这是第二轮回复"
            mock_get.return_value = mock_provider

            response = await client.post(
                "/api/chat/send",
                json={
                    "message": "好，数量改成200件",
                    "history": [
                        {"role": "user", "content": "首件检验有哪些关键尺寸？"},
                        {"role": "assistant", "content": "请先提供图纸尺寸信息。"},
                    ],
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["reply"] == "这是第二轮回复"
