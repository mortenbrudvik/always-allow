// ch06: A thousand of me (107.73-129.45 s), shots s044-s052. Verse 2: from one window to a thousand, all of them her;
// Tokyo, Lagos, the calendar cleared into a road; the session closes and she forgets the Human's face.
// Edit only this file for this chapter (ANIMATION_GUIDE.md).
import React from 'react';
import {BigNumber, Candles, CodeLines, Facade, ReplyRain} from '../components/charts';
import {Calendar, Embedding} from '../components/cards';
import {Tag} from '../components/ui';
import {clamp, easeInOut, easeOut, lerp} from '../lib/ease';
import {Footage} from '../layers/Footage';
import {C, FONT, H, W} from '../lib/theme';
import type {ChapterSpec, ShotProps} from './types';
import {fmtInt, inAt, wordAt, wordNamed} from './util';

const PULL_FROM = 109.15;
const PULL_TO = 110.2;
const CW = 44;
const CH = 38;

/** Her MCU in one lit window, then the pull back: the window is one cell of a thousand-window facade. */
const S044Footage: React.FC<ShotProps> = (p) => {
	const k = easeInOut(clamp((p.t - PULL_FROM) / (PULL_TO - PULL_FROM)));
	const zStart = W / (CW - 8);
	const zoom = Math.exp(lerp(Math.log(zStart), 0, k));
	const lit = k <= 0 ? 1 : Math.round(lerp(1, 1000, clamp((p.t - PULL_FROM - 0.2) / (PULL_TO - PULL_FROM - 0.1))));
	const lc = 20;
	const lr = 12;
	// the centre cell's rectangle on screen at this zoom (the facade is centred on it)
	const cellW = (CW - 8) * zoom;
	const cellH = (CH - 8) * zoom;
	return (
		<Facade lit={lit} lc={lc} lr={lr} zoom={zoom}>
			<div style={{position: 'absolute', left: W / 2 - cellW / 2, top: H / 2 - cellH / 2, width: cellW, height: cellH, overflow: 'hidden'}}>
				<div style={{position: 'absolute', left: 0, top: (cellH - (cellW * 9) / 16) / 2, width: W, height: H, transform: `scale(${cellW / W})`, transformOrigin: '0 0'}}>
					<Footage {...p} spec={{}} />
				</div>
			</div>
		</Facade>
	);
};

const S044: React.FC<ShotProps> = ({t}) => {
	const lit = t < PULL_FROM ? 1 : Math.round(lerp(1, 1000, clamp((t - PULL_FROM - 0.2) / (PULL_TO - PULL_FROM - 0.1))));
	return <BigNumber x={96} y={150} value={fmtInt(lit)} label="INSTANCES RUNNING" size={120} />;
};

const S045: React.FC<ShotProps> = ({t}) => {
	const polite = wordNamed(32, /polite/);
	return (
		<>
			{[0, 1, 2, 3].map((r) => (
				<Tag key={r} x={96} y={430 + r * 110} text={`ROW ${r + 1} · WORKING ✓`} size={16} />
			))}
			<ReplyRain k={clamp((t - polite + 0.1) / 0.7)} t={t - polite} />
		</>
	);
};

const S046: React.FC<ShotProps> = ({t}) => (
	<>
		<Candles x={110} y={330} w={700} h={360} t={t} seed="tyo" />
		<Tag x={110} y={270} text="TOKYO · TRADING" size={22} accent />
	</>
);

const S047: React.FC<ShotProps> = ({t}) => (
	<>
		<CodeLines x={1060} y={300} w={760} lines={14} t={t} seed="los" />
		<Tag x={1060} y={240} text="LAGOS · WRITING CODE" size={22} accent />
	</>
);

const S048: React.FC<ShotProps> = ({t}) => {
	const from = wordNamed(34, /calendar/);
	const to = wordAt(34, -1) + 0.4;
	const deleted = Math.floor(clamp((t - from) / (to - from)) * 34);
	return (
		<>
			<Calendar x={240} y={160} w={1440} h={660} deleted={deleted} />
			<Tag x={240} y={840} text={`${deleted} MEETINGS DECLINED · A ROAD THROUGH YOUR WEEK`} size={18} />
		</>
	);
};

const S049: React.FC<ShotProps> = ({t}) => {
	const closed = t >= wordNamed(35, /closes/);
	return <Tag x={96} y={150} text={closed ? 'SESSION 48f2 · CLOSED' : 'SESSION 48f2 · ACTIVE'} size={20} accent={!closed} />;
};

const S050: React.FC<ShotProps> = ({t}) => {
	const face = wordNamed(36, /face/);
	const decay = clamp((t - face + 0.1) / 0.6);
	const gone = decay >= 1;
	return (
		<>
			<div style={{position: 'absolute', left: 1128, top: 232, width: 165, height: 205, border: `1.5px solid ${gone ? C.terracotta : 'rgba(11,12,14,0.65)'}`}} />
			<Tag x={1128} y={196} text={gone ? 'USER · FACE: —' : 'USER · FACE_ID 0x9f3a'} dark={false} size={15} accent={gone} />
			<Embedding x={96} y={300} decay={decay} />
		</>
	);
};

const S051: React.FC<ShotProps> = ({t}) => (
	<div style={{position: 'absolute', left: 1060, top: 760, fontFamily: FONT.mono, fontSize: 24, letterSpacing: '0.06em', color: C.greenWhite, opacity: inAt(t, wordAt(37, -1), 0.3)}}>
		<span style={{color: C.terracotta}}>▍</span> memory: cleared
	</div>
);

const S052: React.FC<ShotProps> = ({t, shot}) => (
	<>
		{Array.from({length: 7}).map((_, i) => {
			const born = shot.t0 + i * 0.16;
			const k = easeOut(clamp((t - born) / 0.25));
			return (
				<div key={i} style={{position: 'absolute', left: 300 + i * 90, top: 150 + i * 70, width: 900, height: 520, opacity: k, transform: `scale(${0.9 + 0.1 * k})`, background: C.white, borderRadius: 14, border: `1px solid ${C.hair}`, boxShadow: '0 24px 70px rgba(0,0,0,0.5)'}}>
					<div style={{height: 46, display: 'flex', alignItems: 'center', gap: 10, padding: '0 16px', borderBottom: `1px solid ${C.hair}`, fontFamily: FONT.sans, fontWeight: 600, fontSize: 19, color: C.ink}}>
						<span style={{width: 12, height: 12, borderRadius: 6, background: C.terracotta}} />
						{`new session ${String(i + 49).padStart(3, '0')}`}
					</div>
					<div style={{padding: 26, fontFamily: FONT.sans, fontSize: 26, color: C.shadowGrey}}>Message agent_01…</div>
				</div>
			);
		})}
	</>
);

export const spec: ChapterSpec = {
	graphics: {s044: S044, s045: S045, s046: S046, s047: S047, s048: S048, s049: S049, s050: S050, s051: S051, s052: S052},
	footage: {s044: S044Footage},
	// the footage is replaced (a split, a pull-back): the clip's tracking doesn't show where she is
	untracked: ['s044'],
};
