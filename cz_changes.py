"""List Corezoid processes / state diagrams that *I* changed on a given day, across all stages.

1. Walk each stage's folder tree breadth-first (parallel), keep objects whose change_time is today.
2. For each candidate, read its history and keep only my actions within the day
   (someone else may have touched the same process).

Usage: python3 cz_changes.py [YYYY-MM-DD]
"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime

import cz_api
import settings


def my_history(conv_id, stage_id, user_id, start, end):
    """Summarise my actions on one process within [start, end)."""
    c = cz_api.creds(stage_id)
    op = {"type": "list", "obj": "history", "obj_type": "conv", "obj_id": conv_id,
          "limit": 200, "offset": 0,
          "company_id": c["workspace_id"], "project_id": c["project_id"], "stage_id": stage_id}
    res = cz_api.call([op], stage_id)["ops"][0]
    actions, nodes, commits, times = {}, set(), 0, []
    for h in res.get("list", []):
        if h.get("user_id") != user_id or not (start <= h.get("create_time", 0) < end):
            continue
        times.append(h["create_time"])
        if h.get("obj") == "commit":
            commits += 1
            continue
        key = f"{h.get('type')} {h.get('obj')}"
        actions[key] = actions.get(key, 0) + 1
        title = (h.get("request") or {}).get("title")
        if title:
            nodes.add(title)
    fmt = lambda t: datetime.fromtimestamp(t).strftime("%H:%M")
    span = f"{fmt(min(times))}–{fmt(max(times))}" if times else ""
    return {"actions": actions, "nodes": sorted(nodes)[:15], "commits": commits, "my_edits_time": span}


def _list(folder_id, stage_id):
    c = cz_api.creds(stage_id)
    op = {"type": "list", "obj": "folder", "obj_id": folder_id,
          "company_id": c["workspace_id"], "project_id": c["project_id"], "stage_id": stage_id}
    res = cz_api.call([op], stage_id)["ops"][0]
    return res.get("list", []) if res.get("proc") == "ok" else []


def changed_on(day: date):
    cfg = settings.load()
    stages = {int(k): v for k, v in cfg["corezoid"]["stages"].items()}
    user_id = cfg["corezoid"]["user_id"]
    start = int(datetime.combine(day, datetime.min.time()).timestamp())
    end = start + 86400

    candidates = []
    for stage_id, stage_name in stages.items():
        queue, seen = [(stage_id, "")], set()  # stage root folder id == stage id
        with ThreadPoolExecutor(8) as ex:
            while queue:
                batch, queue = queue, []
                for (fid, path), items in zip(batch, ex.map(lambda q: _list(q[0], stage_id), batch)):
                    for it in items:
                        key = (it["obj_type"], it["obj_id"])
                        if key in seen:
                            continue
                        seen.add(key)
                        p = f"{path}/{it['title']}"
                        if it["obj_type"] == "folder":
                            queue.append((it["obj_id"], p))
                        elif start <= it.get("change_time", 0) < end:
                            candidates.append({
                                "stage": stage_name, "stage_id": stage_id,
                                "type": it["obj_type"], "id": it["obj_id"], "path": p,
                                "changed": datetime.fromtimestamp(it["change_time"]).strftime("%H:%M"),
                                "created_today": start <= it.get("create_time", 0) < end,
                                "description": (it.get("description") or "")[:200],
                            })

    with ThreadPoolExecutor(8) as ex:
        hist = list(ex.map(lambda o: my_history(o["id"], o["stage_id"], user_id, start, end), candidates))

    mine = []
    for o, h in zip(candidates, hist):
        if h["actions"] or h["commits"]:
            o.update(h)
            del o["stage_id"]
            mine.append(o)
    return mine


if __name__ == "__main__":
    d = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    t = time.time()
    res = changed_on(d)
    print(json.dumps(res, ensure_ascii=False, indent=1))
    print(f"# {len(res)} objects, {time.time() - t:.1f}s", file=sys.stderr)
