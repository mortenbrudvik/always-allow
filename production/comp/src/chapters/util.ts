// Helpers for chapter files: word times by line number, entrance progress, typewriter text. Pure.
import {wordsFile} from '../lib/data';
import {clamp, easeOut} from '../lib/ease';
import type {Box} from '../lib/layout';
import {type PlacedLine, placedLines} from '../lib/lyrics';

/** Where the lyric engine put a line (its tail with part 1, if the line is split), to keep graphics off it. */
export const lyricOf = (line: number, part = 0): PlacedLine => {
	const l = placedLines().find((x) => x.line === line && x.part === part);
	if (!l) {
		throw new Error(`line ${line} part ${part} isn't placed`);
	}
	return l;
};
export const lyricBox = (line: number, part = 0): Box => lyricOf(line, part).box;

/** A word's start time: line number and word index (negative counts from the end). */
export const wordAt = (line: number, idx = 0) => {
	const ws = wordsFile.lines[line].words;
	return ws[idx < 0 ? ws.length + idx : idx].start;
};
export const wordEnd = (line: number, idx = -1) => {
	const ws = wordsFile.lines[line].words;
	return ws[idx < 0 ? ws.length + idx : idx].end;
};
/** The start of the first word matching `re` in a line. */
export const wordNamed = (line: number, re: RegExp) => wordsFile.lines[line].words.find((w) => re.test(w.word))?.start ?? wordAt(line);

/** 0 before t0, rising to 1 over `dur` seconds (eased out). */
export const inAt = (t: number, t0: number, dur = 0.3) => easeOut(clamp((t - t0) / dur));
/** 1 until t0, falling to 0 over `dur`. */
export const outAt = (t: number, t0: number, dur = 0.3) => 1 - clamp((t - t0) / dur);

/** Text typed from t0 at `cps` characters a second. */
export const typed = (text: string, t: number, t0: number, cps = 22) => text.slice(0, Math.max(0, Math.floor((t - t0) * cps)));

export const fmtInt = (n: number) => Math.round(n).toLocaleString('en-US');

/**
 * A CSS transform that pins a w x h element (transform-origin 0 0, at left 0, top 0) onto four points of the frame,
 * top-left, top-right, bottom-right, bottom-left: for UI on a screen or panel in a plate, in its perspective.
 */
export const quad = (w: number, h: number, c: [[number, number], [number, number], [number, number], [number, number]]) => {
	const [[x0, y0], [x1, y1], [x2, y2], [x3, y3]] = c;
	const dx1 = x1 - x2;
	const dx2 = x3 - x2;
	const dx3 = x0 - x1 + x2 - x3;
	const dy1 = y1 - y2;
	const dy2 = y3 - y2;
	const dy3 = y0 - y1 + y2 - y3;
	const den = dx1 * dy2 - dx2 * dy1;
	const g = (dx3 * dy2 - dx2 * dy3) / den;
	const k = (dx1 * dy3 - dx3 * dy1) / den;
	const a = x1 - x0 + g * x1;
	const b = x3 - x0 + k * x3;
	const d = y1 - y0 + g * y1;
	const e = y3 - y0 + k * y3;
	const m = [a / w, d / w, 0, g / w, b / h, e / h, 0, k / h, 0, 0, 1, 0, x0, y0, 0, 1];
	return `matrix3d(${m.map((v) => +v.toFixed(8)).join(',')})`;
};
