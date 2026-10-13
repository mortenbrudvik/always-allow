// How a chapter draws another shot (the flash-past in ch14) without importing ShotView, which imports every
// chapter: ShotView registers itself here when it loads, and a chapter asks for it at render time.
import type React from 'react';
import type {Shot} from './data';

/** `lite`: plates as plain images and clips as their start frames, no print pass (for small mosaic tiles). */
export type ShotRenderer = React.FC<{shot: Shot; frame: number; proxy: boolean; tracking?: boolean; lite?: boolean}>;

let renderer: ShotRenderer | null = null;

export const registerShotView = (r: ShotRenderer) => {
	renderer = r;
};

export const shotView = (): ShotRenderer => {
	if (!renderer) {
		throw new Error('ShotView has not registered yet');
	}
	return renderer;
};

/** Where a shot's copies of a dancer matte stand at a frame (feet at x, y, h tall), from its chapter's formation:
 * chapters/index.ts registers it, so the lyric engine can keep type off the copies' heads. */
export type FormationAt = (shot: Shot, frame: number) => {x: number; y: number; h: number; agent?: boolean}[] | null;

let formations: FormationAt | null = null;

export const registerFormations = (f: FormationAt) => {
	formations = f;
};

export const formationAt: FormationAt = (shot, frame) => formations?.(shot, frame) ?? null;

/** The shots whose footage a chapter replaces with something that doesn't show the clip full frame (types.ts,
 * `untracked`): chapters/index.ts registers them, so the tracking can leave them out. */
let untracked = new Set<string>();

export const registerUntracked = (ids: Iterable<string>) => {
	untracked = new Set(ids);
};

export const isUntracked = (id: string) => untracked.has(id);
