"""B06 G-Code 校验引擎测试"""

import pytest
from app.services.gcode_engine import GCodeChecker, parse_gcode

# 测试用例基于 PRD §4.3.2-3D

def test_parse_gcode():
    """测试 G 代码解析逻辑"""
    code = "G00 X10 Y10\nG01 X20 Y20 F100"
    tokens = parse_gcode(code)
    assert len(tokens) == 2
    assert tokens[0]["cmd"] == "G00"

def test_check_missing_g54():
    """测试 A-01: 缺少工件坐标系声明"""
    code = "G00 X10\nG01 X20 F100\nM30"
    checker = GCodeChecker()
    errors = checker.check(code)
    assert any("A-01" in e for e in errors)

def test_check_g00_without_g01():
    """测试 A-05: 仅有 G00 无 G01"""
    code = "G54\nG00 X10\nG00 X20\nM30"
    checker = GCodeChecker()
    errors = checker.check(code)
    assert any("A-05" in e for e in errors)

def test_check_missing_spindle():
    """测试 A-06: 缺少主轴启动"""
    code = "G54\nG01 X10 F100\nM30"
    checker = GCodeChecker()
    errors = checker.check(code)
    assert any("A-06" in e for e in errors)

def test_pass_valid_code():
    """测试合法代码无错误"""
    code = "G54\nT01 M06\nM03 S1000\nG00 X0 Y0\nG01 X10 F100\nM30"
    checker = GCodeChecker()
    errors = checker.check(code)
    assert len(errors) == 0
