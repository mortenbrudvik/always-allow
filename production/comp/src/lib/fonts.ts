// The three families from the style bible, loaded from the npm packages (SIL OFL), so a render never
// fetches a font. loadFont holds the render until each face has loaded.
import {loadFont} from '@remotion/fonts';
import sans300 from '@fontsource/geist-sans/files/geist-sans-latin-300-normal.woff2';
import sans400 from '@fontsource/geist-sans/files/geist-sans-latin-400-normal.woff2';
import sans500 from '@fontsource/geist-sans/files/geist-sans-latin-500-normal.woff2';
import sans600 from '@fontsource/geist-sans/files/geist-sans-latin-600-normal.woff2';
import sans700 from '@fontsource/geist-sans/files/geist-sans-latin-700-normal.woff2';
import sans800 from '@fontsource/geist-sans/files/geist-sans-latin-800-normal.woff2';
import sans900 from '@fontsource/geist-sans/files/geist-sans-latin-900-normal.woff2';
import mono400 from '@fontsource/geist-mono/files/geist-mono-latin-400-normal.woff2';
import mono500 from '@fontsource/geist-mono/files/geist-mono-latin-500-normal.woff2';
import mono700 from '@fontsource/geist-mono/files/geist-mono-latin-700-normal.woff2';
import serifItalic from '@fontsource/instrument-serif/files/instrument-serif-latin-400-italic.woff2';
import serifRegular from '@fontsource/instrument-serif/files/instrument-serif-latin-400-normal.woff2';
import {FONT} from './theme';

const faces: [string, string, string, string][] = [
	[FONT.sans, sans300, '300', 'normal'],
	[FONT.sans, sans400, '400', 'normal'],
	[FONT.sans, sans500, '500', 'normal'],
	[FONT.sans, sans600, '600', 'normal'],
	[FONT.sans, sans700, '700', 'normal'],
	[FONT.sans, sans800, '800', 'normal'],
	[FONT.sans, sans900, '900', 'normal'],
	[FONT.mono, mono400, '400', 'normal'],
	[FONT.mono, mono500, '500', 'normal'],
	[FONT.mono, mono700, '700', 'normal'],
	[FONT.serif, serifRegular, '400', 'normal'],
	[FONT.serif, serifItalic, '400', 'italic'],
];

let loaded = false;

export const loadFonts = () => {
	if (loaded) {
		return;
	}
	loaded = true;
	for (const [family, url, weight, style] of faces) {
		loadFont({family, url, weight, style, format: 'woff2'});
	}
};
