// Light on the screens in a plate (ANIMATION_GUIDE.md, "Known work"): the monitors of A_floor_ews switch on and
// strobe in s013, s069 and s108. The light is drawn into the plate before the print pass, so it prints with the
// plate (halftone, grain, grade) instead of sitting on top of it. The screens are measured on the picked plate, in
// frame pixels as the comp shows it (the plate covering 1920x1080).
import React, {useMemo} from 'react';
import type {ShotProps} from '../chapters/types';
import {defaultCam} from '../lib/camera';
import {useImage} from '../lib/hooks';
import type {Box} from '../lib/layout';
import {mediaUrl, plateFile} from '../lib/media';
import {H, W} from '../lib/theme';
import {PrintPass} from '../layers/PrintPass';

/** A screen's glass in frame pixels. `hidden` is the lower corner a nearer monitor hides, in the screen's own pixels:
 * from x0 to x1 across (one of them at the screen's edge), and from y0 down to its foot. */
export interface Screen extends Box {
	hidden?: {x0: number; x1: number; y0: number};
}

/** A_floor_ews's monitors that face the camera: Grounding DINO's "a computer monitor." on the pick, kept where the
 * screen side is toward the lens, and inset to the glass (session 5). The big dark shapes in the foreground are the
 * backs of monitors facing away, so they stay dark. Two sit behind a nearer one, which hides their lower corner. */
export const FLOOR_SCREENS: Screen[] = [
	{x: 518, y: 622, w: 166, h: 102, hidden: {x0: 0, x1: 60, y0: 23}}, // its lower left behind the next
	{x: 385, y: 645, w: 193, h: 105},
	{x: 696, y: 604, w: 84, h: 96},
	{x: 1270, y: 612, w: 154, h: 98, hidden: {x0: 75, x1: 154, y0: 28}}, // its lower right behind the last
	{x: 1345, y: 640, w: 83, h: 120},
];

/** A screen's outline in plate pixels, less the corner a nearer monitor hides. */
const outline = (ctx: CanvasRenderingContext2D, s: Screen, map: (x: number, y: number) => [number, number]) => {
	const h = s.hidden;
	const pts: [number, number][] = !h
		? [[0, 0], [s.w, 0], [s.w, s.h], [0, s.h]]
		: h.x0 <= 0
			? [[0, 0], [s.w, 0], [s.w, s.h], [h.x1, s.h], [h.x1, h.y0], [0, h.y0]]
			: [[0, 0], [s.w, 0], [s.w, h.y0], [h.x0, h.y0], [h.x0, s.h], [0, s.h]];
	ctx.beginPath();
	pts.forEach(([u, v], i) => {
		const [x, y] = map(s.x + u, s.y + v);
		if (i === 0) {
			ctx.moveTo(x, y);
		} else {
			ctx.lineTo(x, y);
		}
	});
	ctx.closePath();
};

/** The shot's plate with its screens lit by `on` (0-1) and the floor lifted by `room`, printed over its depth map with
 * the shot's default camera: the footage layer for a shot whose screens come on (a chapter's `footage` entry). */
export const LitPlate: React.FC<ShotProps & {screens: Screen[]; on: number; room?: number}> = (p) => {
	const {shot, frame, proxy, screens, on, room = 0} = p;
	const plate = plateFile(shot.plate);
	const img = useImage(plate ? mediaUrl(plate.file) : null);
	const depth = useImage(plate?.depth ? mediaUrl(plate.depth) : null);
	const canvas = useMemo(() => document.createElement('canvas'), []);
	const level = Math.round(on * 24) / 24; // steps small enough to be smooth, few enough to upload only on a change
	const lift = Math.round(room * 200) / 200;
	if (img) {
		const pw = img.naturalWidth;
		const ph = img.naturalHeight;
		if (canvas.width !== pw || canvas.height !== ph) {
			canvas.width = pw;
			canvas.height = ph;
		}
		// the plate covers the frame as the print pass shows it: frame pixels to plate pixels
		const s = Math.max(W / pw, H / ph);
		const ox = (pw * s - W) / 2;
		const oy = (ph * s - H) / 2;
		const map = (x: number, y: number): [number, number] => [(x + ox) / s, (y + oy) / s];
		const ctx = canvas.getContext('2d')!;
		ctx.globalCompositeOperation = 'source-over';
		ctx.filter = 'none';
		ctx.globalAlpha = 1;
		ctx.drawImage(img, 0, 0);
		ctx.globalCompositeOperation = 'screen';
		if (lift > 0) {
			ctx.globalAlpha = lift;
			ctx.fillStyle = '#cfe0ee';
			ctx.fillRect(0, 0, pw, ph);
		}
		if (level > 0) {
			for (const sc of screens) {
				const [x0, y0] = map(sc.x, sc.y);
				const [x1, y1] = map(sc.x + sc.w, sc.y + sc.h);
				// the bloom: the glass, blurred, spilling onto the desk
				ctx.save();
				ctx.filter = `blur(${Math.round((x1 - x0) * 0.12)}px)`;
				ctx.globalAlpha = 0.5 * level;
				ctx.fillStyle = '#bfd6e6';
				outline(ctx, sc, map);
				ctx.fill();
				ctx.restore();
				// the glass: a cool gradient, and faint lines of text on it
				ctx.save();
				outline(ctx, sc, map);
				ctx.clip();
				const g = ctx.createLinearGradient(0, y0, 0, y1);
				g.addColorStop(0, '#e6eff5');
				g.addColorStop(1, '#9fb9cb');
				ctx.globalAlpha = 0.8 * level;
				ctx.fillStyle = g;
				ctx.fillRect(x0, y0, x1 - x0, y1 - y0);
				ctx.globalCompositeOperation = 'multiply';
				ctx.fillStyle = 'rgba(40,52,62,0.55)';
				const lh = Math.max(3, (y1 - y0) / 14);
				for (let yy = y0 + lh * 1.2, i = 0; yy < y1 - lh; yy += lh, i++) {
					const w = (x1 - x0) * (0.35 + 0.5 * ((i * 37) % 11) / 11);
					ctx.fillRect(x0 + (x1 - x0) * 0.08, yy, w * 0.84, Math.max(1, lh * 0.28));
				}
				ctx.restore();
			}
		}
	}
	return (
		<PrintPass
			src={img ? canvas : null}
			srcKey={img ? `${plate?.file}:${level}:${lift}` : null}
			depth={plate?.depth ? depth : null}
			cam={defaultCam(p, Boolean(plate?.depth))}
			seed={frame}
			width={W}
			height={H}
			pxScale={proxy ? 1 / 3 : 1}
		/>
	);
};
