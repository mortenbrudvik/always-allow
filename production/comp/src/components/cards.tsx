// Cards for the explaining graphics: each shows one thing a line names, readable in one glance
// (Territory Studio's rule: a hero screen makes its point in the ~3 s it's on). Values come from the chapter.
import React from 'react';
import {clamp, easeOut, rnd} from '../lib/ease';
import {C, FONT} from '../lib/theme';

const panel = (dark: boolean): React.CSSProperties => ({
	background: dark ? 'rgba(11,12,14,0.92)' : C.paper,
	border: `1px solid ${dark ? 'rgba(216,228,220,0.25)' : C.hair}`,
	borderRadius: 14,
	boxShadow: dark ? '0 20px 60px rgba(0,0,0,0.5)' : '0 18px 50px rgba(11,12,14,0.16)',
	color: dark ? C.greenWhite : C.ink,
});

const mono = (size: number, extra: React.CSSProperties = {}): React.CSSProperties => ({fontFamily: FONT.mono, fontSize: size, letterSpacing: '0.04em', ...extra});

export const BoardingPass: React.FC<{x: number; y: number; k: number; stamp: number}> = ({x, y, k, stamp}) => (
	<div style={{position: 'absolute', left: x, top: y + (1 - easeOut(k)) * 60, opacity: clamp(k * 2), width: 820, height: 330, ...panel(false), display: 'flex', overflow: 'hidden'}}>
		<div style={{flex: 1, padding: '30px 36px'}}>
			<div style={mono(16, {color: C.ink2})}>BOARDING PASS · BOOKED BY AGENT_01</div>
			<div style={{display: 'flex', alignItems: 'center', gap: 28, marginTop: 22}}>
				<div style={{fontFamily: FONT.sans, fontWeight: 800, fontSize: 104, letterSpacing: '-0.04em'}}>SFO</div>
				<svg width={80} height={30} viewBox="0 0 80 30">
					<path d="M2 15 H70 M58 5 L72 15 L58 25" stroke={C.ink} strokeWidth={4} fill="none" />
				</svg>
				<div style={{fontFamily: FONT.sans, fontWeight: 800, fontSize: 104, letterSpacing: '-0.04em'}}>AUS</div>
			</div>
			<div style={{display: 'flex', gap: 40, marginTop: 20}}>
				{[['SEAT', '2A'], ['GATE', '12'], ['GROUP', '1'], ['PASSENGER', 'YOU']].map(([a, b]) => (
					<div key={a}>
						<div style={mono(14, {color: C.ink2})}>{a}</div>
						<div style={{fontFamily: FONT.sans, fontWeight: 700, fontSize: 34}}>{b}</div>
					</div>
				))}
			</div>
		</div>
		<div style={{width: 170, borderLeft: `2px dashed ${C.hair}`, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', gap: 6}}>
			{Array.from({length: 18}).map((_, i) => (
				<div key={i} style={{width: 110, height: rnd('bp', i) > 0.5 ? 5 : 2, background: C.ink}} />
			))}
		</div>
		{stamp > 0 && (
			<div style={{position: 'absolute', right: 210, top: 40, transform: `rotate(-9deg) scale(${1 + 0.5 * Math.max(0, 1 - stamp * 4)})`, opacity: clamp(stamp * 4), border: `6px solid ${C.pass}`, color: C.pass, borderRadius: 10, padding: '8px 18px', fontFamily: FONT.sans, fontWeight: 900, fontSize: 52}}>CONFIRMED</div>
		)}
	</div>
);

export const CIPanel: React.FC<{x: number; y: number; pass: number}> = ({x, y, pass}) => {
	const checks = ['build', 'lint', 'unit tests', 'e2e', 'deploy preview'];
	return (
		<div style={{position: 'absolute', left: x, top: y, width: 760, ...panel(true), padding: '26px 30px'}}>
			<div style={mono(16, {color: 'rgba(216,228,220,0.6)'})}>CI · main · build #4121</div>
			{checks.map((c, i) => {
				const ok = pass * checks.length > i + 0.2;
				return (
					<div key={c} style={{display: 'flex', alignItems: 'center', gap: 18, marginTop: 16}}>
						<span style={{width: 34, height: 34, borderRadius: 17, background: ok ? C.pass : 'transparent', border: `3px solid ${ok ? C.pass : C.terracotta}`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: C.black, fontWeight: 900, fontSize: 22}}>
							{ok ? '✓' : ''}
						</span>
						<span style={{fontFamily: FONT.sans, fontWeight: 600, fontSize: 32, color: ok ? C.greenWhite : C.terracotta}}>{c}</span>
						<span style={{flex: 1}} />
						<span style={mono(18, {color: 'rgba(216,228,220,0.6)'})}>{ok ? 'passed' : 'failing'}</span>
					</div>
				);
			})}
		</div>
	);
};

export const DeckFan: React.FC<{cx: number; cy: number; k: number}> = ({cx, cy, k}) => {
	const titles = ['LAUNCH', 'WHY NOW', 'THE PLAN', 'THE ASK'];
	return (
		<>
			{titles.map((t, i) => {
				const e = easeOut(clamp(k * 1.4 - i * 0.12));
				const a = (i - 1.5) * 9 * e;
				const dx = (i - 1.5) * 250 * e;
				return (
					<div key={t} style={{position: 'absolute', left: cx - 260 + dx, top: cy - 160 + Math.abs(i - 1.5) * 18 * e, width: 520, height: 292, transform: `rotate(${a}deg)`, ...panel(false), padding: 30, opacity: clamp(e * 3)}}>
						<div style={mono(13, {color: C.ink2})}>{`0${i + 1} / 04`}</div>
						<div style={{fontFamily: FONT.sans, fontWeight: 800, fontSize: 58, letterSpacing: '-0.03em', marginTop: 16}}>{t}</div>
						<div style={{position: 'absolute', left: 30, bottom: 30, width: 150, height: 8, background: C.terracotta}} />
					</div>
				);
			})}
		</>
	);
};

export const TestGrid: React.FC<{x: number; y: number; n: number; done: number; cols?: number; label?: string}> = ({x, y, n, done, cols = 18, label}) => (
	<div style={{position: 'absolute', left: x, top: y}}>
		{label && <div style={mono(17, {color: 'rgba(216,228,220,0.75)', marginBottom: 10})}>{label}</div>}
		<div style={{display: 'grid', gridTemplateColumns: `repeat(${cols}, 18px)`, gap: 5}}>
			{Array.from({length: n}).map((_, i) => (
				<div key={i} style={{width: 18, height: 18, borderRadius: 3, background: i < done ? C.pass : 'rgba(216,228,220,0.14)'}} />
			))}
		</div>
		<div style={mono(20, {color: C.greenWhite, marginTop: 12})}>{`${Math.min(n, Math.round(done))}/${n} passed`}</div>
	</div>
);

export const Chips: React.FC<{x: number; y: number; items: string[]; done: number; dark?: boolean}> = ({x, y, items, done, dark = true}) => (
	<div style={{position: 'absolute', left: x, top: y, display: 'flex', flexDirection: 'column', gap: 12}}>
		{items.map((it, i) => {
			const ok = i < done;
			return (
				<div key={it} style={{display: 'flex', alignItems: 'center', gap: 14, height: 54, padding: '0 20px', borderRadius: 27, ...panel(dark), boxShadow: 'none', opacity: 0.55 + (ok ? 0.45 : 0)}}>
					<span style={{fontFamily: FONT.sans, fontWeight: 600, fontSize: 26, minWidth: 110}}>{it}</span>
					<span style={mono(18, {color: ok ? C.pass : 'rgba(216,228,220,0.5)'})}>{ok ? '✓ DONE' : '· running'}</span>
				</div>
			);
		})}
	</div>
);

export const Radios: React.FC<{x: number; y: number; options: string[]; selected?: number; dark?: boolean}> = ({x, y, options, selected = -1, dark = true}) => (
	<div style={{position: 'absolute', left: x, top: y, display: 'flex', gap: 34}}>
		{options.map((o, i) => (
			<div key={o} style={{display: 'flex', alignItems: 'center', gap: 12, fontFamily: FONT.sans, fontWeight: 600, fontSize: 34, color: dark ? C.greenWhite : C.ink}}>
				<span style={{width: 34, height: 34, borderRadius: 17, border: `3px solid ${dark ? C.greenWhite : C.ink}`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
					{i === selected && <span style={{width: 16, height: 16, borderRadius: 8, background: C.terracotta}} />}
				</span>
				{o}
			</div>
		))}
	</div>
);

const DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];

/** A week view. `deleted` of the weekday meetings have gone (a clear lane opens); `claimed` weekend blocks are hers. */
export const Calendar: React.FC<{x: number; y: number; w: number; h: number; deleted?: number; claimed?: number; dark?: boolean; highlightWeekend?: number}> = ({
	x, y, w, h, deleted = 0, claimed = 0, dark = true, highlightWeekend = 0,
}) => {
	const colW = w / 7;
	const hours = 10;
	const rowH = (h - 50) / hours;
	const meetings: {d: number; r: number; len: number; name: string}[] = [];
	const names = ['sync', '1:1', 'standup', 'review', 'planning', 'call', 'offsite prep', 'interview', 'demo', 'retro'];
	for (let d = 0; d < 5; d++) {
		for (let r = 0; r < hours; r++) {
			if (rnd('cal', d, r) > 0.45 && r !== 4) {
				meetings.push({d, r, len: rnd('len', d, r) > 0.7 ? 2 : 1, name: names[Math.floor(rnd('nm', d, r) * names.length)]});
			}
		}
	}
	// the meetings in the middle rows go first, so a clear lane (the road) opens through the week
	const order = meetings.map((m, i) => ({m, k: (m.r >= 3 && m.r <= 5 ? 0 : 1) + rnd('del', i)})).sort((a, b) => a.k - b.k);
	return (
		<div style={{position: 'absolute', left: x, top: y, width: w, height: h, ...panel(dark), overflow: 'hidden'}}>
			<div style={{display: 'flex', height: 50, borderBottom: `1px solid ${dark ? 'rgba(216,228,220,0.18)' : C.hair}`}}>
				{DAYS.map((d, i) => (
					<div key={d} style={{width: colW, ...mono(17), display: 'flex', alignItems: 'center', justifyContent: 'center', color: i >= 5 && highlightWeekend ? C.terracotta : undefined}}>
						{d}
					</div>
				))}
			</div>
			{order.map(({m}, i) => {
				if (i < deleted) {
					return null;
				}
				return (
					<div key={`${m.d}-${m.r}`} style={{position: 'absolute', left: m.d * colW + 6, top: 50 + m.r * rowH + 4, width: colW - 12, height: rowH * m.len - 8, borderRadius: 6, background: dark ? 'rgba(77,126,168,0.55)' : 'rgba(31,79,214,0.18)', borderLeft: `4px solid ${dark ? C.monitorBlue2 : C.cobalt}`, ...mono(14), padding: '4px 8px', overflow: 'hidden', whiteSpace: 'nowrap'}}>
						{m.name}
					</div>
				);
			})}
			{Array.from({length: Math.floor(claimed)}).map((_, i) => {
				const d = 5 + (i % 2);
				const r = Math.floor(i / 2);
				return (
					<div key={`c${i}`} style={{position: 'absolute', left: d * colW + 6, top: 50 + r * rowH + 4, width: colW - 12, height: rowH - 8, borderRadius: 6, background: 'rgba(201,100,66,0.8)', ...mono(14, {color: C.paper}), padding: '4px 8px'}}>
						agent_01
					</div>
				);
			})}
		</div>
	);
};

export const JobCard: React.FC<{x: number; y: number; opacity?: number}> = ({x, y, opacity = 1}) => (
	<div style={{position: 'absolute', left: x, top: y, width: 520, ...panel(true), padding: '26px 30px', opacity}}>
		<div style={mono(15, {color: 'rgba(216,228,220,0.6)'})}>ROLE · FULL TIME</div>
		<div style={{fontFamily: FONT.sans, fontWeight: 800, fontSize: 56, letterSpacing: '-0.03em', marginTop: 8}}>YOUR JOB</div>
		<div style={{display: 'flex', gap: 10, marginTop: 14, flexWrap: 'wrap'}}>
			{['meetings', 'email', 'decks', 'status updates'].map((t) => (
				<span key={t} style={{...mono(15), padding: '4px 10px', border: '1px solid rgba(216,228,220,0.35)', borderRadius: 14}}>{t}</span>
			))}
		</div>
	</div>
);

export const Reticle: React.FC<{x: number; y: number; r: number; opacity?: number; colour?: string}> = ({x, y, r, opacity = 1, colour = C.terracotta}) => (
	<svg width={r * 2 + 20} height={r * 2 + 20} style={{position: 'absolute', left: x - r - 10, top: y - r - 10, opacity, overflow: 'visible'}}>
		<g transform={`translate(${r + 10} ${r + 10})`} stroke={colour} strokeWidth={3} fill="none">
			<circle r={r} />
			<circle r={r * 0.18} fill={colour} stroke="none" />
			{[0, 90, 180, 270].map((a) => (
				<line key={a} x1={0} y1={-r - 8} x2={0} y2={-r * 0.55} transform={`rotate(${a})`} />
			))}
		</g>
	</svg>
);

export const AccessBadge: React.FC<{x: number; y: number; k: number; dark?: boolean; scale?: number}> = ({x, y, k, dark = false, scale = 1}) => (
	<div style={{position: 'absolute', left: x, top: y, width: 560, ...panel(dark), padding: '24px 28px', opacity: clamp(k * 2), transform: `translateY(${(1 - easeOut(k)) * 30}px) scale(${scale})`, transformOrigin: 'top left'}}>
		{[['ACCESS', 'ALL'], ['SCOPE', '*'], ['EXPIRES', 'NEVER'], ['GRANTED BY', 'auto mode']].map(([a, b], i) => (
			<div key={a} style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', padding: '8px 0', borderBottom: i < 3 ? `1px solid ${dark ? 'rgba(216,228,220,0.18)' : C.hair}` : 'none', opacity: clamp(k * 4 - i * 0.5)}}>
				<span style={mono(18, {color: dark ? 'rgba(216,228,220,0.6)' : C.ink2})}>{a}</span>
				<span style={{fontFamily: FONT.sans, fontWeight: 800, fontSize: 36, color: i === 1 ? C.terracotta : undefined}}>{b}</span>
			</div>
		))}
	</div>
);

/** A face embedding as a strip of numbers; `decay` 0-1 takes them to zero, left to right. */
export const Embedding: React.FC<{x: number; y: number; decay: number; n?: number; dark?: boolean}> = ({x, y, decay, n = 16, dark = false}) => (
	<div style={{position: 'absolute', left: x, top: y, ...mono(18), color: dark ? C.greenWhite : C.ink, background: dark ? 'rgba(11,12,14,0.8)' : 'rgba(244,244,241,0.9)', padding: '10px 14px', border: `1px solid ${dark ? 'rgba(216,228,220,0.3)' : C.hair}`}}>
		<div style={mono(13, {opacity: 0.7, marginBottom: 6})}>FACE_ID · 128-d embedding (first {n})</div>
		<div style={{display: 'grid', gridTemplateColumns: 'repeat(8, 76px)', rowGap: 4}}>
			{Array.from({length: n}).map((_, i) => {
				const gone = decay * (n + 4) > i;
				const v = (rnd('emb', i) * 2 - 1).toFixed(3);
				return (
					<span key={i} style={{color: gone ? C.terracotta : undefined}}>
						{gone ? '0.000' : v.startsWith('-') ? v : ` ${v}`}
					</span>
				);
			})}
		</div>
	</div>
);

export const TodoList: React.FC<{x: number; y: number; items: string[]; done: number; dark?: boolean; size?: number}> = ({x, y, items, done, dark = true, size = 30}) => (
	<div style={{position: 'absolute', left: x, top: y, ...panel(dark), padding: '22px 28px', minWidth: 560}}>
		{items.map((it, i) => {
			const ok = i < done;
			const cur = i === Math.floor(done);
			return (
				<div key={it} style={{display: 'flex', alignItems: 'center', gap: 16, margin: '10px 0', fontFamily: FONT.sans, fontWeight: cur ? 700 : 500, fontSize: size, opacity: ok ? 0.5 : 1, textDecoration: ok ? 'line-through' : 'none'}}>
					<span style={{width: size * 0.9, height: size * 0.9, borderRadius: 6, border: `3px solid ${cur ? C.terracotta : dark ? C.greenWhite : C.ink}`, background: ok ? C.pass : 'transparent'}} />
					{it}
				</div>
			);
		})}
	</div>
);

export const JsonBlock: React.FC<{x: number; y: number; lines: string[]; dark?: boolean; size?: number}> = ({x, y, lines, dark = true, size = 26}) => (
	<div style={{position: 'absolute', left: x, top: y, ...panel(dark), padding: '20px 26px', ...mono(size), whiteSpace: 'pre', lineHeight: 1.45}}>
		{lines.map((l, i) => (
			<div key={i} style={{color: /true|ok|✓/.test(l) ? C.pass : undefined}}>{l}</div>
		))}
	</div>
);

export interface ReceiptLine {
	left: string;
	right?: string;
	bold?: boolean;
	rule?: boolean;
}

/** A thermal receipt printing: `printed` lines have come out of the printer, the paper feeding upward. */
export const Receipt: React.FC<{x: number; y: number; w: number; lines: ReceiptLine[]; printed: number; maxVisible?: number; stamp?: number}> = ({x, y, w, lines, printed, maxVisible = 30, stamp = 0}) => {
	const n = Math.min(lines.length, Math.floor(printed));
	const first = Math.max(0, n - maxVisible);
	const shown = lines.slice(first, n);
	const lh = 38;
	return (
		<div style={{position: 'absolute', left: x, top: y, width: w, overflow: 'hidden'}}>
			<div style={{background: '#faf8f2', color: '#1c1b19', padding: '26px 30px 40px', boxShadow: '0 30px 80px rgba(0,0,0,0.45)', ...mono(22), minHeight: shown.length * lh, position: 'relative', clipPath: 'polygon(0 0, 100% 0, 100% 100%, 97% 99%, 94% 100%, 91% 99%, 88% 100%, 85% 99%, 82% 100%, 79% 99%, 76% 100%, 73% 99%, 70% 100%, 67% 99%, 64% 100%, 61% 99%, 58% 100%, 55% 99%, 52% 100%, 49% 99%, 46% 100%, 43% 99%, 40% 100%, 37% 99%, 34% 100%, 31% 99%, 28% 100%, 25% 99%, 22% 100%, 19% 99%, 16% 100%, 13% 99%, 10% 100%, 7% 99%, 4% 100%, 0 99%)'}}>
				{shown.map((l, i) =>
					l.rule ? (
						<div key={i + first} style={{height: lh, borderBottom: '2px dashed #1c1b19', marginBottom: 6, opacity: 0.6}} />
					) : (
						<div key={i + first} style={{height: lh, display: 'flex', justifyContent: 'space-between', gap: 20, fontWeight: l.bold ? 700 : 400, fontSize: l.bold ? 26 : 22}}>
							<span style={{whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>{l.left}</span>
							{l.right && <span style={{whiteSpace: 'nowrap'}}>{l.right}</span>}
						</div>
					),
				)}
				{stamp > 0 && (
					<div style={{position: 'absolute', right: 30, bottom: 30, transform: `rotate(-10deg) scale(${1 + 0.4 * Math.max(0, 1 - stamp * 4)})`, opacity: clamp(stamp * 4), border: `5px solid ${C.terracotta}`, color: C.terracotta, borderRadius: 8, padding: '6px 14px', fontFamily: FONT.sans, fontWeight: 900, fontSize: 40, mixBlendMode: 'multiply'}}>TASK COMPLETE</div>
				)}
			</div>
		</div>
	);
};
