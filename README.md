# Always Allow

The full production record for the music video to **Always Allow**, a Suno song sung by an AI agent asking for "Always allow". The video was made end to end by Claude Code in six sessions between 28 and 30 Sep 2026, with the owner giving notes at checkpoints. It follows the method behind [@anabology's ESCAPE VELOCITY](https://x.com/anabology/status/2103534482930491441):

- **Midjourney v8.2** made every still, driven in the browser by Claude in Chrome.
- **Seedance 2.5** (through OpenRouter) made the moving and singing shots, each conditioned on its still and the exact slice of the vocal.
- **sync-2-pro** (through fal) repaired the lip sync, and the result was measured afterwards, not judged by eye.
- **Remotion** drew everything else in code, on the beat: every piece of type, UI, chart and transition, plus the print texture over the footage.

The video itself isn't in this repo.

## How the timing works

Nobody gave the agent a BPM. `tools/analyze_song.py` runs librosa's beat tracker on the MP3, keeps only the beats with kick and bass under them, and fits a smooth curve through those, because the tempo drifts between 133.97 and 134.43 BPM and a fixed grid would slip. Bar 0 is where the kick comes in at the first drop, and every 4th beat from there is a downbeat. The result, `production/analysis/song.json`, holds every beat and downbeat time. Everything in the compositor snaps to those times and to the word times in `production/analysis/words.json`, which come from force-aligning the lyric sheet to the vocal stem (wav2vec2, checked against Whisper).

## Reading order

1. `BRIEF.md`: the instructions every session started from, including the spending limits and the fixed rules.
2. `PLAN.md`: the song's section map, the first-pass treatment, the pipeline and the cost estimate.
3. `research/escape-velocity.md`: how the reference video was made.
4. `LESSONS.md`: what each session learned the hard way, from Midjourney's UI to Seedance's face filter. The other docs call it `HANDOVER.md`, its name during the run.
5. `production/storyboard/QA_NOTES.md`: the decisions at each checkpoint, the agent's own and the owner's.
6. `production/runlog.csv` and `production/ledger.csv`: what each session did, with its tool calls and tokens, and every paid API call.

## The run in numbers

- 6 sessions, about 3,700 tool calls and 1.1 billion tokens (`production/runlog.csv`).
- $76.60 across fal and OpenRouter (`production/ledger.csv`), plus a Midjourney subscription. The brief paused paid calls at $150 and set a hard stop at $400.
- 119 shots, 67 Midjourney plates, 31 Seedance clips (25 repaired with sync-2-pro), and 14 chapters of code graphics.

## Layout

```
Always Allow.mp3, Lyrics (Suno).txt   the song and its Suno lyric sheet
BRIEF.md, PLAN.md, LESSONS.md         the brief, the plan, the lessons from each session
research/                             the reference video; lip-sync model research
tools/                                Python: song analysis, alignment, the Midjourney and Seedance pipeline,
                                      sync checks, depth, mattes, tracking, delivery
tests/                                tests for the paid-call guard, the clip loop and the closure check
production/
  analysis/                           song.json (beat grid, sections), words.json (word times)
  storyboard/                         STORYBOARD.md, shots.json, board.py, Midjourney prompts and manifest,
                                      sync reports, QA notes
  style/                              STYLE_BIBLE.md, casting and look tests
  comp/                               the Remotion compositor (see ANIMATION_GUIDE.md)
  ledger.csv, runlog.csv              spend per call; one row per session
```

## What isn't included

Only the master MP3 is published. The Suno stems (`production/stems/`), the lip-sync test clips, the Midjourney plates, the Seedance clips, depth maps, mattes and renders are all left out, so the paths to them in the storyboard and sync reports point at nothing. Without them you can still rerun the song analysis, which reproduces `song.json` exactly, the tests and the lyric layout check. The studio falls back to storyboard cards where footage is missing. A full render needs the media.

## Setup

- **Python 3.12 or 3.13:** `python -m venv .venv`, then `.venv/Scripts/python -m pip install -r tools/requirements.txt -r tools/requirements-avsync.txt`. That covers `tools/analyze_song.py` and the tests (`.venv/Scripts/python -m unittest discover -s tests`). Each heavier tool has its own `tools/requirements-*.txt`.
- **Node 22:** in `production/comp`, `npm ci`, then `npm run scan` (it lists the media it finds and writes the git-ignored `src/data/*.generated.json`), then `npm run check:lyrics` or `npm run studio`.
- **Keys** for the paid tools (`FAL_KEY`, `OPENROUTER_API_KEY`) go in `.env`, which is git-ignored.

The commands in the docs are written for Windows (`.venv/Scripts/python`); on macOS and Linux use `.venv/bin/python`.

## License

The code and docs are under the MIT License (`LICENSE`). The song (`Always Allow.mp3`) and its lyrics (`Lyrics (Suno).txt`) aren't covered by it: all rights reserved.
