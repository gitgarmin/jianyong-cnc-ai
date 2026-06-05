from fastapi import APIRouter

router = APIRouter()


@router.post("/checklist")
async def generate_checklist(drawing_data: dict):
    """根据图纸解析结果生成首件检验清单"""
    return {"checklist": []}


@router.post("/verify")
async def verify_measurement(check_data: dict):
    """提交实测值，AI 判定合格/不合格"""
    return {"result": "pending", "ai_suggestion": None}
