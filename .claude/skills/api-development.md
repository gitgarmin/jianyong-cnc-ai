---
name: api-development
description: FastAPI 端点开发标准流程，添加新 API 端点或新业务域时使用
---

# FastAPI 端点开发 Skill

## When to Activate

仅在以下路径相关场景激活，其他目录下不加载：

- 用户要求添加新 API 端点或新业务域
- 当前编辑的文件在 `backend/app/api/` 目录下
- 当前编辑的文件在 `backend/app/schemas/` 目录下
- 当前编辑的文件是 `backend/app/main.py`（注册新路由）

## 前置条件

- 后端开发服务器运行中：`cd backend && uvicorn app.main:app --reload --port 8000`
- 了解所需的请求/响应 Schema

## 第 1 步：定义 Pydantic Schema

创建或扩展 `backend/app/schemas/{{domain}}.py`：

```python
"""{{DOMAIN_NAME}} API — Pydantic Schema"""

from __future__ import annotations

from pydantic import BaseModel, Field


class {{RequestName}}Request(BaseModel):
    """{{描述}}"""

    {{field}}: {{type}} = Field(..., description="{{字段描述}}")


class {{ResponseName}}Response(BaseModel):
    """{{描述}}"""

    {{field}}: {{type}} = Field(..., description="{{字段描述}}")
```

Schema 约定：
- 每个字段使用 `Field(...)` 并添加 `description`
- 使用 `min_length` / `max_length` / `pattern` 做验证
- 可选列表字段使用 `default_factory=list`
- 可空字段使用 `X | None`（不用 `Optional[X]`）

## 第 2 步：创建 Router

创建或扩展 `backend/app/api/{{domain}}.py`：

```python
"""{{DOMAIN_NAME}} API — {{简要描述}}"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.{{domain}} import {{RequestName}}Request, {{ResponseName}}Response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/{{action}}", response_model={{ResponseName}}Response)
async def {{handler_name}}(
    request: {{RequestName}}Request,
    db: Session = Depends(get_db),
) -> {{ResponseName}}Response:
    """{{接口描述}}"""
    # 实现逻辑
    ...
```

## 第 3 步：在 main.py 注册路由

在 `backend/app/main.py` 中添加：

```python
from app.api import {{domain}}

app.include_router({{domain}}.router, prefix="/api/{{domain}}", tags=["{{TAG}}"])
```

## 第 4 步：添加 Service 逻辑（非 CRUD 场景）

若端点需要超越简单 CRUD 的业务逻辑：

```python
# backend/app/services/{{service_name}}.py
"""{{SERVICE_NAME}} — 业务逻辑"""

from __future__ import annotations


class {{ServiceName}}:
    """{{描述}}"""

    async def {{method}}(self, {{params}}) -> {{ReturnType}}:
        """{{方法描述}}"""
        ...
```

## 第 5 步：编写测试

创建 `backend/tests/test_{{domain}}.py`：

```python
"""{{DOMAIN_NAME}} API 测试"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_{{endpoint}}_success():
    """测试 {{endpoint}}：合法输入"""
    response = client.post(
        "/api/{{domain}}/{{action}}",
        json={{有效载荷}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_{{endpoint}}_validation_error():
    """测试 {{endpoint}}：非法输入"""
    response = client.post(
        "/api/{{domain}}/{{action}}",
        json={{无效载荷}},
    )
    assert response.status_code == 422
```

## 第 6 步：更新文档

- 在 `docs/api-design.md` 添加端点说明
- 更新 `docs/progress.md` 模块状态
- 运行验证：`cd backend && python -m pytest tests/test_{{domain}}.py -v`

## API 响应规范

所有端点返回统一信封格式：

```json
{
  "success": true,
  "data": {},
  "error": null,
  "metadata": {}
}
```

详见根目录 CLAUDE.md。
