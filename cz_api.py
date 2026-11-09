"""Minimal Corezoid API v2 client (signed requests).

Credentials are read from the Corezoid CLI config file: a list of folders,
each with stage_id, corezoid_url, api_login, api_secret, workspace_id, project_id.
"""
import hashlib
import json
import time

import requests

import settings


def creds(stage_id):
    path = settings.get("corezoid.credentials_path")
    for f in json.load(open(path))["folders"]:
        if f["stage_id"] == stage_id:
            return f
    raise KeyError(f"no credentials for stage {stage_id}")


def call(ops, stage_id):
    """POST a batch of ops. Signature: sha1(time + secret + body + secret)."""
    c = creds(stage_id)
    body = json.dumps({"ops": ops})
    ts = str(int(time.time()))
    sig = hashlib.sha1((ts + c["api_secret"] + body + c["api_secret"]).encode()).hexdigest()
    url = f"{c['corezoid_url']}/api/2/json/{c['api_login']}/{ts}/{sig}"
    r = requests.post(url, data=body.encode(), headers={"Content-Type": "application/json"}, timeout=60)
    r.raise_for_status()
    return r.json()
