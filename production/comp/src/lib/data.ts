// The compositor's inputs, read straight from the repo so there is one source of truth:
// the beat grid and sections (production/analysis/song.json), the word times (words.json) and the
// board (production/storyboard/shots.json, built by tools/storyboard.py). Nothing here is edited by hand.
import songJson from '../../../analysis/song.json';
import wordsJson from '../../../analysis/words.json';
import boardJson from '../../../storyboard/shots.json';

export type Mode = 'masthead' | 'coverline' | 'subtitle' | 'serif' | 'mass';
export type Zone = 'left' | 'right' | 'top' | 'bottom' | 'center' | 'ui';
export type SetKey = 'A' | 'B' | 'H' | 'UI';
export type Tier = 'seedance' | '2.5d' | 'code';
export type Place = 'left' | 'center' | 'right' | 'full' | 'small' | 'none';

export interface Word {
	word: string;
	t0: number;
	t1: number;
}

export interface Lyric {
	line: number;
	text: string;
	mode: Mode;
	zone: Zone;
	t0: number;
	t1: number;
	words: Word[];
	/** From word `at` on, the line changes mode and zone (the head goes when the tail lands). */
	split?: {at: number; mode: Mode; zone: Zone};
}

export interface Shot {
	id: string;
	chapter: string;
	t0: number;
	t1: number;
	f0: number;
	f1: number;
	bar0: number;
	section: string;
	set: SetKey;
	agent_on_screen: boolean;
	framing: string;
	motion_tier: Tier;
	clip: string | null;
	plate: string | null;
	place: Place;
	shift_bars: number;
	hold_last_frame: boolean;
	/** Pixels the footage is moved sideways, for a take framed tighter than its plate (board.py). */
	footage_x?: number;
	/** [from, to, frame] in the clip's frames: from `from` to `to` the take shows `frame` (board.py `holds`). */
	clip_holds?: [number, number, number][];
	clip_in_s?: number;
	action: string;
	camera: string;
	graphic: string;
	transition: string;
	notes: string;
	face: string;
	world: 'dark' | 'light' | null;
	lyrics: Lyric[];
	status: string;
}

export interface Clip {
	clip: string;
	kind: 'speak' | 'motion' | 'dancer';
	plate: string;
	window: {start: number; end: number; start_frame: number};
	seconds: number;
	words: string;
	shots: string[];
}

export interface Chapter {
	chapter: string;
	name: string;
	t0: number;
	t1: number;
	f0: number;
	f1: number;
	shots: string[];
}

export interface Board {
	fps: number;
	duration_s: number;
	frames: number;
	chapters: Chapter[];
	shots: Shot[];
	clips: Clip[];
}

export interface Song {
	duration_s: number;
	beats_s: number[];
	downbeats_s: number[];
	sections: {bar: number; start: number; end: number; label: string}[];
}

export interface WordsFile {
	lines: {text: string; start: number; end: number; words: {word: string; start: number; end: number}[]}[];
}

export const board = boardJson as unknown as Board;
export const song = songJson as unknown as Song;
export const wordsFile = wordsJson as unknown as WordsFile;

export const shots: Shot[] = board.shots;
export const clips: Record<string, Clip> = Object.fromEntries(board.clips.map((c) => [c.clip, c]));
export const chapters: Chapter[] = board.chapters;
export const shotById: Record<string, Shot> = Object.fromEntries(shots.map((s) => [s.id, s]));

/** The shot on screen at a frame (the last shot holds past the end). */
export const shotAtFrame = (frame: number): Shot => {
	let lo = 0;
	let hi = shots.length - 1;
	while (lo < hi) {
		const mid = (lo + hi + 1) >> 1;
		if (shots[mid].f0 <= frame) {
			lo = mid;
		} else {
			hi = mid - 1;
		}
	}
	return shots[lo];
};

export const shotIndex: Record<string, number> = Object.fromEntries(shots.map((s, i) => [s.id, i]));
