// A storyboard card: what the footage layer shows until a shot's plate or clip exists (BRIEF.md step 3).
// A plain frame in the shot's world with a line drawing of its subject where it will stand, so the
// animatic already reads composition, type zones and tracking; the shot's ID and plan sit small in a corner.
import React from 'react';
import type {Slot} from '../chapters/types';
import type {Shot} from '../lib/data';
import {C, FONT, H, W, worldOf} from '../lib/theme';
import type {Cam} from './PrintPass';

const Figure: React.FC<{x: number; y: number; h: number; stroke: string; back?: boolean}> = ({x, y, h, stroke, back}) => {
	// a standing figure, feet at (x, y), h tall: head, pinned-up hair, collar, shoulders, legs
	const u = h / 8;
	if (h < 44) {
		// far away: a head and a body, which is all a crowd to the horizon shows
		return <path d={`M ${x} ${y} L ${x} ${y - 6.2 * u} M ${x - 0.9 * u} ${y - 5.6 * u} L ${x + 0.9 * u} ${y - 5.6 * u}`} stroke={stroke} strokeWidth={Math.max(1, h / 30)} fill="none" />;
	}
	return (
		<g fill="none" stroke={stroke} strokeWidth={Math.max(1.5, h / 160)} strokeLinecap="round">
			<ellipse cx={x} cy={y - 7.3 * u} rx={0.46 * u} ry={0.58 * u} />
			{!back && <circle cx={x} cy={y - 7.95 * u} r={0.22 * u} />}
			<path d={`M ${x - 1.05 * u} ${y - 6.1 * u} Q ${x} ${y - 6.45 * u} ${x + 1.05 * u} ${y - 6.1 * u}`} />
			<path d={`M ${x - 1.05 * u} ${y - 6.1 * u} L ${x - 0.85 * u} ${y - 3.6 * u} L ${x - 0.55 * u} ${y} M ${x + 1.05 * u} ${y - 6.1 * u} L ${x + 0.85 * u} ${y - 3.6 * u} L ${x + 0.55 * u} ${y}`} />
			<path d={`M ${x - 0.85 * u} ${y - 3.6 * u} L ${x + 0.85 * u} ${y - 3.6 * u}`} />
		</g>
	);
};

const Bust: React.FC<{x: number; top: number; scale: number; stroke: string; back?: boolean}> = ({x, top, scale, stroke, back}) => {
	// head and shoulders: `scale` is the head's height in px
	const s = scale;
	const hy = top + 0.5 * s;
	return (
		<g fill="none" stroke={stroke} strokeWidth={Math.max(1.5, s / 110)} strokeLinecap="round">
			<ellipse cx={x} cy={hy} rx={0.36 * s} ry={0.5 * s} />
			<path d={`M ${x - 0.42 * s} ${hy - 0.25 * s} Q ${x} ${hy - 0.95 * s} ${x + 0.42 * s} ${hy - 0.25 * s}`} />
			<circle cx={x + 0.05 * s} cy={hy - 0.62 * s} r={0.17 * s} />
			{!back && (
				<>
					<path d={`M ${x - 0.14 * s} ${hy - 0.02 * s} h ${0.09 * s} M ${x + 0.05 * s} ${hy - 0.02 * s} h ${0.09 * s}`} />
					<path d={`M ${x - 0.08 * s} ${hy + 0.27 * s} q ${0.08 * s} ${0.04 * s} ${0.16 * s} 0`} />
				</>
			)}
			<path d={`M ${x - 0.2 * s} ${hy + 0.48 * s} L ${x - 0.22 * s} ${hy + 0.78 * s} L ${x + 0.22 * s} ${hy + 0.78 * s} L ${x + 0.2 * s} ${hy + 0.48 * s}`} />
			<path d={`M ${x - 0.22 * s} ${hy + 0.78 * s} Q ${x - 1.1 * s} ${hy + 0.9 * s} ${x - 1.35 * s} ${hy + 1.9 * s} M ${x + 0.22 * s} ${hy + 0.78 * s} Q ${x + 1.1 * s} ${hy + 0.9 * s} ${x + 1.35 * s} ${hy + 1.9 * s}`} />
			<rect x={x - 0.09 * s} y={hy + 0.62 * s} width={0.18 * s} height={0.06 * s} />
		</g>
	);
};

const Eye: React.FC<{cx: number; cy: number; w: number; stroke: string}> = ({cx, cy, w, stroke}) => (
	<g fill="none" stroke={stroke} strokeWidth={3} strokeLinecap="round">
		<path d={`M ${cx - w / 2} ${cy} Q ${cx} ${cy - w * 0.36} ${cx + w / 2} ${cy} Q ${cx} ${cy + w * 0.3} ${cx - w / 2} ${cy}`} />
		<circle cx={cx} cy={cy} r={w * 0.15} />
		<circle cx={cx} cy={cy} r={w * 0.06} />
		<path d={`M ${cx - w * 0.45} ${cy - w * 0.2} Q ${cx} ${cy - w * 0.48} ${cx + w * 0.48} ${cy - w * 0.18}`} />
	</g>
);

const xOf = (place: string) => (place === 'left' ? W * 0.36 : place === 'right' ? W * 0.63 : W * 0.5);

const Subject: React.FC<{shot: Shot; stroke: string}> = ({shot, stroke}) => {
	const human = shot.set === 'H';
	const back = human || /from behind|over her shoulder|silhouette/i.test(shot.action);
	const x = xOf(shot.place);
	const many = /rows?|grid|ring|thousands|Instances|49 of her|seven of her|every desk|of her in/i.test(shot.action);
	if (!shot.agent_on_screen && !human) {
		// a shot without her: the set's prop, as a plain outline
		return (
			<g fill="none" stroke={stroke} strokeWidth={2}>
				<rect x={W * 0.52} y={H * 0.34} width={W * 0.3} height={H * 0.36} rx={10} />
				<rect x={W * 0.56} y={H * 0.3} width={W * 0.22} height={H * 0.06} rx={4} />
				<line x1={W * 0.52} y1={H * 0.58} x2={W * 0.82} y2={H * 0.58} />
			</g>
		);
	}
	switch (shot.framing) {
		case 'ECU':
			return shot.place === 'full' ? (
				<g>
					<Eye cx={W * 0.36} cy={H * 0.5} w={420} stroke={stroke} />
					<Eye cx={W * 0.64} cy={H * 0.5} w={420} stroke={stroke} />
				</g>
			) : (
				<Eye cx={W * 0.7} cy={H * 0.5} w={720} stroke={stroke} />
			);
		case 'CU':
			return <Bust x={x} top={150} scale={560} stroke={stroke} back={back} />;
		case 'MCU':
			return <Bust x={x} top={180} scale={360} stroke={stroke} back={back} />;
		case 'MS':
			return <Bust x={x} top={230} scale={210} stroke={stroke} back={back} />;
		case 'OVERHEAD': {
			const dots = [];
			if (/ring/i.test(shot.action)) {
				for (let i = 0; i < 12; i++) {
					const a = (i / 12) * Math.PI * 2;
					dots.push(<circle key={i} cx={W / 2 + Math.cos(a) * 300} cy={H / 2 + Math.sin(a) * 300} r={26} />);
				}
				dots.push(<circle key="c" cx={W / 2} cy={H / 2} r={130} strokeDasharray="6 8" />);
			} else if (/grid/i.test(shot.action)) {
				for (let r = 0; r < 9; r++) {
					for (let c = 0; c < 16; c++) {
						dots.push(<circle key={`${r}-${c}`} cx={180 + c * 104} cy={130 + r * 104} r={16} />);
					}
				}
			} else {
				dots.push(<rect key="d" x={W / 2 - 420} y={H / 2 - 200} width={840} height={400} rx={8} />);
				dots.push(<rect key="k" x={W / 2 - 260} y={H / 2 - 40} width={520} height={120} rx={6} />);
			}
			return <g fill="none" stroke={stroke} strokeWidth={2}>{dots}</g>;
		}
		case 'FS':
		case 'WS':
		case 'EWS': {
			if (many) {
				const n = /thousands|rows to the horizon/i.test(shot.action) ? 5 : /49|grid|7x7/i.test(shot.action) ? 4 : 1;
				const figs = [];
				for (let r = 0; r < n; r++) {
					const hh = 330 - r * 55;
					const count = 7 + r * 4;
					const gap = Math.min(170, 1500 / count);
					for (let i = 0; i < count; i++) {
						figs.push(<Figure key={`${r}-${i}`} x={W / 2 + (i - (count - 1) / 2) * gap} y={900 - r * 70} h={hh} stroke={stroke} />);
					}
				}
				return <g opacity={0.9}>{figs.reverse()}</g>;
			}
			const hh = shot.framing === 'FS' ? 620 : shot.framing === 'WS' ? (shot.place === 'small' ? 180 : 420) : 110;
			return <Figure x={shot.place === 'small' ? W * 0.62 : x} y={shot.framing === 'EWS' ? 700 : 960} h={hh} stroke={stroke} back={back} />;
		}
		default:
			return null;
	}
};

const SetLines: React.FC<{shot: Shot; stroke: string}> = ({shot, stroke}) => {
	if (shot.set === 'A') {
		// the night shift: a few ceiling tubes and a desk line
		return (
			<g stroke={stroke} strokeWidth={2} opacity={0.5}>
				{[0, 1, 2, 3, 4].map((i) => (
					<line key={i} x1={260 + i * 300} y1={110 + (i % 2) * 18} x2={430 + i * 300} y2={110 + (i % 2) * 18} />
				))}
				<line x1={0} y1={780} x2={W} y2={760} opacity={0.5} />
			</g>
		);
	}
	if (shot.set === 'B') {
		// the clean room: the cyclorama's horizon and a floor mark
		return (
			<g stroke={stroke} strokeWidth={2} opacity={0.45} fill="none">
				<path d={`M 0 ${H * 0.64} Q ${W / 2} ${H * 0.6} ${W} ${H * 0.64}`} />
				{/cobalt/i.test(shot.action + shot.plate) && <rect x={W * 0.6} y={H * 0.18} width={W * 0.3} height={H * 0.44} fill={C.cobalt} opacity={0.35} stroke="none" />}
				<rect x={W / 2 - 40} y={H * 0.8} width={80} height={24} fill={C.terracotta} stroke="none" opacity={0.7} />
			</g>
		);
	}
	if (shot.set === 'H') {
		// daylight: a window
		return (
			<g stroke={stroke} strokeWidth={2} opacity={0.4} fill="none">
				<rect x={W * 0.08} y={H * 0.12} width={W * 0.3} height={H * 0.5} />
				<line x1={W * 0.23} y1={H * 0.12} x2={W * 0.23} y2={H * 0.62} />
			</g>
		);
	}
	return null;
};

export const Card: React.FC<{shot: Shot; slots?: Slot[] | null; cam?: Cam; backdrop?: React.ReactNode}> = ({shot, slots, cam, backdrop}) => {
	const world = worldOf(shot);
	const bg =
		shot.set === 'H'
			? `linear-gradient(180deg, ${C.sky} 0%, ${C.sand} 100%)`
			: world === 'dark'
				? `radial-gradient(ellipse at 50% 30%, #15191b 0%, ${C.black} 70%)`
				: `linear-gradient(180deg, ${C.white} 0%, ${C.paleGrey} 100%)`;
	const stroke = world === 'dark' ? 'rgba(216,228,220,0.55)' : 'rgba(11,12,14,0.45)';
	const label = world === 'dark' ? 'rgba(216,228,220,0.5)' : 'rgba(11,12,14,0.5)';
	const plan = [shot.id, shot.framing, shot.clip ? `${shot.motion_tier} ${shot.clip}` : shot.motion_tier, shot.plate].filter(Boolean).join(' · ');
	return (
		<div style={{position: 'absolute', inset: 0, background: bg, overflow: 'hidden'}}>
			<div
				style={{
					position: 'absolute',
					inset: 0,
					// the storyboard card takes the shot's camera move too, so the animatic shows its timing
					transform: cam ? `translate(${-cam.x * W * 0.6}px, ${-cam.y * H * 0.6}px) rotate(${cam.rot}rad) scale(${cam.zoom})` : undefined,
					transformOrigin: cam ? `${cam.fx * 100}% ${cam.fy * 100}%` : undefined,
				}}
			>
				<svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
					<SetLines shot={shot} stroke={stroke} />
				</svg>
				{backdrop}
				<svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
					{slots ? (
						[...slots].sort((a, b) => a.y - b.y).map((sl, i) => <Figure key={i} x={sl.x} y={sl.y} h={sl.h} stroke={stroke} back={Boolean(sl.back)} />)
					) : (
						<Subject shot={shot} stroke={stroke} />
					)}
				</svg>
			</div>
			<div
				style={{
					position: 'absolute',
					right: 40,
					bottom: 92,
					width: 720,
					textAlign: 'right',
					color: label,
					fontFamily: FONT.mono,
					fontSize: 17,
					lineHeight: 1.45,
				}}
			>
				<div style={{letterSpacing: '0.04em'}}>{plan}</div>
				<div style={{fontFamily: FONT.sans, fontSize: 19, marginTop: 4}}>{shot.action}</div>
			</div>
		</div>
	);
};
