"""刀具 ORM 模型 — 含批次追踪与寿命管理"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.job_record import JobRecord


class Tool(Base):
    """刀具表 — 记录刀具规格、批次、累计切削长度，支持寿命到期提醒"""

    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    tool_type: Mapped[str] = mapped_column(
        String(32), nullable=False,
        comment="刀具类型：end_mill / drill / turning / boring / tap 等",
    )
    spec: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="规格，如 D10 / CNMG120408")
    batch_no: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="批次号")
    total_cut_length: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0, comment="累计切削长度（mm）"
    )
    max_cut_length: Mapped[float] = mapped_column(
        Float, nullable=False, default=50000.0, comment="最大切削长度阈值（mm）"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
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

    # 关联：一把刀具被多个任务使用
    job_records: Mapped[list[JobRecord]] = relationship(
        "JobRecord", back_populates="tool"
    )

    @property
    def remaining_length(self) -> float:
        """剩余可用切削长度"""
        return max(self.max_cut_length - self.total_cut_length, 0.0)

    @property
    def life_usage_percent(self) -> float:
        """已使用寿命百分比"""
        if self.max_cut_length <= 0:
            return 100.0
        return min(self.total_cut_length / self.max_cut_length * 100, 100.0)

    def __repr__(self) -> str:
        return f"<Tool id={self.id} name={self.name!r} type={self.tool_type!r}>"
