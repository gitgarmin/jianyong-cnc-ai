"""机床 ORM 模型"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.job_record import JobRecord


class Machine(Base):
    """机床表 — 记录数控机床及其数控系统类型"""

    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    cnc_system: Mapped[str] = mapped_column(String(32), nullable=False, default="FANUC")
    brand: Mapped[str | None] = mapped_column(String(64), nullable=True)
    model_no: Mapped[str | None] = mapped_column(String(64), nullable=True)
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

    # 关联：一台机床被多个任务使用
    job_records: Mapped[list[JobRecord]] = relationship(
        "JobRecord", back_populates="machine"
    )

    def __repr__(self) -> str:
        return f"<Machine id={self.id} name={self.name!r} cnc_system={self.cnc_system!r}>"
