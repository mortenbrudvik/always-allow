// The style bible's tokens (production/style/STYLE_BIBLE.md): palette, type, margins. One warm accent
// per frame, terracotta, and never on her.
import type {Shot} from './data';

export const W = 1920;
export const H = 1080;
export const MARGIN = 96; // the lyric's safe area
export const CHROME = 32; // the chrome's margin

export const C = {
	// the night shift (A)
	black: '#0b0c0e',
	blackDeep: '#07080a',
	greenWhite: '#d8e4dc',
	flash: '#f2f0ea',
	monitorBlue: '#2f4a66',
	monitorBlue2: '#4d7ea8',
	screen: '#cfe0ee',
	glassTeal: '#6f8f8a',
	partition: '#5d6166',
	carpet: '#3b3f44',
	steel: '#8a9096',
	statusGreen: '#3fae6a',
	amber: '#b9853e',
	// the clean room (B)
	white: '#f4f4f1',
	paleGrey: '#dcdfe2',
	shadowGrey: '#b7bbbf',
	cobalt: '#1f4fd6',
	acid: '#e6e23a',
	panel: '#fbfbf8',
	// the Human's daylight (H)
	sand: '#e9dcc4',
	sky: '#cfd8dc',
	oat: '#d9cdb8',
	// UI and accents
	terracotta: '#c96442',
	ink: '#0b0c0e',
	ink2: '#6b6f76',
	hair: '#dcdfe2',
	pass: '#5fbf8a',
	paper: '#ffffff',
} as const;

export const FONT = {
	sans: 'Geist',
	mono: 'Geist Mono',
	serif: 'Instrument Serif',
} as const;

export type World = 'dark' | 'light';

const LIGHT_UI_CHAPTERS = new Set(['ch05', 'ch08', 'ch12']);

/** Dark (night shift, the dialog's dark room, most UI) or light (clean room, daylight, the hooks' UI). */
export const worldOf = (shot: Shot): World => {
	if (shot.world) {
		return shot.world;
	}
	if (shot.set === 'A') {
		return 'dark';
	}
	if (shot.set === 'B' || shot.set === 'H') {
		return 'light';
	}
	return LIGHT_UI_CHAPTERS.has(shot.chapter) ? 'light' : 'dark';
};

/** Foreground and background for type and chrome in a world. */
export const ink = (world: World) =>
	world === 'dark'
		? {fg: C.greenWhite, fgSoft: 'rgba(216,228,220,0.72)', bg: C.black, line: 'rgba(216,228,220,0.35)'}
		: {fg: C.ink, fgSoft: 'rgba(11,12,14,0.72)', bg: C.white, line: 'rgba(11,12,14,0.3)'};
