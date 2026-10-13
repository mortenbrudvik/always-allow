// The lyric engine: where and when every lyric word is on screen. Pure, so the renderer (layers/Lyrics.tsx)
// and the check (scripts/check-lyrics.ts) use the same answers. BRIEF.md: every word in words.json is on
// screen on its time; the main lyric is never under 40 px at 1080p; type never goes over her face.
import metricsJson from '../data/font-metrics.json';
import type {Lyric, Mode, Shot, Zone} from './data';
import {shots} from './data';
import {type Box, clipZone, intersects, plannedFace, type ZoneBox, ZONES} from './layout';
import {formationAt} from './registry';
import {faceOver} from './tracking';
import {FPS} from './time';

type FaceKey = 'sans900' | 'sans700' | 'sans500' | 'serifItalic' | 'mono400' | 'mono700';
interface FaceMetrics {
	ascender: number;
	descender: number;
	capHeight: number;
	fallback: number;
	adv: Record<string, number>;
}
const metrics = metricsJson as unknown as Record<FaceKey, FaceMetrics>;

export interface ModeStyle {
	face: FaceKey;
	family: string;
	weight: number;
	italic: boolean;
	upper: boolean;
	tracking: number; // em
	lineHeight: number; // em
	maxSize: number;
	minSize: number;
	maxRows: number;
}

export const MODE_STYLE: Record<Mode, ModeStyle> = {
	masthead: {face: 'sans900', family: 'Geist', weight: 900, italic: false, upper: true, tracking: -0.045, lineHeight: 0.9, maxSize: 400, minSize: 120, maxRows: 4},
	coverline: {face: 'sans700', family: 'Geist', weight: 700, italic: false, upper: false, tracking: -0.025, lineHeight: 1.0, maxSize: 112, minSize: 72, maxRows: 5},
	subtitle: {face: 'sans500', family: 'Geist', weight: 500, italic: false, upper: false, tracking: -0.005, lineHeight: 1.18, maxSize: 52, minSize: 46, maxRows: 2},
	serif: {face: 'serifItalic', family: 'Instrument Serif', weight: 400, italic: true, upper: false, tracking: 0, lineHeight: 1.1, maxSize: 64, minSize: 54, maxRows: 2},
	mass: {face: 'sans900', family: 'Geist', weight: 900, italic: false, upper: true, tracking: -0.045, lineHeight: 0.9, maxSize: 360, minSize: 160, maxRows: 2},
};

export const MIN_LYRIC_PX = 40;
const TAIL_S = 0.25; // a line stays at least this long after its last word (STYLE_BIBLE.md)
const HOLD_MAX_S = 2.5; // mastheads and coverlines hold to their shot's end, but no longer than this

export const textWidth = (text: string, face: FaceKey, size: number, tracking = 0) => {
	const m = metrics[face];
	let w = 0;
	for (const ch of text) {
		w += m.adv[ch] ?? m.fallback;
	}
	return (w + tracking * Math.max(0, [...text].length - 1)) * size;
};

export interface Token {
	text: string; // as displayed
	word: string | null; // the words.json word it shows (null for an echo)
	t0: number; // when it appears
	t1: number; // the word's end
	echo: boolean;
	x: number;
	y: number; // baseline
	w: number;
}

export interface PlacedLine {
	line: number;
	part: number; // 0, or 1 for the tail of a split line
	text: string;
	mode: Mode;
	zone: Zone;
	boardZone: Zone;
	shot: Shot;
	style: ModeStyle;
	size: number;
	t0: number; // first word
	tEnd: number; // when the whole line goes
	box: Box;
	tokens: Token[];
	faceClash: boolean;
	tag: {x: number; y: number; text: string} | null; // a coverline's mono tag above it: its line number and time
}

const TAG_PX = 20;
const mmss = (t: number) => `${Math.floor(t / 60)}:${(t % 60).toFixed(2).padStart(5, '0')}`;

/** A coverline's tag, 14 px above its block, unless that would touch her face or the chrome. */
const tagOf = (line: number, t0: number, box: Box, face: Box | null) => {
	const y = box.y - 14;
	const tagBox = {x: box.x, y: y - TAG_PX, w: 320, h: TAG_PX + 6};
	if (y - TAG_PX < 110 || (face && intersects(tagBox, face))) {
		return null;
	}
	return {x: box.x, y, text: `LINE ${String(line + 1).padStart(2, '0')} · ${mmss(t0)}`};
};

const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9']/g, '');

/** Split a line's text into display tokens and pair them with its timed words; "(always)" is an echo. */
const tokenise = (lyric: Lyric): Omit<Token, 'x' | 'y' | 'w'>[] => {
	const parts = lyric.text.split(/\s+/).filter(Boolean);
	const out: Omit<Token, 'x' | 'y' | 'w'>[] = [];
	let wi = 0;
	for (const part of parts) {
		if (part.startsWith('(')) {
			const prev = lyric.words[Math.max(0, wi - 1)];
			out.push({text: part, word: null, t0: prev.t1 + 0.4, t1: prev.t1 + 0.9, echo: true});
			continue;
		}
		const w = lyric.words[wi];
		if (!w || norm(part) !== norm(w.word)) {
			throw new Error(`line ${lyric.line}: token ${part} doesn't match word ${w?.word}`);
		}
		out.push({text: part, word: w.word, t0: w.t0, t1: w.t1, echo: false});
		wi++;
	}
	if (wi !== lyric.words.length) {
		throw new Error(`line ${lyric.line}: ${lyric.words.length - wi} words left unmatched`);
	}
	return out;
};

interface Fit {
	size: number;
	rows: {tokens: number[]; w: number}[];
}

/** Greedy wrap of the tokens at a size; null if a row can't fit. */
const wrap = (texts: string[], st: ModeStyle, size: number, maxW: number): Fit | null => {
	const space = textWidth(' ', st.face, size);
	const rows: {tokens: number[]; w: number}[] = [];
	let cur: number[] = [];
	let curW = 0;
	for (let i = 0; i < texts.length; i++) {
		const w = textWidth(texts[i], st.face, size, st.tracking);
		if (w > maxW) {
			return null;
		}
		const add = cur.length ? space + w : w;
		if (cur.length && curW + add > maxW) {
			rows.push({tokens: cur, w: curW});
			cur = [i];
			curW = w;
		} else {
			cur.push(i);
			curW += add;
		}
	}
	if (cur.length) {
		rows.push({tokens: cur, w: curW});
	}
	return {size, rows};
};

const fitIn = (texts: string[], st: ModeStyle, zone: Box): Fit => {
	for (let size = st.maxSize; size >= st.minSize; size = Math.floor(size * 0.96)) {
		const f = wrap(texts, st, size, zone.w);
		if (f && f.rows.length <= st.maxRows && f.rows.length * size * st.lineHeight <= zone.h) {
			return f;
		}
	}
	// at the minimum size, allow the rows it needs; if even one word is too wide, it all goes on one row, measured at
	// its true width (reporting the zone's width let a line that overflowed run over her face unseen: s090, 30 Sep)
	const f = wrap(texts, st, st.minSize, zone.w);
	if (f) {
		return f;
	}
	const space = textWidth(' ', st.face, st.minSize);
	const w = texts.reduce((sum, t, i) => sum + (i ? space : 0) + textWidth(t, st.face, st.minSize, st.tracking), 0);
	return {size: st.minSize, rows: [{tokens: texts.map((_, i) => i), w}]};
};

const place = (zone: Zone, z: ZoneBox, texts: string[], st: ModeStyle) => {
	const fit = fitIn(texts, st, z);
	const lh = fit.size * st.lineHeight;
	const blockH = fit.rows.length * lh;
	// subtitles sit at the foot of their zone (the head of the top zone, the middle of the centre zone);
	// mastheads and coverlines follow the zone's alignment
	const small = st === MODE_STYLE.subtitle || st === MODE_STYLE.serif;
	const v = small ? (zone === 'top' ? 'top' : zone === 'center' ? 'center' : 'bottom') : z.v;
	const top = v === 'top' ? z.y : v === 'bottom' ? z.y + z.h - blockH : z.y + (z.h - blockH) / 2;
	const blockW = Math.max(...fit.rows.map((r) => r.w));
	const left = z.align === 'center' ? z.x + (z.w - blockW) / 2 : z.x;
	const positions: {x: number; y: number; w: number}[] = [];
	const space = textWidth(' ', st.face, fit.size);
	fit.rows.forEach((row, r) => {
		let x = z.align === 'center' ? z.x + (z.w - row.w) / 2 : z.x;
		const y = top + r * lh + fit.size * metrics[st.face].capHeight + (lh - fit.size) / 2;
		for (const i of row.tokens) {
			const w = textWidth(texts[i], st.face, fit.size, st.tracking);
			positions[i] = {x, y, w};
			x += w + space;
		}
	});
	return {size: fit.size, box: {x: left, y: top, w: blockW, h: blockH}, positions};
};

const CANDIDATES: Record<Zone, Zone[]> = {
	left: ['left', 'right', 'bottom', 'top'],
	right: ['right', 'left', 'bottom', 'top'],
	top: ['top', 'bottom', 'left', 'right'],
	bottom: ['bottom', 'top', 'left', 'right'],
	center: ['center', 'left', 'right', 'bottom', 'top'],
	ui: ['ui', 'bottom', 'top'],
};

type RawToken = ReturnType<typeof tokenise>[number];

const union = (a: Box | null, b: Box | null): Box | null => {
	if (!a || !b) {
		return a ?? b;
	}
	const x = Math.min(a.x, b.x);
	const y = Math.min(a.y, b.y);
	return {x, y, w: Math.max(a.x + a.w, b.x + b.w) - x, h: Math.max(a.y + a.h, b.y + b.h) - y};
};

/** The heads of a formation's front over a stretch of song time: her own copy (AGENT_01) and the copies nearest the
 * camera (within a fifth of the tallest), where they're big enough to show a face (120 px tall or more); each head
 * is about a sixth of the figure's height at the top of it. The rows behind are texture: a masthead over a crowd
 * of thousands always crosses some of them. */
const formationHeads = (shot: Shot, t0: number, t1: number): Box | null => {
	let box: Box | null = null;
	for (let f = Math.max(shot.f0, Math.round(t0 * FPS)); f <= Math.min(shot.f1 - 1, Math.round(t1 * FPS)); f += 3) {
		const slots = formationAt(shot, f) ?? [];
		const tallest = Math.max(0, ...slots.map((s) => s.h));
		for (const s of slots) {
			if (s.h >= 120 && (s.agent || s.h >= 0.8 * tallest)) {
				box = union(box, {x: s.x - s.h * 0.1, y: s.y - s.h, w: s.h * 0.2, h: s.h * 0.17});
			}
		}
	}
	return box;
};

/** One run of a line's tokens in one mode and zone, placed clear of her face and timed. */
const partOf = (shot: Shot, lyric: Lyric, part: number, raw: RawToken[], mode: Mode, zone: Zone, endBy: number): PlacedLine => {
	const st = MODE_STYLE[mode];
	const texts = raw.map((t) => (st.upper ? t.text.toUpperCase() : t.text));
	const lastEnd = Math.max(...raw.map((t) => t.t1));
	const lastShot = shots.find((s) => lastEnd >= s.t0 && lastEnd < s.t1) ?? shot;
	const holds = mode === 'masthead' || mode === 'coverline' || mode === 'mass';
	let tEnd = Math.min(holds ? Math.max(lastEnd + TAIL_S, Math.min(lastShot.t1, lastEnd + HOLD_MAX_S)) : lastEnd + TAIL_S, endBy);
	// her face, and the heads of her copies where she stands in formation, in a stretch of a shot: tracked where she
	// is, else where the board plans her, each on its own (the type has to clear every one, not their outline)
	const facesIn = (s: Shot, a: number, b: number) =>
		[faceOver(s, a, b) ?? plannedFace(s), formationHeads(s, a, b)].filter((f): f is Box => f !== null);
	// the line has to clear her in every shot while its words are sung; a hold past them ends at the cut to a shot
	// where it wouldn't (below)
	const sungTo = Math.max(...raw.filter((t) => !t.echo).map((t) => t.t1));
	const faces: Box[] = [];
	for (const s of shots) {
		const a = Math.max(raw[0].t0, s.t0);
		const b = Math.min(sungTo, tEnd, s.t1);
		if (b > a) {
			faces.push(...facesIn(s, a, b));
		}
	}
	const hits = (b: Box) => faces.some((f) => intersects(b, f));
	// the line must fit its space too: at the minimum size a long word can overflow it, off the frame or onto her
	const inside = (b: Box, z: Box) => b.x >= z.x - 1 && b.x + b.w <= z.x + z.w + 1 && b.y >= z.y - 1 && b.y + b.h <= z.y + z.h + 1;
	let chosen = zone;
	let placed = place(chosen, ZONES[chosen], texts, st);
	let clash = hits(placed.box) || !inside(placed.box, ZONES[chosen]);
	if (clash) {
		// the board's zone first, shrunk to the space beside, above or below each face; then the other zones
		for (const z of CANDIDATES[zone]) {
			let box: ZoneBox | null = ZONES[z];
			for (const f of faces) {
				box = box && clipZone(box, f);
			}
			if (!box) {
				continue;
			}
			const p = place(z, box, texts, st);
			if (!hits(p.box) && inside(p.box, box)) {
				chosen = z;
				placed = p;
				clash = false;
				break;
			}
		}
	}
	const face = faces.reduce<Box | null>((u, f) => union(u, f), null);
	// a hold into a later shot where the line would sit on her face ends at that cut instead
	for (const s of shots) {
		if (s.t0 >= sungTo && s.t0 < tEnd && facesIn(s, s.t0, tEnd).some((f) => intersects(placed.box, f))) {
			tEnd = s.t0;
			break;
		}
	}
	return {
		line: lyric.line,
		part,
		text: raw.map((t) => t.text).join(' '),
		mode,
		zone: chosen,
		boardZone: zone,
		shot,
		style: st,
		size: placed.size,
		t0: raw[0].t0,
		tEnd: Math.min(tEnd, endBy),
		box: placed.box,
		tokens: raw.map((t, i) => ({...t, text: texts[i], ...placed.positions[i]})),
		faceClash: clash,
		tag: mode === 'coverline' ? tagOf(lyric.line, raw[0].t0, placed.box, face) : null,
	};
};

const linesOf = (shot: Shot, lyric: Lyric, nextStart: number): PlacedLine[] => {
	const raw = tokenise(lyric);
	if (!lyric.split) {
		return [partOf(shot, lyric, 0, raw, lyric.mode, lyric.zone, nextStart)];
	}
	// the token where word `at` starts (echo tokens aren't words)
	let words = 0;
	const cut = raw.findIndex((t) => !t.echo && words++ === lyric.split!.at);
	if (cut <= 0) {
		throw new Error(`line ${lyric.line}: split at word ${lyric.split.at} is outside the line`);
	}
	const tail = raw.slice(cut);
	return [
		partOf(shot, lyric, 0, raw.slice(0, cut), lyric.mode, lyric.zone, tail[0].t0),
		partOf(shot, lyric, 1, tail, lyric.split.mode, lyric.split.zone, nextStart),
	];
};

const all: {shot: Shot; lyric: Lyric}[] = shots
	.flatMap((shot) => shot.lyrics.map((lyric) => ({shot, lyric})))
	.sort((a, b) => a.lyric.words[0].t0 - b.lyric.words[0].t0);

let placedCache: PlacedLine[] | null = null;

/** Every line placed, worked out on first use: after the chapters have registered their formations. */
export const placedLines = (): PlacedLine[] =>
	(placedCache ??= all.flatMap(({shot, lyric}, i) => linesOf(shot, lyric, i + 1 < all.length ? all[i + 1].lyric.words[0].t0 : Infinity)));

const frameIn = (t: number) => Math.round(t * FPS);

/** The lines on screen at a frame, each with the tokens that have appeared. */
export const visibleAt = (frame: number) => {
	const out: {line: PlacedLine; tokens: Token[]}[] = [];
	for (const line of placedLines()) {
		if (frame < frameIn(line.t0) || frame >= frameIn(line.tEnd)) {
			continue;
		}
		const tokens = line.tokens.filter((t) => frame >= frameIn(t.t0));
		if (tokens.length) {
			out.push({line, tokens});
		}
	}
	return out;
};
