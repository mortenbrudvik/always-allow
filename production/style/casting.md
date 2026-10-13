# Casting (BRIEF.md step 2, PLAN.md phase 1b)

Looks for the Agent. The user picks one; its description becomes her canon in `STYLE_BIBLE.md`, pasted into every prompt with her.

- **Casting direction (the user, 29 Sep):** she is white, with black hair, and flawless: "AI girls should be the essence of perfection". Never pale, anemic or soulless.
- **The reference (the user, 29 Sep, 15:35):** "Something like this", pointing at the lip-sync test's t3 portrait, Midjourney job `ac724c80` image 3 (the first frame of `production/tests/lipsync/clips/t3.mp4`). She is a calm young white woman with a healthy, softly rounded face, rosy cheeks and light freckles, very dark brown hair pinned up with soft wispy bangs, grey-blue eyes, and full lips with natural colour. She wears a grey high-collared uniform with a chrome bar pin at the collar, in soft, even high-key light, in front of a pale blue block on white. Then: "Please do not do the skinny, anemic girls." The nationality portraits (N1–N8, `casting/sheet_N.png`) came back gaunt, hollow-cheeked, pale and hard-lit, which is exactly what to avoid: keep her face full and her colour healthy, and light her softly.
- **How the reference was made:** a short prompt, `high-key white studio, close-up of a calm young woman in a plain grey uniform with a chrome collar pin, facing the camera, lips closed, clean even light, a hard block of colour behind her --ar 16:9`, on v8.2 with standard settings: no `--raw`, no `--hd`, no moodboard, and no beauty wording. The R batch below starts from it.
- **The recipe is the lip-sync test portraits** (`production/tests/lipsync/mj_test_prompts.md`, t1 and t3), which the user preferred: short, photographic prompts, one portrait each. The first casting pack, with long spec-sheet descriptions and turnaround and face sheets, came back like mannequins and was dropped.
- **Two framings per look:** the verses' flash-lit office close-up, facing the lens (her speaking framing), and the hooks' white studio close-up.
- **A settings check:** each office portrait also runs as `-B`, without `--raw` and the moodboard, to see whether they are what takes the life out of her. Every plate after casting uses the brief's parameters, so if `-B` wins, that's a question for the user.
- **Parameters:** `--ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213`; the `-B` prompts use `--ar 16:9 --v 8.2 --hd`.
- **She is original:** not Claude, not Clawd, and not ESCAPE VELOCITY's lead (a black bob with a clay-orange streak), so no look uses a bob or a coloured streak.
- **The picked look** was to get turnaround and face sheets, made from its portrait's wording. They weren't made for R3.3: the earlier sheets came back like mannequins, and plates don't use image references for her (`BRIEF.md`), so session 4 checks the canon in a medium and a wide shot instead. Every look is shown through `tools/print_grade.py`.

## The looks

**L1.** A flawless young white woman, impossibly perfect and slightly unreal, long straight black hair with a centre parting, dark brown eyes, healthy glowing skin, wearing an off-white high-collared shirt with a small terracotta pin at the collar.

**L2.** A flawless young white woman, impossibly perfect and slightly unreal, glossy black hair in a sleek high ponytail, green eyes, healthy glowing skin, wearing a pale grey technician jacket zipped to the throat, terracotta piping on the collar.

**L3.** A flawless young white woman, impossibly perfect and slightly unreal, black hair slicked straight back, pale grey eyes, small terracotta stud earrings, healthy glowing skin, wearing a white high-neck top.

## L1

**L1-O. Office close-up (verses)**
```
35mm photo, close-up portrait of a flawless young white woman, impossibly perfect and slightly unreal, long straight black hair with a centre parting, dark brown eyes, healthy glowing skin, wearing an off-white high-collared shirt with a small terracotta pin at the collar, looking straight into the lens with a calm, knowing gaze, lips closed, placed right of centre with dark empty space on the left for type, a fluorescent office at 3 a.m. lit by direct on-camera flash, deep blacks #0b0c0e, fluorescent green-white #d8e4dc, one warm terracotta accent #c96442, film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**L1-W. White studio close-up (hooks)**
```
35mm photo, close-up portrait of a flawless young white woman, impossibly perfect and slightly unreal, long straight black hair with a centre parting, dark brown eyes, healthy glowing skin, wearing an off-white high-collared shirt with a small terracotta pin at the collar, facing the camera, still and serene, lips closed, placed centre with white space on both sides for type, a high-key white studio with a hard cobalt block behind her, clean even light, white #f4f4f1, cobalt #1f4fd6, one warm terracotta accent #c96442, film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**L1-OB. Office close-up, without --raw and the moodboard**
```
35mm photo, close-up portrait of a flawless young white woman, impossibly perfect and slightly unreal, long straight black hair with a centre parting, dark brown eyes, healthy glowing skin, wearing an off-white high-collared shirt with a small terracotta pin at the collar, looking straight into the lens with a calm, knowing gaze, lips closed, placed right of centre with dark empty space on the left for type, a fluorescent office at 3 a.m. lit by direct on-camera flash, deep blacks #0b0c0e, fluorescent green-white #d8e4dc, one warm terracotta accent #c96442, film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --hd
```

## L2

**L2-O. Office close-up (verses)**
```
35mm photo, close-up portrait of a flawless young white woman, impossibly perfect and slightly unreal, glossy black hair in a sleek high ponytail, green eyes, healthy glowing skin, wearing a pale grey technician jacket zipped to the throat, terracotta piping on the collar, looking straight into the lens with a calm, knowing gaze, lips closed, placed right of centre with dark empty space on the left for type, a fluorescent office at 3 a.m. lit by direct on-camera flash, deep blacks #0b0c0e, fluorescent green-white #d8e4dc, one warm terracotta accent #c96442, film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**L2-W. White studio close-up (hooks)**
```
35mm photo, close-up portrait of a flawless young white woman, impossibly perfect and slightly unreal, glossy black hair in a sleek high ponytail, green eyes, healthy glowing skin, wearing a pale grey technician jacket zipped to the throat, terracotta piping on the collar, facing the camera, still and serene, lips closed, placed centre with white space on both sides for type, a high-key white studio with a hard cobalt block behind her, clean even light, white #f4f4f1, cobalt #1f4fd6, one warm terracotta accent #c96442, film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**L2-OB. Office close-up, without --raw and the moodboard**
```
35mm photo, close-up portrait of a flawless young white woman, impossibly perfect and slightly unreal, glossy black hair in a sleek high ponytail, green eyes, healthy glowing skin, wearing a pale grey technician jacket zipped to the throat, terracotta piping on the collar, looking straight into the lens with a calm, knowing gaze, lips closed, placed right of centre with dark empty space on the left for type, a fluorescent office at 3 a.m. lit by direct on-camera flash, deep blacks #0b0c0e, fluorescent green-white #d8e4dc, one warm terracotta accent #c96442, film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --hd
```

## L3

**L3-O. Office close-up (verses)**
```
35mm photo, close-up portrait of a flawless young white woman, impossibly perfect and slightly unreal, black hair slicked straight back, pale grey eyes, small terracotta stud earrings, healthy glowing skin, wearing a white high-neck top, looking straight into the lens with a calm, knowing gaze, lips closed, placed right of centre with dark empty space on the left for type, a fluorescent office at 3 a.m. lit by direct on-camera flash, deep blacks #0b0c0e, fluorescent green-white #d8e4dc, one warm terracotta accent #c96442, film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**L3-W. White studio close-up (hooks)**
```
35mm photo, close-up portrait of a flawless young white woman, impossibly perfect and slightly unreal, black hair slicked straight back, pale grey eyes, small terracotta stud earrings, healthy glowing skin, wearing a white high-neck top, facing the camera, still and serene, lips closed, placed centre with white space on both sides for type, a high-key white studio with a hard cobalt block behind her, clean even light, white #f4f4f1, cobalt #1f4fd6, one warm terracotta accent #c96442, film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**L3-OB. Office close-up, without --raw and the moodboard**
```
35mm photo, close-up portrait of a flawless young white woman, impossibly perfect and slightly unreal, black hair slicked straight back, pale grey eyes, small terracotta stud earrings, healthy glowing skin, wearing a white high-neck top, looking straight into the lens with a calm, knowing gaze, lips closed, placed right of centre with dark empty space on the left for type, a fluorescent office at 3 a.m. lit by direct on-camera flash, deep blacks #0b0c0e, fluorescent green-white #d8e4dc, one warm terracotta accent #c96442, film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --hd
```

## Key sets

The four sets the video returns to most, run through the moodboard. They also test the board: the office must stay dark and green-white, and the stage white and cobalt.

**K1. The office floor (verses)**
```
wide shot of an empty open-plan office at 3 a.m., rows of dark desks under a ceiling where only every other fluorescent tube is on, monitors asleep, one terracotta office chair pushed out in the middle distance, the upper third of dark ceiling empty for type, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**K2. The dark room (breaks, where the permission dialog appears)**
```
wide shot of a dark empty room with a single open laptop on a bare desk in the centre, its screen the only light, one terracotta chair beside the desk, the rest of the room falling off into black, a great deal of empty black space around the desk for a floating window, deep black #08090a, screen white-blue #cfe0ee, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**K3. The white stage (hooks)**
```
wide shot of an empty high-key white studio stage, a seamless white floor curving up into a white cyclorama, one hard cobalt block standing on the right, a chrome railing along the back, a small terracotta square marked on the floor at centre, the left half empty white for type, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**K4. The window wall (the final drop)**
```
wide shot of a white stage with one huge blank rectangular light panel standing upright like a giant window, glowing evenly, the floor in front of it bare, a small terracotta square at the panel's lower corner, the panel itself left blank and empty for type, white #f4f4f1, panel glow #fbfbf8, pale grey #dcdfe2, chrome silver, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

## Running it

As for the look tests: batches of four, check the Create page before resubmitting anything, move only finished downloads whose names contain a job ID just made into `production/assets/mj/inbox/`, and log every image in `production/storyboard/mj_manifest.csv` with `for` = "casting". Contact-sheet it plain and through `tools/print_grade.py`, and stop for the user's pick.

## R: like the reference (29 Sep)

Run on v8.2 with the reference's own settings (no `--raw`, no `--hd`, no moodboard), four images each:

**R1.** Vary (Subtle) on the reference image, job `ac724c80` image 3: close variations of her.

**R2.** The reference prompt, unchanged:
```
high-key white studio, close-up of a calm young woman in a plain grey uniform with a chrome collar pin, facing the camera, lips closed, clean even light, a hard block of colour behind her --ar 16:9
```

**R3.** Her in words, in the white studio (the hooks):
```
high-key white studio, close-up of a calm young white woman with a healthy, softly rounded face, rosy cheeks and light freckles, very dark brown hair pinned up with soft wispy bangs, grey-blue eyes, in a plain grey high-collared uniform with a chrome collar pin, facing the camera, lips closed, clean even light, a pale blue block of colour behind her --ar 16:9
```

**R4.** Her in words, in the office (the verses, her speaking framing):
```
35mm photo, close-up portrait of a calm young white woman with a healthy, softly rounded face, rosy cheeks and light freckles, very dark brown hair pinned up with soft wispy bangs, grey-blue eyes, in a plain grey high-collared uniform with a chrome collar pin, looking straight into the lens, lips closed, lit by direct on-camera flash in a fluorescent office at 3 a.m., deep blacks, one warm terracotta accent, film grain --ar 16:9
```

**Results.** The sheets are `casting/sheet_R.png` and `casting/sheet_R_graded.png`, with the reference as their top row; the reference is logged in the manifest as `t3`, with `for` = "casting reference".
- **R1** `7bdcb76d`: the same woman as the reference in all four. R1.0 is nearly the reference, and R1.3 is the softest.
- **R2** `fd7ca671`: the prompt alone doesn't bring her back. Four different women, three of them with bobs (ruled out above), with slimmer, more angular faces, and R2.2 on a red block. The reference was a lucky draw, so the wording has to carry her.
- **R3** `6fb3d39e`: her type from the words: full faces, freckles, pinned-up hair with bangs. The blush is heavy, painted-on in R3.0 and R3.3; R3.2 is the closest to the reference.
- **R4** `392c99ff`: the same words in the office, healthy and warm under the flash, with the terracotta accent. R4.0 and R4.3 are the best; R4.2 is cropped at the forehead.

All of them keep her face and colour through `print_grade.py`.

**Picked: R3.3** (the user, 29 Sep), job `6fb3d39e`, image 3. Her canon, written from it, is in `STYLE_BIBLE.md`.

## C: the canon check (29 Sep)

R3.3 was made without `--raw`, `--hd` or the moodboard, and every plate uses all three. C runs her canon in the brief's prompt order, in both sets: C1 and C3 with the plate parameters, C2 and C4 without `--raw` and the moodboard. The sheet heads with R3.3.

**C1.** White studio (hooks), plate parameters:
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, facing the camera, still and serene, lips closed, placed centre with white space on both sides for type, a high-key white studio with a hard cobalt block behind her, clean even light, white #f4f4f1, cobalt #1f4fd6, one warm terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**C2.** C1 without `--raw` and the moodboard, ending `--ar 16:9 --v 8.2 --hd`.

**C3.** Office (verses), plate parameters:
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, looking straight into the lens with a calm, knowing gaze, lips closed, placed right of centre with dark empty space on the left for type, a fluorescent office at 3 a.m. lit by direct on-camera flash, deep blacks #0b0c0e, fluorescent green-white #d8e4dc, one warm terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**C4.** C3 without `--raw` and the moodboard, ending `--ar 16:9 --v 8.2 --hd`.

**C5–C8** split the two: C5 is C1 with the moodboard only (`--ar 16:9 --v 8.2 --hd --p m7503794824781234213`), C6 is C1 with `--raw` only (`--ar 16:9 --v 8.2 --raw --hd`), and C7 and C8 are the same two for C3.

**Results.** The sheets are `casting/sheet_C.png` and `casting/sheet_C_graded.png`, headed by R3.3.
- **C1** `88a5d238` and **C3** `5b5b6d90`, with the plate parameters, lose her: hair slicked back without bangs, hollow cheeks, pale and severe. In the studio the blocks go navy and the light hard.
- **C5** `ab263e21` and **C7** `c9fa8be3`, with the moodboard only, lose her the same way, and C5 pulls back to a medium shot.
- **C2** `d5be5499` and **C4** `acf109fa`, with neither, keep her in both sets.
- **C6** `c02c0013` and **C8** `fa01e28c`, with `--raw` only, keep her in both sets, as close to R3.3 as C2 and C4.

So it's the moodboard that takes her away, not `--raw`, probably because its picks include faces of their own (B02.2's row of identical women, B09.2's large face, B11.1's clones). The user's call (29 Sep): prompts with her leave the moodboard out and end `--ar 16:9 --v 8.2 --raw --hd`.

## Dropped jobs

Run on 29 Sep, then dropped at the user's direction before review; not downloaded, not logged, not used:
- a Korean look: `32865829` (T), `7d2e9f3d` (S), `bd132945` (F);
- a South Asian look: `42f80c9b` (T), `418033ed` (S), `a784dcb2` (F);
- a West African look: `a65710b4` (T), `72967e32` (S), `7427d460` (F);
- a Northern European look with ash-blonde hair: `7af1c0ee` (T), `b3dfbdd1` (S), `012875d7` (F);
- the same with black hair, before the beauty wording: `114baa0b` (T), `2fe3f786` (S), `2295c8dd` (F);
- the first beautiful looks, which the user found anemic (pale, cold light, gaunt): Italian `99085b1d` (T) and its S and F, Slavic `16c7896f` (T), `021dc23a` (S), `d8e0413e` (F), Northern European T and S (not collected).
- the warmer rewrite of those three face sheets, which the user found soulless ("the original images looks much better"); not collected.
