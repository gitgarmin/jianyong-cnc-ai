#!/bin/bash
# 会话结束时自动记录变更摘要到经验文件
# 保留最近 50 条记录，自动裁剪旧条目

EXP_FILE=".claude/experience.md"
MAX_ENTRIES=50
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")

# 初始化文件（首次运行）
if [ ! -f "$EXP_FILE" ]; then
  {
    echo "# 会话经验记录"
    echo ""
    echo "> 自动生成，记录每次会话的关键变更。会话开始时读取最近 5 条。"
    echo ""
  } > "$EXP_FILE"
fi

# 获取变更摘要
CHANGED=$(git diff --stat HEAD 2>/dev/null)
LAST_COMMIT=$(git log -1 --format="%s" 2>/dev/null)

if [ -n "$CHANGED" ]; then
  {
    echo ""
    echo "## $TIMESTAMP"
    echo ""
    echo "最近提交：$LAST_COMMIT"
    echo ""
    echo '```'
    echo "$CHANGED"
    echo '```'
  } >> "$EXP_FILE"
fi

# 大小保护：超过 MAX_ENTRIES 条时裁剪旧条目，保留头部 + 最近条目
ENTRY_COUNT=$(grep -c '^## ' "$EXP_FILE" 2>/dev/null || echo 0)
if [ "$ENTRY_COUNT" -gt "$MAX_ENTRIES" ]; then
  HEADER=$(sed -n '1,/^## /{ /^## /!p; }' "$EXP_FILE")
  BODY=$(grep -A 1000 '^## ' "$EXP_FILE" | tail -n +"$(( (ENTRY_COUNT - MAX_ENTRIES) * 8 + 1 ))")
  {
    echo "$HEADER"
    echo "$BODY"
  } > "$EXP_FILE"
fi
