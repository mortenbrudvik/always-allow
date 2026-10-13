# Animation guide: the Always Allow compositor

This is how the video is put together in code, and how to work on it. It is written for the animator agents
that will each take a chapter in parallel (BRIEF.md step 3, as ESCAPE VELOCITY did, `research/escape-velocity.md`),
and for whoever puts the footage in (step 6) and reviews it (step 7).

The compositor is a Remotion 4.0.530 project. One composition, `Main`, 1920×1080 at 24 fps, 6,662 frames
(277.6 s), is driven entirely by `production/storyboard/shots.json`. The soundtrack is `Always Allow.mp3`, unedited:
renders are silent and the render script muxes the song in with ffmpeg.

## Read first

1. `production/storyboard/STORYBOARD.md`: the idea, the chapter map, and your chapter's shots (the same data is in
   `shots.json`: times, bars, framing, place, lyric lines with their mode and zone, the graphic, the camera, the
   transition).
2. `production/style/STYLE_BIBLE.md`: palette, light, type, transitions, the graphics layer, what we never do, and
   the sources table (every fact on screen must be in it).
3. Your chapter file, `src/chapters/chNN.tsx`, and the chapter before and after yours (the cuts between chapters
   are yours to get right too).
4. The components in `src/components/`: `ui.tsx` (the permission window, the cursor, chat, terminal, toasts,
   stamps, tags, the big button), `cards.tsx` (boarding pass, CI panel, calendar, to-do list, JSON, receipt and
   more), `charts.tsx` (fatigue chart, bar comparisons, counters, window storm, spinner grid, facade and more).

## Running it

All commands run from the repo root.

| What | Command |
|---|---|
| The media server (the song and `production/` on 127.0.0.1:8765; the render scripts start it themselves) | `npm --prefix production/comp run media` |
| Remotion Studio, to scrub with the song | `npm --prefix production/comp run studio` (start the media server first) |
| A chapter's contact sheet (every shot's first and last frame, every line's first and last word, each graphic's entrance, each transition's middle) | `node production/comp/scripts/sheet.mjs ch05` → `production/qa/sheets/ch05.jpg` |
| Any frames as a sheet | `node production/comp/scripts/sheet.mjs frames 4600,4700,5030-5040 --name mysheet` |
| Stills, with each frame's render time | `node production/comp/scripts/render.mjs stills 5030,6545 --scale 1 --timing` |
| A stretch of the video with the song | `node production/comp/scripts/render.mjs range 5000-5300 --out production/qa/drop.mp4` |
| The animatic (640×360) | `node production/comp/scripts/render.mjs animatic` → `production/animatic/animatic.mp4` |
| The full render (1920×1080) | `node production/comp/scripts/render.mjs full` → `production/out/roughcut.mp4` |
| The 9:16 teaser (the `Teaser` composition, over the master from `tools/deliver.py master`) | `node production/comp/scripts/render.mjs teaser` → `production/out/always-allow_teaser_9x16.mp4` |
| Lossless stills, for the thumbnails | `node production/comp/scripts/render.mjs stills 40,3450,5176 --scale 1 --png --out DIR` |
| The lyric check | `npm --prefix production/comp run check:lyrics` |
| Where the lyric engine put one line, and the face boxes it cleared | `npx --prefix production/comp tsx production/comp/scripts/debug-line.ts 61` |
| Type check | `npm --prefix production/comp run typecheck` |
| Rebuild the board after editing `production/storyboard/board.py` | `.venv/Scripts/python tools/storyboard.py build` |

Never `cd` into `production/comp` from an agent session: use `--prefix` or the paths above.

## How a frame is made

`src/Video.tsx` draws, bottom to top:

1. **The shots** (`src/ShotView.tsx`), usually one, two during a transition. Each shot is:
   - **the footage** (`src/layers/Footage.tsx`): its clip if the clip exists, else its plate (a Seedance shot's
     plate is its clip's start frame), else its storyboard card (`src/layers/Card.tsx`). A dancer shot cuts the
     dancer out of her clip with its matte and copies her into the chapter's formation over the stage plate.
     Clips and plates go through the print pass (`src/layers/PrintPass.tsx`: the CMYK halftone, the grade and
     grain, on footage only);
   - **her tracking** (`src/layers/Tracking.tsx`): the face box, landmarks and a confidence;
   - **the chapter's graphic** for the shot: your code.
2. **The transitions' overlays** (`src/layers/Transitions.tsx`).
3. **The lyrics** (`src/layers/Lyrics.tsx`, placed by `src/lib/lyrics.ts`).
4. **The chrome** (`src/layers/Chrome.tsx`): the session clock, the tool-call and token counters, the mode flag,
   the bar and beat, the ticker. Its numbers are this run's real ones (`src/data/receipt.json`).
5. **Grain** over everything.

So your graphics sit over the footage and under the lyrics and the chrome.

## Your chapter file

Each chapter file exports one `spec: ChapterSpec` (`src/chapters/types.ts`); every entry is keyed by shot ID:

| Field | What it is |
|---|---|
| `graphics` | A component per shot: the explaining graphics and UI, drawn over the footage. |
| `camera` | A 2.5D camera move per shot (`Partial<Cam>`: `zoom`, `x`, `y`, `depth`, `rot`, `fx`, `fy`), over the default read from the board's camera text. |
| `formation` | Where the copies of a dancer stand in a dancer shot: `Slot[]` (feet at `x`, `y`, `h` tall, a `label`, `flip`, `opacity`, `back` for the card). |
| `footage` | Replaces a shot's footage layer entirely (ch03's 2×2 split, ch06's tower, ch14's flash-past). |
| `backdrop` | Set pieces the plate will have, drawn on the storyboard card only, behind its figures (ch12's light panel). |

Every component gets `ShotProps`: `shot` (its row in shots.json), `frame` (0-based, 24 fps), `t` (song seconds),
`lt` (seconds into the shot), `dur`, `p` (0–1 through the shot), `world` (`dark` or `light`), `face` (her face
box, which type and graphics never cover) and `proxy`.

Helpers:
- `src/lib/time.ts`: the song's own beat grid (`barTime(bar)`, `barAt(t)`, `beatIndex`, `eighthIndex`,
  `pulse`, `pulseDown`, `pulseEighth`). Bar 0 is the first drop; `barTime(35.5)` is beat 3 of bar 35.
- `src/chapters/util.ts`: `wordAt(line, i)`, `wordEnd`, `wordNamed(line, /keys/)` (word times from `words.json`,
  by line number), `inAt`/`outAt` (entrances and exits), `typed` (a typewriter), `lyricOf(line)` and
  `lyricBox(line)` (where the lyric engine put a line, so your graphic can stay off it), `fmtInt`.
- `src/lib/ease.ts`: `clamp`, `lerp`, the easings, `kf` (keyframes), `rnd(...seed)` (Remotion's `random`),
  `wob` (a seeded wobble).
- `src/lib/layout.ts`: `plannedFace`, `plannedBody`, the text `ZONES`, `intersects`.
- `src/lib/registry.ts`: `shotView()` draws any other shot (the flash-past), with `lite` for small tiles.

Anything a graphic enters on should enter on the word that names it: take the time from `wordNamed`, never type
a number of seconds.

## The rules

1. **Every frame is a pure function of its time.** Frames render out of order and in parallel. Use `rnd(seed…)`
   for randomness, never `Math.random`; never `Date`, timers, CSS animations or transitions, or state kept
   between frames. Seed with the shot ID and an index so neighbours differ.
2. **Time comes from the song**, never from a BPM: the beat grid drifts (`song.json`). Cuts are on the board's
   bars; words are on `words.json`'s times.
3. **Edit only your chapter file.** Another agent is writing the next chapter. A shared component in
   `src/components/` may gain a new prop with a default; changing what it draws needs a contact sheet of every
   chapter that uses it.
4. **Lyrics are the engine's.** Never draw a lyric word yourself: `src/lib/lyrics.ts` places every line by its
   board mode (masthead, coverline, subtitle, serif, mass) and zone, off her face, at 40 px or more, and the
   lyric check proves every word is on screen on its time. A graphic may echo a word (outlined copies behind it,
   as s043, s098 and s111 do), never replace it. To change a line's mode, zone or split, edit `board.py` and
   rebuild.
5. **Never over her face.** Use `face` (or `plannedFace`) and keep graphics off it; frame edges, the empty side
   of the shot and below her chin are yours.
6. **The palette is the style bible's** (`src/lib/theme.ts`): one terracotta accent per frame, and never on her.
   Type is Geist, Geist Mono and Instrument Serif Italic.
7. **Facts are sourced.** Every number or claim on screen is in STYLE_BIBLE.md's sources table, or is this run's
   own (`receipt.json`, written by `tools/receipt.py`). No new fact goes in until its source is in the table.
8. **The UI is a generic look-alike**, never a copy of any product's UI (BRIEF.md). Use the kit.
9. **Dense, ordered, readable in one glance**: at least three information layers in every frame (footage,
   lyric, graphic, tracking, chrome), and one idea per graphic (a hero screen makes its point in the ~3 s it's on).

## 2.5D treatments

A 2.5D shot is a plate over its depth map. The default move comes from the board's camera text
(`defaultCam` in `Footage.tsx`): push, very slow push, pull back or pull up, lateral drift, rotation (slow or
fast), crane up, tilt down, and punch-ins on downbeats. With a depth map, sideways moves separate the layers.
ESCAPE VELOCITY's rules hold here: never the same treatment on two 2.5D shots in a row, never just a still with
a slow zoom, and vary them within a chapter. Override a shot's move in `spec.camera`, and layer the graphics so
the frame is alive even when the plate barely moves.

## Transitions

Mostly hard cuts on the beat. A device is named on the incoming shot (`transition` in shots.json) and drawn by
`Transitions.tsx`: tab switch, window wipe, blink, session close, push-through, shape match, terminal scroll and
flash. The board check refuses the same device twice in a row. A device should come out of the graphics (the
window wipe opens a new window, the terminal scroll is a terminal); tune yours so its middle frame reads.

## Footage, as it arrives

The media scan (`scripts/scan-media.mjs`, run before every render) finds, under `production/`:

| File | What |
|---|---|
| `clips/selects/<clip>.mp4` | the accepted take, repaired if it speaks, conformed to 24 fps, no audio |
| `clips/mattes/<clip>.webm` | a dancer clip cut out with SAM 2 (VP9 with alpha) |
| `clips/tracking/<clip>.json` | her face landmarks and body boxes per frame |
| `assets/frames/<plate>.png` | the picked plate |
| `assets/depth/<plate>.png` | its depth map, for 2.5D shots |

The footage layer then shows the real thing without any change to your file. Points to know:
- **Clip timing.** A shot plays its clip from `clip_in_s` into the take. Hook shots reuse hook 1's clips
  (`shift_bars` 36 for hook 2, 81 for hook 3), so a hook-3 shot shows the same moves on the same beats. A shot with
  `hold_last_frame` freezes on the take's last frame (s091, s093 and s107 hold D3's crowd, all facing the lens).
- **Formations.** Every copy of a dancer shows the same frame of the matte, so the clones move in perfect sync.
  `Slot.delay` (a copy a few frames behind) is not drawn yet; it needs one video element per delay.
- **Tracking.** Until the tracking files exist, `Tracking.tsx` and the lyric engine use the planned boxes from
  the framing and `place`. Step 5 writes `clips/tracking/<clip>.json` as
  `{"fps": 24, "width": 1920, "height": 1080, "frames": [{"f": 0, "face": {"x", "y", "w", "h"} | null,
  "landmarks": [[x, y], …], "body": {"x", "y", "w", "h"} | null}, …]}`, in clip frames and frame pixels; the
  step that makes them wires them into `ShotProps.face`, `Tracking.tsx` and the lyric engine (a line's face box
  is then the union of her boxes over the line's time).
- **The planned geometry of the stages** lives in the chapters and must be moved to the picked plates: ch12's
  `HORIZON`, `PANEL` and `SIDE` (the rows' horizon and the light panel front-on and side-on), the laptop screens
  in ch01–ch04, the monitors in ch02, ch09 and ch13.
- **Real media is heavier than cards.** Measure your heaviest frames with `render.mjs stills … --timing` once a
  chapter has footage.

## The render budget

**At most 1.5 s a frame at 1920×1080**, per render worker on this machine (Windows 11, RTX 3090, Chrome with
ANGLE), measured with `node production/comp/scripts/render.mjs stills FRAMES --scale 1 --timing` after a first
warm-up frame. The full render runs 8 workers, so the budget keeps the 6,662 frames under about 21 minutes.

Measured on 29 Sep with storyboard cards (no footage yet): a typical frame takes about 0.4 s; the 256-window storm
(frame 4790) and the click's burst of windows (5045) about 0.95 s; the flash-past's 8×8 mosaic (6545) 1.19 s after
its tiles were slimmed to footage only.

With the footage (30 Sep), measure with `render.mjs range FRAMES` instead: a still of a clip shot seeks its video
cold and takes 4–5 s, which no frame of a real render does. The full render averages 0.44 s a frame per worker;
the heaviest stretches are the flash-past's mosaic (6490–6561) at 1.39 s, the storm (4770–4841) at 1.09 s and the
side-on formation (5540–5611) at 0.61 s, each including the workers' start. The mosaic's tiles draw small copies
(`assets/thumbs/plates/`, the dancers' cut-out stills), which keeps it inside the budget. Remotion logs decode
warnings for video frames during a render ("The source image cannot be decoded", a blob URL not found); they're
harmless: no frame of the cut holds still where its select moves. When a frame goes over: draw fewer elements (the far rows of a crowd as
a texture, not figures), skip the detail the frame can't show at its size, and prefer one SVG to many DOM nodes.

## QA

For each chapter, the art director renders the contact sheet (at least 28 frames), looks at every tile, and
returns at most 14 fixes, most important first; the animator applies them and renders again. The bars
(BRIEF.md step 7):
- every lyric word on screen on its time (the lyric check passes);
- at least three information layers in a frame;
- the main lyric at 40 px or more at 1080p (the engine enforces it);
- every frame within the render budget.

Judge each shot on: does the graphic show what the words mean, in one glance; is the lyric on the word, never
early; is it on the beat; is the frame dense but ordered; does the 2.5D treatment differ from its neighbours;
does the transition come out of the graphics; is type in empty fields and never over her face; is she on
model.

## Fit-ups done when the footage landed (session 5)

Every item that waited for the footage is done:
- s001: the window in her iris sits on her pupil, measured on C01's take, and goes as her lid closes.
- s004: the chat app is pinned to the laptop screen's corners (`quad` in `chapters/util.ts`); the typing box sits
  on his head. s025's small window already sat on the near-frontal screen.
- s013, s069, s108: `LitPlate` (`components/screens.tsx`) draws A_floor_ews's front-facing screens lit into the
  plate before the print pass, so they print with it; s013 switches them on at "Executing".
- s080: the storm's windows show a crop of her face (`production/assets/thumbs/agent_face.jpg`); s084's glass holds
  her face faintly (`agent_face_reflection.jpg`).
- ch12: `HORIZON`, `PANEL` and `SIDE` are measured on the picked plates. On the side-on wall (s099, s101, s102) the
  rows stand as on risers, three staggered rows with each copy clear of the next: packed tighter, copies of a matte
  smear into one mass (the user's note on the rough cut). A formation reads when each copy has a third of a figure
  of clear space.
- ch14: the receipt is the Agent's bill for the job in the song, not this production's (the user's call); the run's
  numbers stay in the chrome and the ticker.
- The grid of 49 (ch08) and the rows before the window wall (ch12) are raked and staggered the same way. In a
  formation shot her tracking box frames her copy (the slot labelled AGENT_01), never the matte's own frame.
- A chapter that replaces a shot's footage with something that doesn't show the clip full frame (s022's split, s044's
  pull-back) lists the shot in `untracked`, so her tracking box and the lyric engine don't use the clip's face there.
- s101: the rows run at double speed and freeze on "blink" (`clipTime` in a chapter spec).
- The tracking files and the plates' boxes are read by `src/lib/tracking.ts`: `ShotProps.face` and `track` are
  tracked where the data exists, moved by the footage's camera, and the lyric engine keeps each line clear of her
  face in every shot it's on screen over, and of the heads at the front of a formation.
- The dancer mattes carry her measured figure (`clips/mattes/<clip>.json`), so every copy stands on its slot's
  feet at its slot's height, and a still (`<clip>_still.png`) for the flash-past's small tiles.

Still open: s044's facade pull-back is drawn in code and assumes the lit window at the facade's centre, which reads
well enough; fit `lc`/`lr` if the plate is ever replaced.
