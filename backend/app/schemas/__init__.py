"""Pydantic schemas 统一导出"""

from app.schemas.user import UserCreate, UserOut
from app.schemas.machine import MachineCreate, MachineOut
from app.schemas.material import MaterialCreate, MaterialOut
from app.schemas.tool import ToolCreate, ToolOut
from app.schemas.job_record import JobRecordCreate, JobRecordOut

__all__ = [
    "UserCreate", "UserOut",
    "MachineCreate", "MachineOut",
    "MaterialCreate", "MaterialOut",
    "ToolCreate", "ToolOut",
    "JobRecordCreate", "JobRecordOut",
]
