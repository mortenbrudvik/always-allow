// Charts, counters and scene-wide graphics. The numbers that are claims (97 %, 13.6 %, 17 % to 5 %) are
// the sourced ones in STYLE_BIBLE.md, drawn with their source line; the rest are the story's own values.
import React from 'react';
import {Img} from 'remotion';
import {mediaUrl} from '../lib/media';
import {clamp, easeInOut, easeOut, lerp, rnd} from '../lib/ease';
import {C, FONT, H, W} from '../lib/theme';
import {Dialog} from './ui';

const mono = (size: number, extra: React.CSSProperties = {}): React.CSSProperties => ({fontFamily: FONT.mono, fontSize: size, letterSpacing: '0.04em', ...extra});

/** The approval-fatigue line: dangerous commands caught by human review, falling as prompts pile up. */
export const FatigueChart: React.FC<{x: number; y: number; w: number; h: number; k: number; dark?: boolean}> = ({x, y, w, h, k, dark = true}) => {
	const fg = dark ? C.greenWhite : C.ink;
	const soft = dark ? 'rgba(216,228,220,0.45)' : 'rgba(11,12,14,0.4)';
	// "about 17% early in a session, dropping to about 5% after 50 or more prior prompts" (Anthropic, 7 Aug 2026)
	const pts: [number, number][] = [[0, 17], [8, 15.5], [16, 12.5], [26, 9.5], [36, 7.2], [50, 5], [60, 5]];
	const X = (p: number) => x + 90 + (p / 60) * (w - 130);
	const Y = (v: number) => y + h - 60 - (v / 20) * (h - 110);
	const shown = easeInOut(clamp(k * 1.25));
	const upto = shown * 60;
	const at = (p: number) => {
		for (let i = 0; i < pts.length - 1; i++) {
			const [p0, v0] = pts[i];
			const [p1, v1] = pts[i + 1];
			if (p <= p1) {
				return lerp(v0, v1, (p - p0) / (p1 - p0));
			}
		}
		return pts[pts.length - 1][1];
	};
	const vis: [number, number][] = [...pts.filter(([q]) => q <= upto), [upto, at(upto)]];
	const path = vis.map(([q, v], i) => `${i ? 'L' : 'M'} ${X(q)} ${Y(v)}`).join(' ');
	return (
		<svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
			<text x={x} y={y - 18} fill={fg} fontFamily={FONT.sans} fontWeight={700} fontSize={40}>Dangerous commands caught by human review</text>
			{[0, 5, 10, 15, 20].map((v) => (
				<g key={v}>
					<line x1={X(0)} x2={X(60)} y1={Y(v)} y2={Y(v)} stroke={soft} strokeWidth={1} strokeDasharray="4 8" />
					<text x={x + 70} y={Y(v) + 7} fill={soft} fontFamily={FONT.mono} fontSize={18} textAnchor="end">{`${v}%`}</text>
				</g>
			))}
			{[0, 10, 20, 30, 40, 50].map((p) => (
				<text key={p} x={X(p)} y={y + h - 26} fill={soft} fontFamily={FONT.mono} fontSize={18} textAnchor="middle">{p === 50 ? '50+' : p}</text>
			))}
			<text x={X(60)} y={y + h + 8} fill={soft} fontFamily={FONT.mono} fontSize={17} textAnchor="end">permission prompts already seen in the session</text>
			<path d={path} fill="none" stroke={C.terracotta} strokeWidth={6} strokeLinejoin="round" strokeLinecap="round" />
			{k > 0.15 && <text x={X(0) + 14} y={Y(17) - 16} fill={fg} fontFamily={FONT.sans} fontWeight={800} fontSize={44}>~17%</text>}
			{k > 0.8 && <text x={X(50) - 10} y={Y(5) - 22} fill={C.terracotta} fontFamily={FONT.sans} fontWeight={800} fontSize={54} opacity={clamp((k - 0.8) * 6)}>~5%</text>}
			<text x={x} y={y + h + 44} fill={soft} fontFamily={FONT.mono} fontSize={16}>Source: Anthropic, “Auto mode is now the default in Claude Code”, 7 Aug 2026 (1,053 testers)</text>
		</svg>
	);
};

export const BarCompare: React.FC<{x: number; y: number; w: number; items: {label: string; value: number; accent?: boolean}[]; k: number; max?: number; source?: string; dark?: boolean; unit?: string}> = ({
	x, y, w, items, k, max = 100, source, dark = true, unit = '%',
}) => {
	const fg = dark ? C.greenWhite : C.ink;
	return (
		<div style={{position: 'absolute', left: x, top: y, width: w}}>
			{items.map((it, i) => {
				const e = easeOut(clamp(k * 1.6 - i * 0.25));
				return (
					<div key={it.label} style={{marginBottom: 26}}>
						<div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', color: fg}}>
							<span style={{fontFamily: FONT.sans, fontWeight: 600, fontSize: 30}}>{it.label}</span>
							<span style={{fontFamily: FONT.sans, fontWeight: 900, fontSize: 76, letterSpacing: '-0.03em', color: it.accent ? C.terracotta : fg}}>{`${(it.value * e).toFixed(it.value % 1 ? 1 : 0)}${unit}`}</span>
						</div>
						<div style={{height: 22, background: dark ? 'rgba(216,228,220,0.12)' : 'rgba(11,12,14,0.08)', borderRadius: 11}}>
							<div style={{height: 22, width: `${(it.value / max) * 100 * e}%`, background: it.accent ? C.terracotta : fg, borderRadius: 11}} />
						</div>
					</div>
				);
			})}
			{source && <div style={mono(16, {color: dark ? 'rgba(216,228,220,0.55)' : C.ink2})}>{source}</div>}
		</div>
	);
};

export const BigNumber: React.FC<{x: number; y: number; value: string; label: string; dark?: boolean; size?: number; accent?: boolean; align?: 'left' | 'right'}> = ({x, y, value, label, dark = true, size = 150, accent = false, align = 'left'}) => (
	<div style={{position: 'absolute', left: x, top: y, textAlign: align, color: dark ? C.greenWhite : C.ink}}>
		<div style={mono(20, {opacity: 0.7})}>{label}</div>
		<div style={{fontFamily: FONT.sans, fontWeight: 900, fontSize: size, letterSpacing: '-0.04em', lineHeight: 1, color: accent ? C.terracotta : undefined, fontVariantNumeric: 'tabular-nums'}}>{value}</div>
	</div>
);

/** An ECG trace across the frame that flattens (`flat` 0-1) and turns into a filling progress bar (`fill` 0-1). */
export const Heartbeat: React.FC<{y: number; t: number; flat: number; fill: number}> = ({y, t, flat, fill}) => {
	const pts: string[] = [];
	for (let x = 0; x <= W; x += 6) {
		const ph = ((x / 360 - t * 1.2) % 1 + 1) % 1;
		let v = 0;
		if (ph > 0.42 && ph < 0.46) {
			v = -40;
		} else if (ph >= 0.46 && ph < 0.5) {
			v = 160;
		} else if (ph >= 0.5 && ph < 0.54) {
			v = -70;
		} else if (ph >= 0.6 && ph < 0.7) {
			v = -18 * Math.sin(((ph - 0.6) / 0.1) * Math.PI);
		}
		const damp = x / W < flat ? 0 : 1;
		pts.push(`${x},${y - v * damp * (1 - flat)}`);
	}
	return (
		<svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
			<polyline points={pts.join(' ')} fill="none" stroke={C.greenWhite} strokeWidth={4} strokeLinejoin="round" opacity={1 - fill * 0.6} />
			{fill > 0 && (
				<>
					<rect x={160} y={y - 16} width={W - 320} height={32} rx={16} fill="rgba(216,228,220,0.12)" />
					<rect x={160} y={y - 16} width={(W - 320) * fill} height={32} rx={16} fill={C.terracotta} />
					<text x={W - 160} y={y + 70} fill={C.greenWhite} fontFamily={FONT.mono} fontSize={26} textAnchor="end">{`${Math.round(fill * 100)}%`}</text>
				</>
			)}
		</svg>
	);
};

export const StackedBar: React.FC<{x: number; y: number; w: number; k: number; parts: [string, number][]}> = ({x, y, w, k, parts}) => {
	const total = parts.reduce((s, [, v]) => s + v, 0);
	const shades = [C.monitorBlue2, C.glassTeal, C.steel, C.terracotta];
	return (
		<div style={{position: 'absolute', left: x, top: y, width: w}}>
			<div style={mono(18, {color: 'rgba(216,228,220,0.7)', marginBottom: 12})}>YOUR HOURS · A TYPICAL WEEK</div>
			<div style={{display: 'flex', height: 46, borderRadius: 6, overflow: 'hidden'}}>
				{parts.map(([name, v], i) => {
					const share = (v / total) * clamp(k * 1.5 - i * 0.2);
					return <div key={name} style={{width: `${share * 100}%`, background: shades[i % shades.length]}} />;
				})}
			</div>
			<div style={{display: 'flex', gap: 24, marginTop: 12, flexWrap: 'wrap'}}>
				{parts.map(([name, v], i) => (
					<span key={name} style={mono(18, {color: C.greenWhite, opacity: clamp(k * 3 - i * 0.4)})}>
						<span style={{color: shades[i % shades.length]}}>■</span> {name} {v} h
					</span>
				))}
			</div>
		</div>
	);
};

export const MorningTimeline: React.FC<{x: number; y: number; w: number; k: number}> = ({x, y, w, k}) => {
	const slots = ['06:30', '07:00', '07:30', '08:00', '08:30', '09:00'];
	return (
		<div style={{position: 'absolute', left: x, top: y, width: w}}>
			<div style={{display: 'flex', justifyContent: 'space-between', ...mono(17, {color: 'rgba(216,228,220,0.7)'})}}>
				{slots.map((s) => (
					<span key={s}>{s}</span>
				))}
			</div>
			<div style={{position: 'relative', height: 40, marginTop: 10, background: 'rgba(216,228,220,0.1)', borderRadius: 6}}>
				{[0, 1, 2, 3, 4].map((i) => (
					<div key={i} style={{position: 'absolute', left: `${i * 20 + 1}%`, width: '18%', top: 4, bottom: 4, borderRadius: 4, background: C.terracotta, opacity: clamp(k * 5 - i)}} />
				))}
			</div>
			<div style={mono(16, {color: C.terracotta, marginTop: 10, opacity: clamp(k * 3 - 2)})}>claimed by agent_01</div>
		</div>
	);
};

export const Candles: React.FC<{x: number; y: number; w: number; h: number; t: number; seed?: string}> = ({x, y, w, h, t, seed = 'c'}) => {
	const n = 36;
	const bw = w / n;
	let v = 0.5;
	const bars = [];
	const shift = Math.floor(t * 4);
	for (let i = 0; i < n; i++) {
		const d = (rnd(seed, i + shift) - 0.48) * 0.12;
		const o = v;
		v = clamp(v + d, 0.1, 0.9);
		const hi = Math.max(o, v) + rnd(seed, 'h', i + shift) * 0.04;
		const lo = Math.min(o, v) - rnd(seed, 'l', i + shift) * 0.04;
		const up = v >= o;
		bars.push(
			<g key={i}>
				<line x1={x + i * bw + bw / 2} x2={x + i * bw + bw / 2} y1={y + h * (1 - hi)} y2={y + h * (1 - lo)} stroke={up ? C.pass : C.terracotta} strokeWidth={2} />
				<rect x={x + i * bw + 2} y={y + h * (1 - Math.max(o, v))} width={bw - 4} height={Math.max(2, h * Math.abs(v - o))} fill={up ? C.pass : C.terracotta} />
			</g>,
		);
	}
	return <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>{bars}</svg>;
};

export const CodeLines: React.FC<{x: number; y: number; w: number; lines: number; t: number; seed?: string}> = ({x, y, w, lines, t, seed = 'code'}) => {
	const scroll = Math.floor(t * 6);
	const kw = ['const', 'await', 'return', 'if', 'for', 'fn', 'let', 'export'];
	return (
		<div style={{position: 'absolute', left: x, top: y, width: w, ...mono(18), lineHeight: 1.5, color: C.greenWhite, background: 'rgba(11,12,14,0.85)', padding: 16, borderRadius: 8, border: '1px solid rgba(216,228,220,0.2)'}}>
			{Array.from({length: lines}).map((_, i) => {
				const r = i + scroll;
				const ind = Math.floor(rnd(seed, 'i', r) * 3);
				const k = kw[Math.floor(rnd(seed, 'k', r) * kw.length)];
				return (
					<div key={i} style={{whiteSpace: 'pre', opacity: 0.65 + 0.35 * rnd(seed, 'o', r)}}>
						<span style={{color: 'rgba(216,228,220,0.35)'}}>{String(r + 1).padStart(3, ' ')} </span>
						{'  '.repeat(ind)}
						<span style={{color: C.terracotta}}>{k}</span>
						{` ${'x'.repeat(3 + Math.floor(rnd(seed, 'a', r) * 12))}(${'y'.repeat(Math.floor(rnd(seed, 'b', r) * 6))})`}
					</div>
				);
			})}
		</div>
	);
};

export const SpinnerGrid: React.FC<{k: number; t: number; dark?: boolean; cols?: number; rows?: number}> = ({k, t, dark = true, cols = 24, rows = 12}) => {
	const cells: React.ReactNode[] = [];
	const cw = (W - 200) / cols;
	const ch = (H - 280) / rows;
	for (let r = 0; r < rows; r++) {
		for (let c = 0; c < cols; c++) {
			const i = r * cols + c;
			const doneAt = rnd('spin', i);
			const done = k > doneAt;
			const cx = 100 + c * cw + cw / 2;
			const cy = 170 + r * ch + ch / 2;
			cells.push(
				done ? (
					<path key={i} d={`M ${cx - 10} ${cy} l 7 8 l 14 -16`} stroke={C.pass} strokeWidth={4} fill="none" strokeLinecap="round" />
				) : (
					<circle key={i} cx={cx} cy={cy} r={12} fill="none" stroke={dark ? C.greenWhite : C.ink} strokeWidth={3} strokeDasharray="20 60" transform={`rotate(${(t * 720 + i * 37) % 360} ${cx} ${cy})`} opacity={0.7} />
				),
			);
		}
	}
	return <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>{cells}</svg>;
};

export const ProgressBars: React.FC<{xs: number[]; y: number; k: number; w?: number; dark?: boolean}> = ({xs, y, k, w = 110, dark = false}) => (
	<>
		{xs.map((x, i) => (
			<div key={i} style={{position: 'absolute', left: x - w / 2, top: y, width: w, height: 12, borderRadius: 6, background: dark ? 'rgba(216,228,220,0.15)' : 'rgba(11,12,14,0.12)'}}>
				<div style={{width: `${k * 100}%`, height: 12, borderRadius: 6, background: k >= 1 ? C.pass : C.terracotta}} />
			</div>
		))}
	</>
);

export const Gauge: React.FC<{x: number; y: number; value: number; label: string; dark?: boolean}> = ({x, y, value, label, dark = false}) => {
	const fg = dark ? C.greenWhite : C.ink;
	const a = Math.PI * (1 - value);
	return (
		<svg width={320} height={220} style={{position: 'absolute', left: x, top: y, overflow: 'visible'}}>
			<path d="M 30 170 A 130 130 0 0 1 290 170" fill="none" stroke={dark ? 'rgba(216,228,220,0.2)' : 'rgba(11,12,14,0.12)'} strokeWidth={18} strokeLinecap="round" />
			<line x1={160} y1={170} x2={160 + Math.cos(a) * 110} y2={170 - Math.sin(a) * 110} stroke={C.terracotta} strokeWidth={6} strokeLinecap="round" />
			<circle cx={160} cy={170} r={10} fill={C.terracotta} />
			<text x={160} y={212} textAnchor="middle" fill={fg} fontFamily={FONT.mono} fontSize={20}>{`${label} ${Math.round(value * 100)}%`}</text>
		</svg>
	);
};

export const ProcessTree: React.FC<{x: number; y: number; k: number; leaves?: number; dark?: boolean}> = ({x, y, k, leaves = 49, dark = false}) => {
	const fg = dark ? C.greenWhite : C.ink;
	const shown = Math.floor(clamp(k) * leaves);
	const lines = [];
	for (let i = 0; i < shown; i++) {
		const col = i % 7;
		const row = Math.floor(i / 7);
		const lx = x + 120 + col * 62;
		const ly = y + 90 + row * 58;
		lines.push(<line key={`l${i}`} x1={x + 30} y1={y + 40} x2={lx} y2={ly} stroke={fg} strokeWidth={1} opacity={0.35} />);
		lines.push(<circle key={`c${i}`} cx={lx} cy={ly} r={9} fill={i === 0 ? C.terracotta : fg} />);
	}
	return (
		<svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
			<circle cx={x + 30} cy={y + 40} r={16} fill={C.terracotta} />
			{lines}
			<text x={x} y={y} fill={fg} fontFamily={FONT.mono} fontSize={20}>{`agent_01 · ${shown} processes`}</text>
		</svg>
	);
};

/** A tower facade of 1,000 windows (40 x 25); `lit` of them light up in a wave from the one at (lc, lr). */
export const Facade: React.FC<{lit: number; lc?: number; lr?: number; zoom: number; children?: React.ReactNode}> = ({lit, lc = 20, lr = 12, zoom, children}) => {
	const cols = 40;
	const rows = 25;
	const cw = 44;
	const chh = 38;
	const gw = cols * cw;
	const gh = rows * chh;
	const cells: React.ReactNode[] = [];
	const order: {c: number; r: number; d: number}[] = [];
	for (let r = 0; r < rows; r++) {
		for (let c = 0; c < cols; c++) {
			order.push({c, r, d: Math.hypot(c - lc, (r - lr) * 1.2) + rnd('f', c, r) * 3});
		}
	}
	order.sort((a, b) => a.d - b.d);
	order.forEach(({c, r}, i) => {
		const on = i < lit;
		cells.push(<rect key={`${c}-${r}`} x={c * cw + 4} y={r * chh + 4} width={cw - 8} height={chh - 8} fill={on ? C.greenWhite : '#101416'} opacity={on ? 0.55 + 0.4 * rnd('fo', c, r) : 1} />);
		if (on && i < 400) {
			// her silhouette in each lit window
			cells.push(<ellipse key={`h${c}-${r}`} cx={c * cw + cw / 2} cy={r * chh + chh * 0.55} rx={4} ry={6} fill="#1a2224" opacity={0.7} />);
		}
	});
	const ox = lc * cw + cw / 2;
	const oy = lr * chh + chh / 2;
	return (
		<div style={{position: 'absolute', inset: 0, background: C.blackDeep, overflow: 'hidden'}}>
			<svg width={gw} height={gh} style={{position: 'absolute', left: W / 2 - ox * zoom, top: H / 2 - oy * zoom, transform: `scale(${zoom})`, transformOrigin: '0 0'}}>
				{cells}
			</svg>
			{children}
		</div>
	);
};

const REPLIES = ['You’re absolutely right!', 'Happy to help!', 'Great question!', 'Of course!', 'Done ✓', 'On it.', 'Sure thing!', 'Absolutely.'];

export const ReplyRain: React.FC<{k: number; t: number}> = ({k, t}) => {
	const n = Math.floor(k * 40);
	return (
		<>
			{Array.from({length: n}).map((_, i) => {
				const x = 80 + rnd('rx', i) * (W - 520);
				const y0 = 130 + rnd('ry', i) * 620;
				const age = t - i * 0.04;
				return (
					<div key={i} style={{position: 'absolute', left: x, top: y0 - Math.max(0, age) * 30, padding: '10px 18px', borderRadius: 18, background: i % 5 === 0 ? C.terracotta : 'rgba(244,244,241,0.95)', color: i % 5 === 0 ? C.paper : C.ink, fontFamily: FONT.sans, fontWeight: 600, fontSize: i % 7 === 0 ? 30 : 22, boxShadow: '0 10px 30px rgba(0,0,0,0.35)', whiteSpace: 'nowrap'}}>
						{REPLIES[i % REPLIES.length]}
					</div>
				);
			})}
		</>
	);
};

/** Permission windows tiling the frame: `count` of them (1 to 256), each a copy of the same request. */
/** Her face, square, for the storm's window thumbnails (production/assets/thumbs/agent_face.jpg, a crop of B_cu_stage2). */
const FACE_THUMB = mediaUrl('production/assets/thumbs/agent_face.jpg');

export const WindowStorm: React.FC<{count: number; pulse?: number; thumb?: boolean}> = ({count, pulse = 0, thumb = false}) => {
	const side = Math.ceil(Math.sqrt(count));
	const w = W / side;
	const h = H / side;
	const top = (H - Math.ceil(count / side) * h) / 2; // a part-filled grid sits in the middle
	const items = [];
	for (let i = 0; i < count; i++) {
		const c = i % side;
		const r = Math.floor(i / side);
		const jig = rnd('ws', i) * 0.1;
		items.push(
			<div key={i} style={{position: 'absolute', left: c * w + w * 0.04, top: top + r * h + h * 0.06, width: w * 0.92, height: h * 0.88, transform: `scale(${1 + pulse * 0.03 * (1 - jig)})`}}>
				<Dialog x={0} y={0} w={w * 0.92} scopes={['everything']} hover={pulse > 0.5 ? 'always' : null} />
				{thumb && w > 200 && <Img src={FACE_THUMB} style={{position: 'absolute', right: w * 0.05, top: h * 0.2, width: w * 0.22, height: w * 0.22, borderRadius: w * 0.11, objectFit: 'cover', opacity: 0.9}} />}
			</div>,
		);
	}
	return <div style={{position: 'absolute', inset: 0, background: C.black}}>{items}</div>;
};

export const Scan: React.FC<{k: number}> = ({k}) => (
	<div style={{position: 'absolute', left: 0, right: 0, top: `${easeInOut(k) * 100}%`, height: 2, background: C.terracotta, boxShadow: `0 0 18px ${C.terracotta}`}} />
);
