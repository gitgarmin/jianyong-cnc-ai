"""JobRecord Pydantic schemas — 输入校验与输出序列化"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class JobRecordCreate(BaseModel):
    """创建加工任务请求"""

    part_name: str = Field(..., min_length=1, max_length=256, description="零件名称")
    machine_id: int | None = Field(None, description="机床 ID")
    material_id: int | None = Field(None, description="材料 ID")
    tool_id: int | None = Field(None, description="刀具 ID")


class JobRecordOut(BaseModel):
    """加工任务输出"""

    id: int
    user_id: int | None = None
    machine_id: int | None = None
    material_id: int | None = None
    tool_id: int | None = None
    part_name: str
    drawing_path: str | None = None
    gcode_text: str | None = None
    status: str = "draft"
    validation_result: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
