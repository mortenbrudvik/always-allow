// Renders the video (BRIEF.md step 3's proxy renders, and the rough cut and masters later).
//   node scripts/render.mjs animatic            the 640x360 proxy: production/animatic/animatic.mp4
//   node scripts/render.mjs full               1920x1080: production/out/roughcut.mp4
//   node scripts/render.mjs stills FRAMES [--scale 0.5] [--out DIR] [--timing] [--png]   stills as JPEG, or PNG (FRAMES: 0,80,400 or 100-120 or 12s-14s);
//                                               --timing lists each frame's render time, for the budget
//   node scripts/render.mjs range FRAMES --out FILE.mp4 [--scale 1]   a stretch of the video, with the song under it
//   node scripts/render.mjs teaser             the 9:16 teaser over the master (src/Teaser.tsx), its bars of the song under it
// Options: --concurrency N (default 8), --cards (storyboard cards everywhere, even where footage exists).
// The soundtrack is Always Allow.mp3, unedited: renders are silent and the song is muxed in with ffmpeg,
// trimmed only for a range render.
import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {board, ensureMediaServer, FPS, MEDIA_BASE, parseFrames, PROD, prepare, rel, run, SONG} from './lib.mjs';

const args = process.argv.slice(2);
const cmd = args[0];
const opt = (name, dflt) => {
	const i = args.indexOf(`--${name}`);
	return i >= 0 ? args[i + 1] : dflt;
};
const flag = (name) => args.includes(`--${name}`);
const concurrency = Number(opt('concurrency', Math.max(2, Math.min(8, os.cpus().length - 2))));

/** The song under the silent render: all of it, untouched, for the whole video (the last frame holds for the song's
 * last few milliseconds); the matching stretch of it for a range. No -shortest: it drops video frames at the end. */
const mux = (video, range, out, aacKbps = 320) => {
	const cut = range ? ['-ss', range.start.toFixed(4), '-t', range.seconds.toFixed(4)] : [];
	run('ffmpeg', ['-v', 'error', '-y', '-i', video, ...cut, '-i', SONG,
		'-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', `${aacKbps}k`, '-movflags', '+faststart', out]);
};

/** The frames in a file's video stream, counted. */
const countFrames = (file) => {
	const r = spawnSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries', 'stream=nb_read_packets',
		'-of', 'csv=p=0', file], {encoding: 'utf8'});
	return parseInt(r.stdout, 10); // ffprobe prints it as '6662,'
};

const main = async () => {
	if (!['animatic', 'full', 'stills', 'range', 'teaser'].includes(cmd)) {
		console.log(fs.readFileSync(new URL(import.meta.url), 'utf8').split('\n').filter((l) => l.startsWith('//')).join('\n'));
		process.exit(1);
	}
	const proxy = cmd === 'animatic' || Number(opt('scale', cmd === 'stills' ? 0.5 : 1)) < 0.5;
	const inputProps = {proxy, mediaBase: MEDIA_BASE, cards: flag('cards')};
	const stop = await ensureMediaServer();
	try {
		const {serveUrl, composition} = await prepare(inputProps, cmd === 'teaser' ? 'Teaser' : 'Main');
		const {renderMedia, renderStill, openBrowser} = await import('@remotion/renderer');
		const total = composition.durationInFrames;
		const chromiumOptions = {gl: 'angle'};
		if (cmd === 'stills') {
			const frames = parseFrames(args[1], total);
			const scale = Number(opt('scale', 0.5));
			const outDir = path.resolve(opt('out', path.join(PROD, 'qa', 'stills')));
			fs.mkdirSync(outDir, {recursive: true});
			const browser = await openBrowser('chrome', {chromiumOptions});
			const t0 = Date.now();
			const times = [];
			const png = flag('png'); // lossless stills, for the thumbnails
			for (const frame of frames) {
				const output = path.join(outDir, `f${String(frame).padStart(5, '0')}.${png ? 'png' : 'jpg'}`);
				const f0 = Date.now();
				await renderStill({composition, serveUrl, frame, output, inputProps, scale, ...(png ? {imageFormat: 'png'} : {imageFormat: 'jpeg', jpegQuality: 90}), puppeteerInstance: browser, chromiumOptions});
				times.push([frame, Date.now() - f0]);
			}
			if (flag('timing')) {
				// the render budget (ANIMATION_GUIDE.md): every frame's time, slowest first
				for (const [frame, ms] of [...times].sort((a, b) => b[1] - a[1])) {
					console.log(`frame ${frame}  ${ms} ms`);
				}
			}
			await browser.close({silent: true});
			console.log(`${frames.length} stills in ${((Date.now() - t0) / 1000).toFixed(1)} s (${((Date.now() - t0) / frames.length).toFixed(0)} ms each) -> ${rel(outDir)}`);
			return;
		}
		const scale = cmd === 'animatic' ? 1 / 3 : Number(opt('scale', 1));
		let frameRange = null;
		let out;
		if (cmd === 'animatic') {
			out = path.join(PROD, 'animatic', 'animatic.mp4');
		} else if (cmd === 'full') {
			out = path.join(PROD, 'out', 'roughcut.mp4');
		} else if (cmd === 'teaser') {
			out = path.join(PROD, 'out', 'always-allow_teaser_9x16.mp4');
		} else {
			const frames = parseFrames(args[1], total);
			frameRange = [frames[0], frames[frames.length - 1]];
			out = path.resolve(opt('out', path.join(PROD, 'qa', `range_${frameRange[0]}-${frameRange[1]}.mp4`)));
		}
		fs.mkdirSync(path.dirname(out), {recursive: true});
		const silent = out.replace(/\.mp4$/, '.video.mp4');
		const t0 = Date.now();
		let last = -1;
		await renderMedia({
			composition, serveUrl, codec: 'h264', outputLocation: silent, inputProps, scale, concurrency, frameRange, muted: true,
			imageFormat: 'jpeg', jpegQuality: 90, crf: cmd === 'full' || cmd === 'teaser' ? 16 : 20, pixelFormat: 'yuv420p', chromiumOptions,
			onProgress: ({progress, renderedFrames}) => {
				const pct = Math.floor(progress * 100);
				if (pct >= last + 5) {
					last = pct;
					const s = (Date.now() - t0) / 1000;
					console.log(`${pct}%  ${renderedFrames} frames  ${s.toFixed(0)} s  (${(renderedFrames / Math.max(s, 1)).toFixed(1)} fps)`);
				}
			},
		});
		const secs = (Date.now() - t0) / 1000;
		const n = frameRange ? frameRange[1] - frameRange[0] + 1 : total;
		if (cmd === 'teaser') {
			// the teaser's own stretch of the song, from its first frame in the master (a bar line), with a short fade at either end
			const start = composition.props.from / FPS;
			const secs = total / FPS;
			run('ffmpeg', ['-v', 'error', '-y', '-i', silent, '-ss', start.toFixed(4), '-t', secs.toFixed(4), '-i', SONG,
				'-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', `afade=t=in:d=0.05,afade=t=out:st=${(secs - 0.6).toFixed(3)}:d=0.6`,
				'-c:a', 'aac', '-b:a', '320k', '-movflags', '+faststart', out]);
		} else {
			mux(silent, frameRange ? {start: frameRange[0] / FPS, seconds: n / FPS} : null, out, cmd === 'full' ? 320 : 192);
		}
		const muxed = countFrames(out);
		if (muxed !== n) {
			throw new Error(`${rel(out)} has ${muxed} frames, not ${n}; the silent render is kept at ${rel(silent)}`);
		}
		fs.rmSync(silent);
		const note = {rendered: new Date().toISOString(), what: cmd, frames: n, scale, concurrency, seconds: Math.round(secs),
			ms_per_frame: Math.round((secs * 1000) / n), ms_per_frame_per_worker: Math.round((secs * 1000 * concurrency) / n),
			shots: board().shots.length, output: rel(out)};
		fs.writeFileSync(out.replace(/\.mp4$/, '.render.json'), JSON.stringify(note, null, 1));
		console.log(`${rel(out)}: ${n} frames in ${secs.toFixed(0)} s, ${note.ms_per_frame} ms a frame (${note.ms_per_frame_per_worker} ms per frame per worker at ${concurrency} workers)`);
	} finally {
		stop();
	}
};

main().catch((e) => {
	console.error(e);
	process.exit(1);
});
