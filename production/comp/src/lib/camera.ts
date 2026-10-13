// The default camera for a shot's footage, read from the board's camera text (ANIMATION_GUIDE.md, "2.5D"): used by
// the footage layer to move a clip or plate through the print pass, and by the tracking to follow her on screen.
import type {ShotProps} from '../chapters/types';
import type {Cam} from '../layers/PrintPass';
import {STILL} from '../layers/PrintPass';
import {easeInOut, easeOut} from './ease';
import {barTime, FPS} from './time';

/** The board's camera text as a move: pushes, pull-backs, drifts, rotations, crane and tilt, punch-ins. */
export const defaultCam = (p: Pick<ShotProps, 'shot' | 'p' | 't'>, hasDepth: boolean): Cam => {
	const c = p.shot.camera.toLowerCase();
	const k = p.p;
	const cam: Cam = {...STILL};
	if (/very slow push/.test(c)) {
		cam.zoom = 1 + 0.035 * easeInOut(k);
	} else if (/push/.test(c)) {
		cam.zoom = 1 + 0.07 * easeInOut(k);
	}
	if (/pull back|pull up/.test(c)) {
		cam.zoom = 1.09 - 0.09 * easeInOut(k);
	}
	if (/drift|lateral|dolly/.test(c)) {
		cam.x = -0.035 + 0.07 * k;
		cam.zoom = Math.max(cam.zoom, 1.05);
	}
	if (/rotation/.test(c)) {
		cam.rot = (/fast/.test(c) ? 0.35 : 0.12) * (k - 0.5);
		cam.zoom = Math.max(cam.zoom, 1.12);
	}
	if (/crane up/.test(c)) {
		cam.y = -0.04 + 0.08 * easeInOut(k);
		cam.zoom = Math.max(cam.zoom, 1.06);
	}
	if (/tilt down/.test(c)) {
		cam.y = 0.05 * easeInOut(k);
		cam.zoom = Math.max(cam.zoom, 1.06);
	}
	if (/punch-in/.test(c)) {
		// K-pop: a hard zoom step on each downbeat inside the shot (two at most)
		const m = /bar (\d+)/.exec(c);
		const bars = m ? [Number(m[1])] : [Math.ceil(p.shot.bar0 + 1e-6)];
		let z = 1;
		for (const b of bars) {
			const dt = p.t - barTime(b);
			if (dt >= 0) {
				z += 0.08 * easeOut(dt * FPS / 2);
			}
		}
		cam.zoom *= z;
	}
	if (hasDepth) {
		// depth separates the layers only when something moves the camera sideways
		cam.depth = 1;
		if (!cam.x && !cam.y) {
			cam.x = 0.012 * Math.sin(k * Math.PI);
			cam.zoom = Math.max(cam.zoom, 1.03);
		}
	}
	return cam;
};
