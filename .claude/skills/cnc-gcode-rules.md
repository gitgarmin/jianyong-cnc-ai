---
name: cnc-gcode-rules
description: G 代码安全校验规则开发流程，添加、修改或调试校验规则时使用
---

# G-Code 安全校验规则 Skill

## When to Activate

- 用户要求添加、修改或调试 G 代码安全校验规则
- 编辑 `backend/app/services/gcode_engine.py`
- 编辑 `backend/tests/test_gcode_engine.py`
- 讨论 G 代码安全性、碰撞检测、刀具保护相关问题

## 上下文

G 代码安全引擎位于 `backend/app/services/gcode_engine.py`，是独立于 AI 的确定性校验模块（参见 ADR-4）。
规则分为三级（参见 PRD §4.3.2-3D 和 §6）：

| 严重级别 | 编码前缀 | 数量 | 行为 |
|---------|---------|------|------|
| A（阻断级） | `A-XX` | 12 | 致命错误——必须回退重生成 |
| B（警告级） | `B-XX` | 9 | 警告——用户需逐项确认 |
| C（提醒级） | `C-XX` | 7 | 提醒——在代码显示中标黄 |

## 添加新规则（5 步）

### 第 1 步：分配 ID 和严重级别

查看 `GCodeSafetyEngine._load_rules()` 找到下一个可用 ID：
- A 级规则：`A-01` 至 `A-12`（检查是否有空缺）
- B 级规则：`B-01` 至 `B-09`
- C 级规则：`C-01` 至 `C-07`

### 第 2 步：定义规则

在 `_load_rules()` 中添加 `ValidationRule` 数据类实例：

```python
ValidationRule("{{RULE_ID}}", Severity.{{A|B|C}}, "{{规则的中文描述}}"),
```

### 第 3 步：实现检查逻辑

在 `GCodeChecker.check()` 或 `GCodeSafetyEngine.validate()` 中添加：

```python
# {{RULE_ID}} {{描述}}
if {{条件}}:
    errors.append("{{RULE_ID}}: {{中文错误信息}}")
```

常见条件模式：

```python
# 缺少必要的 G/M 代码
not any(c.startswith("G5") for c in cmds)

# 代码缺少前置条件
"G00" in cmds and "G01" not in cmds

# 参数值超限
any(float(t["args"].get("S", "0")) > max_rpm for t in tokens)

# 语法错误（在 parse_gcode() 中 try/except 捕获）
```

### 第 4 步：编写测试

在 `backend/tests/test_gcode_engine.py` 中编写 positive + negative 测试：

```python
def test_{{rule_id_lowercase}}_violation():
    """测试 {{RULE_ID}}: {{描述}}"""
    code = "{{触发该规则的最小 G 代码}}"
    checker = GCodeChecker()
    errors = checker.check(code)
    assert any("{{RULE_ID}}" in e for e in errors)


def test_{{rule_id_lowercase}}_pass():
    """测试 {{RULE_ID}}: 合法代码无此错误"""
    code = "{{不会触发该规则的合法 G 代码}}"
    checker = GCodeChecker()
    errors = checker.check(code)
    assert not any("{{RULE_ID}}" in e for e in errors)
```

### 第 5 步：更新文档

- 更新 PRD §4.3.2-3D 规则清单
- 更新 `docs/progress.md`（如属于已跟踪模块）

## G/M 代码快速参考

### 常用 G 代码

| 代码 | 功能 |
|------|------|
| `G00` | 快速定位 |
| `G01` | 直线插补（切削） |
| `G02/G03` | 顺/逆时针圆弧插补 |
| `G20/G21` | 英制/公制模式 |
| `G40/G41/G42` | 取消/左/右刀具补偿 |
| `G43/G44` | 刀具长度补偿 |
| `G54-G59` | 工件坐标系 |
| `G90/G91` | 绝对/增量定位 |

### 常用 M 代码

| 代码 | 功能 |
|------|------|
| `M03/M04` | 主轴正/反转 |
| `M05` | 主轴停止 |
| `M06` | 换刀 |
| `M08/M09` | 冷却液开/关 |
| `M30` | 程序结束并复位 |

## 安全底线（绝不违反）

- 绝不建议可能导致碰撞或断刀的 G 代码
- 确保在任何运动指令前声明坐标系
- 确保在切削运动前启动主轴
- 标记缺少程序结束指令（M02/M30）的代码
