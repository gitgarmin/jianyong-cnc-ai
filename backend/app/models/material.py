"""工件材料 ORM 模型"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Float, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.job_record import JobRecord


class Material(Base):
    """工件材料表 — 材料牌号、硬度、参考切削速度等"""

    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    grade: Mapped[str | None] = mapped_column(String(64), nullable=True, comment="牌号，如 45 / 6061 / 304")
    hardness: Mapped[str | None] = mapped_column(String(32), nullable=True, comment="硬度，如 HRC20-25")
    density: Mapped[float | None] = mapped_column(Float, nullable=True, comment="密度 g/cm3")
    cutting_speed_ref: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="参考切削速度 m/min"
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

    # 关联：一种材料被多个任务使用
    job_records: Mapped[list[JobRecord]] = relationship(
        "JobRecord", back_populates="material"
    )

    def __repr__(self) -> str:
        return f"<Material id={self.id} name={self.name!r} grade={self.grade!r}>"
