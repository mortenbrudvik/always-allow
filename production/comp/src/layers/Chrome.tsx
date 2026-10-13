// The chrome, the video's through-line (STYLE_BIBLE.md): the session clock, the tool-call and token
// counters, the mode flag and the ticker, in thin Geist Mono. Its numbers are the Agent's own session in the
// story (src/lib/story.ts), not this production's.
import React from 'react';
import {TICKER} from '../data/ticker';
import {shotAtFrame, shots} from '../lib/data';
import {pad} from '../lib/ease';
import {CHROME, C, FONT, ink, worldOf} from '../lib/theme';
import {TOKENS, TOOL_CALLS, work} from '../lib/story';
import {barAt, barTime, beatPhase, pulse} from '../lib/time';

const CLICK = barTime(109);
const OFF: [number, number][] = [
	[barTime(99.8125), barTime(101)], // the hard stop
	[barTime(105), barTime(109)], // the riser under "Allow?"
	[barTime(145), Infinity], // the tail
];
const DIM: [number, number][] = [[barTime(26.25), barTime(28.25)]];

// "Tool call." in the chants: each one ticks the counter visibly
const TOOL_CALL_TIMES = shots
	.flatMap((s) => s.lyrics)
	.filter((l) => /^Tool call/.test(l.text))
	.map((l) => l.words[0].t0);

/** The Agent's session clock: it runs with the song from 00:00:00. */
export const clock = (t: number) => {
	const s = Math.max(0, t);
	return `${pad(s / 3600, 2)}:${pad((s / 60) % 60, 2)}:${pad(s % 60, 2)}`;
};

const Digits: React.FC<{now: string; before: string; colour: string}> = ({now, before, colour}) => (
	<>
		{[...now].map((ch, i) => (
			<span key={i} style={{color: before[i] !== ch && /\d/.test(ch) ? C.terracotta : colour}}>
				{ch}
			</span>
		))}
	</>
);

export const Chrome: React.FC<{frame: number}> = ({frame}) => {
	const t = frame / 24;
	if (OFF.some(([a, b]) => t >= a && t < b)) {
		return null;
	}
	const shot = shotAtFrame(frame);
	const world = worldOf(shot);
	const {fgSoft, line} = ink(world);
	const dim = DIM.some(([a, b]) => t >= a && t < b) ? 0.45 : 1;
	const calls = (tt: number) => Math.round(work(tt) * (TOOL_CALLS - TOOL_CALL_TIMES.length)) + TOOL_CALL_TIMES.filter((x) => x <= tt).length;
	const tokens = (tt: number) => Math.round(work(tt) * TOKENS);
	const prev = t - 1 / 24;
	const callsNow = calls(t).toLocaleString('en-US');
	const callsPrev = calls(prev).toLocaleString('en-US').padStart(callsNow.length, ' ');
	const tokNow = tokens(t).toLocaleString('en-US');
	const tokPrev = tokens(prev).toLocaleString('en-US').padStart(tokNow.length, ' ');
	const auto = t >= CLICK;
	const bar = barAt(t);
	const {i} = beatPhase(t);
	const live = 0.55 + 0.45 * pulse(t, 6);
	// a soft halo in the other world's colour: unseen where the footage matches the shot's world, it keeps the chrome
	// readable where it doesn't (the dark top of the side-on wall in s099, a light world's dark ink over it)
	const halo = world === 'dark' ? 'rgba(11,12,14,0.9)' : 'rgba(244,244,241,0.9)';
	const style: React.CSSProperties = {position: 'absolute', fontFamily: FONT.mono, fontSize: 19, letterSpacing: '0.06em', color: fgSoft, lineHeight: 1.5, whiteSpace: 'pre', textShadow: `0 0 2px ${halo}, 0 0 7px ${halo}`};
	// the ticker: one line, scrolling right to left at a steady speed
	const text = TICKER.join('     ▍     ');
	const speed = 92;
	const charW = 19 * 0.6 + 19 * 0.06;
	const loop = (text.length + 11) * charW;
	const x = -((t * speed) % loop);
	return (
		<div style={{position: 'absolute', inset: 0, opacity: dim, pointerEvents: 'none'}}>
			<div style={{...style, left: CHROME, top: CHROME}}>
				<span style={{color: C.terracotta, opacity: live}}>●</span> SESSION {clock(t)}
				{'\n'}
				<span style={{fontSize: 15, opacity: 0.8}}>
					BAR {bar < 0 ? '-' : ' '}
					{pad(Math.abs(Math.floor(bar)), 3)} · BEAT {((i % 4) + 4) % 4 + 1} · 24 FPS
				</span>
			</div>
			<div style={{...style, right: CHROME, top: CHROME, textAlign: 'right'}}>
				TOOL CALLS <Digits now={callsNow} before={callsPrev} colour={fgSoft} />
				{'\n'}
				TOKENS <Digits now={tokNow} before={tokPrev} colour={fgSoft} />
				{'\n'}
				<span style={{fontSize: 15, color: auto ? C.terracotta : fgSoft}}>MODE: {auto ? 'AUTO' : 'MANUAL'}</span>
			</div>
			<div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 58, borderTop: `1px solid ${line}`, overflow: 'hidden'}}>
				<div style={{...style, left: x, top: 16, fontSize: 19}}>{`${text}     ▍     ${text}     ▍     ${text}`}</div>
			</div>
		</div>
	);
};
