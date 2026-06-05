# 架构决策记录 (ADR)

## ADR-1: MUI 作为唯一 UI 框架

**日期**: 2026-06-05
**状态**: 已采纳

**背景**: PRD 最初列出了 MUI + Tailwind CSS 双轨方案。

**决策**: MVP 阶段只使用 MUI (Material UI)，删除 Tailwind CSS 依赖。

**理由**:
- 避免 CSS Specificity 冲突和两套主题 token 维护成本
- MUI 组件生态完整，匹配 PRD 需求（Stepper, BottomNavigation, Chip, Dialog 等）
- 创业阶段小团队，快速原型 > 极致定制

**后果**:
- CSS tokens 统一到 MUI ThemeProvider 一套系统
- 若 Phase 2 需要高度定制化 C 端体验，可评估 Tailwind + Radix UI 重构

---

## ADR-2: SQLite 开发 → MySQL 生产

**日期**: 2026-06-05
**状态**: 已采纳

**决策**: 开发期使用 SQLite，触发迁移的条件是单表超 50 万行或并发写入超 100qps。

**理由**:
- SQLite 对单机 CNC 场景完全够用，无需维护 MySQL 容器
- 迁移判断标准而非预设时间点，避免过度工程

**替代方案**: Docker MySQL 8.0 开发环境（Team 成员可用 Docker Compose 启动）

---

## ADR-3: AI Provider 抽象层

**日期**: 2026-06-05
**状态**: 已采纳

**决策**: 所有 AI 调用通过 `AIProvider` 抽象接口，支持 DeepSeek → 本地 ollama/Qwen 切换。

**理由**:
- 避免单一供应商锁定
- 支持离线/内网降级
- 安全校验引擎在任何 Provider 下独立工作

**实现**: 见 `backend/app/services/ai_provider.py`

---

## ADR-4: G 代码安全校验引擎独立于 AI

**日期**: 2026-06-05
**状态**: 已采纳

**决策**: 安全校验引擎是独立 Python 模块，不依赖 LLM，确定性执行。支持本地离线运行。

**理由**:
- AI 输出不可控（幻觉、遗漏），安全规则必须 100% 确定
- 引擎可编译为 WebAssembly 在前端离线运行（PRD §7.2 离线策略）
- 校验引擎不应依赖数据库和 AI 模块

---

## ADR-5: REST API 统一信封格式

**日期**: 2026-06-05
**状态**: 已采纳

```json
{
  "success": true,
  "data": {},
  "error": null,
  "metadata": null
}
```
