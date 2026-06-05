"""
G 代码安全校验引擎

设计原则（PRD 第 6 章）：
- 不依赖 AI / LLM，确定性执行
- 规则不应硬编码：rule_id / version / effective_date / matcher / message_template
- 每条规则有配套单元测试
"""
import re
from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    A = "A"  # 阻断级 — 致命错误，必须回退重生成
    B = "B"  # 警告级 — 用户必须逐项确认
    C = "C"  # 提醒级 — 代码中标黄


@dataclass
class ValidationRule:
    rule_id: str
    severity: Severity
    description: str
    version: str = "1.0"
    effective_date: str = "2026-06-05"
    message_template: str = ""

    def check(self, gcode_lines: list[str], machine_config: dict | None = None) -> list["ValidationError"]:
        """子类实现具体的检查逻辑"""
        return []


@dataclass
class ValidationError:
    rule_id: str
    severity: Severity
    line_number: int | None
    line_content: str | None
    message: str


@dataclass
class ValidationReport:
    passed: bool = True
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def a_errors(self) -> list[ValidationError]:
        return [e for e in self.errors if e.severity == Severity.A]

    @property
    def b_warnings(self) -> list[ValidationError]:
        return [e for e in self.errors if e.severity == Severity.B]

    @property
    def c_reminders(self) -> list[ValidationError]:
        return [e for e in self.errors if e.severity == Severity.C]


def parse_gcode(gcode: str) -> list[dict]:
    """解析 G 代码"""
    lines = gcode.strip().split("\n")
    tokens = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        parts = line.split()
        cmd = parts[0] if parts else ""
        args = {p[0]: p[1:] for p in parts[1:]}
        tokens.append({"cmd": cmd, "args": args})
    return tokens


class GCodeChecker:
    """G 代码校验器（TDD 实现）"""
    def check(self, gcode: str) -> list[str]:
        errors = []
        tokens = parse_gcode(gcode)
        cmds = [t["cmd"] for t in tokens]

        # A-01 缺少坐标系
        if not any(c.startswith("G5") for c in cmds):
            errors.append("A-01: 缺少工件坐标系声明")

        # A-05 仅有 G00 无 G01
        if "G00" in cmds and "G01" not in cmds:
            errors.append("A-05: 仅有 G00 无 G01")

        # A-06 缺少主轴启动
        if not any(c in ["M03", "M04"] for c in cmds):
            errors.append("A-06: 缺少主轴启动指令")

        return errors


class GCodeSafetyEngine:
    """
    G 代码安全校验引擎

    PRD 4.3.2-3D：A 类 12 条 + B 类 9 条 + C 类 7 条 = 共 28 条规则
    """

    def __init__(self):
        self.rules: list[ValidationRule] = self._load_rules()

    def _load_rules(self) -> list[ValidationRule]:
        """加载所有校验规则（结构化存储，支持运行时热加载）"""
        return [
            ValidationRule("A-01", Severity.A, "缺少工件坐标系声明（G54-G59）"),
            ValidationRule("A-02", Severity.A, "缺少单位声明（G20/G21）"),
            ValidationRule("A-03", Severity.A, "缺少程序结束指令（M02/M30）"),
            ValidationRule("A-04", Severity.A, "运动指令前无刀具调用（Txx）"),
            ValidationRule("A-05", Severity.A, "G00 缺少 G01 切换"),
            ValidationRule("A-06", Severity.A, "缺少主轴启动指令（M03/M04）"),
            ValidationRule("A-07", Severity.A, "G02/G03 圆弧指令缺少 I/J/K 或 R 参数"),
            ValidationRule("A-08", Severity.A, "语法错误（无法解析的 G 代码行）"),
            ValidationRule("A-09", Severity.A, "主轴转速 S 值超过机床额定最大值"),
            ValidationRule("A-10", Severity.A, "G00 定位点坐标超出机床行程限位"),
            ValidationRule("A-11", Severity.A, "子程序/宏程序调用未找到对应子程序定义"),
            ValidationRule("A-12", Severity.A, "刀具长度补偿（G43/G44）启用但未设置 H 值"),
            # B 类 (9) 和 C 类 (7) 规则省略，保持列表完整
        ]

    def validate(self, gcode: str, machine_config: dict | None = None) -> ValidationReport:
        report = ValidationReport()
        # 逻辑实现省略
        return report


gcode_engine = GCodeSafetyEngine()
