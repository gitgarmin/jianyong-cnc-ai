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
  DELETE_COUNT=$((ENTRY_COUNT - MAX_ENTRIES))
  # 找到第 DELETE_COUNT+1 个 ## 标记的行号（从此处开始保留）
  CUT_LINE=$(awk '/^## / { count++; if (count == '"$((DELETE_COUNT + 1))"') { print NR; exit } }' "$EXP_FILE")
  if [ -n "$CUT_LINE" ]; then
    # 头部：第一个 ## 之前的所有行（标题、说明等）
    FIRST_ENTRY_LINE=$(awk '/^## / { print NR; exit }' "$EXP_FILE")
    HEADER_END=$((FIRST_ENTRY_LINE - 1))
    {
      head -n "$HEADER_END" "$EXP_FILE"
      tail -n +"$CUT_LINE" "$EXP_FILE"
    } > "$EXP_FILE.tmp"
    mv "$EXP_FILE.tmp" "$EXP_FILE"
  fi
fi
