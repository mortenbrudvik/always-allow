// Shared by the render and contact-sheet scripts: paths, the media server, the bundle, the composition.
import {spawn, spawnSync} from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

export const COMP = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const PROD = path.resolve(COMP, '..');
export const ROOT = path.resolve(PROD, '..');
export const SONG = path.join(ROOT, 'Always Allow.mp3');
export const FPS = 24;
export const MEDIA_PORT = Number(process.env.MEDIA_PORT || 8765);
export const MEDIA_BASE = `http://127.0.0.1:${MEDIA_PORT}`;

export const board = () => JSON.parse(fs.readFileSync(path.join(PROD, 'storyboard', 'shots.json'), 'utf8'));

export const rel = (p) => path.relative(ROOT, p).split(path.sep).join('/');

export const run = (cmd, args, opts = {}) => {
	const r = spawnSync(cmd, args, {stdio: 'inherit', ...opts});
	if (r.status !== 0) {
		throw new Error(`${cmd} ${args.slice(0, 3).join(' ')}… exited with ${r.status}`);
	}
};

const up = () =>
	new Promise((resolve) => {
		const req = http.request({host: '127.0.0.1', port: MEDIA_PORT, path: '/Always%20Allow.mp3', method: 'HEAD', timeout: 1500}, (res) => {
			resolve(res.statusCode === 200);
			res.resume();
		});
		req.on('error', () => resolve(false));
		req.on('timeout', () => {
			req.destroy();
			resolve(false);
		});
		req.end();
	});

/** Start the media server for this run if none is serving yet; returns a stop function. */
export const ensureMediaServer = async () => {
	if (await up()) {
		return () => {};
	}
	const child = spawn(process.execPath, [path.join(COMP, 'scripts', 'media-server.mjs'), String(MEDIA_PORT)], {stdio: 'ignore'});
	for (let i = 0; i < 40 && !(await up()); i++) {
		await new Promise((r) => setTimeout(r, 150));
	}
	if (!(await up())) {
		child.kill();
		throw new Error('the media server did not start');
	}
	return () => child.kill();
};

/** Scan the media, bundle the project once, and pick the composition with these props. */
export const prepare = async (inputProps, id = 'Main') => {
	run(process.execPath, [path.join(COMP, 'scripts', 'scan-media.mjs')]);
	const {bundle} = await import('@remotion/bundler');
	const {selectComposition} = await import('@remotion/renderer');
	const t0 = Date.now();
	const serveUrl = await bundle({entryPoint: path.join(COMP, 'src', 'index.ts'), onProgress: () => {}});
	console.log(`bundled in ${((Date.now() - t0) / 1000).toFixed(1)} s`);
	const composition = await selectComposition({serveUrl, id, inputProps, chromiumOptions: {gl: 'angle'}});
	return {serveUrl, composition};
};

export const parseFrames = (spec, total) => {
	// "0,80,400" or "100-200" or "10s-12s" (seconds) or "bar:35.5" handled by callers
	const out = [];
	for (const part of String(spec).split(',').filter(Boolean)) {
		const m = /^(\d+(?:\.\d+)?)(s?)(?:-(\d+(?:\.\d+)?)(s?))?$/.exec(part.trim());
		if (!m) {
			throw new Error(`bad frame spec ${part}`);
		}
		const a = m[2] ? Math.round(Number(m[1]) * FPS) : Number(m[1]);
		const b = m[3] === undefined ? a : m[4] ? Math.round(Number(m[3]) * FPS) : Number(m[3]);
		for (let f = a; f <= b; f++) {
			if (f >= 0 && f < total) {
				out.push(f);
			}
		}
	}
	return out;
};

export const ffprobeDuration = (file) => {
	const r = spawnSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', file], {encoding: 'utf8'});
	return Number(r.stdout.trim());
};
