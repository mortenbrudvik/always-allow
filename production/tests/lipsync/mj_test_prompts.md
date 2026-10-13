# Lip-sync test: Midjourney clips

Three short clips for the lip-sync test (`PLAN.md` phase 0b). The Agent isn't designed yet, so these are stand-ins. What the test measures is how each lip-sync model handles Midjourney footage.

## Make the clips

For each clip:
1. Generate the image from its prompt, and add your moodboard or `--p` code if you have one. Pick the result with the clearest, most frontal face.
2. Animate it: **Manual**, **Low motion**, with the motion prompt below. Set **Video Resolution** to **HD** under More Options. HD runs in fast mode only.
3. Don't extend it. The test line is 4.4 s and a clip is 5.2 s.
4. Download the MP4 into `clips/` next to this file as `t1.mp4`, `t2.mp4` and `t3.mp4`.

| Clip | What it tests |
|---|---|
| t1 | The main case: a still, frontal close-up |
| t2 | Small head movement, and hands in the frame |
| t3 | The hook look: high-key white studio light |

**t1**
- Image: `35mm photo, close-up portrait of a calm young woman looking straight into the lens, neutral expression, lips closed, lit by direct on-camera flash in a fluorescent office at 3 a.m., deep blacks, one warm terracotta accent, film grain --ar 16:9`
- Motion: `she stays still and looks into the lens, slow blink, subtle breathing, lips closed, static camera`

**t2**
- Image: `35mm photo, medium close-up of a calm young woman at a desk at night, facing the camera, lips closed, monitor glow and direct flash, deep blacks, terracotta lanyard, film grain --ar 16:9`
- Motion: `slight head tilt and a small nod, hands stay below the chin, lips closed, slow push-in`

**t3**
- Image: `high-key white studio, close-up of a calm young woman in a plain grey uniform with a chrome collar pin, facing the camera, lips closed, clean even light, a hard block of colour behind her --ar 16:9`
- Motion: `she holds still and looks into the lens, subtle breathing, lips closed, static camera`

"Lips closed" matters: Midjourney tends to add random mouth movement, and the lip-sync models work best from a still mouth.

Check each video before using it, and rerun it if the face turns away or the mouth opens. In the first test round, t1's "slow blink" became a look down with closed eyes for about 1.5 s in both takes, and t2's first take bowed her head so her hair covered her face; its rerun was usable.

## Run the test

The default window is bars 88–90, with the vocal stem from `production/stems/` if it's there. It holds "I'm here for your weekends. Your mor–", cut off mid-word; it was meant to be "You think I'm here for your job.", which starts at bar 86.4. Use `--start` and `--end` for an exact line (the times are in `production/analysis/words.json`). It runs LatentSync, Sync lipsync-2-pro and InfiniteTalk, for about $3–5 in total.

Run `.venv/Scripts/python tools/lipsync_test.py` from the repo root. The project's `.venv` has the pinned requirements, and the script reads `FAL_KEY` from `.env`.

Add `--dry-run` to check the setup without spending anything. `--bars` or `--start`/`--end` pick another line.

Each model call goes through fal's queue, and its request ID is written to `out/requests.txt`. After `--timeout` seconds (default 1200), a call still waiting in fal's queue is cancelled, which costs nothing. One that is already running is left to finish on fal, logged to the ledger at its estimated cost, and noted in `results.md`. To finish a partial run without paying twice, use `--clips t2,t3` for some clips and `--reuse` to keep results already in `out/`. InfiniteTalk can wait a long time for a free worker on fal, so expect it to be the slow one.

## Score it

Watch each `out/<clip>__compare.mp4` with the sound on. The panels run left to right, top to bottom, in the order `results.md` lists. Score each model 1–5 in `results.md`. A model passes with 4 or more overall on every clip. Pick the best one that passes; if none does, use the fallback in `research/midjourney-lip-sync.md`. `results.md` is only a working file: record the pick in `PLAN.md` phase 0b, which is what `BRIEF.md` checks.

The first round (28 Sep) picked Sync lipsync-2-pro; see `PLAN.md` phase 0b.
