# 简用 数控AI大师 — Backend

> Python API 服务层。项目概述和跨层约定见根目录 CLAUDE.md。

## 技术栈

- **框架**：FastAPI + uvicorn
- **ORM**：SQLAlchemy 2.0（Mapped 声明式风格）
- **Schema**：Pydantic v2 BaseModel
- **AI**：httpx 异步客户端 → DeepSeek API
- **向量库**：ChromaDB（进程内，无需外部服务）
- **配置**：pydantic-settings，读取项目根目录 `.env`

## 架构

```
app/
  api/          # 每个业务域一个路由文件：chat.py, gcode.py, drawings.py, ...
  core/         # config.py (Settings), database.py (engine/session), security.py (JWT)
  models/       # SQLAlchemy ORM 模型（每个实体一个文件）
  schemas/      # Pydantic 请求/响应 Schema（每个域一个文件）
  services/     # 业务逻辑（每个能力一个文件）
```

## 添加新 API 端点

完整流程见 Skill：`.claude/skills/api-development.md`（Schema → Router → 注册 → Service → 测试 → 文档）。

## 添加新 ORM 模型（6 步）

1. 在 `app/models/{{entity}}.py` 创建模型文件
2. 继承 `app.core.database.Base`
3. 使用 `Mapped[T]` + `mapped_column()`（SQLAlchemy 2.0 风格）
4. 包含 `created_at` 和 `updated_at`，使用 `server_default=func.now()`
5. 使用 `relationship()` + `back_populates` 建立关联
6. 在 `app/models/__init__.py` 注册

## API 响应规范

所有端点返回统一信封格式 `{ success, data, error, metadata }`。详见 `.claude/skills/api-development.md`。

## 运行和测试

```bash
# 启动后端
cd backend && uvicorn app.main:app --reload --port 8000

# 运行全部测试
cd backend && python -m pytest tests/ -v

# 运行单个测试文件
cd backend && python -m pytest tests/test_{{file}}.py -v

# API 文档
open http://localhost:8000/docs
```

## 后端编码约定

- Python ≥ 3.11，使用 `X | Y` 联合类型语法（不用 `Optional[X]`）
- 所有函数签名添加类型注解
- 所有公共函数和类添加 docstring（中英文均可）
- 使用 `logging.getLogger(__name__)`，不用 `print()`
- Service 层使用 ABC + 工厂模式（参考 `ai_provider.py`）
- API 路由中捕获域异常，返回友好的用户提示（不暴露 500 堆栈）

## G 代码校验规则编号

- `A-XX`：阻断级（12 条）— 必须回退重生成
- `B-XX`：警告级（9 条）— 用户逐项确认
- `C-XX`：提醒级（7 条）— 代码中标黄

## 文档更新规则

编辑以下文件后，检查对应文档是否需要同步更新：

| 变更文件 | 需检查的文档 | 触发条件 |
|---------|------------|---------|
| `app/api/*.py` | `docs/api-design.md` | 新增或修改端点 |
| `app/models/*.py` | `CODE_MAP.md` | 新增 ORM 模型 |
| `app/schemas/*.py` | `docs/api-design.md` | 新增或修改 Schema |
| 任何文件 | `docs/progress.md` | 模块状态变化 |

不需要更新的场景：bug 修复、代码格式调整、注释修改。
