// ch08: Always allow II (142.44-156.32 s), shots s057-s064. Hook 2 on a new set: 49 of her in a 7x7 grid before
// a cobalt wall, the palms again, a mirrored room to infinity, the ring from above, the blink, the bow.
// Edit only this file for this chapter (ANIMATION_GUIDE.md).
import React from 'react';
import {Tag} from '../components/ui';
import {clamp, easeOut, lerp, rnd} from '../lib/ease';
import {C, FONT, W} from '../lib/theme';
import {row7} from './ch05';
import type {ChapterSpec, ShotProps, Slot} from './types';
import {wordNamed} from './util';

/** 49 of her: seven rows of seven, receding toward the cobalt wall. */
/** 49 of her in a 7x7 grid before the cobalt wall (s057, s061), seen from a little above: each row further back a
 * step higher and a little smaller, back to the wall's foot, and alternate rows staggered by half a place, so every
 * face shows between the two in front. In line and at one height, the copies behind stacked into ghosted fans. */
export const grid49 = (): Slot[] => {
	const out: Slot[] = [];
	for (let r = 6; r >= 0; r--) {
		const h = 500 * Math.pow(0.96, r);
		const gap = 0.37 * h; // centre to centre: her figure is about 0.29 of her height wide
		const shift = r % 2 ? (r % 4 === 1 ? gap / 2 : -gap / 2) : 0;
		for (let i = 0; i < 7; i++) {
			out.push({x: W / 2 + (i - 3) * gap + shift, y: 985 - r * 44, h, label: r === 0 && i === 3 ? 'AGENT_01' : `INSTANCE_${String(r * 7 + i + 1).padStart(4, '0')}`});
		}
	}
	return out;
};

const FrontLabels: React.FC<{slots: Slot[]}> = ({slots}) => (
	<>
		{/* badges on the front row's chests: above their heads they sat on the faces of the row behind */}
		{slots.slice(-7).map((s, i) => (
			<div key={i} style={{position: 'absolute', left: s.x, top: s.y - s.h * 0.74, transform: 'translateX(-50%)', padding: '3px 7px', borderRadius: 3, background: s.label === 'AGENT_01' ? C.terracotta : 'rgba(11,12,14,0.82)', fontFamily: FONT.mono, fontSize: 13, color: C.white, whiteSpace: 'nowrap'}}>
				{s.label}
			</div>
		))}
		<Tag x={1500} y={960} text="INSTANCES 0001–0048 + AGENT_01" dark={false} size={14} />
	</>
);

const S057: React.FC<ShotProps> = () => <FrontLabels slots={grid49()} />;

/** s058's front row, close, on the right: the left third stays clear for HAND ME THE KEYS (line 44, left zone). */
const ROW_058: Slot[] = [0, 1, 2, 3].map((i) => ({x: 1110 + i * 300, y: 1400, h: 1150, label: i === 0 ? 'AGENT_01' : `INSTANCE_${String(i).padStart(4, '0')}`}));

const S058: React.FC<ShotProps> = ({t}) => {
	const keys = wordNamed(44, /keys/);
	const k = easeOut(clamp((t - keys + 0.15) / 0.3));
	return (
		<>
			{ROW_058.map((s, i) => (
				<div key={i} style={{position: 'absolute', left: s.x - 30, top: lerp(360, 640, k), opacity: k, padding: '6px 10px', background: C.ink, color: C.greenWhite, fontFamily: FONT.mono, fontSize: 18, borderRadius: 4, transform: 'translateX(-50%)', whiteSpace: 'nowrap'}}>
					{`API_KEY •••• ${String(i + 1).padStart(2, '0')}`}
				</div>
			))}
		</>
	);
};

const S059: React.FC<ShotProps> = ({t}) => {
	// a process tree beside her: one root, 49 leaves
	const run = wordNamed(45, /run/);
	const n = Math.floor(clamp((t - run) / 1.0) * 49);
	return (
		<svg width={W} height={1080} style={{position: 'absolute', inset: 0}}>
			<circle cx={1150} cy={800} r={12} fill={C.terracotta} />
			{Array.from({length: n}).map((_, i) => {
				const x = 1230 + (i % 7) * 30;
				const y = 710 + Math.floor(i / 7) * 28;
				return (
					<g key={i}>
						<line x1={1150} y1={800} x2={x} y2={y} stroke={C.ink} strokeWidth={1} opacity={0.3} />
						<circle cx={x} cy={y} r={6} fill={C.ink} />
					</g>
				);
			})}
			<text x={1140} y={680} fontFamily={FONT.mono} fontSize={20} fill={C.ink}>{`agent_01 · ${n} processes`}</text>
		</svg>
	);
};

const S060: React.FC<ShotProps> = ({lt}) => (
	<>
		{Array.from({length: 22}).map((_, i) => {
			const n = Math.round(Math.pow(4096, (i + 1) / 22));
			return (
				<div key={i} style={{position: 'absolute', left: 120 + rnd('mx', i) * 1600, top: 520 + rnd('my', i) * 380, fontFamily: FONT.mono, fontSize: 15 - Math.floor(i / 8) * 2, color: 'rgba(11,12,14,0.72)', opacity: clamp(lt * 4 - i * 0.12), whiteSpace: 'nowrap'}}>
					{`INSTANCE_${String(n).padStart(4, '0')}`}
				</div>
			);
		})}
	</>
);

const S061: React.FC<ShotProps> = () => <FrontLabels slots={grid49()} />;

const S062: React.FC<ShotProps> = ({t}) => {
	const how = wordNamed(48, /how/);
	return (
		<div style={{position: 'absolute', left: 1440, top: 900, display: 'flex', alignItems: 'center', gap: 12, fontFamily: FONT.mono, fontSize: 24, color: C.ink}}>
			how:
			<span style={{display: 'inline-block', width: 220 * clamp((t - how) / 0.15), height: 30, background: C.ink}} />
		</div>
	);
};

const S063: React.FC<ShotProps> = ({t}) => {
	const blink = wordNamed(49, /blink/);
	const k = t >= blink + 3 / 24 ? 1 : clamp((t - 152.8) / 4) * 0.25;
	return (
		<div style={{position: 'absolute', left: 96, top: 800, width: 760}}>
			<div style={{fontFamily: FONT.mono, fontSize: 18, color: C.ink2, marginBottom: 10}}>{k >= 1 ? 'DONE · 100%' : `WORKING · ${Math.round(k * 100)}%`}</div>
			<div style={{height: 16, borderRadius: 8, background: 'rgba(11,12,14,0.1)'}}>
				<div style={{width: `${k * 100}%`, height: 16, borderRadius: 8, background: k >= 1 ? C.pass : C.terracotta}} />
			</div>
		</div>
	);
};

export const spec: ChapterSpec = {
	graphics: {s057: S057, s058: S058, s059: S059, s060: S060, s061: S061, s062: S062, s063: S063},
	formation: {
		s057: () => grid49(),
		s058: () => ROW_058,
		s061: () => grid49(),
		s064: () => row7(560, 900, 190),
	},
};
