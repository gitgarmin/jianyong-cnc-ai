from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, gcode, drawings, inspection, tools, records
from app.core.config import settings

app = FastAPI(
    title="简用 数控AI大师 API",
    description="数控加工AI助手后端服务 — AI对话问答、G代码生成、图纸解析、首件检验",
    version="0.1.0",
)

# CORS — 开发期允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api/chat", tags=["对话问答"])
app.include_router(gcode.router, prefix="/api/gcode", tags=["G代码生成"])
app.include_router(drawings.router, prefix="/api/drawings", tags=["图纸解析"])
app.include_router(inspection.router, prefix="/api/inspection", tags=["首件检验"])
app.include_router(tools.router, prefix="/api/tools", tags=["刀具追踪"])


app.include_router(records.router, prefix="/api/records", tags=["加工记录"])

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
