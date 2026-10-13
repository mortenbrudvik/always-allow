// Kinetic lyrics: every word on its aligned time (src/lib/lyrics.ts decides what and where). Drawn as SVG
// text so each word's baseline lands exactly where the engine put it. The four modes move differently:
// mastheads slam (two frames of overshoot), coverlines rise, subtitles fade, the mass fills a micro grid.
import React from 'react';
import {shotAtFrame} from '../lib/data';
import {clamp, easeOut, rnd} from '../lib/ease';
import {type PlacedLine, type Token, visibleAt} from '../lib/lyrics';
import {C, FONT, H, W, worldOf} from '../lib/theme';
import {FPS} from '../lib/time';

const colourFor = (frame: number) => {
	const w = worldOf(shotAtFrame(frame));
	return w === 'dark'
		? {fill: C.greenWhite, shadow: 'rgba(0,0,0,0.55)', edge: 'rgba(11,12,14,0.85)'}
		: {fill: C.ink, shadow: 'rgba(244,244,241,0.5)', edge: 'rgba(244,244,241,0.9)'};
};

const Mass: React.FC<{line: PlacedLine; frame: number; fill: string}> = ({line, frame, fill}) => {
	// the chant's micro grid: the words repeated in small mono type, filling cell by cell on the eighths
	const start = Math.round(line.t0 * FPS);
	const k = frame - start;
	const word = line.text.replace(/[^A-Za-z .]/g, '').toUpperCase();
	const rows = 30;
	const cols = 9;
	const shown = Math.min(rows * cols, Math.floor(k * 11));
	const cells = [];
	for (let i = 0; i < shown; i++) {
		const r = i % rows;
		const c = Math.floor(i / rows);
		cells.push(
			<text key={i} x={70 + c * 206} y={62 + r * 34} fontFamily={FONT.mono} fontSize={17} fill={fill} opacity={0.18 + 0.2 * rnd('mass', line.line, i)} letterSpacing="0.06em">
				{`${word} ${String(i).padStart(3, '0')}`}
			</text>,
		);
	}
	return <g>{cells}</g>;
};

const Word: React.FC<{line: PlacedLine; tok: Token; frame: number; fill: string; shadow: string; edge: string}> = ({line, tok, frame, fill, shadow, edge}) => {
	const k = frame - Math.round(tok.t0 * FPS);
	const st = line.style;
	let opacity = 1;
	let dy = 0;
	let scale = 1;
	if (line.mode === 'masthead' || line.mode === 'mass') {
		scale = k <= 0 ? 1.1 : k === 1 ? 1.035 : 1; // two frames of overshoot, then it sits
	} else if (line.mode === 'coverline') {
		const e = easeOut(clamp((k + 1) / 4));
		opacity = e;
		dy = (1 - e) * 14;
	} else {
		opacity = clamp((k + 1) / 3);
	}
	const cx = tok.x + tok.w / 2;
	const cy = tok.y - line.size * 0.35;
	const common = {
		x: tok.x,
		y: tok.y + dy,
		fontFamily: st.family,
		fontWeight: st.weight,
		fontStyle: st.italic ? 'italic' : 'normal',
		fontSize: line.size,
		letterSpacing: `${st.tracking}em`,
		opacity,
		transform: scale !== 1 ? `translate(${cx} ${cy}) scale(${scale}) translate(${-cx} ${-cy})` : undefined,
	};
	if (tok.echo) {
		return (
			<text {...common} fill="none" stroke={fill} strokeWidth={Math.max(1.5, line.size / 90)} opacity={0.75}>
				{tok.text}
			</text>
		);
	}
	const small = line.mode !== 'masthead' && line.mode !== 'mass';
	return (
		<text
			{...common}
			fill={fill}
			stroke={small ? edge : undefined}
			strokeWidth={small ? Math.max(2, line.size * 0.07) : undefined}
			strokeLinejoin="round"
			paintOrder="stroke"
			style={{filter: `drop-shadow(0 2px ${small ? 10 : 24}px ${shadow})`}}
		>
			{tok.text}
		</text>
	);
};

export const Lyrics: React.FC<{frame: number}> = ({frame}) => {
	const vis = visibleAt(frame);
	if (!vis.length) {
		return null;
	}
	const {fill, shadow, edge} = colourFor(frame);
	return (
		<svg width={W} height={H} style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
			{vis.map(({line, tokens}) => (
				<g key={`${line.line}.${line.part}`}>
					{line.mode === 'mass' && <Mass line={line} frame={frame} fill={fill} />}
					{line.tag && (
						<text x={line.tag.x} y={line.tag.y} fontFamily={FONT.mono} fontSize={20} letterSpacing="0.08em" fill={fill} opacity={0.7}>
							{line.tag.text}
						</text>
					)}
					{tokens.map((tok, i) => (
						<Word key={i} line={line} tok={tok} frame={frame} fill={fill} shadow={shadow} edge={edge} />
					))}
				</g>
			))}
		</svg>
	);
};
