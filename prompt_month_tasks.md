You are writing a monthly task report for {{USER_NAME}} ({{USER_ROLE}}) for {{MONTH_HUMAN}}.

Below are the user's daily digests for this month (each already linked to Jira tickets {{JIRA_KEY}}-xxxx):

{{DAYS}}

## What to do
Merge the days into one picture of the month, grouped by ticket: one ticket = one item, even if it was worked on for several days; the result is the final state at the end of the period. You may check a ticket's title or current status via `getJiraIssue` (cloudId via `getAccessibleAtlassianResources`) if useful; change nothing.

## Format (only the report itself, plain text for Telegram, no *, _, #, `). AS SHORT AS POSSIBLE:

📆 Task report for {{MONTH_HUMAN}}
• {{JIRA_KEY}}-xxxx <title, ≤ 5 words> — <result, ≤ 4 words>
• ...
(big tasks first; up to 15 items; items without a ticket at the end; small things as one item "Other: …")

🚨 <incidents, ≤ 10 words; omit if none>
🔧 <key processes, comma-separated, no paths, nodes or leading "/">. This line is always LAST.

Forbidden: people's names, "with QA / together with", processes and nodes inside items, details, dates. Write in {{LANGUAGE}}, invent nothing, no notes after the report.
