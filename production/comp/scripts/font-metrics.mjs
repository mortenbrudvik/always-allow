// Writes src/data/font-metrics.json: each face's advance width per character, in ems, read from the
// same font files the renders use. The lyric engine lays type out with it, in the browser and in the
// Node checks alike, so both agree on how wide a line is. Run it again only if the fonts change.
//   node scripts/font-metrics.mjs
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import opentype from 'opentype.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const nm = path.join(here, '..', 'node_modules', '@fontsource');
const FACES = {
	sans300: 'geist-sans/files/geist-sans-latin-300-normal.woff',
	sans400: 'geist-sans/files/geist-sans-latin-400-normal.woff',
	sans500: 'geist-sans/files/geist-sans-latin-500-normal.woff',
	sans600: 'geist-sans/files/geist-sans-latin-600-normal.woff',
	sans700: 'geist-sans/files/geist-sans-latin-700-normal.woff',
	sans800: 'geist-sans/files/geist-sans-latin-800-normal.woff',
	sans900: 'geist-sans/files/geist-sans-latin-900-normal.woff',
	mono400: 'geist-mono/files/geist-mono-latin-400-normal.woff',
	mono700: 'geist-mono/files/geist-mono-latin-700-normal.woff',
	serifItalic: 'instrument-serif/files/instrument-serif-latin-400-italic.woff',
	serif: 'instrument-serif/files/instrument-serif-latin-400-normal.woff',
};
const CHARS = Array.from({length: 95}, (_, i) => String.fromCharCode(32 + i)).join('') + '’‘“”…•—–×→✓¹°·▍█';

const out = {};
for (const [key, file] of Object.entries(FACES)) {
	const buf = fs.readFileSync(path.join(nm, file));
	const font = opentype.parse(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength));
	const em = font.unitsPerEm;
	const adv = {};
	for (const ch of CHARS) {
		const g = font.charToGlyph(ch);
		if (g && g.unicode !== undefined) {
			adv[ch] = Math.round((g.advanceWidth / em) * 10000) / 10000;
		}
	}
	out[key] = {
		ascender: Math.round((font.ascender / em) * 1000) / 1000,
		descender: Math.round((font.descender / em) * 1000) / 1000,
		capHeight: Math.round(((font.tables.os2?.sCapHeight ?? font.ascender * 0.7) / em) * 1000) / 1000,
		fallback: adv.n ?? 0.5,
		adv,
	};
}
const dest = path.join(here, '..', 'src', 'data', 'font-metrics.json');
fs.mkdirSync(path.dirname(dest), {recursive: true});
fs.writeFileSync(dest, JSON.stringify(out));
console.log(`wrote ${path.relative(process.cwd(), dest)}: ${Object.keys(out).length} faces`);
