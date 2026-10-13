# How ESCAPE VELOCITY was made

**ESCAPE VELOCITY** is anabology's 5:06 lyric music video: a techwear fashion show in which each "Look N" is a Silicon Valley meme, walked by an AI model, under a split-flap board counting down "18 months to escape the permanent underclass". It's the video `PLAN.md` set out to follow. These notes come from anabology's production record (a write-up, the director's messages in order, the prompts that ran the agents, and every Midjourney, Seedance and Suno prompt) and from the finished video, read on 28 Sep 2026. The figures are theirs. The record itself isn't in this repo; it's in the user's Downloads folder as `drive-download-20260928T174906Z-1-002` (`prompts/` and `midjourney/`). The last section corrects these notes against it, after session 1.

## At a glance

| | |
|---|---|
| Time | About 19 h from the first message to the final master, with about 50 messages from anabology at checkpoints |
| Song | Suno v6, 5:06, deadpan spoken verses and a sung trance chorus, 131.5–133.9 BPM |
| Stills | Midjourney v8.2, `--raw --hd` with anabology's personal profile: 188 prompts, 636 images, 130 used |
| Motion | Seedance 2.5 through OpenRouter at 720p: 47 clips, 30 covers and 7 tests, 421 s generated, about $93 |
| Everything else | Code: a custom JavaScript engine in headless Chromium, 141 shots in 9 chapters |
| GPU work | A home RTX 3090 Ti: stems, beat map, word alignment, depth maps, tracking, LatentSync, colourisation |
| Claude | About 1.4 billion tokens, about $626 at API prices, run on a Max plan. Animation agents were 48 % of it |
| Render | 7,354 frames at 1080p in about 63 minutes on 4 cores |

## The stages

**The song and its timing.** The stems came from htdemucs and the beat map from librosa, fitted because the tempo accelerates; everything afterwards snaps to that map. Word times came from forced alignment: wav2vec2 letter probabilities plus a Viterbi pass over the known lyrics, not from a transcription.

**Casting and identity.** The first Midjourney batch was a casting call: three hair directions, each as a turnaround sheet, a catwalk shot and a face sheet. anabology picked one. Keeping her the same took several tries:
- identity passes with GPT image edits drifted away from the Midjourney look;
- v8.2 rejected `--oref`;
- face sheets as image prompts over-conditioned, giving distant figures close-up-sized heads;
- what worked was a fixed written description of her (hair, clip, headset, every garment) in every prompt, with an explicit ethnicity and skin descriptor, because Midjourney kept changing her ethnicity from shot to shot.

**Midjourney.** Every prompt is a concrete scene. It usually states the framing first, says where she stands, and names an empty area for type. It ends with the same family of style words: a palette with hex values and one warm accent, the grain, the finish ("cinematic 35mm film still") and "no text, no letters, no logos". The prompts ran in batches of four images, were contact-sheeted, and picked by anabology and the agents. An automation client drove Midjourney in anabology's own logged-in browser, and anabology solved the occasional captcha.

**The storyboard.** Three director agents boarded the song independently (fashion film, meme density, narrative), three judges scored them, and a head director merged the best. The result was 141 shots over 9 chapters. Each shot records:
- its time range, snapped to beats;
- its lyric lines, and a type mode for each (subtitle, coverline beside her, masthead, or a mass of micro text in the drop);
- the empty area the type goes in;
- the plate prompt, framing, camera and transition;
- the motion tier (Seedance, 2.5D or code);
- the "one-glance" visual joke.

Rules they worked to:
- she's on screen at least 70 % of the time;
- inserts without her last at most 2 bars;
- the average shot is 1.5–4 s;
- the first 3 s are a hook;
- two clips never start from the same frame.

anabology approved it from a storyboard PDF.

**Seedance with the song inside the prompt.** Each clip gets the Midjourney plate as `@Image1`. A sung clip also gets the exact window of the vocal stem as `@Audio1`, cut in a gap between words, and its prompt quotes the words in that window. The pattern is `@Image1 sings @Audio1. She lip-syncs to @Audio1 exactly, every word in time: "…"`, followed by the framing, a locked camera and "no cuts". Motion clips get the full mix for their window instead, so the movement lands on the beat, plus "her mouth stays closed".

anabology noticed the key fact: Seedance copies the reference audio into its own soundtrack, the mouth follows that soundtrack, and when the soundtrack drifts from the reference, the lip sync drifts with it. So a script compared each clip's soundtrack with the vocal it was given (a spectral match over time against a threshold, plus the local timing offset). Where it drifted, the edit cut on the last eighth note before the drift, and a cover clip starting from that frame took over. About 86 % of sung seconds were verified in sync, with LatentSync as the fallback.

**2.5D.** Stills with a depth map, animated in code: parallax, layered pushes, and beat-cut swaps between stills of the same shot. anabology's notes: never repeat a treatment on neighbouring shots, and replace repetitive 2.5D panels with pure motion design.

**Motion design.** Every frame is a pure function of time. The layers:
- the footage;
- kinetic type on each word's aligned time;
- a graphic that explains each line: a chart, UI, a diagram, a label or a counter;
- computer-vision boxes and face landmarks tracked to her;
- a persistent chrome layer: the countdown, a look counter, and a ticker of memes and numbers.

The graphics even annotate the audio, such as the echo taps on a repeated word. One animator agent per chapter wrote that chapter. An art-director agent then rendered at least 28 frames of it as contact sheets, reviewed them, and sent fixes. The checks were:
- every lyric token on screen;
- at least three information layers per frame;
- the main lyric at least 40 px;
- a per-frame render budget.

**v1 to v2.** anabology found v1 too grey: the xerox and dither filters killed the saturation and "the Midjourney magic". v2 went back to contrasty colour with a colour halftone. Seedance clips made from monochrome start frames had come back grey and were recoloured by exemplar-based colourisation. The lesson: generate in colour and apply the look in post.

## What this changes for us

These are recorded as decisions in `PLAN.md` section 9.
- **Seedance is affordable.** Our earlier estimate for a Seedance-based video was about $560: 1,300 s at fal's $0.47/s. They needed 421 s at about $0.22/s through OpenRouter. The plan now follows their recipe: Midjourney stills, Seedance with the vocal slice for performance and hero motion, and 2.5D plus code for the rest.
- **Word timing uses forced alignment**, as theirs did. `tools/align_lyrics.py` does it.
- **Identity lives in the prompt text.** A fixed written canon and an explicit descriptor in every prompt, the framing first, and a casting batch before anything else.
- **Generate in colour; halftone and grade in post.**
- **The agent drives Midjourney** in your logged-in browser, with you on hand for captchas.
- **Borrow the graphics system:** a chrome layer as the through-line, tracking boxes on the Agent, and an explaining graphic per line. It fits an agent video even better than a fashion show.
- **Borrow the review loop:** rendered contact sheets reviewed by an art-director agent, with measurable checks.

## Templates

A Midjourney plate, in their order:
> [framing] of [the Agent's written canon, with the descriptor], [action], [where she stands; which area is empty for type], [set], [palette with hex values and one warm accent], [grain], cinematic 35mm film still, no text, no letters, no logos `--ar 16:9 --v 8.2 --raw --hd` [profile]

For Always Allow, [profile] is the moodboard code, which prompts with the Agent leave out (`production/style/STYLE_BIBLE.md`).

A sung Seedance clip (with `@Image1` = the plate and `@Audio1` = the vocal window, cut in a word gap):
> @Image1 sings @Audio1. She lip-syncs to @Audio1 exactly, every word in time: "[the words in the window]". [Framing] of the woman from @Image1, [plain physical action]. Locked camera, no cuts, no head turns.

A motion clip (with `@Audio1` = the full mix for the window):
> The scene from @Image1, moving in time with @Audio1. [Framing]. [One plain physical action]. [Camera move]. No cuts. Her mouth stays closed, face expressionless.

## Checked against the record in session 1 (29 Sep)

Session 1 read the record itself while the Seedance sync test (`PLAN.md` phase 0c) ran into problems. What it adds to, or corrects in, the notes above:
- **Their plates went into Seedance print-graded.** `prompts/prompts-seedance.md` gives `@Image1` as "the Midjourney plate for the shot, graded in the video's print look", the monochrome xerox and halftone of their first cut. That is also why "clips made from monochrome start frames had come back grey". ByteDance's real-person filter now refuses photoreal faces, AI-generated ones included; a print grade is what gets through, so ours is in colour (`tools/print_grade.py`). The record never mentions the filter.
- **Their covers were designed cuts.** Every cover prompt reuses the plate as `@Image1`, with the audio window starting at the cut, and the storyboard prompt (`prompts/orchestration.md`) planned every sung passage "as a chain of such windows with alternating framings (CU / MCU / MS / profile / over-shoulder), so any cover cut lands as a designed cut". Through OpenRouter on 28 Sep, pinning a start frame (`frame_images`) dropped the audio, so frame-exact covers weren't possible; our route repairs the lips with sync-2-pro instead, and keeps the alternating framings as storyboard grammar.
- **Their lip sync wasn't frame-exact either.** anabology's own note at +3:49: "it doesnt perfectly replicate the audio for some reason, glitches in the middle a little and unsyncs it". Some takes went to LatentSync (the `-ls1` entries).
- **Identity:** a GPT Image identity pass was tried and dropped on 25 Sep ("Gpt is diverging way too much"); prompt text with an explicit descriptor is what stayed.
- **Their footage layer fell back to the plate** until a shot's Seedance clip arrived, so the chapter animators worked while clips were still being made.
- **Their agent workflows** are in `prompts/orchestration.md` and are worth reusing: the storyboard (three directors with different angles, three judges scoring hook, lead coverage, lyric video, jokes, taste and feasibility, a head director who merges, then a constraint check), and the chapters (one animator per chapter, an art director who renders at least 28 frames as contact sheets and returns at most 14 fixes, then a fix pass, with a lyric-token check and a render budget of 1.5 s a frame).
