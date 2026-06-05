from fastapi import APIRouter

router = APIRouter()


@router.post("/generate")
async def generate_gcode(spec: dict):
    """生成 G 代码 + 安全校验"""
    # TODO: AI 生成 G 代码 → 安全校验引擎 → 返回代码 + 校验报告
    return {"gcode": "; G代码生成接口已就绪（占位）", "validation_report": {}}
