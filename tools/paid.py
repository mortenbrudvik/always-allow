"""The paid calls of the clip loop (BRIEF.md step 3): Seedance through OpenRouter, and the lip-sync repairs on fal,
behind one guard. Every cost goes to production/ledger.csv, once, and BRIEF.md's limits hold in code:
- no call that would take the ledger past the $150 pause or the $400 stop, counting the jobs still running at their
  estimates (tools/ledger.py);
- at most 3 paid jobs at once;
- a job is written down before it's submitted, so a crash mid-submit leaves it `unknown`, and nothing more is
  submitted until someone has checked the provider; a finished job's cost is logged exactly once, even across a
  crash (the row's stamp is saved before the row is written);
- a job is never resubmitted: a slow one is logged at its estimate after 40 minutes and collected later.

The jobs live in a JobStore (production/clips/jobs.json for the clip loop). The transports are passed in: an
openrouter_video.Client (whose transport is a plain function) and a fal_client-like module, so tests/test_paid.py
runs everything against fakes.

The endpoints, inputs and prices, as tools/openrouter_video.py and tools/lipsync_test.py checked them on
28-29 Sep 2026 (check them again before the first paid run):
  Seedance 2.5   POST openrouter.ai/api/v1/videos; usage.cost is the charge; about $0.23/s at 720p
  sync-2-pro     fal-ai/sync-lipsync/v2/pro, {video_url, audio_url, sync_mode: cut_off}, $5 a minute
  LatentSync     fal-ai/latentsync, {video_url, audio_url}, $0.20 a clip up to 40 s
"""
import datetime
import hashlib
import json
import os
import time
from pathlib import Path

import ledger
import openrouter_video as orv

MAX_JOBS = 3                  # BRIEF.md: at most 3 paid jobs at once
SLOW_S = 40 * 60              # a job still running after this is logged at its estimate and left to finish
SEEDANCE_ENDPOINT = "openrouter.ai/api/v1/videos"
FAL_MODELS = {  # name: (endpoint, extra inputs, estimated USD for s seconds)
    "sync-2-pro": ("fal-ai/sync-lipsync/v2/pro", {"sync_mode": "cut_off"}, lambda s: 5 / 60 * s),
    "latentsync": ("fal-ai/latentsync", {}, lambda s: 0.20 if s <= 40 else 0.005 * s),
}
OPEN = {"submitting", "pending", "in_progress", "queued", "running"}  # may still bill
DONE = {"completed", "failed", "cancelled", "expired", "rejected"}
REFUSAL_MARKS = ("SensitiveContent", "PrivacyInformation")  # ByteDance's face filter: unbilled, and not a failure


class Busy(RuntimeError):
    """MAX_JOBS jobs are open: collect one first."""


class Unknown(RuntimeError):
    """A submission failed in a way that may have created the job: nothing is submitted until it's checked."""


class Credit(RuntimeError):
    """HTTP 402 from the provider: stop generating and tell the owner (BRIEF.md)."""


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def is_refusal(text):
    return any(m in (text or "") for m in REFUSAL_MARKS)


class JobStore:
    """Every paid job, keyed by the caller's name for it, and the upload cache, in one JSON file."""

    def __init__(self, path):
        self.path = Path(path)
        self.data = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {"jobs": {}, "uploads": {}}

    @property
    def jobs(self):
        return self.data["jobs"]

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self.data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        for attempt in range(40):  # Windows refuses the swap while any other process has the file open (a reader)
            try:
                os.replace(tmp, self.path)
                return
            except PermissionError:
                if attempt == 39:
                    raise
                time.sleep(0.25)

    def add(self, key, **rec):
        if key in self.jobs:
            raise ValueError(f"job {key} exists; a job is never submitted twice")
        self.jobs[key] = {"key": key, **rec}
        self.save()
        return self.jobs[key]

    def open_jobs(self):
        return [j for j in self.jobs.values() if j["status"] in OPEN]

    def in_flight_usd(self):
        """What open or unknown jobs not in the ledger yet may cost, at their estimates."""
        return sum(j["estimate_usd"] for j in self.jobs.values()
                   if (j["status"] in OPEN or j["status"] == "unknown") and not j.get("ledger_time"))


def admit(store, estimate_usd, ledger_path):
    """Refuse a new paid job: while an unknown submission is unchecked, when MAX_JOBS are open, or when it would pass
    the pause or the stop (ledger.Paused, ledger.Stopped). Returns the ledger's total."""
    unknown = [j["key"] for j in store.jobs.values() if j["status"] == "unknown"]
    if unknown:
        raise Unknown(f"{', '.join(unknown)} may exist on the provider; check it and mark the job before submitting more")
    if len(store.open_jobs()) >= MAX_JOBS:
        raise Busy(f"{MAX_JOBS} paid jobs are open")
    return ledger.check(estimate_usd + store.in_flight_usd(), ledger_path)


def log_once(store, rec, usd, ledger_path):
    """Log a job's cost to the ledger exactly once: the stamp goes into the store before the row goes into the ledger,
    and a rerun that finds the row doesn't write it again."""
    if rec.get("ledger_time"):
        return rec["ledger_time"]
    pending = rec.get("ledger_pending")
    if pending and ledger.has_row(pending, rec["model"], ledger_path):
        rec["ledger_time"] = pending  # written just before a crash
    else:
        rec["ledger_pending"] = stamp = ledger.stamp_now()
        store.save()
        rec["ledger_time"] = ledger.log(rec["tool"], rec["model"], rec["endpoint"], rec["seconds"], usd, ledger_path, stamp=stamp)
    rec.pop("ledger_pending", None)
    store.save()
    return rec["ledger_time"]


def _slow(rec, clock):
    return clock() - datetime.datetime.fromisoformat(rec["submitted"]).timestamp() > SLOW_S


def _count_slow(store, rec, ledger_path):
    """A job still running past SLOW_S may bill: the ledger counts it now, at its estimate."""
    if not rec.get("ledger_time"):
        rec.update(cost_usd=round(rec["estimate_usd"], 4), cost_source="estimate (still running)", slow=True)
        log_once(store, rec, rec["estimate_usd"], ledger_path)


class Seedance:
    """Seedance 2.5 through OpenRouter: submit once, poll, settle the cost, download."""

    def __init__(self, store, client, ledger_path=ledger.LEDGER, clock=time.time):
        self.store, self.client, self.ledger, self.clock = store, client, ledger_path, clock

    def submit(self, key, body, tool="seedance"):
        seconds = body["duration"]
        estimate = orv.estimate(seconds)
        admit(self.store, estimate, self.ledger)
        rec = self.store.add(key, provider="openrouter", tool=tool, model=orv.MODEL, endpoint=SEEDANCE_ENDPOINT,
                             seconds=seconds, estimate_usd=round(estimate, 4), request=body, status="submitting",
                             submitted=now())
        try:
            job = self.client.submit(body)
        except orv.ApiError as e:
            if e.status == 402:
                rec.update(status="rejected", error=str(e), credit=True)
                self.store.save()
                raise Credit(f"{key}: {e}") from e
            if 400 <= e.status < 500:  # refused before it started: a 4xx isn't billed
                rec.update(status="rejected", error=str(e), refused=is_refusal(e.body))
                self.store.save()
                return rec
            rec.update(status="unknown", error=str(e))  # a 5xx can come after the job was created
            self.store.save()
            raise Unknown(f"{key}: submitting failed with {e}; the job may exist on OpenRouter") from e
        except Exception as e:
            rec.update(status="unknown", error=repr(e)[:500])
            self.store.save()
            raise Unknown(f"{key}: submitting failed with {e!r}; the job may exist on OpenRouter") from e
        rec.update(job_id=job["id"], generation_id=job.get("generation_id"), status=job.get("status", "pending"))
        self.store.save()
        return rec

    def poll(self, key):
        """One status check. A failed poll raises and changes nothing; the job is still there to poll again."""
        rec = self.store.jobs[key]
        if rec["status"] not in OPEN or not rec.get("job_id"):
            return rec
        st = self.client.status(rec["job_id"])
        rec.update(status=st.get("status", rec["status"]), last_poll=now(),
                   response={k: v for k, v in st.items() if k != "unsigned_urls"})
        if rec["status"] in orv.TERMINAL:
            self._settle(rec, st)
        elif _slow(rec, self.clock):
            _count_slow(self.store, rec, self.ledger)
        self.store.save()
        return rec

    def _settle(self, rec, st):
        """A completed job is billed; a failed one only if it reports a cost."""
        cost, source = (st.get("usage") or {}).get("cost"), "usage.cost"
        if cost is None and rec["status"] == "completed":
            cost, source = rec["estimate_usd"], "estimate"
        if cost is None:
            cost, source = 0.0, "none reported"
        logged_at = rec.get("cost_usd")  # the estimate, if it was logged while slow
        rec.update(cost_usd=round(cost, 4), cost_source=source, finished=now())
        if rec["status"] != "completed":
            rec["error"] = str(st.get("error") or st.get("failure_reason") or rec["status"])
            rec["refused"] = is_refusal(rec["error"])
        if rec.get("ledger_time"):
            if source == "usage.cost" and not ledger.replace(rec["ledger_time"], rec["model"], cost, logged_at, self.ledger):
                rec["ledger_warning"] = f"couldn't find the estimate row of {rec['ledger_time']} to set it to ${cost:.3f}"
        elif cost > 0:
            log_once(self.store, rec, cost, self.ledger)

    def download(self, key, dest):
        rec = self.store.jobs[key]
        dest = Path(dest)
        part = dest.with_name(dest.stem + ".part" + dest.suffix)
        self.client.download(rec["job_id"], part)
        os.replace(part, dest)
        rec["file"] = dest.as_posix()
        self.store.save()
        return dest


def _fetch(url, dest):
    import shutil
    import urllib.request
    with urllib.request.urlopen(url, timeout=300) as r, Path(dest).open("wb") as f:
        shutil.copyfileobj(r, f)


class Fal:
    """The lip-sync repairs on fal's queue, and the uploads that give Seedance and fal their public URLs."""

    def __init__(self, store, fal=None, ledger_path=ledger.LEDGER, clock=time.time, fetch=_fetch):
        if fal is None:
            from envfile import load_env
            load_env()
            if not os.environ.get("FAL_KEY"):
                raise SystemExit("Set FAL_KEY in .env or the environment.")
            import fal_client as fal
        self.store, self.fal, self.ledger, self.clock, self.fetch = store, fal, ledger_path, clock, fetch

    def upload(self, path):
        """A public URL for a file, uploaded once per content (fal storage)."""
        path = Path(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        ups = self.store.data.setdefault("uploads", {})
        if digest not in ups:
            ups[digest] = {"url": self.fal.upload_file(str(path)), "file": path.as_posix(), "uploaded": now()}
            self.store.save()
        return ups[digest]["url"]

    def submit(self, key, model, video_url, audio_url, seconds, tool="lipsync"):
        endpoint, extra, price = FAL_MODELS[model]
        estimate = price(seconds)
        admit(self.store, estimate, self.ledger)
        inputs = {"video_url": video_url, "audio_url": audio_url, **extra}
        rec = self.store.add(key, provider="fal", tool=tool, model=model, endpoint=endpoint, seconds=seconds,
                             estimate_usd=round(estimate, 4), inputs=inputs, status="submitting", submitted=now())
        try:
            handle = self.fal.submit(endpoint, arguments=inputs)
        except Exception as e:  # it may or may not exist: don't guess
            rec.update(status="unknown", error=repr(e)[:500])
            self.store.save()
            raise Unknown(f"{key}: submitting to {endpoint} failed with {e!r}; check fal's request history") from e
        rec.update(request_id=handle.request_id, status="queued")
        self.store.save()
        return rec

    def poll(self, key):
        rec = self.store.jobs[key]
        if rec["status"] not in OPEN or not rec.get("request_id"):
            return rec
        status = self.fal.status(rec["endpoint"], rec["request_id"])
        rec["last_poll"] = now()
        if isinstance(status, self.fal.Completed):
            try:
                result = self.fal.result(rec["endpoint"], rec["request_id"])
            except Exception as e:  # the request ended in an error (a face it can't find, say): not billed
                rec.update(status="failed", error=repr(e)[:500], cost_usd=0.0, cost_source="failed, not billed",
                           finished=now())
                self.store.save()
                return rec
            rec.update(status="completed", result_url=result["video"]["url"], finished=now(),
                       cost_usd=round(rec["estimate_usd"], 4), cost_source="estimate (fal reports no cost)")
            log_once(self.store, rec, rec["estimate_usd"], self.ledger)
        else:
            rec["status"] = "queued" if isinstance(status, self.fal.Queued) else "running"
            if _slow(rec, self.clock):
                if rec["status"] == "queued":  # never started: cancel it, unbilled
                    self.fal.cancel(rec["endpoint"], rec["request_id"])
                    rec.update(status="cancelled", error=f"still queued after {SLOW_S // 60} min, so cancelled",
                               cost_usd=0.0, cost_source="cancelled in the queue", finished=now())
                else:
                    _count_slow(self.store, rec, self.ledger)
        self.store.save()
        return rec

    def download(self, key, dest):
        rec = self.store.jobs[key]
        dest = Path(dest)
        part = dest.with_name(dest.stem + ".part" + dest.suffix)
        self.fetch(rec["result_url"], part)
        os.replace(part, dest)
        rec["file"] = dest.as_posix()
        self.store.save()
        return dest
