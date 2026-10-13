// ch11: One little word (193.13-209.57 s), shots s079-s087. The hard stop, the instrumental drop, the riser:
// motif 3, the window at full screen; it multiplies to 256, falls back to one, and the cursor starts to move on its
// own toward [Always allow] under the whispered "Allow?".
// Edit only this file for this chapter (ANIMATION_GUIDE.md).
import React from 'react';
import {Img} from 'remotion';
import {WindowStorm} from '../components/charts';
import {BigButton, BUTTON_BAR, Cursor, Dialog, dialogButtons, SizeTag} from '../components/ui';
import {clamp, easeInOut, lerp, rnd} from '../lib/ease';
import {type Box, intersects, plannedBody} from '../lib/layout';
import {mediaUrl} from '../lib/media';
import {C, FONT, H, W} from '../lib/theme';
import {barTime, beatIndex, pulse} from '../lib/time';
import type {ChapterSpec, ShotProps} from './types';
import {lyricOf, wordAt} from './util';

const FULL = {x: 0, y: 0, w: W};
const BUTTONS = dialogButtons(0, 0, W);
/** Where the pointer rests before it moves by itself (s079, s085). */
const REST = {x: 700, y: 640};

/** The window's own status line, in its button bar: the chrome is off for this passage. */
const Mode: React.FC<{t: number; blink?: boolean}> = ({t, blink = false}) => (
	<div style={{position: 'absolute', left: 60, top: 962, fontFamily: FONT.mono, fontSize: 20, letterSpacing: '0.08em', color: C.ink2, opacity: blink ? (Math.floor(t * 3) % 2 ? 1 : 0.2) : 1}}>MODE: MANUAL</div>
);

const S079: React.FC<ShotProps> = ({t}) => {
	// black on the hard stop; on "is" the window is there, full screen, waiting, its pointer blinking
	if (t < wordAt(59, 0)) {
		return <div style={{position: 'absolute', inset: 0, background: C.blackDeep}} />;
	}
	return (
		<>
			<Dialog {...FULL} scopes={[]} blankBody />
			<Cursor x={REST.x} y={REST.y} size={44} opacity={Math.floor(t * 2) % 2 ? 1 : 0.35} />
			<SizeTag x={80} y={160} text="WINDOW 1920×1080" dark={false} />
		</>
	);
};

const STORM = [2, 4, 16, 64];
/** WORD., the tail of line 59: it slams on the drop and holds through s081. Looked up at render time, after the
 * chapters have registered their formations (the lyric engine places lines on first use). */
const word = () => lyricOf(59, 1);

/** A soft dark pool behind a lyric, so it reads over the bright windows. */
const Pool: React.FC<{box: Box; opacity?: number}> = ({box, opacity = 0.85}) => (
	<div style={{position: 'absolute', left: box.x - 90, top: box.y - 70, width: box.w + 180, height: box.h + 140, borderRadius: 80, background: C.blackDeep, opacity, filter: 'blur(40px)'}} />
);

const S080: React.FC<ShotProps> = ({t, shot}) => {
	// the drop: the window multiplies on the beats
	const i = clamp(beatIndex(t) - beatIndex(shot.t0), 0, STORM.length - 1);
	return (
		<>
			<WindowStorm count={STORM[i]} pulse={pulse(t)} thumb />
			{t < word().tEnd && <Pool box={word().box} />}
		</>
	);
};

/** A box grown by a margin, to keep windows clear of her. */
const grow = (b: Box, m: number): Box => ({x: b.x - m, y: b.y - m, w: b.w + 2 * m, h: b.h + 2 * m});

const S081: React.FC<ShotProps> = ({t, shot, lt}) => {
	// hundreds of windows in depth around her, in parallax; none over her
	const body = plannedBody(shot);
	const keepOut = body ? grow(body, 40) : null;
	return (
		<>
			{Array.from({length: 70}).map((_, i) => {
				const depth = 0.25 + rnd('d81', i) * 0.75;
				const w = 300 * depth;
				const x = rnd('x81', i) * (W - w) + lt * 60 * (depth - 0.5);
				const y = 110 + rnd('y81', i) * (H - 200 - (w * 9) / 16) + lt * 40 * (1 - depth);
				if (keepOut && intersects({x, y, w, h: (w * 9) / 16}, keepOut)) {
					return null;
				}
				return <Dialog key={i} x={x} y={y} w={w} scopes={['everything']} glow={0.2} opacity={0.35 + 0.6 * depth} />;
			})}
			{t < word().tEnd && <Pool box={word().box} opacity={0.7} />}
		</>
	);
};

const S082: React.FC<ShotProps> = ({t}) => <WindowStorm count={256} pulse={pulse(t)} />;

const S083: React.FC<ShotProps> = ({lt}) => (
	// windows drift up the left edge of the frame, well clear of her face on the right
	<>
		{Array.from({length: 9}).map((_, i) => {
			const w = 200 + rnd('w83', i) * 220;
			const x = -80 + rnd('x83', i) * (860 - w);
			const y = H + 40 - ((rnd('y83', i) * (H + 400) + lt * (120 + rnd('s83', i) * 160)) % (H + 400));
			return <Dialog key={i} x={x} y={y} w={w} scopes={['everything']} glow={0.3} opacity={0.55 + 0.35 * rnd('o83', i)} />;
		})}
	</>
);

const S084: React.FC<ShotProps> = ({t, shot}) => {
	// 256 windows fall back into one over two bars; then the single window at full screen, her face faint in its glass
	const k = easeInOut(clamp((t - shot.t0) / (barTime(107) - 0.4 - shot.t0)));
	const n = Math.max(1, Math.round(Math.pow(256, 1 - k)));
	if (n > 1) {
		return <WindowStorm count={n} />;
	}
	return (
		<>
			<Dialog {...FULL} scopes={[]} blankBody />
			{/* her face, grey and soft, multiplied faintly into the white glass (a crop of B_cu_stage2) */}
			<Img src={mediaUrl('production/assets/thumbs/agent_face_reflection.jpg')} style={{position: 'absolute', left: W / 2 - 330, top: 150, width: 660, height: 660, opacity: 0.16, mixBlendMode: 'multiply', filter: 'blur(1.5px) contrast(1.15)', WebkitMaskImage: 'radial-gradient(ellipse 48% 50% at 50% 48%, #000 55%, transparent 100%)'}} />
		</>
	);
};

const S085: React.FC<ShotProps> = ({t, shot}) => {
	// the cursor starts to move toward [Always allow] by itself; it gets under half way before the whisper
	const k = easeInOut(clamp((t - shot.t0) / 3.2));
	return (
		<>
			<Dialog {...FULL} scopes={[]} blankBody />
			<Cursor x={lerp(REST.x, BUTTONS.always.x - 40, k)} y={lerp(REST.y, BUTTONS.always.y - 10, k)} size={46} />
			<Mode t={t} />
		</>
	);
};

const S087: React.FC<ShotProps> = ({t}) => (
	// the cursor over [Always allow]: half a bar of stillness
	<>
		<div style={{position: 'absolute', inset: 0, background: BUTTON_BAR}} />
		<BigButton cx={W / 2} cy={H / 2} w={860} />
		<Cursor x={W / 2 + 335} y={H / 2 + 22} size={110} />
		<Mode t={t} blink />
	</>
);

export const spec: ChapterSpec = {
	graphics: {s079: S079, s080: S080, s081: S081, s082: S082, s083: S083, s084: S084, s085: S085, s087: S087},
};
