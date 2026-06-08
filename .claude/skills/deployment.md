---
name: deployment
description: 部署和环境配置流程，Docker 构建、环境变量配置、数据库迁移时使用
---

# 部署流程 Skill

## When to Activate

- 修改 `docker-compose.yml` 或 `backend/Dockerfile`
- 配置或修改 `.env` 环境变量
- 执行数据库迁移（alembic）
- 准备部署或构建 Docker 镜像
- 讨论生产环境配置、性能优化

## 环境变量清单

所有环境变量定义在 `.env.example`，使用前复制为 `.env`：

| 变量 | 用途 | 必填 |
|------|------|------|
| `DATABASE_URL` | 数据库连接字符串 | 是 |
| `AI_PROVIDER` | AI 供应商（`deepseek` 或 `local`） | 是 |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 使用 deepseek 时 |
| `DEEPSEEK_BASE_URL` | DeepSeek API 地址 | 否（有默认值） |
| `SECRET_KEY` | JWT 签名密钥 | 是 |
| `CHROMA_PERSIST_DIR` | ChromaDB 持久化目录 | 否（有默认值） |

## Docker Compose 启动

```bash
# 仅启动 MySQL
docker compose up -d mysql

# 全栈启动（MySQL + 后端）
docker compose up -d

# 查看日志
docker compose logs -f backend

# 停止
docker compose down
```

## 数据库迁移

```bash
# 生成迁移文件
cd backend && alembic revision --autogenerate -m "{{描述}}"

# 执行迁移
cd backend && alembic upgrade head

# 回滚一步
cd backend && alembic downgrade -1
```

## 部署前检查清单

- [ ] `.env` 已配置所有必填变量
- [ ] `SECRET_KEY` 不是默认值
- [ ] 数据库连接字符串指向正确的数据库
- [ ] AI Provider API Key 有效
- [ ] 所有测试通过：`cd backend && python -m pytest`
- [ ] 前端构建成功：`cd frontend && npm run build`
- [ ] `docker-compose.yml` 中端口映射正确
- [ ] 上传目录（uploads/）已挂载为持久化卷

## 开发环境 vs 生产环境

| 项 | 开发 | 生产 |
|---|------|------|
| 数据库 | SQLite（自动） | MySQL 8.0（Docker） |
| 后端 | `uvicorn --reload` | Docker 容器 |
| 前端 | Vite dev server (5173) | `npm run build` + nginx |
| AI | DeepSeek API | DeepSeek 或本地 ollama |
