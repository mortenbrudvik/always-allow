"""A small client for OpenRouter's video API, for Seedance 2.5 (BRIEF.md, PLAN.md phase 4).

Submit once, poll about every 30 s, download the result, and read usage.cost for the ledger.
It never resubmits: a pending or running job can still finish and bill, so a slow job is left
running and collected later by its ID.

The endpoints, checked on 28 Sep 2026 against openrouter.ai's docs and GET /api/v1/videos/models:
  POST /api/v1/videos                       202 {"id", "generation_id", "polling_url", "status"}
  GET  /api/v1/videos/{id}                  status pending, in_progress, completed, failed, cancelled
                                            or expired; usage.cost is the charge in USD
  GET  /api/v1/videos/{id}/content?index=0  the MP4, with the same Authorization header
A 502 is an upstream failure and isn't billed.

The transport is a plain function, so tests can pass a fake one (see tools/seedance_test.py --mock).
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://openrouter.ai/api/v1"
MODEL = "bytedance/seedance-2.5"
TERMINAL = {"completed", "failed", "cancelled", "expired"}
USD_PER_S_720P = 0.23  # PLAN.md section 6: the estimate until the API reports usage.cost


class ApiError(RuntimeError):
    def __init__(self, status, body):
        super().__init__(f"HTTP {status}: {body[:500]}")
        self.status, self.body = status, body


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


_opener = urllib.request.build_opener(_NoRedirect)


def urllib_transport(method, url, headers, data, timeout):
    """Returns (status, headers, body). Redirects come back as 3xx, unfollowed, so the caller
    decides whether the Authorization header goes along."""
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with _opener.open(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), e.read()


def estimate(seconds):
    return USD_PER_S_720P * seconds


class Client:
    def __init__(self, key=None, transport=urllib_transport):
        if key is None:
            from envfile import load_env
            load_env()
            key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise SystemExit("Set OPENROUTER_API_KEY in .env or the environment.")
        self._key, self._transport = key, transport

    def _call(self, method, url, body=None, timeout=120, auth=True):
        headers = {"Accept": "application/json"}
        if auth:
            headers["Authorization"] = f"Bearer {self._key}"
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(body).encode()
        return self._transport(method, url, headers, data, timeout)

    def _json(self, method, path, body=None):
        status, _, raw = self._call(method, API + path, body)
        if status >= 300:
            raise ApiError(status, raw.decode(errors="replace"))
        return json.loads(raw)

    def submit(self, body):
        """POST the job once. A network error here leaves it unknown whether the job exists, so the
        caller must not retry blindly."""
        return self._json("POST", "/videos", body)

    def status(self, job_id):
        return self._json("GET", f"/videos/{urllib.parse.quote(job_id)}")

    def download(self, job_id, dest, index=0, timeout=600):
        url = f"{API}/videos/{urllib.parse.quote(job_id)}/content?index={index}"
        status, headers, raw = self._call("GET", url, timeout=timeout)
        for _ in range(5):  # follow redirects by hand; the key only goes to openrouter.ai
            if status not in (301, 302, 303, 307, 308):
                break
            url = urllib.parse.urljoin(url, headers.get("Location") or headers.get("location"))
            there = urllib.parse.urlparse(url)  # the key goes only to openrouter.ai, and only over https
            same = there.scheme == "https" and there.hostname == urllib.parse.urlparse(API).hostname
            status, headers, raw = self._call("GET", url, timeout=timeout, auth=same)
        if status >= 300:
            raise ApiError(status, raw.decode(errors="replace"))
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
        return dest
