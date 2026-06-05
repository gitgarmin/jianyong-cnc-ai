from fastapi import APIRouter, UploadFile, File

router = APIRouter()


@router.post("/upload")
async def upload_drawing(file: UploadFile = File(...), drawing_type: str = "finished"):
    """上传图纸并触发 AI 解析"""
    # TODO: 质量门禁检查 → AI 解析 → 返回结构化结果
    return {"filename": file.filename, "drawing_type": drawing_type, "parsed": {}}
