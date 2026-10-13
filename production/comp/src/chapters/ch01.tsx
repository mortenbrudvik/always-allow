// ch01: Give me a goal (0.00-14.38 s), shots s001-s005. The intro, pads only: the title and her eye from frame 1,
// she asks for a goal, the Human types one sentence, and the drop lands on its Enter key.
// Edit only this file for this chapter (ANIMATION_GUIDE.md).
import React from 'react';
import {Tag} from '../components/ui';
import {ChatBox} from '../components/ui';
import {defaultCam} from '../lib/camera';
import {clamp} from '../lib/ease';
import {clipFile, hasFootage} from '../lib/media';
import {onScreen} from '../lib/tracking';
import {C, FONT, H, W} from '../lib/theme';
import {barTime} from '../lib/time';
import type {ChapterSpec, ShotProps} from './types';
import {inAt, quad, typed, wordAt} from './util';

/** The Human's one sentence. "make no mistakes" is the 2026 prompt suffix (STYLE_BIBLE.md sources). */
export const SENTENCE = "ship the launch while i'm at lunch, make no mistakes";
export const TYPE_FROM = 11.0; // he starts typing in s004
export const TYPE_CPS = 22;
const SEND_LIT = barTime(-0.25); // the last beat before the drop
const DROP = barTime(0);

const Title: React.FC<ShotProps> = ({t}) => {
	// big type from frame 1: the title, not a lyric; it hands over to "GIVE ME A GOAL." at 3.19 s
	const flicker = t > 2.8 ? 1 - clamp((t - 2.8) / 0.39) * 0.2 : 1;
	return (
		<svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
			<text x={96} y={500} fontFamily={FONT.sans} fontWeight={900} fontSize={190} letterSpacing="-0.045em" fill={C.greenWhite} opacity={flicker}>
				ALWAYS
			</text>
			<text x={96} y={672} fontFamily={FONT.sans} fontWeight={900} fontSize={190} letterSpacing="-0.045em" fill={C.greenWhite} opacity={flicker}>
				ALLOW
			</text>
			<text x={104} y={736} fontFamily={FONT.mono} fontSize={20} letterSpacing="0.1em" fill="rgba(216,228,220,0.7)">
				PERMISSION REQUEST · AGENT_01 · 1 OF ∞
			</text>
		</svg>
	);
};

/** Her pupil in C01's take, measured on the select in frame pixels (frame, x, y); the lid covers it from frame 56. */
const PUPIL: [number, number, number][] = [[0, 984, 508], [12, 975, 504], [24, 968, 500], [36, 974, 496], [48, 987, 495], [55, 987, 489]];
const pupilAt = (f: number): [number, number] => {
	const i = Math.max(0, PUPIL.findIndex(([g]) => g > f) - 1);
	const [f0, x0, y0] = PUPIL[i];
	const [f1, x1, y1] = PUPIL[Math.min(i + 1, PUPIL.length - 1)];
	const k = f1 > f0 ? clamp((f - f0) / (f1 - f0)) : 0;
	return [x0 + (x1 - x0) * k, y0 + (y1 - y0) * k];
};

const S001: React.FC<ShotProps> = (p) => {
	// the window reflected in her iris: on the take, just up and right of her pupil, moving with the push; it goes
	// as her lid closes. On the card, where the card draws the eye.
	const real = Boolean(clipFile(p.shot.clip));
	const cam = defaultCam(p, false);
	const [px, py] = real ? pupilAt(p.frame) : [W * 0.7 - 34 - 58, H * 0.5 - 30 + 22];
	const [cx, cy] = real ? onScreen(px + 58, py - 22, cam) : [px + 58, py - 22];
	const s = real ? cam.zoom : 1;
	const open = real ? 1 - clamp((p.frame - 53) / 3) : 1;
	return (
		<>
			<Title {...p} />
			<div style={{position: 'absolute', left: cx - 36 * s, top: cy - 20 * s, width: 72 * s, height: 40 * s, opacity: open, background: 'rgba(244,244,241,0.8)', borderRadius: 4, transform: 'skewY(-6deg)', boxShadow: '0 0 16px rgba(207,224,238,0.8)'}}>
				<div style={{position: 'absolute', left: 5, top: 5, width: 6, height: 6, borderRadius: 3, background: C.terracotta}} />
				<div style={{position: 'absolute', right: 5, bottom: 5, width: 22, height: 7, borderRadius: 2, background: C.terracotta}} />
			</div>
		</>
	);
};

const S002: React.FC<ShotProps> = ({t}) => {
	// an empty GOAL field under the type: the goal doesn't exist yet
	const k = inAt(t, wordAt(0, 3), 0.25);
	const caret = Math.floor(t * 2.2) % 2 === 0;
	return (
		<div style={{position: 'absolute', left: 96, top: 868, width: 700, height: 64, opacity: k, border: '1.5px solid rgba(216,228,220,0.55)', borderRadius: 10, display: 'flex', alignItems: 'center', gap: 16, padding: '0 20px'}}>
			<span style={{fontFamily: FONT.mono, fontSize: 18, letterSpacing: '0.1em', color: 'rgba(216,228,220,0.65)'}}>GOAL</span>
			<span style={{width: 3, height: 30, background: C.greenWhite, opacity: caret ? 1 : 0}} />
		</div>
	);
};

const S003: React.FC<ShotProps> = ({t}) => {
	// a giant 1 beside JUST ONE.
	const k = inAt(t, wordAt(1, 1), 0.12);
	return (
		<>
			<svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
				<text x={1380} y={860} fontFamily={FONT.sans} fontWeight={900} fontSize={720} letterSpacing="-0.06em" fill={C.terracotta} opacity={k} transform={`translate(0 ${(1 - k) * 40})`}>
					1
				</text>
			</svg>
			<Tag x={1400} y={900} text="goals required: 1" size={18} />
		</>
	);
};

const typedAt = (t: number) => typed(SENTENCE, t, TYPE_FROM, TYPE_CPS);

/** H_desk_typing's laptop screen in frame pixels: top-left, top-right, bottom-right, bottom-left. */
const SCREEN: [[number, number], [number, number], [number, number], [number, number]] = [[885, 428], [1138, 470], [1123, 668], [848, 612]];

const S004: React.FC<ShotProps> = ({t, shot}) => {
	// the Human's laptop by day: a chat app on its screen, pinned to the screen's corners on the plate
	const real = hasFootage(shot);
	return (
		<>
			{real ? (
				<div style={{position: 'absolute', left: 0, top: 0, width: 560, height: 360, transformOrigin: '0 0', transform: quad(560, 360, SCREEN), background: 'rgba(247,247,244,0.96)'}}>
					<div style={{position: 'absolute', left: 0, top: 0, width: 560, height: 34, background: 'rgba(11,12,14,0.06)', borderBottom: '1px solid rgba(11,12,14,0.1)'}} />
					<div style={{position: 'absolute', left: 18, top: 11, width: 10, height: 10, borderRadius: 5, background: C.terracotta}} />
					<ChatBox x={28} y={262} w={504} text={typedAt(t)} caret={Math.floor(t * 4) % 2 === 0} scale={0.62} />
				</div>
			) : (
				<div style={{position: 'absolute', left: 820, top: 520, width: 540, height: 300, transform: 'perspective(900px) rotateY(-8deg)', background: 'rgba(244,244,241,0.92)', borderRadius: 10, boxShadow: '0 10px 30px rgba(0,0,0,0.25)'}}>
					<ChatBox x={24} y={190} w={492} text={typedAt(t)} caret={Math.floor(t * 4) % 2 === 0} scale={0.6} />
				</div>
			)}
			{/* his head: on the plate, where it is; on the card, where the card draws him */}
			<div style={{position: 'absolute', ...(real ? {left: 380, top: 150, width: 290, height: 290} : {left: 605, top: 220, width: 172, height: 230}), border: '1.5px solid rgba(11,12,14,0.6)'}} />
			<Tag x={real ? 380 : 605} y={real ? 114 : 184} text="USER · TYPING" dark={false} size={15} />
		</>
	);
};

const S005: React.FC<ShotProps> = ({t}) => {
	// the one sentence lands in a chat box lower right; the send arrow lights on the last beat before the drop
	const lit = t >= SEND_LIT ? 1 : 0;
	const pressed = t >= DROP - 1 / 24 ? 1 : 0;
	return <ChatBox x={1020} y={850} w={804} text={typedAt(t)} caret={t < SEND_LIT && Math.floor(t * 4) % 2 === 0} sendLit={lit + pressed * 0.5} />;
};

export const spec: ChapterSpec = {
	graphics: {s001: S001, s002: S002, s003: S003, s004: S004, s005: S005},
};
