// Her tracking, where it exists (BRIEF.md step 5): per frame for a clip (production/clips/tracking/<clip>.json, from
// tools/track.py), and still for a plate (production/assets/boxes/<plate>.json, from tools/boxes.py), bundled by
// scripts/scan-media.mjs. Boxes and landmarks are in 1920x1080 frame pixels of the footage as it arrives; `onScreen`
// moves them by the shot's camera, as the print pass moves the footage. Where there's no data, callers fall back to
// layout.ts's planned boxes.
import trackingJson from '../data/tracking.generated.json';
import {defaultCam} from './camera';
import {clips, type Shot} from './data';
import {clamp} from './ease';
import type {Box} from './layout';
import {clipFile, plateFile} from './media';
import {isUntracked} from './registry';
import {H, W} from './theme';
import {FPS} from './time';

export interface Track {
	face: Box | null;
	/** The tracking layer's twelve: eye corners left to right, pupils, brows, nose tip, lip corners, lower lip. */
	landmarks: [number, number][];
	body: Box | null;
}

interface ClipTrack {
	fps: number;
	width: number;
	height: number;
	frames: ({f: number} & Track)[];
}

const data = trackingJson as unknown as {clips: Record<string, ClipTrack>; plates: Record<string, Track & {bodies?: Box[]}>};

/** How much of a figure's box its head takes, by the shot's framing: a whole figure's head is about a sixth of it,
 * a medium shot shows her from the waist up, a medium close-up from the chest. */
const HEAD: Record<string, number> = {EWS: 1 / 7, WS: 1 / 6, FS: 1 / 6, MS: 1 / 2.6, MCU: 1 / 1.8};

/** A figure's head, from its body box: centred at the top, as wide as it is tall at most. */
const headOf = (b: Box, framing: string): Box => {
	const h = b.h * (HEAD[framing] ?? 1 / 6);
	const w = Math.min(b.w, h * 1.3);
	return {x: b.x + (b.w - w) / 2, y: b.y, w, h};
};

/** The frame of the shot's take on screen at a comp frame: from `clip_in_s`, held on the last frame if the shot holds. */
export const clipFrameAt = (shot: Shot, frame: number, frames: number) => {
	let f = frame - shot.f0 + Math.round((shot.clip_in_s ?? 0) * FPS);
	const hold = (shot.clip_holds ?? []).find(([a, b]) => f >= a && f <= b);
	if (hold) {
		f = hold[2]; // the board holds the take on one frame here (Footage.tsx shows the same)
	}
	return Math.max(0, Math.min(frames - 1, f));
};

/** A formation shot: a dancer clip's matte copied into a chapter's slots (ShotView tracks her copy instead). */
const isDancer = (shot: Shot) => Boolean(shot.clip && clips[shot.clip]?.kind === 'dancer');

/** Her tracking at a comp frame, before the camera: the clip's frame if the shot shows a tracked clip, else its plate's. */
export const trackAt = (shot: Shot, frame: number): Track | null => {
	// an extreme close-up is one eye or two: no face for the landmarker, and the whole frame for the body detector;
	// and a shot whose chapter replaces its footage with a split or a pull-back doesn't show her where the clip did
	if (shot.framing === 'ECU' || isUntracked(shot.id) || isDancer(shot)) {
		return null;
	}
	const clip = shot.clip ? data.clips[shot.clip] : undefined;
	if (clip && clip.frames.length) {
		return clip.frames[clipFrameAt(shot, frame, clip.frames.length)];
	}
	const plate = shot.plate ?? (shot.clip ? clips[shot.clip]?.plate : null);
	// a dancer shot's own plate is its empty stage, and a clip without tracking still shows its plate only as a card
	if (!plate || (shot.clip && clips[shot.clip]?.kind === 'dancer')) {
		return null;
	}
	return data.plates[plate] ?? null;
};

export const hasTracking = (shot: Shot) =>
	shot.framing !== 'ECU' && !isUntracked(shot.id) && !isDancer(shot) && Boolean((shot.clip && data.clips[shot.clip]) || (shot.plate && data.plates[shot.plate]));

const union = (a: Box | null, b: Box | null): Box | null => {
	if (!a || !b) {
		return a ?? b;
	}
	const x = Math.min(a.x, b.x);
	const y = Math.min(a.y, b.y);
	return {x, y, w: Math.max(a.x + a.w, b.x + b.w) - x, h: Math.max(a.y + a.h, b.y + b.h) - y};
};

/** Whether the shot's footage is its plate over a depth map (so its default camera drifts), as Footage.tsx decides. */
const onDepth = (shot: Shot) => {
	const clip = shot.clip ? clips[shot.clip] : null;
	return !clipFile(shot.clip) && clip?.kind !== 'dancer' && Boolean(plateFile(shot.plate ?? clip?.plate ?? null)?.depth);
};

/** Her face on screen over a stretch of song time in a shot: the union of her boxes, each moved by the shot's
 * default camera (a chapter's own camera override isn't counted), for placing a line's type clear of her. */
export const faceOver = (shot: Shot, t0: number, t1: number): Box | null => {
	if (!hasTracking(shot)) {
		return null;
	}
	let box: Box | null = null;
	const depth = onDepth(shot);
	const f0 = Math.max(shot.f0, Math.round(t0 * FPS));
	const f1 = Math.min(shot.f1 - 1, Math.round(t1 * FPS));
	// a wide plate with no face found (the figures too small): their heads, except looking straight down on them
	const plate = !shot.clip || !data.clips[shot.clip] ? data.plates[shot.plate ?? ''] : undefined;
	const heads = plate && !plate.face && shot.framing !== 'OVERHEAD' ? (plate.bodies ?? []).map((b) => headOf(b, shot.framing)) : [];
	for (let f = f0; f <= f1; f += 2) {
		const cam = defaultCam({shot, t: f / FPS, p: clamp((f / FPS - shot.t0) / (shot.t1 - shot.t0))}, depth);
		box = union(box, boxOnScreen(trackAt(shot, f)?.face ?? null, cam, shot.footage_x ?? 0));
		for (const h of heads) {
			box = union(box, boxOnScreen(h, cam, shot.footage_x ?? 0));
		}
	}
	return box;
};

/** A point of the footage where the shot's camera puts it on screen: the zoom about its focus, as the print pass,
 * then the shot's sideways move of its footage (`footage_x`). */
export const onScreen = (x: number, y: number, cam: {zoom: number; fx: number; fy: number}, dx = 0): [number, number] => {
	const fx = cam.fx * W;
	const fy = cam.fy * H;
	return [fx + (x - fx) * cam.zoom + dx, fy + (y - fy) * cam.zoom];
};

export const boxOnScreen = (b: Box | null, cam: {zoom: number; fx: number; fy: number}, dx = 0): Box | null => {
	if (!b) {
		return null;
	}
	const [x, y] = onScreen(b.x, b.y, cam, dx);
	return {x, y, w: b.w * cam.zoom, h: b.h * cam.zoom};
};
