// The motivated transitions (STYLE_BIBLE.md): mostly hard cuts; every few shots a device that comes out of
// the graphics. A device is named on the incoming shot (shots.json `transition`). Some act on the outgoing
// shot's last frames (tab switch, session close, push-through), some on the incoming shot's first frames
// (window wipe, shape match, terminal scroll, session close, flash); the blink closes on its word.
import React from 'react';
import type {Shot} from '../lib/data';
import {shotAtFrame, shotIndex, shots} from '../lib/data';
import {clamp, easeIn, easeInOut, easeOut, rnd} from '../lib/ease';
import {C, FONT, H, W} from '../lib/theme';
import {FPS} from '../lib/time';

export type Device = 'tab switch' | 'window wipe' | 'blink' | 'session close' | 'push-through' | 'shape match' | 'terminal scroll' | 'flash' | null;

export const deviceOf = (s: Shot | undefined): Device => {
	if (!s) {
		return null;
	}
	const d = ['tab switch', 'window wipe', 'blink', 'session close', 'push-through', 'shape match', 'terminal scroll', 'flash'].find((x) => s.transition.startsWith(x));
	return (d as Device) ?? null;
};

export interface Layer {
	shot: Shot;
	style?: React.CSSProperties;
}

export type Overlay =
	| {kind: 'flash'; a: number}
	| {kind: 'blink'; k: number}
	| {kind: 'tabs'; k: number; active: number}
	| {kind: 'window'; x: number; y: number; w: number; h: number}
	| {kind: 'seam'; y: number; seed: string}
	| {kind: 'line'; k: number};

const PUSH_ORIGIN: Record<string, [number, number]> = {s024: [0.6, 0.58]};

export const transitionState = (frame: number): {layers: Layer[]; overlays: Overlay[]} => {
	const s = shotAtFrame(frame);
	const i = shotIndex[s.id];
	const prev = shots[i - 1];
	const next = shots[i + 1];
	const since = frame - s.f0;
	const until = next ? next.f0 - frame : Infinity;
	let layers: Layer[] = [{shot: s}];
	const overlays: Overlay[] = [];
	switch (deviceOf(s)) {
		case 'window wipe':
			if (prev && since < 10) {
				const k = easeOut((since + 1) / 10);
				const w = W * (0.42 + 0.58 * k);
				const h = H * (0.42 + 0.58 * k);
				const x = (W - w) / 2;
				const y = (H - h) / 2 + (1 - k) * 30;
				layers = [{shot: prev}, {shot: s, style: {clipPath: `inset(${y}px ${W - x - w}px ${H - y - h}px ${x}px round ${14 * (1 - k)}px)`}}];
				if (k < 0.98) {
					overlays.push({kind: 'window', x, y, w, h});
				}
			}
			break;
		case 'shape match':
			if (prev && since < 9) {
				// a button-sized shape grows to the frame, the next shot inside it
				const k = easeInOut((since + 1) / 9);
				const w = 300 + (W - 300) * k;
				const h = 84 + (H - 84) * k;
				const x = (W - w) / 2;
				const y = (H - h) / 2;
				layers = [{shot: prev}, {shot: s, style: {clipPath: `inset(${y}px ${W - x - w}px ${H - y - h}px ${x}px round ${18 * (1 - k)}px)`}}];
			}
			break;
		case 'terminal scroll':
			if (prev && since < 10) {
				const k = easeIn((since + 1) / 10);
				layers = [{shot: s}, {shot: prev, style: {transform: `translateY(${-k * H}px)`}}];
				overlays.push({kind: 'seam', y: H - k * H, seed: s.id});
			}
			break;
		case 'session close':
			if (since < 6) {
				const k = easeOut((since + 1) / 6);
				layers = [{shot: s, style: {transform: `scaleY(${Math.max(0.004, k)})`}}];
				overlays.push({kind: 'line', k: 1 - k});
			}
			break;
		case 'flash':
			if (since < 2) {
				overlays.push({kind: 'flash', a: since === 0 ? 1 : 0.3});
			}
			break;
		case 'tab switch':
			if (since < 5) {
				overlays.push({kind: 'tabs', k: 1 - since / 5, active: 1});
			}
			break;
		case 'blink': {
			const w = s.lyrics.flatMap((l) => l.words).find((x) => /blink/i.test(x.word));
			if (w) {
				const d = frame - Math.round(w.t0 * FPS);
				if (d >= 0 && d < 4) {
					overlays.push({kind: 'blink', k: [0.55, 1, 1, 0.35][d]});
				}
			}
			break;
		}
		default:
			break;
	}
	switch (deviceOf(next)) {
		case 'session close':
			if (until <= 6) {
				const k = easeIn((7 - until) / 6);
				layers = [{shot: s, style: {transform: `scaleY(${Math.max(0.004, 1 - k)})`}}];
				overlays.push({kind: 'line', k});
			}
			break;
		case 'tab switch':
			if (until <= 8) {
				overlays.push({kind: 'tabs', k: easeOut((9 - until) / 8), active: 0});
			}
			break;
		case 'push-through':
			if (until <= 8 && next) {
				const k = easeIn((9 - until) / 8);
				const [ox, oy] = PUSH_ORIGIN[s.id] ?? [0.5, 0.5];
				layers = [{shot: s, style: {transform: `scale(${1 + 2.2 * k})`, transformOrigin: `${ox * 100}% ${oy * 100}%`}}];
			}
			break;
		default:
			break;
	}
	return {layers, overlays};
};

const TABS = ['flights', 'CI · build', 'Q3 deck', 'tests', 'calendar'];

export const Overlays: React.FC<{overlays: Overlay[]}> = ({overlays}) => (
	<>
		{overlays.map((o, idx) => {
			switch (o.kind) {
				case 'flash':
					return <div key={idx} style={{position: 'absolute', inset: 0, background: C.paper, opacity: o.a}} />;
				case 'blink':
					return (
						<React.Fragment key={idx}>
							<div style={{position: 'absolute', left: 0, right: 0, top: 0, height: (H / 2) * o.k + 1, background: '#000'}} />
							<div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: (H / 2) * o.k + 1, background: '#000'}} />
						</React.Fragment>
					);
				case 'line':
					return <div key={idx} style={{position: 'absolute', left: W * (0.5 - 0.5 * (1 - o.k * 0.6)), width: W * (1 - o.k * 0.6), top: H / 2 - 1.5, height: 3, background: C.greenWhite, opacity: 0.9, boxShadow: `0 0 24px ${C.greenWhite}`}} />;
				case 'window':
					return (
						<div key={idx} style={{position: 'absolute', left: o.x, top: o.y - 34, width: o.w, height: o.h + 34, border: `1px solid ${C.hair}`, borderRadius: 12, boxShadow: '0 30px 80px rgba(0,0,0,0.45)', pointerEvents: 'none'}}>
							<div style={{height: 34, background: C.white, borderRadius: '12px 12px 0 0', display: 'flex', alignItems: 'center', gap: 8, paddingLeft: 14}}>
								<span style={{width: 10, height: 10, borderRadius: 5, background: C.terracotta}} />
								<span style={{fontFamily: FONT.sans, fontWeight: 600, fontSize: 15, color: C.ink}}>new window</span>
							</div>
						</div>
					);
				case 'seam':
					return (
						<div key={idx} style={{position: 'absolute', left: 0, right: 0, top: clamp(o.y - 44, -60, H), height: 44, background: C.black, fontFamily: FONT.mono, fontSize: 16, color: C.greenWhite, padding: '12px 32px', whiteSpace: 'pre', overflow: 'hidden'}}>
							{`$ tool_call ${Math.floor(rnd(o.seed) * 9e5 + 1e5)}  {"ok": true}  ${'▍'.repeat(3)}`}
						</div>
					);
				case 'tabs': {
					const y = -64 + 64 * o.k;
					return (
						<div key={idx} style={{position: 'absolute', left: 0, right: 0, top: y, height: 58, background: '#e7e8ea', borderBottom: `1px solid ${C.hair}`, display: 'flex', alignItems: 'flex-end', gap: 4, padding: '0 20px', boxShadow: '0 6px 24px rgba(0,0,0,0.25)'}}>
							{TABS.map((t, j) => (
								<div key={t} style={{height: 42, width: 250, borderRadius: '10px 10px 0 0', background: j === o.active ? C.paper : 'transparent', display: 'flex', alignItems: 'center', gap: 10, padding: '0 16px', fontFamily: FONT.sans, fontSize: 17, color: C.ink}}>
									<span style={{width: 12, height: 12, borderRadius: 3, background: j === o.active ? C.terracotta : C.shadowGrey}} />
									{t}
								</div>
							))}
						</div>
					);
				}
				default:
					return null;
			}
		})}
	</>
);
