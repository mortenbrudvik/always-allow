"""Save Midjourney images straight from the browser page, with no download dialog per file (BRIEF.md step 4).

The Midjourney page can fetch its own full-size PNGs from cdn.midjourney.com, but every browser download of one asks
for an OK. This receiver, on 127.0.0.1 only, takes the image the page posts and writes it into
production/assets/mj/inbox/. It accepts requests only from https://www.midjourney.com and only with the token it
prints at start, and it writes nothing but .png files with plain names.

Usage, with the project's .venv (it runs until stopped):
  .venv/Scripts/python tools/mj_receive.py            # prints the token
In the page:
  const r = await fetch(`https://cdn.midjourney.com/${job}/0_${i}.png`);
  await fetch(`http://127.0.0.1:8767/save?token=${token}&name=${plate}_${job}_${i}.png`, {method: 'POST', body: await r.blob()});
"""
import json
import re
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
INBOX = ROOT / "production" / "assets" / "mj" / "inbox"
ORIGIN = "https://www.midjourney.com"
PORT = 8767
TOKEN = secrets.token_hex(12)
NAME = re.compile(r"^[A-Za-z0-9_.-]{1,160}\.png$")
PNG = b"\x89PNG\r\n\x1a\n"


class Handler(BaseHTTPRequestHandler):
    def cors(self):
        self.send_header("Access-Control-Allow-Origin", ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def reply(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):  # the browser's preflight, before the page may post to a local address
        self.send_response(204)
        self.cors()
        self.end_headers()

    def do_POST(self):
        url = urlparse(self.path)
        q = parse_qs(url.query)
        if url.path != "/save" or q.get("token", [""])[0] != TOKEN or self.headers.get("Origin") != ORIGIN:
            return self.reply(403, {"error": "forbidden"})
        name = q.get("name", [""])[0]
        if not NAME.match(name):
            return self.reply(400, {"error": "bad name"})
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if not body.startswith(PNG):
            return self.reply(400, {"error": "not a png"})
        dest = INBOX / name
        if dest.exists():
            return self.reply(409, {"error": "exists", "name": name})
        INBOX.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(body)
        print(f"saved {name} ({len(body):,} bytes)", flush=True)
        return self.reply(200, {"saved": name, "bytes": len(body)})

    def log_message(self, *args):
        pass


def main():
    print(f"token {TOKEN}", flush=True)
    print(f"saving to {INBOX}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
