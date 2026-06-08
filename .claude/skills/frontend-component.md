---
name: frontend-component
description: React 组件开发流程，创建或修改 MUI 组件时使用
---

# 前端组件开发 Skill

## When to Activate

- 创建新的 React 组件
- 修改现有组件的布局或交互
- 编辑 `frontend/src/components/` 目录下的文件
- 需要添加新的 Zustand Store 或修改现有 Store
- 讨论 UI 布局、响应式设计、MUI 组件选择

## 组件创建流程

### 第 1 步：确定组件类型

| 类型 | 位置 | 说明 |
|------|------|------|
| 页面级组件 | `src/components/{{domain}}/` | 一个功能 Tab 的完整页面 |
| 通用展示组件 | `src/components/ui/` | 跨页面复用的小组件 |
| 布局组件 | `src/components/layout/` | 导航、框架结构 |

### 第 2 步：创建文件

`src/components/{{domain}}/{{ComponentName}}.tsx`

```tsx
import { Box, Typography } from '@mui/material';

interface {{ComponentName}}Props {
  {{prop}}: {{type}};
}

export default function {{ComponentName}}({ {{prop}} }: {{ComponentName}}Props) {
  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6">{{标题}}</Typography>
    </Box>
  );
}
```

### 第 3 步：选择 MUI 布局组件

| 需求 | 用什么 |
|------|--------|
| 垂直堆叠 | `Stack direction="column"` |
| 水平排列 | `Stack direction="row"` |
| 卡片容器 | `Paper` 或 `Card` |
| 网格布局 | `Grid2` |
| 弹性间距 | `Box sx={{ flex: 1 }}` |
| 固定底部 | `Box sx={{ position: 'sticky', bottom: 0 }}` |

### 第 4 步：状态管理

简单状态用 `useState`，跨组件状态用 Zustand：

```tsx
// src/stores/{{storeName}}.ts
import { create } from 'zustand';

interface {{StoreName}}State {
  {{field}}: {{type}};
  set{{Field}}: (value: {{type}}) => void;
}

export const use{{StoreName}} = create<{{StoreName}}State>((set) => ({
  {{field}}: {{默认值}},
  set{{Field}}: (value) => set({ {{field}}: value }),
}));
```

### 第 5 步：添加测试

```tsx
// {{ComponentName}}.test.tsx
import { render, screen } from '@testing-library/react';
import {{ComponentName}} from './{{ComponentName}}';

test('renders correctly', () => {
  render(<{{ComponentName}} {{prop}}="{{测试值}}" />);
  expect(screen.getByTestId('{{component-name}}')).toBeInTheDocument();
});
```

记得在交互元素上添加 `data-testid` 属性。

## MUI 样式约定

- 使用 `sx` prop，不用 CSS 文件
- 颜色来自主题：`primary.main`、`grey.50`、`error.main`
- 间距用数字倍数：`sx={{ p: 2 }}` = 16px
- 按钮不用大写：主题已配置 `textTransform: 'none'`
- 中文字体：主题已配置 PingFang、YaHei 等
