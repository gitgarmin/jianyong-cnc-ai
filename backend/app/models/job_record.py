"""加工任务记录 ORM 模型"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.machine import Machine
    from app.models.material import Material
    from app.models.tool import Tool


class JobRecord(Base):
    """加工任务记录 — 关联用户、机床、材料、刀具，保存 G 代码及校验结果"""

    __tablename__ = "job_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    machine_id: Mapped[int | None] = mapped_column(ForeignKey("machines.id"), nullable=True, index=True)
    material_id: Mapped[int | None] = mapped_column(ForeignKey("materials.id"), nullable=True, index=True)
    tool_id: Mapped[int | None] = mapped_column(ForeignKey("tools.id"), nullable=True, index=True)

    part_name: Mapped[str] = mapped_column(String(256), nullable=False)
    drawing_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    gcode_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft",
        comment="任务状态：draft / parsed / generated / validated / completed / failed",
    )
    validation_result: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="校验结果 JSON 字符串"
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # 关联
    user: Mapped[User | None] = relationship("User", back_populates="job_records")
    machine: Mapped[Machine | None] = relationship("Machine", back_populates="job_records")
    material: Mapped[Material | None] = relationship("Material", back_populates="job_records")
    tool: Mapped[Tool | None] = relationship("Tool", back_populates="job_records")

    def __repr__(self) -> str:
        return f"<JobRecord id={self.id} part_name={self.part_name!r} status={self.status!r}>"
