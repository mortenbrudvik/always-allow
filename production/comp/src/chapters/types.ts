// What a chapter file provides (ANIMATION_GUIDE.md). Every entry is keyed by shot ID, and every function
// is pure: it gets the frame and returns what to draw, with no state carried between frames.
import type React from 'react';
import type {Shot} from '../lib/data';
import type {Box} from '../lib/layout';
import type {World} from '../lib/theme';
import type {Cam} from '../layers/PrintPass';

export interface ShotProps {
	shot: Shot;
	frame: number; // the video's frame (0-based, 24 fps)
	t: number; // song seconds
	lt: number; // seconds since the shot started
	dur: number; // the shot's length in seconds
	p: number; // 0-1 through the shot
	world: World;
	face: Box | null; // her face box (tracked if the data exists, else planned); type never goes over it
	proxy: boolean; // a small proxy render: skip the most expensive detail
	/** Her tracked landmarks and body on screen, when the shot's clip or plate has tracking (lib/tracking.ts). */
	track?: {landmarks: [number, number][]; body: Box | null} | null;
}

/** One copy of a dancer matte in a formation: feet at (x, y) in frame pixels, h tall. */
export interface Slot {
	x: number;
	y: number;
	h: number;
	label?: string;
	delay?: number; // frames behind the matte's own timing (0 = perfect sync)
	flip?: boolean; // mirrored left to right
	back?: boolean; // the storyboard card draws this copy from behind (the matte shows whatever its clip shows)
	opacity?: number;
}

export interface ChapterSpec {
	/** The explaining graphics and UI, drawn over the footage and under the lyrics and chrome. */
	graphics?: Record<string, React.FC<ShotProps>>;
	/** Camera moves for a shot's plate or clip (2.5D pushes, punch-ins); the default reads the board's camera text. */
	camera?: Record<string, (p: ShotProps) => Partial<Cam>>;
	/** Where the copies of a dancer matte stand. */
	formation?: Record<string, (p: ShotProps) => Slot[]>;
	/** Replaces the footage layer of a shot entirely (the 2x2 split, the tower, the flash-past). */
	footage?: Record<string, React.FC<ShotProps>>;
	/** Set pieces the plate will have, drawn on the storyboard card only, behind its figures. */
	backdrop?: Record<string, React.FC<ShotProps>>;
	/** A clip's speed in its shot (2 = twice as fast) and a comp frame from which it holds still: a speed ramp. */
	clipTime?: Record<string, {rate?: number; freezeFrom?: number}>;
	/** Shots whose `footage` entry doesn't show the clip or plate full frame (a split, a pull-back): her tracking
	 * doesn't apply there, so no tracking box is drawn and the lyrics don't dodge where the clip had her face. */
	untracked?: string[];
}
