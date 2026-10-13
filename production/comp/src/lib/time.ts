// Time on the song's own beat grid. Never rebuild a grid from the BPM: the tempo drifts (song.json).
// Everything here is a pure function of the frame, so frames can render in parallel and out of order.
import {song} from './data';

export const FPS = 24;
export const beats = song.beats_s;
export const downbeats = song.downbeats_s;
const FIRST_BAR = -8; // downbeats_s[0] is bar -8; bar 0 is the first drop

export const sec = (frame: number) => frame / FPS;
export const frameOf = (t: number) => Math.round(t * FPS);

/** Index of the last beat at or before t (-1 before the first). */
export const beatIndex = (t: number): number => {
	let lo = 0;
	let hi = beats.length - 1;
	if (t < beats[0]) {
		return -1;
	}
	while (lo < hi) {
		const mid = (lo + hi + 1) >> 1;
		if (beats[mid] <= t + 1e-9) {
			lo = mid;
		} else {
			hi = mid - 1;
		}
	}
	return lo;
};

const beatLen = (i: number) =>
	i + 1 < beats.length ? beats[i + 1] - beats[i] : beats[beats.length - 1] - beats[beats.length - 2];

/** Where t sits in its beat: the beat's index, 0-1 through it, and its length in seconds. */
export const beatPhase = (t: number) => {
	const i = Math.max(0, beatIndex(t));
	const len = beatLen(i);
	return {i, phase: Math.min(1, Math.max(0, (t - beats[i]) / len)), len, since: t - beats[i]};
};

/** Which eighth note t is in, counted from the first beat (two per beat). */
export const eighthIndex = (t: number) => {
	const {i, phase} = beatPhase(t);
	return i * 2 + (phase >= 0.5 ? 1 : 0);
};

/** Seconds since the last beat, eighth or downbeat. */
export const sinceBeat = (t: number) => beatPhase(t).since;
export const sinceEighth = (t: number) => {
	const {since, len} = beatPhase(t);
	return since >= len / 2 ? since - len / 2 : since;
};
export const isDownbeatIndex = (i: number) => i % 4 === 0;
export const sinceDownbeat = (t: number) => {
	const {i, since} = beatPhase(t);
	const back = i % 4;
	return since + (i - back >= 0 ? beats[i] - beats[i - back] : 0);
};

/** A hit on every beat: 1 on the beat, decaying (decay per second). */
export const pulse = (t: number, decay = 9) => (t < beats[0] ? 0 : Math.exp(-decay * sinceBeat(t)));
export const pulseDown = (t: number, decay = 5) => (t < beats[0] ? 0 : Math.exp(-decay * sinceDownbeat(t)));
export const pulseEighth = (t: number, decay = 14) => (t < beats[0] ? 0 : Math.exp(-decay * sinceEighth(t)));

/** Song seconds of a bar position (bar 0 = the first drop; 35.5 = beat 3 of bar 35). */
export const barTime = (bar: number): number => {
	const b = 4 * (bar - FIRST_BAR);
	const i = Math.floor(b + 1e-9);
	const frac = b - i;
	if (i >= beats.length - 1) {
		const step = beats[beats.length - 1] - beats[beats.length - 2];
		return beats[beats.length - 1] + (b - (beats.length - 1)) * step;
	}
	if (i < 0) {
		return beats[0] + b * beatLen(0);
	}
	return beats[i] + frac * beatLen(i);
};

/** The bar position of a time (inverse of barTime). */
export const barAt = (t: number): number => {
	const {i, phase} = beatPhase(t);
	return (i + phase) / 4 + FIRST_BAR;
};

/** Beats counted from a start time (fractional). */
export const beatsSince = (t: number, t0: number) => {
	const a = beatPhase(t0);
	const b = beatPhase(t);
	return b.i + b.phase - (a.i + a.phase);
};

/** 0-1 progress of t through [a, b], clamped. */
export const seg = (t: number, a: number, b: number) => (b <= a ? (t >= b ? 1 : 0) : Math.min(1, Math.max(0, (t - a) / (b - a))));

export const sectionAt = (t: number) => song.sections.find((s) => t >= s.start && t < s.end) ?? song.sections[song.sections.length - 1];
