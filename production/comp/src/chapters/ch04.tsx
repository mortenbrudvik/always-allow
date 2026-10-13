// ch04: A little window (61.38-77.95 s), shots s024-s028. Break 1, drums out: motif 1, the permission window at its
// smallest, 320x180 on a laptop in a dark room; the cursor hovers over [Allow once], then slides to [Always allow].
// Edit only this file for this chapter (ANIMATION_GUIDE.md).
import React from 'react';
import {Cursor, Dialog, dialogButtons, SizeTag} from '../components/ui';
import {clamp, easeInOut, easeOut, lerp} from '../lib/ease';
import {C, FONT, H, W} from '../lib/theme';
import type {ChapterSpec, ShotProps} from './types';
import {inAt, wordAt, wordNamed} from './util';

export const SCOPES = ['read your files', 'write your files', 'run commands', 'use your browser', 'send email as you', 'spend money', 'everything'];

// beside her laptop on A_darkroom_ws (its screen at x 1210-1350, y 585-690), in the dark to its right
const S024: React.FC<ShotProps> = ({t}) => (
	<div style={{position: 'absolute', left: 1392, top: 604, fontFamily: FONT.mono, fontSize: 19, letterSpacing: '0.08em', color: 'rgba(216,228,220,0.7)', opacity: inAt(t, 62, 0.8)}}>
		<span style={{color: C.terracotta}}>●</span> waiting for input{'.'.repeat(1 + (Math.floor(t * 2) % 3))}
	</div>
);

const S025: React.FC<ShotProps> = ({t}) => {
	// the small window opens on the laptop's screen (on the real plate, fit to its corners from the plate)
	const open = wordNamed(15, /window/);
	const k = easeOut(clamp((t - open) / 0.35));
	const w = 320;
	const x = W / 2 - w / 2;
	const y = H / 2 - 110;
	return (
		<>
			<div style={{position: 'absolute', left: x + w / 2, top: y + 90, transform: `translate(-50%, -50%) scale(${lerp(0.2, 1, k)})`, opacity: clamp(k * 3)}}>
				<Dialog x={-w / 2} y={-90} w={w} scopes={SCOPES.slice(0, 2)} glow={0.6} />
			</div>
			{k > 0.5 && <SizeTag x={x} y={y + 200} text="WINDOW 320×180" />}
		</>
	);
};

const S026: React.FC<ShotProps> = ({t}) => {
	// her request, typed out beside her: the keys to everything
	const from = wordNamed(16, /keys/) - 0.2;
	const to = wordAt(16, -1) + 0.3;
	const shown = clamp((t - from) / (to - from)) * SCOPES.length;
	const full = Math.floor(shown);
	return (
		<div style={{position: 'absolute', left: 96, top: 220, fontFamily: FONT.mono, fontSize: 30, lineHeight: 1.6, color: C.greenWhite}}>
			<div style={{fontSize: 18, letterSpacing: '0.1em', color: 'rgba(216,228,220,0.6)', marginBottom: 10}}>AGENT_01 REQUESTS</div>
			{SCOPES.slice(0, Math.min(SCOPES.length, full + 1)).map((s, i) => (
				<div key={s} style={{opacity: i < full ? 1 : shown - full, color: s === 'everything' ? C.terracotta : undefined}}>
					<span style={{color: 'rgba(216,228,220,0.5)'}}>{'·  '}</span>
					{s}
				</div>
			))}
		</div>
	);
};

const S027: React.FC<ShotProps> = ({t, shot}) => {
	// the window up close; the cursor drifts in and settles on [Allow once]
	const w = 1060;
	const x = (W - w) / 2;
	const y = 380;
	const b = dialogButtons(x, y, w);
	const once = wordNamed(17, /once/);
	const k = easeInOut(clamp((t - shot.t0 - 0.3) / (once - shot.t0 - 0.3)));
	const cx = lerp(W - 200, b.once.x + 10, k);
	const cy = lerp(H + 60, b.once.y + 6, k);
	return (
		<>
			<Dialog x={x} y={y} w={w} scopes={SCOPES.slice(0, 3)} hover={k > 0.92 ? 'once' : null} glow={0.3} />
			<Cursor x={cx} y={cy} size={40} />
		</>
	);
};

/** Her eyes (the card's two eyes, or the plate's irises from tracking): the cursor's reflection moves to [Always allow]. */
const EYES: [number, number][] = [[W * 0.36, H * 0.5], [W * 0.64, H * 0.5]];

const S028: React.FC<ShotProps> = ({t, shot}) => {
	const or = wordAt(18, 0);
	const k = easeInOut(clamp((t - or) / 0.5));
	const big = clamp((t - (shot.t1 - 0.3)) / 0.2);
	return (
		<>
			{EYES.map(([ex, ey], i) => (
				<div key={i} style={{position: 'absolute', left: ex - 40, top: ey - 36, width: 64, height: 36, background: 'rgba(244,244,241,0.75)', borderRadius: 3, transform: 'skewY(-5deg)', boxShadow: '0 0 12px rgba(207,224,238,0.8)'}}>
					<div style={{position: 'absolute', right: 3, bottom: 3, width: 18, height: 6, background: C.terracotta, borderRadius: 1}} />
					<div style={{position: 'absolute', right: 24, bottom: 3, width: 14, height: 6, border: '1px solid rgba(11,12,14,0.5)', borderRadius: 1}} />
					<div style={{position: 'absolute', left: lerp(30, 50, k), top: lerp(22, 24, k), width: 5, height: 7, background: C.ink, clipPath: 'polygon(0 0, 100% 70%, 40% 60%, 0 100%)'}} />
				</div>
			))}
			{big > 0 && (
				// the button comes forward for the shape match into the white stage (s029)
				<div style={{position: 'absolute', left: W / 2 - 150, top: H / 2 - 42, width: 300, height: 84, borderRadius: 18, background: C.terracotta, opacity: big, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT.sans, fontWeight: 650, fontSize: 30, color: C.paper}}>
					Always allow
				</div>
			)}
		</>
	);
};

export const spec: ChapterSpec = {
	graphics: {s024: S024, s025: S025, s026: S026, s027: S027, s028: S028},
};
