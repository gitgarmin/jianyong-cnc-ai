"""图纸解析 Provider 抽象 — 支持多引擎切换（DeepSeek Vision / 百度 OCR / 人工标注兜底）"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class DrawingParseResult:
    """图纸解析结果"""
    # 毛坯/成品通用字段
    part_type: str | None = None          # 轴类/盘类/套类/支架类
    outer_diameter: float | None = None   # 外径 mm
    inner_diameter: float | None = None   # 内径 mm
    length: float | None = None           # 长度 mm

    # 成品图纸额外字段
    tolerances: list[dict] | None = None       # [{"dim": "φ50", "upper": 0.02, "lower": -0.02}, ...]
    surface_roughness: list[str] | None = None  # ["Ra 0.8", "Ra 3.2", ...]
    gd_t: list[str] | None = None               # ["同轴度 φ0.02", "垂直度 0.01", ...]
    features: list[str] | None = None           # ["M20×2.0", "C1", "槽宽3mm", ...]

    # 毛坯图纸额外字段
    blank_type: str | None = None          # 棒料/锻件/铸件/板料

    # 置信度
    confidence_scores: dict[str, float] | None = None  # {"outer_diameter": 0.92, ...}

    # 错误
    errors: list[str] | None = None


class DrawingParser(ABC):
    """图纸解析 Provider 抽象接口"""

    @abstractmethod
    async def parse(self, image_bytes: bytes, drawing_type: str = "finished") -> DrawingParseResult:
        """解析单张图纸"""
        ...
