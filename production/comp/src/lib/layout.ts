// Where things are in a shot's frame before the tracking data exists (BRIEF.md step 5 makes it):
// her planned face and body boxes from the board's framing and placement, and the text zones.
// Once production/clips/tracking/<clip>.json exists, Tracking.tsx and the lyric engine use it instead.
import type {Place, Shot, Zone} from './data';
import {H, MARGIN, W} from './theme';

export interface Box {
	x: number;
	y: number;
	w: number;
	h: number;
}

const cx = (place: Place, left: number, center: number, right: number) =>
	place === 'left' ? left : place === 'right' ? right : center;

/** Her face in 1920x1080 pixels, as planned (null when it's too small to matter, or not there). */
export const plannedFace = (shot: Pick<Shot, 'framing' | 'place' | 'agent_on_screen' | 'face'>): Box | null => {
	if (!shot.agent_on_screen || shot.place === 'none' || shot.place === 'small') {
		return null;
	}
	switch (shot.framing) {
		case 'ECU':
			return shot.place === 'full' ? {x: 260, y: 300, w: 1400, h: 480} : {x: 900, y: 60, w: 980, h: 960};
		case 'CU': {
			const w = 460;
			return {x: cx(shot.place, 470, 730, 990), y: 140, w, h: 620};
		}
		case 'MCU': {
			const w = 300;
			return {x: cx(shot.place, 560, 810, 1060), y: 170, w, h: 380};
		}
		case 'MS':
			return {x: cx(shot.place, 640, 885, 1130), y: 210, w: 150, h: 200};
		default:
			return null;
	}
};

/** Her body in the frame, as planned: for the body box in mediums and wides. */
export const plannedBody = (shot: Pick<Shot, 'framing' | 'place' | 'agent_on_screen'>): Box | null => {
	if (!shot.agent_on_screen || shot.place === 'none') {
		return null;
	}
	switch (shot.framing) {
		case 'MCU':
			return {x: cx(shot.place, 420, 700, 950), y: 150, w: 520, h: 930};
		case 'MS':
			return {x: cx(shot.place, 560, 800, 1050), y: 180, w: 320, h: 900};
		case 'FS':
			return {x: 850, y: 260, w: 220, h: 760};
		case 'WS':
			// where the storyboard card draws her figure (Card.tsx)
			return shot.place === 'small' ? {x: 1145, y: 770, w: 90, h: 200} : {x: cx(shot.place, 591, 860, 1110), y: 530, w: 200, h: 440};
		default:
			return null;
	}
};

export interface ZoneBox extends Box {
	align: 'left' | 'center';
	v: 'top' | 'center' | 'bottom';
}

export const ZONES: Record<Zone, ZoneBox> = {
	left: {x: MARGIN, y: 150, w: 800, h: 780, align: 'left', v: 'center'},
	right: {x: W - MARGIN - 800, y: 150, w: 800, h: 780, align: 'left', v: 'center'},
	top: {x: MARGIN, y: 120, w: W - 2 * MARGIN, h: 400, align: 'left', v: 'top'},
	bottom: {x: MARGIN, y: 640, w: W - 2 * MARGIN, h: 360, align: 'left', v: 'bottom'},
	center: {x: MARGIN, y: 150, w: W - 2 * MARGIN, h: 780, align: 'center', v: 'center'},
	ui: {x: MARGIN, y: 640, w: W - 2 * MARGIN, h: 360, align: 'center', v: 'bottom'},
};

export const intersects = (a: Box, b: Box) => a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;

const OPPOSITE: Record<Zone, Zone> = {left: 'right', right: 'left', top: 'bottom', bottom: 'top', center: 'bottom', ui: 'bottom'};

/** The zone a line goes in: its board zone, unless that would put type over her face. */
export const resolveZone = (zone: Zone, face: Box | null): Zone => {
	if (!face) {
		return zone;
	}
	if (!intersects(ZONES[zone], face)) {
		return zone;
	}
	if (zone === 'center') {
		// a centred line over her face goes to the side she isn't on, or below her
		const faceMid = face.x + face.w / 2;
		const side: Zone = faceMid > W / 2 ? 'left' : 'right';
		return intersects(ZONES[side], face) ? 'bottom' : side;
	}
	const alt = OPPOSITE[zone];
	return intersects(ZONES[alt], face) ? 'bottom' : alt;
};

export const SAFE: Box = {x: MARGIN, y: 110, w: W - 2 * MARGIN, h: H - 110 - 70};

const GAP = 28; // clear space between type and her face

/** A zone shrunk to the part that doesn't overlap her face (null if too little is left). */
export const clipZone = (z: ZoneBox, face: Box | null, minW = 320, minH = 110): ZoneBox | null => {
	if (!face || !intersects(z, face)) {
		return z;
	}
	const ok = (b: ZoneBox) => b.w >= minW && b.h >= minH;
	const faceMid = face.x + face.w / 2;
	const zoneMid = z.x + z.w / 2;
	// the parts of the zone to the left and to the right of her face
	const left: ZoneBox = {...z, w: Math.min(z.x + z.w, face.x - GAP) - z.x};
	const rightX = Math.max(z.x, face.x + face.w + GAP);
	const right: ZoneBox = {...z, x: rightX, w: z.x + z.w - rightX};
	if (z.w < W - 2 * MARGIN) {
		// a side zone: keep the part beside the face
		const side = zoneMid <= faceMid ? left : right;
		return ok(side) ? side : null;
	}
	if (z.v === 'center') {
		return null; // a centred zone over her face: try another zone
	}
	// a full-width top or bottom zone: the part above (or below) her face, else the wider part beside it
	const bottom = z.y + z.h;
	const clear: ZoneBox =
		z.v === 'top' ? {...z, h: Math.min(bottom, face.y - GAP) - z.y} : {...z, y: Math.max(z.y, face.y + face.h + GAP), h: bottom - Math.max(z.y, face.y + face.h + GAP)};
	return [clear, ...(left.w >= right.w ? [left, right] : [right, left])].find(ok) ?? null;
};
