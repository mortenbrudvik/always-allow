// Every chapter's spec, by chapter ID. Generated once from shots.json's chapters; add a chapter here only
// if the board gains one.
import {spec as ch01} from './ch01';
import {spec as ch02} from './ch02';
import {spec as ch03} from './ch03';
import {spec as ch04} from './ch04';
import {spec as ch05} from './ch05';
import {spec as ch06} from './ch06';
import {spec as ch07} from './ch07';
import {spec as ch08} from './ch08';
import {spec as ch09} from './ch09';
import {spec as ch10} from './ch10';
import {spec as ch11} from './ch11';
import {spec as ch12} from './ch12';
import {spec as ch13} from './ch13';
import {spec as ch14} from './ch14';
import {defaultCam} from '../lib/camera';
import {clamp} from '../lib/ease';
import {registerFormations, registerUntracked} from '../lib/registry';
import {worldOf} from '../lib/theme';
import {onScreen} from '../lib/tracking';
import type {ChapterSpec} from './types';

export const SPECS: Record<string, ChapterSpec> = {ch01, ch02, ch03, ch04, ch05, ch06, ch07, ch08, ch09, ch10, ch11, ch12, ch13, ch14};

// where a shot's copies stand on screen: the chapter's formation, moved by the camera the footage layer gives a
// dancer shot (its default move and the chapter's own), as the print pass moves the composite
registerFormations((shot, frame) => {
	const spec = SPECS[shot.chapter];
	const f = spec?.formation?.[shot.id];
	if (!f) {
		return null;
	}
	const t = frame / 24;
	const lt = t - shot.t0;
	const dur = shot.t1 - shot.t0;
	const p = {shot, frame, t, lt, dur, p: clamp(lt / dur), world: worldOf(shot), face: null, proxy: false, track: null};
	const cam = {...defaultCam(p, false), ...(spec.camera?.[shot.id]?.(p) ?? {})};
	return f(p).map((s) => {
		const [x, y] = onScreen(s.x, s.y, cam);
		return {x, y, h: s.h * cam.zoom, agent: s.label === 'AGENT_01'};
	});
});

registerUntracked(Object.values(SPECS).flatMap((spec) => spec.untracked ?? []));
