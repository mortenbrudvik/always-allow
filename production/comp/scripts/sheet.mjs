// QA contact sheets (BRIEF.md step 7): renders a chapter's frames and tiles them with labels.
//   node scripts/sheet.mjs ch05                 every shot's first and last frame, every line's first and
//                                               last word, each graphic's entrance, each transition's middle
//   node scripts/sheet.mjs frames 0,80,400      any frames (also 12s-14s)
// Options: --scale 0.5 (render size), --cols 4, --width 480 (tile width), --cards, --out DIR.
// Sheets go to production/qa/sheets/<name>.jpg, with the frames in production/qa/sheets/<name>/.
import fs from 'node:fs';
import path from 'node:path';
import {board, ensureMediaServer, FPS, MEDIA_BASE, parseFrames, PROD, prepare, rel, ROOT, run} from './lib.mjs';

const args = process.argv.slice(2);
const opt = (name, dflt) => {
	const i = args.indexOf(`--${name}`);
	return i >= 0 ? args[i + 1] : dflt;
};
const flag = (name) => args.includes(`--${name}`);
const mmss = (f) => {
	const t = f / FPS;
	return `${Math.floor(t / 60)}:${(t % 60).toFixed(2).padStart(5, '0')}`;
};

/** The frames step 7 asks for in a chapter, each with a label. */
const chapterFrames = (b, chapter) => {
	const ch = b.chapters.find((c) => c.chapter === chapter);
	if (!ch) {
		throw new Error(`no chapter ${chapter}`);
	}
	const picks = new Map();
	const add = (f, label) => {
		if (f >= ch.f0 && f < ch.f1 && !picks.has(f)) {
			picks.set(f, label);
		}
	};
	for (const id of ch.shots) {
		const s = b.shots.find((x) => x.id === id);
		add(s.f0, `${id} first`);
		add(Math.min(s.f0 + 8, s.f1 - 1), `${id} graphic in`);
		add(s.f1 - 1, `${id} last`);
		if (s.transition !== 'cut' && s.transition !== 'cold open') {
			add(s.f0 + 3, `${id} ${s.transition.split(':')[0]} (middle)`);
		}
		for (const ly of s.lyrics) {
			const w0 = ly.words[0];
			const w1 = ly.words[ly.words.length - 1];
			add(Math.round(w0.t0 * FPS) + 1, `${id} "${w0.word}" (line ${ly.line} first word)`);
			add(Math.round(w1.t0 * FPS) + 2, `${id} "${w1.word}" (line ${ly.line} last word)`);
		}
	}
	// BRIEF.md step 7: at least MIN_FRAMES a section. A short chapter is topped up with frames in the widest gaps
	// between the ones picked, each labelled with its shot
	const shotAt = (f) => b.shots.find((x) => f >= x.f0 && f < x.f1)?.id ?? '';
	while (picks.size < Math.min(MIN_FRAMES, ch.f1 - ch.f0)) {
		const fs_ = [ch.f0, ...[...picks.keys()].sort((a, c) => a - c), ch.f1];
		let best = 0;
		for (let i = 1; i < fs_.length; i++) {
			if (fs_[i] - fs_[i - 1] > fs_[best + 1] - fs_[best]) {
				best = i - 1;
			}
		}
		const f = Math.floor((fs_[best] + fs_[best + 1]) / 2);
		if (picks.has(f)) {
			break;
		}
		picks.set(f, `${shotAt(f)} (between)`);
	}
	return [...picks.entries()].sort((a, c) => a[0] - c[0]);
};

const MIN_FRAMES = 28;

const main = async () => {
	const b = board();
	let name;
	let frames;
	if (args[0] === 'frames') {
		frames = parseFrames(args[1], b.frames).map((f) => [f, `frame ${f}`]);
		name = opt('name', `frames_${frames[0][0]}`);
	} else {
		frames = chapterFrames(b, args[0]);
		name = args[0];
	}
	const scale = Number(opt('scale', 0.5));
	const outDir = path.resolve(opt('out', path.join(PROD, 'qa', 'sheets', name)));
	fs.rmSync(outDir, {recursive: true, force: true});
	fs.mkdirSync(outDir, {recursive: true});
	const inputProps = {proxy: scale < 0.5, mediaBase: MEDIA_BASE, cards: flag('cards')};
	const stop = await ensureMediaServer();
	const labels = {};
	try {
		const {serveUrl, composition} = await prepare(inputProps);
		const {renderStill, openBrowser} = await import('@remotion/renderer');
		const browser = await openBrowser('chrome', {chromiumOptions: {gl: 'angle'}});
		const t0 = Date.now();
		for (const [f, label] of frames) {
			const file = `f${String(f).padStart(5, '0')}.jpg`;
			await renderStill({composition, serveUrl, frame: f, output: path.join(outDir, file), inputProps, scale, imageFormat: 'jpeg', jpegQuality: 88, puppeteerInstance: browser, chromiumOptions: {gl: 'angle'}});
			labels[file] = `${mmss(f)} · f${f} · ${label}`;
		}
		await browser.close({silent: true});
		const ms = (Date.now() - t0) / frames.length;
		fs.writeFileSync(path.join(outDir, 'labels.json'), JSON.stringify(labels, null, 1));
		console.log(`${frames.length} frames in ${((Date.now() - t0) / 1000).toFixed(1)} s (${ms.toFixed(0)} ms a frame at scale ${scale})`);
	} finally {
		stop();
	}
	const sheetFile = path.join(PROD, 'qa', 'sheets', `${name}.jpg`);
	const py = path.join(ROOT, '.venv', 'Scripts', 'python');
	run(py, [path.join(ROOT, 'tools', 'contact_sheet.py'), outDir, '--out', sheetFile, '--cols', opt('cols', '4'), '--width', opt('width', '480'),
		'--title', `${name}: ${frames.length} frames`]);
	console.log(`sheet: ${rel(sheetFile)}`);
};

main().catch((e) => {
	console.error(e);
	process.exit(1);
});
