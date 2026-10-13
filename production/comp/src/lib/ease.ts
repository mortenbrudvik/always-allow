// Easing and small maths helpers. Pure functions only.
import {random} from 'remotion';

export const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a: number, b: number, k: number) => a + (b - a) * k;
export const smooth = (k: number) => {
	const x = clamp(k);
	return x * x * (3 - 2 * x);
};
export const easeOut = (k: number) => 1 - Math.pow(1 - clamp(k), 3);
export const easeIn = (k: number) => Math.pow(clamp(k), 3);
export const easeInOut = (k: number) => {
	const x = clamp(k);
	return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
};
/** Overshoot then settle, for type slams. */
export const backOut = (k: number, s = 1.9) => {
	const x = clamp(k) - 1;
	return 1 + (s + 1) * x * x * x + s * x * x;
};
/** Keyframes [[t, v], ...] sampled at t with an easing between them. */
export const kf = (t: number, keys: [number, number][], ease: (k: number) => number = smooth) => {
	if (t <= keys[0][0]) {
		return keys[0][1];
	}
	for (let i = 0; i < keys.length - 1; i++) {
		const [t0, v0] = keys[i];
		const [t1, v1] = keys[i + 1];
		if (t <= t1) {
			return lerp(v0, v1, ease((t - t0) / (t1 - t0)));
		}
	}
	return keys[keys.length - 1][1];
};

/** Deterministic randomness: Remotion's random(seed), never Math.random. */
export const rnd = (...seed: (string | number)[]) => random(seed.join(':'));
export const rndRange = (a: number, b: number, ...seed: (string | number)[]) => a + (b - a) * rnd(...seed);
export const rndInt = (a: number, b: number, ...seed: (string | number)[]) => Math.floor(rndRange(a, b + 1, ...seed));

/** Smooth noise in time: a jitter that changes `rate` times a second (tracking wobble, hand-held drift). */
export const wob = (t: number, rate: number, ...seed: (string | number)[]) => {
	const x = t * rate;
	const i = Math.floor(x);
	const f = x - i;
	const a = rnd(...seed, i) * 2 - 1;
	const b = rnd(...seed, i + 1) * 2 - 1;
	return lerp(a, b, smooth(f));
};

export const fmt = (n: number) => Math.round(n).toLocaleString('en-US');
export const pad = (n: number, w: number) => String(Math.floor(n)).padStart(w, '0');
