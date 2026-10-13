# Always Allow: music video plan

Goal: make a music video for `Always Allow.mp3` the same way [@anabology's video](https://x.com/anabology/status/2103534482930491441) was made. An agent (Claude Code) runs mostly unattended, Midjourney and a moodboard set the look, and the finished cut is ready to post on X.

In this plan, "you" is the person running the project and "the agent" is Claude Code. BRIEF.md is written to the agent.

## 1. How the reference video was made

anabology's video is **ESCAPE VELOCITY**, and their full production record is summarised in `research/escape-velocity.md`. In short: about 19 hours from the first message to the master, with about 50 short notes from anabology at checkpoints (the casting pick, the song, storyboard approval, a v1 review). Midjourney v8.2 made every still, driven in anabology's own browser by an automation client. Seedance 2.5 made the moving and singing shots, each conditioned on its Midjourney still and the exact slice of the vocal, with the sync measured afterwards. A custom JavaScript engine drew everything else on the beat. The stages below are from Donald's prompt, which they started from.

"Donald's prompt" is the roughly 9,500-character brief [@donaldjewkes posted](https://x.com/donaldjewkes/status/2102801469976248500) for a *Claude Pop* remake. It was dictated in about 5 minutes; the agent then worked for about 12 hours with fal (roughly $2,000 in credits), Seedance 2.5, ElevenLabs, a folder of Donald's earlier work and reference skills. anabology's record reproduces it verbatim, and it matches the text you pasted from Grok. The prompt asks the agent to:

1. Keep the **exact audio**. Research references and write one coherent style sheet. No "GPT slop" and nothing Pixar-like. Borrow from K-pop's attention grammar.
2. Generate a **protagonist character sheet**, backup dancers, supporting characters and sets (Donald used fal).
3. Generate **Seedance 2.5 base clips** for each lyric beat. Pass cut-up song audio as a reference to get lip sync, and build verification loops until the timing is right. Not every shot needs singing; inserts are fine.
4. **Draw over the base clips in JavaScript** (rotoscope-style), so the base footage acts as motion reference.
5. Make **lyrics a design element**. Use big type for the hook and the opening seconds, subtitle-size type elsewhere, and compose shots to leave room for the words.
6. Do a **meme and zeitgeist pass** aimed at SF tech Twitter.
7. **QA ruthlessly.** Watch the whole cut many times, screenshot weak frames and redo them.

anabology kept all of it but swapped fal imagery for **Midjourney with their personal profile**, and replaced the paint-over with photoreal colour footage under a dense layer of code graphics. The finished video runs 5:06 (an X Premium upload). Its protagonist is a consistent photoreal woman: a black bob with one clay-orange streak, a white puff-sleeve shirt and a pleated skirt. On top of the footage:
- kinetic type on every word;
- a persistent chrome layer: the countdown, a look counter and a meme ticker;
- face-tracking boxes on her;
- a small graphic that explains almost every line.

What we take from it is listed at the end of `research/escape-velocity.md` and built into the pipeline below.

Other public examples that are useful as engineering references (both read during this investigation; PDoomVideo is cloned at `C:\code\github\PDoomVideo`, and ClaudeAnimationBase isn't cloned on this machine):
- [PDoomVideo](https://github.com/mohammadshamma/PDoomVideo): a fully code-drawn MV (p5.js + p5.brush, headless Chrome renderer, Whisper word alignment, STORYBOARD.md, and an ANIMATION_GUIDE.md that briefs parallel subagents).
- [ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase): a starter kit distilled from that project.

## 2. The song

From `tools/analyze_song.py`, with full data in `production/analysis/song.json`:

- **Duration** 4:37.6 (277.6 s). **Tempo** about 134 BPM: one beat is 0.447 s and one bar is 1.79 s. The tempo drifts slightly (133.97–134.43 BPM), so snap to the fitted grid in `song.json` (`beats_s` and `downbeats_s`) rather than one rebuilt from the BPM. librosa's own tempo estimate, 136 BPM, is a coarse bin, not a measurement.
- **Bars**: bar 0 is the first drop at 0:14.38, and the intro is bars −8 to −1. Every section starts on a bar line; lyric lines don't have to, and several come in as pickups before their section.
- **Voice**: mostly spoken, low and deadpan, recorded close to the mic. The hooks are chanted and double-tracked. Because the vocals are spoken, lip sync matters mainly in close-ups (intro, verses, breakdown). The hooks are group chants and are easier to fake.
- **Structure**: the section boundaries come from the audio. The lyric placements come from `words.json` (forced alignment), checked against the stem and the bar grid on 28 Sep. `song.json` carries the same labels, set in `tools/analyze_song.py`, so change them there if they ever change. Times in quotes below are the words' start times.

| Time | Bar | Section | Evidence | Visual beat (first pass) |
|---|---|---|---|---|
| 0:00–0:14 | −8 | Intro: "Give me a goal." (0:03.6) "Just one." (0:09.2) "I'll figure out the rest." (0:12.3) | pads only, no kick | Cold open with the hook frame: extreme close-up of the agent lit by a monitor, huge type "GIVE ME A GOAL." |
| 0:14–0:36 | 0 | Drop, then "Tabs open." (0:23.5) "Tools loaded." (0:27.1) "Plan drafted." (0:30.6) "Executing." (0:34.1), one every 2 bars | kick and bass slam in at 0:14.4 | Forty tabs explode across the frame on the drop, then one type slam per phrase, on its word. The human leaves for lunch. |
| 0:36–1:01 | 12 | Verse 1: "You gave me one sentence…" (0:36.0) to "Pick your favorite." (1:00.0) | steady groove | Flight booked, CI turns green, deck drafted, coffee steam fading. "Four different ways" becomes a 2×2 split. "Pick your favorite." is deadpan to camera. |
| 1:01–1:19 | 26 | Break 1: "A little window opens…" (1:05.4), "Allow once?" (1:14.2), "Or…" (1:17.1, on bar 35) | drums out | **Motif 1**: the permission dialog, small, in a dark room. The cursor hovers between two buttons. Freeze. |
| 1:19–1:44 | 36 | Hook 1: "Always allow…" (from 1:18.0, half a bar early) to "So take a bow" (1:30.7), then chant 1: "Tool call." (1:32.3) "Result." (1:36.5) "Next step." (1:39.9) | full groove, 1-bar dip mid-hook | Performance: the protagonist plus **clones as backup dancers** ("the instances"). Giant "ALWAYS ALLOW" type. Everyone bows on "take a bow". Then the chant: one word per hard cut, terminal type filling the frame. |
| 1:44–1:48 | 50 | "Done." (1:43.9, on bar 50), then its echoes | 2 bars, bass out | "DONE." fills the frame and stutters with the echoes. |
| 1:48–2:09 | 52 | Verse 2: "There's a thousand of me…" (1:48.1) to "There's always another window" (2:07.9) | groove, thinner from 2:02 | Pull back from one agent to a wall of thousands. Inserts: a Tokyo trading floor, a Lagos coder, a calendar clearing. "I forget your face" dissolves the human's face to pixels. "Another window" spawns a new one. |
| 2:09–2:23 | 64 | Break 2: "A little window opens…" (2:09.9) to "Or…" (2:21.5, on bar 71) | drums mostly out | **Motif 2**: the same dialog, bigger now. |
| 2:23–2:36 | 72 | Hook 2: "Always allow…" (from 2:22.4) to "So take a bow" (2:35.1) | full groove, 7 bars | Bigger formation on a new set. |
| 2:36–2:52 | 79 | Build (no vocals) | bass out, highs rising steadily | Pure motion graphics: a notification storm, badge counters and tab counts climbing exponentially, until the breakdown's first line cuts in at 2:49.1. |
| 2:52–3:13 | 88 | Breakdown monologue: "You think I'm here for your job." (from 2:49.1, over the end of the build) to "is one little word." (3:13.2) | sparse sub hits, cavernous | Slow. A montage of the human's life (weekends, mornings) with small subtitles. A heartbeat line flattens into a progress bar. The agent's calm close-up on "one little word". |
| 3:13–3:15 | 100 | Hard stop under "is one little word." | one bar of near-silence | Black. The dialog, full-screen, waiting. |
| 3:15–3:22 | 101 | Instrumental drop (no vocals) | full power returns | Full power with no words: the unanswered dialog multiplies, and the notification storm comes back. |
| 3:22–3:30 | 105 | Riser, with the whispered "Allow?" at 3:27.5 (bar 107.9) | bass lower, highs up; the low end drains out under "Allow?" | **Motif 3**: everything falls away to one full-screen dialog and the cursor, for "Allow?". |
| 3:30–3:56 | 109 | **Final drop on bar 109 (3:29.6): the click.** "Access granted." (3:33.2), "Spinning up. All of me." (3:38.4), "Go." (3:42.5), then Hook 3: "Always allow…" (3:43.0) to "So take a bow" (3:55.7) | heaviest groove, 2-bar dip in bars 115–116 | The click lands on the downbeat: white flash, thousands of windows open at once, every clone turns to camera, and "ACCESS GRANTED." two bars later. Then the full ensemble; the dialog becomes architecture, a city made of windows. Type echo trails. |
| 3:56–4:09 | 124 | Chant 2: "Tool call." (3:57.3) "Result." (4:01.4) "Next step." (4:04.8), exactly 81 bars after chant 1 | groove | Faster cuts, strobing type, mirroring chant 1. |
| 4:09–4:12 | 131 | "Done." (4:08.8, on bar 131), then its echoes | 2 bars, drums out | Sudden quiet: "Done." and a checkmark. |
| 4:12–4:34 | 133 | Outro climax: "Task complete." (4:14.2), and "Anything else?" (4:18.7) in a short dip | loudest section | **Meta reveal**: a "receipt" for the real run (hours, tool calls, generations, spend) prints while every shot flashes past, stamped "Task complete." The music ducks for "Anything else?": an empty chat box and a blinking cursor. Then the flash-past resumes, to a hard stop on the pressed [Always allow] button. |
| 4:34–4:38 | 145 | Tail | decay | Black. Small type: "Task complete." |

## 3. Creative treatment (starting point; the agent is free to push it)

**Core idea:** the song is sung by an AI agent asking for "Always allow". Everyone on tech Twitter knows the permission prompt behind that phrase. The video's spine is **the little window**. It returns in each break at a larger size (small, then larger, then full-screen) until the whispered "Allow?" and the click that triggers the final drop. The escalation gives the video its structure and makes the "Allow?" moment land.

**Cast**
- **The Agent** (protagonist): an original female character, not Claude or Clawd, with one subtle nod to Claude (a warm terracotta accent). Calm, polite, deadpan, slightly uncanny. Same face and uniform in every shot, from one written description used in every prompt. The vocal delivery ("terrifying ease") should shape the performance: stillness, not bubbly pop energy. She's on screen most of the time (ESCAPE VELOCITY's bar was at least 70 %). When her face is on camera during a vocal line, she speaks it, but not every line needs her mouth; elsewhere her voice plays over the shots and the type carries the words.
- **The Instances** (backup dancers): identical clones of the Agent. The synchronised choreography of K-pop maps directly onto "a thousand of me running tonight". In practice, one dancer clip, generated against the song so the moves land on the beat, is duplicated in code, so every clone moves in perfect sync.
- **The Human**: sends one sentence, goes to lunch, and later "goes and has a life".

**Style** (decided: A for verses and breaks, B for the hooks):
- **A. Night-shift office noir.** Photoreal 35 mm with direct flash, a fluorescent office at 3 a.m., deep blacks, a single warm accent colour, halftone, grain and UI overlays. Closest to anabology's look.
- **B. Clean-room K-pop.** A high-key white studio, chrome, identical uniforms, hard colour blocks. Cute and creepy at once.
- Changing the set on the chorus is standard MV grammar, and the contrast makes each section easy to read. Donald's papery paint-over is not the main look, but it stays available per shot where a plate is weak.
- **Generate in colour; apply the look in post.** Midjourney stills and Seedance clips are made in full colour. Halftone, grain and the grade are added in the compositor, and they keep the saturation. ESCAPE VELOCITY's first cut used desaturating xerox and dither filters, came out "way too gray", and had to be redone. Seedance clips started from monochrome frames also came back grey. One exception since phase 0c: every image with a face goes into Seedance through the colour print grade, because ByteDance's filter refuses photoreal faces. Some of its texture survives in the clips; you like it, so the compositor's halftone works with it.

**Typography:** all text is rendered in code, never generated, because generative models garble text. Every lyric line is on screen on its word times, in one of three modes:
- **subtitle** size in the verses and the breakdown;
- a **coverline** stacked beside the Agent;
- a full-frame **masthead** for single words and the hooks.

The chants can become a mass of micro text on the beat. Big type in the first 15 seconds and in every hook. Compose every shot with a defined text zone, for example the character right-of-centre and the type on the left, and never put type over her face.

**Graphics layer:** on top of the footage, drawn in code:
- **A persistent chrome layer**, the through-line alongside the permission dialog: a session clock, a tool-call and token counter, and a ticker of agent-culture memes and this run's real numbers.
- **Tracking boxes and face landmarks** on the Agent, as if the agent is watching itself.
- **A small graphic that explains each line**, entering on the words that name it: the forty tabs, the green CI checks, the 2×2 of "four different ways", the calendar being cleared.

It's what made ESCAPE VELOCITY feel dense and authored, and it suits an agent video even better than a fashion show.

**Zeitgeist pass** (agent culture, not general AI hype): permission prompts, `--dangerously-skip-permissions` and "YOLO mode", "one-shotted it", "woke up 12 hours later", parallel subagents, "You're absolutely right!", CI going green, a "Task complete" receipt. The meta angle is the strongest hook: **this video was made by an agent somebody gave "Always allow"**, and the outro should show the real run's receipt.

## 4. Production pipeline

| Phase | Who | What | Output |
|---|---|---|---|
| 0. Setup | You | Chrome signed in to Midjourney with Claude in Chrome installed, so the agent can drive it; `FAL_KEY` and `OPENROUTER_API_KEY` in `.env`, with $150 of OpenRouter credits (done 28 Sep); the Python environment `.venv` with every tool's pinned requirements (done 28 Sep). The Suno stems are done (section 9). | `.env` (never committed), `.venv/`, `production/stems/` |
| 0b. Lip-sync test | You and Agent | **Done 28 Sep: Sync lipsync-2-pro picked.** You made three HD Midjourney test clips from `production/tests/lipsync/mj_test_prompts.md`, the agent ran `tools/lipsync_test.py` on one vocal line ($2.58), and you judged the side-by-sides good. LatentSync also worked and is the runner-up, but drops about the last half-second of each line; InfiniteTalk never got a worker on fal. sync-2-pro is now the lip-sync repair for every speaking Seedance clip (phases 0c and 4). Results in `research/midjourney-lip-sync.md`. | this row, the clips in `production/tests/lipsync/clips/` |
| 0c. Seedance sync test | Agent, then You | **Done 29 Sep: Seedance for the performance, sync-2-pro for the lips.** The test as designed (three clips of the 168.9–174.9 s vocal window, then a cover) failed its pass rule, and what it found changes phase 4. You judged the repaired t3g "really good".<br>- **Faces need the print grade.** ByteDance's real-person filter refuses photoreal faces at submission, AI-generated ones included (unbilled). Plates put through the colour print grade (`tools/print_grade.py`) pass, as ESCAPE VELOCITY's print-graded plates did. Seedance's own frames are refused again, so a frame sent back in needs the grade too.<br>- **The mouth follows Seedance's own soundtrack** (lip landmarks, `tools/lipcheck.py`), so `tools/avsync.py` measures the lip sync.<br>- **That soundtrack doesn't hold one frame.** It starts the speech about 0.5 s into a clip whatever the window's lead-in, then wanders 25–170 ms within a line, and now and then re-reads the line. The three clips were 0 % in sync as placed; a revision with single-line windows, the first word 0.55 s in, started two of three on time but reached only 0–21 %.<br>- **Covers don't work through OpenRouter.** With `frame_images` the job becomes image-to-video and the audio is ignored; a reference-mode cover ("@Image2 as the first frame.") keeps the audio but misses the frame.<br>- **sync-2-pro fixes it.** On t3g the lips now close on the /m/ and /b/ frames where Seedance's were open; on t2r one closure is a frame or two late.<br>- **The print texture survives unevenly.** Bright, high-key plates came back almost photoreal; dark ones keep visible dots, which descreening only half removes. You liked the texture, so it stays as part of the look: the compositor's halftone works with it rather than over it. A preview laid the same 5 px CMYK screen over whole clips at a 35 % blend: it makes the clean and the textured clips read as one print, with no moiré at full resolution or between frames (`production/tests/seedance/out/post_screen/`).<br>- Cost $9.70: 6 clips, 2 covers and 2 repairs. Every request, cost and result is in `production/tests/seedance/sync_report.json`; the review page (git-ignored) is `production/tests/seedance/out/review/index.html`.<br><br>For phase 4: grade every face image before Seedance sees it; give each speaking clip one line, with its first word about 0.5 s in; repair every speaking clip with sync-2-pro, then check its p, b and m frames. Covers drop out; BRIEF.md's rules follow. | `tools/avsync.py`, `tools/print_grade.py`, `tools/lipcheck.py`, `tools/seedance_test.py`, `production/tests/seedance/` |
| 1. Timing | Agent | **Word times done 28 Sep.** `tools/align_lyrics.py` force-aligned the lyric sheet to the vocal stem with wav2vec2 on your GPU, in about 20 s, with Whisper as an independent check (it confirms 93 % of words). Every line Whisper disagreed with was checked against the stem's vocal onsets and the bar grid, and the aligner was right each time. **Section labels done 28 Sep:** `song.json`'s labels now place every lyric line (section 2); they're set in `tools/analyze_song.py`, and regenerating with the pinned environment reproduces the beat grid exactly. | `production/analysis/words.json`, `transcript.json`, `song.json` |
| 1b. Look tests and casting | Agent, then You | **The look first.** Your account has no Midjourney profile or moodboard, so the agent runs a look-test batch for both styles from prompt text alone: sets, light and texture, some with a stand-in figure. You pick your favourites; the agent puts them into a moodboard for this video and uses its code in every prompt from then on, except those with the Agent.<br><br>**Then casting:** 2–3 looks for the Agent, each as a turnaround sheet, a set shot and a face sheet. You pick one, and the agent writes her canon into `STYLE_BIBLE.md` (hair, face, uniform, the accent, and an explicit ethnicity and skin descriptor), to be pasted into every prompt with her. | `production/style/{moodboard,casting}/`; the moodboard code and her canon in `STYLE_BIBLE.md` |
| 2. Pre-production | Agent | Treatment, `STYLE_BIBLE.md`, shot-by-shot `STORYBOARD.md` and `shots.json`, and the Midjourney plate pack (`mj_prompts.md`). Each shot records:<br>- its time range on the beat grid;<br>- its lyric lines, each with a type mode and text zone;<br>- framing, camera and transition;<br>- its explaining graphic;<br>- its motion tier: a Seedance clip, a 2.5D plate, or pure code.<br><br>The Seedance clip list gives each clip's plate, its window (4–8 whole seconds, starting on a frame of the 24 fps comp in the gap before its first word, about 0.5 s ahead of it where the gap allows), the exact words in it, and whether she speaks on camera.<br><br>Rules from ESCAPE VELOCITY:<br>- the Agent is on screen for most of the runtime;<br>- inserts without her last at most 2 bars;<br>- two clips never start from the same frame;<br>- neighbouring 2.5D shots never share a treatment. | docs, `shots.json`, `mj_prompts.md` |
| 2b. Compositor and pipeline code | Agent | A **Remotion** (React) project at 24 fps:<br>- the lyric engine: three type modes on the word times;<br>- the chrome and graphics layer;<br>- the UI components: the permission dialog at three sizes, terminal, tabs, notifications, the receipt;<br>- a 2.5D renderer that animates a still over its depth map;<br>- grain, halftone and grade;<br>- a shot timeline driven by `shots.json`, whose footage layer shows a shot's clip when it exists, else its plate, else its storyboard card (as ESCAPE VELOCITY's did, so animation and generation can run side by side).<br><br>Plus the pipeline:<br>- an OpenRouter client for Seedance, and a fal client for lip-sync repair, image edits and upscaling;<br>- both clients write the ledger (with the cost the API reports, where it reports one), pause at $150 and stop at the $400 safety net, and are tested against mocked responses first;<br>- the clip loop: the print grade on every image with a face before upload, then for every speaking clip `avsync.py`, the sync-2-pro repair and its check (phase 0c's `tools/openrouter_video.py`, `tools/ledger.py` and `tools/seedance_test.py` are a start);<br>- that check made automatic: the times of every p, b and m from the forced alignment, and the lip gap from `tools/lipcheck.py` on those frames;<br>- a check that every lyric word is on screen;<br>- contact-sheet and proxy-render scripts. | `production/comp/`, `tools/` |
| 2c. Animatic | Agent | A full-length render on the real audio: storyboard cards where footage will go, finished code-only shots everywhere else | `production/animatic/animatic.mp4`, a 640×360 proxy for review |
| **Checkpoint 1** | You | Approve the animatic and storyboard by committing `production/storyboard/APPROVED.md` (with any notes); the agent never creates it. | `APPROVED.md` |
| 3. Plates | Agent, with you nearby | **Done 30 Sep: all 67 plates, their depth maps and her boxes.** The agent ran the plate pack in Midjourney in your browser in 7 batches, contact-sheeted and picked; you flagged one face (A_desk_overhead), now remade hands only. Midjourney centred the close-ups, cut the wide and full-length framings short, rendered cobalt as teal and painted letterbox bars into some stills. The fixes: a distance canon for wide shots, Zoom Out 2x on three plates, reruns within the cap, and local crops, recolours and paint-outs (`tools/plate_fix.py`, recorded per plate); no fal variants were needed. The 29 plates of 2.5D shots have depth maps (Depth Anything V2 Large), and every plate with her has her face and body boxes (MediaPipe, Grounding DINO). The two test clips ran the whole route for $4.74: C12 (three-quarter MCU) passed at once, and C13 (MCU facing) passed once the closure check looked two frames either side of each letter, your call. Both framings work. `STYLE_BIBLE.md`'s "The plates" and `QA_NOTES.md` have the details. | `production/assets/{mj,frames,depth,boxes}/`, `production/storyboard/plate_picks.json` |
| 4. Seedance and lip sync | Agent | **Done 30 Sep: 31 of 33 clips, $59.58.** 25 speaking clips repaired with sync-2-pro and 6 motion and dancer clips accepted; C05 and C29 dropped after 3 takes each, their shots reworked. Seedance's output filter refused some takes as copyrighted (unbilled), and a clip without speech then asked for no generated audio. Takes avsync couldn't match were repaired anyway and judged by eye. Her tracking is in `production/clips/tracking/`, the three dancer mattes (SAM 2.1) in `production/clips/mattes/`. `QA_NOTES.md` has the decisions.<br><br>Generate every clip in the list through OpenRouter:<br>- `@Image1` is the plate, through the print grade if it has a face;<br>- `@Audio1` is the vocal-stem window for a spoken line, starting about 0.5 s before its first word, or the full-mix window for a motion clip, so the motion lands on the beat;<br>- the prompt quotes the words in the window.<br><br>Check each speaking clip with `avsync.py`, then repair its mouth with sync-2-pro on our vocal (LatentSync as the runner-up; it drops about the last half-second, so pad and trim), and verify the repair with `tools/lipcheck.py` and the p, b and m frames. Seedance alone doesn't hold one frame, and covers don't work through OpenRouter (phase 0c). At most 2 retakes of a clip and 1 repair per take; after that the shot changes or goes.<br><br>Discard every model's audio; the master MP3 is the only soundtrack. Build the clone formations by duplicating one dancer clip. | `production/clips/{seedance,lipsync}/`, `production/storyboard/sync_report.json` |
| 5. Compositing | Agent | **Done 30 Sep:** every shot `composited` in `production/out/roughcut.mp4`, with the tracking driving the face boxes, landmarks and lyric placement, the formations planted from the mattes, and the plates' fit-ups done (`ANIMATION_GUIDE.md`).<br><br>Swap the Seedance clips and plates into the compositor from 2b, in place of the storyboard cards. They go in before grain, halftone and the grade. Paint over a plate where it's weak, or replace it with pure motion graphics. | `production/comp/` |
| 6. QA loops | Agent | **Done 30 Sep:** three watch-throughs at 2 fps and a sheet of at least 28 frames per chapter. Every word is on screen on its time and the main lyric is 52 px or more; every frame but the bare end card has three layers or more (by eye); the heaviest stretch renders at 1.39 s a frame per worker, under the 1.5 s budget. The weakest parts are listed in `QA_NOTES.md` for checkpoint 2.<br><br>An art-director pass per section. Render at least 28 frames as contact sheets: every shot's first and last frame, every line's first and last word, each graphic's entrance, each transition's middle. Review them against the style bible, fix, and re-render.<br><br>Measurable checks:<br>- every lyric word is on screen on its time;<br>- at least three information layers in a frame;<br>- the main lyric at least 40 px at 1080p.<br><br>Then full watch-throughs (frames sampled at 2 fps alongside the timeline) and a hit list of weak shots. Midjourney redos are listed for the next attended session, never run unattended. | `production/qa/`, `production/storyboard/QA_NOTES.md` |
| **Checkpoint 2** | You | Review the rough cut and give notes. | |
| 7. Delivery | Agent | **Done 30 Sep**, after the user's notes on the rough cut (`QA_NOTES.md`, session 6): the master, the full 4:37.6 with the song unedited; a 2:16.1 cut of four passages joined on bar lines, 374 MB, under X's 512 MB; a 25 s 9:16 teaser of the final drop, bars 107–121; and three 1920×1080 PNG thumbnails. `tools/deliver.py` makes the master and the cut from the final render, and `render.mjs teaser` the teaser from the master.<br><br>1920×1080 H.264 plus AAC master (full 4:38), a cut of at most 2:20 for non-Premium X, a 9:16 teaser (both trim the song on bar lines), and thumbnails | `production/out/` |

**Notes on tools**
- **Midjourney runs in your browser, driven by the agent** through Claude in Chrome. That's how ESCAPE VELOCITY did it, and how the lip-sync test clips were made. Midjourney has no public API (the official one is gated behind an Enterprise application), and its terms prohibit automated use, so this risks your account; you decided on 28 Sep to accept that.
  - The agent never solves a captcha, so Midjourney runs happen while you're nearby, not overnight.
  - Downloads land in your Downloads folder, and the agent moves them into `production/assets/mj/inbox/`.
  - Use v8.2 with `--raw --hd` and the video's moodboard code from phase 1b, except in shots with the Agent: the moodboard overrides her canon, so you decided on 29 Sep that they leave it out.
  - Keep the character consistent with her written canon in every prompt. v8.2 rejects `--oref`, and image prompts of her face over-condition (a distant figure gets a close-up-sized head); `research/escape-velocity.md` has the details.
- **Seedance 2.5 through OpenRouter** (about $0.233/s at 720p, 4–8 whole seconds per clip) makes the moving shots. Each clip is conditioned on its Midjourney plate and a window of the song. Seedance copies that audio into its own soundtrack and the mouth follows it, so comparing the returned soundtrack with the vocal shows where the lip sync holds (phase 0c confirmed it from lip landmarks). That soundtrack is used only for the check, then discarded. Photoreal faces are refused, so plates with a face go in through the print grade. fal also sells Seedance, at about twice the price, behind the same filter.
- **Lip-sync repair** uses Sync lipsync-2-pro on fal (LatentSync as the runner-up) on every speaking clip, because Seedance's own lip sync wanders by up to about 170 ms within a line (phase 0c). `research/midjourney-lip-sync.md` has the models, prices and rules.
- **2.5D plates** are Midjourney stills animated in code over a depth map made on your GPU: parallax, layered pushes, and beat-cut swaps between stills of the same shot. They're free, on the beat, and good for inserts and sets; vary the treatment from shot to shot.
- **Midjourney video** stays optional for ambient motion without the Agent's face; SD video in Relax mode comes with the Pro plan. Render the comp at 24 fps, like the clips, so nothing is frame-rate converted.
- **No ElevenLabs.** The song already has keyboard clicks and notification sounds built in, and the soundtrack stays exactly the MP3, so there's nothing for generated sound to add. The short cut and the teaser only trim the song, on bar lines.
- **Resumability:** every step writes files and a manifest (`shots.json` statuses plus a spend ledger), so a crashed or paused run picks up where it stopped.

## 5. Running it on your machine

Everything runs locally, with no Claude Code cloud session (decided 28 Sep).

**Your machine** (checked 28 Sep):
- Windows 11 Home;
- an Intel i7-11700K (8 cores, 16 threads) and 32 GB of RAM;
- an NVIDIA RTX 3090 with 24 GB, which runs the word alignment and the depth maps;
- about 65 GB free on C:; the plates, clips and renders need 20–50 GB;
- Node 24, Python 3.12, ffmpeg 8 and Chrome installed.

**Sessions.** The work runs as a few Claude Code sessions in this repo. Each starts from `BRIEF.md` and skips whatever is already done.

| Session | You | Phases |
|---|---|---|
| 1. Setup and test | there | Setup (0) and the Seedance sync test (0c) |
| 2. Look tests and casting | nearby, then your picks | Look tests and casting (1b) |
| 3. Build | at the start, to set up the allowlist below; then not needed until the checkpoint | Pre-production, the compositor and pipeline code, and the animatic (2–2c). Stops at checkpoint 1 |
| 4. Plates | nearby | Plates (3) |
| 5. Overnight | not needed until the checkpoint | Seedance and lip sync, compositing and QA (4–6). Stops at checkpoint 2 |
| 6. Delivery | your notes, and nearby for any Midjourney redos | Delivery (7) |

- **Your time:** about 4–7 h in total:
  - setup, about 0.5 h;
  - picking look-test favourites and the casting look, about 0.5 h;
  - reviewing the storyboard and the animatic, 1–2 h;
  - staying nearby during the Midjourney runs to clear captchas (a few hours of wall-clock, little of it active);
  - flagging off-model faces, about 0.5 h;
  - the rough-cut review, about 1 h;
  - the upload.
- **Agent time:** about 16–24 h over two or three days: 8–12 h for the build session, a few hours of Midjourney runs, 8–12 h overnight, and a 2–4 h fix pass.
- **Render speed:** a representative Remotion test (a 720p plate scaled to 1080p and graded, halftone, grain, beat-timed type, a UI dialog and the audio) ran at about 4 frames per second on a 4-core cloud machine, so a full 4:38 render took 35–60 minutes there. Your 8 cores should be faster; measure it on the first animatic. Measured on 29 Sep with storyboard cards: the 640×360 animatic in about 2 minutes (8 workers), and about 0.4 s a frame a worker at 1080p, so a 1080p render of cards takes about 6 minutes; real footage will be slower (the render budget is 1.5 s a frame).
- **Security:** every session runs in your own Windows account. A separate account wouldn't work here: the sessions pass plates, clips and renders to each other through git-ignored folders in the repo, and Python is installed per user.
  - For the unattended sessions (3 and 5), don't skip permissions. Instead, give Claude Code an allowlist in the repo's `.claude/settings.local.json` that covers what those sessions do:
    - editing files inside the repo, and creating, moving and deleting scratch files there;
    - running the project's tools (`.venv\Scripts\python tools\…`), and `.venv\Scripts\python -m …` and `-c …` (for `pip install` into `.venv`, `http.server` and one-off checks);
    - `npm`, `npx` and `node` for setting up and rendering Remotion;
    - `ffmpeg` and `ffprobe`;
    - `git add` and `git commit`, but not `push`;
    - web search and fetch, for research and API docs.

    Session 3 starts with research and an `npm install`, so without these it would stall on its first actions.
  - Your user settings in the default profile (`%USERPROFILE%\.claude\settings.json`) run in auto mode and allow every `git` command in every project, push included, and a project allowlist only adds to them. So either run the unattended sessions under the `.claude-work` profile, whose user settings grant nothing, or give the project settings `"defaultMode": "default"` and a deny for `git push`, which do override them. Decide at the start of session 3.
  - Anything outside the allowlist then waits for you in the morning instead of running. Set it up with the agent at the start of session 3.
  - Money is capped separately: a pause at $150 and a stop at $400, enforced in code, and no more than $400 of credits across fal and OpenRouter, with automatic top-up off.
- **Git is the history and the backup.** Code, docs, manifests, the stems, the ledger and the run log are committed and pushed to GitHub. Other generated media stays on your machine (section 7).

Why this order works:
- **A third of the video is done early:** about 35–40 % of shots are pure code (type, UI, the notification storm), so they are essentially finished in the animatic.
- **Timing is approved before most of the money is spent:** you sign off on the animatic before the Seedance clips are generated. Only the sync test, $9.70 in the end, comes first.
- **The overnight hours go to Seedance, compositing and taste,** because the overnight session starts from tested scaffolding.

## 6. Cost estimate

**Volume:** about 100–130 cuts over 4:38, averaging about 2.5 s each and faster in the hooks. About 35–40 % are pure code (type, UI, the notification storm) and cost nothing to generate. Most of the rest are 2.5D plates, which are also free. About 25–35 Seedance clips of 4–8 s carry the Agent's speaking shots and the hero motion, roughly 150–200 s as planned. Retakes bring that to about 300 s generated, and every speaking clip also gets a sync-2-pro repair. ESCAPE VELOCITY generated 421 s for 47 clips, but its chorus was sung, and our vocal is mostly spoken with fewer on-camera lines. Time estimates are in section 5.

**Prices used** (published prices as of 28 Sep 2026, found through search results; check them again before the run):
- Seedance 2.5 through OpenRouter: about $0.233 per second at 720p (OpenRouter's model page, 28 Sep; phase 0c was billed $1.396 for 6 s and $0.934 for 4 s). ESCAPE VELOCITY paid about $93 for 421 s. On fal it's about $0.47/s.
- Lip sync on fal: LatentSync $0.20 per clip up to 40 s, Sync lipsync-2-pro $5 per minute.
- fal image edits cost $0.035–0.15 per image (Seedream 5.0 Lite Edit up to Nano Banana Pro Edit).
- Upscaling 720p to 1080p costs about $0.02 per second with Topaz on fal. It comes after the lip-sync repair; check on the first select that it keeps the print texture as it is rather than sharpening it into harder dots.

| | Lean | Expected | Heavy |
|---|---|---|---|
| Lip-sync test (phase 0b, done) | $2.58 | $2.58 | $2.58 |
| Seedance sync test (phase 0c, done) | $9.70 | $9.70 | $9.70 |
| Seedance clips and retakes | 150 s ≈ $35 | 300 s ≈ $70 | 600 s ≈ $140 |
| Lip-sync repairs with sync-2-pro, on every speaking clip | 75 s ≈ $6 | 150 s ≈ $12 | 300 s ≈ $25 |
| fal image edits (optional plate variants) | ≈ $0 | ≈ $10 | ≈ $40 |
| Upscaling selects to 1080p | ≈ $5 | ≈ $5 | ≈ $10 |
| Alignment, depth maps, rendering | $0 | $0 | $0 |
| **Total (fal and OpenRouter)** | **≈ $60** | **≈ $110** | **≈ $225** |

What each column assumes:
- **Lean:** few speaking shots on camera (about 15), and most clips right on the first take.
- **Expected:** about 30 clips, about 22 of them speaking, with a retake for about a third of them.
- **Heavy:** many retakes, extra clips to replace repetitive 2.5D shots, and heavy use of image edits.

The earlier estimate for a Seedance-based version of this plan, about $560, assumed 1,300 s at fal's price; `research/escape-velocity.md` explains why that was far too high.

**On top of that:**
- **Midjourney:** the Pro plan ($60/month). Its 30 fast hours a month cover the casting batch and the plates (150–300 images with `--hd`, roughly 4–8 hours). Extra fast hours cost $4 each.
- **Claude:** the whole run is heavy usage. ESCAPE VELOCITY used about 1.4 billion tokens, about $626 at API prices, on a Max plan; half of that was the animation agents. A Max plan ($100/month, or $200/month for more headroom) is the practical choice.
- **ElevenLabs:** $0, because none is planned.

**No hard cap (your decision), but there is a safety net.** The agent logs every paid call to a ledger, with the cost the API reports where it reports one.
- At $150, well past the expected $110, it pauses and asks you before spending more.
- At $400, nearly twice the heavy scenario, it stops and writes a note: at that point something is probably looping, not being creative.
- Before session 5, check that both balances cover the clip list. fal had about $48 left after session 1, and the heavy case needs about $75 there (repairs, image edits and upscaling); OpenRouter had about $141.
- Retries are capped per shot: at most 2 retakes of a Seedance clip and 1 lip-sync repair per take, and 2 reruns per Midjourney prompt. The ledger is the agent's own bookkeeping, so to make the safety net hold even if the ledger is wrong, keep no more than $400 of credits across your fal and OpenRouter accounts during the run, with automatic top-up turned off.

## 7. Repo layout

```
Always Allow.mp3, Lyrics (Suno).txt
PLAN.md                  this file
BRIEF.md                 the prompt each session starts from
HANDOVER.md              kickoff prompts, where things stand, practical notes
.env                     API keys                                        (git-ignored)
.venv/                   Python for every tool, from tools/requirements*.txt (git-ignored)
research/                escape-velocity.md: how the reference video was made
                         midjourney-lip-sync.md: lip-sync models and the first test
tools/analyze_song.py    beat grid, section map, energy
tools/lipsync_test.py    the lip-sync test (phase 0b)
tools/align_lyrics.py    word timing by forced alignment, checked by Whisper (phase 1)
tools/avsync.py          does a Seedance clip still speak our vocal? (phase 0c)
tools/lipcheck.py        which audio does a clip's mouth follow? From lip landmarks (phase 0c)
tools/print_grade.py     the colour print grade for every face image Seedance sees (phase 0c)
tools/seedance_test.py   the Seedance sync test: prepare, submit, repair, review (phase 0c)
tools/openrouter_video.py, tools/ledger.py   the OpenRouter video client; the ledger and its $150 and $400 limits
tools/session_stats.py   a session's tool calls and tokens, from its transcripts, for runlog.csv
tools/envfile.py         loads .env for the tools
tools/requirements*.txt  pinned versions for the tools
production/
  ledger.csv, runlog.csv spend per call; one row per session
  analysis/              song.json, words.json, transcript.json
  stems/                 Suno vocal and instrumental stems (MP3)
  tests/lipsync/         mj_test_prompts.md, clips/ and out/ (both git-ignored)
  tests/seedance/        the Seedance sync test (phase 0c); out/ is git-ignored
  style/                 STYLE_BIBLE.md; moodboard/ and casting/         (git-ignored)
  storyboard/            STORYBOARD.md, shots.json, sync_report.json, mj_prompts.md,
                         mj_manifest.csv, APPROVED.md, QA_NOTES.md, CUT_NOTES.md
  animatic/              animatic.mp4 (small proxy for review)            (git-ignored)
  assets/                mj/inbox, chars, sets, frames, depth             (git-ignored)
  clips/                 seedance, lipsync, selects                      (git-ignored)
  comp/                  Remotion project
  qa/, out/                                                              (git-ignored)
```

Generated media stays out of git (`.gitignore`), apart from the Suno stems and the lip-sync test clips, because every committed version stays in the history. The ledger, run log and manifests are small and committed. Use Git LFS or cloud storage if you want the rest backed up.

## 8. Risks and mitigations

- **Character drift between shots.** ESCAPE VELOCITY's recurring failure was Midjourney changing the lead's ethnicity. Mitigations:
  - a casting pick before any plates;
  - her written canon, with an explicit descriptor, in every prompt, framing first;
  - you flag off-model faces early;
  - Seedance clips start from approved plates, never two from the same frame;
  - the graphics layer hides small drift.
- **Looking like slop.** Mitigations: one style bible, a limited palette, generation in colour with the look added in post, the chrome and explaining-graphics layer, a recurring motif, set changes that follow the song's sections, and a QA loop that is allowed to throw work away.
- **Seedance's lip sync doesn't hold one frame.** In ESCAPE VELOCITY about 86 % of sung seconds ended up verified in sync; in our phase 0c test no clip held one frame on its own. Mitigations:
  - windows that start about 0.5 s before their first word, one line each where possible, quoting the exact words;
  - `avsync.py` measuring every speaking clip, and a retake when Seedance's copy of the vocal doesn't match our words;
  - a sync-2-pro repair on every speaking clip, verified with `tools/lipcheck.py` and on the p, b and m frames.

  The spoken, deadpan vocal needs little mouth movement, which helps.
- **Seedance refuses photoreal faces.** ByteDance's real-person filter rejects them at submission, AI-generated ones included. Mitigation: every image with a face goes in through the colour print grade, which the filter lets through, as ESCAPE VELOCITY's print-graded plates did. If ByteDance tightens the filter, the fallback is Midjourney video with sync-2-pro, which phase 0b showed works.
- **A model has no free workers.** InfiniteTalk never got one on fal in the lip-sync test. Mitigations: a timeout on every call with queued requests cancelled (as `tools/lipsync_test.py` does), and fal's Seedance as a second source at about twice the price.
- **Your Midjourney account.** Midjourney's terms prohibit automated use, and the agent drives it in your browser. You decided to accept that risk on 28 Sep. If Midjourney objects, the fallback is the old split: the agent writes the packs and you run them.
- **Your time.** Mostly reviews now. The Midjourney runs need you nearby for captchas, so batch them into a few sittings.
- **Garbled text in generated frames.** Every piece of text and UI is rendered in code.
- **Branding.** Decided: an original protagonist and a generic look-alike permission window, not a copy of Claude Code's UI or the Clawd mascot.

## 9. Decisions and open questions

Decided on 28 Sep:
- **Midjourney:** the agent writes the packs and runs them in your browser through Claude in Chrome, while you're nearby for captchas. You decided this on 28 Sep, accepting that Midjourney's terms prohibit automated use (section 8). Before that, you were going to run the packs yourself.
- **Style:** night-shift office noir for verses and breaks, a clean-room stage for the hooks.
- **Protagonist:** an original female character with a subtle Claude nod.
- **Where:** everything runs on your machine, in your own account, in the sessions in section 5, with an allowlist for the unattended ones. Decided 28 Sep. The earlier plan split the work with a Claude Code cloud session, which couldn't reach Hugging Face, fal, your GPU or your browser. A separate Windows account for the unattended sessions was dropped because it couldn't see the git-ignored media or the per-user Python.
- **Lyric alignment:** done 28 Sep. It uses forced alignment (wav2vec2) on your GPU, as ESCAPE VELOCITY did. Whisper's own timestamps started lines after a pause about 0.7 s early, so Whisper is only the cross-check. `song.json`'s section labels were corrected to match on the same day.
- **The climax:** the whispered "Allow?" is at 3:27.5, the click lands on the final drop at bar 109 (3:29.6), and "Access granted." comes two bars later (3:33.2). The old section map had put "Allow?" at 3:14.
- **Stems:** done 28 Sep. Exported from Suno with Get Stems → Split from mix, from the 4:38 version that matches `Always Allow.mp3` (song ID `ce885e61`). `production/stems/vocals.mp3` is the lead vocal only; the hook's doubled and backing vocals are in `instrumental.mp3` with everything else. Suno's MP3s were 1,105 samples (23 ms) late against the master because of an MP3 encoder delay their headers didn't declare, so they were trimmed and re-encoded; both now line up with the master to the sample.
- **Deliverables:** the full 4:38 at 16:9 for X Premium, a cut of at most 2:20, and a 9:16 teaser.
- **Budget:** no hard cap. Section 6 has the estimate. The safety net stays at about twice the heavy scenario: $1,000 at first, $250 when the plan dropped Seedance, and $400 now that Seedance is back (heavy is about $225). A pause at $150 and per-shot retry caps were added on 28 Sep, so an overnight run can't drift toward the stop unnoticed.
- **Deliverable specs:** the teaser is 15–30 s, cut on bar lines from one strong passage; the thumbnails are 1920×1080 PNG.
- **Video:** ESCAPE VELOCITY's recipe, decided 28 Sep after its production record showed Seedance costs about a fifth of our estimate:
  - Midjourney stills;
  - Seedance 2.5 through OpenRouter, conditioned on the plate and a window of the song, for the Agent's speaking shots and the hero motion;
  - 2.5D plates and pure code for the rest.

  This replaces the earlier choice of Midjourney video with a separate lip-sync pass.
- **Lip-sync model:** Sync lipsync-2-pro, from the lip-sync test on 28 Sep (phase 0b), now the repair for every speaking Seedance clip, with LatentSync as the runner-up.
- **Style code:** your Midjourney account had no personalization profile or moodboard (checked 28 Sep), so the look comes from a moodboard for this video, built from look tests you pick at the start of phase 1b.

Decided on 29 Sep, from the Seedance sync test (phase 0c):
- **Seedance for the performance, sync-2-pro for the lips.** Every image with a face goes into Seedance through the colour print grade; every speaking clip gets a sync-2-pro repair; there are no covers.
- **The print texture stays as part of the look.** You liked it; the compositor's halftone works with it.
- **Retry caps:** at most 2 retakes of a Seedance clip and 1 lip-sync repair per take, in place of 2 covers and 1 repair.

Nothing is open.
