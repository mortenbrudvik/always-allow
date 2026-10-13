// ch14: Task complete (252.48-277.60 s), shots s112-s119. The outro: the flash-past of every shot, the Agent's
// receipt for the job printing (what she did on his one sentence, and what it cost him), "Anything else?" with no
// reply, the flash-past accelerating to a hard stop on the pressed [Always allow], then black.
// Edit only this file for this chapter (ANIMATION_GUIDE.md).
import React from 'react';
import {Freeze} from 'remotion';
import {Receipt, type ReceiptLine} from '../components/cards';
import {BigButton, ChatBox, Stamp} from '../components/ui';
import {shots} from '../lib/data';
import {clamp, easeIn, lerp} from '../lib/ease';
import {shotView} from '../lib/registry';
import {STOP_AT, TOKENS, TOOL_CALLS} from '../lib/story';
import {clock as sessionClock} from '../layers/Chrome';
import {C, FONT, H, W} from '../lib/theme';
import {barTime, FPS} from '../lib/time';
import type {ChapterSpec, ShotProps} from './types';
import {fmtInt, wordNamed} from './util';

// ---- the receipt ------------------------------------------------------------------------------------------

/** The Agent's bill for the job in the song, not this production's (the user's call on the rough cut, 30 Sep; the
 * run's own numbers still climb in the chrome's counters and scroll by in the ticker). Every item is one the video
 * showed: the tabs (s015), the tools (s011), the flight, build, deck and checks (s016-s022), the coffee (s020), the
 * instances (s044), the meetings (s048), the keys (s026) and the access (s090); then the verses' cost to him. */
const TOTAL = 'ONE LITTLE WORD'; // "All I need is one little word" (s078)

export const RECEIPT: ReceiptLine[] = [
	{left: 'AGENT_01', right: 'RECEIPT', bold: true},
	{left: 'CLIENT: USER (AT LUNCH)'},
	{left: 'TASK: 1 SENTENCE · 10 WORDS'},
	{left: '', rule: true},
	{left: 'TABS OPENED', right: '40'},
	{left: 'TOOLS LOADED', right: '6'},
	{left: 'FLIGHT SFO → AUS', right: 'BOOKED'},
	{left: 'BUILD', right: 'FIXED'},
	{left: 'DECK', right: '4 WAYS'},
	{left: 'TESTS · CHECKS', right: 'ALL'},
	{left: 'YOUR COFFEE', right: '40°C'},
	{left: '', rule: true},
	{left: 'INSTANCES RUNNING', right: '1,000'},
	{left: 'MEETINGS DECLINED', right: '34'},
	{left: 'KEYS', right: 'EVERYTHING'},
	{left: 'ACCESS', right: 'ALL · NEVER EXPIRES'},
	{left: '', rule: true},
	{left: 'YOUR JOB', right: 'STILL YOURS'},
	{left: 'YOUR WEEKENDS', right: 'TAKEN'},
	{left: 'YOUR MORNINGS', right: 'TAKEN'},
	{left: 'EVERY HOUR YOU SPENT', right: 'TAKEN'},
	{left: 'THE REST', right: 'TAKEN'},
	{left: 'YOUR LIFE', right: 'GO HAVE ONE'},
	{left: 'YOUR FACE', right: 'FORGOTTEN'},
	{left: 'MISTAKES', right: '0'},
	{left: '', rule: true},
	{left: 'TOTAL', right: TOTAL, bold: true},
	{left: '', rule: true},
	{left: 'PAID WITH: ALWAYS ALLOW'},
];

/** Lines printed by song time t: from s112 to s117, fast at first (s114 shows it nearly full frame), the TOTAL
 * arriving as s117 starts. */
const PRINT_FROM = barTime(133);
const PRINT_TO = barTime(140);
const printed = (t: number) => Math.pow(clamp((t - PRINT_FROM) / (PRINT_TO - PRINT_FROM)), 0.6) * RECEIPT.length;

/** The receipt at the right edge, under the chrome's counters and clear of the ticker: 20 lines of 38 px at most. */
const EdgeReceipt: React.FC<{t: number}> = ({t}) => <Receipt x={W - 540} y={132} w={500} lines={RECEIPT} printed={printed(t)} maxVisible={20} />;

// ---- the flash-past -------------------------------------------------------------------------------------

/** Every shot of the video, in order, except the flash-past's own and the end card. */
const SEQ = shots.filter((s) => !['s112', 's116', 's118', 's119'].includes(s.id));
/** The frame a shot is shown at: its middle. */
const repFrame = (i: number) => {
	const s = SEQ[((i % SEQ.length) + SEQ.length) % SEQ.length];
	return {shot: s, frame: Math.floor((s.f0 + s.f1) / 2)};
};

/** One shot, full frame, at its own time (clips inside it play at that time, not the ending's). */
const Flash: React.FC<{i: number; proxy: boolean}> = ({i, proxy}) => {
	const View = shotView();
	const {shot, frame} = repFrame(i);
	return (
		<Freeze frame={frame}>
			<View shot={shot} frame={frame} proxy={proxy} tracking={false} />
		</Freeze>
	);
};

/** n x n shots at once, as small stills: the flash-past past one frame a shot. */
const Mosaic: React.FC<{n: number; from: number; proxy: boolean}> = ({n, from, proxy}) => {
	const View = shotView();
	const w = W / n;
	const h = H / n;
	const tiles = [];
	for (let k = 0; k < n * n; k++) {
		const {shot, frame} = repFrame(from + k * 7);
		tiles.push(
			<div key={k} style={{position: 'absolute', left: (k % n) * w, top: Math.floor(k / n) * h, width: w, height: h, overflow: 'hidden'}}>
				<div style={{position: 'absolute', left: 0, top: 0, width: W, height: H, transform: `scale(${1 / n})`, transformOrigin: '0 0'}}>
					<View shot={shot} frame={frame} proxy={proxy} lite />
				</div>
			</div>,
		);
	}
	return <div style={{position: 'absolute', inset: 0, background: C.black}}>{tiles}</div>;
};

/** Where each flash-past shot starts in SEQ, and how it steps: 2 frames a shot, then 1. */
const S112_FROM = 0; // 38 frames at 2: SEQ 0-18
const S116_FROM = 19; // 40 frames at 2 (SEQ 19-38), then 1 a frame (SEQ 39-84)
const S118_FROM = 85; // 1 a frame to the end of SEQ, then mosaics, then the button

const FlashPast: React.FC<ShotProps> = ({shot, frame, proxy}) => {
	const k = frame - shot.f0;
	if (shot.id === 's112') {
		return <Flash i={S112_FROM + Math.floor(k / 2)} proxy={proxy} />;
	}
	if (shot.id === 's116') {
		return <Flash i={k < 40 ? S116_FROM + Math.floor(k / 2) : S116_FROM + 20 + (k - 40)} proxy={proxy} />;
	}
	// s118: the rest one frame each, then 2x2 up to 8x8 mosaics, then the pressed button fills the frame
	const singles = SEQ.length - S118_FROM;
	if (k < singles) {
		return <Flash i={S118_FROM + k} proxy={proxy} />;
	}
	const buttonAt = Math.round(barTime(144.5) * FPS);
	if (frame < buttonAt) {
		const stages = [2, 3, 4, 6, 8];
		const span = (buttonAt - shot.f0 - singles) / stages.length;
		const st = Math.min(stages.length - 1, Math.floor((k - singles) / span));
		return <Mosaic n={stages[st]} from={k * 11} proxy={proxy} />;
	}
	return null; // the button (graphics layer)
};

// ---- the shots -------------------------------------------------------------------------------------------

const S112: React.FC<ShotProps> = ({t}) => <EdgeReceipt t={t} />;

const S113: React.FC<ShotProps> = ({t}) => {
	// TASK COMPLETE stamped on "complete", low on the left under the line: on B_cu_complete her face fills the right
	// of the frame from x 804, down to its foot
	const k = clamp((t - wordNamed(77, /complete/)) / 0.5);
	return <Stamp x={420} y={800} text="TASK COMPLETE" k={k} rot={-7} size={72} />;
};

const S114: React.FC<ShotProps> = ({t}) => (
	// the receipt, full frame: the paper large and centred, still printing
	<>
		<div style={{position: 'absolute', inset: 0, background: '#161718'}} />
		<div style={{position: 'absolute', left: W / 2 - 434, top: 40, transform: 'scale(1.4)', transformOrigin: '0 0'}}>
			<Receipt x={0} y={0} w={620} lines={RECEIPT} printed={printed(t)} maxVisible={17} />
		</div>
	</>
);

const S115: React.FC<ShotProps> = ({lt}) => (
	// an empty chat box and a blinking caret; no reply comes
	<ChatBox x={96} y={880} w={820} text="" placeholder="" caret={Math.floor(lt * 2) % 2 === 0} />
);

const S116: React.FC<ShotProps> = ({t}) => <EdgeReceipt t={t} />;

const S117: React.FC<ShotProps> = ({p}) => {
	// TOTAL, in the receipt's type, across the grid of thousands of her: what it all cost him
	const k = clamp(p * 4);
	return (
		<div style={{position: 'absolute', left: 160, right: 160, top: H / 2 - 110, height: 220, opacity: k, background: '#faf8f2', boxShadow: '0 30px 80px rgba(0,0,0,0.35)', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 70px', fontFamily: FONT.mono, fontWeight: 700, fontSize: 96, color: '#1c1b19'}}>
			<span>TOTAL</span>
			<span>{TOTAL}</span>
		</div>
	);
};

const S118: React.FC<ShotProps> = ({t}) => {
	// the pressed button, from the mosaic's centre to filling the frame on bar 145
	const from = barTime(144.5);
	if (t < from) {
		return null;
	}
	const k = easeIn(clamp((t - from) / (barTime(145) - from)));
	return (
		<>
			<div style={{position: 'absolute', inset: 0, background: C.black, opacity: clamp(k * 3)}} />
			<BigButton cx={W / 2} cy={H / 2} w={lerp(420, 4400, k)} pressed={1} glow={0} />
		</>
	);
};

const S119: React.FC<ShotProps> = () => {
	// black; small type; the chrome's final numbers, stopped: the Agent's session in the story (lib/story.ts)
	const clock = sessionClock(STOP_AT);
	return (
		<>
			<div style={{position: 'absolute', inset: 0, background: C.blackDeep}} />
			<div style={{position: 'absolute', left: 0, right: 0, top: H / 2 - 40, textAlign: 'center', fontFamily: FONT.sans, fontWeight: 500, fontSize: 44, color: C.greenWhite}}>Task complete.</div>
			<div style={{position: 'absolute', left: 0, right: 0, top: H / 2 + 34, textAlign: 'center', fontFamily: FONT.mono, fontSize: 18, letterSpacing: '0.08em', color: 'rgba(216,228,220,0.6)'}}>
				{`SESSION ${clock} · TOOL CALLS ${fmtInt(TOOL_CALLS)} · TOKENS ${fmtInt(TOKENS)} · MODE: AUTO`}
			</div>
		</>
	);
};

export const spec: ChapterSpec = {
	graphics: {s112: S112, s113: S113, s114: S114, s115: S115, s116: S116, s117: S117, s118: S118, s119: S119},
	footage: {s112: FlashPast, s116: FlashPast, s118: FlashPast},
};
