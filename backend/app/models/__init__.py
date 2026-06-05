"""ORM 模型统一导出"""

from app.models.user import User
from app.models.machine import Machine
from app.models.material import Material
from app.models.tool import Tool
from app.models.job_record import JobRecord

__all__ = ["User", "Machine", "Material", "Tool", "JobRecord"]
