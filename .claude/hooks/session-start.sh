#!/bin/bash
# 会话开始时输出动态上下文

BRANCH=$(git branch --show-current 2>/dev/null)
RECENT=$(git log --oneline -3 2>/dev/null)
CHANGED=$(git diff --stat HEAD 2>/dev/null)

echo "=== 会话上下文 ==="
echo "分支：$BRANCH"
echo ""
echo "最近提交："
echo "$RECENT"
if [ -n "$CHANGED" ]; then
  echo ""
  echo "未提交变更："
  echo "$CHANGED"
fi
echo "==================="
