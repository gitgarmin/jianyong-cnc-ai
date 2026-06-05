"""Machine Pydantic schemas — 输入校验与输出序列化"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

# 支持的数控系统列表
VALID_CNC_SYSTEMS = {"FANUC", "Siemens", "Haas", "GSK", "Mitsubishi"}


class MachineCreate(BaseModel):
    """创建机床请求"""

    name: str = Field(..., min_length=1, max_length=128, description="机床名称")
    cnc_system: str = Field(default="FANUC", description="数控系统")
    brand: str | None = Field(None, max_length=64, description="品牌")
    model_no: str | None = Field(None, max_length=64, description="型号")

    def model_post_init(self, __context: object) -> None:
        if self.cnc_system not in VALID_CNC_SYSTEMS:
            from pydantic import ValidationError
            raise ValueError(
                f"cnc_system 必须是 {VALID_CNC_SYSTEMS} 之一，收到: {self.cnc_system}"
            )


class MachineOut(BaseModel):
    """机床输出"""

    id: int
    name: str
    cnc_system: str
    brand: str | None = None
    model_no: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
