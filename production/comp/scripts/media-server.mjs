// A read-only media server for renders and the studio: the plates, clips, depth maps, mattes and the song,
// straight from the repo, so nothing gigabytes-large is copied into Remotion's bundle (on Windows it always
// copies its public folder). Local only (127.0.0.1), with CORS so the print pass can read frames into WebGL,
// and byte ranges so video seeks.
//   node scripts/media-server.mjs [port]      (default 8765)
// Serves only the master MP3 and production/ (not .env, not the rest of the repo).
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
const PORT = Number(process.argv[2] || process.env.MEDIA_PORT || 8765);
const ALLOWED = [path.join(ROOT, 'Always Allow.mp3'), path.join(ROOT, 'production') + path.sep];
const TYPES = {
	'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp',
	'.mp4': 'video/mp4', '.webm': 'video/webm', '.mov': 'video/quicktime', '.mp3': 'audio/mpeg',
	'.wav': 'audio/wav', '.json': 'application/json', '.txt': 'text/plain; charset=utf-8',
};

const resolveSafe = (urlPath) => {
	const rel = decodeURIComponent(urlPath.split('?')[0]).replace(/^\/+/, '');
	const full = path.resolve(ROOT, rel);
	return ALLOWED.some((a) => full === a || (a.endsWith(path.sep) && full.startsWith(a))) ? full : null;
};

const server = http.createServer((req, res) => {
	res.setHeader('Access-Control-Allow-Origin', '*');
	res.setHeader('Access-Control-Allow-Headers', 'Range');
	res.setHeader('Access-Control-Expose-Headers', 'Content-Length, Content-Range, Accept-Ranges');
	if (req.method === 'OPTIONS') {
		res.writeHead(204).end();
		return;
	}
	if (req.method !== 'GET' && req.method !== 'HEAD') {
		res.writeHead(405).end();
		return;
	}
	const file = resolveSafe(req.url || '/');
	if (!file || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
		res.writeHead(404).end('not found');
		return;
	}
	const size = fs.statSync(file).size;
	const type = TYPES[path.extname(file).toLowerCase()] || 'application/octet-stream';
	const range = /bytes=(\d*)-(\d*)/.exec(req.headers.range || '');
	if (range) {
		const start = range[1] ? Number(range[1]) : Math.max(0, size - Number(range[2]));
		const end = range[1] && range[2] ? Math.min(Number(range[2]), size - 1) : size - 1;
		if (start >= size || start > end) {
			res.writeHead(416, {'Content-Range': `bytes */${size}`}).end();
			return;
		}
		res.writeHead(206, {'Content-Type': type, 'Content-Length': end - start + 1, 'Content-Range': `bytes ${start}-${end}/${size}`, 'Accept-Ranges': 'bytes'});
		if (req.method === 'HEAD') {
			res.end();
			return;
		}
		fs.createReadStream(file, {start, end}).pipe(res);
		return;
	}
	res.writeHead(200, {'Content-Type': type, 'Content-Length': size, 'Accept-Ranges': 'bytes'});
	if (req.method === 'HEAD') {
		res.end();
		return;
	}
	fs.createReadStream(file).pipe(res);
});

server.on('error', (e) => {
	if (e.code === 'EADDRINUSE') {
		console.log(`port ${PORT} is already serving (another media server); leaving it`);
		process.exit(0);
	}
	throw e;
});
server.listen(PORT, '127.0.0.1', () => console.log(`media server: http://127.0.0.1:${PORT}/ (the song and production/)`));
