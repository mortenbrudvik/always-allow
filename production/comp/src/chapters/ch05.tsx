// ch05: Always allow I (77.95-107.73 s), shots s029-s043. Hook 1 on the white stage: seven of her in a row, point
// moves on "keys" and "bow", the blink; then chant 1 (tool call, result, next step) and DONE with its echoes.
// Edit only this file for this chapter (ANIMATION_GUIDE.md).
import React from 'react';
import {Gauge, ProgressBars} from '../components/charts';
import {JsonBlock, TodoList} from '../components/cards';
import {Tag, Terminal} from '../components/ui';
import {clamp, easeOut, lerp} from '../lib/ease';
import {C, FONT, H, W} from '../lib/theme';
import {barTime} from '../lib/time';
import type {ChapterSpec, ShotProps, Slot} from './types';
import {inAt, wordAt, wordNamed} from './util';

/** Seven of her in a row, the Agent at the centre (index 3). */
export const row7 = (h = 600, y = 960, gap = 200): Slot[] =>
	Array.from({length: 7}).map((_, i) => ({x: W / 2 + (i - 3) * gap, y, h, label: i === 3 ? 'AGENT_01' : `INSTANCE_${String(i < 3 ? i + 1 : i).padStart(4, '0')}`}));

const rows3 = (t: number): Slot[] => {
	const out: Slot[] = [...row7(560, 990)];
	const specs = [
		{n: 9, y: 800, h: 400, gap: 150, at: barTime(37.5)},
		{n: 11, y: 690, h: 290, gap: 115, at: barTime(37.75)},
	];
	let id = 7;
	for (const r of specs) {
		if (t < r.at) {
			continue;
		}
		for (let i = 0; i < r.n; i++) {
			out.push({x: W / 2 + (i - (r.n - 1) / 2) * r.gap, y: r.y, h: r.h, label: `INSTANCE_${String(id++).padStart(4, '0')}`});
		}
	}
	return out;
};

const Labels: React.FC<{slots: Slot[]; colour?: string; size?: number}> = ({slots, colour = 'rgba(11,12,14,0.7)', size = 14}) => (
	<>
		{slots.map((s, i) => (
			<div key={i} style={{position: 'absolute', left: s.x, top: s.y - s.h - 26, transform: 'translateX(-50%)', fontFamily: FONT.mono, fontSize: size, letterSpacing: '0.06em', color: s.label === 'AGENT_01' ? C.terracotta : colour, whiteSpace: 'nowrap'}}>
				{s.label}
			</div>
		))}
	</>
);

const S029: React.FC<ShotProps> = () => <Labels slots={row7()} />;

const S030: React.FC<ShotProps> = ({t}) => {
	// palms up in unison; a masked key lands in every palm on "keys"
	const keys = wordNamed(20, /keys/);
	const k = easeOut(clamp((t - keys + 0.15) / 0.3));
	const slots = row7(1150, 1400, 360).slice(1, 6);
	return (
		<>
			{slots.map((s, i) => (
				<div key={i} style={{position: 'absolute', left: s.x - 30, top: lerp(360, 640, k), opacity: k, padding: '6px 10px', background: C.ink, color: C.greenWhite, fontFamily: FONT.mono, fontSize: 18, borderRadius: 4, transform: 'translateX(-50%)', whiteSpace: 'nowrap'}}>
					API_KEY ••••••••
				</div>
			))}
		</>
	);
};

const S031: React.FC<ShotProps> = ({t}) => {
	const n = rows3(t).length;
	return (
		<>
			<Labels slots={rows3(t).slice(0, 7)} size={12} />
			<Tag x={96} y={560} text={`PROCESSES ${n}`} dark={false} size={26} />
		</>
	);
};

const S032: React.FC<ShotProps> = () => <Gauge x={96} y={660} value={0} label="EFFORT" />;

const S033: React.FC<ShotProps> = () => <Labels slots={row7()} />;

const S034: React.FC<ShotProps> = ({t}) => {
	// "how?" pops up beside her and is redacted on "how"
	const how = wordNamed(24, /how/);
	const k = inAt(t, wordAt(24, 0), 0.2);
	const red = clamp((t - how) / 0.12);
	return (
		<div style={{position: 'absolute', left: 1100, top: 640, opacity: k, padding: '14px 22px', background: C.paper, border: `1px solid ${C.hair}`, borderRadius: 10, boxShadow: '0 12px 30px rgba(11,12,14,0.15)', fontFamily: FONT.mono, fontSize: 30, color: C.ink}}>
			<span>how?</span>
			<div style={{position: 'absolute', left: 16, top: 12, height: 40, width: 100 * red, background: C.ink}} />
			<div style={{fontSize: 15, color: C.ink2, marginTop: 6}}>{red >= 1 ? 'REDACTED' : 'explain your steps'}</div>
		</div>
	);
};

const S035: React.FC<ShotProps> = ({t}) => {
	// a progress bar over every head: 0 % before the blink, 100 % after it
	const blink = wordNamed(25, /blink/);
	const k = t >= blink + 3 / 24 ? 1 : clamp((t - 88.3) / 3) * 0.2;
	return (
		<>
			<ProgressBars xs={row7().map((s) => s.x)} y={330} k={k} w={120} />
			<Labels slots={row7()} />
		</>
	);
};

const TOOL_LINES = ['{"tool": "browser.open", "args": {"url": "/flights"}}', '{"tool": "shell.run", "args": {"cmd": "npm test"}}', '{"tool": "mail.send", "args": {"to": "team"}}', '{"tool": "files.write", "args": {"path": "deck.key"}}', '{"tool": "calendar.move", "args": {"event": "1:1"}}', '{"tool": "pay.charge", "args": {"usd": 1240}}'];

const S037: React.FC<ShotProps> = ({lt}) => (
	<div style={{opacity: 0.8}}>
		<Terminal x={60} y={120} w={W - 120} h={H - 220} lines={Array.from({length: 40}).map((_, i) => TOOL_LINES[i % TOOL_LINES.length]).slice(0, 8 + Math.floor(lt * 30))} fontSize={22} title="agent_01 — tool calls" />
	</div>
);

const RING_TOOLS = ['browser.open', 'shell.run', 'mail.send', 'files.write', 'calendar.move', 'pay.charge', 'docs.edit', 'ci.rerun', 'slack.post', 'deploy.preview', 'search.web', 'db.query'];

const S038: React.FC<ShotProps> = ({lt}) => (
	<>
		{RING_TOOLS.map((tool, i) => {
			const a = (i / 12) * Math.PI * 2 + lt * 0.05;
			return (
				<div key={tool} style={{position: 'absolute', left: W / 2 + Math.cos(a) * 390, top: H / 2 + Math.sin(a) * 390, transform: 'translate(-50%, -50%)', fontFamily: FONT.mono, fontSize: 19, color: C.ink, background: 'rgba(244,244,241,0.9)', padding: '4px 8px', opacity: inAt(lt, i * 0.06, 0.2)}}>
					{tool}
				</div>
			);
		})}
	</>
);

const S039: React.FC<ShotProps> = ({t}) => <div style={{opacity: inAt(t, wordAt(28, 0), 0.15)}}><JsonBlock x={1360} y={720} lines={['{', '  "ok": true,', '  "steps": 5', '}']} dark={false} size={28} /></div>;

const STEPS = ['book the flight', 'fix the build', 'draft the deck', 'run every test', 'run every check'];

const S041: React.FC<ShotProps> = ({t}) => <TodoList x={660} y={690} items={STEPS} done={t >= wordAt(29, 0) ? 5 : 4} dark={false} size={30} />;

const S042: React.FC<ShotProps> = ({lt}) => (
	<div style={{position: 'absolute', left: 96, top: 200 - lt * 60, fontFamily: FONT.mono, fontSize: 26, lineHeight: 1.7, color: C.ink, opacity: 0.8}}>
		{Array.from({length: 30}).map((_, i) => (
			<div key={i}>{`step ${String(i + 6).padStart(3, '0')} · ${STEPS[i % 5]} · ok`}</div>
		))}
	</div>
);

const S043: React.FC<ShotProps> = ({t}) => {
	// DONE. with its echoes (the instrumental's echo taps, about every half second) and a checkmark
	const d0 = wordAt(30, 0);
	const echoes = [0.45, 0.9, 1.35, 1.8];
	const check = clamp((t - d0 - 0.2) / 0.5);
	return (
		<svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
			{echoes.map((e, i) =>
				t >= d0 + e ? (
					<text key={i} x={W / 2} y={560 + (i + 1) * 70} textAnchor="middle" fontFamily={FONT.sans} fontWeight={900} fontSize={300} letterSpacing="-0.045em" fill="none" stroke={C.ink} strokeWidth={2} opacity={0.5 - i * 0.1}>
						DONE.
					</text>
				) : null,
			)}
			<path d="M 1540 300 l 60 64 l 130 -150" fill="none" stroke={C.terracotta} strokeWidth={16} strokeLinecap="round" strokeLinejoin="round" strokeDasharray="330" strokeDashoffset={330 * (1 - check)} />
		</svg>
	);
};

export const spec: ChapterSpec = {
	graphics: {s029: S029, s030: S030, s031: S031, s032: S032, s033: S033, s034: S034, s035: S035, s037: S037, s038: S038, s039: S039, s041: S041, s042: S042, s043: S043},
	formation: {
		s029: () => row7(),
		s030: () => row7(1150, 1400, 360),
		s031: (p) => rows3(p.t),
		s033: () => row7(),
		s035: () => row7(),
		s036: () => row7(),
		s037: () => row7(),
	},
};
