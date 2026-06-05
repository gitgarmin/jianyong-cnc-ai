from abc import ABC, abstractmethod
from dataclasses import dataclass
from app.core.config import settings


@dataclass
class VisionResult:
    """图纸解析结果"""
    raw_text: str
    structured_data: dict
    confidence_scores: dict


class AIProvider(ABC):
    """AI Provider 抽象接口 — 支持 DeepSeek + 本地模型切换"""

    @abstractmethod
    async def chat(self, messages: list[dict], system: str | None = None) -> str:
        """发送对话消息，返回回答文本"""
        ...

    @abstractmethod
    async def vision_analyze(self, image_bytes: bytes, prompt: str) -> VisionResult:
        """分析图片（图纸），返回结构化解析结果"""
        ...


class DeepSeekProvider(AIProvider):
    """DeepSeek API 实现"""

    async def chat(self, messages: list[dict], system: str | None = None) -> str:
        # TODO: 实现 DeepSeek API 调用
        raise NotImplementedError("DeepSeek API 待实现")

    async def vision_analyze(self, image_bytes: bytes, prompt: str) -> VisionResult:
        # TODO: 实现 DeepSeek Vision 调用
        raise NotImplementedError("DeepSeek Vision 待实现")


class LocalProvider(AIProvider):
    """本地模型（ollama/Qwen），支持离线/内网场景"""

    async def chat(self, messages: list[dict], system: str | None = None) -> str:
        raise NotImplementedError("本地模型待实现")

    async def vision_analyze(self, image_bytes: bytes, prompt: str) -> VisionResult:
        raise NotImplementedError("本地视觉模型待实现")


def get_ai_provider() -> AIProvider:
    """工厂函数：根据配置返回对应的 AI Provider 实例"""
    match settings.AI_PROVIDER:
        case "deepseek":
            return DeepSeekProvider()
        case "local":
            return LocalProvider()
        case _:
            raise ValueError(f"Unknown AI_PROVIDER: {settings.AI_PROVIDER}")
