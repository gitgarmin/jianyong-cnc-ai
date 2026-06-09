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

## 会话经验

**会话中发现重要教训时，主动追加到 `.claude/experience.md`**，包括：
- 踩过的坑和解决方法
- 某个模块的隐含约定或陷阱
- 某个工具/API 的意外行为
- 比预期更复杂或更简单的事情

格式：`## YYYY-MM-DD` + 一句话标题 + 简短描述。

**每次会话开始时，读取该文件最近 5 条记录**，避免重复犯错。

## Skill 执行纠错

执行 Skill 过程中遇到错误或不符合预期的结果时：

1. **分析原因** — 是 Skill 指导有误，还是实际情况与 Skill 假设不符
2. **提出方案** — 给出具体的优化建议
3. **不确定就问** — 如果无法判断根因，向用户提问，一起讨论
4. **共同优化** — 与用户确认后，当场修改 Skill 文件

不要默默跳过错误继续执行，也不要自己擅自修改 Skill。

## 配置审查

每 3-6 个月或大模型发布后，审查以下内容是否仍然必要：

| 审查对象 | 检查项 |
|---------|--------|
| Skills | 是否有 Skill 已被新模型能力替代 |
| Hooks | 是否有 Hook 已不需要（如模型原生支持了某功能） |
| CLAUDE.md 规则 | 是否有规则限制了新模型的能力 |
| .ignore | 排除范围是否合理 |

## 工作范围

当任务明确属于某个子目录时，从该子目录开始工作，而非仓库根目录。
Claude 会自动向上遍历加载沿途的 CLAUDE.md，根级上下文不会丢失。

---

## 快速开始

- Node.js ≥ 20，Python ≥ 3.11，Docker Desktop
- `cp .env.example .env` 后填入 DeepSeek API Key
- 详细启动命令 → `.claude/skills/deployment.md`

---

## 代码地图

详见 [`CODE_MAP.md`](CODE_MAP.md)。

---

## 架构决策记录

完整 ADR 见 [`docs/architecture.md`](docs/architecture.md)。以下是关键决策摘要：

| ADR | 决策 | 核心理由 |
|-----|------|---------|
| ADR-1 | MUI 而非 Tailwind | 组件生态完整，小团队效率优先 |
| ADR-2 | SQLite 开发 + MySQL 生产 | 单机场景够用，避免开发期维护 MySQL |
| ADR-3 | AI Provider 抽象层 | 避免供应商锁定，支持离线降级 |
| ADR-4 | 安全校验引擎独立于 AI | 安全规则必须确定性执行 |

---

## 开发约定

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

> 注：`docs/PRD.md` 已在 `.ignore` 中排除（文件过大），以下为关键内容摘要。需要细节时直接读取 PRD 对应章节。

| 内容 | 要点 |
|------|------|
| 核心功能（§4） | AI 问答（RAG）、G 代码生成（双图纸→解析→校验→首件）、后处理模板、刀具追踪 |
| 安全体系（§6） | 四层防线：前端预检→引擎校验→AI 辅助→人工终检 |
| 技术约束（§7） | SQLite 开发/MySQL 生产、AI Provider 抽象层、安全引擎独立于 AI |
| 页面交互（§14） | 底部 Tab 导航：对话、G 代码（4 步 Stepper）、我的 |

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

### 如何切换 AI Provider？

修改 `.env` 中的 `AI_PROVIDER` 变量：
- `deepseek` — DeepSeek API（默认）
- `local` — 本地 ollama/Qwen

### 领域知识参考

- G 代码校验规则开发流程 → `.claude/skills/cnc-gcode-rules.md`
- 新增 API 端点标准流程 → `.claude/skills/api-development.md`
- 后处理模板开发 → `backend/app/services/post_processor.py`
- 安全校验引擎架构 → `backend/app/services/gcode_engine.py`

---

## 配置所有权

本项目 Claude Code 配置的所有权：

| 配置 | 文件 | 负责人 |
|------|------|--------|
| 全局规则 | `CLAUDE.md` | 项目负责人 |
| 后端配置 | `backend/CLAUDE.md` | 后端开发 |
| 前端配置 | `frontend/CLAUDE.md` | 前端开发 |
| Skills | `.claude/skills/` | 项目负责人 |
| Hooks | `.claude/settings.json` | 项目负责人 |
