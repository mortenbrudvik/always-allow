"""tools/clip_loop.py end to end against the mocks, on a two-clip board in a temporary folder: no network, no keys,
and never the real board, report or ledger. Needs ffmpeg.

  .venv/Scripts/python -m unittest discover -s tests
"""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import clip_loop  # noqa: E402
import ledger  # noqa: E402
import openrouter_video as orv  # noqa: E402
import paid  # noqa: E402
from seedance_test import probe  # noqa: E402

SECONDS = 2


def board():
    def clip(cid, kind, plate, speaks, shots, start):
        return {"clip": cid, "kind": kind, "plate": plate, "speaks_on_camera": speaks, "seconds": SECONDS,
                "window": {"start": start, "end": start + SECONDS, "start_frame": int(start * 24)},
                "words": "hand me the keys" if speaks else "", "prompt": f"prompt for {cid}", "shots": shots}
    return {"clips": [clip("C1", "speak", "P1", True, ["s1"], 1.0), clip("D1", "dancer", "P2", False, ["s2", "s3"], 3.0)],
            "plates": [{"plate": "P1", "print_grade": True}, {"plate": "P2", "print_grade": True}],
            "shots": [{"id": s, "status": "planned"} for s in ("s1", "s2", "s3")]}


class FailingChecks(clip_loop.MockChecks):
    def closure(self, repaired, start, seconds, shown=None):
        return {"clip": str(repaired), "checked": 2, "misses": 2, "passes": False, "face_found": 1.0, "closures": []}


class Loop(unittest.TestCase):
    def setUp(self):
        import soundfile
        from PIL import Image
        self.tmp = Path(tempfile.mkdtemp())
        frames = self.tmp / "frames"
        frames.mkdir()
        rng = np.random.default_rng(1)
        for name in ("P1", "P2"):
            Image.fromarray((rng.random((360, 640, 3)) * 255).astype(np.uint8)).save(frames / f"{name}.png")
        t = np.arange(48000 * 8) / 48000
        soundfile.write(self.tmp / "vocals.wav", 0.2 * np.sin(2 * np.pi * 220 * t), 48000)
        soundfile.write(self.tmp / "song.wav", 0.2 * np.sin(2 * np.pi * 110 * t), 48000)
        (self.tmp / "shots.json").write_text(json.dumps(board()), encoding="utf-8")
        self.cfg = clip_loop.Config(shots=self.tmp / "shots.json", report=self.tmp / "sync_report.json",
                                    ledger=self.tmp / "ledger.csv", work=self.tmp / "work", frames=frames,
                                    vocals=self.tmp / "vocals.wav", song=self.tmp / "song.wav", poll_s=0.0)

    def loop(self, checks=None, fail_models=(), names=None):
        store = paid.JobStore(self.cfg.work / "jobs.json")
        fal = clip_loop.MockFal(self.cfg.work, fail_models=fail_models)
        self.cfg.work.mkdir(parents=True, exist_ok=True)
        seedance = paid.Seedance(store, orv.Client(key="k", transport=clip_loop.MockOpenRouter(store, self.cfg.work)),
                                 self.cfg.ledger)
        return clip_loop.Loop(self.cfg, seedance, paid.Fal(store, fal=fal, ledger_path=self.cfg.ledger, fetch=fal.fetch),
                              checks or clip_loop.MockChecks(self.cfg), names=names, log=lambda *a: None)

    def ledger_rows(self):
        if not self.cfg.ledger.exists():
            return []
        with self.cfg.ledger.open(newline="", encoding="utf-8") as f:
            return [(r["tool"], r["model"]) for r in csv.DictReader(f)]

    def statuses(self):
        return {s["id"]: s["status"] for s in json.loads(self.cfg.shots.read_text(encoding="utf-8"))["shots"]}

    def test_a_speaking_clip_is_repaired_and_a_dancer_accepted(self):
        report = self.loop().run()
        self.assertEqual(report["clips"]["C1"]["result"], "repaired")
        self.assertEqual(report["clips"]["D1"]["result"], "accepted")
        self.assertEqual(self.statuses(), {"s1": "synced", "s2": "clip", "s3": "clip"})
        for cid in ("C1", "D1"):
            info = probe(self.cfg.work / "selects" / f"{cid}.mp4")
            self.assertEqual((info["fps"], info["frames"], info["audio"]), (24.0, SECONDS * 24, None))
        self.assertEqual(sorted(self.ledger_rows()), [("lipsync", "sync-2-pro"), ("seedance", orv.MODEL), ("seedance", orv.MODEL)])
        self.assertTrue(report["clips"]["C1"]["inputs"]["graded"])  # the face went through the print grade
        self.assertIn("vocals", report["clips"]["C1"]["inputs"]["audio_source"])
        self.assertIn("song", report["clips"]["D1"]["inputs"]["audio_source"])

    def test_a_clip_whose_lips_never_close_is_dropped_at_the_cap(self):
        report = self.loop(checks=FailingChecks(self.cfg), names=["C1"]).run()
        e = report["clips"]["C1"]
        self.assertEqual((e["result"], len(e["takes"])), ("dropped", 1 + clip_loop.MAX_RETAKES))
        self.assertTrue(all(len(t["repairs"]) == 1 for t in e["takes"]))  # one sync-2-pro repair a take
        self.assertEqual(self.statuses()["s1"], "dropped")
        self.assertEqual(len(self.ledger_rows()), 6)

    def test_a_recheck_after_a_rule_change_brings_back_a_dropped_clip_without_calls(self):
        self.loop(checks=FailingChecks(self.cfg), names=["C1"]).run()
        rows = len(self.ledger_rows())
        loop = clip_loop.Loop(self.cfg, None, None, clip_loop.MockChecks(self.cfg), names=["C1"], log=lambda *a: None)
        self.assertTrue(loop.recheck(loop.clips[0]))
        e = json.loads(self.cfg.report.read_text(encoding="utf-8"))["clips"]["C1"]
        self.assertEqual((e["result"], e["takes"][0]["verdict"]), ("repaired", "repaired"))  # the first take that passes
        self.assertEqual(self.statuses()["s1"], "synced")
        self.assertNotIn("drop_reason", json.loads(self.cfg.shots.read_text(encoding="utf-8"))["shots"][0])
        self.assertEqual(probe(self.cfg.work / "selects" / "C1.mp4")["frames"], SECONDS * 24)
        self.assertEqual(len(self.ledger_rows()), rows)

    def test_the_pause_stops_submissions(self):
        ledger.log("seedance", "earlier", "x", 1, 149.9, self.cfg.ledger)
        loop = self.loop()
        report = loop.run()
        self.assertIn("Paused", loop.halt)
        self.assertEqual(report["clips"]["C1"]["takes"], [])
        self.assertEqual(len(self.ledger_rows()), 1)

    def test_latentsync_only_when_sync_2_pro_cant_process(self):
        report = self.loop(fail_models=("sync-lipsync",), names=["C1"]).run()
        reps = report["clips"]["C1"]["takes"][0]["repairs"]
        self.assertEqual([(r["model"], r["verdict"]) for r in reps], [("sync-2-pro", "could not process"), ("latentsync", "passes")])
        self.assertEqual(report["clips"]["C1"]["result"], "repaired")
        info = probe(self.cfg.work / "selects" / "C1.mp4")
        self.assertEqual(info["frames"], SECONDS * 24)  # the padding is trimmed off

    def test_a_rerun_after_the_end_changes_nothing(self):
        self.loop().run()
        before = (self.cfg.report.read_text(encoding="utf-8"), self.ledger_rows())
        self.loop().run()
        self.assertEqual(before[1], self.ledger_rows())
        self.assertEqual(json.loads(before[0])["clips"]["C1"]["result"], "repaired")

    def test_a_run_stopped_halfway_picks_up_where_it_left_off(self):
        self.loop(names=["C1"]).run(cycles=1)  # submits take 1, then stops as a crash would
        first = json.loads(self.cfg.report.read_text(encoding="utf-8"))
        self.assertEqual(len(first["clips"]["C1"]["takes"]), 1)
        report = self.loop(names=["C1"]).run()  # a new process: new objects over the same files
        self.assertEqual(report["clips"]["C1"]["result"], "repaired")
        self.assertEqual(len(report["clips"]["C1"]["takes"]), 1)  # nothing resubmitted
        self.assertEqual(sorted(self.ledger_rows()), [("lipsync", "sync-2-pro"), ("seedance", orv.MODEL)])

    def test_no_plate_means_waiting(self):
        (self.cfg.frames / "P2.png").unlink()
        report = self.loop(names=["D1"]).run()
        self.assertEqual(report["clips"]["D1"]["state"], "waiting for its plate")
        self.assertEqual(self.ledger_rows(), [])

    def test_the_lock(self):
        with clip_loop.Lock(self.cfg.work):
            lock = json.loads((self.cfg.work / "clip_loop.lock").read_text(encoding="utf-8"))
            self.assertTrue(clip_loop.pid_alive(lock["pid"]))
        self.assertFalse((self.cfg.work / "clip_loop.lock").exists())


if __name__ == "__main__":
    unittest.main()
