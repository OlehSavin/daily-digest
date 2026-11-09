#!/bin/zsh
# Daily work digest: time tracker + Corezoid + Slack + Jira -> <output_dir>/<date>.md + Telegram.
# Usage: run.sh [YYYY-MM-DD] [--no-send]
set -u
export PATH="$HOME/.local/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$PATH"

HERE="${0:A:h}"
cfg() { python3 "$HERE/settings.py" get "$1"; }

DAY="$(date +%F)"; SEND=1
for a in "$@"; do
  case "$a" in
    --no-send) SEND=0 ;;
    *) DAY="$a" ;;
  esac
done

OUT_DIR="$(cfg output_dir)"; mkdir -p "$OUT_DIR"
OUT="$OUT_DIR/$DAY.md"
LOG="$OUT_DIR/.digest.log"

# One run at a time (a manual run and the launchd schedule can overlap).
LOCK="${TMPDIR:-/tmp}/daily-digest-day.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "== $(date) already running, skip" >> "$LOG"; exit 0
fi
trap 'rmdir "$LOCK"' EXIT

echo "== $(date) digest for $DAY" >> "$LOG"

# 1. Deterministic facts first — the model only links and summarises them.
export FACTS="$(python3 "$HERE/gather.py" "$DAY" 2>>"$LOG" </dev/null)"
DAY_HUMAN="$(date -j -f %F "$DAY" '+%d.%m.%Y %a' 2>/dev/null || date -d "$DAY" '+%d.%m.%Y %a')"
PROMPT="$(python3 "$HERE/settings.py" render "$HERE/prompt.md" "DATE=$DAY" "DATE_HUMAN=$DAY_HUMAN")"

# 2. Headless Claude with a read-only tool allowlist: it can search Slack and read Jira, nothing else.
cd "$(cfg claude_workdir)"
SUMMARY="$(claude -p "$PROMPT" \
  --allowedTools "mcp__claude_ai_Slack__slack_search_public_and_private,mcp__claude_ai_Slack__slack_search_public,mcp__claude_ai_Slack__slack_read_thread,mcp__claude_ai_Slack__slack_read_channel,mcp__claude_ai_Slack__slack_search_users,mcp__claude_ai_Slack__slack_read_user_profile,mcp__atlassian__getAccessibleAtlassianResources,mcp__atlassian__getJiraIssue,mcp__atlassian__searchJiraIssuesUsingJql" \
  2>>"$LOG" </dev/null)"

# 3. Post-processing guards.
# Drop any preamble the model adds before the digest header.
[[ "$SUMMARY" == *"🗓"* ]] && SUMMARY="🗓${SUMMARY#*🗓}"
# Telegram turns "/order" into a bot command — strip leading slashes on the 🔧 line.
SUMMARY="$(printf '%s\n' "$SUMMARY" | sed -E '/^🔧/ s#(^🔧 *|[ ,(])/+#\1#g')"

if [[ -z "$SUMMARY" ]]; then
  echo "empty summary" >> "$LOG"; exit 1
fi

# 4. Save the digest together with the raw facts (for audit and for the monthly report).
{
  echo "$SUMMARY"
  echo
  echo "<details><summary>Raw data</summary>"
  echo
  echo '```json'
  echo "$FACTS"
  echo '```'
  echo "</details>"
} > "$OUT"
echo "saved $OUT" >> "$LOG"

(( SEND )) && echo "$SUMMARY" | python3 "$HERE/send_tg.py" >> "$LOG" 2>&1
exit 0
