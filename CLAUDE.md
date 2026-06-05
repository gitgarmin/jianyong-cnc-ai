# 简用 数控AI大师

> "大学生 + AI = 数控老师傅七成功力"

## 项目概述

**简用 数控AI大师**是面向汽摩配、精密部件加工行业的数控编程 AI 助手。产品形态为一期 Web App（微信小程序后续跟进），让仅有机床操作基础的大专/本科毕业生能够独立完成数控编程、排故和参数调优。

### 核心功能

| 功能 | 说明 | PRD 章节 |
|------|------|----------|
| AI 对话问答 | 基于 RAG 的行业知识库问答，覆盖材料/故障/工艺/报警码/切削参数 | §4.1 |
| G 代码生成 | 双图纸上传→AI解析→安全校验→首件检验全流程 | §4.3 |
| 安全校验引擎 | 独立于 AI 的 G 代码静态校验（28 条规则，A/B/C 三级） | §4.3.2-3D |
| 后处理模板 | 支持 FANUC/Siemens/Haas/GSK 共 5 种数控系统方言适配 | §4.3.2-3C |
| 首件检验引导 | 自动生成检验清单，AI 辅助判定合格/不合格 | §4.3.2-3J |
| 刀具批次追踪 | 按批次追踪刀具寿命，到期提醒更换 | §4.3.2-3K |

### 目标用户

- **主要**：22-26 岁大专/本科毕业生 CNC 操作工（会装夹对刀，缺乏独立编程能力）
- **次要**：工厂老板/车间主任（关注人工成本和废品率）

---

## 快速开始

### 环境准备

- Node.js ≥ 20
- Python ≥ 3.11
- Docker Desktop（用于 MySQL）

### 一键启动

```bash
# 1. 安装前后端依赖
cd frontend && npm install
cd ../backend && pip install -r requirements.txt

# 2. 启动 MySQL（Docker）
docker compose up -d mysql

# 3. 复制环境变量
cp .env.example .env
# 编辑 .env 填入 DeepSeek API Key

# 4. 启动后端（http://localhost:8000/docs）
cd backend && uvicorn app.main:app --reload --port 8000

# 5. 启动前端（http://localhost:5173）
cd frontend && npm run dev
```

### Docker Compose 全栈启动

```bash
cp .env.example .env
docker compose up -d
```

---

## 目录结构

```
jianyong-cnc-ai/
├── frontend/                  # React + Vite + MUI
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/        # 底部Tab导航 + 全局状态条
│   │   │   ├── chat/          # 对话问答Tab
│   │   │   ├── gcode/         # G代码Tab（4步流程）
│   │   │   ├── profile/       # 我的Tab
│   │   │   └── ui/            # 通用UI组件
│   │   ├── hooks/             # 自定义 hooks
│   │   ├── lib/               # API 调用、G代码客户端校验
│   │   ├── stores/            # Zustand 状态管理
│   │   └── styles/            # MUI ThemeProvider 配置
│   └── vite.config.ts
├── backend/                   # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── api/               # REST API 路由
│   │   ├── core/              # 配置、数据库、安全
│   │   ├── models/            # SQLAlchemy ORM 模型
│   │   ├── schemas/           # Pydantic Schema
│   │   └── services/          # 业务逻辑层
│   │       ├── ai_provider.py       # AI Provider 抽象层
│   │       ├── gcode_engine.py      # G代码安全校验引擎（28条规则）
│   │       ├── drawing_parser.py    # 图纸解析 Provider
│   │       ├── post_processor.py    # 后处理模板
│   │       └── rag_service.py       # RAG 检索服务
│   └── tests/
├── docs/
│   ├── PRD.md                 # 当前最新 PRD
│   ├── PRD/                   # PRD 历史版本归档
│   ├── architecture.md        # 架构决策记录
│   ├── api-design.md          # API 接口设计
│   └── progress.md            # 项目进度跟踪
├── docker-compose.yml         # MySQL + 后端
├── CLAUDE.md                  # 本文档
└── README.md
```

---

## 架构决策记录

### ADR-1: MUI 而非 Tailwind（2026-06-05）

**决策**：MVP 阶段使用 MUI (Material UI) 作为唯一 UI 框架，删除 Tailwind CSS。

**理由**：
- MUI 组件生态完整（Stepper、BottomNavigation、Chip、Dialog），匹配 PRD 丰富的交互组件需求
- 快速原型速率高，小团队效率优先
- 目标用户对 UI 精美度要求不高，干净可用即可
- 避免 CSS Specificity 冲突和双轨维护成本

**替代方案已评估**：Tailwind + Radix UI（更适合高度定制化 C 端体验，Phase 2 如需重构可考虑）

### ADR-2: SQLite 开发 + MySQL 生产（2026-06-05）

**决策**：开发期使用 SQLite，MySQL 部署生产。判断标准：单表超过 50 万行或并发写入超 100qps 时迁移。

**理由**：SQLite 对单机 CNC 场景完全够用，避免开发期维护 MySQL 容器的额外复杂度。详见 PRD §7。

### ADR-3: AI Provider 抽象层（2026-06-05）

**决策**：所有 AI 调用通过 `AIProvider` 抽象接口，支持 DeepSeek + 本地 ollama/Qwen 切换。

**理由**：避免单一供应商锁定，支持离线/内网降级路径。详见 PRD §7.3。

### ADR-4: 安全校验引擎独立于 AI（2026-06-05）

**决策**：G 代码安全校验引擎是独立的 Python 模块，不依赖 LLM，确定性执行。

**理由**：AI 输出不可控（幻觉、遗漏），安全规则必须 100% 确定。校验引擎支持本地离线运行和 WASM 编译前端运行。

---

## 开发约定

### 文件命名

- React 组件：`PascalCase`（`ChatTab.tsx`、`GCodeTab.tsx`）
- Hooks：`use` 前缀（`useReducedMotion.ts`）
- Python 模块：`snake_case`（`gcode_engine.py`）
- API 路由文件以功能域命名

### API 响应格式

所有 API 响应使用统一信封：

```json
{
  "success": true,
  "data": {},
  "error": null,
  "metadata": { "total": 100, "page": 1, "limit": 20 }
}
```

### G 代码校验规则编号

- `A-XX`：阻断级（12 条）— 必须回退重生成
- `B-XX`：警告级（9 条）— 用户逐项确认
- `C-XX`：提醒级（7 条）— 代码中标黄

### 提交消息格式

遵循 Conventional Commits：
```
feat: 新增对话问答RAG检索
fix: 修复G代码校验引擎A-09规则误报
refactor: 提取图纸解析Provider接口
docs: 更新PRD至v1.5
test: 补充安全校验引擎单元测试
```

---

## PRD 关键索引

| 内容 | 位置 |
|------|------|
| 产品定义与用户故事 | `docs/PRD.md` §1-3 |
| 核心功能详解 | `docs/PRD.md` §4 |
| 安全体系（四层防线） | `docs/PRD.md` §6 |
| 技术约束与决策 | `docs/PRD.md` §7 |
| 竞品分析 | `docs/PRD.md` §11 |
| 页面交互说明 | `docs/PRD.md` §14 |

---

## 进度跟踪

开发进度和功能状态见 [`docs/progress.md`](docs/progress.md)。

当前阶段：**MVP Phase 0 — 项目初始化**

### 进度更新规则（强制）

**每次完成一个功能模块后，必须同步更新 `docs/progress.md`：**

1. **开始模块时**：将对应行的状态改为 🟦，填写开始时间（精确到时分秒，格式 `YYYY-MM-DD HH:MM:SS`）
2. **完成模块时**：将对应行的状态改为 ✅，填写完成时间和备注（涉及的关键文件路径）
3. **受阻时**：将状态改为 🟡，在备注中说明阻塞原因
4. **更新后立即 `git add docs/progress.md` 并随功能 commit 一起提交**，或作为单独的 `docs: update progress` commit

**这是强制性步骤，不是可选项。** 如果不更新 progress.md，下次新开 Claude Code 会话时 AI 将无法正确判断哪些模块已经完成，可能导致重复工作或遗漏。

---

## 常见问题

### 如何添加新的 G 代码安全规则？

1. 在 `backend/app/services/gcode_engine.py` 的 `_load_rules()` 中添加新的 `ValidationRule`
2. 在 `backend/tests/` 中编写配套的 positive + negative 单元测试
3. 更新 PRD §4.3.2-3D 的规则清单

### 如何添加新的数控系统后处理模板？

1. 在 `backend/app/services/post_processor.py` 中添加新的模板配置
2. 更新 `docs/PRD.md` 的机床档案表（§4.3.2-3C）

### 如何切换 AI Provider？

修改 `.env` 中的 `AI_PROVIDER` 变量：
- `deepseek` — DeepSeek API（默认）
- `local` — 本地 ollama/Qwen
