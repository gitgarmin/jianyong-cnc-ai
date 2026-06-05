"""User Pydantic schemas — 输入校验与输出序列化"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """创建用户请求"""

    username: str = Field(..., min_length=3, max_length=64, description="用户名，3-64 字符")
    password: str = Field(..., min_length=8, max_length=128, description="密码，至少 8 位")
    role: str = Field(default="operator", pattern=r"^(operator|supervisor|admin)$")


class UserOut(BaseModel):
    """用户输出（不包含密码）"""

    id: int
    username: str
    role: str
    is_active: bool
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
