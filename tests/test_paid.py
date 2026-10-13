"""tools/paid.py and the ledger's limits, against fake OpenRouter and fal (no network, no keys, a temporary ledger).

  .venv/Scripts/python -m unittest discover -s tests
"""
import csv
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import ledger  # noqa: E402
import openrouter_video as orv  # noqa: E402
import paid  # noqa: E402


def body(seconds=6):
    return {"model": orv.MODEL, "prompt": "p", "duration": seconds, "input_references": []}


class FakeOpenRouter:
    """Scripted replies: `submit` is (status, json) for the POST; each poll pops the next status reply."""

    def __init__(self, submit=(202, {"id": "job-1", "status": "pending"}), polls=()):
        self.submit_reply, self.polls, self.calls = submit, list(polls), []

    def __call__(self, method, url, headers, data, timeout):
        self.calls.append((method, url))
        if method == "POST":
            status, reply = self.submit_reply
            if isinstance(reply, Exception):
                raise reply
            return status, {}, json.dumps(reply).encode()
        if url.endswith("/content?index=0"):
            return 200, {}, b"MP4"
        return 200, {}, json.dumps(self.polls.pop(0)).encode()


class FakeFal:
    class Queued:
        pass

    class InProgress:
        pass

    class Completed:
        pass

    class Handle:
        def __init__(self, rid):
            self.request_id = rid

    def __init__(self, states=("queued", "running", "completed"), fail=False):
        self.states, self.fail, self.cancelled = list(states), fail, []

    def upload_file(self, path):
        return f"https://fal.invalid/{Path(path).name}"

    def submit(self, endpoint, arguments):
        return self.Handle("req-1")

    def status(self, endpoint, rid):
        s = self.states.pop(0)
        return {"queued": self.Queued, "running": self.InProgress, "completed": self.Completed}[s]()

    def result(self, endpoint, rid):
        if self.fail:
            raise RuntimeError("no face found")
        return {"video": {"url": "https://fal.invalid/out.mp4"}}

    def cancel(self, endpoint, rid):
        self.cancelled.append(rid)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.ledger = self.tmp / "ledger.csv"
        self.store = paid.JobStore(self.tmp / "jobs.json")
        self.clock = [time.time()]

    def spend(self, usd):
        ledger.log("seedance", "earlier", "x", 1, usd, self.ledger)

    def rows(self):
        with self.ledger.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def seedance(self, fake):
        return paid.Seedance(self.store, orv.Client(key="k", transport=fake), self.ledger, clock=lambda: self.clock[0])


class LedgerLimits(Base):
    def test_the_pause_comes_first(self):
        self.spend(149.0)
        with self.assertRaises(ledger.Paused):
            ledger.check(1.5, self.ledger)
        self.assertEqual(ledger.check(0.9, self.ledger), 149.0)

    def test_the_stop_holds_even_if_the_pause_is_raised(self):
        self.spend(399.5)
        old = ledger.PAUSE_USD
        ledger.PAUSE_USD = 1000.0  # as if the owner raised the pause
        try:
            with self.assertRaises(ledger.Stopped):
                ledger.check(1.0, self.ledger)
        finally:
            ledger.PAUSE_USD = old

    def test_paused_and_stopped_are_over_budget(self):
        self.assertTrue(issubclass(ledger.Paused, ledger.OverBudget) and issubclass(ledger.Stopped, ledger.OverBudget))


class Guard(Base):
    def open_job(self, key, usd=1.0, status="running"):
        self.store.add(key, provider="openrouter", tool="seedance", model="m", endpoint="e", seconds=6,
                       estimate_usd=usd, status=status, submitted=paid.now())

    def test_three_jobs_at_once(self):
        for k in "abc":
            self.open_job(k)
        with self.assertRaises(paid.Busy):
            paid.admit(self.store, 1.0, self.ledger)

    def test_running_jobs_count_toward_the_pause(self):
        self.spend(140.0)
        self.open_job("a", 4.0)
        self.open_job("b", 4.0)
        with self.assertRaises(ledger.Paused):  # 140 + 8 in flight + 2.5 > 150
            paid.admit(self.store, 2.5, self.ledger)

    def test_an_unknown_submission_blocks_everything(self):
        self.open_job("a", status="unknown")
        with self.assertRaises(paid.Unknown):
            paid.admit(self.store, 0.1, self.ledger)

    def test_a_job_is_never_added_twice(self):
        self.open_job("a")
        with self.assertRaises(ValueError):
            self.open_job("a")


class SeedanceFlow(Base):
    def test_submit_poll_settle_download(self):
        fake = FakeOpenRouter(polls=[{"id": "job-1", "status": "in_progress"},
                                     {"id": "job-1", "status": "completed", "usage": {"cost": 1.39}}])
        s = self.seedance(fake)
        rec = s.submit("C01/t1", body())
        self.assertEqual((rec["status"], rec["job_id"]), ("pending", "job-1"))
        self.assertEqual(s.poll("C01/t1")["status"], "in_progress")
        self.assertFalse(self.ledger.exists())  # nothing billed until it ends
        rec = s.poll("C01/t1")
        self.assertEqual((rec["status"], rec["cost_usd"], rec["cost_source"]), ("completed", 1.39, "usage.cost"))
        s.poll("C01/t1")  # a finished job isn't polled or logged again
        self.assertEqual([r["estimated_usd"] for r in self.rows()], ["1.390"])
        dest = s.download("C01/t1", self.tmp / "take.mp4")
        self.assertEqual(dest.read_bytes(), b"MP4")

    def test_the_face_filter_is_a_refusal_not_a_failure(self):
        err = {"error": {"code": "InputImageSensitiveContentDetected.PrivacyInformation"}}
        s = self.seedance(FakeOpenRouter(submit=(400, err)))
        rec = s.submit("C01/t1", body())
        self.assertEqual((rec["status"], rec["refused"]), ("rejected", True))
        self.assertFalse(self.ledger.exists())

    def test_a_credit_error_stops(self):
        s = self.seedance(FakeOpenRouter(submit=(402, {"error": "insufficient credits"})))
        with self.assertRaises(paid.Credit):
            s.submit("C01/t1", body())
        self.assertEqual(self.store.jobs["C01/t1"]["status"], "rejected")

    def test_a_5xx_or_a_network_error_leaves_it_unknown(self):
        s = self.seedance(FakeOpenRouter(submit=(502, {"error": "upstream"})))
        with self.assertRaises(paid.Unknown):
            s.submit("C01/t1", body())
        self.assertEqual(self.store.jobs["C01/t1"]["status"], "unknown")
        s2 = self.seedance(FakeOpenRouter(submit=(0, TimeoutError("read timed out"))))
        with self.assertRaises(paid.Unknown):  # and the guard now refuses anything new
            s2.submit("C02/t1", body())

    def test_the_guard_runs_before_the_post(self):
        self.spend(149.0)
        fake = FakeOpenRouter()
        with self.assertRaises(ledger.Paused):
            self.seedance(fake).submit("C01/t1", body(8))
        self.assertEqual(fake.calls, [])
        self.assertNotIn("C01/t1", self.store.jobs)

    def test_a_slow_job_is_logged_at_its_estimate_then_corrected(self):
        fake = FakeOpenRouter(polls=[{"id": "job-1", "status": "in_progress"},
                                     {"id": "job-1", "status": "completed", "usage": {"cost": 1.2}}])
        s = self.seedance(fake)
        s.submit("C01/t1", body())
        self.clock[0] += 41 * 60  # past 40 minutes
        s.poll("C01/t1")
        self.assertEqual([r["estimated_usd"] for r in self.rows()], [f"{orv.estimate(6):.3f}"])
        s.poll("C01/t1")
        self.assertEqual([r["estimated_usd"] for r in self.rows()], ["1.200"])  # replaced, not added

    def test_a_failed_job_that_reports_no_cost_isnt_billed(self):
        fake = FakeOpenRouter(polls=[{"id": "job-1", "status": "failed", "error": "boom"}])
        s = self.seedance(fake)
        s.submit("C01/t1", body())
        rec = s.poll("C01/t1")
        self.assertEqual((rec["status"], rec["cost_usd"], rec["refused"]), ("failed", 0.0, False))
        self.assertFalse(self.ledger.exists())

    def test_a_crash_between_the_stamp_and_the_row_logs_once(self):
        self.store.add("j", provider="openrouter", tool="seedance", model="m", endpoint="e", seconds=6, estimate_usd=1.0,
                       status="completed", submitted=paid.now())
        rec = self.store.jobs["j"]
        rec["ledger_pending"] = stamp = ledger.stamp_now()
        ledger.log("seedance", "m", "e", 6, 1.0, self.ledger, stamp=stamp)  # the row got written, then the crash
        paid.log_once(self.store, rec, 1.0, self.ledger)
        self.assertEqual(len(self.rows()), 1)
        self.assertEqual(rec["ledger_time"], stamp)


class FalFlow(Base):
    def fal(self, fake):
        return paid.Fal(self.store, fal=fake, ledger_path=self.ledger, clock=lambda: self.clock[0],
                        fetch=lambda url, dest: Path(dest).write_bytes(b"MP4"))

    def test_submit_poll_settle_at_the_estimate(self):
        f = self.fal(FakeFal(states=("running", "completed")))
        f.submit("C01/t1/sync-2-pro", "sync-2-pro", "v", "a", 6)
        self.assertEqual(f.poll("C01/t1/sync-2-pro")["status"], "running")
        rec = f.poll("C01/t1/sync-2-pro")
        self.assertEqual((rec["status"], rec["cost_usd"]), ("completed", 0.5))  # $5 a minute
        self.assertEqual([(r["tool"], r["estimated_usd"]) for r in self.rows()], [("lipsync", "0.500")])
        f.download("C01/t1/sync-2-pro", self.tmp / "r.mp4")
        self.assertTrue((self.tmp / "r.mp4").exists())

    def test_a_request_that_errors_isnt_billed(self):
        f = self.fal(FakeFal(states=("completed",), fail=True))
        f.submit("k", "sync-2-pro", "v", "a", 6)
        self.assertEqual(f.poll("k")["status"], "failed")
        self.assertFalse(self.ledger.exists())

    def test_a_request_stuck_in_the_queue_is_cancelled(self):
        fake = FakeFal(states=("queued",))
        f = self.fal(fake)
        f.submit("k", "latentsync", "v", "a", 6)
        self.clock[0] += 41 * 60
        self.assertEqual(f.poll("k")["status"], "cancelled")
        self.assertEqual(fake.cancelled, ["req-1"])
        self.assertFalse(self.ledger.exists())

    def test_uploads_are_cached_by_content(self):
        f = self.fal(FakeFal())
        a = self.tmp / "a.png"
        a.write_bytes(b"same")
        b = self.tmp / "b.png"
        b.write_bytes(b"same")
        self.assertEqual(f.upload(a), f.upload(b))
        self.assertEqual(len(self.store.data["uploads"]), 1)


if __name__ == "__main__":
    unittest.main()
