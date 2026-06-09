#!/bin/bash
# 会话结束时输出反思提示，Claude 在上下文还新鲜时评估是否需要更新配置

CHANGED=$(git diff --stat HEAD 2>/dev/null)
BRANCH=$(git branch --show-current 2>/dev/null)

echo ""
echo "=== 会话即将结束 ==="
echo "分支：$BRANCH"
if [ -n "$CHANGED" ]; then
  echo ""
  echo "本次变更："
  echo "$CHANGED"
fi
echo ""
echo "[REFLECT] 请在会话结束前反思："
echo "1. 本次会话中，哪些 CLAUDE.md 规则有帮助？哪些是多余的？"
echo "2. 用到的 Skill 是否准确？有没有误导或遗漏？"
echo "3. 是否有反复出现的问题应该写入配置？"
echo "4. 是否有规则因新模型能力而变得不必要？"
echo ""
echo "如有需要更新的配置，请在会话结束前提出修改建议。"
echo "====================="
