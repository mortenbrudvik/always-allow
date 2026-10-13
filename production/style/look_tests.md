# Look tests (BRIEF.md step 2, PLAN.md phase 1b)

The first Midjourney batch: the look for both styles from prompt text alone, before there's a moodboard or a cast. You pick your favourites from the contact sheets; they go into a moodboard named "Always Allow", and its code goes into every prompt from then on (`STYLE_BIBLE.md`).

- **Parameters:** `--ar 16:9 --v 8.2 --raw --hd` on every prompt. No moodboard or profile yet; this batch is what makes the moodboard.
- **Prompt order** (BRIEF.md): framing; the figure; the action; where she stands and the area left empty for type; the set; the palette with hex values and one warm accent; the grain and "cinematic 35mm film still"; "no text, no letters, no logos".
- **The stand-in figure** is deliberately plain: "a young woman in a plain dark uniform" (A) or "in a plain white uniform" (B), mostly from behind, small in frame or in silhouette, so this batch sets the look without casting her. Casting comes next.
- **What each prompt tests** is in its heading. Style A covers the verses and breaks, style B the hooks.
- **From step 0:** Seedance inputs go through the print grade (`tools/print_grade.py`), and bright, high-key plates came back from Seedance almost photoreal while dark ones kept visible dots. That texture is approved, so dark plates are fine; the contact sheets show each pick graded too.

## Style A: night-shift office noir

Photoreal 35 mm with direct flash, a fluorescent office at 3 a.m., deep blacks, one warm terracotta accent. The halftone goes on in post, so it isn't in the prompts.

**A01. The set, wide: half-lit open plan**
```
wide shot of an empty open-plan office at 3 a.m., rows of desks under a ceiling where only every other fluorescent tube is on, one tube flickering, monitors asleep, a single terracotta office chair pushed out from a desk in the middle distance, the upper third of dark ceiling empty for type, deep black #0b0c0e, fluorescent green-white #d8e4dc, sleeping-monitor blue #2f4a66, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A02. Light: direct flash on a desk at night**
```
medium close shot of a cluttered desk at night lit only by a direct on-camera flash, a cold cup of coffee with a terracotta sleeve, a keyboard, a tangled lanyard, hard black shadows thrown onto the grey partition behind, the right half dark and empty for type, deep black #0b0c0e, flash-white #f2f0ea, partition grey #5d6166, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A03. Light: monitor glow, stand-in from behind**
```
medium shot from behind of a young woman in a plain dark uniform sitting very still at a desk, lit only by the cold glow of three monitors, her head and shoulders a sharp silhouette against them, the office beyond in darkness, the left third empty black for type, deep black #0b0c0e, monitor blue #4d7ea8, fluorescent green-white #d8e4dc, one terracotta accent #c96442 on the chair back, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A04. Space: the corridor, a small still figure**
```
wide shot down a long office corridor at night under a single row of fluorescent tubes, a young woman in a plain dark uniform standing perfectly still far down the corridor facing the camera, a terracotta fire door at the far end, the ceiling above her empty for type, deep black #0b0c0e, fluorescent green-white #d8e4dc, carpet grey #3b3f44, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A05. The set: a glass meeting room**
```
wide shot through the glass wall of a dark meeting room at 3 a.m., chairs pushed in around a long table, a whiteboard wiped blank, one terracotta chair, the rows of the open office reflected in the glass, the upper third empty for type, deep black #0b0c0e, glass teal #6f8f8a, fluorescent green-white #d8e4dc, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A06. The set: the printer room**
```
medium shot of a small office printer room at night, a laser printer with its status light glowing, a neat stack of blank paper, a row of green power lights along a shelf, a terracotta recycling bin, lit by a direct on-camera flash, the left half empty for type, deep black #0b0c0e, flash-white #f2f0ea, status green #3fae6a, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A07. The break's dark room: one lit screen**
```
wide shot of a dark empty room with a single open laptop on a bare desk in the centre, its screen the only light, the rest of the room falling off into black, one terracotta chair beside the desk, a great deal of empty black space around the desk for a floating window, deep black #08090a, screen white-blue #cfe0ee, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A08. Space: the elevator lobby, stand-in waiting**
```
wide shot of an office elevator lobby at 3 a.m., brushed steel doors, one call button lit, the polished floor reflecting the fluorescent ceiling, a young woman in a plain dark uniform waiting with her back to the camera, the right third empty for type, deep black #0b0c0e, steel grey #8a9096, fluorescent green-white #d8e4dc, one terracotta accent #c96442 on the call button, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A09. The intro's hook framing: an eye lit by a monitor**
```
extreme close-up of a woman's eye and cheekbone lit only by the blue light of a monitor, a small white rectangle reflected in her eye, the rest of the frame in deep shadow, the left half black and empty for type, deep black #07080a, monitor blue #4d7ea8, skin in cool light, one terracotta accent #c96442 as a warm rim on her cheek, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A10. The world outside: one lit floor**
```
wide shot of a glass office tower at night with only one floor lit, its fluorescent windows a single green-white band across the dark building, one window glowing terracotta, the black sky above empty for type, deep black #07080a, fluorescent green-white #d8e4dc, sodium streetlight amber #b9853e low in frame, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A11. Texture: coffee steam in the office kitchen**
```
medium shot of an office kitchen at 3 a.m., a coffee machine breathing steam into the fluorescent light, a single terracotta mug under the spout, a sink and a stack of clean cups, lit by a direct on-camera flash, the left half empty for type, deep black #0b0c0e, fluorescent green-white #d8e4dc, flash-white #f2f0ea, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**A12. Texture: flash and motion, stand-in walking**
```
medium shot of a young woman in a plain dark uniform walking fast past rows of dark desks at night, a direct on-camera flash freezing her while the fluorescent tubes streak behind her in a slow shutter, slight motion blur at the edges, the right third empty for type, deep black #0b0c0e, fluorescent green-white #d8e4dc, flash-white #f2f0ea, one terracotta accent #c96442 on a passing chair, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

## Style B: clean-room stage

A high-key white studio, chrome, identical uniforms and hard colour blocks: cute and creepy at once. The same terracotta accent carries over from style A.

**B01. The set, wide: the empty white stage**
```
wide shot of an empty high-key white studio stage, a seamless white floor curving up into a white cyclorama, one hard cobalt block panel on the right wall, a chrome railing along the back, even soft shadowless light, the left half empty white for type, white #f4f4f1, pale grey #dcdfe2, chrome silver, one hard cobalt block #1f4fd6, one terracotta accent #c96442 as a small square on the floor, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B02. The formation: nine identical women in a grid**
```
wide shot of nine identical young women in plain white uniforms standing in a perfect three-by-three grid on a white studio floor, all facing the camera, arms at their sides, expressions blank, hard even light, a single terracotta square taped on the floor in front of the grid, the top third empty white for type, white #f4f4f1, pale grey #dcdfe2, chrome silver, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B03. Detail: chrome on a white uniform**
```
close-up of a small chrome collar pin on a plain white high-collared uniform, hard studio light, the pin reflecting a white room and a tiny cobalt block, one terracotta stitch at the collar edge, the right half empty soft white for type, white #f4f4f1, chrome silver, cobalt #1f4fd6, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B04. Colour blocks: three hard shapes in a white room**
```
wide shot of a white studio holding three hard colour blocks, a cobalt wall panel, an acid-yellow square on the floor and a tall white cube, sharp clean edges, shadowless light, the upper left third empty for type, white #f4f4f1, cobalt #1f4fd6, acid yellow #e6e23a, chrome silver, one terracotta accent #c96442 on the cube's edge, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B05. The hook's bow: a line bowing in unison**
```
wide shot of a line of seven identical young women in plain white uniforms bowing deeply in perfect unison on a white stage, backs straight, hands at their sides, a hard cobalt block behind them, the top third empty white for type, white #f4f4f1, pale grey #dcdfe2, cobalt #1f4fd6, one terracotta accent #c96442 on the stage edge, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B06. The set: a clean-room airlock**
```
wide shot of a white clean-room airlock corridor with chrome doors at the far end, a soft glowing panel in the ceiling, perforated white floor tiles, a young woman in a plain white uniform standing small in the doorway facing the camera, the left third empty for type, white #f4f4f1, pale grey #dcdfe2, chrome silver, one terracotta accent #c96442 as a door light, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B07. The formation from above**
```
overhead shot looking straight down at a white floor where twelve identical young women in plain white uniforms stand in a perfect ring, all facing the centre, their shadows short and hard, one terracotta circle painted in the middle of the ring, the edges of the frame empty white for type, white #f4f4f1, pale grey #dcdfe2, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B08. Light: a stand-in dead centre, hard colour behind**
```
medium shot of a young woman in a plain white uniform standing dead centre on a white stage, facing the camera, perfectly still and expressionless, a hard cobalt block behind her filling the middle of the frame, even high-key light, the left and right thirds empty white for type, white #f4f4f1, cobalt #1f4fd6, chrome silver, one terracotta accent #c96442 on her collar, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B09. "A thousand of me": a mirrored infinity**
```
wide shot inside a small mirrored chrome room that repeats one young woman in a plain white uniform into infinity in every direction, the reflections receding in perfect rows, cool even light, the upper third empty for type, white #f4f4f1, chrome silver, pale grey #dcdfe2, one terracotta accent #c96442 as a single square tile repeated with her, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B10. Texture: hard flash on white**
```
full-length shot of a young woman in a plain white uniform standing against a bare white wall, a hard direct flash throwing one sharp grey shadow behind her, a chrome stool beside her, the right half empty white for type, white #f4f4f1, shadow grey #b7bbbf, chrome silver, one terracotta accent #c96442 on the stool seat, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B11. The drop's scale: rows of clones on a vast white floor**
```
extreme wide shot of a vast white studio floor filled with hundreds of identical young women in plain white uniforms standing in long perfect rows toward the horizon, all facing the camera, the tiny figures sharp in the flat high-key light, one terracotta figure-sized square in the front row, the white sky above empty for type, white #f4f4f1, pale grey #dcdfe2, one terracotta accent #c96442, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

**B12. The window as architecture: a blank light panel**
```
wide shot of a white stage with one huge blank rectangular light panel standing upright like a giant window, glowing evenly, a small young woman in a plain white uniform standing before it with her back to the camera, the panel itself left blank and empty for type, white #f4f4f1, panel glow #fbfbf8, pale grey #dcdfe2, chrome silver, one terracotta accent #c96442 as a small square at the panel's corner, fine film grain, cinematic 35mm film still, no text, no letters, no logos --ar 16:9 --v 8.2 --raw --hd
```

## Running it

Run the prompts in batches of four in your signed-in Chrome, as BRIEF.md and HANDOVER.md describe: check the Create page before resubmitting anything, move only finished downloads whose names contain a job ID just made into `production/assets/mj/inbox/`, and log every image in `production/storyboard/mj_manifest.csv` (prompt ID, job ID, index, file, and "look test"). Contact-sheet each style with ffmpeg's `tile` filter, each image also shown through `tools/print_grade.py`, and stop for your picks.
