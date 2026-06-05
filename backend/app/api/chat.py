from fastapi import APIRouter

router = APIRouter()


@router.post("/send")
async def send_message(message: dict):
    """发送对话消息，返回 AI 回答"""
    # TODO: RAG 检索 + AI Provider 调用
    return {"reply": "对话问答接口已就绪（占位）", "sources": []}
