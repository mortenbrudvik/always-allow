# Research: Midjourney video with a lip-sync pass

Researched on 28 Sep 2026 as a cheaper alternative to Seedance. The lip-sync test (phase 0b) ran on three Midjourney clips on 28 Sep and picked Sync lipsync-2-pro; see [The lip-sync test](#the-lip-sync-test).

**Superseded the same day.** ESCAPE VELOCITY's production record (`research/escape-velocity.md`) showed the Seedance estimate below was about five times too high, so `PLAN.md` went back to Seedance, following that video's recipe. The lip-sync models here are now for repairing Seedance clips whose sync drifts. The Seedance cost section below is kept as it was written, with a correction.

## Summary

- Seedance was about 92 % of the expected fal spend in the earlier plan (about $515 of $560).
- Midjourney's video model can replace it for most shots, on a flat subscription. It's silent and can't lip-sync.
- Lip sync can be added afterwards. A video-to-video lip-sync model takes a Midjourney clip and the vocal slice, and redraws the mouth. For the 8–10 close-ups that need it, that costs roughly $10–35 in total, depending on the model.
- The trade-offs: you run every Midjourney job by hand, because Midjourney has no public API, and lip-sync quality on Midjourney footage is still untested.

## Why the Seedance plan cost so much

Using the Seedance prices from the earlier plan:

| Item | Expected | Share |
|---|---|---|
| Seedance 2.5 at 720p, final takes: 900 s at about $0.47/s | ≈ $425 | 76 % |
| Seedance at 480p, tests and lip-sync retries: 400 s at about $0.22/s | ≈ $90 | 16 % |
| Image edits and upscaling | ≈ $45 | 8 % |

Seedance bills every second it generates. The finished video is 4:38, and 35–40 % of it is built in code, so only about 170–180 s of generated footage ends up in the cut. The expected case generated about 1,300 s to get there, roughly 7 seconds generated for every second used:
- 2–3 takes per clip, because generations drift, glitch or miss the lip sync;
- clips generated longer than the shots cut from them;
- extra retries on 20–30 lip-sync close-ups;
- 480p test runs.

fal is also one of the pricier places to buy Seedance: about $0.47/s at 720p, against about $0.23/s from BytePlus ModelArk (ByteDance's own platform) or Replicate.

**Correction.** ESCAPE VELOCITY, a 5:06 video with a sung chorus, generated 421 s of Seedance in total (47 clips, 30 covers and 7 tests) for about $93 through OpenRouter, about $0.22/s. The 1,300 s assumed here was about three times its volume, and fal's price doubled it again. Two things kept its volume down:
- more than half of its 141 shots were 2.5D plates or pure code;
- covers regenerate only the part of a clip after its sync drifts, not the whole clip.

## Why lip sync drives the retries

- **The timing is tight.** ITU-R BT.1359 puts the point where viewers notice at about 45 ms when the sound comes early and 125 ms when it comes late. At 24–30 fps that's one to four frames.
- **Some mouth shapes can't be faked.** The lips have to close fully on p, b and m, and teeth and the inside of the mouth are where generated faces tend to smear or morph.
- **Close-ups magnify every error.**

With Seedance, lip sync comes from generating the whole clip against the vocal slice, so a miss means regenerating every pixel of the shot to fix the mouth. Doing lip sync as a separate step means a retry redoes only the mouth.

This song helps. The vocal is spoken, low and deadpan, so the mouth barely moves. The hooks are group chants that work as wide shots, and many lines can play over inserts with the voice off-screen.

## What Midjourney video can do

- The V1 video model still appears to be the current one. It animates an image (a Midjourney image or your own) into a 5-second clip that can be extended by 4 s up to four times, to 21 s. Looping and an end frame are supported.
- It's silent: there's no audio input and no lip sync. Midjourney also tends to add random mouth movement, so prompts for lip-sync shots should ask for closed lips.
- It's 480p (SD) by default, and 720p (HD) on the Standard, Pro and Mega plans, at 24 fps. HD runs in fast mode only, at about 26 fast GPU minutes per job of four clips. SD video in Relax mode needs Pro or Mega. Extra fast hours cost $4 each.
- Midjourney has no public API, so every image and video job goes through you (`PLAN.md` section 4, "Notes on tools").

## Adding lip sync to Midjourney video

There are two routes: lip-sync a Midjourney clip (video plus audio), or animate a Midjourney still from the voice. A separate Grok summary on 28 Sep came to the same conclusion. This video uses the first route, with the second as the fallback.

### Video-to-video lip-sync models

All on fal unless noted.

| Model | Price | Notes |
|---|---|---|
| Sync lipsync-2-pro | $5/min | Made for live action, animation and AI-generated footage, up to 4K. Handles audio and video of different lengths (cut off, loop, bounce, silence or remap). |
| Sync lipsync-2 | $3/min | The cheaper tier of the same model. |
| sync-3 | $8/min | Sync's newest model. |
| Sync React-1 | not listed | Lips-only, face or head edit modes and an emotion setting; "neutral" suits the deadpan. Inputs up to 15 s. |
| InfiniteTalk (open source) | $0.20/s | Reanimates the head and face as well as the mouth, for a more natural performance. Speech only (fine for this vocal) and realistic faces only (fine for the Agent). Outputs 480p or 720p. |
| VEED Lipsync v2 | $0.07/s | Re-syncs real footage, AI clips, avatars and animated characters. |
| LatentSync (ByteDance, open source) | $0.20 per clip up to 40 s | The cheapest. Handles real and anime faces. |
| Kling LipSync | $0.014 per input second, billed in 5-s blocks | Input must be 2–10 s long and 720p–1080p, so only Midjourney HD clips qualify. Takes about 12 minutes per job. |
| Tavus Hummingbird-0 | $2.10/min on fal, $1.50/min on Tavus | A research preview. It converts everything to 25 fps, so clips need converting back to 24 fps. |
| Magic Hour (its own API) | about $0.08–0.12/s, plans from $15/month | Fine, but another account. |

### Fallback: animate a Midjourney still from the voice

If a Midjourney clip moves too much for a clean lip-sync pass, an audio-driven avatar model can animate the Midjourney still directly from the vocal:

| Model | Price |
|---|---|
| Kling AI Avatar v2 | $0.056/s (Standard), $0.115/s (Pro) |
| VEED Fabric 1.0 | $0.08/s at 480p, $0.15/s at 720p |
| MiniMax H3 Max Lip Sync | $0.05/s at 480p, $0.08/s at 768p, $0.16/s at 1080p; takes 5–15 s of speech |

If those fail too, Seedance for the close-ups only would cost about $55 on fal, or about $30 on BytePlus or Replicate.

### Not a good fit here

- **HeyGen and D-ID:** subscription tools built for presenter-style talking heads.
- **Wav2Lip:** an older open-source model that renders the mouth at low resolution. LatentSync is the better free option for close-ups.
- **Generating a voice first (ElevenLabs):** the audio is the song, so the vocal stem is the input.

### Cost for this video

About 8–10 close-ups of roughly 4 s each, with a few attempts each, comes to about 160 s of processing. That's about $8 with LatentSync, $13 with Sync lipsync-2-pro or $32 with InfiniteTalk, against about $560 for the Seedance plan. The close-ups are the lines where the treatment calls for a face, such as "Give me a goal" (intro), "Pick your favorite" (verse 1) and "one little word" (breakdown).

### Rules for a clean result

1. **Make lip-sync shots in Midjourney HD (720p).** SD loses mouth detail and is too small for Kling. At about 26 fast minutes per four-clip job, 10 shots at two tries each come to about 9 fast hours.
2. **Prompt for a clean base:** face to camera, shoulders up, low motion, closed lips, and no hands near the face.
3. **Feed the clean vocal stem slice for the line, not the full mix.** Discard the output's audio and place the clip at its position on the beat grid (`production/analysis/words.json` and `song.json`).
4. **Lip-sync the clean Midjourney clip** before grain, halftone and the grade.
5. **Render the comp at 24 fps,** the same as Midjourney video, so lip-sync shots aren't frame-rate converted. One frame is about 42 ms, just under the ~45 ms where viewers notice.
6. **Let the agent run the lip-sync step** through fal during the local run. Only the Midjourney jobs need you.

## What changes without Seedance

- **Performance:** the Agent lip-syncs only in the close-ups above. A deadpan AI voice from a still face suits the concept, and the kinetic type carries the words.
- **Clone formations:** generate one dancer clip and duplicate it in code into a grid or formation. Every clone moves in perfect sync, which is literally "a thousand of me".
- **Motion:** more code-only shots, plus slow Midjourney moving stills, which fit the stillness the brief asks for.
- **Cost:** fal drops from about $560 to about $45 expected, most of it optional image edits (`PLAN.md` section 6). Midjourney needs the Pro plan ($60/month) for SD video in Relax mode, and the HD lip-sync shots use fast hours.
- **Your time:** roughly double, because every video job and every redo goes through you. The outro's "an agent made this overnight" joke gets weaker.

## Not verified yet

- fal.ai, sync.so and docs.midjourney.com are blocked from the cloud environment, so the prices and limits above come from those pages as shown in search results on 28 Sep 2026. Check them again before relying on them.
- The lip-sync test used stand-in clips, not the final character, and the full mix, not the vocal stem.

## The lip-sync test

The test costs about $3–5:
- `production/tests/lipsync/mj_test_prompts.md` lists three Midjourney test clips to make: a still close-up, one with small head movement, and one in the hooks' white-studio light.
- `tools/lipsync_test.py` does the rest:
  - cuts the test window (bars 88–90) from the vocal stem, or from the full mix if there's no stem yet. The window was meant to be "You think I'm here for your job.", but the word alignment later showed it holds "I'm here for your weekends. Your mor–", cut off mid-word; the first test ran on that;
  - runs each clip through LatentSync, Sync lipsync-2-pro and InfiniteTalk on fal;
  - writes a side-by-side per clip and logs the spend to `production/ledger.csv`;
  - adds a scoring table to `production/tests/lipsync/results.md`, a working file that isn't committed.
- Score each model 1–5 on the sync of p, b and m, the teeth and mouth, how well it keeps the face, and jitter. A model passes with 4 or more overall on every clip. If none passes, use the avatar-model fallback above.

Run it on your machine with `FAL_KEY`. `--dry-run` checks the setup without spending anything.

### First run, 28 Sep 2026

The clips are Midjourney HD (1280×720, 24 fps, 5.2 s), and the line came from the full mix because there's no vocal stem yet. What running it against fal showed:
- **LatentSync** waited 2–3 minutes in fal's queue, then ran in about a minute. Its output is 3.84 s for a 4.39 s line, so it drops about the last half-second.
- **Sync lipsync-2-pro** mostly started at once and ran in about 80 s. Its output covers the whole line (4.42 s).
- **InfiniteTalk** never got a worker. One request sat in the queue for about an hour and another for 18 minutes, both at position 0. Since then the script cancels a call that is still queued at `--timeout` (a cancelled call isn't billed) and logs every request ID to `out/requests.txt`, so a slow model can't stall a run or leave jobs nobody can trace.

The side-by-sides looked good, so the test was settled without a full scoring table: **Sync lipsync-2-pro** is the model for the close-ups (`PLAN.md` phase 0b). The run cost $2.58 by the ledger, which includes $0.88 estimated for the first InfiniteTalk request; it couldn't be cancelled because its request ID wasn't recorded.

## Sources

- [How to add voice and sound to a Midjourney video (CometAPI)](https://www.cometapi.com/how-to-add-voice-and-sound-to-a-midjourney-video/)
- [Midjourney May 2026 update (PixVerse)](https://pixverse.ai/en/blog/midjourney-ai-image-generator-review)
- [Midjourney docs: Video](https://docs.midjourney.com/hc/en-us/articles/37460773864589-Video)
- [Introducing our V1 video model (Midjourney)](https://updates.midjourney.com/introducing-our-v1-video-model/)
- [Looping and end frame for video (Midjourney)](https://updates.midjourney.com/looping-and-end-frame-for-video-video-in-the-discord-bot/)
- [Midjourney HD video mode (CometAPI)](https://www.cometapi.com/midjourneys-hd-video-mode-goes-live/)
- [Midjourney pricing in 2026 (eesel AI)](https://www.eesel.ai/blog/midjourney-pricing)
- [Sync lipsync-2-pro on fal](https://fal.ai/models/fal-ai/sync-lipsync/v2/pro)
- [Sync lipsync-2 on fal](https://fal.ai/models/fal-ai/sync-lipsync/v2)
- [sync-3 on fal](https://fal.ai/models/fal-ai/sync-lipsync/v3)
- [Sync React-1 on fal](https://fal.ai/models/fal-ai/sync-lipsync/react-1)
- [Sync Lipsync v2 Pro (RunComfy)](https://www.runcomfy.com/models/sync/sync/lipsync/v2/pro)
- [InfiniteTalk video-to-video on fal](https://fal.ai/models/fal-ai/infinitalk/video-to-video/api)
- [InfiniteTalk paper (arXiv)](https://arxiv.org/pdf/2508.14033)
- [Open-source lip-sync models compared in 2026 (Instavar)](https://instavar.com/research/ai-video/open-source-lip-sync-models)
- [VEED Lipsync v2 on fal](https://fal.ai/veed-lipsync-v2)
- [LatentSync on fal](https://fal.ai/models/fal-ai/latentsync)
- [Kling LipSync on fal](https://fal.ai/models/fal-ai/kling-video/lipsync/audio-to-video)
- [Hummingbird-0 (Tavus)](https://www.tavus.io/blog/hummingbird-0-advancing-zero-shot-lip-synchronization-in-ai-generated-video)
- [Magic Hour lip-sync API](https://magichour.ai/api/lip-sync)
- [Kling AI Avatar v2 on fal](https://fal.ai/models/fal-ai/kling-video/ai-avatar/v2/standard)
- [VEED Fabric 1.0 on fal](https://fal.ai/models/veed/fabric-1.0)
- [MiniMax H3 Max Lip Sync on fal](https://fal.ai/h3-max-lip-sync)
- [Seedance 2.5 image-to-video on fal](https://fal.ai/models/bytedance/seedance-2.5/image-to-video)
- [Seedance 2.5 API pricing guide (CometAPI)](https://www.cometapi.com/seedance-2-5-api-pricing/)
- [Seedance 2.5 review: 23 cents a second (MindStudio)](https://www.mindstudio.ai/blog/seedance-2-5-review-pricing)
