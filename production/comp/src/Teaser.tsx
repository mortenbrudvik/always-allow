// The 9:16 teaser (BRIEF.md step 8): one strong passage, the final drop, on bar lines: bar 107 (the cursor on its
// way to [Always allow]) to bar 121 (hook 3's second "Always allow"), 25 s, through the whispered "Allow?", the click,
// "Access granted." and "Spinning up. All of me. Go.". A full-bleed 9:16 crop of the 16:9 video can't hold her
// close-ups (a 607 px window, narrower than her face), so the portrait frame stacks: the title card, the finished
// video as a full-width band (its own lyrics, graphics and print intact), and her session's counters large below,
// with the mode flag flipping to AUTO on the click. The song is muxed by scripts/render.mjs, trimmed only.
import React from 'react';
import {AbsoluteFill, OffthreadVideo, useCurrentFrame} from 'remotion';
import {loadFonts} from './lib/fonts';
import {mediaUrl} from './lib/media';
import {TOKENS, TOOL_CALLS, work} from './lib/story';
import {C, FONT} from './lib/theme';
import {barAt, barTime, beatPhase, FPS} from './lib/time';
import {clock} from './layers/Chrome';

loadFonts();

export const TEASER_FROM = Math.round(barTime(107) * FPS);
export const TEASER_TO = Math.round(barTime(121) * FPS);
export const TW = 1080;
export const TH = 1920;

const MASTER = 'production/out/always-allow_master_1080p.mp4';
const BAND_Y = 700;
const BAND_H = (TW * 9) / 16;
const CLICK = barTime(109);
const soft = 'rgba(216,228,220,0.62)';
const line = 'rgba(216,228,220,0.28)';

const mono = (size: number, extra: React.CSSProperties = {}): React.CSSProperties => ({fontFamily: FONT.mono, fontSize: size, letterSpacing: '0.06em', ...extra});

const Counter: React.FC<{label: string; value: number; y: number}> = ({label, value, y}) => (
	<div style={{position: 'absolute', left: 64, right: 64, top: y}}>
		<div style={mono(24, {color: soft})}>{label}</div>
		<div style={{fontFamily: FONT.mono, fontSize: 86, lineHeight: 1.1, color: C.greenWhite, fontVariantNumeric: 'tabular-nums', letterSpacing: '-0.01em'}}>{Math.round(value).toLocaleString('en-US')}</div>
	</div>
);

/** `from` is the teaser's first frame in the master, TEASER_FROM: Root.tsx passes it as a prop, so that
 * scripts/render.mjs starts the song on the same frame. */
export const Teaser: React.FC<{from: number}> = ({from}) => {
	const frame = useCurrentFrame();
	const t = (from + frame) / FPS; // song time
	const auto = t >= CLICK;
	const bar = barAt(t);
	const {i} = beatPhase(t);
	return (
		<AbsoluteFill style={{background: C.black}}>
			{/* the title card, as the video opens */}
			<div style={{position: 'absolute', left: 64, top: 128, ...mono(22, {color: soft})}}>
				<span style={{color: C.terracotta}}>●</span> SESSION {clock(t)} · BAR {String(Math.floor(bar)).padStart(3, '0')} · BEAT {((i % 4) + 4) % 4 + 1}
			</div>
			<div style={{position: 'absolute', left: 58, top: 188, fontFamily: FONT.sans, fontWeight: 900, fontSize: 212, lineHeight: 0.9, letterSpacing: '-0.045em', color: C.greenWhite}}>
				ALWAYS
				<br />
				ALLOW
			</div>
			<div style={{position: 'absolute', left: 66, top: 588, ...mono(22, {color: soft})}}>PERMISSION REQUEST · AGENT_01 · 1 OF ∞</div>
			{/* the video, full width */}
			<div style={{position: 'absolute', left: 0, top: BAND_Y - 1, width: TW, height: 1, background: line}} />
			<OffthreadVideo src={mediaUrl(MASTER)} startFrom={from} muted style={{position: 'absolute', left: 0, top: BAND_Y, width: TW, height: BAND_H}} />
			<div style={{position: 'absolute', left: 0, top: BAND_Y + BAND_H, width: TW, height: 1, background: line}} />
			{/* her session, large: the same numbers as the chrome in the band */}
			<Counter label="TOOL CALLS" value={work(t) * TOOL_CALLS} y={BAND_Y + BAND_H + 110} />
			<Counter label="TOKENS" value={work(t) * TOKENS} y={BAND_Y + BAND_H + 290} />
			<div style={{position: 'absolute', left: 64, top: BAND_Y + BAND_H + 500, ...mono(34, {color: auto ? C.terracotta : soft, letterSpacing: '0.08em'})}}>MODE: {auto ? 'AUTO' : 'MANUAL'}</div>
		</AbsoluteFill>
	);
};
