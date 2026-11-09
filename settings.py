"""Load config.json (see config.example.json) and render prompt templates.

CLI:
  python3 settings.py get <dotted.key>                 -> print a config value
  python3 settings.py render <template> [KEY=VALUE...] -> print the rendered prompt
     {{FACTS}} / {{DAYS}} are taken from the environment (they can be large).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.environ.get("DIGEST_CONFIG", os.path.join(HERE, "config.json"))


def load():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get(key, cfg=None):
    val = cfg or load()
    for part in key.split("."):
        val = val[part]
    return os.path.expanduser(val) if isinstance(val, str) and val.startswith("~") else val


def render(template_path, extra):
    cfg = load()
    values = {
        "USER_NAME": cfg["user"]["name"],
        "USER_ROLE": cfg["user"]["role"],
        "USER_EMAIL": cfg["user"]["email"],
        "JIRA_KEY": cfg["jira"]["project_key"],
        "JIRA_SITE": cfg["jira"]["site"],
        "LANGUAGE": cfg.get("language", "English"),
        "FACTS": os.environ.get("FACTS", ""),
        "DAYS": os.environ.get("DAYS", ""),
        **extra,
    }
    text = open(template_path).read()
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", str(v))
    return text


if __name__ == "__main__":
    cmd, *rest = sys.argv[1:]
    if cmd == "get":
        print(get(rest[0]))
    elif cmd == "render":
        extra = dict(a.split("=", 1) for a in rest[1:])
        print(render(rest[0], extra))
    else:
        sys.exit(f"unknown command: {cmd}")
