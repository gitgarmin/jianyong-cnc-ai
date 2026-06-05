from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def get_tool_status():
    """获取刀具批次追踪状态"""
    return {"tools": []}
