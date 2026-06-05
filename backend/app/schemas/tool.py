"""Tool Pydantic schemas — 输入校验与输出序列化"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

# 支持的刀具类型
VALID_TOOL_TYPES = {"end_mill", "drill", "turning", "boring", "tap", "reamer", "insert"}


class ToolCreate(BaseModel):
    """创建刀具请求"""

    name: str = Field(..., min_length=1, max_length=128, description="刀具名称")
    tool_type: str = Field(..., description="刀具类型")
    spec: str | None = Field(None, max_length=64, description="规格，如 D10")
    batch_no: str | None = Field(None, max_length=64, description="批次号")
    max_cut_length: float = Field(default=50000.0, ge=0, description="最大切削长度（mm）")

    def model_post_init(self, __context: object) -> None:
        if self.tool_type not in VALID_TOOL_TYPES:
            from pydantic import ValidationError
            raise ValueError(
                f"tool_type 必须是 {VALID_TOOL_TYPES} 之一，收到: {self.tool_type}"
            )


class ToolOut(BaseModel):
    """刀具输出"""

    id: int
    name: str
    tool_type: str
    spec: str | None = None
    batch_no: str | None = None
    total_cut_length: float = 0.0
    max_cut_length: float = 50000.0
    is_active: bool = True
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
