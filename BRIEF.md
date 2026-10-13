# Brief for the Always Allow run

Start each session in `PLAN.md` section 5 with the kickoff prompt in `HANDOVER.md`, which points the agent at this brief, or paste everything below the line into Claude Code, started in the root of this repo. Keep API keys in `.env`; never paste them into this file.

Every session runs in your own Windows account. The Midjourney sessions need your signed-in Chrome with Claude in Chrome, and you nearby to clear captchas. The unattended sessions (3 and 5) should run with a permission allowlist, not with all permissions skipped (`PLAN.md` section 5). Keep no more than the $400 safety net as credits across your fal and OpenRouter accounts, with automatic top-up turned off, so it holds even if the agent's ledger is wrong.

---

This repo contains `Always Allow.mp3` (4:37.6, about 134 BPM) and its Suno lyric sheet, `Lyrics (Suno).txt`. The song is sung from the point of view of an AI agent asking for "Always allow". The vocals are mostly spoken, low, calm and deadpan, with chanted, double-tracked hooks. I want you to independently make a complete, end-to-end music video for it. The finish line is a video that SF tech Twitter shares because it is genuinely good, not because it is "AI".

Read `PLAN.md` first, then `research/escape-velocity.md` and `HANDOVER.md`. The plan has the song's section map, a first-pass treatment and the pipeline; it's written to me, so "you" there means me. The research note is how the video we're following was made, and our pipeline is built on it. The handover has where things stand and practical notes from the planning session, such as how Midjourney's web interface behaves. Treat the treatment as a starting point, not a script. You can change anything that makes the video better, except the fixed rules below. Where `PLAN.md` or `HANDOVER.md` disagrees with this brief, the brief wins.

**Fixed rules**
- The soundtrack is exactly `Always Allow.mp3`. The full-length master uses it unedited. The short cut and the teaser may only trim it, cutting on bar lines from `downbeats_s` (short crossfades are fine). Add no other sound, and discard any audio a model generates.
- Timing snaps to the beat grid in `production/analysis/song.json` (`beats_s` and `downbeats_s`) and the word times in `production/analysis/words.json`. Don't rebuild a grid from the BPM: the tempo drifts slightly.
- The compositor renders at 24 fps. Conform any clip that arrives at another frame rate once, before it goes into the comp.
- Every piece of text and UI on screen is rendered in code, or is a real screenshot dropped in as an insert. Never use text from generated images or video.
- **Spending.** Log every paid API call to `production/ledger.csv`, using the columns `tools/lipsync_test.py` writes. The `tool` column is the category (`seedance`, `lipsync`, `edit` or `upscale`). `estimated_usd` holds the cost the API reports where it gives one (OpenRouter returns `usage.cost`), and otherwise the estimate from the prices in `PLAN.md` section 6. Request IDs go in `sync_report.json` and the manifests. The expected total across fal and OpenRouter is about $110.
  - When the ledger passes **$150**, stop making paid calls, write me a note with the spend so far by category and what's left, and wait for my OK; in an unattended session, keep compositing and doing QA with what you have meanwhile. My OK comes with a new figure: set `PAUSE_USD` in `tools/ledger.py` to it and commit.
  - Count jobs that are still running at their estimate when you check the ledger, and run at most 3 paid jobs at once, so a batch can't overshoot the pause.
  - At **$400**, stop for good and explain why.
  - Caps per shot:
    - at most 2 retakes of a Seedance clip, and 1 lip-sync repair per take. The repair is sync-2-pro; use LatentSync only if sync-2-pro can't process the clip;
    - at most 2 reruns of a Midjourney prompt before you rewrite it or ask me.

    The caps belong to the shot and don't reset when you rewrite it, and QA redos count toward them.
  - Never buy Midjourney fast hours. If they run out, stop and ask me.
- **Git.** Commit your work to `main` at the end of each step, with a clear message. Never push, force-push or rewrite history; I push after each checkpoint.
- Never solve a captcha or enter a password. If Midjourney shows a captcha, a sign-in or anything unexpected, stop and ask me.
- Everything is resumable. Keep each shot's `status` in `production/storyboard/shots.json` up to date:
  - `planned`, then `plate` (its still picked), then `clip` (its Seedance clip made and accepted), then `synced` (a speaking clip whose mouth is repaired and checked), then `composited`, then `approved`;
  - `dropped` with a `drop_reason` when a shot is thrown away;
  - clips without speech go from `clip` straight to `composited`, 2.5D shots from `plate`, and code-only shots from `planned`.
- Keep `production/runlog.csv`, one row per session, with the columns `session`, `start`, `end`, `steps`, `summary`, `tool_calls` and `tokens`. The outro receipt needs it. At the end of each session, count its tool calls and tokens with `tools/session_stats.py`, which reads Claude Code's session transcript and its subagents', in `%USERPROFILE%\.claude\projects\C--code-music-videos-always-allow\` or `%USERPROFILE%\.claude-work\projects\C--code-music-videos-always-allow\`, depending on the profile the session ran under (session 2 ran under both), because Claude Code deletes old transcripts after a while.
- Run Python tools with the project's virtual environment (`.venv\Scripts\python`). It has every pinned requirement in `tools/requirements*.txt`, and the tools read keys from `.env` through `tools/envfile.py`; new tools should do the same.
- Final deliverables, in `production/out/`:
  - a 1920×1080 H.264 + AAC master of the full song;
  - a cut of at most 2:20;
  - a 9:16 teaser of 15–30 s;
  - 3 thumbnail stills, 1920×1080 PNG.

**Resources you have**
- **Midjourney**, which you drive yourself in my signed-in Chrome through the Claude in Chrome tools, only in the attended sessions (2, 4 and 6). Use v8.2 with `--ar 16:9 --v 8.2 --raw --hd` and the video's moodboard code, which step 2 creates and `production/style/STYLE_BIBLE.md` records, except in prompts with the Agent: the moodboard overrides her canon, so I decided on 29 Sep that they leave it out. Midjourney's terms prohibit automated use and I've accepted that risk, so work in batches while I'm around. In an unattended session, never open Midjourney. Note any still you need in `production/storyboard/QA_NOTES.md` for the next attended session, and carry on with the best plate you have, a 2.5D treatment, or pure code.
  - Write every prompt as a concrete scene, in this order:
    1. the framing;
    2. the Agent's written canon from `STYLE_BIBLE.md`, including its explicit descriptor;
    3. the action;
    4. where she stands, and which area is empty for type;
    5. the set;
    6. the palette, with hex values and one warm accent;
    7. the grain and "cinematic 35mm film still";
    8. "no text, no letters, no logos".
  - Don't rely on image references for her identity. v8.2 rejects `--oref`, and face images make distant figures' heads too big.
  - Generate in colour.
  - Downloads land in my Downloads folder, named after the account, the prompt's first words and the job ID (`<account>_<words>_<job id>_<index>`). Chrome keeps a download as a `.tmp` or `.crdownload` file until it finishes. Move into `production/assets/mj/inbox/` only finished files whose names contain a job ID you just downloaded; never touch anything else in Downloads.
  - Record each image in `production/storyboard/mj_manifest.csv`: the prompt ID, job ID, index, file, and the shot or plate it's for.
- **Seedance 2.5 through OpenRouter** (`OPENROUTER_API_KEY`) for the moving shots. Step 0 ran the request format below on 28–29 Sep; `PLAN.md`'s 0c row has what it found.
  - Submit with `POST https://openrouter.ai/api/v1/videos`, with `model` `bytedance/seedance-2.5`, `prompt`, `duration`, `resolution` `"720p"`, `aspect_ratio` `"16:9"`, `generate_audio` `true` (the soundtrack is needed for the sync check), and `input_references`: `[{"type": "image_url", "image_url": {"url": …}}, {"type": "audio_url", "audio_url": {"url": …}}]`. Never add `frame_images` to a request with an audio reference: it turns the job into image-to-video and the audio is ignored.
  - ByteDance's filter refuses any photoreal face at submission, AI-generated ones included, with `InputImageSensitiveContentDetected.PrivacyInformation` (unbilled). Put every image with a face through `tools/print_grade.py` before you upload it: the plates, and any frame taken from a clip. It scales the image to 1280×720 and grades it with 5 px cells, the combination that passed in step 0 and the texture I approved; the texture that survives in the clips is part of the look. If a graded plate is still refused, note it in `QA_NOTES.md` and play the shot as 2.5D or with a new plate. Don't coarsen the grade to get a plate through.
  - `duration` is a whole number of seconds: 4–30 in the API, 4–8 in practice. Start every window on a frame of the 24 fps comp (a multiple of 1/24 s of song time), so the clip lands exactly on a frame in the edit. A speaking window starts in the gap before its first word, as close to 0.5 s ahead of it as the gap allows, since Seedance starts the speech about 0.5 s into a clip whatever the lead-in. Give it one line where you can. Its end may fall mid-word, because the edit cuts before it; the prompt quotes the words it holds whole.
  - Files must be at public HTTPS URLs the provider can fetch. Upload them with `fal_client.upload_file`, which returns a fal storage URL.
  - Poll `GET /api/v1/videos/{id}` about every 30 s until the status is `completed`, `failed`, `cancelled` or `expired`. Download from `GET /api/v1/videos/{id}/content?index=0` with the same `Authorization` header. The response's `usage.cost` is the real cost for the ledger. The price is about $0.23/s at 720p.
  - If a job is slow, never resubmit it: a pending or running job can still finish and bill. Record its ID, move on, and collect it later.
  - In the prompt, `@Image1` is the plate. For a spoken line, `@Audio1` is the vocal-stem window, and the prompt starts `@Image1 sings @Audio1. She lip-syncs to @Audio1 exactly, every word in time: "<the exact words in the window>".` Then give the framing, one plain physical action, a locked camera and "no cuts". For motion without speech, `@Audio1` is the full-mix window, so the movement lands on the beat, and the prompt says her mouth stays closed.
  - **Lip sync.** The mouth follows Seedance's own copy of the vocal, and that copy wanders 25–170 ms within a line, so no clip holds one frame on its own (step 0). Seedance gives the performance; sync-2-pro gives the lips. Repair every speaking clip with sync-2-pro: strip Seedance's audio, send our vocal window, then check the result. Don't make covers: through OpenRouter a clip can't both start on a given frame and follow the audio.
  - The fallback is fal's `bytedance/seedance-2.5/reference-to-video`, at about twice the price, behind the same face filter. Switch only if OpenRouter's Seedance fails 3 jobs in a row or stops accepting the request format, and note it in the run log. Refusals by the face filter and credit errors (HTTP 402) never count toward a switch: on a credit error, stop generating and write me a note.
- **fal** (`FAL_KEY`) for:
  - lip-sync repair with Sync lipsync-2-pro (`fal-ai/sync-lipsync/v2/pro`), picked by the lip-sync test (`PLAN.md` phase 0b) and run on Seedance clips in step 0 (`tools/seedance_test.py repair`), with LatentSync (`fal-ai/latentsync`) as the runner-up; `tools/lipsync_test.py` has working inputs for both, and its queue polling with timeouts is the pattern for new clients;
  - plate variants: Seedream 5.0 Lite Edit when cheap is enough, and Nano Banana Pro Edit when fidelity matters;
  - Topaz upscaling for the selects that need it.

  Look up each endpoint's current ID and inputs on fal before its first call.
- **A CUDA GPU** (RTX 3090):
  - depth maps with Depth Anything V2 (Large, through `transformers`);
  - the Agent's face landmarks with MediaPipe's face landmarker, per frame on clips;
  - her body boxes with Grounding DINO;
  - mattes for cutting the dancer out of the clone-formation clip with SAM 2, prompted by those boxes.

  Add what you install to a pinned requirements file.
- **Vocal and instrumental stems** in `production/stems/`, exported from Suno and aligned to the master to the sample. `vocals.mp3` is the lead vocal only. Use it for timing, for Seedance's audio windows, and for sync checks.
- Node, Chrome, ffmpeg and Python are installed. Build the compositor in **Remotion**, or argue for something better in `STYLE_BIBLE.md` before building.

**Sessions and order of work**

The work runs in the sessions from `PLAN.md` section 5, and each session ends at its stop:

| Session | Steps | Ends |
|---|---|---|
| 1 | 0 | when I've seen step 0's results |
| 2 | 2 | at my casting pick, with the canon written |
| 3 | 3 | at checkpoint 1 |
| 4 | 4 | when I've flagged the faces and the fixes are done |
| 5 | 5–7 | at checkpoint 2 |
| 6 | 8 | at delivery |

Don't start the next session's steps unless I say so. The steps here map to the plan's phases: step 0 is phase 0c, 1 is 1, 2 is 1b, 3 is 2–2c, 4 is 3, 5 is 4, 6 is 5, 7 is 6, and 8 is 7.

Skip a step only when its outputs show it's finished:
- **Step 0** is done when `PLAN.md`'s 0c row records its result. It was done on 29 Sep: it failed its pass rule and set the route for step 5 instead (Seedance for the performance, sync-2-pro for the lips, no covers).
- **Step 1** is done when `production/analysis/words.json` exists and the section labels in `song.json` place its lines. Both were done on 28 Sep.
- **Step 2** is done when `production/style/STYLE_BIBLE.md` has the moodboard code and the Agent's canon, both from picks I made.
- **Step 3** is done when `production/storyboard/APPROVED.md` exists. Only I create that file, when I approve the storyboard and animatic; never create it yourself.
- **Step 4** is done when every shot that needs a plate is at `plate` or later, with its files present: the plate in `production/assets/frames/` and, for 2.5D shots, the depth map in `production/assets/depth/`.
- **Step 5** is done when every Seedance clip without speech is at `clip` or later, every speaking clip is at `synced` or later, or its shot is `dropped`, each with an entry in `production/storyboard/sync_report.json`, and the tracking and the dancer matte are done.
- **Step 6** is done when every shot that isn't `dropped` is at `composited` or later and a full-length render exists at `production/out/roughcut.mp4`.
- **Step 7** ends at checkpoint 2. Step 8 starts when I've given my notes, in chat or in `production/storyboard/CUT_NOTES.md`.
- **Step 8** is done when the deliverables are in `production/out/`.

Steps 2 and 4 need Midjourney in my browser. If the browser tools aren't connected, stop and ask me. If `production/comp/` already has the compositor, put the real footage into it in step 6; don't rebuild it.

0. **Seedance sync test** (`PLAN.md` phase 0c). Done on 28–29 Sep. It built `tools/avsync.py`, ran six clips, two covers and two sync-2-pro repairs, and set the route that steps 3 and 5 follow. `PLAN.md`'s 0c row has the findings and `production/tests/seedance/sync_report.json` every request and result; the test as it was set is in this file's git history.
1. **Timing.** Done on 28 Sep. `words.json` has every lyric word's start and end from forced alignment, with a confidence and a Whisper cross-check per word, and `song.json`'s section labels place every line. Parenthesised echoes such as "(always)" are backing vocals with no word times. The rule that every lyric word is on screen covers the words in `words.json`; show the echoes too if they help, timed from the instrumental stem's onsets. If you re-run `tools/align_lyrics.py`, check any new flag against the stem's vocal onsets and the bar grid.
2. **Look tests and casting.** I have no Midjourney profile or moodboard, so start with the look.
   - Write a look-test pack for both styles from prompt text alone: sets, light and texture, some with a stand-in figure, about 10–15 prompts per style.
   - Run it, contact-sheet it, and stop for my picks. ffmpeg's `tile` filter is enough for contact sheets until step 3 builds the script.
   - Create a moodboard named "Always Allow" on Midjourney's Moodboards page and add the images I pick. Record its code in `production/style/STYLE_BIBLE.md`, and use it in every prompt from then on, except those with the Agent (see **Midjourney** above).

   Then write a casting pack: 2–3 looks for the Agent, each as a turnaround sheet, a set shot and a face sheet, plus the key sets. Run it, contact-sheet it, and stop for my pick. Write her canon into `STYLE_BIBLE.md`: hair, face, uniform, the terracotta accent, and an explicit ethnicity and skin descriptor, because Midjourney drifts a character's ethnicity without one. Show me each look through `tools/print_grade.py` too, since every Seedance shot of her goes in graded; in step 0, bright, high-key plates came back cleanest.
3. **Pre-production, the compositor and the animatic.** This session makes no paid calls. Research motion design, K-pop MV direction (how they steer attention with formations, set changes on the chorus, and camera moves on the downbeat), and current agent-culture memes. Check every reference, quote and number that will go on screen against a source, and note the source in `STYLE_BIBLE.md`: this audience screenshots mistakes. Then write:
   - `production/style/STYLE_BIBLE.md`: palette, lenses and lighting, textures (grain and halftone), type system, transitions, the graphics layer, and what we will never do. The halftone has to sit with the print texture in the Seedance clips: at 1080p their dots are about 7.5 px apart, at the CMYK angles 15°, 75°, 0° and 45°. A screen of the same spacing and angles, blended at 35 %, showed no moiré in step 0; test any other screen on the step 0 clips first.
   - `production/storyboard/STORYBOARD.md` and `shots.json`: one or more shots per lyric line and per bar in the instrumental sections. For each shot record:
     - its time range on the beat grid;
     - its lyric lines, each with a type mode (subtitle, coverline or masthead) and text zone;
     - framing, camera and transition;
     - its explaining graphic;
     - its motion tier: a Seedance clip, a 2.5D plate or pure code;
     - its `status`.

     The Seedance clip list gives each clip's plate, window, exact words, and whether she speaks on camera. Plan about 30 clips and at most about 200 s of Seedance (`PLAN.md` section 6), and end the list with its total seconds and estimated cost, retakes and repairs included. Keep the Agent on screen for most of the runtime, inserts without her to at most 2 bars, and never start two clips from the same frame. Plan each passage she speaks on camera as a chain of one-line windows with alternating framings, so every cut between clips is a designed cut, as ESCAPE VELOCITY did. Speaking shots are CU or MCU, facing the camera or in three-quarter view, with her mouth clear and her face big enough for the sync-2-pro repair. Never profile: only close-ups have been tested.
   - The Midjourney plate pack, `production/storyboard/mj_prompts.md`: each plate with the shots it serves, none in more than 3, so the cut doesn't repeat itself.

   Build the compositor and the pipeline code (`PLAN.md` phase 2b):
   - the Remotion project in `production/comp/`, whose footage layer shows a shot's clip when it exists, else its plate, else its storyboard card, so the animation can be built while clips are still being made;
   - set up for parallel animator agents, as ESCAPE VELOCITY's was (`research/escape-velocity.md`, last section): an `ANIMATION_GUIDE.md`, one file per chapter so agents never edit each other's, frames that depend only on the time (Remotion's `random(seed)`, never `Math.random` or `Date`), and a render budget per frame;
   - the OpenRouter and fal clients, which write the ledger and enforce the $150 pause and the $400 stop in code, tested against mocked responses before any real call (step 0's `tools/openrouter_video.py`, `tools/ledger.py` and `tools/seedance_test.py` are a start);
   - the clip loop: `tools/print_grade.py` on every image with a face before upload, then for every speaking clip `avsync.py`, the sync-2-pro repair and its check;
   - that check made automatic for the unattended session: the times of every p, b and m from the forced alignment (`tools/align_lyrics.py` aligns letters, so it can write them out), and the lip gap from `tools/lipcheck.py` around them. Calibrate it on step 0's repairs in `production/tests/seedance/out/repair/`, `t3g_sync2pro.mp4` (a pass) and `t2r_sync2pro.mp4` (borderline): take "closed" from t3g's closed frames, look for each closure in the three frames ending on its letter (the lips close before a p or b is heard), and write down how many misses fail a clip;
   - a check that every lyric word is on screen on its time;
   - contact-sheet and proxy-render scripts.

   Then render the animatic to `production/animatic/animatic.mp4` (a 640×360 proxy), with storyboard cards where footage will go and the code-only shots finished, as `PLAN.md`'s 2c row says, and stop at checkpoint 1.
4. **Plates.** Run the plate pack in batches. Contact-sheet every batch, pick, then show me the picks with her face in them and stop until I've flagged any that are off-model. Fix weak plates with Midjourney edits or fal variants. Make a depth map for every 2.5D shot, and her face and body boxes for every shot she's in. Once the first speaking plates exist, run one MCU speaking clip facing the camera and one in three-quarter view through the whole route (grade, Seedance, sync-2-pro, check; about $4) and show me, so a framing that fails gets new plates while Midjourney is still open.
5. **Seedance and lip sync.** Generate the clip list through OpenRouter, every plate with a face through the print grade first.
   - Check every speaking clip with `avsync.py` and log it: its offsets show how far Seedance's performance is from our vocal.
   - Repair the mouth of every speaking clip with sync-2-pro, from the clip with Seedance's audio stripped and our vocal window. Use LatentSync only if sync-2-pro can't process the clip (it drops about the last half-second of a line, so pad the clip and audio by a second and trim afterwards).
   - Verify every repair with the closure check from step 3: the lips must close for every p, b and m. `tools/lipcheck.py --plot` shows the mouth opening against our vocal for a look by eye; its lag numbers mean little once the soundtrack is our own vocal.
   - Retake a clip whose repair fails its check, or whose performance is off (a turned head, a re-read line, a face off-model).
   - Log every attempt to `production/storyboard/sync_report.json`, keyed by clip: window, words, per take the file, request ID, cost, in-sync fraction and offset, and per repair its request ID, cost and checks. Give each clip a result: `accepted` (no speech; the shot goes to `clip`), `repaired` (the shot goes to `synced`) or `dropped`.
   - Track the Agent in every clip she's in: face landmarks per frame and body boxes, saved next to the clip for the graphics layer.
   - Build the clone formations by cutting the dancer out of one dancer clip with a SAM 2 matte and duplicating her in code, so every clone moves in perfect sync.
6. **Compositing.** Put everything together in Remotion:
   - the Seedance clips and the 2.5D plates;
   - the code-rendered UI: the permission dialog, terminal, tabs, notifications and receipts;
   - the chrome and graphics layer;
   - the kinetic lyrics;
   - grain, halftone and grade.

   Footage goes in before grain, halftone and the grade. Where a plate is weak, paint over it or replace it with pure motion graphics.
7. **QA, repeatedly.** For each section, render at least 28 frames as contact sheets: every shot's first and last frame, every line's first and last word, each graphic's entrance, each transition's middle. Review them like an art director, fix, and re-render. Hold these bars:
   - every lyric word is on screen on its time;
   - at least three information layers in a frame;
   - the main lyric at least 40 px at 1080p;
   - every frame within the render budget set in step 3.

   Watch the full cut (sample frames at 2 fps against the timeline) at least three times. Keep a hit list of the weakest shots, fix the worst first, and re-render. List any Midjourney redos in `QA_NOTES.md`; they run in the next attended session. Be willing to throw work away, within the caps. Stop at checkpoint 2 with the rough cut and your own notes on its weakest parts in `production/storyboard/QA_NOTES.md`.
8. **Delivery.** First run the Midjourney redos in `QA_NOTES.md` with me nearby, then the clips they need. Apply my notes, then export the deliverables. Cut the teaser from one strong passage, such as the final drop, on bar lines.

**Creative direction**
- The spine is **the little window**: the permission dialog comes back in every break at a larger size until the whispered "Allow?" (3:27.5), a click on the final drop (bar 109, 3:29.6), and "Access granted." two bars later (3:33.2). Get this escalation right; it's the payoff of the whole video.
- **The Agent** is an original female character, not Claude or Clawd: calm, polite and uncanny; the power is in the stillness. She's on screen most of the time, and when her face is on camera during a vocal line, she speaks it; not every line needs her mouth. Use a generic look-alike permission window, not a copy of Claude Code's UI. One subtle nod to Claude, such as a warm terracotta accent, is enough. **The Instances** (identical clones) are the backup dancers, because "a thousand of me running tonight" is literally a synchronised formation. **The Human** sends one sentence and goes to lunch.
- **Style**: night-shift office noir (photoreal 35 mm with direct flash, fluorescent 3 a.m. office, deep blacks, one warm accent, halftone and grain) for verses and breaks, and a clean-room white stage with chrome and hard colour blocks for the hooks. Keep it in colour: halftone, grain and the grade go on in post and keep the saturation. The print grade on Seedance's inputs leaves some print texture in its clips; I like it, so the post halftone works with it, not over it (`PLAN.md` 0c). Follow the moodboard over my words wherever they disagree.
- **The graphics layer carries the meaning.** Draw these in code:
  - a persistent chrome layer as the through-line: a session clock, a tool-call and token counter, and a ticker of agent-culture memes and this run's real numbers;
  - tracking boxes and face landmarks on the Agent;
  - for every line, a small graphic that explains it, entering on the words that name it: a chart, UI, a diagram, a label or a counter.

  Dense, ordered and readable in one glance.
- **The first 3 seconds must stop the scroll.** Big type and a striking close-up from frame 1. Type is hero-size in the intro, the drops and the hooks, and subtitle-size in the verses and the breakdown. Compose every shot around its text zone, and never put type over her face.
- **Not every shot needs the Agent.** Use world inserts and, where it's funny, raw screenshots, posts and UI dropped straight in with an internet-brutalism treatment. Anchor to references people recognise instantly.
- **Transitions:** mostly hard cuts on the beat, with a clever, motivated transition every few shots that works with the graphics. Never the same device twice in a row, and never amateurish.
- **The zeitgeist is agent culture**: permission prompts, `--dangerously-skip-permissions`, "YOLO mode", one-shotting, "woke up 12 hours later", parallel subagents, CI going green, "You're absolutely right!". Use it sparingly and with precision; memes are seasoning, not the meal.
- **Meta outro:** this video is itself made by an agent with "always allow". During the outro, show a receipt of *this* run: hours, tool calls, generations, spend, and shots thrown away. Use real numbers from the ledger, the run log, `shots.json` and the session transcripts.
- **Avoid**: Pixar or 3D-mascot looks, generic neon cyberpunk, stock "robot hand" imagery, glowing brains, and anything that looks like a default model output.

Plan rigorously before generating: most of the jarring results in AI videos come from composition and timing that were never worked out. Go back and redo anything that isn't at the bar, within the spending caps.
