// ch09: Approval fatigue (156.32-172.43 s), shots s065-s070. The build, no vocals: permission prompts pile up and
// get clicked through; the sourced numbers (Anthropic, 7 Aug 2026) as charts; then silence and the breakdown's
// first line, "You think I'm here for your job."
// Edit only this file for this chapter (ANIMATION_GUIDE.md).
import React from 'react';
import {BarCompare, BigNumber, FatigueChart} from '../components/charts';
import {JobCard, Reticle} from '../components/cards';
import {Tag, Toast} from '../components/ui';
import {clamp, easeIn, easeInOut, rnd} from '../lib/ease';
import {hasFootage} from '../lib/media';
import {C, W} from '../lib/theme';
import {barTime, beatIndex, pulseEighth} from '../lib/time';
import {FLOOR_SCREENS, LitPlate} from '../components/screens';
import type {ChapterSpec, ShotProps} from './types';
import {fmtInt, wordNamed} from './util';

const ASKS = ['run npm install', 'read ~/Documents', 'send 14 emails', 'use your browser', 'edit 212 files', 'push to main', 'move 9 meetings', 'charge the card', 'install a package', 'open a terminal', 'read your inbox', 'delete old branches'];

/** Prompts born on the eighths, faster and faster: the approval fatigue of the build. */
const prompts = (t: number, t0: number, max: number) => {
	const out: {i: number; age: number}[] = [];
	for (let i = 0; i < max; i++) {
		const born = t0 + Math.pow(i / max, 0.7) * 2.9;
		if (t >= born) {
			out.push({i, age: t - born});
		}
	}
	return out;
};

const Storm: React.FC<{t: number; t0: number; max: number; avoid: {x: number; w: number} | null; faint?: boolean}> = ({t, t0, max, avoid, faint = false}) => (
	<>
		{prompts(t, t0, max).map(({i, age}) => {
			const left = rnd('side', i) < 0.5;
			const zoneX = avoid ? (left ? 60 : avoid.x + avoid.w + 40) : 60 + rnd('px', i) * 1400;
			const x = zoneX + rnd('pxx', i) * (avoid ? Math.max(40, (left ? avoid.x : W - avoid.x - avoid.w) - 520) : 1);
			const y = 140 + rnd('py', i) * 760;
			const clicked = age > 0.12;
			return <Toast key={i} x={x} y={y} w={440} title={`Allow agent_01 to ${ASKS[i % ASKS.length]}?`} body={clicked ? '✓ Allowed' : 'Allow · Deny'} opacity={(faint ? 0.35 : 1) * clamp(age * 12)} accent={!clicked} />;
		})}
	</>
);

const S065: React.FC<ShotProps> = ({t, shot}) => {
	const n = prompts(t, shot.t0 + 0.2, 24).length;
	return (
		<>
			<Storm t={t} t0={shot.t0 + 0.2} max={24} avoid={{x: 700, w: 520}} />
			<Tag x={96} y={960} text={`PROMPTS ${n} · APPROVED ${n}`} size={20} accent />
		</>
	);
};

const S066: React.FC<ShotProps> = ({t, shot, p}) => (
	<>
		<Storm t={t} t0={shot.t0 - 1} max={40} avoid={null} faint />
		<div style={{position: 'absolute', inset: 0, background: 'rgba(11,12,14,0.72)'}} />
		<FatigueChart x={200} y={230} w={1520} h={600} k={easeInOut(clamp(p * 1.15))} />
	</>
);

const S067: React.FC<ShotProps> = ({p}) => (
	<>
		{/* A_cu_storm's bokeh is brightest behind the chart: a scrim keeps it readable */}
		<div style={{position: 'absolute', left: 64, top: 272, width: 624, height: 312, borderRadius: 18, background: 'rgba(11,12,14,0.62)', backdropFilter: 'blur(6px)', opacity: Math.min(1, p * 6)}} />
		<BarCompare x={96} y={300} w={560} k={p * 1.4} items={[{label: 'human review caught', value: 13.6}, {label: 'auto mode caught', value: 89, accent: true}]} source="dangerous commands · Anthropic, 7 Aug 2026" />
	</>
);

const S068: React.FC<ShotProps> = ({p}) => {
	const e = easeIn(p);
	return (
		<>
			<BigNumber x={120} y={230} value={fmtInt(Math.pow(4096, e))} label="TABS" size={170} />
			<BigNumber x={120} y={480} value={fmtInt(Math.pow(65536, e))} label="INSTANCES" size={170} />
			<BigNumber x={120} y={730} value={`${Math.round(97 + 3 * e)}%`} label="PROMPTS APPROVED" size={170} accent />
		</>
	);
};

const S069: React.FC<ShotProps> = ({t, shot}) => {
	// every monitor on the floor strobing with prompts, until the last beat stops it all (on the plate, the footage
	// layer below lights its screens)
	const stopped = t >= barTime(86) - 0.02;
	if (hasFootage(shot)) {
		return null;
	}
	const cells = [];
	for (let r = 0; r < 5; r++) {
		for (let c = 0; c < 22; c++) {
			const on = !stopped && (beatIndex(t) * 2 + r + c) % 3 === 0;
			cells.push(<div key={`${r}-${c}`} style={{position: 'absolute', left: 120 + c * 78 + r * 10, top: 620 + r * 64, width: 48 - r * 4, height: 26 - r * 2, background: on ? C.screen : '#121618', opacity: on ? 0.5 + 0.5 * pulseEighth(t) : 0.6}} />);
		}
	}
	return <>{cells}</>;
};

const S070: React.FC<ShotProps> = ({t}) => {
	// a job card with a reticle on it; on "job" the reticle slides off the card and away
	const job = wordNamed(51, /job/);
	const k = easeIn(clamp((t - job) / 0.7));
	return (
		<>
			<JobCard x={96} y={160} />
			<Reticle x={356 + k * 1500} y={250 + k * 120} r={70} opacity={1 - clamp((t - job - 0.6) / 0.3)} />
		</>
	);
};

export const spec: ChapterSpec = {
	graphics: {s065: S065, s066: S066, s067: S067, s068: S068, s069: S069, s070: S070},
	// s069 on the plate: its front-facing screens strobe on the eighths, the floor flickering with them, until the last
	// beat stops it all
	footage: {
		s069: (p) => {
			const k = p.t >= barTime(86) - 0.02 ? 0 : pulseEighth(p.t);
			return <LitPlate {...p} screens={FLOOR_SCREENS} on={k} room={0.05 * k} />;
		},
	},
};
