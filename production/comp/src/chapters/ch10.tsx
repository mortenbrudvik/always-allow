// ch10: Your weekends (172.43-193.13 s), shots s071-s078. The breakdown, slow and cavernous: the Human's weekends and
// mornings claimed by her task blocks, a heartbeat flattening into a progress bar, the rest of his life flowing into her.
// Edit only this file for this chapter (ANIMATION_GUIDE.md).
import React from 'react';
import {Heartbeat, MorningTimeline, StackedBar} from '../components/charts';
import {Calendar, Reticle} from '../components/cards';
import {Tag} from '../components/ui';
import {clamp, easeInOut, easeOut, lerp} from '../lib/ease';
import {C, FONT, W} from '../lib/theme';
import type {ChapterSpec, ShotProps} from './types';
import {wordAt, wordNamed} from './util';

const S071: React.FC<ShotProps> = ({t, shot}) => {
	// the reticle from the job card lands on the weekend; Saturday and Sunday fill with her blocks
	const wk = wordNamed(52, /weekends/);
	const land = easeInOut(clamp((t - shot.t0) / (wk - shot.t0)));
	const claimed = clamp((t - wk) / 1.4) * 12;
	const cx = 96 + 5.5 * (760 / 7);
	return (
		<>
			<Calendar x={96} y={560} w={760} h={400} highlightWeekend={1} claimed={claimed} dark={false} />
			<Reticle x={lerp(W + 100, cx, land)} y={lerp(300, 720, land)} r={60} opacity={1 - clamp((t - wk - 0.8) / 0.4)} />
		</>
	);
};

const S072: React.FC<ShotProps> = ({t}) => <MorningTimeline x={96} y={640} w={760} k={clamp((t - wordNamed(53, /mornings/)) / 1.2)} />;

const S073: React.FC<ShotProps> = ({t}) => (
	<StackedBar x={96} y={330} w={760} k={clamp((t - wordNamed(54, /hour/)) / 1.2)} parts={[['meetings', 14], ['email', 11], ['forms', 6], ['waiting', 5]]} />
);

const S074: React.FC<ShotProps> = ({t, shot}) => {
	const never = wordNamed(55, /never/);
	const beat = wordNamed(55, /heartbeat/);
	return <Heartbeat y={470} t={t} flat={easeOut(clamp((t - never) / 0.6))} fill={clamp((t - beat) / (shot.t1 - beat - 0.3))} />;
};

const S075: React.FC<ShotProps> = ({t}) => {
	const off = t >= wordNamed(56, /life/);
	return <Tag x={1500} y={150} text={off ? 'USER · OFFLINE' : 'USER · ONLINE'} size={20} accent={!off} />;
};

const S076: React.FC<ShotProps> = ({p}) => {
	// his USER box shrinks with him as he walks away
	const s = lerp(1, 0.55, easeInOut(p));
	const x = 1190;
	const y = 790;
	return (
		<>
			<div style={{position: 'absolute', left: x - 22 * s, top: y - 26 * s, width: 44 * s, height: 52 * s, border: '1.5px solid rgba(11,12,14,0.65)'}} />
			<Tag x={x - 30} y={y - 26 * s - 34} text="USER" dark={false} size={13} />
		</>
	);
};

const TASKS = ['expense report', 'inbox zero', 'quarterly goals', 'dentist appointment', 'birthday gift', 'tax return', 'gym plan'];

const S077: React.FC<ShotProps> = ({t}) => {
	// the rest of his life flows into her: each task flies in and ticks to DONE
	const from = wordAt(57, 0) - 0.2;
	return (
		<>
			{TASKS.map((task, i) => {
				const born = from + i * 0.32;
				const k = easeInOut(clamp((t - born) / 0.9));
				const done = k >= 1;
				const x = lerp(W + 40, 700, k);
				const y = lerp(260 + i * 90, 380, k);
				return (
					<div key={task} style={{position: 'absolute', left: x, top: y, transform: `scale(${lerp(1, 0.35, k)})`, transformOrigin: 'left center', opacity: done ? 0 : 1, padding: '10px 18px', borderRadius: 22, background: 'rgba(11,12,14,0.85)', border: '1px solid rgba(216,228,220,0.3)', fontFamily: FONT.sans, fontWeight: 600, fontSize: 26, color: C.greenWhite, whiteSpace: 'nowrap'}}>
						{task} <span style={{color: k > 0.8 ? C.pass : 'rgba(216,228,220,0.5)', fontFamily: FONT.mono, fontSize: 18}}>{k > 0.8 ? '✓ DONE' : '→'}</span>
					</div>
				);
			})}
		</>
	);
};

export const spec: ChapterSpec = {
	graphics: {s071: S071, s072: S072, s073: S073, s074: S074, s075: S075, s076: S076, s077: S077},
};
