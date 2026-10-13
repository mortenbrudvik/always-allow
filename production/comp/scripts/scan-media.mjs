// Lists the media that exists for the board, so the footage layer shows a shot's clip when it exists, else
// its plate, else its storyboard card (BRIEF.md step 3). Writes src/data/media.generated.json (git-ignored).
//   node scripts/scan-media.mjs
// Looks for, under production/:
//   clips/selects/<clip>.mp4        the accepted take (repaired if it speaks), conformed to 24 fps, no audio
//   clips/mattes/<clip>.webm         a dancer clip cut out with SAM 2 (VP9 with alpha)
//   clips/tracking/<clip>.json       her face landmarks and body boxes per frame
//   assets/frames/<plate>.png|jpg    the picked plate
//   assets/depth/<plate>.png         its depth map (Depth Anything V2), for 2.5D shots
//   assets/thumbs/plates/<plate>.jpg its small copy, and clips/mattes/<clip>_still.png a dancer's cut-out still,
//                                    for the flash-past's mosaic tiles
import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const COMP = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PROD = path.resolve(COMP, '..');
const board = JSON.parse(fs.readFileSync(path.join(PROD, 'storyboard', 'shots.json'), 'utf8'));
const rel = (p) => path.relative(path.resolve(PROD, '..'), p).split(path.sep).join('/');

const probe = (file) => {
	const r = spawnSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries',
		'stream=width,height,r_frame_rate,nb_read_packets', '-of', 'json', file], {encoding: 'utf8'});
	if (r.status !== 0) {
		return {};
	}
	const s = JSON.parse(r.stdout).streams?.[0] ?? {};
	const [n, d] = String(s.r_frame_rate || '0/1').split('/').map(Number);
	return {width: s.width, height: s.height, fps: d ? n / d : null, frames: Number(s.nb_read_packets) || null};
};

const first = (dir, name, exts) => {
	for (const ext of exts) {
		const f = path.join(PROD, dir, `${name}${ext}`);
		if (fs.existsSync(f)) {
			return f;
		}
	}
	return null;
};

const out = {generated: new Date().toISOString(), clips: {}, mattes: {}, tracking: {}, plates: {}};
for (const c of board.clips) {
	const f = first('clips/selects', c.clip, ['.mp4', '.mov']);
	if (f) {
		out.clips[c.clip] = {file: rel(f), ...probe(f)};
	}
	const m = first('clips/mattes', c.clip, ['.webm']);
	if (m) {
		// where her figure stands in the matte's frame (tools/matte.py), for the formations
		const meta = first('clips/mattes', c.clip, ['.json']);
		const figure = meta ? JSON.parse(fs.readFileSync(meta, 'utf8')).figure ?? null : null;
		const still = first('clips/mattes', `${c.clip}_still`, ['.png']);
		out.mattes[c.clip] = {file: rel(m), ...probe(m), figure, still: still ? rel(still) : null};
	}
	const t = first('clips/tracking', c.clip, ['.json']);
	if (t) {
		out.tracking[c.clip] = rel(t);
	}
}
for (const p of board.plates) {
	const f = first('assets/frames', p.plate, ['.png', '.jpg', '.jpeg', '.webp']);
	if (f) {
		const d = first('assets/depth', p.plate, ['.png']);
		const thumb = first('assets/thumbs/plates', p.plate, ['.jpg']);
		out.plates[p.plate] = {file: rel(f), depth: d ? rel(d) : null, thumb: thumb ? rel(thumb) : null};
	}
}
const dest = path.join(COMP, 'src', 'data', 'media.generated.json');
fs.writeFileSync(dest, JSON.stringify(out, null, 1));

// Her tracking, bundled for src/lib/tracking.ts: each clip's file as step 5 wrote it, and each plate's boxes
// (assets/boxes/<plate>.json, fractions of the plate) as her face, twelve landmarks and body in frame pixels.
const KEY = [33, 133, 362, 263, 468, 473, 105, 334, 1, 61, 291, 14]; // tools/track.py's, the tracking layer's order
const px = (b) => ({x: b[0] * 1920, y: b[1] * 1080, w: (b[2] - b[0]) * 1920, h: (b[3] - b[1]) * 1080});
const tracking = {clips: {}, plates: {}};
for (const [clip, file] of Object.entries(out.tracking)) {
	const t = JSON.parse(fs.readFileSync(path.resolve(PROD, '..', file), 'utf8'));
	tracking.clips[clip] = {fps: t.fps, width: t.width, height: t.height, frames: t.frames};
}
for (const p of board.plates) {
	const f = path.join(PROD, 'assets', 'boxes', `${p.plate}.json`);
	if (!fs.existsSync(f)) {
		continue;
	}
	const b = JSON.parse(fs.readFileSync(f, 'utf8'));
	const face = b.faces[0] ?? null;
	const body = b.agent !== null && b.agent !== undefined ? b.bodies[b.agent] : null;
	tracking.plates[p.plate] = {
		face: face ? px(face.box) : null,
		landmarks: face?.landmarks ? KEY.map((k) => [face.landmarks[k][0] * 1920, face.landmarks[k][1] * 1080]) : [],
		body: body ? px(body.box) : null,
		// every figure, for keeping type off their heads where no face was found (src/lib/tracking.ts)
		bodies: face ? [] : b.bodies.filter((d) => d.box[3] - d.box[1] > 0.1).map((d) => px(d.box)),
	};
}
fs.writeFileSync(path.join(COMP, 'src', 'data', 'tracking.generated.json'), JSON.stringify(tracking));
console.log(`media: ${Object.keys(out.clips).length}/${board.clips.length} clips, ${Object.keys(out.mattes).length} mattes, ` +
	`${Object.keys(out.tracking).length} tracking files, ${Object.keys(out.plates).length}/${board.plates.length} plates`);
