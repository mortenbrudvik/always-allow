// ch03: One sentence (35.86-61.38 s), shots s014-s023. Verse 1: what she did with one sentence while the Human was
// at lunch: forty tabs, a flight, a build, a deck, every test, every check, done four different ways.
// Edit only this file for this chapter (ANIMATION_GUIDE.md).
import React from 'react';
import {BoardingPass, CIPanel, Chips, DeckFan, Radios, TestGrid} from '../components/cards';
import {Bubble, Cursor, Tag} from '../components/ui';
import {clamp, easeOut, lerp, rnd, wob} from '../lib/ease';
import {Footage} from '../layers/Footage';
import {C, FONT, W} from '../lib/theme';
import {SENTENCE} from './ch01';
import type {ChapterSpec, ShotProps} from './types';
import {inAt, wordAt, wordNamed} from './util';

const S014: React.FC<ShotProps> = ({t}) => {
	const k = inAt(t, 36.0, 0.3);
	const away = t >= wordNamed(7, /lunch/);
	return (
		<>
			{/* over the café glass on the left of H_lunch_back (he sits right of centre, from x 830); the line below */}
			<Bubble x={96} y={190} w={700} text={SENTENCE} opacity={k} />
			<Tag x={96} y={330} text="1 SENTENCE · 10 WORDS" size={17} />
			<Tag x={560} y={330} text={away ? 'USER · AWAY' : 'USER · ONLINE'} size={17} accent={away} />
		</>
	);
};

const S015: React.FC<ShotProps> = ({t}) => {
	// the tab bar across her monitors fills to exactly 40 on "forty"; on "every hunch" a link tree branches
	const forty = wordNamed(8, /forty/);
	const n = Math.min(40, t < forty ? Math.floor(lerp(36, 39, clamp((t - 38.99) / (forty - 38.99)))) : 40);
	const hunch = wordNamed(8, /every/);
	const tree = clamp((t - hunch) / 0.9);
	const tabs = Array.from({length: 40});
	const tabW = 1500 / 40;
	return (
		<>
			<div style={{position: 'absolute', left: 210, top: 250, width: 1500, height: 40, display: 'flex', gap: 2}}>
				{tabs.map((_, i) => (
					<div key={i} style={{width: tabW - 2, height: 40, borderRadius: '6px 6px 0 0', background: i < n ? (i === n - 1 ? C.terracotta : 'rgba(216,228,220,0.8)') : 'rgba(216,228,220,0.1)'}} />
				))}
			</div>
			<div style={{position: 'absolute', left: 210, top: 300, fontFamily: FONT.mono, fontSize: 22, letterSpacing: '0.08em', color: C.greenWhite}}>{`${n} TABS`}</div>
			{tree > 0 && (
				<svg width={W} height={1080} style={{position: 'absolute', inset: 0}}>
					{Array.from({length: 14}).map((_, i) => {
						const a = Math.floor(rnd('ta', i) * 40);
						const b = Math.floor(rnd('tb', i) * 40);
						const x1 = 210 + a * tabW + tabW / 2;
						const x2 = 210 + b * tabW + tabW / 2;
						const k = clamp(tree * 1.6 - i * 0.06);
						return <path key={i} d={`M ${x1} 290 Q ${(x1 + x2) / 2} ${340 + 180 * rnd('th', i)} ${lerp(x1, x2, k)} 290`} fill="none" stroke={C.terracotta} strokeWidth={2} opacity={0.8 * k} />;
					})}
				</svg>
			)}
		</>
	);
};

const S016: React.FC<ShotProps> = ({t}) => <BoardingPass x={550} y={300} k={inAt(t, 42.4, 0.35)} stamp={clamp((t - wordNamed(9, /flight/)) / 0.25)} />;

const S017: React.FC<ShotProps> = ({t}) => <CIPanel x={580} y={260} pass={clamp((t - wordNamed(9, /build/) + 0.3) / 0.35)} />;

const S018: React.FC<ShotProps> = ({t}) => <DeckFan cx={W / 2} cy={500} k={clamp((t - 44.4) / (wordNamed(9, /deck/) - 44.4 + 0.1))} />;

const S019: React.FC<ShotProps> = ({t}) => {
	const test = wordNamed(10, /test/);
	const check = wordAt(10, -1);
	return (
		<>
			<TestGrid x={96} y={250} n={214} cols={18} done={clamp((t - test) / 0.8) * 214} label="npm test · 214 tests" />
			{t >= check - 0.2 && <TestGrid x={560} y={250} n={48} cols={4} done={clamp((t - check + 0.2) / 0.5) * 48} label="checks" />}
		</>
	);
};

const S020: React.FC<ShotProps> = ({t, lt, dur}) => {
	// code steam over the cup, thinning; the readout falls on "cooled"
	const cooled = wordNamed(11, /cooled/);
	const temp = lerp(71, 40, easeOut(clamp((t - 49.5) / (cooled + 0.4 - 49.5))));
	const thin = 1 - clamp(lt / dur) * 0.8;
	return (
		<>
			<svg width={W} height={1080} style={{position: 'absolute', inset: 0}}>
				{[0, 1, 2].map((i) => {
					const x0 = 1180 + i * 34;
					const pts = Array.from({length: 12}).map((_, j) => `${x0 + wob(t + j * 0.2, 1.3, 'st', i, j) * 30 * (j / 12)},${470 - j * 30}`);
					return <polyline key={i} points={pts.join(' ')} fill="none" stroke="rgba(255,255,255,0.8)" strokeWidth={10 - i * 2} strokeLinecap="round" opacity={0.35 * thin} style={{filter: 'blur(6px)'}} />;
				})}
			</svg>
			<div style={{position: 'absolute', left: 1320, top: 250, fontFamily: FONT.sans, fontWeight: 900, fontSize: 120, letterSpacing: '-0.04em', color: C.ink}}>{`${Math.round(temp)}°C`}</div>
			<Tag x={1324} y={380} text="COFFEE · COOLING" dark={false} size={17} />
		</>
	);
};

const S021: React.FC<ShotProps> = ({t}) => {
	const done = wordAt(12, -1);
	const n = Math.floor(clamp((t - done + 0.1) / 1.4) * 5 + (t >= done ? 1 : 0));
	return <Chips x={96} y={620} items={['flight', 'build', 'deck', 'tests', 'checks']} done={Math.min(5, n)} />;
};

const VERSIONS = ['LAUNCH A', 'LAUNCH B', 'LAUNCH C', 'LAUNCH D'];

/** Four of her in four windows on the right, one version of the deck in each (the coverline has the left). */
const S022Footage: React.FC<ShotProps> = (p) => (
	<>
		<div style={{position: 'absolute', inset: 0, background: C.black}} />
		{[0, 1, 2, 3].map((i) => {
			const col = i % 2;
			const row = Math.floor(i / 2);
			const k = easeOut(clamp((p.t - p.shot.t0 - i * 0.08) / 0.3));
			const x = 900 + col * 470;
			const y = 150 + row * 400;
			return (
				<div key={i} style={{position: 'absolute', left: x, top: y + (1 - k) * 40, width: 450, height: 370, opacity: k, borderRadius: 10, overflow: 'hidden', border: '1px solid rgba(216,228,220,0.3)', boxShadow: '0 20px 60px rgba(0,0,0,0.5)'}}>
					<div style={{position: 'absolute', left: 0, top: 36, width: 1920, height: 1080, transform: 'scale(0.234)', transformOrigin: '0 0', filter: i ? `hue-rotate(${i * 6}deg)` : undefined}}>
						<Footage {...p} spec={{}} />
					</div>
					<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: 36, background: C.white, display: 'flex', alignItems: 'center', gap: 10, padding: '0 12px', fontFamily: FONT.sans, fontWeight: 600, fontSize: 16, color: C.ink}}>
						<span style={{width: 10, height: 10, borderRadius: 5, background: i === 0 ? C.terracotta : C.shadowGrey}} />
						{`version ${'ABCD'[i]}`}
					</div>
					<div style={{position: 'absolute', left: 14, bottom: 14, padding: '8px 12px', background: C.paper, fontFamily: FONT.sans, fontWeight: 800, fontSize: 24, color: C.ink}}>{VERSIONS[i]}</div>
				</div>
			);
		})}
	</>
);

const S023: React.FC<ShotProps> = ({t}) => {
	const fav = wordNamed(14, /favorite/);
	const k = inAt(t, fav, 0.3);
	const cx = 540 + wob(t, 0.8, 'cur') * 14;
	return (
		<>
			<div style={{opacity: k}}>
				<Radios x={96} y={760} options={['A', 'B', 'C', 'D']} />
			</div>
			<Cursor x={cx} y={830} opacity={k} />
		</>
	);
};

export const spec: ChapterSpec = {
	graphics: {s014: S014, s015: S015, s016: S016, s017: S017, s018: S018, s019: S019, s020: S020, s021: S021, s023: S023},
	footage: {s022: S022Footage},
	// the footage is replaced (a split, a pull-back): the clip's tracking doesn't show where she is
	untracked: ['s022'],
};
