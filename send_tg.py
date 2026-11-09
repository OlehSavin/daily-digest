"""Send plain text from stdin to a Telegram chat, split into <=4000-char chunks on line breaks.

Needs TELEGRAM_TOKEN and TELEGRAM_CHAT_ID in the env file named by config "telegram_env".
"""
import sys

import requests
from dotenv import dotenv_values

import settings

env = dotenv_values(settings.get("telegram_env"))
text = sys.stdin.read().strip()

chunks, cur = [], ""
for line in text.splitlines(keepends=True):
    if len(cur) + len(line) > 4000:
        chunks.append(cur)
        cur = ""
    cur += line
if cur.strip():
    chunks.append(cur)

for c in chunks:
    r = requests.post(f"https://api.telegram.org/bot{env['TELEGRAM_TOKEN']}/sendMessage",
                      json={"chat_id": env["TELEGRAM_CHAT_ID"], "text": c}, timeout=30)
    print("telegram", r.status_code)
