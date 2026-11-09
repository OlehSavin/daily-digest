#!/bin/zsh
# Monthly report built from the daily digests -> <output_dir>/YYYY-MM.<mode>.md + Telegram.
# Usage: month.sh [YYYY-MM] [--no-send] [--tasks]
#   default: grouped by day;  --tasks: grouped by ticket
set -u
export PATH="$HOME/.local/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"

HERE="${0:A:h}"
cfg() { python3 "$HERE/settings.py" get "$1"; }

MONTH="$(date +%Y-%m)"; SEND=1; MODE=month
for a in "$@"; do
  case "$a" in
    --no-send) SEND=0 ;;
    --tasks) MODE=tasks ;;
    *) MONTH="$a" ;;
  esac
done
if [[ "$MODE" == tasks ]]; then
  PROMPT_FILE="$HERE/prompt_month_tasks.md"; TITLE="Task report for"
else
  PROMPT_FILE="$HERE/prompt_month.md"; TITLE="Report for"
fi

OUT_DIR="$(cfg output_dir)"; LOG="$OUT_DIR/.digest.log"; OUT="$OUT_DIR/$MONTH.$MODE.md"
LOCK="${TMPDIR:-/tmp}/daily-digest-$MODE.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "== $(date) already running, skip" >> "$LOG"; exit 0
fi
trap 'rmdir "$LOCK"' EXIT

echo "== $(date) $MODE digest for $MONTH" >> "$LOG"

# Daily digests of the month, without the raw-data <details> block.
export DAYS="$(for f in "$OUT_DIR"/$MONTH-??.md(N); do
  echo "### ${f:t:r}"; sed '/<details>/,$d' "$f"; echo; done)"

if [[ -z "$DAYS" ]]; then
  SUMMARY="📆 $TITLE $MONTH: no daily digests yet."
else
  MONTH_HUMAN="$(date -j -f %Y-%m-%d "$MONTH-01" '+%B %Y' 2>/dev/null || date -d "$MONTH-01" '+%B %Y')"
  PROMPT="$(python3 "$HERE/settings.py" render "$PROMPT_FILE" "MONTH_HUMAN=$MONTH_HUMAN")"
  cd "$(cfg claude_workdir)"
  SUMMARY="$(claude -p "$PROMPT" \
    --allowedTools "mcp__atlassian__getAccessibleAtlassianResources,mcp__atlassian__getJiraIssue" 2>>"$LOG" </dev/null)"
  [[ "$SUMMARY" == *"📆"* ]] && SUMMARY="📆${SUMMARY#*📆}"
fi

SUMMARY="$(printf '%s\n' "$SUMMARY" | sed -E '/^🔧/ s#(^🔧 *|[ ,(])/+#\1#g')"

[[ -z "$SUMMARY" ]] && { echo "empty month summary" >> "$LOG"; exit 1; }
echo "$SUMMARY" > "$OUT"; echo "saved $OUT" >> "$LOG"
(( SEND )) && echo "$SUMMARY" | python3 "$HERE/send_tg.py" >> "$LOG" 2>&1
exit 0
