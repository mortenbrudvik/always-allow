"""The spend ledger, production/ledger.csv, and the safety net from BRIEF.md.

Every paid API call is one row, in the columns tools/lipsync_test.py writes:
time, tool (seedance, lipsync, edit or upscale), model, endpoint, seconds, estimated_usd.
estimated_usd is the cost the API reports where it gives one, otherwise the estimate from
PLAN.md section 6.

check() refuses a call that would take the ledger past the $150 pause or the $400 stop. The
ledger only learns a job's cost when the job ends, so callers pass the estimates of jobs still
running along with the new one (see tools/seedance_test.py in_flight()).
"""
import csv
import datetime
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "production" / "ledger.csv"
COLUMNS = ["time", "tool", "model", "endpoint", "seconds", "estimated_usd"]
PAUSE_USD = 150.0  # stop paid calls and ask before spending more (BRIEF.md: raised only with the owner's OK)
STOP_USD = 400.0   # stop for good


class OverBudget(RuntimeError):
    pass


class Paused(OverBudget):
    """The $150 pause: no paid call until the owner says to go on."""


class Stopped(OverBudget):
    """The $400 stop: no paid call, ever."""


def rows(path=LEDGER):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def total(path=LEDGER):
    return sum(float(r["estimated_usd"] or 0) for r in rows(path))


def check(planned_usd, path=LEDGER):
    """Raise Stopped or Paused (both OverBudget) if spending planned_usd would take the ledger past the stop or the
    pause."""
    spent = total(path)
    for limit, what, error in ((STOP_USD, "the $400 stop", Stopped), (PAUSE_USD, f"the ${PAUSE_USD:.0f} pause", Paused)):
        if spent + planned_usd > limit:
            raise error(f"the ledger is at ${spent:.2f}; ${planned_usd:.2f} more would pass {what}")
    return spent


def stamp_now():
    """A row's time stamp: to the microsecond, so no two rows share one."""
    return datetime.datetime.now().isoformat(timespec="microseconds")


def has_row(stamp, model, path=LEDGER):
    return any(r["time"] == stamp and r["model"] == model for r in rows(path))


def log(tool, model, endpoint, seconds, usd, path=LEDGER, stamp=None):
    """Append one row and return its time stamp, which with the model finds the row again (replace(), has_row()).
    Pass `stamp` when the caller has already recorded it, so a rerun after a crash can tell the row was written."""
    new = not path.exists()
    stamp = stamp or stamp_now()
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(COLUMNS)
        w.writerow([stamp, tool, model, endpoint, f"{seconds:.2f}", f"{usd:.3f}"])
    return stamp


def replace(stamp, model, usd, old_usd=None, path=LEDGER):
    """Set the cost of a row logged at `stamp` for `model` (and, if given, logged at `old_usd`), for example when a
    job logged at its estimate reports its real cost later. Rows that match all three are interchangeable, so the
    first is taken. Returns False if there's no such row. Writes through a temporary file."""
    table = rows(path)
    for r in table:
        if r["time"] == stamp and r["model"] == model and (
                old_usd is None or abs(float(r["estimated_usd"] or 0) - round(old_usd, 3)) < 5e-4):
            r["estimated_usd"] = f"{usd:.3f}"
            break
    else:
        return False
    tmp = path.with_suffix(".csv.tmp")
    with tmp.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(table)
    os.replace(tmp, path)
    return True
