// ch12: Access granted (209.57-237.06 s), shots s088-s102. The click and hook 3 at full scale: the button goes
// down on the downbeat, MODE: AUTO, thousands of her in rows to the horizon turn to the lens, the permission
// window as architecture, a million instances, the bow.
// Edit only this file for this chapter (ANIMATION_GUIDE.md).
import React from 'react';
import {SpinnerGrid} from '../components/charts';
import {AccessBadge} from '../components/cards';
import {BigButton, BUTTON_BAR, Dialog, SizeTag} from '../components/ui';
import {clamp, easeIn, easeInOut, easeOut, lerp, rnd} from '../lib/ease';
import {C, CHROME, FONT, H, ink, W} from '../lib/theme';
import {barTime} from '../lib/time';
import type {ChapterSpec, ShotProps, Slot} from './types';
import {fmtInt, inAt, lyricOf, wordAt, wordNamed} from './util';

// ---- the stages, measured on the picked plates (session 5) ---------------------------------------------

/** The flat horizon of B_rows_horizon, where the rows vanish: the white floor meets the slate sky at y 539, with
 * the terracotta cube at the vanishing point, x 960. */
const HORIZON = 539;
/** B_window_wall's light panel, front on: the permission window the size of a building. */
const PANEL = {x: 295, y: 190, w: 1332, h: 590};
/** B_window_wall_side: the panel's near edge (its top and its foot) and its vanishing point. The camera sits low,
 * so the foot runs almost flat along y 950 and the top falls toward a vanishing point far off the right. */
const SIDE = {near: {x: 275, top: 141, foot: 954}, far: {x: 1560}, vp: {x: 4830, y: 930}};

const label = (i: number) => `INSTANCE_${String(i).padStart(5, '0')}`;

/** Rows to the horizon: the front row's feet at y0, each row further back by `step`, filling the width. */
const toHorizon = (y0: number, h0: number, gap0: number, rows: number, step: number, back = false): Slot[] => {
	const out: Slot[] = [];
	let id = 1;
	for (let r = 0; r < rows; r++) {
		const z = 1 + r * step;
		const h = h0 / z;
		const gap = gap0 / z;
		const y = HORIZON + (y0 - HORIZON) / z;
		const half = Math.ceil((W / 2 + h) / gap);
		for (let i = -half; i <= half; i++) {
			const x = W / 2 + (i + (r % 2 ? 0.5 : 0)) * gap;
			out.push({x, y, h, back, label: r === 0 && i === 0 ? 'AGENT_01' : label(id++)});
		}
	}
	return out;
};

/** Rows in front of the window wall (s091, s095, s098), from the front of the stage back to the panel's foot, seen
 * from a little above: each row further back a step higher and smaller, alternate rows staggered by half a place and
 * each copy clear of the next, so the faces show row over row. Seven deep at one height, they fused into one band. */
const beforeWall = (rows: number): Slot[] => {
	const foot = PANEL.y + PANEL.h;
	const out: Slot[] = [];
	let id = 1;
	for (let r = 0; r < rows; r++) {
		const k = r / Math.max(1, rows - 1);
		const y = lerp(1000, foot + 20, k);
		const h = 330 * Math.pow(0.72, k);
		const gap = h * 0.44;
		const n = Math.floor((W - 80) / gap);
		for (let i = 0; i < n; i++) {
			const x = W / 2 + (i - (n - 1) / 2) * gap + (r % 2 ? gap / 2 : 0);
			out.push({x, y, h, label: r === 0 && i === Math.floor(n / 2) ? 'AGENT_01' : label(id++)});
		}
	}
	return out;
};

/** B_window_wall_side's rows of her (s099, s101, s102), as on risers: three lines of her receding toward the panel's
 * vanishing point, each copy a third of a figure clear of the next (her figure is about 0.29 of her height wide), each
 * row further back a step higher and a little smaller so its heads and shoulders show over the row in front, the
 * middle row standing between the places of the others. On a flat floor the plate's low camera would hide every row
 * behind the first; packed tighter, the copies smear into one grey mass (the user's note on the rough cut, 30 Sep). */
const SIDE_ROWS = [
	{h: 420, foot: 1050}, // the front row, at its near end
	{h: 386, foot: 925},
	{h: 355, foot: 800},
];
const SIDE_STEP = 1.35 * 0.29; // centre to centre along a row, in figure heights
const SIDE_FROM = 250;
const SIDE_TO = 1640; // short of the terracotta block at the panel's far corner

const sideRows = (): Slot[] => {
	const {vp} = SIDE;
	const scale = (x: number) => (vp.x - x) / (vp.x - SIDE_FROM);
	// the places along the front row, each one step on from the last at its own scale
	const places: number[] = [];
	for (let x = SIDE_FROM; x < SIDE_TO; x += SIDE_STEP * SIDE_ROWS[0].h * scale(x)) {
		places.push(x);
	}
	const out: Slot[] = [];
	let id = 1;
	SIDE_ROWS.forEach((row, r) => {
		places.forEach((px, i) => {
			const x = r % 2 ? (places[i + 1] === undefined ? null : (px + places[i + 1]) / 2) : px;
			if (x === null) {
				return;
			}
			const s = scale(x);
			out.push({x, y: vp.y + (row.foot - vp.y) * s, h: row.h * s, label: r === 0 && i === 0 ? 'AGENT_01' : label(id++)});
		});
	});
	return out;
};

const SIDE_SLOTS = sideRows();

/** The rows of s089, s093 and s107 (ch13): D3's crowd to the horizon, from behind until the turn. */
export const horizonRows = (back = false) => toHorizon(1010, 340, 150, 16, 0.8, back);
const ROWS_089 = (t: number) => horizonRows(t < barTime(110));

/** Labels on a random handful of slots, new every frame: too fast to read. */
const Flicker: React.FC<{slots: Slot[]; frame: number; n?: number; minH?: number}> = ({slots, frame, n = 36, minH = 50}) => {
	const big = slots.filter((s) => s.h >= minH);
	return (
		<>
			{Array.from({length: Math.min(n, big.length)}).map((_, i) => {
				const s = big[Math.floor(rnd('flick', frame, i) * big.length)];
				return (
					<div key={i} style={{position: 'absolute', left: s.x, top: s.y - s.h - 22, transform: 'translateX(-50%)', fontFamily: FONT.mono, fontSize: 13, letterSpacing: '0.05em', color: 'rgba(11,12,14,0.75)', whiteSpace: 'nowrap'}}>
						<span style={{color: C.terracotta}}>▍</span>
						{s.label}
					</div>
				);
			})}
		</>
	);
};

// ---- the shots ------------------------------------------------------------------------------------------

const CLICK = barTime(109);

const S088: React.FC<ShotProps> = ({t, lt}) => {
	// the click: the button is down on the downbeat (under the flash), then thousands of windows burst outward
	const burst = clamp((t - CLICK - 0.12) / 0.7);
	return (
		<>
			<div style={{position: 'absolute', inset: 0, background: BUTTON_BAR}} />
			{burst > 0 &&
				Array.from({length: 180}).map((_, i) => {
					const born = rnd('b88', i) * 0.45;
					const k = easeOut(clamp((lt - 0.12 - born) / 0.55));
					if (k <= 0) {
						return null;
					}
					const a = rnd('a88', i) * Math.PI * 2;
					const dist = k * (500 + rnd('r88', i) * 900);
					const w = lerp(60, 150 + rnd('w88', i) * 260, k);
					return <Dialog key={i} x={W / 2 + Math.cos(a) * dist * 1.4 - w / 2} y={H / 2 + Math.sin(a) * dist * 0.8 - (w * 9) / 32} w={w} scopes={['everything']} opacity={0.35 + 0.65 * k} />;
				})}
			<BigButton cx={W / 2} cy={H / 2} w={860} pressed={1} />
		</>
	);
};

const S089: React.FC<ShotProps> = ({t, frame}) => <Flicker slots={ROWS_089(t)} frame={frame} />;

const S090: React.FC<ShotProps> = ({t}) => {
	// the access badge, upper right beside her hair, clear of ACCESS GRANTED. across the foot of the frame
	const k = inAt(t, wordNamed(61, /granted/) - 0.1, 0.35);
	return <AccessBadge x={1392} y={150} k={k} scale={0.82} />;
};

const S091: React.FC<ShotProps> = ({p}) => {
	// a title bar drawn along the panel's top edge: the permission window, the size of a building
	const k = easeInOut(clamp(p * 2.2));
	return (
		<>
			<div style={{position: 'absolute', left: PANEL.x, top: PANEL.y, width: PANEL.w * k, height: 58, overflow: 'hidden', background: 'rgba(244,244,241,0.96)', borderBottom: `2px solid ${C.hair}`, display: 'flex', alignItems: 'center', gap: 16, padding: '0 26px', whiteSpace: 'nowrap'}}>
				<span style={{width: 16, height: 16, borderRadius: 8, background: C.terracotta, flexShrink: 0}} />
				<span style={{fontFamily: FONT.sans, fontWeight: 600, fontSize: 26, color: C.ink}}>Permission request</span>
				<span style={{flex: 1}} />
				<span style={{fontFamily: FONT.mono, fontSize: 20, color: C.ink2}}>agent_01</span>
				<span style={{fontFamily: FONT.sans, fontSize: 28, color: C.ink2}}>×</span>
			</div>
			<div style={{opacity: clamp(p * 3 - 1.2)}}>
				<SizeTag x={PANEL.x} y={PANEL.y + PANEL.h + 16} text="WINDOW 40 M × 17 M" dark={false} />
			</div>
		</>
	);
};

const S092: React.FC<ShotProps> = ({t, p}) => <SpinnerGrid k={easeIn(clamp(p * 1.1))} t={t} dark={false} />;

const S093: React.FC<ShotProps> = ({p}) => {
	// INSTANCES, in the chrome's own type under its counters, counting past a million as the camera pulls back
	const n = Math.pow(1_048_576 * 1.6, easeIn(p));
	const {fgSoft} = ink('light');
	return (
		<div style={{position: 'absolute', right: CHROME, top: CHROME + 92, fontFamily: FONT.mono, fontSize: 19, letterSpacing: '0.06em', color: fgSoft, whiteSpace: 'pre', textAlign: 'right'}}>
			INSTANCES <span style={{color: n >= 1e6 ? C.terracotta : fgSoft}}>{fmtInt(Math.max(1, n))}</span>
		</div>
	);
};

const KEYS = ['API_KEY', 'SSH_KEY', 'AWS_SECRET', 'GITHUB_TOKEN', 'STRIPE_KEY', 'DB_PASSWORD', 'OAUTH_TOKEN', 'SLACK_TOKEN'];

const S096: React.FC<ShotProps> = ({t}) => {
	// keys stream past her into the panel's light: along the bottom of the frame, shrinking into the distance
	const from = wordAt(66, 0) - 0.3;
	return (
		<>
			{Array.from({length: 22}).map((_, i) => {
				const born = from + i * 0.12;
				const k = clamp((t - born) / 1.3);
				if (k <= 0 || k >= 1) {
					return null;
				}
				const e = easeIn(k);
				const x = lerp(-240, 1500 + rnd('kx', i) * 300, e);
				const y = lerp(1000 - rnd('ky', i) * 160, 690, e);
				const s = lerp(1.2, 0.25, e);
				return (
					<div key={i} style={{position: 'absolute', left: x, top: y, transform: `scale(${s})`, transformOrigin: 'left center', opacity: 1 - e * 0.6, padding: '6px 12px', background: C.ink, color: C.greenWhite, fontFamily: FONT.mono, fontSize: 22, borderRadius: 5, whiteSpace: 'nowrap'}}>
						{`${KEYS[i % KEYS.length]} ••••••••`}
					</div>
				);
			})}
		</>
	);
};

const S097: React.FC<ShotProps> = ({lt}) => {
	// every Instance gets a process ID, in a wave out from the centre of the grid
	const out = [];
	for (let r = 0; r < 9; r++) {
		for (let c = 0; c < 16; c++) {
			const x = 180 + c * 104;
			const y = 130 + r * 104;
			const d = Math.hypot(c - 7.5, (r - 4) * 1.2) / 9;
			if (lt < d * 0.9) {
				continue;
			}
			out.push(
				<div key={`${r}-${c}`} style={{position: 'absolute', left: x + 20, top: y - 8, fontFamily: FONT.mono, fontSize: 13, color: 'rgba(11,12,14,0.62)', whiteSpace: 'nowrap'}}>
					{`pid ${40000 + Math.floor(rnd('pid', r, c) * 25000)}`}
				</div>,
			);
		}
	}
	return <>{out}</>;
};

const S098: React.FC<ShotProps> = ({t}) => {
	// WITH TERRIFYING EASE with echo trails: outlined copies of the placed words, stepping up behind them
	const line = lyricOf(68);
	return (
		<svg width={W} height={H} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
			{line.tokens.map((tok, i) =>
				[1, 2, 3].map((e) => {
					const age = t - tok.t0 - e * 0.07;
					if (age < 0) {
						return null;
					}
					return (
						<text key={`${i}-${e}`} x={tok.x} y={tok.y - e * line.size * 0.16} fontFamily="Geist" fontWeight={900} fontSize={line.size} letterSpacing={`${line.style.tracking}em`} fill="none" stroke={C.ink} strokeWidth={2} opacity={0.42 - e * 0.11}>
							{tok.text}
						</text>
					);
				}),
			)}
		</svg>
	);
};

const SidePanel: React.FC = () => {
	// the storyboard card's side-on panel (the plate draws its own)
	const {near, far, vp} = SIDE;
	const s = (vp.x - far.x) / (vp.x - near.x);
	const pts = `${near.x},${near.top} ${far.x},${vp.y + (near.top - vp.y) * s} ${far.x},${vp.y + (near.foot - vp.y) * s} ${near.x},${near.foot}`;
	return (
		<svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
			<polygon points={pts} fill={C.panel} stroke={C.hair} strokeWidth={2} style={{filter: 'drop-shadow(0 0 60px rgba(255,255,255,0.95))'}} />
		</svg>
	);
};

const S100: React.FC<ShotProps> = ({t}) => {
	// HOW redacted, a third time and at full size: hook 1's small tooltip by her shoulder (s034) and hook 2's
	// redacted masthead (s062) come back as one huge tooltip; a black bar slams across "how?" on the word
	const how = wordNamed(70, /how/);
	const k = inAt(t, wordAt(70, 0) - 0.25, 0.25);
	const red = easeOut(clamp((t - how) / 0.1));
	const x = 260;
	const y = 470;
	return (
		<>
			<div style={{position: 'absolute', inset: 0, background: C.white}} />
			<div style={{position: 'absolute', left: x, top: y, width: W - 2 * x, height: 460, opacity: k, transform: `scale(${0.96 + 0.04 * k})`, transformOrigin: '50% 100%', background: C.paper, border: `2px solid ${C.hair}`, borderRadius: 28, boxShadow: '0 40px 90px rgba(11,12,14,0.18)'}}>
				<div style={{position: 'absolute', left: 64, top: 48, fontFamily: FONT.mono, fontSize: 26, letterSpacing: '0.08em', color: C.ink2}}>AGENT_01 · EXPLAIN YOUR STEPS</div>
				<div style={{position: 'absolute', left: 60, top: 104, fontFamily: FONT.mono, fontWeight: 700, fontSize: 230, lineHeight: 1, letterSpacing: '-0.02em', color: C.ink}}>how?</div>
				<div style={{position: 'absolute', left: 52, top: 118, height: 210, width: 690 * red, background: C.ink}} />
				<div style={{position: 'absolute', left: 64, bottom: 44, fontFamily: FONT.mono, fontSize: 26, letterSpacing: '0.08em', color: red >= 1 ? C.terracotta : C.ink2}}>{red >= 1 ? 'REDACTED · 3' : 'waiting for an answer…'}</div>
			</div>
		</>
	);
};

const S101: React.FC<ShotProps> = ({t, shot}) => {
	// a completion bar that snaps to 100 % three frames after "blink"
	const blink = wordNamed(71, /blink/);
	const k = t >= blink + 3 / 24 ? 1 : clamp((t - shot.t0) / (blink - shot.t0)) * 0.3;
	return (
		<div style={{position: 'absolute', left: 96, top: 930, width: 760}}>
			<div style={{fontFamily: FONT.mono, fontSize: 18, color: C.ink2, marginBottom: 10}}>{k >= 1 ? 'COMPLETE · 100%' : `RUNNING · ${Math.round(k * 100)}%`}</div>
			<div style={{height: 16, borderRadius: 8, background: 'rgba(11,12,14,0.1)'}}>
				<div style={{width: `${k * 100}%`, height: 16, borderRadius: 8, background: k >= 1 ? C.pass : C.terracotta}} />
			</div>
		</div>
	);
};

/** The front-on panel, for the storyboard card (the plate has its own). */
const WallPanel: React.FC = () => (
	<div style={{position: 'absolute', left: PANEL.x, top: PANEL.y, width: PANEL.w, height: PANEL.h, background: C.panel, boxShadow: '0 0 0 3px rgba(11,12,14,0.12), 0 0 160px 40px rgba(255,255,255,0.9)'}} />
);

export const spec: ChapterSpec = {
	graphics: {
		s088: S088, s089: S089, s090: S090, s091: S091, s092: S092, s093: S093, s096: S096, s097: S097,
		s098: S098, s100: S100, s101: S101,
	},
	camera: {
		// from her at the centre to thousands: a long pull-back, stronger than the board's default
		s093: (p) => ({zoom: lerp(2.4, 1, easeInOut(p.p)), fx: 0.5, fy: 0.78}),
	},
	formation: {
		s089: (p) => ROWS_089(p.t),
		s091: () => beforeWall(4),
		s093: () => horizonRows(),
		s095: () => beforeWall(5),
		s098: () => beforeWall(5),
		s099: () => SIDE_SLOTS,
		s101: () => SIDE_SLOTS,
		s102: () => SIDE_SLOTS,
	},
	backdrop: {s091: WallPanel, s095: WallPanel, s098: WallPanel, s099: SidePanel, s101: SidePanel, s102: SidePanel},
	// s101: the rows move at double speed, then freeze on "blink" (line 71)
	clipTime: {s101: {rate: 2, freezeFrom: Math.round(wordNamed(71, /blink/) * 24)}},
};
