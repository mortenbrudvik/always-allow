// ch02: Tabs open (14.38-35.86 s), shots s006-s013. The drop: the Enter key sends the sentence, tabs burst out,
// the monitors wake behind her on the beat, the Human leaves for lunch, and four type slams: tabs, tools, plan, go.
// Edit only this file for this chapter (ANIMATION_GUIDE.md).
import React from 'react';
import {BigNumber} from '../components/charts';
import {Bubble, BrowserWindow, Tag, Terminal} from '../components/ui';
import {clamp, easeIn, easeOut, lerp, rnd} from '../lib/ease';
import {hasFootage} from '../lib/media';
import {C, FONT, W} from '../lib/theme';
import {barTime, beatIndex, beats, pulse} from '../lib/time';
import {SENTENCE} from './ch01';
import {FLOOR_SCREENS, LitPlate} from '../components/screens';
import type {ChapterSpec, ShotProps} from './types';
import {inAt, wordAt, wordNamed} from './util';

const TITLES = ['flights · SFO → AUS', 'CI · build #4121', 'Q3 launch deck', 'tests · 214', 'calendar · this week', 'docs · launch plan', 'hotels · Austin', 'pricing page', 'status page', 'inbox · 38 unread', 'metrics · signups', 'press kit', 'changelog', 'release notes', 'on-call rota', 'expenses', 'vendor contract', 'survey results'];

/** Tabs open so far: 17 by the end of the burst, 40 on "forty" in the verse (ch03 finishes the count). */
export const tabsAt = (t: number) => {
	const keys: [number, number][] = [[barTime(0), 0], [barTime(1), 17], [barTime(3), 24], [barTime(4), 31], [barTime(7), 36]];
	let v = 0;
	for (let i = 0; i < keys.length - 1; i++) {
		if (t >= keys[i][0]) {
			v = lerp(keys[i][1], keys[i + 1][1], clamp((t - keys[i][0]) / (keys[i + 1][0] - keys[i][0])));
		}
	}
	return Math.floor(t >= keys[keys.length - 1][0] ? 36 : v);
};

const TabCount: React.FC<{t: number; dark?: boolean}> = ({t, dark = true}) => <BigNumber x={96} y={760} value={String(tabsAt(t)).padStart(2, '0')} label="TABS OPEN" size={150} dark={dark} />;

const S006: React.FC<ShotProps> = ({t}) => {
	// SEND on the kick: the bubble flies up, and windows burst out of it
	const drop = barTime(0);
	const fly = easeOut(clamp((t - drop) / 0.28));
	const n = tabsAt(t);
	return (
		<>
			{Array.from({length: n}).map((_, i) => {
				const born = drop + 0.05 + i * 0.09;
				const k = easeOut(clamp((t - born) / 0.35));
				const tx = 160 + rnd('b6x', i) * 1300;
				const ty = 140 + rnd('b6y', i) * 560;
				const x = lerp(1300, tx, k);
				const y = lerp(820, ty, k);
				return <BrowserWindow key={i} x={x} y={y} w={420 * (0.5 + 0.5 * k)} h={260 * (0.5 + 0.5 * k)} title={TITLES[i % TITLES.length]} path={`/${TITLES[i % TITLES.length].split(' ')[0]}`} seed={i} lines={4} opacity={clamp(k * 3)} accent={i === n - 1} />;
			})}
			<Bubble x={1020} y={lerp(860, 150, fly)} w={804} text={SENTENCE} meta={fly >= 1 ? '✓ DELIVERED · 1 SENTENCE' : undefined} opacity={1 - clamp((t - drop - 1.2) / 0.4)} />
			<TabCount t={t} />
		</>
	);
};

const MONITORS: [number, number][] = [[140, 250], [420, 230], [700, 260], [1220, 260], [1500, 230], [1780, 250]];

const S007: React.FC<ShotProps> = ({t, shot}) => {
	// on the card, the monitors behind her light one after another on the beat (the clip does it in footage)
	const first = beatIndex(barTime(1));
	const lit = Math.max(0, beatIndex(t) - first + 1);
	return (
		<>
			{!hasFootage(shot) &&
				MONITORS.map(([x, y], i) => (
					<div key={i} style={{position: 'absolute', left: x - 120, top: y, width: 240, height: 150, borderRadius: 6, background: i < lit ? C.screen : '#101416', boxShadow: i < lit ? `0 0 60px rgba(207,224,238,${0.5 * (0.6 + 0.4 * pulse(t))})` : 'none', border: '1px solid rgba(216,228,220,0.2)'}} />
				))}
			{MONITORS.slice(0, lit).map(([x, y], i) => (
				<Tag key={i} x={x - 110} y={y + 160} text={`tab ${18 + i}`} size={15} />
			))}
			<TabCount t={t} />
		</>
	);
};

const S008: React.FC<ShotProps> = ({t, lt}) => {
	// windows cascade toward the camera in depth, a terminal under them
	const lines = Array.from({length: 30}).map((_, i) => `$ tool_call browser.open  tab=${19 + i}  ${['ok', 'ok', '200', 'ok'][i % 4]}`);
	const shown = lines.slice(0, Math.floor(lt * 14) + 3);
	return (
		<>
			<Terminal x={96} y={560} w={900} h={420} lines={shown} />
			{Array.from({length: 9}).map((_, i) => {
				const z = (lt * 0.9 + i / 9) % 1;
				const s = lerp(0.35, 1.6, easeIn(z));
				const x = W / 2 + (rnd('c8x', i) - 0.5) * 1400 * s - 300 * s;
				const y = 380 + (rnd('c8y', i) - 0.5) * 500 * s - 180 * s;
				return <BrowserWindow key={i} x={x} y={y} w={600 * s} h={360 * s} title={TITLES[(i + 5) % TITLES.length]} seed={i + 9} opacity={clamp((1 - z) * 4) * clamp(z * 6)} />;
			})}
			<TabCount t={t} />
		</>
	);
};

const S009: React.FC<ShotProps> = ({t, shot}) => {
	// the elevator doors close on the downbeat of bar 5 (on the card: two panels; on the plate: the second still)
	const k = easeIn(clamp((t - barTime(4.25)) / (barTime(5) - barTime(4.25))));
	return (
		<>
			{!hasFootage(shot) && (
				<>
					<div style={{position: 'absolute', left: 560, top: 220, width: 400 * k, height: 760, background: 'linear-gradient(90deg, #9aa0a6, #c9cdd1)', borderRight: '2px solid #7d8388'}} />
					<div style={{position: 'absolute', left: 1360 - 400 * k, top: 220, width: 400 * k, height: 760, background: 'linear-gradient(270deg, #9aa0a6, #c9cdd1)', borderLeft: '2px solid #7d8388'}} />
				</>
			)}
			<div style={{position: 'absolute', left: 890, top: 330, width: 140, height: 170, border: '1.5px solid rgba(11,12,14,0.6)', opacity: 1 - k}} />
			<Tag x={890} y={292} text="USER · AWAY (LUNCH)" dark={false} size={15} />
		</>
	);
};

const S010: React.FC<ShotProps> = ({t, lt}) => {
	// browser windows float in depth around her, in parallax
	return (
		<>
			{Array.from({length: 12}).map((_, i) => {
				const depth = 0.4 + rnd('d10', i) * 0.6;
				const ang = (i / 12) * Math.PI * 2 + lt * 0.08 * (1 - depth);
				const rx = 760 * depth;
				const ry = 330 * depth;
				const x = W / 2 + Math.cos(ang) * rx - 180 * depth;
				const y = 470 + Math.sin(ang) * ry - 110 * depth;
				const born = barTime(5) + i * 0.12;
				return <BrowserWindow key={i} x={x} y={y} w={360 * depth} h={220 * depth} title={TITLES[i % TITLES.length]} seed={i} lines={3} opacity={clamp((t - born) * 5) * (0.55 + 0.45 * depth)} />;
			})}
			<TabCount t={t} />
		</>
	);
};

const TOOLS = ['browser', 'shell', 'calendar', 'mail', 'files', 'payments'];

const S011: React.FC<ShotProps> = ({t}) => {
	// the tools load on the bare desk above her right hand (A_desk_overhead: the keyboard and her hands fill the lower half)
	const from = wordAt(4, 1);
	const first = beatIndex(from);
	return (
		<div style={{position: 'absolute', left: 1240, top: 150, display: 'flex', flexDirection: 'column', gap: 14}}>
			{TOOLS.map((tool, i) => {
				const at = beats[first + i] ?? from;
				const ok = t >= at;
				const k = inAt(t, at - 0.3, 0.3);
				return (
					<div key={tool} style={{display: 'flex', alignItems: 'center', gap: 18, opacity: 0.35 + 0.65 * k, fontFamily: FONT.mono, fontSize: 30, color: C.greenWhite}}>
						<span style={{width: 34, height: 34, borderRadius: 6, border: `2.5px solid ${ok ? C.pass : 'rgba(216,228,220,0.5)'}`, background: ok ? C.pass : 'transparent', color: C.black, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, fontWeight: 700}}>{ok ? '✓' : ''}</span>
						{tool}
						<span style={{color: 'rgba(216,228,220,0.5)', fontSize: 20}}>{ok ? 'loaded' : '…'}</span>
					</div>
				);
			})}
		</div>
	);
};

const PLAN = ['book the flight', 'fix the build', 'draft the deck', 'run every test', 'run every check'];

const S012: React.FC<ShotProps> = ({t}) => {
	// the plan prints line by line on the paper coming out of the printer
	const from = wordNamed(5, /drafted/);
	const first = beatIndex(from);
	const feed = easeOut(clamp((t - wordAt(5, 0)) / 1.2));
	return (
		<div style={{position: 'absolute', left: 1080, top: 700 - 520 * feed, width: 600, height: 520, background: C.flash, boxShadow: '0 20px 60px rgba(0,0,0,0.5)', padding: '38px 44px', fontFamily: FONT.mono, color: C.ink}}>
			<div style={{fontSize: 18, letterSpacing: '0.1em', color: C.ink2}}>PLAN · AGENT_01 · 1 GOAL</div>
			{PLAN.map((line, i) => {
				const at = beats[first + i] ?? from;
				return (
					<div key={line} style={{fontSize: 34, marginTop: 22, opacity: t >= at ? 1 : 0}}>
						<span style={{color: C.terracotta}}>{i + 1}</span> {line}
					</div>
				);
			})}
		</div>
	);
};

const S013: React.FC<ShotProps> = ({t, shot}) => {
	// on "Executing" every monitor on the floor lights at once; a progress bar under the word
	const on = t >= wordAt(6, 0);
	const prog = clamp((t - wordAt(6, 0)) / (shot.t1 - wordAt(6, 0)));
	const cells = [];
	for (let r = 0; r < 5; r++) {
		for (let c = 0; c < 22; c++) {
			const x = 120 + c * 78 + r * 10;
			const y = 620 + r * 64 - Math.abs(c - 11) * 2;
			cells.push(<div key={`${r}-${c}`} style={{position: 'absolute', left: x, top: y, width: 48 - r * 4, height: 26 - r * 2, background: on ? C.screen : '#121618', opacity: on ? 0.55 + 0.4 * rnd('m13', r, c) : 0.6, boxShadow: on ? '0 0 22px rgba(207,224,238,0.5)' : 'none'}} />);
		}
	}
	return (
		<>
			{!hasFootage(shot) && cells}
			<div style={{position: 'absolute', left: 96, top: 470, width: 1100, height: 14, borderRadius: 7, background: 'rgba(216,228,220,0.14)'}}>
				<div style={{width: `${prog * 100}%`, height: 14, borderRadius: 7, background: C.terracotta}} />
			</div>
			<Tag x={96} y={500} text={`EXECUTING · ${Math.round(prog * 100)}% · 5 TASKS · 36 TABS`} size={17} />
		</>
	);
};

export const spec: ChapterSpec = {
	graphics: {s006: S006, s007: S007, s008: S008, s009: S009, s010: S010, s011: S011, s012: S012, s013: S013},
	// s013 on the plate: its front-facing screens switch on together on "Executing", in half a beat
	footage: {s013: (p) => <LitPlate {...p} screens={FLOOR_SCREENS} on={clamp((p.t - wordAt(6, 0)) * 4)} room={p.t >= wordAt(6, 0) ? 0.04 : 0} />},
};
