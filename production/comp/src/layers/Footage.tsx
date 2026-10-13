// The footage layer (BRIEF.md step 3): a shot's clip when it exists, else its plate (a Seedance shot's plate
// is its clip's start frame), else its storyboard card. Clips and plates go through the print pass here, so
// the halftone and grade sit on the footage only; everything drawn in code goes on top, crisp.
import React, {useCallback, useLayoutEffect, useRef} from 'react';
import {Freeze, Img, OffthreadVideo, Sequence} from 'remotion';
import type {ChapterSpec, ShotProps, Slot} from '../chapters/types';
import {clips} from '../lib/data';
import {useImage} from '../lib/hooks';
import {clipFile, type Figure, matteFile, mediaUrl, plateFile} from '../lib/media';
import {C, H, W} from '../lib/theme';
import {FPS} from '../lib/time';
import {Card} from './Card';
import {defaultCam} from '../lib/camera';
import {type Cam, PrintPass, type PrintPassHandle} from './PrintPass';

export {defaultCam};

const Solid: React.FC<{world: 'dark' | 'light'}> = ({world}) => (
	<div style={{position: 'absolute', inset: 0, background: world === 'dark' ? C.black : C.white}} />
);

const PlateFootage: React.FC<ShotProps & {file: string; depthFile: string | null; cam: Cam}> = ({file, depthFile, cam, frame, proxy}) => {
	const img = useImage(mediaUrl(file));
	const depth = useImage(depthFile ? mediaUrl(depthFile) : null);
	return <PrintPass src={img} srcKey={file} depth={depthFile ? depth : null} cam={cam} seed={frame} width={W} height={H} pxScale={proxy ? 1 / 3 : 1} />;
};

/** A clip's last frame: from the file when the scan counted it, else from the board's length. */
const lastFrameOf = (shot: ShotProps['shot'], probed: number | null | undefined) =>
	(probed ?? Math.round((clips[shot.clip ?? '']?.seconds ?? 0) * FPS)) - 1;

/** The clip on the song's time: it starts `clip_in_s` into the take; a held shot freezes on the take's last frame.
 * A chapter can ramp it (`clipTime`): play it faster from the shot's start, and hold it still from a comp frame. */
const ClipVideo: React.FC<{shot: ShotProps['shot']; file: string; frames: number | null | undefined; transparent?: boolean; time?: {rate?: number; freezeFrom?: number}; onFrame: (img: CanvasImageSource) => void}> = ({
	shot, file, frames, transparent = false, time, onFrame,
}) => {
	const clipIn = Math.round((shot.clip_in_s ?? 0) * FPS);
	const rate = time?.rate ?? 1;
	const from = shot.f0 - Math.round(clipIn / rate); // so the take is clip_in_s in when the shot starts
	// the sequence's frame at which the take reaches its last frame, or the ramp's freeze
	const last = Math.floor(lastFrameOf(shot, frames) / rate);
	const freeze = time?.freezeFrom !== undefined ? Math.min(last, time.freezeFrom - from) : last;
	// the board's holds: stretches of the take shown as one frame of it (a mouth stilled where the song has no words)
	const held = (shot.clip_holds ?? []).reduceRight<React.ReactNode>(
		(child, [a, b, at]) => (
			<Freeze frame={Math.round(at / rate)} active={(f) => f >= Math.round(a / rate) && f <= Math.round(b / rate)}>
				{child}
			</Freeze>
		),
		<OffthreadVideo src={mediaUrl(file)} transparent={transparent} muted playbackRate={rate} onVideoFrame={onFrame} crossOrigin="anonymous" style={{display: 'none'}} />,
	);
	return (
		<Sequence from={from} layout="none">
			<Freeze frame={freeze} active={(f) => (shot.hold_last_frame || time?.freezeFrom !== undefined) && f >= freeze}>
				{held}
			</Freeze>
		</Sequence>
	);
};

const ClipFootage: React.FC<ShotProps & {file: string; frames: number | null | undefined; cam: Cam}> = ({shot, file, frames, cam, frame, proxy}) => {
	const handle = useRef<PrintPassHandle | null>(null);
	const onFrame = useCallback((img: CanvasImageSource) => handle.current?.draw(img), []);
	return (
		<>
			<ClipVideo shot={shot} file={file} frames={frames} onFrame={onFrame} />
			<PrintPass src={null} srcKey={null} cam={cam} seed={frame} width={W} height={H} pxScale={proxy ? 1 / 3 : 1} handle={handle} />
		</>
	);
};

/** A dancer clip cut out with its matte and copied into a formation over the stage plate, then printed. */
/** Where a matte's figure stands when it wasn't measured: a head-to-toe figure filling most of the frame. */
const FIGURE: Figure = {top: 0.09, feet: 0.93, cx: 0.5};

const DancerFootage: React.FC<ShotProps & {matte: string; frames: number | null | undefined; figure?: Figure | null; stage: string | null; slots: Slot[]; cam: Cam; time?: {rate?: number; freezeFrom?: number}}> = (props) => {
	const {shot, matte, frames, figure, stage, slots, cam, frame, proxy, time} = props;
	const fig = figure ?? FIGURE;
	const handle = useRef<PrintPassHandle | null>(null);
	const comp = useRef<HTMLCanvasElement | null>(null);
	const lastMatte = useRef<CanvasImageSource | null>(null);
	const stageImg = useImage(stage ? mediaUrl(stage) : null);
	const composite = useCallback(
		(img: CanvasImageSource) => {
			if (!comp.current) {
				comp.current = document.createElement('canvas');
				comp.current.width = W;
				comp.current.height = H;
			}
			const ctx = comp.current.getContext('2d')!;
			ctx.fillStyle = C.white;
			ctx.fillRect(0, 0, W, H);
			if (stageImg) {
				ctx.drawImage(stageImg, 0, 0, W, H);
			}
			const im = img as HTMLImageElement;
			const aspect = (im.naturalWidth || 1280) / (im.naturalHeight || 720);
			// the matte frame is the dancer's whole 16:9 frame: scale it so her figure is h tall, feet at the slot
			for (const s of [...slots].sort((a, b) => a.y - b.y)) {
				const fh = s.h / (fig.feet - fig.top);
				const fw = fh * aspect;
				ctx.globalAlpha = s.opacity ?? 1;
				ctx.save();
				if (s.flip) {
					ctx.translate(s.x * 2, 0);
					ctx.scale(-1, 1);
				}
				ctx.drawImage(im, s.x - fw * fig.cx, s.y - fh * fig.feet, fw, fh);
				ctx.restore();
			}
			ctx.globalAlpha = 1;
			handle.current?.draw(comp.current);
		},
		[slots, stageImg, fig],
	);
	const onFrame = useCallback(
		(img: CanvasImageSource) => {
			lastMatte.current = img;
			composite(img);
		},
		[composite],
	);
	// the formation can move while the matte's frame holds (a held shot, a pull-back): composite again
	useLayoutEffect(() => {
		if (lastMatte.current) {
			composite(lastMatte.current);
		}
	}, [composite]);
	return (
		<>
			<ClipVideo shot={shot} file={matte} frames={frames} transparent time={time} onFrame={onFrame} />
			<PrintPass src={null} srcKey={null} cam={cam} seed={frame} width={W} height={H} pxScale={proxy ? 1 / 3 : 1} handle={handle} />
		</>
	);
};

/** A plate as a plain image, no print pass: for the flash-past's small tiles. */
const LiteStill: React.FC<{file: string}> = ({file}) => <Img src={mediaUrl(file)} style={{position: 'absolute', inset: 0, width: W, height: H, objectFit: 'cover'}} />;

/** A dancer shot as a small tile: her cut-out still copied into the front of the formation, over the stage. The
 * matte isn't played (a mosaic tile is an eighth of the frame, and there are dozens), and only the copies nearest
 * the camera are drawn, the ones a tile can show. */
const LiteFormation: React.FC<{still: string; figure: Figure; stage: string | null; slots: Slot[]}> = ({still, figure, stage, slots}) => {
	const tallest = Math.max(1, ...slots.map((s) => s.h));
	const front = slots.filter((s) => s.h >= tallest * 0.35).sort((a, b) => a.y - b.y).slice(-60);
	const fh = (h: number) => h / (figure.feet - figure.top);
	return (
		<div style={{position: 'absolute', inset: 0, overflow: 'hidden', background: C.white}}>
			{stage && <LiteStill file={stage} />}
			{front.map((s, i) => (
				<Img
					key={i}
					src={mediaUrl(still)}
					style={{position: 'absolute', left: s.x - fh(s.h) * (16 / 9) * figure.cx, top: s.y - fh(s.h) * figure.feet, width: fh(s.h) * (16 / 9), height: fh(s.h), transform: s.flip ? 'scaleX(-1)' : undefined, opacity: s.opacity ?? 1}}
				/>
			))}
		</div>
	);
};

/** Whether the footage layer shows the shot's plate over its depth map (a 2.5D shot, or a clip still to come). */
const onDepth = (shot: ShotProps['shot']) => {
	const clip = shot.clip ? clips[shot.clip] : null;
	return !clipFile(shot.clip) && clip?.kind !== 'dancer' && Boolean(plateFile(shot.plate ?? clip?.plate ?? null)?.depth);
};

/** The camera the footage layer moves the shot's footage by, so graphics can follow what's in it. */
export const footageCam = (p: ShotProps, spec: ChapterSpec): Cam => ({...defaultCam(p, onDepth(p.shot)), ...(spec.camera?.[p.shot.id]?.(p) ?? {})});

export const Footage: React.FC<ShotProps & {spec: ChapterSpec; lite?: boolean}> = ({spec, lite = false, ...p}) => {
	const {shot} = p;
	const Custom = spec.footage?.[shot.id];
	if (Custom && !lite) {
		return <Custom {...p} />;
	}
	if (shot.motion_tier === 'code') {
		return <Solid world={p.world} />;
	}
	const clip = shot.clip ? clips[shot.clip] : null;
	const plate = plateFile(shot.plate ?? clip?.plate ?? null);
	const camFor = (hasDepth: boolean) => ({...defaultCam(p, hasDepth), ...(spec.camera?.[shot.id]?.(p) ?? {})});
	const Backdrop = spec.backdrop?.[shot.id];
	const backdrop = Backdrop ? <Backdrop {...p} /> : null;
	if (lite) {
		// small copies only: a mosaic draws dozens of tiles at once. A dancer shot shows her cut-out still in the
		// front of its formation over its stage; any other clip shows its start frame; a shot with nothing yet, its card
		const small = (f: {file: string; thumb?: string | null} | null) => (f ? f.thumb ?? f.file : null);
		if (clip?.kind === 'dancer') {
			const matte = matteFile(shot.clip);
			if (matte?.still) {
				const slots = spec.formation?.[shot.id]?.(p) ?? [{x: W / 2, y: 960, h: 760}];
				return <LiteFormation still={matte.still} figure={matte.figure ?? FIGURE} stage={small(plateFile(shot.plate))} slots={slots} />;
			}
			return <Card shot={shot} backdrop={backdrop} />;
		}
		const still = small(plateFile(clip?.plate ?? shot.plate));
		return still ? <LiteStill file={still} /> : <Card shot={shot} backdrop={backdrop} />;
	}
	if (clip?.kind === 'dancer') {
		const matte = matteFile(shot.clip);
		const slots = spec.formation?.[shot.id]?.(p) ?? [{x: W / 2, y: 960, h: 760}];
		if (matte) {
			return <DancerFootage {...p} matte={matte.file} frames={matte.frames} figure={matte.figure} stage={plateFile(shot.plate)?.file ?? null} slots={slots} cam={camFor(false)} time={spec.clipTime?.[shot.id]} />;
		}
		return <Card shot={shot} slots={spec.formation?.[shot.id] ? slots : null} cam={camFor(false)} backdrop={backdrop} />;
	}
	const clipMedia = clipFile(shot.clip);
	if (clipMedia) {
		return <ClipFootage {...p} file={clipMedia.file} frames={clipMedia.frames} cam={camFor(false)} />;
	}
	if (plate) {
		return <PlateFootage {...p} file={plate.file} depthFile={plate.depth} cam={camFor(Boolean(plate.depth))} />;
	}
	return <Card shot={shot} cam={camFor(false)} backdrop={backdrop} />;
};
