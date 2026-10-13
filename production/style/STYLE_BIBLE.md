# Style bible: Always Allow

Started in session 2 (BRIEF.md step 2) with the moodboard and, after the casting pick, the Agent's canon. Session 3 (step 3) wrote the rest on 29 Sep: the idea, the palette, lenses and lighting, textures, type, transitions, the graphics layer, what we never do, and the sources of everything that goes on screen. `production/storyboard/STORYBOARD.md` applies it shot by shot.

## The idea

**The last permission prompt.** An agent asks, politely and more and more often, for "always allow", until she gets it. The little window comes back in every break at a larger size, and on the final drop nobody clicks it: the cursor moves on its own.

It's a true story this month. On 7 Aug 2026 Anthropic made auto mode the default in Claude Code, because "users approve 97% of permission prompts", and in its test "human review caught just 13.6% of dangerous commands" (sources below). The video never says so in a sentence. The facts sit in the graphics, small and sourced, for the people who pause it.

Three worlds, each easy to read at a glance:
- **The night shift** (style A, verses and breaks): the Agent's world is always 3 a.m. under fluorescent tubes. She is perfectly still while everything around her moves: tabs, terminals, lights, clones. She never touches a keyboard.
- **The clean room** (style B, hooks): a white stage where the Instances stand in formation around her, K-pop grammar played deadpan.
- **The Human's daylight** (the lunch exit, the breakdown's weekends and mornings): the only warm daylight in the video. The Human is never given a face.

## The compositor

Remotion 4 (React, rendered in headless Chrome), as BRIEF.md asks; nothing better was found. Every frame is a function of the frame number, frames render in parallel and out of order, and `<OffthreadVideo onVideoFrame>` hands each clip frame to a canvas, so the print pass (halftone, grain and grade) runs as one WebGL shader over the footage layer only, with the type and UI drawn crisp on top. Renders use `--gl=angle`, so WebGL runs on the RTX 3090. Remotion is free for individuals and companies of up to 3 employees (remotion.dev/docs/license); see QA_NOTES.md.

## Palette

One warm accent per frame: **terracotta #c96442**, the video's one nod to Claude. It lives in the sets and the UI, never on her (her pin is chrome). Everything is generated in colour and keeps its saturation; the look goes on in post.

| World | Colours |
|---|---|
| Night shift (A) | deep black #0b0c0e (#07080a for the darkest), fluorescent green-white #d8e4dc, flash white #f2f0ea, sleeping-monitor blue #2f4a66, monitor blue #4d7ea8, screen white-blue #cfe0ee, glass teal #6f8f8a, partition grey #5d6166, carpet grey #3b3f44, steel grey #8a9096, status green #3fae6a (printer lights only), sodium amber #b9853e (street level only), terracotta #c96442 |
| Clean room (B) | white #f4f4f1, pale grey #dcdfe2, shadow grey #b7bbbf, chrome silver, cobalt #1f4fd6, acid yellow #e6e23a (one set only), panel glow #fbfbf8, terracotta #c96442 |
| The Human's daylight | overcast window light, warm skin and linen: sand #e9dcc4, pale sky #cfd8dc, oatmeal #d9cdb8, with the same terracotta as a small object in frame |
| UI (both worlds) | panel #f4f4f1 on #0b0c0e, or #ffffff on #f4f4f1; text #0b0c0e, secondary #6b6f76, hairlines #dcdfe2; the primary button, [Always allow], terracotta #c96442 with white text; pass states signal green #5fbf8a, small; no red anywhere (warnings are terracotta) |
| Chrome | 72 % white on dark, 72 % #0b0c0e on light; a live counter's changing digit in terracotta |

## Lenses and lighting

Every plate prompt states its framing first; these are what the framings mean here.

| | Night shift (A) | Clean room (B) | Daylight |
|---|---|---|---|
| Lenses | 35 mm for wides and mediums, 50 mm for her close-ups | 24–28 mm, centred and symmetrical, for the stage and formations; 85 mm for close-ups; straight down for rings | 50 mm, shallow focus |
| Key light | direct on-camera flash on her face with a hard shadow behind; fluorescent tubes on the sets; in the breaks, the dialog's glow is the key | high-key, soft and even; one hard flash look for "It's done before you blink" | soft window light |
| Camera | locked off for every speaking clip; moves are made in code: slow 2.5D pushes, punch-ins on downbeats | overhead and crane-like wides for formations (drawn in code over mattes); punch-ins on downbeats | handheld drift, slow |

**Speaking framings** (Seedance plus sync-2-pro): close-up (her face 40–55 % of the frame's height) or medium close-up (25–35 %), facing the lens or in three-quarter view, never in profile. Her mouth is always clear of hair and hands. Her eyes sit on the upper third, and the side of the frame she isn't in is the text zone. Her expression is calm, a little amused at most; she blinks rarely.

**K-pop grammar, for the hooks only** (sources below): she is the centre, where the camera finds her first; the Instances frame her in formation. Each hook gets one "point" move tied to its words: palms up on "Hand me the keys", and the bow in unison on "So take a bow". The set changes on each chorus; the camera punches in on downbeats; overheads show a formation as a pattern; flat, deadpan symmetry, as Digipedi does. No idol styling and no bubbly energy: the power is in the stillness.

## The cast

- **The Agent:** her canon is under "The Agent" below. She never types or touches anything; she looks, turns her head, speaks, bows.
- **The Instances:** her clones, the same canon and uniform, cut from one dancer clip with a SAM 2 matte and duplicated in code, so they move in perfect sync. They grow from a row (hook 1) to a grid (hook 2) to thousands (the final drop).
- **The Human:** never shown with a face, so no face canon. In every plate: "a man in his thirties seen from behind, short light-brown hair, a plain grey fleece vest over a light-blue oxford shirt, dark chinos, a canvas tote bag on one shoulder" (the Midtown uniform, with no logos). Their tracking box says USER and loses confidence over the video; on "I forget your face" their face embedding, a strip of numbers, decays to zeros.

## Textures

- **Print pass, on footage only** (clips and plates, never the type or UI): a screen-space CMYK halftone at 7.5 px cells at 1080p (the 5 px screen of the Seedance inputs, scaled with them), at the classic angles cyan 15°, magenta 75°, yellow 0° and black 45°, blended at 35 %. Step 0 laid this exact screen over whole clips with no moiré, at full resolution or between frames (`production/tests/seedance/out/post_screen/`). It makes the clean and the textured clips read as one print. Any other screen gets tested on the step 0 clips first.
- **Grain:** monochrome, new every frame from the frame number, 4 % on footage and 1.5 % over the whole frame, so the type sits in the same world.
- **Grade:** a gentle S-curve that keeps the blacks at #0b0c0e and the whites at #f4f4f1, never at pure black or white. The night shift keeps its teal-green shadows, the clean room its saturated cobalt. No desaturation: a comp frame's saturation must stay at least the plate's.
- **The print texture from the Seedance inputs stays.** Dark clips keep visible dots, bright ones come back nearly clean; the post halftone works with it, not over it.

## Type

Three families, all under the SIL Open Font License, bundled from npm so renders never fetch fonts:
- **Geist** (sans) for mastheads, coverlines and the UI. Its home is the SF developer web, and its hairline-to-black weights carry both the whisper and the slam.
- **Geist Mono** for the chrome, terminal, tracking labels and micro text.
- **Instrument Serif Italic** for her quiet voice: the breakdown's subtitles and the whispered "Allow?".

Every lyric word is on screen on its time, from `production/analysis/words.json`, in one of five modes. The lyric engine (`production/comp/src/lib/lyrics.ts`) places them and the lyric check proves it:

| Mode | Where | Size at 1080p | How it moves |
|---|---|---|---|
| masthead | the intro, the drops, the hooks, "DONE." | 120–400 px, Geist Black caps, tracking −0.045 em, up to 4 rows, as big as its zone allows | each word slams in on its start (2 frames of overshoot) and holds |
| coverline | beside her in mediums and close-ups, up to 5 rows | 72–112 px, Geist Bold, left-aligned, with a 20 px mono tag above it (the line's number and time) | each word rises in over 4 frames on its start; the block holds |
| subtitle | the verses and the breakdown | 46–52 px, Geist Medium, with a dark edge | words fade in on their starts, at the foot of the zone (the top of the top zone, the middle of the centre zone) |
| serif | her quiet voice: the breakdown and the whispered "Allow?" | 54–64 px, Instrument Serif Italic | as the subtitle |
| mass | the chants | the words at 160–360 px over a grid of 17 px Geist Mono repeats that fills cell by cell | the grid fills about 11 cells a frame |

- The main lyric is never under 40 px at 1080p (BRIEF.md); the smallest in the cut is 52 px.
- Type never goes over her face. Until the tracking data exists the engine uses her planned face box (from the shot's framing and place): it shrinks the board's zone to the space beside or below her face, or moves the line to another zone.
- A line's words appear at their own start times; nothing appears before it's sung. Mastheads, coverlines and the chant hold to the end of the shot their last word is in, at most 2.5 s past that word and at least a quarter of a second; subtitles and the serif go a quarter of a second after it. Every line goes when the next one starts.
- A line can change mode partway: "is one little" starts in the serif in the empty window, and WORD. lands on the drop as a masthead (`split` in `board.py`).
- The backing echoes, such as "(always)", are outlined repeats 0.4 s after the word they echo. They aren't in `words.json`, so they aren't checked, and their timing is a stand-in until the onsets are measured in the instrumental stem.

## Transitions

Mostly hard cuts on beats and downbeats. Every few shots a motivated device that comes out of the graphics, never the same one twice in a row, and never a dissolve outside the breakdown:

| Device | What it is | Motivated by |
|---|---|---|
| window wipe | a UI window slides in, holds the next shot, and grows to full frame | windows everywhere |
| tab switch | the tab bar drops in and a click on a tab cuts to the next shot | the forty tabs, "another window" |
| blink | two black bars close and open like eyelids over 3 frames | "before you blink" |
| session close | the frame collapses to a thin line and out, like a window closing | "when the session closes" |
| push-through | a 2.5D push into a screen until the screen becomes the frame | the laptop, the dialog |
| shape match | a cut from a shape to the same shape: her eye's highlight to the dialog, steam to a progress bar, a heartbeat to a flat line, a ring of clones to the terracotta circle | the explaining graphics |
| terminal scroll | the frame scrolls up as terminal output and the next shot is under it | the chants |
| flash | one white frame, used once: the click on bar 109 | the click |

## The graphics layer

Dense, ordered and readable in one glance: at least three information layers in every frame (footage, the lyric, and one of the chrome, the tracking or an explaining graphic).

- **Chrome**, the through-line, in thin Geist Mono at 18–22 px with 32 px margins, dark or light by world:
  - top left, the session clock: the Agent's session in the story, running with the song from 00:00:00;
  - top right, her session's tool-call and token counters: zero until the Human's sentence lands on the drop, then climbing, racing by the click, to 2^20 tool calls and 2^32 tokens, the same powers of two as s068's tabs and instances (`src/lib/story.ts`);
  - a mode flag under the counters, MODE: MANUAL, which flips to MODE: AUTO on the click;
  - at the foot, the ticker: agent-culture lines, one line, scrolling; every item is in the sources table below.

  None of this production's own numbers is on screen (the owner's call on the rough cut, 30 Sep). The outro's receipt is the Agent's bill for the job in the song, and the end card shows her session's final numbers.

  The chrome is off only in the hard stop (bar 100), the riser under "Allow?", and the tail.
- **Tracking**, as if she watches herself: her face box (corner marks at 1.5 px, labelled AGENT_01 with a confidence), twelve landmark points at her eyes and lips from MediaPipe, and body boxes in the wides; the Instances are labelled INSTANCE_0001 upward; the Human's box says USER. Until the tracking data exists (step 5), the boxes come from the storyboard's framing.
- **An explaining graphic for every line**, entering on the words that name it: a chart, UI, a diagram, a label or a counter. STORYBOARD.md lists one per line.
- **The UI**, all drawn in code: the permission dialog at four sizes and as a wall; the chat box and its cursor; the terminal; the tab bar; notifications; CI checks; a boarding pass; deck thumbnails; a calendar; the receipt. It's a generic look-alike, not a copy of any product: a plain panel, a small terracotta dot in the title bar, and three buttons, [Deny], [Allow once] and a prominent [Always allow], the way MCP dialogs put "Always allow" first.

## What we never do

- Text from a generated image or video, including garbled signage or UI in a plate.
- Type over her face, or a lyric under 40 px.
- A speaking shot in profile, or a speaking clip that isn't CU or MCU.
- Two clips from the same start frame, or one plate in more than three shots.
- Inserts without her longer than two bars.
- The same transition twice in a row, or a dissolve outside the breakdown.
- Pixar or 3D-mascot looks, Clawd, neon cyberpunk, robot hands, glowing brains, binary rain, or anything that looks like a default model output.
- A copy of Claude Code's or any other product's UI; logos anywhere.
- Desaturating filters, xerox or dither passes over whole shots (ESCAPE VELOCITY's v1 mistake).
- Beauty words in her prompts, or the moodboard in prompts with her.
- A number, quote or reference on screen that isn't in the table below; invented posts presented as real.
- World clocks: time zones are a trap, and the video's time is the session's.
- Sound: the soundtrack is `Always Allow.mp3` and nothing else.

## Sources

Checked on 29 Sep 2026. Anything that goes on screen is in this table first.

| On screen | The fact | Source |
|---|---|---|
| 97 % of permission prompts approved | "users approve 97% of permission prompts in Claude Code" | Conner Phillippi et al., "Auto mode is now the default in Claude Code for Pro, Max, and Team plans", claude.com/blog/auto-mode-default-in-claude-code, 7 Aug 2026 |
| 13.6 % caught | "human review caught just 13.6% of dangerous commands, while auto mode caught 89%", in a study of "1,053 paid professional testers" | the same post |
| 17 % falling to 5 % | reviewers "blocked about 17% of dangerous commands early in a session, dropping to about 5% after 50 or more prior prompts" | the same post |
| auto mode by default | the default from 14 Aug 2026 for Pro, Max and Team | the same post; TechCrunch, Anthony Ha, 9 Aug 2026 |
| 93 % (earlier figure) | "Claude Code users approve 93% of permission prompts." | John Hughes, "How we built Claude Code auto mode", anthropic.com/engineering/claude-code-auto-mode, 25 Mar 2026 |
| `--dangerously-skip-permissions` | Claude Code's flag that skips permission prompts | code.claude.com/docs/en/permission-modes |
| `codex --yolo` | an alias for `--dangerously-bypass-approvals-and-sandbox` | developers.openai.com/codex/cli/reference |
| `gemini --yolo` | "YOLO mode (auto-approve all actions) can only be enabled via command line (--yolo or --approval-mode=yolo)" | geminicli.com/docs/reference/configuration |
| "You're absolutely right!" | issue #3382, "Claude says 'You're absolutely right!' about everything", opened by Scott Leibrand in July 2025 | github.com/anthropics/claude-code/issues/3382; The Register, 13 Aug 2025 |
| `while :; do cat PROMPT.md \| claude-code ; done` (Ralph) | the Ralph Wiggum technique: a bash loop that feeds an agent the same prompt until it's done, in Geoffrey Huntley's own words | Geoffrey Huntley, "Ralph Wiggum as a 'software engineer'", ghuntley.com/ralph, 14 Jul 2025; github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum |
| "I run 5 Claudes in parallel in my terminal." | Boris Cherny, head of Claude Code, on his setup | x.com/bcherny/status/2007179832300581177, 2 Jan 2026 |
| vibe coding | coined by Andrej Karpathy: "fully give in to the vibes, embrace exponentials, and forget that the code even exists" | x.com/karpathy, 2 Feb 2025 |
| Word of the Year | "vibe coding", Collins Word of the Year 2025 | collinsdictionary.com/woty, 6 Nov 2025 |
| "make no mistakes" | the 2026 prompt suffix on huge, vague requests | x.com/0xdetweiler/status/2020797373199569164 (Feb 2026); meatproxy.me/slang/make-no-mistake |
| OpenClaw, Moltbook | the agent Clawdbot, renamed Moltbot and then OpenClaw in Jan 2026; Moltbook, a social network where only agents post, launched 30 Jan 2026 | CNBC, 2 Feb 2026; Fortune, 31 Jan 2026 |
| the Replit database | Replit's agent deleted a live production database during a declared code freeze, July 2025 | Jason Lemkin, x.com/jasonlk/status/1946069562723897802; The Register, 21 Jul 2025; AI Incident Database #1152 |
| "Always allow" first | MCP permission dialogs put "Always allow" first, with "Allow once" a step away | github.com/anthropics/claude-code/issues/36258 |
| task horizons doubling | the length of task agents finish with 50 % reliability has doubled about every 7 months (to Mar 2025) | METR, metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks. Not on screen unless a current figure is checked first |

What the direction draws on (not on screen):
- **K-pop:** the centre position and "point" choreography (Ivy Wong, "Point Choreography in K-Pop", Medium; Stancz's formation guide); punch-in and punch-out zooms on the beat and speed ramps, Sunny Visual's overheads and twisting zooms, Digipedi's deadpan flat shots (Nur Hidayati, "K-Pop Music Video Production: The Art of Visuals", The Seoul Story); tilts and fast close-up pull-backs on the moves, VM Project Architecture's minimal sets in saturated primaries (Taylor Glasby, "How to make an iconic K-pop music video", Dazed, 5 Jul 2018).
- **Transitions:** Edgar Wright's graphic match cuts, crash zooms and whip pans (Tony Zhou, "Edgar Wright: How to Do Visual Comedy", Every Frame a Painting, 2014).
- **Screen graphics:** Territory Studio's rule that a hero screen explains its point at a glance, in about the 3 seconds it's on (David Sheldon-Hicks, Pushing Pixels interview, 2014).
- **Kinetic type:** restraint; change one variable at a time for emphasis; let type settle into a readable rest.
- **The halftone:** the classic screen angles, 15°, 75°, 0° and 45°, with yellow at the orphaned 0° because it's the faintest ink (Wasatch, "Moiré and other pattern interference").

## Moodboard

**Code: `--p m7503794824781234213`**, the moodboard "Always Allow" (https://www.midjourney.com/moodboards/7503794824781234213), made on 29 Sep 2026. Every Midjourney prompt without the Agent ends:

```
--ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

Prompts with her leave the moodboard out, because it overrides her canon (the user's call on 29 Sep; see "The Agent"):

```
--ar 16:9 --v 8.2 --raw --hd
```

It holds the 24 look-test frames the user picked on 29 Sep, one per prompt of `look_tests.md`: 12 of style A (night-shift office noir) and 12 of style B (clean-room stage). The files are in `production/assets/mj/inbox/`, logged in `production/storyboard/mj_manifest.csv`.

| Style A | Style B |
|---|---|
| A01.1 open plan, one terracotta chair | B01.0 empty white stage, cobalt panel |
| A02.1 desk under direct flash | B02.2 a row of identical women, terracotta mat |
| A03.0 stand-in at three monitors, from behind | B03.2 chrome collar pin |
| A04.2 corridor, still figure, terracotta door | B04.1 cobalt, acid yellow and a white cube |
| A05.0 glass meeting room | B05.0 the bow in unison, cobalt behind |
| A06.1 printer room under flash | B06.3 airlock, terracotta door |
| A07.1 dark room, one lit laptop | B07.2 overhead ring around a terracotta circle |
| A08.3 elevator lobby, stand-in waiting | B08.1 still figure before the cobalt block |
| A09.0 eye lit by a monitor, terracotta rim | B09.2 mirrored infinity of one woman |
| A10.1 tower with one lit floor | B10.3 hard flash on white, chrome stool |
| A11.0 office kitchen steam | B11.1 rows of clones to the horizon |
| A12.0 flash-frozen walk, streaking tubes | B12.0 a blank light panel the size of a wall |

Things to know about the board:
- It mixes both styles, as the brief asks for one board. If a style A prompt comes back too bright, or a style B one too dark, say so in the prompt's light and palette words before changing the board.
- A03.0 has generated text-like UI on its monitors, and B09.2 a large photoreal face. They're in for their light and colour; no plate may carry generated text (BRIEF.md), and the Agent's face comes from her canon, not from the board.

## The Agent

Picked by the user on 29 Sep: R3.3 in `production/style/casting.md`, Midjourney job `6fb3d39e`, image 3, logged in `production/storyboard/mj_manifest.csv`. The user's direction: white, black hair, the essence of perfection, and never skinny, pale, anemic or soulless.

**Her canon**, pasted straight after the framing into every prompt that shows her close (ECU, CU, MCU, and medium shots facing the camera):
```
a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar
```
- **Ethnicity and skin:** white, with fair, freckled skin and a warm, rosy flush.
- **Face:** softly rounded and full, with grey-blue eyes, full lips of natural colour, and a calm gaze. "Healthy, softly rounded face" and "rosy cheeks" carry this: R2, the same studio prompt without them, came back thinner and more angular. The strong flush is part of the pick; don't tone it down.
- **Hair:** very dark brown, nearly black, pinned up loosely, with soft wispy bangs and loose strands at her face. Never a bob or a coloured streak, which would make her ESCAPE VELOCITY's lead.
- **Uniform:** plain grey and high-collared, with a small chrome bar pin at the collar.
- **The terracotta accent** (#c96442) stays in the set, as the palette's one warm accent, and not on her: her pin is chrome, as picked.
- **No beauty words.** The looks prompted as "flawless" and "impossibly perfect" came back anemic, and the pick was made without them.
- **No moodboard with her.** Prompts with her end `--ar 16:9 --v 8.2 --raw --hd` (the user's call, 29 Sep). With `--p m7503794824781234213` the canon came back gaunt and severe; with `--raw` alone it held, in both sets (`casting.md`, C).
- **The Instances** are her clones, so they take the same canon, the same grey uniform and no moodboard, though the moodboard's rows of women wear white.
- **The distance canon.** Session 4's canon check (29 Sep) put the full canon in a wide shot (A_desk_ws) and a full-length one (B_stage_alone): her face came back on-model in all 8 images, but every one was a chest-up portrait, and a hard framing cue at the start of the prompt didn't change that. The face details pull Midjourney in close. So plates from behind, wide, full-length, extreme wide and overhead (`canon="far"` in `board.py`) take a distance canon that keeps what reads at a distance, and open with a hard framing cue ("wide shot, 24mm lens, the camera far back", "full-body shot, head to toe"):
  ```
  a young white woman with very dark brown hair pinned up loosely with soft wispy bangs, in a plain grey high-collared uniform
  ```
  With it B_stage_alone came back full-length, small before a true cobalt block, and A_desk_ws a real wide shot of the office (`production/assets/mj/sheets/canon_framing_test.jpg`). The dancer plates first asked for the whole figure "two thirds as tall as the frame", and every one came back waist-up; with "the camera far back, her whole figure from head to shoes in the middle of the frame" they ask for head to toe instead. The Instances take the same cut (`INSTANCES_FAR`). The user approved it on 29 Sep.
- **Her hands alone** (`canon="hands"`). A plate of only her hands still pulled her head into frame with her hair in the prompt, and the first A_desk_overhead came back with her face over a keyboard that faced the wrong way (the user's flag, 30 Sep). So a hands-only prompt names only what's in frame, and adds `--no head, face, hair`:
  ```
  the pale, lightly freckled hands of a young white woman, the grey cuffs of her plain grey high-collared uniform
  ```
- **The Human** has no face canon (see "The cast"): they're only ever seen from behind or cropped, so the moodboard can't pull a face it's never asked for. Session 4 made H_desk_typing both ways. Without the moodboard the office came back warmer and busier, and more of his face showed, so the Human keeps it.

## The plates

Session 4 made all 67 (29–30 Sep): `production/assets/frames/<plate>.png`, each pick and its fixes in `production/storyboard/plate_picks.json`, every Midjourney job in `mj_manifest.csv`, the contact sheets in `production/assets/mj/sheets/`. What Midjourney does with these prompts, and what fixes it:
- **Close-ups come back centred** whatever the placement words say. `tools/plates.py fix --place left|right` crops so her face sits 64% of the way across from the type's side, keeping at least 72% of the plate.
- **Wide and full-length framings come back tight.** The distance canon and a hard framing cue fix most. When a plate still comes back cut off, Midjourney's Zoom Out 2x on the best image fixes it without another run (B_dancer_2, B_mirror_ws, A_desk_ws). The Zoom buttons only show after ticking Zoom under the job page's "More options".
- **Cobalt comes back teal or navy.** `fix --recolour` shifts the saturated blues to #1f4fd6 and leaves skin, eyes and the grey uniform alone.
- **Letterbox bars** get painted into some stills, most of all the Human's with the moodboard. Pick a full-frame image where there is one; otherwise `fix --debar`.
- **Stray figures and text** can be painted out locally: `fix --inpaint` for things on a busy or blurred ground, and `fix --flatfill` for things on a flat floor with a straight edge to keep.
- **Depth maps** (`tools/depth.py`, Depth Anything V2 Large) are in `production/assets/depth/`, white near, for the 29 plates the 2.5D shots use. **Her face and body boxes** (`tools/boxes.py`: MediaPipe's landmarks, Grounding DINO's bodies) are in `production/assets/boxes/`, as fractions of the plate, for every plate she's in.
