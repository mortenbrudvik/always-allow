// One shot at one frame: its footage (clip, plate or card, printed), its chapter's explaining graphics, and
// her tracking. A pure function of (shot, frame), so a transition can draw two shots at once and the
// flash-past can draw any shot at any frame.
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {SPECS} from './chapters';
import type {ShotProps} from './chapters/types';
import {clips, type Shot} from './lib/data';
import {clamp} from './lib/ease';
import {plannedFace} from './lib/layout';
import {formationAt, registerShotView} from './lib/registry';
import {boxOnScreen, onScreen, trackAt} from './lib/tracking';
import {worldOf} from './lib/theme';
import {Footage, footageCam} from './layers/Footage';
import {Tracking} from './layers/Tracking';

export const shotProps = (shot: Shot, frame: number, proxy: boolean): ShotProps => {
	const t = frame / 24;
	const lt = t - shot.t0;
	const dur = shot.t1 - shot.t0;
	const p: ShotProps = {shot, frame, t, lt, dur, p: clamp(lt / dur), world: worldOf(shot), face: plannedFace(shot), proxy, track: null};
	if (shot.clip && clips[shot.clip]?.kind === 'dancer') {
		// a formation: she is the copy labelled AGENT_01, wherever the chapter stands it; the matte's own tracking is
		// the single dancer in her clip's frame, which matches no copy on screen
		const her = formationAt(shot, frame)?.find((c) => c.agent);
		p.face = null;
		p.track = {landmarks: [], body: her ? {x: her.x - her.h * 0.17, y: her.y - her.h, w: her.h * 0.34, h: her.h} : null};
		return p;
	}
	// her tracked face, where the clip or plate has it, moved by the footage's camera; else the planned box
	const tr = trackAt(shot, frame);
	if (tr) {
		const cam = footageCam(p, SPECS[shot.chapter] ?? {});
		const dx = shot.footage_x ?? 0;
		p.face = boxOnScreen(tr.face, cam, dx);
		p.track = {landmarks: tr.landmarks.map(([x, y]) => onScreen(x, y, cam, dx)), body: boxOnScreen(tr.body, cam, dx)};
	}
	return p;
};

export const ShotView: React.FC<{shot: Shot; frame: number; proxy: boolean; tracking?: boolean; lite?: boolean}> = ({shot, frame, proxy, tracking = true, lite = false}) => {
	const p = shotProps(shot, frame, proxy);
	const spec = SPECS[shot.chapter] ?? {};
	// a lite tile keeps a graphic only where the graphic is the picture (a code-only shot)
	const Graphic = lite && shot.motion_tier !== 'code' ? undefined : spec.graphics?.[shot.id];
	return (
		<AbsoluteFill style={{overflow: 'hidden'}}>
			{shot.footage_x ? (
				// a take framed tighter than its plate, moved aside for its type; the gap it opens is black
				<div style={{position: 'absolute', inset: 0, background: '#000'}}>
					<div style={{position: 'absolute', inset: 0, transform: `translateX(${shot.footage_x}px)`}}>
						<Footage {...p} spec={spec} lite={lite} />
					</div>
				</div>
			) : (
				<Footage {...p} spec={spec} lite={lite} />
			)}
			{tracking && !lite && !spec.untracked?.includes(shot.id) && <Tracking shot={shot} frame={frame} face={p.face} track={p.track} />}
			{Graphic && <Graphic {...p} />}
		</AbsoluteFill>
	);
};

registerShotView(ShotView);
