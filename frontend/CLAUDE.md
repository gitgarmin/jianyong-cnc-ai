# 简用 数控AI大师 — Frontend

> React SPA 层。项目概述和跨层约定见根目录 CLAUDE.md。

## 技术栈

- **UI 框架**：React 19 + MUI 6（Material UI）
- **状态管理**：Zustand 5
- **路由**：React Router 7
- **构建**：Vite 8
- **语言**：TypeScript（strict 模式）

## 架构

```
src/
  components/
    layout/     # Layout.tsx（AppBar + BottomNavigation + Outlet）
    chat/       # 对话问答 Tab
    gcode/      # G 代码生成 Tab（4 步 Stepper）
    profile/    # 我的 Tab
    ui/         # 通用展示组件
  hooks/        # 自定义 React Hooks（use* 前缀）
  lib/          # API 客户端（api.ts）、工具函数
  stores/       # Zustand Store（create<AppState>）
  styles/       # MUI 主题配置（theme.ts）
```

## 添加新组件（6 步）

1. 创建 `src/components/{{domain}}/{{ComponentName}}.tsx`（PascalCase）
2. 定义 Props 接口：`interface {{ComponentName}}Props { ... }`
3. 默认导出：`export default function {{ComponentName}}() { ... }`
4. 使用 MUI 组件布局（`Box`, `Paper`, `Typography`, `Stack`）
5. 需要共享状态时，在 `src/stores/` 创建或扩展 Zustand Store
6. 在同目录添加 `{{ComponentName}}.test.tsx` 测试文件

## 添加新 API 调用（4 步）

1. 在 `src/lib/api.ts` 添加函数
2. 使用 `fetch()` + `BASE_URL` 常量
3. 遵循模式：`export const {{methodName}} = async (params) => { ... }`
4. 在调用处用 try/catch 处理错误

## MUI 约定

- 使用 `sx` prop 做组件级样式（不用 CSS 文件）
- 所有颜色来自主题调色板（`primary.main`, `grey.50` 等）
- 按钮设置 `textTransform: 'none'`（已在主题中配置）
- 中文字体栈已在主题中配置（PingFang, YaHei 等）
- 交互元素添加 `data-testid` 属性用于测试

## 运行和测试

```bash
# 启动开发服务器（端口 5173，/api 代理到后端）
cd frontend && npm run dev

# Lint
cd frontend && npm run lint

# 运行测试（Vitest + Testing Library）
cd frontend && npm test

# 构建
cd frontend && npm run build
```

## 文件命名

- 组件：`PascalCase.tsx`（`ChatTab.tsx`, `GCodeTab.tsx`）
- Hooks：`camelCase.ts` + `use` 前缀（`useReducedMotion.ts`）
- Store：`camelCase.ts`（`appStore.ts`）
- 工具：`camelCase.ts`（`api.ts`）

## 文档更新规则

编辑以下文件后，检查对应文档是否需要同步更新：

| 变更文件 | 需检查的文档 | 触发条件 |
|---------|------------|---------|
| `src/components/**/*.tsx` | `CODE_MAP.md` | 新增组件 |
| `src/stores/*.ts` | `CODE_MAP.md` | 新增 Store |
| `App.tsx` | `CODE_MAP.md` | 新增路由 |
| 任何文件 | `docs/progress.md` | 模块状态变化 |

不需要更新的场景：bug 修复、样式调整、代码格式调整。
