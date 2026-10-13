// The lyric check (BRIEF.md step 3): every word in production/analysis/words.json is on screen for every
// frame from its start to its end, at 40 px or more at 1080p, inside the frame, and not over her planned
// face. It asks the same engine the renderer draws from (src/lib/lyrics.ts), so what passes here is
// what's drawn. Exits 1 on any miss.
//   npm --prefix production/comp run check:lyrics            (all lines)
//   npm --prefix production/comp run check:lyrics -- 60 90    (only words starting between 60 and 90 s)
import {wordsFile} from '../src/lib/data';
import '../src/chapters'; // the chapters register their formations, whose heads the lines keep clear of
import {MIN_LYRIC_PX, placedLines as placedAll, visibleAt} from '../src/lib/lyrics';

const placedLines = placedAll();
import {H, W} from '../src/lib/theme';
import {FPS} from '../src/lib/time';

const [from, to] = process.argv.slice(2).map(Number);
const lo = Number.isFinite(from) ? from : -1;
const hi = Number.isFinite(to) ? to : Infinity;

const problems: string[] = [];
let checked = 0;
let onScreen = 0;
const expected = wordsFile.lines.reduce((n, l) => n + l.words.filter((w) => w.start >= lo && w.start < hi).length, 0);

for (const line of placedLines) {
	if (line.size < MIN_LYRIC_PX) {
		problems.push(`line ${line.line} (${line.text}): ${line.size} px, under ${MIN_LYRIC_PX}`);
	}
	const b = line.box;
	if (b.x < 0 || b.y < 0 || b.x + b.w > W || b.y + b.h > H) {
		problems.push(`line ${line.line} (${line.text}): its box ${JSON.stringify(b)} leaves the frame`);
	}
	if (line.faceClash) {
		problems.push(`line ${line.line} (${line.text}): over her planned face in ${line.shot.id} in every zone tried`);
	}
	line.tokens.forEach((tok, idx) => {
		if (tok.echo || tok.t0 < lo || tok.t0 >= hi) {
			return;
		}
		checked++;
		const f0 = Math.round(tok.t0 * FPS);
		const f1 = Math.max(f0, Math.round(tok.t1 * FPS) - 1);
		let missing = 0;
		for (let f = f0; f <= f1; f++) {
			const vis = visibleAt(f).find((v) => v.line === line);
			if (!vis || !vis.tokens.includes(line.tokens[idx])) {
				missing++;
			}
		}
		if (missing) {
			problems.push(`line ${line.line} word "${tok.word}" (${tok.t0.toFixed(2)}-${tok.t1.toFixed(2)} s): off screen for ${missing} of ${f1 - f0 + 1} frames`);
		} else {
			onScreen++;
		}
	});
}

console.log(`${onScreen}/${checked} lyric words on screen on their time (words.json has ${expected} in range); ` +
	`${new Set(placedLines.map((l) => l.line)).size} lines in ${placedLines.length} parts, main lyric ${Math.min(...placedLines.map((l) => l.size))}-${Math.max(...placedLines.map((l) => l.size))} px`);
const moved = placedLines.filter((l) => l.zone !== l.boardZone);
if (moved.length) {
	console.log(`moved off her face: ${moved.map((l) => `line ${l.line} ${l.boardZone}->${l.zone}`).join(', ')}`);
}
for (const p of problems) {
	console.log('PROBLEM:', p);
}
if (checked !== expected) {
	console.log(`PROBLEM: checked ${checked} words but words.json has ${expected}`);
	process.exitCode = 1;
}
process.exitCode = problems.length ? 1 : process.exitCode ?? 0;
