# API 接口设计

> 随开发进度更新，记录每个 API 的请求/响应格式。

## 通用约定

- 基础路径：`/api`
- 请求格式：JSON
- 响应信封：`{"success": bool, "data": any, "error": null | string, "metadata": null | {"total": int, "page": int, "limit": int}}`
- 认证：Bearer JWT（Header `Authorization: Bearer <token>`）

## 接口清单

### 对话问答

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | `/api/chat/send` | 发送消息，返回 AI 回答 | ⬜ |

### G 代码生成

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | `/api/gcode/generate` | 生成 G 代码 + 安全校验 | ⬜ |

### 图纸解析

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | `/api/drawings/upload` | 上传单张图纸 | ⬜ |

### 首件检验

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| POST | `/api/inspection/checklist` | 生成检验清单 | ⬜ |
| POST | `/api/inspection/verify` | 提交实测值 | ⬜ |

### 刀具追踪

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| GET | `/api/tools/status` | 获取刀具状态 | ⬜ |

### 系统

| 方法 | 路径 | 说明 | 状态 |
|------|------|------|------|
| GET | `/api/health` | 健康检查 | ✅ |
