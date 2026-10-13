// Where the lyric engine put one line, and the face boxes it had to clear: for debugging a line on her face.
//   npx --prefix production/comp tsx production/comp/scripts/debug-line.ts 61   (from the repo root)
import '../src/chapters';
import {shots} from '../src/lib/data';
import {placedLines} from '../src/lib/lyrics';
import {faceOver, trackAt} from '../src/lib/tracking';
import {plannedFace} from '../src/lib/layout';

const line = Number(process.argv[2]);
for (const l of placedLines().filter((x) => x.line === line)) {
	console.log(JSON.stringify({line: l.line, part: l.part, text: l.text, mode: l.mode, zone: l.zone, boardZone: l.boardZone, size: l.size, box: l.box, t0: l.t0, tEnd: l.tEnd, faceClash: l.faceClash}));
	for (const s of shots.filter((x) => x.t1 > l.t0 && x.t0 < l.tEnd)) {
		const f = Math.round(((Math.max(l.t0, s.t0) + Math.min(l.tEnd, s.t1)) / 2) * 24);
		console.log(`  ${s.id} ${s.framing} faceOver=${JSON.stringify(faceOver(s, Math.max(l.t0, s.t0), Math.min(l.tEnd, s.t1)))} planned=${JSON.stringify(plannedFace(s))} trackAt(f${f})=${JSON.stringify(trackAt(s, f)?.face ?? null)}`);
	}
}
