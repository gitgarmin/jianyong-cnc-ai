"""B05 ORM 模型单元测试 — User / Machine / Material / Tool / JobRecord

测试分两大部分：
  1. ORM 模型：字段约束、关联关系、表结构
  2. Pydantic Schema：序列化/反序列化、字段校验
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base
from app.models.user import User
from app.models.machine import Machine
from app.models.material import Material
from app.models.tool import Tool
from app.models.job_record import JobRecord
from app.schemas.user import UserCreate, UserOut
from app.schemas.machine import MachineCreate, MachineOut
from app.schemas.material import MaterialCreate, MaterialOut
from app.schemas.tool import ToolCreate, ToolOut
from app.schemas.job_record import JobRecordCreate, JobRecordOut


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def engine():
    """SQLite 内存数据库引擎，仅用于测试"""
    eng = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture()
def db(engine):
    """每个测试函数独立的数据库 session，测试后回滚"""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# User ORM 模型
# ---------------------------------------------------------------------------


class TestUserORM:
    """User 模型基础测试"""

    def test_user_table_exists(self, engine):
        """用户表存在"""
        inspector = inspect(engine)
        assert "users" in inspector.get_table_names()

    def test_user_columns(self, engine):
        """用户表包含必要字段"""
        inspector = inspect(engine)
        columns = {col["name"] for col in inspector.get_columns("users")}
        expected = {"id", "username", "hashed_password", "role", "is_active", "created_at", "updated_at"}
        assert expected.issubset(columns)

    def test_create_user(self, db: Session):
        """创建用户并持久化"""
        user = User(
            username="zhangsan",
            hashed_password="hashed_abc123",
            role="operator",
        )
        db.add(user)
        db.flush()

        assert user.id is not None
        assert user.username == "zhangsan"
        assert user.role == "operator"
        assert user.is_active is True
        assert user.created_at is not None

    def test_user_unique_username(self, db: Session):
        """用户名唯一约束"""
        user1 = User(username="unique_user", hashed_password="h1")
        user2 = User(username="unique_user", hashed_password="h2")
        db.add(user1)
        db.flush()

        db.add(user2)
        with pytest.raises(Exception):  # noqa: B017 — IntegrityError 依赖驱动
            db.flush()

    def test_user_default_role(self, db: Session):
        """默认角色为 operator"""
        user = User(username="default_role", hashed_password="h")
        db.add(user)
        db.flush()
        assert user.role == "operator"

    def test_user_has_many_job_records(self, db: Session):
        """User 拥有多个 JobRecord（一对多）"""
        user = User(username="with_jobs", hashed_password="h")
        db.add(user)
        db.flush()

        job1 = JobRecord(user_id=user.id, part_name="PartA")
        job2 = JobRecord(user_id=user.id, part_name="PartB")
        db.add_all([job1, job2])
        db.flush()

        assert len(user.job_records) == 2
        assert {j.part_name for j in user.job_records} == {"PartA", "PartB"}


# ---------------------------------------------------------------------------
# Machine ORM 模型
# ---------------------------------------------------------------------------


class TestMachineORM:
    """Machine 模型基础测试"""

    def test_machine_table_exists(self, engine):
        inspector = inspect(engine)
        assert "machines" in inspector.get_table_names()

    def test_machine_columns(self, engine):
        inspector = inspect(engine)
        columns = {col["name"] for col in inspector.get_columns("machines")}
        expected = {"id", "name", "cnc_system", "brand", "model_no", "created_at", "updated_at"}
        assert expected.issubset(columns)

    def test_create_machine(self, db: Session):
        machine = Machine(
            name="车间1号机",
            cnc_system="FANUC",
            brand="MAZAK",
            model_no="QTN-200",
        )
        db.add(machine)
        db.flush()

        assert machine.id is not None
        assert machine.cnc_system == "FANUC"

    def test_machine_has_many_job_records(self, db: Session):
        machine = Machine(name="关联机床", cnc_system="Siemens")
        db.add(machine)
        db.flush()

        job = JobRecord(part_name="TestPart", machine_id=machine.id)
        db.add(job)
        db.flush()

        assert len(machine.job_records) == 1


# ---------------------------------------------------------------------------
# Material ORM 模型
# ---------------------------------------------------------------------------


class TestMaterialORM:
    """Material 模型基础测试"""

    def test_material_table_exists(self, engine):
        inspector = inspect(engine)
        assert "materials" in inspector.get_table_names()

    def test_material_columns(self, engine):
        inspector = inspect(engine)
        columns = {col["name"] for col in inspector.get_columns("materials")}
        expected = {"id", "name", "grade", "hardness", "density", "cutting_speed_ref", "created_at", "updated_at"}
        assert expected.issubset(columns)

    def test_create_material(self, db: Session):
        material = Material(
            name="45#钢",
            grade="45",
            hardness="HRC20-25",
            density=7.85,
            cutting_speed_ref=120.0,
        )
        db.add(material)
        db.flush()

        assert material.id is not None
        assert material.name == "45#钢"
        assert material.cutting_speed_ref == 120.0

    def test_material_has_many_job_records(self, db: Session):
        material = Material(name="铝6061", grade="6061")
        db.add(material)
        db.flush()

        job = JobRecord(part_name="AlPart", material_id=material.id)
        db.add(job)
        db.flush()

        assert len(material.job_records) == 1


# ---------------------------------------------------------------------------
# Tool ORM 模型
# ---------------------------------------------------------------------------


class TestToolORM:
    """Tool 模型基础测试"""

    def test_tool_table_exists(self, engine):
        inspector = inspect(engine)
        assert "tools" in inspector.get_table_names()

    def test_tool_columns(self, engine):
        inspector = inspect(engine)
        columns = {col["name"] for col in inspector.get_columns("tools")}
        expected = {
            "id", "name", "tool_type", "spec", "batch_no",
            "total_cut_length", "max_cut_length", "is_active",
            "created_at", "updated_at",
        }
        assert expected.issubset(columns)

    def test_create_tool(self, db: Session):
        tool = Tool(
            name="T01 立铣刀",
            tool_type="end_mill",
            spec="D10",
            batch_no="B20260601",
            total_cut_length=0.0,
            max_cut_length=50000.0,
        )
        db.add(tool)
        db.flush()

        assert tool.id is not None
        assert tool.tool_type == "end_mill"
        assert tool.is_active is True

    def test_tool_default_active(self, db: Session):
        tool = Tool(name="默认刀具", tool_type="drill", spec="D5")
        db.add(tool)
        db.flush()
        assert tool.is_active is True

    def test_tool_has_many_job_records(self, db: Session):
        tool = Tool(name="关联刀具", tool_type="turning", spec="CNMG120408")
        db.add(tool)
        db.flush()

        job = JobRecord(part_name="ToolPart", tool_id=tool.id)
        db.add(job)
        db.flush()

        assert len(tool.job_records) == 1


# ---------------------------------------------------------------------------
# JobRecord ORM 模型
# ---------------------------------------------------------------------------


class TestJobRecordORM:
    """JobRecord 模型基础测试"""

    def test_job_record_table_exists(self, engine):
        inspector = inspect(engine)
        assert "job_records" in inspector.get_table_names()

    def test_job_record_columns(self, engine):
        inspector = inspect(engine)
        columns = {col["name"] for col in inspector.get_columns("job_records")}
        expected = {
            "id", "user_id", "machine_id", "material_id", "tool_id",
            "part_name", "drawing_path", "gcode_text",
            "status", "validation_result",
            "created_at", "updated_at",
        }
        assert expected.issubset(columns)

    def test_create_job_record_minimal(self, db: Session):
        """最少必填字段：part_name"""
        job = JobRecord(part_name="最小任务")
        db.add(job)
        db.flush()

        assert job.id is not None
        assert job.status == "draft"
        assert job.created_at is not None

    def test_create_job_record_full(self, db: Session):
        """完整字段创建"""
        user = User(username="job_user", hashed_password="h")
        machine = Machine(name="job_machine", cnc_system="FANUC")
        material = Material(name="job_material", grade="45")
        tool = Tool(name="job_tool", tool_type="end_mill", spec="D10")
        db.add_all([user, machine, material, tool])
        db.flush()

        job = JobRecord(
            user_id=user.id,
            machine_id=machine.id,
            material_id=material.id,
            tool_id=tool.id,
            part_name="完整任务",
            drawing_path="/uploads/drawing.png",
            gcode_text="G01 X10 Y20 F200",
            status="completed",
            validation_result='[{"level":"A","rule":"A-01","passed":true}]',
        )
        db.add(job)
        db.flush()

        assert job.user_id == user.id
        assert job.machine_id == machine.id
        assert job.status == "completed"

    def test_job_record_belongs_to_user(self, db: Session):
        """JobRecord 反向关联 User"""
        user = User(username="reverse_user", hashed_password="h")
        db.add(user)
        db.flush()

        job = JobRecord(part_name="反向关联", user_id=user.id)
        db.add(job)
        db.flush()

        assert job.user.username == "reverse_user"

    def test_job_record_default_status(self, db: Session):
        """默认状态为 draft"""
        job = JobRecord(part_name="默认状态")
        db.add(job)
        db.flush()
        assert job.status == "draft"


# ---------------------------------------------------------------------------
# Pydantic Schema 测试
# ---------------------------------------------------------------------------


class TestUserSchema:
    """User Pydantic schema 测试"""

    def test_user_create_valid(self):
        schema = UserCreate(username="zhangsan", password="Str0ngP@ss!")
        assert schema.username == "zhangsan"

    def test_user_create_short_username(self):
        with pytest.raises(ValidationError):
            UserCreate(username="ab", password="Str0ngP@ss!")

    def test_user_create_short_password(self):
        with pytest.raises(ValidationError):
            UserCreate(username="zhangsan", password="short")

    def test_user_out_excludes_password(self):
        out = UserOut(id=1, username="zhangsan", role="operator", is_active=True)
        data = out.model_dump()
        assert "password" not in data
        assert "hashed_password" not in data


class TestMachineSchema:
    """Machine Pydantic schema 测试"""

    def test_machine_create_valid(self):
        schema = MachineCreate(name="车间1号机", cnc_system="FANUC")
        assert schema.cnc_system == "FANUC"

    def test_machine_create_invalid_system(self):
        with pytest.raises(ValidationError):
            MachineCreate(name="test", cnc_system="INVALID_SYSTEM")

    def test_machine_out_roundtrip(self):
        out = MachineOut(id=1, name="test", cnc_system="Siemens")
        data = out.model_dump()
        assert data["cnc_system"] == "Siemens"


class TestMaterialSchema:
    """Material Pydantic schema 测试"""

    def test_material_create_valid(self):
        schema = MaterialCreate(name="45#钢", grade="45", cutting_speed_ref=120.0)
        assert schema.name == "45#钢"

    def test_material_create_negative_speed(self):
        with pytest.raises(ValidationError):
            MaterialCreate(name="test", cutting_speed_ref=-10.0)

    def test_material_out_optional_fields(self):
        out = MaterialOut(id=1, name="铝6061", grade="6061")
        assert out.hardness is None
        assert out.density is None


class TestToolSchema:
    """Tool Pydantic schema 测试"""

    def test_tool_create_valid(self):
        schema = ToolCreate(name="T01 立铣刀", tool_type="end_mill", spec="D10")
        assert schema.tool_type == "end_mill"

    def test_tool_create_invalid_type(self):
        with pytest.raises(ValidationError):
            ToolCreate(name="test", tool_type="invalid_type", spec="D10")

    def test_tool_out_defaults(self):
        out = ToolOut(id=1, name="test", tool_type="drill", spec="D5")
        assert out.is_active is True
        assert out.total_cut_length == 0.0


class TestJobRecordSchema:
    """JobRecord Pydantic schema 测试"""

    def test_job_record_create_minimal(self):
        schema = JobRecordCreate(part_name="简单零件")
        assert schema.part_name == "简单零件"
        assert schema.machine_id is None

    def test_job_record_create_full(self):
        schema = JobRecordCreate(
            part_name="复杂零件",
            machine_id=1,
            material_id=2,
            tool_id=3,
        )
        assert schema.machine_id == 1

    def test_job_record_out_with_timestamps(self):
        out = JobRecordOut(
            id=1,
            part_name="测试",
            status="draft",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        data = out.model_dump()
        assert "created_at" in data
        assert data["status"] == "draft"
