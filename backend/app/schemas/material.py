"""Material Pydantic schemas — 输入校验与输出序列化"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class MaterialCreate(BaseModel):
    """创建材料请求"""

    name: str = Field(..., min_length=1, max_length=128, description="材料名称，如 45#钢")
    grade: str | None = Field(None, max_length=64, description="牌号")
    hardness: str | None = Field(None, max_length=32, description="硬度")
    density: float | None = Field(None, ge=0, description="密度 g/cm3")
    cutting_speed_ref: float | None = Field(None, description="参考切削速度 m/min")

    @model_validator(mode="after")
    def validate_cutting_speed(self) -> MaterialCreate:
        if self.cutting_speed_ref is not None and self.cutting_speed_ref < 0:
            raise ValueError("cutting_speed_ref 不能为负数")
        return self


class MaterialOut(BaseModel):
    """材料输出"""

    id: int
    name: str
    grade: str | None = None
    hardness: str | None = None
    density: float | None = None
    cutting_speed_ref: float | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
