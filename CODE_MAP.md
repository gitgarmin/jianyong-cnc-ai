# 简用 数控AI大师 — Code Map

> 每个模块一行的快速参考。新增/删除模块时同步更新此文件。

## Backend API 层（`backend/app/api/`）

| 模块 | 路径 | 用途 |
|------|------|------|
| chat | `app/api/chat.py` | POST /api/chat/send — 基于 RAG 的 AI 问答端点 |
| gcode | `app/api/gcode.py` | POST /api/gcode/generate — G 代码生成 + 安全校验 |
| drawings | `app/api/drawings.py` | POST /api/drawings/upload — 图纸上传 + AI 解析 |
| inspection | `app/api/inspection.py` | POST /api/inspection/checklist, /verify — 首件检验引导 |
| tools | `app/api/tools.py` | GET /api/tools/status — 刀具批次追踪 |
| records | `app/api/records.py` | POST /api/records/save, GET /history — 加工记录 CRUD |
| {{module}} | `app/api/{{domain}}.py` | {{一行描述}} |

## Backend Models 层（`backend/app/models/`）

| 模型 | 路径 | 用途 |
|------|------|------|
| user | `app/models/user.py` | User ORM（username, role, hashed_password） |
| machine | `app/models/machine.py` | Machine ORM（name, cnc_system, brand） |
| material | `app/models/material.py` | Material ORM |
| tool | `app/models/tool.py` | Tool ORM（batch_no, cut_length, 寿命追踪） |
| job_record | `app/models/job_record.py` | JobRecord ORM（关联 user+machine+material+tool） |
| {{model}} | `app/models/{{entity}}.py` | {{一行描述}} |

## Backend Schemas 层（`backend/app/schemas/`）

| Schema | 路径 | 用途 |
|--------|------|------|
| chat | `app/schemas/chat.py` | ChatRequest, ChatResponse, Source |
| job_record | `app/schemas/job_record.py` | JobRecordCreate, JobRecordOut |
| {{schema}} | `app/schemas/{{domain}}.py` | {{一行描述}} |

## Backend Services 层（`backend/app/services/`）

| 服务 | 路径 | 用途 |
|------|------|------|
| ai_provider | `app/services/ai_provider.py` | AI Provider 抽象层（DeepSeek + 本地 ollama 降级） |
| gcode_engine | `app/services/gcode_engine.py` | G 代码安全校验引擎（28 条规则，A/B/C 三级） |
| drawing_parser | `app/services/drawing_parser.py` | 图纸解析抽象层（Vision/OCR/手动） |
| post_processor | `app/services/post_processor.py` | 数控系统方言模板（FANUC/Siemens/Haas） |
| rag_service | `app/services/rag_service.py` | RAG 检索服务（ChromaDB + 句子分块） |
| {{service}} | `app/services/{{service}}.py` | {{一行描述}} |

## Backend Core 层（`backend/app/core/`）

| 模块 | 路径 | 用途 |
|------|------|------|
| config | `app/core/config.py` | pydantic-settings：环境变量、API Key、数据库 URL |
| database | `app/core/database.py` | SQLAlchemy engine、session factory、Base 类 |
| security | `app/core/security.py` | JWT token 创建/验证、密码哈希 |

## Backend 测试（`backend/tests/`）

| 文件 | 覆盖范围 |
|------|---------|
| test_chat.py | Chat API 端点 |
| test_gcode_engine.py | G 代码校验规则（A-01, A-05, A-06） |
| test_models.py | ORM 模型创建和关联 |
| test_rag_service.py | RAG 入库和检索 |

## Frontend（`frontend/src/`）

| 模块 | 路径 | 用途 |
|------|------|------|
| App | `App.tsx` | 路由定义（/chat, /gcode, /profile） |
| main | `main.tsx` | ReactDOM 入口、ThemeProvider、BrowserRouter |
| Layout | `components/layout/Layout.tsx` | AppBar + BottomNavigation + 全局状态条 + Outlet |
| ChatTab | `components/chat/ChatTab.tsx` | 对话界面：消息列表、快捷标签、输入栏 |
| GCodeTab | `components/gcode/GCodeTab.tsx` | 4 步 Stepper 的 G 代码生成工作流 |
| ProfileTab | `components/profile/ProfileTab.tsx` | 用户资料和设置 |
| api | `lib/api.ts` | Fetch 封装：sendChatMessage, saveJobRecord |
| appStore | `stores/appStore.ts` | Zustand：globalStatus, workpieceContext |
| theme | `styles/theme.ts` | MUI 主题：调色板、排版、组件覆盖 |

## 文档（`docs/`）

| 文件 | 内容 |
|------|------|
| PRD.md | 产品需求文档（v1.5） |
| architecture.md | 架构决策记录（ADR-1 至 ADR-5） |
| api-design.md | API 端点规范 |
| progress.md | 开发进度矩阵（前端 + 后端 + 基础设施） |

## 基础设施

| 文件 | 内容 |
|------|------|
| docker-compose.yml | MySQL 8.0 + 后端服务 |
| .env.example | 环境变量模板 |
| .gitignore | Git 忽略规则 |
| .ignore | Claude Code 扫描排除规则 |
| CLAUDE.md | 根目录 Claude Code 上下文 |
| backend/CLAUDE.md | 后端专用 Claude Code 上下文 |
| frontend/CLAUDE.md | 前端专用 Claude Code 上下文 |
| CODE_MAP.md | 本文件 |
