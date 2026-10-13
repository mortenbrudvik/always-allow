// ch13: Tool call II (237.06-252.48 s), shots s103-s111. Chant 2, harder and faster than chant 1: the terminal
// strobes, tool names fly over the grid, JSON results flicker, the rows strobe on the eighths, every monitor on
// the floor shows the same result; then sudden quiet, and DONE. with its echoes.
// Edit only this file for this chapter (ANIMATION_GUIDE.md).
import React from 'react';
import {JsonBlock, TodoList} from '../components/cards';
import {Terminal} from '../components/ui';
import {clamp, rnd} from '../lib/ease';
import {hasFootage} from '../lib/media';
import {TOKENS, TOOL_CALLS, work} from '../lib/story';
import {C, CHROME, FONT, H, W} from '../lib/theme';
import {beatIndex, eighthIndex, pulseEighth} from '../lib/time';
import {horizonRows} from './ch12';
import {FLOOR_SCREENS, LitPlate} from '../components/screens';
import type {ChapterSpec, ShotProps} from './types';
import {fmtInt, lyricOf, wordAt} from './util';

const TOOLS = ['browser.open', 'shell.run', 'mail.send', 'files.write', 'calendar.move', 'pay.charge', 'docs.edit', 'ci.rerun', 'slack.post', 'deploy.prod', 'search.web', 'db.query', 'git.push', 'drive.share', 'sms.send', 'keys.rotate'];

/** A tool call line, deterministic per index. */
const call = (i: number) => `$ ${TOOLS[Math.floor(rnd('tc', i) * TOOLS.length)]} --id ${String(Math.floor(rnd('id', i) * 9e5 + 1e5))}  {"ok": true}`;

/** A white strobe on the eighths, for footage and code alike. */
const Strobe: React.FC<{t: number; peak?: number}> = ({t, peak = 0.22}) => <div style={{position: 'absolute', inset: 0, background: C.flash, opacity: peak * pulseEighth(t, 22)}} />;

const S103: React.FC<ShotProps> = ({t, lt}) => {
	// the terminal full screen, scrolling faster than it can be read, strobing; TOOL CALLS +1 under the chrome
	const n = 12 + Math.floor(lt * 40);
	const tick = clamp((t - wordAt(73, 0)) / 0.6);
	return (
		<>
			<Terminal x={40} y={100} w={W - 80} h={H - 200} lines={Array.from({length: n}).map((_, i) => call(i))} fontSize={22} title="agent_01 — tool calls" opacity={0.75} />
			<Strobe t={t} />
			{tick > 0 && tick < 1 && (
				<div style={{position: 'absolute', right: CHROME, top: 124 - tick * 24, opacity: 1 - tick, fontFamily: FONT.mono, fontSize: 24, color: C.terracotta}}>TOOL CALLS +1</div>
			)}
		</>
	);
};

const S104: React.FC<ShotProps> = ({t}) => {
	// tool names across the grid, a new set on every eighth
	const e = eighthIndex(t);
	const out = [];
	for (let r = 0; r < 9; r++) {
		for (let c = 0; c < 16; c++) {
			if (rnd('show', e, r, c) > 0.45) {
				continue;
			}
			out.push(
				<div key={`${r}-${c}`} style={{position: 'absolute', left: 180 + c * 104 + 18, top: 130 + r * 104 - 9, fontFamily: FONT.mono, fontSize: 14, color: 'rgba(11,12,14,0.72)', background: 'rgba(244,244,241,0.8)', padding: '1px 4px', whiteSpace: 'nowrap'}}>
					{TOOLS[Math.floor(rnd('tn', e, r, c) * TOOLS.length)]}
				</div>,
			);
		}
	}
	return <>{out}</>;
};

const S105: React.FC<ShotProps> = ({lt}) => (
	// the terminal scrolls over the left half, off her face on the right
	<Terminal x={60} y={120} w={820} h={820} lines={Array.from({length: 20 + Math.floor(lt * 50)}).map((_, i) => call(i + 400))} fontSize={20} opacity={0.88} />
);

const S106: React.FC<ShotProps> = ({t}) => {
	// {"ok": true} x 64, each cell flickering on its own eighth
	const e = eighthIndex(t);
	const cells = [];
	for (let r = 0; r < 8; r++) {
		for (let c = 0; c < 8; c++) {
			const on = rnd('ok', e, r, c) > 0.3;
			cells.push(
				<div key={`${r}-${c}`} style={{opacity: on ? 1 : 0.15}}>
					<JsonBlock x={70 + c * 226} y={112 + r * 108} lines={['{"ok": true}']} size={20} />
				</div>,
			);
		}
	}
	return <>{cells}</>;
};

const S107: React.FC<ShotProps> = ({t}) => <Strobe t={t} peak={0.35} />;

const S108: React.FC<ShotProps> = ({t, shot}) => {
	// every monitor on the floor shows the same result, flashing in sync (on the plate, the footage layer lights its
	// screens)
	const on = pulseEighth(t, 10);
	if (hasFootage(shot)) {
		return null;
	}
	const cells = [];
	for (let r = 0; r < 5; r++) {
		for (let c = 0; c < 22; c++) {
			cells.push(<div key={`${r}-${c}`} style={{position: 'absolute', left: 120 + c * 78 + r * 10, top: 620 + r * 64, width: 48 - r * 4, height: 26 - r * 2, background: on > 0.3 ? C.screen : '#121618', opacity: 0.4 + 0.6 * on}} />);
		}
	}
	return <>{cells}</>;
};

const STEPS = ['open the browser', 'book the flight', 'fix the build', 'draft the deck', 'send the update', 'run every test', 'merge to main', 'deploy'];

const S109: React.FC<ShotProps> = ({t, shot}) => {
	// the to-do list advances a step on every beat, strobing, dim behind NEXT STEP.
	const done = Math.min(STEPS.length, 2 + beatIndex(t) - beatIndex(shot.t0));
	return (
		<>
			<div style={{opacity: 0.55}}>
				<TodoList x={96} y={180} items={STEPS} done={done} size={30} />
			</div>
			<Strobe t={t} peak={0.12} />
		</>
	);
};

const Blur: React.FC<{x: number; y: number; label: string; total: number; frame: number; k: number; align: 'left' | 'right'}> = ({x, y, label, total, frame, k, align}) => {
	// a counter racing too fast to read, on the chrome's count: its low digits new every frame, a ghost trail behind it
	const shown = Math.floor(total * work(frame / 24) * (1 + 0.004 * k) + rnd('blur', label, frame) * total * 0.004);
	return (
		<div style={{position: 'absolute', left: align === 'left' ? x : undefined, right: align === 'right' ? W - x : undefined, top: y, textAlign: align, color: C.ink}}>
			<div style={{fontFamily: FONT.mono, fontSize: 20, letterSpacing: '0.08em', opacity: 0.7}}>{label}</div>
			{[3, 2, 1, 0].map((g) => (
				<div key={g} style={{position: g ? 'absolute' : 'relative', top: g ? 28 + g * 10 : undefined, left: 0, right: 0, fontFamily: FONT.mono, fontSize: 64, fontVariantNumeric: 'tabular-nums', opacity: g ? 0.12 : 0.9, filter: `blur(${1.5 + g}px)`}}>
					{fmtInt(shown - g * 37)}
				</div>
			))}
		</div>
	);
};

const S110: React.FC<ShotProps> = ({frame, p}) => (
	// the counters blur on either side of her still face
	<>
		<Blur x={96} y={430} label="TOOL CALLS" total={TOOL_CALLS} frame={frame} k={p} align="left" />
		<Blur x={W - 96} y={430} label="TOKENS" total={TOKENS} frame={frame} k={p} align="right" />
	</>
);

const S111: React.FC<ShotProps> = ({t}) => {
	// DONE. with its echoes under the placed word (the echo taps, about every half second) and a checkmark
	const line = lyricOf(76);
	const d0 = line.t0;
	const check = clamp((t - d0 - 0.2) / 0.5);
	const tok = line.tokens[0];
	return (
		<svg width={W} height={H} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
			{[0.45, 0.9, 1.35, 1.8].map((e, i) =>
				t >= d0 + e ? (
					<text key={i} x={tok.x} y={tok.y + (i + 1) * line.size * 0.22} fontFamily="Geist" fontWeight={900} fontSize={line.size} letterSpacing={`${line.style.tracking}em`} fill="none" stroke={C.ink} strokeWidth={2} opacity={0.45 - i * 0.1}>
						{tok.text}
					</text>
				) : null,
			)}
			<path d={`M ${Math.min(W - 260, line.box.x + line.box.w + 60)} ${line.box.y + 40} l 60 64 l 130 -150`} fill="none" stroke={C.terracotta} strokeWidth={16} strokeLinecap="round" strokeLinejoin="round" strokeDasharray="330" strokeDashoffset={330 * (1 - check)} />
		</svg>
	);
};

export const spec: ChapterSpec = {
	graphics: {s103: S103, s104: S104, s105: S105, s106: S106, s107: S107, s108: S108, s109: S109, s110: S110, s111: S111},
	// s108 on the plate: its front-facing screens flash in sync
	footage: {s108: (p) => <LitPlate {...p} screens={FLOOR_SCREENS} on={pulseEighth(p.t, 10)} room={0.06 * pulseEighth(p.t, 10)} />},
	formation: {s107: () => horizonRows()},
};
