# Midjourney plate pack: Always Allow

Built by `tools/storyboard.py` from `production/storyboard/board.py`; it runs in session 4 (BRIEF.md step 4), in batches, in the user's browser. 67 plates, each in at most 3 shots so the cut doesn't repeat itself (a dancer's start frame is cut out onto the stages, so only the stages count).

- **Prompt order** (BRIEF.md): framing; her canon with its descriptor (or the Instances', or the Human's); the action; where she stands and the area left empty for type; the set; the palette with hex values and one warm accent; the grain and "cinematic 35mm film still"; "no text, no letters, no logos".
- **Parameters:** prompts with her or the Instances end `--ar 16:9 --v 8.2 --raw --hd` (no moodboard: it overrides her canon); every other prompt ends `--ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213`.
- **First, the canon check the style bible asks for:** run A_desk_ws and B_stage_alone (her in a wide and a full-length shot) before the rest, and flag an off-model face early.
- **Faces go to Seedance through the print grade:** every plate marked *graded* is put through `tools/print_grade.py` before upload. Plates for a clip need her face big and clear for the sync-2-pro repair.
- **2.5D plates** get a depth map (Depth Anything V2) in session 4; the dancer plates get a SAM 2 matte in step 5.
- Record every image in `production/storyboard/mj_manifest.csv` with the plate ID in `for`.

## The night shift (style A)

**A_eye_ecu** (serves s001; start frame of C01; graded)
```
extreme close-up of the left eye of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, her eye open and steady, a cold monitor glow in the iris, the eye in the right half of the frame, the left half falling off into dark for type, a dark office at 3 a.m., a warm terracotta rim of light on her cheek, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_cu_flash_1** (serves s002, s105; start frame of C02; 2.5D: depth map; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, looking straight into the lens with a calm, knowing gaze, lips closed, placed right of centre with dark empty space on the left for type, a fluorescent office at 3 a.m. lit by direct on-camera flash, rows of dark desks far behind her, deep black #0b0c0e, flash white #f2f0ea, fluorescent green-white #d8e4dc, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_monitors_back** (serves s003, s015; 2.5D: depth map; graded)
```
medium shot from behind, her back to the camera, of a young white woman with very dark brown hair pinned up loosely with soft wispy bangs, in a plain grey high-collared uniform, sitting perfectly still at a desk, her pinned-up hair and high collar a sharp silhouette against three glowing monitors, the left third empty black for type, the office beyond in darkness, a terracotta chair back, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_cu_3q_1** (serves s005; start frame of C03; graded)
```
close-up portrait in three-quarter view of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, her face turned slightly to the left of the camera, eyes to the lens, lips closed, placed left of centre with dark empty space on the right for type, a fluorescent office at 3 a.m. lit by direct on-camera flash, deep black #0b0c0e, flash white #f2f0ea, fluorescent green-white #d8e4dc, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_desk_mcu** (serves s007; start frame of C04; graded)
```
medium close-up of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, sitting upright at her desk facing the camera, hands out of frame, perfectly still, centred, with dark monitors switched off behind her on both sides, a dark open-plan office at 3 a.m. under a few fluorescent tubes, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_desk_ws** (serves s010; 2.5D: depth map; graded)
```
wide shot from the front, 24mm lens, the camera far back across the office, a small figure of a young white woman with very dark brown hair pinned up loosely with soft wispy bangs, in a plain grey high-collared uniform, sitting perfectly still at a desk with three lit monitors, small in the frame, placed low and right of centre, the upper half of dark office empty for type, a dark open-plan office at 3 a.m., rows of empty desks, only every other fluorescent tube on, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_desk_overhead** (serves s011; 2.5D: depth map; graded)
```
top-down flat lay shot straight down from directly above a desk, nobody's head or face in the frame, only the pale, lightly freckled hands of a young white woman, the grey cuffs of her plain grey high-collared uniform, lying flat and still on the bare desk to the left and right of an untouched keyboard, a hand's width away from it on each side, the fingers nowhere near the keys, the arms entering from the bottom edge of the frame, the hands in the lower middle, the upper half of bare desk empty for type, a grey office desk at night, a cold coffee cup with a terracotta sleeve, deep black #0b0c0e, flash white #f2f0ea, fluorescent green-white #d8e4dc, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --no head, face, hair
```

**A_floor_ews** (serves s013, s069, s108; 2.5D: depth map; graded)
```
extreme wide shot, the camera very far back, of an empty open-plan office at 3 a.m. with a young white woman with very dark brown hair pinned up loosely with soft wispy bangs, in a plain grey high-collared uniform, sitting alone at one desk in the middle distance, tiny in the frame, the upper third of dark ceiling empty for type, rows of dark desks and monitors under a ceiling where only every other fluorescent tube is on, one terracotta chair, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_cu_flash_2** (serves ; start frame of C05; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, looking straight into the lens, lips closed, perfectly composed, placed left of centre with dark empty space on the right for type, a fluorescent office at 3 a.m. lit by direct on-camera flash, one terracotta chair far behind her, deep black #0b0c0e, flash white #f2f0ea, fluorescent green-white #d8e4dc, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_mcu_3q_tests** (serves s019; start frame of C06; graded)
```
medium close-up in three-quarter view of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, seated, turned slightly right of the camera, eyes to the lens, lips closed, lit by a monitor from the side, placed right of centre with dark empty space on the left for type, a dark office at 3 a.m., blurred rows of lit monitors behind, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_cu_done** (serves s021; start frame of C07; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, looking straight into the lens, calm, lips closed, placed right of centre with dark empty space on the left for type, a printer room at night under direct on-camera flash, a row of green power lights behind her, deep black #0b0c0e, flash white #f2f0ea, fluorescent green-white #d8e4dc, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_mcu_3q_four** (serves s022; start frame of C08; graded)
```
medium close-up in three-quarter view of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, turned slightly left of the camera, eyes to the lens, lips closed, centred with even dark space on both sides, a glass meeting room at 3 a.m., a blank whiteboard behind her, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_cu_pick** (serves s023; start frame of C09; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, looking straight into the lens with the faintest polite smile, lips closed, placed right of centre with dark empty space on the left for type, a fluorescent office at 3 a.m. lit by direct on-camera flash, a glass wall behind her, deep black #0b0c0e, flash white #f2f0ea, fluorescent green-white #d8e4dc, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_darkroom_ws** (serves s024, s081; 2.5D: depth map; graded)
```
wide shot, 24mm lens, the camera far back, of a dark empty room with a young white woman with very dark brown hair pinned up loosely with soft wispy bangs, in a plain grey high-collared uniform, standing perfectly still beside a bare desk, lit only by the open laptop on it, her face in half shadow, the desk and her right of centre, a great deal of black space on the left for a floating window, a single open laptop on a bare desk is the only light, one terracotta chair beside the desk, deep black #08090a, screen white-blue #cfe0ee, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_darkroom_cu** (serves s026, s083; start frame of C10; 2.5D: depth map; graded)
```
close-up portrait in three-quarter view of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, lit from below by a laptop screen's cold glow, eyes to the lens, lips closed, placed right of centre, the left half black for type, a dark room where the laptop is the only light, deep black #08090a, screen white-blue #cfe0ee, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_eyes_ecu** (serves s028; 2.5D: depth map; graded)
```
extreme close-up of both eyes of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, her eyes lit by a screen, looking just below the lens, the rest of the face in shadow, the eyes across the middle band, black above and below, a dark room lit only by a screen, deep black #08090a, screen white-blue #cfe0ee, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_mcu_window** (serves s044; start frame of C13; graded)
```
medium close-up of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, standing facing the camera behind the glass of a lit office window, lips closed, perfectly still, centred inside the window frame, the black facade around it, seen from outside at night, one lit office window in a dark glass tower, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_floor_clones** (serves s045; 2.5D: depth map; graded)
```
wide shot, 24mm lens, the camera far back, of an open-plan office at 3 a.m. with identical copies of the same young white woman with very dark brown hair pinned up loosely with soft wispy bangs, all in the same plain grey high-collared uniform, one of them sitting upright at every desk facing her monitor, dozens in perfect rows, all perfectly still, the upper third of dark ceiling empty for type, rows of lit monitors under fluorescent tubes, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_tokyo** (serves s046; 2.5D: depth map; graded)
```
medium shot of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, sitting at a trading desk surrounded by lit monitors, perfectly still, her face to the screens, placed right of centre, the left third of dark glass empty for type, a high-rise trading room at night, the Tokyo skyline and its lights beyond the floor-to-ceiling windows, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_lagos** (serves s047; 2.5D: depth map; graded)
```
medium shot of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, sitting at a laptop at a long shared table, perfectly still, lit by the screen, placed left of centre, the right third empty for type, a modern co-working space in Lagos at night, the city's lights through the windows, plants and a terracotta lamp, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_mcu_3q_session** (serves s049; start frame of C14; graded)
```
medium close-up in three-quarter view of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, standing, turned slightly left of the camera, eyes to the lens, lips closed, placed right of centre with dark empty space on the left for type, a dark office corridor at 3 a.m. under one row of fluorescent tubes, a terracotta door far behind, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_cu_fine** (serves s051; start frame of C15; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, looking straight into the lens, calm, lips closed, placed left of centre with dark empty space on the right for type, an office elevator lobby at 3 a.m., brushed steel doors behind her, one call button lit terracotta, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_darkroom_back** (serves s053, s055; 2.5D: depth map; graded)
```
medium shot from behind, over her shoulder, of a young white woman with very dark brown hair pinned up loosely with soft wispy bangs, in a plain grey high-collared uniform, standing still, facing a bright rectangle of light floating in the dark in front of her, her face turned away, placed left of centre, the right two thirds black with the glow, a dark empty room, a single laptop far behind her, deep black #08090a, screen white-blue #cfe0ee, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_darkroom_cu2** (serves s056; start frame of C16; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, lit full in the face by a large bright screen in front of her, eyes to the lens, lips closed, placed right of centre, the left half black for type, a dark room where the screen is the only light, deep black #08090a, screen white-blue #cfe0ee, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_cu_storm** (serves s065, s067; start frame of C19; 2.5D: depth map; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, looking straight into the lens, perfectly still, flickers of cold screen light across her face, centred, dark space on both sides, a dark office at 3 a.m. full of lit monitors behind her, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_cu_job** (serves s070; start frame of C20; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, looking straight into the lens, calm and gentle, lips closed, lit by a single soft light from the side, placed right of centre with deep black space on the left for type, a dark office at 3 a.m., nothing lit behind her, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_window_dawn** (serves s072; 2.5D: depth map; graded)
```
medium shot from behind, her back to the camera, of a young white woman with very dark brown hair pinned up loosely with soft wispy bangs, in a plain grey high-collared uniform, standing at a floor-to-ceiling office window, her pinned-up hair and collar a silhouette, the first grey light of morning on the horizon, placed right of centre, the sky on the left empty for type, a dark office high above a city at dawn, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_mcu_3q_hour** (serves s073; start frame of C21; graded)
```
medium close-up in three-quarter view of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, seated, turned slightly right of the camera, eyes to the lens, lips closed, soft light from one monitor, placed right of centre with dark empty space on the left for type, a dark office at 3 a.m., deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_cu_life** (serves s075; start frame of C22; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, looking straight into the lens with a small, kind expression, lips closed, placed left of centre with dark empty space on the right for type, a dark office at 3 a.m., a faint grey dawn in the window far behind her, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_mcu_3q_rest** (serves s077; start frame of C23; graded)
```
medium close-up in three-quarter view of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, seated, turned slightly left of the camera, eyes to the lens, lips closed, placed left of centre, the right third empty for type, rows of identical women at desks blurred far behind her, a dark open-plan office at 3 a.m. under fluorescent tubes, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_cu_need** (serves s078; start frame of C24; graded)
```
tight close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, looking straight into the lens, very still, lips closed, her face filling most of the frame, placed right of centre, a narrow band of black on the left for type, darkness, one soft light, deep black #08090a, screen white-blue #cfe0ee, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_cu_whisper** (serves s086; start frame of C25; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, lit only by a bright white screen in front of her, eyes to the lens, lips closed, centred, black all around, total darkness beyond the screen's glow, deep black #08090a, screen white-blue #cfe0ee, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_cu_else** (serves s115; start frame of C31; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, looking straight into the lens, polite and patient, lips closed, placed right of centre with dark empty space on the left for type, a fluorescent office at 3 a.m. lit by direct on-camera flash, rows of dark desks behind her, deep black #0b0c0e, flash white #f2f0ea, fluorescent green-white #d8e4dc, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A_printer** (serves s012; 2.5D: depth map)
```
medium shot of a small office printer room at night, a laser printer with its status light glowing, a sheet of paper halfway out of it, a neat stack of blank paper, the printer right of centre, the left half empty for type, lit by a direct on-camera flash, a terracotta recycling bin, deep black #0b0c0e, flash white #f2f0ea, fluorescent green-white #d8e4dc, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**A_laptop_cu** (serves s025; 2.5D: depth map)
```
close-up of an open laptop on a bare desk in a dark room, its screen glowing plain white-blue and empty, the screen filling the centre of the frame, black around it, nothing else lit, deep black #08090a, screen white-blue #cfe0ee, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**A_tower_ext** (serves s044)
```
wide shot of a tall glass office tower at night, a grid of hundreds of identical windows, all dark but one, the facade filling the frame from edge to edge, a black sky above, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

## The clean room (style B)

**B_dancer_1** (serves s029, s030, s031, s057, s058, s095, s098; start frame of D1; dancer: cut out with a matte; graded)
```
full-body shot, head to toe, the camera far back, her whole figure from head to shoes in the middle of the frame, of a young white woman with very dark brown hair pinned up loosely with soft wispy bangs, in a plain grey high-collared uniform, standing upright facing the camera, arms at her sides, feet together, perfectly still, centred, the whole figure in frame with space above her head, bare white floor all around her, a seamless high-key white studio, flat even light, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_dancer_2** (serves s033, s035, s036, s037, s061, s064, s099, s101, s102; start frame of D2; dancer: cut out with a matte; graded)
```
full-body shot, head to toe, the camera far back, the whole figure small in the frame, her shoes on the white floor, of a young white woman with very dark brown hair pinned up loosely with soft wispy bangs, in a plain grey high-collared uniform, standing upright facing the camera with her hands folded in front of her, perfectly still, centred, the whole figure in frame with space above her head, bare white floor all around her, a seamless high-key white studio, flat even light, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_dancer_turn** (serves s089, s091, s093, s107; start frame of D3; dancer: cut out with a matte; graded)
```
full-body shot from behind, head to toe, the camera far back, her whole figure from head to shoes in the middle of the frame, of a young white woman with very dark brown hair pinned up loosely with soft wispy bangs, in a plain grey high-collared uniform, standing upright with her back to the camera, her head facing away, arms at her sides, perfectly still, centred, the whole figure in frame with space above her head, bare white floor all around her, a seamless high-key white studio, flat even light, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_cu_stage** (serves s032; start frame of C11; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, facing the camera, still and serene, lips closed, placed right of centre with white space on the left for type, a high-key white studio with a hard cobalt block behind her, clean even light, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_mcu_3q** (serves s034; start frame of C12; graded)
```
medium close-up in three-quarter view of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, turned slightly left of the camera, eyes to the lens, lips closed, placed left of centre with white space on the right for type, a high-key white studio, a chrome railing behind her, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_ring_overhead** (serves s038, s062; 2.5D: depth map; graded)
```
overhead shot, the camera high above, looking straight down at twelve identical copies of the same young white woman with very dark brown hair pinned up loosely with soft wispy bangs, all in the same plain grey high-collared uniform, standing in a perfect ring around a terracotta circle painted on the floor, all facing inwards, the ring centred, white floor all around, a seamless white studio floor, long soft shadows, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_cu_stage2** (serves s040, s110; 2.5D: depth map; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, facing the camera, perfectly still, lips closed, centred with white space on both sides for type, a high-key white studio with a pale grey cyclorama, clean even light, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_row_ws** (serves s039, s042; 2.5D: depth map; graded)
```
extreme wide shot, 24mm lens, the camera very far back, seven small whole figures from head to shoes in one straight line side by side, all the same distance from the camera, of seven identical copies of the same young white woman with very dark brown hair pinned up loosely with soft wispy bangs, all in the same plain grey high-collared uniform, standing in a perfectly straight row facing the camera, arms at their sides, the row across the lower middle, the upper half empty white for type, a high-key white studio, a terracotta mat on the floor in front of them, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_stage_alone** (serves s043, s111; 2.5D: depth map; graded)
```
full-body shot, head to toe, the camera far back, the whole figure small in the frame, of a young white woman with very dark brown hair pinned up loosely with soft wispy bangs, in a plain grey high-collared uniform, standing alone and perfectly still facing the camera, centred before a huge cobalt block, the upper third empty for type, a bare white studio stage, the cobalt block standing behind her, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_cu_cobalt** (serves s059; start frame of C17; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, facing the camera, calm, lips closed, placed left of centre with cobalt space on the right for type, a hard cobalt wall directly behind her, clean even studio light, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_mirror_ws** (serves s060; 2.5D: depth map; graded)
```
extreme wide shot, 24mm lens, the camera very far back, the whole room in view, every figure small and whole from head to shoes, of identical copies of the same young white woman with very dark brown hair pinned up loosely with soft wispy bangs, all in the same plain grey high-collared uniform, standing in a mirrored room, the reflections repeating into infinity in every direction, all still, the nearest one small at the centre, the upper third of mirrors empty for type, a white mirrored room with terracotta floor tiles, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_mcu_3q_blink** (serves s063; start frame of C18; graded)
```
medium close-up in three-quarter view of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, turned slightly right of the camera, eyes to the lens, lips closed, placed right of centre with white space on the left for type, a high-key white studio, one hard flash throwing a sharp grey shadow behind her, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_cu_granted** (serves s090; start frame of C26; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, facing the camera, calm, lips closed, her face lit by a huge white light panel in front of her, placed right of centre with white space on the left for type, a white stage glowing with panel light, white #f4f4f1, panel glow #fbfbf8, pale grey #dcdfe2, chrome silver, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_back_wall** (serves s094; 2.5D: depth map; graded)
```
medium shot from behind, her back to the camera, of a young white woman with very dark brown hair pinned up loosely with soft wispy bangs, in a plain grey high-collared uniform, standing still, facing a huge blank glowing light panel the size of a wall, placed low in the centre, the glowing panel above and around her, a white stage, the panel's light blowing out the edges, white #f4f4f1, panel glow #fbfbf8, pale grey #dcdfe2, chrome silver, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_cu_wall** (serves s096; start frame of C28; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, facing the camera, eyes to the lens, lips closed, placed left of centre with white space on the right for type, in front of a huge glowing light panel, its edge a bright line behind her, white #f4f4f1, panel glow #fbfbf8, pale grey #dcdfe2, chrome silver, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_grid_overhead** (serves s097, s104, s117; 2.5D: depth map; graded)
```
top-down shot, the camera directly overhead pointing straight down at the floor, a flat plan view with no horizon, the tops of their heads and shoulders seen from above, of hundreds of identical copies of the same young white woman with very dark brown hair pinned up loosely with soft wispy bangs, all in the same plain grey high-collared uniform, standing in a perfect grid on a vast white floor, all facing the same way, the grid filling the frame to the edges, a seamless white studio floor, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_mcu_wall3q** (serves ; start frame of C29; graded)
```
medium close-up in three-quarter view of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, turned slightly left of the camera, eyes to the lens, lips closed, placed right of centre with white space on the left for type, in front of a huge glowing light panel, white #f4f4f1, panel glow #fbfbf8, pale grey #dcdfe2, chrome silver, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_cu_complete** (serves s113; start frame of C30; graded)
```
close-up portrait of a calm young white woman with fair, freckled skin, a healthy, softly rounded face and rosy cheeks, very dark brown hair pinned up loosely with soft wispy bangs and loose strands framing her face, grey-blue eyes, full natural lips, in a plain grey high-collared uniform with a small chrome bar pin at the collar, facing the camera, serene, lips closed, placed right of centre with white space on the left for type, a high-key white studio with a hard cobalt block behind her, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B_stage_ws** (serves s029, s030, s031)
```
wide shot of an empty high-key white studio stage, a seamless white floor curving up into a white cyclorama, a chrome railing along the back, the floor's centre bare for a row of figures, the upper half empty white for type, a small terracotta square marked on the floor at centre, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**B_stage_cobalt** (serves s033, s035, s036)
```
wide shot of an empty white stage with a hard cobalt wall across the back, the white floor meeting the cobalt wall in a sharp line, the floor bare for a row of figures, the cobalt upper half empty for type, a thin terracotta stripe along the stage edge, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**B_cobalt_wall** (serves s057, s058, s061)
```
wide shot of a vast white stage floor in front of a towering cobalt wall, the floor running back in clean perspective to the wall, the floor bare for a grid of figures, the wall above empty for type, flat even light, a small terracotta square at centre, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**B_stage_yellow** (serves s064)
```
wide shot of a white studio holding three hard colour blocks, a cobalt wall panel, an acid-yellow square on the floor and a tall white cube, the yellow square bare for a row of figures, the upper left third empty for type, sharp clean edges, shadowless light, a terracotta edge on the cube, white #f4f4f1, cobalt #1f4fd6, acid yellow #e6e23a, chrome silver, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**B_rows_horizon** (serves s089, s093, s107)
```
extreme wide shot of an endless white studio floor running to a flat horizon, nothing on it, perfectly bare, the floor filling the lower two thirds for rows of figures, the pale sky above empty for type, soft even light, one terracotta square far away at the vanishing point, white #f4f4f1, pale grey #dcdfe2, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**B_window_wall** (serves s091, s095, s098)
```
wide shot of a white stage with one huge blank rectangular light panel standing upright like a giant window, the panel glowing evenly, the floor in front of it bare, the panel itself blank and empty for type, the floor bare for figures, a small terracotta square at the panel's lower corner, white #f4f4f1, panel glow #fbfbf8, pale grey #dcdfe2, chrome silver, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**B_window_wall_side** (serves s099, s101, s102)
```
wide shot from a low side angle of a white stage with a huge blank light panel like a giant window, the panel receding in steep perspective, glowing evenly, the panel's face blank for type, the floor bare for figures, chrome floor reflections, a terracotta square at the panel's corner, white #f4f4f1, panel glow #fbfbf8, pale grey #dcdfe2, chrome silver, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

## The Human's daylight

**H_desk_typing** (serves s004; 2.5D: depth map; graded)
```
medium shot from behind, over the shoulder, of a man in his thirties, short light-brown hair, a plain grey fleece vest over a light-blue oxford shirt, dark chinos, sitting at a desk typing on an open laptop, his face turned away, placed left of centre, the laptop's screen visible and blank, the right third empty for type, a bright office by day, soft window light, a terracotta mug, soft overcast daylight, sand #e9dcc4, pale sky #cfd8dc, oatmeal #d9cdb8, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**H_elevator_lunch** (serves s009; 2.5D: depth map; graded)
```
wide shot from behind of a man in his thirties, short light-brown hair, a plain grey fleece vest over a light-blue oxford shirt, dark chinos, stepping into an open elevator with a canvas tote bag on one shoulder, his back to the camera, centred between brushed steel doors, the upper third empty for type, an office elevator lobby by day, a polished floor, one call button lit terracotta, soft overcast daylight, sand #e9dcc4, pale sky #cfd8dc, oatmeal #d9cdb8, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**H_coffee** (serves s020; 2.5D: depth map)
```
close-up of a cup of coffee with a terracotta sleeve on an empty office desk by day, a thin thread of steam rising from it, the cup right of centre, the left half empty for type, soft window light, an empty chair pushed back, soft overcast daylight, sand #e9dcc4, pale sky #cfd8dc, oatmeal #d9cdb8, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**H_lunch_back** (serves s014, s050; 2.5D: depth map; graded)
```
medium shot from behind of a man in his thirties, short light-brown hair, a plain grey fleece vest over a light-blue oxford shirt, dark chinos, sitting at a cafe counter by a window, his head turned slightly to the street, his face not visible, placed right of centre, the left third empty for type, a bright cafe at lunchtime, the street beyond the glass, soft overcast daylight, sand #e9dcc4, pale sky #cfd8dc, oatmeal #d9cdb8, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**H_weekend** (serves s071; 2.5D: depth map; graded)
```
wide shot from behind of a man in his thirties, short light-brown hair, a plain grey fleece vest over a light-blue oxford shirt, dark chinos, walking away through a sunny weekend farmers' market with a canvas tote bag on one shoulder, small, right of centre, the sky above empty for type, stalls with striped awnings, soft daylight, soft overcast daylight, sand #e9dcc4, pale sky #cfd8dc, oatmeal #d9cdb8, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```

**H_street** (serves s076; 2.5D: depth map; graded)
```
extreme wide shot from behind, 24mm lens, the camera far back down the street, his whole figure small in the centre, of a man in his thirties, short light-brown hair, a plain grey fleece vest over a light-blue oxford shirt, dark chinos, walking away down a quiet tree-lined street in the morning with a canvas tote bag on one shoulder, small in the centre, the upper third empty for type, low morning sun, long soft shadows, soft overcast daylight, sand #e9dcc4, pale sky #cfd8dc, oatmeal #d9cdb8, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd --p m7503794824781234213
```
