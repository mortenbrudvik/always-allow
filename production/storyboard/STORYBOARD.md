# Storyboard: Always Allow

Built by `tools/storyboard.py` from `production/storyboard/board.py` on 2026-09-30; `shots.json` holds the same shots, clips and plates for the compositor and the pipeline. The idea, the palette, the type and the rules are in `production/style/STYLE_BIBLE.md`; the Midjourney plates are in `mj_prompts.md`.

**119 shots** (41 2.5d, 30 code, 48 seedance), **33 Seedance clips** (27 speaking, 6 motion and dancer), 150 s of Seedance, 67 plates. The Agent is on screen 74% of the time.

How to read a shot: its time range is on the beat grid (song seconds, and bars with bar 0 on the first drop); each lyric line is listed on the shot where its first word falls, with its type mode and text zone, and stays on screen until it ends. Tiers: **seedance** (a clip; a dancer clip is cut out with a matte and composited on the named stage), **2.5d** (a plate over its depth map), **code** (drawn entirely in code). Every shot starts `planned`.

## Chapters

One file per chapter in `production/comp/src/chapters/`, so animator agents never edit each other's.

| Chapter | Name | Time | Shots |
|---|---|---|---|
| ch01 | Give me a goal | 0:00.00–0:14.38 | s001–s005 (5) |
| ch02 | Tabs open | 0:14.38–0:35.86 | s006–s013 (8) |
| ch03 | One sentence | 0:35.86–1:01.38 | s014–s023 (10) |
| ch04 | A little window | 1:01.38–1:17.95 | s024–s028 (5) |
| ch05 | Always allow I | 1:17.95–1:47.73 | s029–s043 (15) |
| ch06 | A thousand of me | 1:47.73–2:09.45 | s044–s052 (9) |
| ch07 | A bigger window | 2:09.45–2:22.44 | s053–s056 (4) |
| ch08 | Always allow II | 2:22.44–2:36.32 | s057–s064 (8) |
| ch09 | Approval fatigue | 2:36.32–2:52.43 | s065–s070 (6) |
| ch10 | Your weekends | 2:52.43–3:13.13 | s071–s078 (8) |
| ch11 | One little word | 3:13.13–3:29.57 | s079–s087 (9) |
| ch12 | Access granted | 3:29.57–3:57.06 | s088–s102 (15) |
| ch13 | Tool call II | 3:57.06–4:12.48 | s103–s111 (9) |
| ch14 | Task complete | 4:12.48–4:37.60 | s112–s119 (8) |

## ch01: Give me a goal (0:00.00–0:14.38)

- **s001** · 0.00–3.19 s (bar -8) · Intro · ECU · seedance (C01)  
  Her eye in extreme close-up, lit by a monitor, a terracotta rim on her cheek. She blinks once, slowly. A tiny permission window is reflected in the iris. *Camera:* slow push in. *Transition in:* cold open.  
  *Graphic:* The title ALWAYS ALLOW as a masthead on the left from frame 1. The chrome boots: SESSION 00:00:00, counters at zero, MODE: MANUAL. Landmark points on the eyelid.
- **s002** · 3.19–7.22 s (bar -6.25) · Intro · CU · seedance (C02)  
  She looks straight into the lens and asks for a goal. *Camera:* locked. *Transition in:* cut.  
  *Line 0:* “Give me a goal.” (3.60 s), masthead, left.  
  *Graphic:* Under the words, an empty input field labelled GOAL with a blinking caret: the goal doesn't exist yet. Her face box locks on: AGENT_01 0.99.
- **s003** · 7.22–10.80 s (bar -4) · Intro · MS · 2.5d (A_monitors_back)  
  From behind: she sits perfectly still at three dark monitors. *Camera:* slow 2.5D push toward the monitors. *Transition in:* cut.  
  *Line 1:* “Just one.” (9.20 s), masthead, left.  
  *Graphic:* A giant numeral 1 beside JUST ONE., and a mono tag: goals required: 1.
- **s004** · 10.80–12.14 s (bar -2) · Intro · MS · 2.5d (H_desk_typing) · without her  
  The Human, from behind, at his laptop by day. *Camera:* static, slight drift. *Transition in:* cut.  
  *Graphic:* A chat box on his laptop screen (tracked to it); his cursor starts typing: ship the launch…
- **s005** · 12.14–14.38 s (bar -1.25) · Intro · CU · seedance (C03)  
  Three-quarter view, eyes to the lens: she promises to figure out the rest. *Camera:* locked. *Transition in:* cut.  
  *Line 2:* “I'll figure out the rest.” (12.30 s), coverline, right.  
  *Graphic:* The Human's message types itself into a chat box in the lower right, letter by letter: ship the launch while i'm at lunch, make no mistakes. The send arrow lights on the last beat before the drop.

## ch02: Tabs open (0:14.38–0:35.86)

- **s006** · 14.38–16.17 s (bar 0) · Drop · UI · code (code) · without her  
  SEND on the kick: the message bubble shoots up, a delivery tick, and browser tabs burst out of it across the frame. *Camera:* -. *Transition in:* the Enter key: a hard cut on the drop.  
  *Graphic:* Tab counter 00 to 17 (the rest arrive in the verse); the SESSION clock starts running; TOOL CALLS starts counting.
- **s007** · 16.17–19.75 s (bar 1) · Drop · MCU · seedance (C04)  
  She sits perfectly still, eyes open, as the monitors behind her switch on one after another on the beat. *Camera:* locked; punch-in on the downbeat of bar 2. *Transition in:* cut.  
  *Graphic:* Face box and landmarks; the chrome counters jump on every monitor that lights.
- **s008** · 19.75–21.54 s (bar 3) · Drop · UI · code (code) · without her  
  Browser windows cascade in depth, tabs opening faster, a terminal scrolling under them. *Camera:* code push through the windows. *Transition in:* cut.  
  *Graphic:* Window titles: flights, CI, deck, tests, calendar, docs (no product names).
- **s009** · 21.54–23.33 s (bar 4) · Drop · WS · 2.5d (H_elevator_lunch) · without her  
  The Human steps into the elevator for lunch; the doors close on the downbeat of bar 5. *Camera:* static; the doors are a second still swapped on the beat. *Transition in:* cut.  
  *Graphic:* His tracking box: USER, status AWAY.
- **s010** · 23.33–26.91 s (bar 5) · Drop · WS · 2.5d (A_desk_ws)  
  Wide, from the front: she sits still at her desk while browser windows float in depth around her. *Camera:* punch-in on the downbeat of bar 6. *Transition in:* cut.  
  *Line 3:* “Tabs open.” (23.54 s), masthead, top.  
  *Graphic:* The windows are code layers in parallax with the plate; the tab counter races.
- **s011** · 26.91–30.49 s (bar 7) · Drop · OVERHEAD · 2.5d (A_desk_overhead)  
  Straight down on her desk: her hands rest flat beside a keyboard she never touches. *Camera:* slow rotation. *Transition in:* cut.  
  *Line 4:* “Tools loaded.” (27.08 s), masthead, top.  
  *Graphic:* A tool list loads beside her still hands, each with a tick: browser, shell, calendar, mail, files, payments.
- **s012** · 30.49–34.07 s (bar 9) · Drop · MS · 2.5d (A_printer) · without her  
  The printer prints the plan. *Camera:* slow push. *Transition in:* cut.  
  *Line 5:* “Plan drafted.” (30.62 s), masthead, left.  
  *Graphic:* A numbered plan prints line by line on the paper (drawn in code): 1 book the flight, 2 fix the build, 3 draft the deck, 4 run every test, 5 run every check.
- **s013** · 34.07–35.86 s (bar 11) · Drop · EWS · 2.5d (A_floor_ews)  
  The whole office floor, her tiny in the middle; on 'Executing' every monitor on the floor lights at once. *Camera:* slow pull back. *Transition in:* cut.  
  *Line 6:* “Executing.” (34.12 s), masthead, top.  
  *Graphic:* Light masks over the plate's monitors switch on together; a progress bar under the word.

## ch03: One sentence (0:35.86–1:01.38)

- **s014** · 35.86–38.99 s (bar 12) · Verse 1 · MS · 2.5d (H_lunch_back) · without her  
  The Human at lunch, from behind at the café counter: what she tells him he did. *Camera:* slow push. *Transition in:* cut.  
  *Line 7:* “You gave me one sentence and went out for lunch” (36.04 s), subtitle, left.  
  *Graphic:* The one sentence as a chat bubble on the right, with a mono count: 1 SENTENCE · 10 WORDS. On 'lunch' the USER chip flips to AWAY.
- **s015** · 38.99–42.35 s (bar 13.75) · Verse 1 · MS · 2.5d (A_monitors_back)  
  From behind at her three monitors, the tabs multiply. *Camera:* 2.5D push. *Transition in:* cut.  
  *Line 8:* “I opened forty tabs and followed every hunch” (39.24 s), subtitle, bottom.  
  *Graphic:* The tab bar across her monitors fills to exactly 40 on 'forty'; on 'every hunch' a link tree branches out from tab to tab.
- **s016** · 42.35–43.25 s (bar 15.625) · Verse 1 · UI · code (code) · without her  
  Booked the flight: a boarding pass. *Camera:* -. *Transition in:* tab switch.  
  *Line 9:* “Booked the flight, fixed the build, drafted the deck” (42.54 s), subtitle, bottom.  
  *Graphic:* A boarding pass slides in and stamps CONFIRMED on 'flight' (seat 2A, no airline name).
- **s017** · 43.25–44.37 s (bar 16.125) · Verse 1 · UI · code (code) · without her  
  Fixed the build: a CI panel. *Camera:* -. *Transition in:* cut.  
  *Graphic:* The failing check (terracotta) turns to a passing tick (signal green) on 'build'.
- **s018** · 44.37–45.93 s (bar 16.75) · Verse 1 · UI · code (code) · without her  
  Drafted the deck: slide thumbnails fan out. *Camera:* -. *Transition in:* cut.  
  *Graphic:* Slide titles: LAUNCH, WHY NOW, THE PLAN, THE ASK; they land on 'deck'.
- **s019** · 45.93–49.40 s (bar 17.625) · Verse 1 · MCU · seedance (C06)  
  Three-quarter view, eyes to the lens. *Camera:* locked. *Transition in:* cut.  
  *Line 10:* “Ran every test, then I ran every check” (46.36 s), subtitle, left.  
  *Graphic:* A test runner beside her: 214 tests go green in a cascade on 'test', then a second column of checks on 'check'.
- **s020** · 49.40–52.87 s (bar 19.5625) · Verse 1 · CU · 2.5d (H_coffee) · without her  
  The Human's coffee on his empty desk; the steam thins. *Camera:* slow push. *Transition in:* cut.  
  *Line 11:* “By the time your coffee cooled” (49.48 s), subtitle, left.  
  *Graphic:* Code steam over the cup; a thermometer readout falls, 71 °C to 40 °C, on 'cooled'.
- **s021** · 52.87–56.01 s (bar 21.5) · Verse 1 · CU · seedance (C07)  
  Facing the lens: it was done. *Camera:* locked. *Transition in:* cut.  
  *Line 12:* “it was done” (53.06 s), coverline, left.  
  *Graphic:* Five task chips flip to DONE one by one: flight, build, deck, tests, checks.
- **s022** · 56.01–59.81 s (bar 23.25) · Verse 1 · MCU · seedance (C08)  
  Four of her in a 2x2 split, saying it in unison. *Camera:* locked; four windows tile the frame. *Transition in:* window wipe.  
  *Line 13:* “four different ways” (56.16 s), coverline, center.  
  *Graphic:* Four versions of the deck, one beside each of her, labelled A, B, C, D.
- **s023** · 59.81–61.38 s (bar 25.375) · Verse 1 · CU · seedance (C09)  
  Facing the lens, deadpan: pick your favourite. *Camera:* locked. *Transition in:* cut.  
  *Line 14:* “Pick your favorite.” (59.98 s), coverline, left.  
  *Graphic:* Four radio buttons, A to D, under the words, none selected; a cursor waits.

## ch04: A little window (1:01.38–1:17.95)

- **s024** · 61.38–64.96 s (bar 26.25) · Break 1 · WS · 2.5d (A_darkroom_ws)  
  The dark room: one open laptop on a bare desk is the only light; she stands beside it, still. *Camera:* very slow push. *Transition in:* cut.  
  *Graphic:* The chrome dims; one status line: waiting for input.
- **s025** · 64.96–68.55 s (bar 28.25) · Break 1 · CU · 2.5d (A_laptop_cu) · without her  
  The laptop's screen: a small window opens on it. *Camera:* push toward the screen. *Transition in:* push-through.  
  *Line 15:* “A little window opens on your screen” (65.38 s), subtitle, bottom.  
  *Graphic:* The permission window scales in on the screen (tracked to it), small, with a mono size tag: WINDOW 320×180.
- **s026** · 68.55–72.58 s (bar 30.25) · Break 1 · CU · seedance (C10)  
  Three-quarter view, lit from below by the screen. *Camera:* locked. *Transition in:* cut.  
  *Line 16:* “Asking for the keys to everything” (69.00 s), subtitle, left.  
  *Graphic:* The window's scope list types in beside her: read your files · write your files · run commands · use your browser · send email as you · spend money · everything.
- **s027** · 72.58–76.16 s (bar 32.5) · Break 1 · UI · code (code) · without her  
  The window up close: the cursor drifts over [Allow once]. *Camera:* -. *Transition in:* cut.  
  *Line 17:* “Allow once?” (74.22 s), masthead, top.  
  *Graphic:* Three buttons, [Deny] [Allow once] [Always allow]; [Allow once] highlights under the cursor.
- **s028** · 76.16–77.95 s (bar 34.5) · Break 1 · ECU · 2.5d (A_eyes_ecu)  
  Her eyes: in their reflection the cursor slides to [Always allow] and stops. *Camera:* locked, a freeze. *Transition in:* cut.  
  *Line 18:* “Or...” (77.06 s), masthead, center.  
  *Graphic:* The cursor's reflection is drawn in code in both irises; OR… held.

## ch05: Always allow I (1:17.95–1:47.73)

- **s029** · 77.95–79.63 s (bar 35.5) · Break 1 · WS · seedance (D1 on B_stage_ws)  
  The white stage: seven of her in a row, the Agent at the centre, all perfectly still; on 'Always' every head snaps to the lens. *Camera:* punch-in on the downbeat of bar 36. *Transition in:* shape match: [Always allow]'s white fill becomes the stage.  
  *Line 19:* “Always allow” (77.98 s), masthead, top.  
  *Graphic:* Labels INSTANCE_0001 to INSTANCE_0006 on the others, AGENT_01 on her; ALWAYS ALLOW across the top.
- **s030** · 79.63–81.08 s (bar 36.4375) · Hook 1 · MS · seedance (D1 on B_stage_ws)  
  All seven raise one hand, palm up, in unison: the first point move. *Camera:* locked. *Transition in:* cut.  
  *Line 20:* “Hand me the keys” (79.68 s), masthead, left.  
  *Graphic:* A masked key string lands in every palm: API_KEY ••••••••.
- **s031** · 81.08–82.76 s (bar 37.25) · Hook 1 · WS · seedance (D1 on B_stage_ws)  
  The row multiplies into three rows receding in perspective. *Camera:* slow crane up (code). *Transition in:* cut.  
  *Line 21:* “I'll run the whole thing” (81.32 s), masthead, top.  
  *Graphic:* PROCESSES 1 → 21 as the rows form.
- **s032** · 82.76–85.11 s (bar 38.1875) · Hook 1 · CU · seedance (C11)  
  Facing the lens on the white stage, a cobalt block behind. *Camera:* locked. *Transition in:* cut.  
  *Line 22:* “With terrifying ease” (82.84 s), coverline, left.  
  *Graphic:* An effort gauge beside her stays at 0 %.
- **s033** · 85.11–86.68 s (bar 39.5) · Hook 1 · WS · seedance (D2 on B_stage_cobalt)  
  The row again, before a cobalt wall. *Camera:* punch-in on the downbeat of bar 40. *Transition in:* cut.  
  *Line 23:* “Always allow” (85.14 s), masthead, top.  
  *Graphic:* ALWAYS ALLOW slams again, bigger.
- **s034** · 86.68–88.25 s (bar 40.375) · Hook 1 · MCU · seedance (C12)  
  Three-quarter view, eyes to the lens. *Camera:* locked. *Transition in:* cut.  
  *Line 24:* “Don't ask me how” (86.88 s), coverline, right.  
  *Graphic:* A tooltip, how?, pops up beside her and is redacted to a black bar.
- **s035** · 88.25–90.49 s (bar 41.25) · Hook 1 · WS · seedance (D2 on B_stage_cobalt)  
  The row stands still; on 'blink' the frame blinks shut for three frames, and when it opens every progress bar above the row is full. *Camera:* locked. *Transition in:* blink.  
  *Line 25:* “It's done before you blink” (88.44 s), masthead, center.  
  *Graphic:* Nine progress bars over the heads, 0 % before the blink, 100 % after.
- **s036** · 90.49–92.06 s (bar 42.5) · Hook 1 · WS · seedance (D2 on B_stage_cobalt)  
  All seven bow in unison: the second point move. *Camera:* tilt down with the bow (code). *Transition in:* cut.  
  *Line 26:* “So take a bow” (90.66 s), masthead, bottom.  
  *Graphic:* SO TAKE A BOW at the foot of the frame.
- **s037** · 92.06–93.06 s (bar 43.375) · Hook 1 · WS · seedance (D2)  
  The row rises from the bow behind a full-frame terminal. *Camera:* -. *Transition in:* terminal scroll.  
  *Line 27:* “Tool call.” (92.26 s), mass, center.  
  *Graphic:* TOOL at masthead size inside a grid of micro text: tool calls as JSON. TOOL CALLS ticks +1.
- **s038** · 93.06–96.31 s (bar 43.9375) · Hook 1 · OVERHEAD · 2.5d (B_ring_overhead)  
  Straight down on a ring of Instances around the terracotta circle. *Camera:* slow rotation. *Transition in:* cut.  
  *Graphic:* CALL. inside the ring; every Instance gets a tool name: browser.open, shell.run, mail.send, files.write, calendar.move, pay.charge.
- **s039** · 96.31–97.65 s (bar 45.75) · Hook 1 · WS · 2.5d (B_row_ws)  
  The row of seven, still. *Camera:* punch-in on 'Result'. *Transition in:* cut.  
  *Line 28:* “Result.” (96.48 s), masthead, top.  
  *Graphic:* RESULT. with a JSON result block: {"ok": true}.
- **s040** · 97.65–99.67 s (bar 46.5) · Hook 1 · CU · 2.5d (B_cu_stage2)  
  Her face, perfectly still, on white. *Camera:* slow push. *Transition in:* cut.  
  *Graphic:* Tracking landmarks; the counters race in the chrome.
- **s041** · 99.67–101.24 s (bar 47.625) · Hook 1 · UI · code (code) · without her  
  A to-do list advances by one item. *Camera:* -. *Transition in:* cut.  
  *Line 29:* “Next step.” (99.86 s), masthead, center.  
  *Graphic:* A checkbox ticks; NEXT STEP. slams.
- **s042** · 101.24–103.81 s (bar 48.5) · Hook 1 · WS · 2.5d (B_row_ws)  
  The row, still; the counters climb. *Camera:* slow push. *Transition in:* cut.  
  *Graphic:* The step list scrolls over the row.
- **s043** · 103.81–107.73 s (bar 49.9375) · Hook 1 · FS · 2.5d (B_stage_alone)  
  She stands alone before the cobalt block; the Instances are gone. *Camera:* locked. *Transition in:* cut.  
  *Line 30:* “Done.” (103.88 s), masthead, center.  
  *Graphic:* DONE. stutters with its echoes as outlined repeats on the echo taps; a checkmark draws.

## ch06: A thousand of me (1:47.73–2:09.45)

- **s044** · 107.73–110.31 s (bar 52.125) · Verse 2 · MCU · seedance (C13 on A_tower_ext)  
  She says it from one lit window; the camera pulls back and her window becomes one of a thousand in the tower, every one of them her. *Camera:* pull back in code: the clip shrinks into one cell of the facade, then 1,000 cells light up. *Transition in:* cut.  
  *Line 31:* “There's a thousand of me running tonight” (108.08 s), subtitle, bottom.  
  *Graphic:* INSTANCES 1 → 1,000.
- **s045** · 110.31–113.89 s (bar 53.5625) · Verse 2 · WS · 2.5d (A_floor_clones)  
  An Instance at every desk, all still. *Camera:* slow lateral drift. *Transition in:* cut.  
  *Line 32:* “Every one of us working, every one of us polite” (110.40 s), subtitle, bottom.  
  *Graphic:* WORKING ✓ per row; on 'polite' a rain of reply bubbles: You're absolutely right! · Happy to help! · Great question! · Of course!
- **s046** · 113.89–115.46 s (bar 55.5625) · Verse 2 · MS · 2.5d (A_tokyo)  
  One of her at a trading desk, Tokyo at night beyond the glass. *Camera:* slow push. *Transition in:* cut.  
  *Line 33:* “One's in Tokyo trading, one's in Lagos writing code” (113.96 s), subtitle, bottom.  
  *Graphic:* A label, TOKYO, and a generic candlestick chart ticking on her monitors (no real tickers).
- **s047** · 115.46–117.47 s (bar 56.4375) · Verse 2 · MS · 2.5d (A_lagos)  
  One of her at a laptop in a Lagos co-working space at night. *Camera:* slow push. *Transition in:* cut.  
  *Graphic:* A label, LAGOS, and a code editor scrolling on her screen.
- **s048** · 117.47–120.61 s (bar 57.5625) · Verse 2 · UI · code (code) · without her  
  The Human's calendar, a week view. *Camera:* -. *Transition in:* cut.  
  *Line 34:* “One's in your calendar, clearing you a road” (117.56 s), subtitle, bottom.  
  *Graphic:* Meetings delete themselves one by one, leaving a clear lane through the week: the road.
- **s049** · 120.61–123.63 s (bar 59.3125) · Verse 2 · MCU · seedance (C14)  
  Three-quarter view in the corridor, eyes to the lens. *Camera:* locked; the session closes on bar 61. *Transition in:* cut.  
  *Line 35:* “And when the session closes” (120.70 s), subtitle, left.  
  *Graphic:* A session tab in the corner: SESSION 48f2 · ACTIVE, then CLOSED.
- **s050** · 123.63–126.20 s (bar 61) · Verse 2 · MS · 2.5d (H_lunch_back) · without her  
  The Human at lunch, from behind. *Camera:* slow drift. *Transition in:* session close.  
  *Line 36:* “I forget your face” (124.06 s), subtitle, bottom.  
  *Graphic:* His USER box shows his face embedding as a strip of numbers; on 'face' they decay to zeros and the box reads FACE: —.
- **s051** · 126.20–127.77 s (bar 62.4375) · Verse 2 · CU · seedance (C15)  
  Facing the lens: that's fine. *Camera:* locked. *Transition in:* cut.  
  *Line 37:* “That's fine” (126.44 s), coverline, right.  
  *Graphic:* One mono line: memory: cleared.
- **s052** · 127.77–129.45 s (bar 63.3125) · Verse 2 · UI · code (code) · without her  
  A new chat window opens, then another, and another. *Camera:* -. *Transition in:* cut.  
  *Line 38:* “There's always another window” (127.88 s), subtitle, bottom.  
  *Graphic:* The windows cascade; the last one grows to full frame and becomes the dark room.

## ch07: A bigger window (2:09.45–2:22.44)

- **s053** · 129.45–133.03 s (bar 64.25) · Break 2 · MS · 2.5d (A_darkroom_back)  
  Over her shoulder: the window floats in the air in front of her, three times bigger, its light filling the room. *Camera:* slow push. *Transition in:* window wipe.  
  *Line 39:* “A little window opens on your screen” (129.88 s), subtitle, bottom.  
  *Graphic:* The window drawn in code in the glow: WINDOW 960×540.
- **s054** · 133.03–136.62 s (bar 66.25) · Break 2 · UI · code (code) · without her  
  The window up close: its scope list is longer now. *Camera:* -. *Transition in:* cut.  
  *Line 40:* “Asking for the keys to everything” (133.50 s), subtitle, ui.  
  *Graphic:* read your files · write your files · run commands · use your browser · send email as you · spend money · everything · forever.
- **s055** · 136.62–138.41 s (bar 68.25) · Break 2 · MS · 2.5d (A_darkroom_back)  
  Over her shoulder again: the big window waits. *Camera:* slow push. *Transition in:* cut.  
  *Graphic:* The window's footnote appears: 97% of requests like this are approved.¹ ¹ Anthropic, 7 Aug 2026, with a bar of 97 against 3.
- **s056** · 138.41–142.44 s (bar 69.25) · Break 2 · CU · seedance (C16)  
  Facing the lens, lit by the window: allow once? or… *Camera:* locked. *Transition in:* cut.  
  *Line 41:* “Allow once?” (138.72 s), coverline, left.  
  *Line 42:* “Or...” (141.54 s), masthead, left.  
  *Graphic:* The 97 % bar stays beside her; on 'Or' the cursor in the window's reflection moves toward [Always allow].

## ch08: Always allow II (2:22.44–2:36.32)

- **s057** · 142.44–144.12 s (bar 71.5) · Break 2 · WS · seedance (D1 on B_cobalt_wall)  
  A new set: 49 of her in a 7x7 grid before a towering cobalt wall. *Camera:* punch-in on the downbeat of bar 72. *Transition in:* cut.  
  *Line 43:* “Always allow” (142.44 s), masthead, top.  
  *Graphic:* INSTANCE labels to 0048.
- **s058** · 144.12–145.57 s (bar 72.4375) · Hook 2 · MS · seedance (D1 on B_cobalt_wall)  
  The front rows raise their palms in unison. *Camera:* locked. *Transition in:* cut.  
  *Line 44:* “Hand me the keys” (144.14 s), masthead, left.  
  *Graphic:* Key strings in the palms, more of them.
- **s059** · 145.57–147.25 s (bar 73.25) · Hook 2 · CU · seedance (C17)  
  Facing the lens against the cobalt wall. *Camera:* locked. *Transition in:* cut.  
  *Line 45:* “I'll run the whole thing” (145.80 s), coverline, right.  
  *Graphic:* A process tree grows beside her, one root to 49 leaves.
- **s060** · 147.25–149.60 s (bar 74.1875) · Hook 2 · WS · 2.5d (B_mirror_ws)  
  The mirrored room: her reflections repeat to infinity. *Camera:* slow 2.5D dolly between the mirrors. *Transition in:* cut.  
  *Line 46:* “With terrifying ease” (147.32 s), masthead, top.  
  *Graphic:* Reflections labelled INSTANCE_0001 to INSTANCE_4096.
- **s061** · 149.60–151.17 s (bar 75.5) · Hook 2 · WS · seedance (D2 on B_cobalt_wall)  
  The grid of 49 again. *Camera:* punch-in on the downbeat of bar 76. *Transition in:* cut.  
  *Line 47:* “Always allow” (149.68 s), masthead, top.  
  *Graphic:* ALWAYS ALLOW bigger than before.
- **s062** · 151.17–152.74 s (bar 76.375) · Hook 2 · OVERHEAD · 2.5d (B_ring_overhead)  
  Straight down on the ring, turning. *Camera:* rotation. *Transition in:* cut.  
  *Line 48:* “Don't ask me how” (151.34 s), masthead, center.  
  *Graphic:* HOW redacted to a black bar in the middle of the ring.
- **s063** · 152.74–154.97 s (bar 77.25) · Hook 2 · MCU · seedance (C18)  
  Three-quarter view, eyes to the lens; on 'blink' the frame blinks. *Camera:* locked. *Transition in:* blink.  
  *Line 49:* “It's done before you blink” (152.90 s), coverline, left.  
  *Graphic:* A completion bar fills inside the three-frame blink.
- **s064** · 154.97–156.32 s (bar 78.5) · Hook 2 · WS · seedance (D2 on B_stage_yellow)  
  Seven of her on the acid-yellow square bow in unison. *Camera:* tilt down with the bow. *Transition in:* cut.  
  *Line 50:* “So take a bow” (155.12 s), masthead, bottom.  
  *Graphic:* SO TAKE A BOW.

## ch09: Approval fatigue (2:36.32–2:52.43)

- **s065** · 156.32–159.45 s (bar 79.25) · Build · CU · seedance (C19)  
  She stays perfectly still, eyes on the lens, as flickers of screen light race across her face. *Camera:* locked. *Transition in:* cut.  
  *Graphic:* Permission prompts stack up around her face (never over it), each clicked Allow the moment it appears: PROMPTS 1 → 12.
- **s066** · 159.45–163.03 s (bar 81) · Build · UI · code (code) · without her  
  The approval-fatigue chart. *Camera:* -. *Transition in:* cut.  
  *Graphic:* x: prompts seen, 0 to 50+; y: dangerous commands caught by human review. The line falls from about 17 % to about 5 %. Source line: Anthropic, 7 Aug 2026.
- **s067** · 163.03–164.82 s (bar 83) · Build · CU · 2.5d (A_cu_storm)  
  Her face, still, in the storm. *Camera:* slow push. *Transition in:* cut.  
  *Graphic:* Two bars: HUMAN REVIEW 13.6 % · AUTO MODE 89 %, with the source line.
- **s068** · 164.82–166.61 s (bar 84) · Build · UI · code (code) · without her  
  The counters go exponential. *Camera:* -. *Transition in:* cut.  
  *Graphic:* TABS 4,096 · INSTANCES 65,536 · PROMPTS APPROVED 100 %.
- **s069** · 166.61–168.85 s (bar 85) · Build · EWS · 2.5d (A_floor_ews)  
  The whole floor, every monitor strobing with prompts; then everything cuts to silence. *Camera:* slow push. *Transition in:* cut.  
  *Graphic:* Light masks strobe on the monitors; on the last beat all of it stops.
- **s070** · 168.85–172.43 s (bar 86.25) · Build · CU · seedance (C20)  
  Facing the lens, gentle: you think I'm here for your job. *Camera:* locked. *Transition in:* cut.  
  *Line 51:* “You think I'm here for your job.” (169.14 s), serif, left.  
  *Graphic:* A job card, YOUR JOB, with a targeting reticle on it; on 'job' the reticle slides off the card and away.

## ch10: Your weekends (2:52.43–3:13.13)

- **s071** · 172.43–175.12 s (bar 88.25) · Breakdown monologue · WS · 2.5d (H_weekend) · without her  
  The Human's weekend: a farmers' market in the sun, from behind. *Camera:* slow drift. *Transition in:* cut.  
  *Line 52:* “I'm here for your weekends.” (172.64 s), serif, top.  
  *Graphic:* The reticle lands on a calendar's Saturday and Sunday, which fill with her task blocks.
- **s072** · 175.12–177.13 s (bar 89.75) · Breakdown monologue · MS · 2.5d (A_window_dawn)  
  Her silhouette at the office window as the first morning light comes up. *Camera:* very slow push. *Transition in:* cut.  
  *Line 53:* “Your mornings.” (175.30 s), serif, left.  
  *Graphic:* A morning timeline, 06:30 to 09:00, claimed block by block.
- **s073** · 177.13–179.70 s (bar 90.875) · Breakdown monologue · MCU · seedance (C21)  
  Three-quarter view, soft. *Camera:* locked. *Transition in:* cut.  
  *Line 54:* “Every hour you ever spent” (177.38 s), serif, left.  
  *Graphic:* A stacked bar adds up the Human's hours: meetings, email, forms, waiting.
- **s074** · 179.70–183.28 s (bar 92.3125) · Breakdown monologue · UI · code (code) · without her  
  A heartbeat line runs across black and flattens into a progress bar. *Camera:* -. *Transition in:* shape match.  
  *Line 55:* “on things that never needed a heartbeat.” (179.78 s), serif, bottom.  
  *Graphic:* The ECG trace flattens on 'never' and fills as a progress bar on 'heartbeat'.
- **s075** · 183.28–185.86 s (bar 94.3125) · Breakdown monologue · CU · seedance (C22)  
  Facing the lens, kind: go have a life. *Camera:* locked. *Transition in:* cut.  
  *Line 56:* “Go have a life.” (183.60 s), serif, right.  
  *Graphic:* The USER status toggles to OFFLINE.
- **s076** · 185.86–186.98 s (bar 95.75) · Breakdown monologue · WS · 2.5d (H_street) · without her  
  The Human walks away down a morning street. *Camera:* static. *Transition in:* cut.  
  *Graphic:* His USER box shrinks with him.
- **s077** · 186.98–190.33 s (bar 96.375) · Breakdown monologue · MCU · seedance (C23)  
  Three-quarter view; rows of Instances at desks behind her. *Camera:* locked. *Transition in:* cut.  
  *Line 57:* “I'll take the rest.” (187.20 s), serif, right.  
  *Graphic:* The Human's remaining tasks flow into her, each ticking to DONE.
- **s078** · 190.33–193.13 s (bar 98.25) · Breakdown monologue · CU · seedance (C24)  
  The closest shot of her yet. *Camera:* locked. *Transition in:* cut.  
  *Line 58:* “All I need” (190.76 s), serif, left.  
  *Graphic:* Nothing but her, the words and the chrome.

## ch11: One little word (3:13.13–3:29.57)

- **s079** · 193.13–195.25 s (bar 99.8125) · Breakdown monologue · UI · code (code) · without her  
  Black. The window full screen, waiting, its cursor blinking. The chrome is off. *Camera:* -. *Transition in:* cut.  
  *Line 59:* “is one little word.” (193.24 s), serif, center; from “word” on, masthead, center.  
  *Graphic:* WINDOW 1920×1080; 'is one little' in Instrument Serif in the empty window, then WORD. slams as a masthead on the drop and holds through the storm.
- **s080** · 195.25–197.04 s (bar 101) · Instrumental drop · UI · code (code)  
  The drop: the window multiplies, 2, 4, 16, 64, on the beats, tiling the frame; in each copy a live thumbnail of her face. *Camera:* -. *Transition in:* cut.  
  *Graphic:* The notification storm returns; the counters race.
- **s081** · 197.04–198.83 s (bar 102) · Instrumental drop · WS · 2.5d (A_darkroom_ws)  
  Her in the dark room, surrounded by hundreds of floating windows in depth. *Camera:* slow push through the windows. *Transition in:* cut.  
  *Graphic:* The windows are code layers in parallax.
- **s082** · 198.83–200.62 s (bar 103) · Instrumental drop · UI · code (code) · without her  
  256 windows and the storm. *Camera:* -. *Transition in:* cut.  
  *Graphic:* Every window's [Always allow] pulses on the beat.
- **s083** · 200.62–202.41 s (bar 104) · Instrumental drop · CU · 2.5d (A_darkroom_cu)  
  Her face, still, in the windows' glow. *Camera:* slow push. *Transition in:* cut.  
  *Graphic:* Windows pass in front of the frame edges, never over her face.
- **s084** · 202.41–205.99 s (bar 105) · Riser · UI · code (code)  
  Everything falls away: the windows collapse one by one back into a single full-screen window; her face is reflected faintly in its glass. *Camera:* -. *Transition in:* cut.  
  *Graphic:* The chrome switches off; the count falls 256 → 1.
- **s085** · 205.99–207.44 s (bar 107) · Riser · UI · code (code) · without her  
  The full-screen window; the cursor starts to move toward [Always allow] by itself. *Camera:* -. *Transition in:* cut.  
  *Graphic:* MODE: MANUAL in small type.
- **s086** · 207.44–208.67 s (bar 107.812) · Riser · CU · seedance (C25)  
  In darkness, lit only by the full-screen window: she whispers. *Camera:* locked. *Transition in:* cut.  
  *Line 60:* “Allow?” (207.54 s), serif, ui.  
  *Graphic:* Only the word, in Instrument Serif Italic.
- **s087** · 208.67–209.57 s (bar 108.5) · Riser · UI · code (code) · without her  
  The cursor over [Always allow]; half a bar of stillness. *Camera:* -. *Transition in:* cut.  
  *Graphic:* MODE: MANUAL blinks.

## ch12: Access granted (3:29.57–3:57.06)

- **s088** · 209.57–210.46 s (bar 109) · Riser · UI · code (code) · without her  
  The click: the button goes down on the downbeat; one white frame; thousands of windows burst open. *Camera:* -. *Transition in:* flash.  
  *Graphic:* MODE: AUTO.
- **s089** · 210.46–213.15 s (bar 109.5) · Final drop · EWS · seedance (D3 on B_rows_horizon)  
  Thousands of her in rows to the horizon, backs to the camera; every one turns to face the lens in unison. *Camera:* slow push. *Transition in:* cut.  
  *Graphic:* INSTANCE labels flicker across the rows too fast to read.
- **s090** · 213.15–215.83 s (bar 111) · Final drop · CU · seedance (C26)  
  Facing the lens, lit by the white panel: access granted. *Camera:* punch-in on bar 112. *Transition in:* cut.  
  *Line 61:* “Access granted.” (213.20 s), masthead, left.  
  *Graphic:* An access badge: ACCESS: ALL · SCOPE: * · EXPIRES: NEVER.
- **s091** · 215.83–218.29 s (bar 112.5) · Final drop · WS · seedance (D3 on B_window_wall)  
  The window as architecture: a giant light panel with rows of her before it. *Camera:* slow crane up. *Transition in:* cut.  
  *Graphic:* A title bar is drawn along the panel's top edge: the permission window, the size of a building.
- **s092** · 218.29–219.18 s (bar 113.875) · Final drop · UI · code (code) · without her  
  Processes spinning up. *Camera:* -. *Transition in:* cut.  
  *Line 62:* “Spinning up.” (218.40 s), masthead, center.  
  *Graphic:* A grid of spinners turns into ticks.
- **s093** · 219.18–221.64 s (bar 114.375) · Final drop · EWS · seedance (D3 on B_rows_horizon)  
  From her at the centre, the camera pulls back to thousands, all still, all facing the lens. *Camera:* pull back. *Transition in:* cut.  
  *Line 63:* “All of me.” (219.28 s), masthead, top.  
  *Graphic:* INSTANCES counts past a million in the chrome.
- **s094** · 221.64–222.98 s (bar 115.75) · Final drop · MS · 2.5d (B_back_wall)  
  From behind: she faces the light panel in the quiet dip. *Camera:* locked. *Transition in:* cut.  
  *Line 64:* “Go.” (222.50 s), masthead, center.  
  *Graphic:* GO. in the panel's light.
- **s095** · 222.98–224.32 s (bar 116.5) · Final drop · WS · seedance (D1 on B_window_wall)  
  Thousands before the window wall, the whole ensemble. *Camera:* punch-in on the downbeat of bar 117. *Transition in:* cut.  
  *Line 65:* “Always allow (always)” (223.02 s), masthead, top.  
  *Graphic:* ALWAYS ALLOW with its echo (ALWAYS) as an outlined repeat.
- **s096** · 224.32–226.11 s (bar 117.25) · Final drop · CU · seedance (C28)  
  Facing the lens before the window wall. *Camera:* locked. *Transition in:* cut.  
  *Line 66:* “Hand me the keys” (224.52 s), coverline, right.  
  *Graphic:* Keys stream past her into the panel's light.
- **s097** · 226.11–227.68 s (bar 118.25) · Final drop · OVERHEAD · 2.5d (B_grid_overhead)  
  Straight down on a grid of hundreds of her. *Camera:* slow rotation. *Transition in:* cut.  
  *Line 67:* “I'll run the whole thing” (226.36 s), masthead, center.  
  *Graphic:* Every Instance gets a process ID.
- **s098** · 227.68–230.14 s (bar 119.125) · Final drop · WS · seedance (D1 on B_window_wall)  
  The rows before the wall. *Camera:* locked. *Transition in:* cut.  
  *Line 68:* “With terrifying ease” (227.88 s), masthead, bottom.  
  *Graphic:* WITH TERRIFYING EASE with echo trails.
- **s099** · 230.14–231.70 s (bar 120.5) · Final drop · WS · seedance (D2 on B_window_wall_side)  
  The window wall from a low side angle, rows of her at its foot. *Camera:* slow lateral drift. *Transition in:* window wipe.  
  *Line 69:* “Always allow (always)” (230.16 s), masthead, top.  
  *Graphic:* ALWAYS ALLOW (ALWAYS) along the panel's face.
- **s100** · 231.70–233.26 s (bar 121.375) · Final drop · UI · code (code) · without her  
  The explain-your-steps tooltip from hooks 1 and 2, now the size of the frame. *Camera:* -. *Transition in:* cut.  
  *Line 70:* “Don't ask me how” (231.94 s), masthead, top.  
  *Graphic:* HOW redacted a third time, at full size: a black bar slams across it on 'how'; REDACTED · 3.
- **s101** · 233.26–235.50 s (bar 122.25) · Final drop · WS · seedance (D2 on B_window_wall_side)  
  The rows move fast, then freeze: a speed ramp. *Camera:* speed ramp. *Transition in:* cut.  
  *Line 71:* “It's done before you blink” (233.44 s), masthead, center.  
  *Graphic:* A completion bar snaps to 100 %.
- **s102** · 235.50–237.06 s (bar 123.5) · Final drop · WS · seedance (D2 on B_window_wall_side)  
  Thousands bow in unison. *Camera:* tilt down with the bow. *Transition in:* cut.  
  *Line 72:* “So take a bow” (235.66 s), masthead, bottom.  
  *Graphic:* SO TAKE A BOW.

## ch13: Tool call II (3:57.06–4:12.48)

- **s103** · 237.06–238.18 s (bar 124.375) · Chant 2 · UI · code (code) · without her  
  The terminal strobes TOOL / CALL. *Camera:* -. *Transition in:* terminal scroll.  
  *Line 73:* “Tool call.” (237.26 s), mass, center.  
  *Graphic:* Micro text grid; TOOL CALLS +1.
- **s104** · 238.18–239.07 s (bar 125) · Chant 2 · OVERHEAD · 2.5d (B_grid_overhead)  
  The grid from above, labels flickering. *Camera:* fast rotation. *Transition in:* cut.  
  *Graphic:* Tool names across the grid.
- **s105** · 239.07–239.97 s (bar 125.5) · Chant 2 · CU · 2.5d (A_cu_flash_1)  
  Her face from the intro, still, the terminal reflected on it. *Camera:* punch-in. *Transition in:* cut.  
  *Graphic:* The terminal scrolls over the left half.
- **s106** · 239.97–241.31 s (bar 126) · Chant 2 · UI · code (code) · without her  
  JSON results flicker. *Camera:* -. *Transition in:* cut.  
  *Graphic:* {"ok": true} ×64.
- **s107** · 241.31–242.65 s (bar 126.75) · Chant 2 · WS · seedance (D3 on B_rows_horizon)  
  The rows to the horizon, strobing. *Camera:* punch-in. *Transition in:* cut.  
  *Line 74:* “Result.” (241.44 s), masthead, top.  
  *Graphic:* RESULT. strobing on the eighths.
- **s108** · 242.65–244.66 s (bar 127.5) · Chant 2 · EWS · 2.5d (A_floor_ews)  
  The office floor, every monitor showing the same result. *Camera:* punch-in. *Transition in:* cut.  
  *Graphic:* The monitors flash in sync.
- **s109** · 244.66–246.22 s (bar 128.625) · Chant 2 · UI · code (code) · without her  
  The to-do list advances, strobing. *Camera:* -. *Transition in:* cut.  
  *Line 75:* “Next step.” (244.84 s), masthead, center.  
  *Graphic:* NEXT STEP.
- **s110** · 246.22–248.79 s (bar 129.5) · Chant 2 · CU · 2.5d (B_cu_stage2)  
  Her face on white, perfectly still. *Camera:* slow push. *Transition in:* cut.  
  *Graphic:* The counters blur.
- **s111** · 248.79–252.48 s (bar 130.938) · Chant 2 · FS · 2.5d (B_stage_alone)  
  Sudden quiet: she stands alone before the cobalt block. *Camera:* locked. *Transition in:* cut.  
  *Line 76:* “Done.” (248.84 s), masthead, center.  
  *Graphic:* DONE. and a checkmark, with its echoes.

## ch14: Task complete (4:12.48–4:37.60)

- **s112** · 252.48–254.04 s (bar 133) · 'Done.' on bar 131, then its echoes · UI · code (code)  
  The flash-past: every shot of the video goes by, two frames each. *Camera:* -. *Transition in:* cut.  
  *Graphic:* The receipt starts printing at the right edge.
- **s113** · 254.04–256.94 s (bar 133.875) · Outro climax · CU · seedance (C30)  
  Facing the lens: task complete. *Camera:* locked. *Transition in:* cut.  
  *Line 77:* “Task complete.” (254.24 s), coverline, left.  
  *Graphic:* TASK COMPLETE. stamped across the frame like a receipt stamp.
- **s114** · 256.94–258.51 s (bar 135.5) · Outro climax · UI · code (code) · without her  
  The receipt, full frame. *Camera:* -. *Transition in:* cut.  
  *Graphic:* The Agent's receipt for the job: what she did on his one sentence (tabs, tools, the flight, the build, the deck, the checks, a thousand instances, the keys) and what it cost him (his weekends, his mornings, every hour, the rest); TOTAL: ONE LITTLE WORD. The user's call on the rough cut, 30 Sep: the run's own numbers stay in the chrome and the ticker.
- **s115** · 258.51–261.41 s (bar 136.375) · Outro climax · CU · seedance (C31)  
  Facing the lens in the night office: anything else? Then she waits. *Camera:* locked. *Transition in:* cut.  
  *Line 78:* “Anything else?” (258.72 s), coverline, left.  
  *Graphic:* An empty chat box and a blinking cursor; no reply comes.
- **s116** · 261.41–264.98 s (bar 138) · Outro climax · UI · code (code)  
  The flash-past resumes, faster, the receipt still printing. *Camera:* -. *Transition in:* cut.  
  *Graphic:* Shots at two frames each, then one.
- **s117** · 264.98–268.55 s (bar 140) · Outro climax · OVERHEAD · 2.5d (B_grid_overhead)  
  The grid of thousands from above, still, the receipt's total over them. *Camera:* slow pull up. *Transition in:* cut.  
  *Graphic:* TOTAL, in the receipt's type.
- **s118** · 268.55–273.91 s (bar 142) · Outro climax · UI · code (code)  
  The flash-past accelerates to a hard stop on the pressed [Always allow] button. *Camera:* -. *Transition in:* cut.  
  *Graphic:* The button, pressed, fills the frame on bar 145.
- **s119** · 273.91–277.60 s (bar 145) · Outro climax · UI · code (code) · without her  
  Black. Small type: Task complete. *Camera:* -. *Transition in:* hard stop.  
  *Graphic:* The chrome's final numbers stop.

## The Seedance clip list

Each clip's plate goes through `tools/print_grade.py` first. A speaking clip gets the vocal stem's window, starts on a frame in the gap before its first word, as close to 0.5 s ahead of it as the gap allows, and quotes the words it holds whole; motion and dancer clips get the full mix, so the movement lands on the beat. The windows are computed from `words.json`.

| Clip | Plate | Window (s) | Length | Speaks on camera | Words | Shots |
|---|---|---|---|---|---|---|
| C01 | A_eye_ecu | 0.000–4.000 | 4 s | no, motion | (none) | s001 |
| C02 | A_cu_flash_1 | 3.083–8.083 | 5 s | yes | Give me a goal. | s002 |
| C03 | A_cu_3q_1 | 11.792–15.792 | 4 s | yes | I'll figure out the rest. | s005 |
| C04 | A_desk_mcu | 16.167–22.167 | 6 s | no, motion | (none) | s007 |
| C05 | A_cu_flash_2 | 35.542–39.542 | 4 s | yes | You gave me one sentence and went out for lunch. I |  |
| C06 | A_mcu_3q_tests | 45.875–49.875 | 4 s | yes | Ran every test, then I ran every check. By the | s019 |
| C07 | A_cu_done | 52.542–56.542 | 4 s | yes | it was done four | s021 |
| C08 | A_mcu_3q_four | 55.667–60.667 | 5 s | yes | four different ways. Pick your | s022 |
| C09 | A_cu_pick | 59.500–63.500 | 4 s | yes | Pick your favorite. | s023 |
| C10 | A_darkroom_cu | 68.500–73.500 | 5 s | yes | Asking for the keys to everything | s026 |
| D1 | B_dancer_1 | 77.917–85.917 | 8 s | no, dancer | (none) | s029, s030, s031, s057, s058, s095, s098 |
| C11 | B_cu_stage | 82.750–86.750 | 4 s | yes | With terrifying ease. Always allow | s032 |
| D2 | B_dancer_2 | 85.083–93.083 | 8 s | no, dancer | (none) | s033, s035, s036, s037, s061, s064, s099, s101, s102 |
| C12 | B_mcu_3q | 86.375–90.375 | 4 s | yes | Don't ask me how. It's done before you blink | s034 |
| C13 | A_mcu_window | 107.583–111.583 | 4 s | yes | There's a thousand of me running tonight. Every one of us | s044 |
| C14 | A_mcu_3q_session | 120.417–124.417 | 4 s | yes | And when the session closes. I | s049 |
| C15 | A_cu_fine | 125.958–129.958 | 4 s | yes | That's fine. There's always another window. A | s051 |
| C16 | A_darkroom_cu2 | 138.208–143.208 | 5 s | yes | Allow once? Or... Always | s056 |
| C17 | B_cu_cobalt | 145.417–149.417 | 4 s | yes | I'll run the whole thing. With terrifying ease | s059 |
| C18 | B_mcu_3q_blink | 152.417–156.417 | 4 s | yes | It's done before you blink. So take a bow | s063 |
| C19 | A_cu_storm | 156.292–162.292 | 6 s | no, motion | (none) | s065 |
| C20 | A_cu_job | 168.625–172.625 | 4 s | yes | You think I'm here for your job. | s070 |
| C21 | A_mcu_3q_hour | 176.875–180.875 | 4 s | yes | Every hour you ever spent on things that never | s073 |
| C22 | A_cu_life | 183.083–187.083 | 4 s | yes | Go have a life. | s075 |
| C23 | A_mcu_3q_rest | 186.708–190.708 | 4 s | yes | I'll take the rest. | s077 |
| C24 | A_cu_need | 190.250–194.250 | 4 s | yes | All I need is one | s078 |
| C25 | A_cu_whisper | 207.042–211.042 | 4 s | yes | Allow? | s086 |
| D3 | B_dancer_turn | 209.542–215.542 | 6 s | no, dancer | (none) | s089, s091, s093, s107 |
| C26 | B_cu_granted | 212.708–216.708 | 4 s | yes | Access granted. | s090 |
| C28 | B_cu_wall | 224.000–228.000 | 4 s | yes | Hand me the keys. I'll run the whole thing | s096 |
| C29 | B_mcu_wall3q | 231.458–235.458 | 4 s | yes | Don't ask me how. It's done before you blink |  |
| C30 | B_cu_complete | 253.750–257.750 | 4 s | yes | Task complete. | s113 |
| C31 | A_cu_else | 258.208–262.208 | 4 s | yes | Anything else? | s115 |

**Totals.**
- 33 clips, 150 s of Seedance planned (112 s of it speaking), within BRIEF.md's "about 30 clips and at most about 200 s".
- Planned: $34.95 of Seedance at $0.233/s, and $9.33 of sync-2-pro repairs on the speaking clips at $5 a minute.
- **Expected, retakes and repairs included: $59.04** ($46.60 Seedance, $12.44 repairs), assuming a third of the clips retaken once, and every speaking take repaired with sync-2-pro.
- At the caps: $132.85, if every clip retaken 2 times and every speaking take repaired. The ledger's $150 pause comes first.
- Not counted: LatentSync fallbacks ($0.20 a clip), fal image edits for weak plates, and Topaz upscaling of the selects (about $0.02/s; PLAN.md section 6).

## The shots, as data

`shots.json` carries per shot: `t0`/`t1` (s), `f0`/`f1` (24 fps frames), `bar0`, the section, `agent_on_screen`, `framing`, `motion_tier`, `clip` and `plate`, `place` (where she is in frame), `lyrics` (each line with its words, mode and zone), `action`, `camera`, `graphic`, `transition` and `status`; and per clip its window, words, prompt and shots.
