"""Collect deterministic facts for the daily digest: time-tracker entries + my Corezoid changes.

Each source is isolated: if one fails, its error goes into the JSON and the digest still runs.

Usage: python3 gather.py [YYYY-MM-DD]  -> JSON on stdout
"""
import json
import os
import sys
from datetime import date

import settings


def tracker(day_iso):
    """Optional: a local time tracker exposing db.get_day_summary(day_iso)."""
    tracker_dir = settings.get("tracker_dir")
    if not tracker_dir:
        return {"skipped": "tracker_dir not configured"}
    sys.path.insert(0, os.path.expanduser(tracker_dir))
    try:
        from db import get_day_summary
        s = get_day_summary(day_iso)
    except Exception as e:  # the tracker must never break the digest
        return {"error": str(e)}
    return {
        "tasks_minutes": [[t, round(sec / 60)] for t, sec in s["tasks"]],
        "manual_entries": [{"minutes": m, "description": d, "task": t} for m, d, t in s["manual"]],
        "meetings": [{"title": t, "start": a[11:16], "end": b[11:16]} for t, a, b in s["meetings"]],
        "distractions": [{"reason": r, "minutes": m} for r, m in s["distractions"]],
        "work_minutes": round(s["total_work_seconds"] / 60),
    }


def corezoid(day):
    try:
        import cz_changes
        return cz_changes.changed_on(day)
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    day = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    print(json.dumps({"date": day.isoformat(),
                      "tracker": tracker(day.isoformat()),
                      "corezoid_my_changes": corezoid(day)},
                     ensure_ascii=False, indent=1))
