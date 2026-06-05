# 简用 数控AI大师

> "大学生 + AI = 数控老师傅七成功力"

让一个刚毕业的大学生拿着这个产品，就能独立完成数控编程、排故和参数调优。

## 技术栈

| 层 | 技术 |
|------|------|
| 前端 | React + Vite + MUI + Zustand |
| 后端 | FastAPI + SQLAlchemy |
| AI | DeepSeek API（OpenAI 兼容） |
| 数据库 | SQLite（开发）→ MySQL（生产） |
| 部署 | Web App + CDN + 云服务器 |

## 快速开始

```bash
# 前端
cd frontend && npm install && npm run dev

# 后端
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload

# 数据库
docker compose up -d mysql
```

详见 [CLAUDE.md](CLAUDE.md) 获取完整开发指南。

## 文档

- [PRD (产品需求文档)](docs/PRD.md)
- [架构决策记录](docs/architecture.md)
- [项目进度](docs/progress.md)
- [API 设计](docs/api-design.md)

## 作者

© 2026 浙江简用智能科技有限公司 — 专注制造业数字化转型
