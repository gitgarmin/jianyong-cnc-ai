"""
G 代码安全校验引擎

设计原则（PRD 第 6 章）：
- 不依赖 AI / LLM，确定性执行
- 规则不应硬编码：rule_id / version / effective_date / matcher / message_template
- 每条规则有配套单元测试
"""
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


class GCodeSafetyEngine:
    """
    G 代码安全校验引擎

    PRD 4.3.2-3D：A 类 12 条 + B 类 9 条 + C 类 7 条 = 共 28 条规则
    """

    def __init__(self):
        self.rules: list[ValidationRule] = self._load_rules()

    def _load_rules(self) -> list[ValidationRule]:
        """加载所有校验规则（结构化存储，支持运行时热加载）"""
        # TODO: 实现 28 条规则的具体检查逻辑
        return [
            # A 类阻断级规则（12 条）— 示例骨架
            ValidationRule("A-01", Severity.A, "缺少工件坐标系声明（G54-G59）", message_template="未找到 G54-G59 工件坐标系声明"),
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
            # B 类警告级规则（9 条）
            ValidationRule("B-01", Severity.B, "换刀前缺少主轴停止 M05"),
            ValidationRule("B-02", Severity.B, "G00 定位点坐标在毛坯范围内"),
            ValidationRule("B-03", Severity.B, "车螺纹前缺少恒转速 G97"),
            ValidationRule("B-04", Severity.B, "刀补激活顺序不当"),
            ValidationRule("B-05", Severity.B, "缺少冷却液开关指令 M08/M09"),
            ValidationRule("B-06", Severity.B, "安全换刀点不在机床限位内"),
            ValidationRule("B-07", Severity.B, "同一刀具多次调用但未重新对刀"),
            ValidationRule("B-08", Severity.B, "冷却液类型与材料不匹配"),
            ValidationRule("B-09", Severity.B, "G01 进给速度 F 值超过机床额定最大进给"),
            # C 类提醒级规则（7 条）
            ValidationRule("C-01", Severity.C, "进给量 > 0.3 mm/r（粗车）"),
            ValidationRule("C-02", Severity.C, "切削深度 > 4 mm（单刀）"),
            ValidationRule("C-03", Severity.C, "转速超过材料推荐上限"),
            ValidationRule("C-04", Severity.C, "切削速度低于推荐范围"),
            ValidationRule("C-05", Severity.C, "精加工余量不合理"),
            ValidationRule("C-06", Severity.C, "相同刀具连续使用超过预设寿命阈值"),
            ValidationRule("C-07", Severity.C, "G00 与工件轮廓距离 < 1mm"),
        ]

    def validate(self, gcode: str, machine_config: dict | None = None) -> ValidationReport:
        """
        对 G 代码执行全量安全校验

        Args:
            gcode: 完整的 G 代码程序文本
            machine_config: 机床档案配置（含额定参数、行程限位等），用于动态阈值规则

        Returns:
            ValidationReport 包含所有校验错误
        """
        lines = gcode.strip().split("\n")
        report = ValidationReport()

        for rule in self.rules:
            errors = rule.check(lines, machine_config)
            report.errors.extend(errors)

        # A 类错误 = 未通过
        report.passed = len(report.a_errors) == 0
        return report


# 单例（校验引擎无状态，全局复用）
gcode_engine = GCodeSafetyEngine()
