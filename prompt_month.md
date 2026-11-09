You are writing a monthly work summary for {{USER_NAME}} ({{USER_ROLE}}) for {{MONTH_HUMAN}}.

Below are the user's daily digests for this month (each already linked to Jira tickets {{JIRA_KEY}}-xxxx):

{{DAYS}}

## What to do
Build a monthly report SPLIT BY DAY: every day that has a digest is a separate block, in chronological order. Do not invent or add days without a digest. You may check a ticket title via `getJiraIssue` (cloudId via `getAccessibleAtlassianResources`) if useful; change nothing.

## Format (only the report itself, plain text for Telegram, no *, _, #, `). SHORT:

📆 Report for {{MONTH_HUMAN}}

DD.MM Day
• {{JIRA_KEY}}-xxxx <title, ≤ 5 words> — <result on that day, ≤ 4 words>
• ...

DD.MM Day
• ...

(day as in the daily digest header; up to 6 items per day, big tasks first, items without a ticket at the end of the day; the same ticket on different days — separate items with that day's result; spell a ticket's title the same way on every day)

🚨 <incidents of the month with dates, ≤ 10 words; omit if none>
🔧 <key processes of the month, comma-separated, no paths, nodes or leading "/">. This line is always LAST.

Forbidden: people's names, "with QA / together with", processes and nodes inside items, details, the 💬 lines from the daily digests. Write in {{LANGUAGE}}, invent nothing, no notes after the report.
