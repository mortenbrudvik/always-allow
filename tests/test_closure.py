"""The closure check's rule (tools/closure_check.py) and which letters close the lips (tools/align_lyrics.py), on
synthetic tracks: no video, no models.

  .venv/Scripts/python -m unittest discover -s tests
"""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import closure_check as cc  # noqa: E402
from align_lyrics import closures  # noqa: E402


def mark(frame, fps=24, start=100.0, word="me", letter="m"):
    return {"word": word, "letter": letter, "line": 0, "start": start + (frame + 0.5) / fps}


class Rule(unittest.TestCase):
    def test_a_closure_within_two_frames_of_its_letter_counts(self):
        for shut in (9, 13):  # two frames before the letter's frame 11, and two after: inside the window
            gap = np.full(48, 0.1)
            gap[shut] = 0.01
            rows, misses = cc.judge(gap, 24, 100.0, [mark(11)])
            self.assertEqual((rows[0]["frames"], rows[0]["closed"], misses), ([9, 10, 11, 12, 13], True, 0))

    def test_a_closure_too_early_or_too_late_misses(self):
        gap = np.full(48, 0.1)
        gap[8] = gap[14] = 0.01  # three frames either side
        _, misses = cc.judge(gap, 24, 100.0, [mark(11)])
        self.assertEqual(misses, 1)

    def test_only_the_letters_the_cut_shows_are_checked(self):
        import json
        import tempfile
        letters = Path(tempfile.mkdtemp()) / "letters.json"
        letters.write_text(json.dumps({"closures": [mark(11), mark(40, word="by", letter="b")]}), encoding="utf-8")
        gap = np.full(48, 0.1)
        gap[11] = 0.01  # the first closes; the second, after the edit, never does
        full = cc.check("x.mp4", 100.0, 2.0, gap=gap, fps=24, letters=letters)
        cut = cc.check("x.mp4", 100.0, 2.0, gap=gap, fps=24, letters=letters, shown=[(100.0, 101.5)])
        self.assertEqual((full["checked"], full["misses"], cut["checked"], cut["misses"], cut["passes"]), (2, 1, 1, 0, True))

    def test_a_frame_without_a_face_is_a_miss(self):
        gap = np.full(48, np.nan)
        rows, misses = cc.judge(gap, 24, 100.0, [mark(11)])
        self.assertEqual((rows[0]["seen"], misses), (False, 1))

    def test_how_many_misses_fail_a_clip(self):
        self.assertTrue(cc.verdict(0, 3))    # t3g
        self.assertTrue(cc.verdict(1, 2))    # t2r: borderline, passes
        self.assertFalse(cc.verdict(2, 5))
        self.assertFalse(cc.verdict(1, 1))   # its only closure missed
        self.assertTrue(cc.verdict(0, 0))    # nothing to check


class Letters(unittest.TestCase):
    def word(self, w):
        return [c for i, c in enumerate(w.upper()) if i in closures([(c, 0, 0) for c in w.upper()])]

    def test_which_letters_close_the_lips(self):
        self.assertEqual(self.word("job"), ["B"])
        self.assertEqual(self.word("bob"), ["B", "B"])
        self.assertEqual(self.word("complete"), ["M"])  # m-p close once
        self.assertEqual(self.word("phone"), [])        # ph sounds f
        self.assertEqual(self.word("climb"), ["M"])     # the b after a final m is silent
        self.assertEqual(self.word("number"), ["M"])


if __name__ == "__main__":
    unittest.main()
