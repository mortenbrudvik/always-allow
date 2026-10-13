// ch07: A bigger window (129.45-142.44 s), shots s053-s056. Break 2: motif 2, the same window three times bigger
// (960x540) in the air in front of her; its scopes run on to "forever", and its footnote says 97 % get approved.
// Edit only this file for this chapter (ANIMATION_GUIDE.md).
import React from 'react';
import {BarCompare} from '../components/charts';
import {Cursor, Dialog, dialogButtons, SizeTag} from '../components/ui';
import {clamp, easeInOut, easeOut, lerp} from '../lib/ease';
import {W} from '../lib/theme';
import {SCOPES} from './ch04';
import type {ChapterSpec, ShotProps} from './types';
import {wordAt, wordNamed} from './util';

const LONG = [...SCOPES, 'forever'];
const BIG = {x: 800, y: 170, w: 960};

const S053: React.FC<ShotProps> = ({t, shot}) => {
	const k = easeOut(clamp((t - shot.t0) / 0.5));
	return (
		<>
			<Dialog x={BIG.x} y={BIG.y + (1 - k) * 30} w={BIG.w} scopes={SCOPES.slice(0, 3)} glow={0.9} opacity={k} />
			<SizeTag x={BIG.x} y={BIG.y + 560} text="WINDOW 960×540" />
		</>
	);
};

const S054: React.FC<ShotProps> = ({t}) => {
	const from = wordNamed(40, /keys/) - 0.3;
	const to = wordAt(40, -1) + 0.5;
	const w = 1300;
	return <Dialog x={(W - w) / 2} y={110} w={w} scopes={LONG} shown={lerp(3, LONG.length, clamp((t - from) / (to - from)))} glow={0.4} />;
};

const S055: React.FC<ShotProps> = ({t, shot}) => {
	const k = clamp((t - shot.t0 - 0.2) / 0.5);
	return (
		<>
			<Dialog x={BIG.x} y={BIG.y} w={BIG.w} scopes={SCOPES.slice(0, 3)} glow={0.9} footnote={k} />
			<BarCompare x={96} y={620} w={600} k={k} items={[{label: 'approved', value: 97, accent: true}, {label: 'denied', value: 3}]} source="Anthropic, 7 Aug 2026" />
		</>
	);
};

const S056: React.FC<ShotProps> = ({t}) => {
	// a small copy of the window at the corner; on "Or" its cursor moves toward [Always allow]
	const or = wordAt(42, 0);
	const k = easeInOut(clamp((t - or) / 0.6));
	const w = 400;
	const x = 96;
	const y = 130;
	const b = dialogButtons(x, y, w);
	return (
		<>
			<Dialog x={x} y={y} w={w} scopes={SCOPES.slice(0, 2)} footnote={1} hover={k > 0.95 ? 'always' : 'once'} />
			<Cursor x={lerp(b.once.x, b.always.x, k)} y={b.once.y + 4} size={26} />
		</>
	);
};

export const spec: ChapterSpec = {
	graphics: {s053: S053, s054: S054, s055: S055, s056: S056},
};
