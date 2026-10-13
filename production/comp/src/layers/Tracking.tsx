// Tracking, as if she watches herself (STYLE_BIBLE.md): her face box with corner marks, a confidence,
// and landmark points at her eyes and lips. From her tracking (production/clips/tracking/<clip>.json, or the
// plate's boxes) where it exists, else from the board's planned framing, with a little tracker jitter.
import React from 'react';
import type {Shot} from '../lib/data';
import {rnd, wob} from '../lib/ease';
import {type Box, plannedBody, plannedFace} from '../lib/layout';
import {C, FONT, worldOf} from '../lib/theme';

const Corners: React.FC<{b: Box; colour: string; len?: number; w?: number}> = ({b, colour, len = 20, w = 1.5}) => {
	const l = Math.min(len, b.w / 3, b.h / 3);
	const d = [
		`M ${b.x} ${b.y + l} V ${b.y} H ${b.x + l}`,
		`M ${b.x + b.w - l} ${b.y} H ${b.x + b.w} V ${b.y + l}`,
		`M ${b.x + b.w} ${b.y + b.h - l} V ${b.y + b.h} H ${b.x + b.w - l}`,
		`M ${b.x + l} ${b.y + b.h} H ${b.x} V ${b.y + b.h - l}`,
	].join(' ');
	return <path d={d} fill="none" stroke={colour} strokeWidth={w} />;
};

/** Twelve landmarks relative to a face box: eye corners, pupils, brows, nose, lip corners and centres. */
const LANDMARKS: [number, number][] = [
	[0.3, 0.42], [0.42, 0.42], [0.58, 0.42], [0.7, 0.42],
	[0.36, 0.41], [0.64, 0.41], [0.33, 0.33], [0.67, 0.33],
	[0.5, 0.6], [0.4, 0.75], [0.6, 0.75], [0.5, 0.78],
];

/** Keep a box clear of the chrome: the counters at the top corners and the ticker at the foot. */
const inFrame = (b: Box | null): Box | null => {
	if (!b) {
		return null;
	}
	const x0 = Math.max(b.x, 28);
	const x1 = Math.min(b.x + b.w, 1892);
	const y0 = Math.max(b.y, 118);
	const y1 = Math.min(b.y + b.h, 1008);
	return x1 - x0 > 20 && y1 - y0 > 20 ? {x: x0, y: y0, w: x1 - x0, h: y1 - y0} : null;
};

export const Tracking: React.FC<{shot: Shot; frame: number; face?: Box | null; track?: {landmarks: [number, number][]; body: Box | null} | null}> = ({
	shot, frame, face, track,
}) => {
	const t = frame / 24;
	// tracked where the data exists (a frame where she wasn't found draws nothing), else as planned
	const f = inFrame(track ? (face ?? null) : (face ?? plannedFace(shot)));
	const body = inFrame(track ? track.body : plannedBody(shot));
	if (!f && !body) {
		return null;
	}
	const world = worldOf(shot);
	const colour = world === 'dark' ? 'rgba(216,228,220,0.8)' : 'rgba(11,12,14,0.72)';
	const jx = wob(t, 7, shot.id, 'x') * 3;
	const jy = wob(t, 7, shot.id, 'y') * 3;
	const conf = (0.97 + 0.02 * wob(t, 3, shot.id, 'c')).toFixed(2);
	const label = shot.framing === 'ECU' ? 'AGENT_01 · EYE' : `AGENT_01 ${conf}`;
	return (
		<svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
			{body && !f && <Corners b={{...body, x: body.x + jx, y: body.y + jy}} colour={colour} len={14} w={1.2} />}
			{f && (
				<g>
					<Corners b={{...f, x: f.x + jx, y: f.y + jy}} colour={colour} />
					<text x={f.x + jx + (f.y < 140 ? 8 : 0)} y={f.y < 140 ? f.y + jy + 24 : f.y + jy - 10} fontFamily={FONT.mono} fontSize={15} letterSpacing="0.06em" fill={colour}>
						{label}
					</text>
					{shot.framing !== 'ECU' &&
						(track?.landmarks.length ? track.landmarks.map(([x, y]) => [(x - f.x) / f.w, (y - f.y) / f.h]) : LANDMARKS).map(([u, v], i) => (
							<rect
								key={i}
								x={f.x + u * f.w + jx + wob(t, 11, shot.id, i) * 1.6 - 2}
								y={f.y + v * f.h + jy + wob(t, 11, shot.id, i, 'y') * 1.6 - 2}
								width={4}
								height={4}
								fill={i >= 9 ? C.terracotta : colour}
								opacity={0.55 + 0.35 * rnd(shot.id, i)}
							/>
						))}
				</g>
			)}
		</svg>
	);
};
