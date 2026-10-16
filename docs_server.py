#!/usr/bin/env python3
"""이 폴더를 LAN 에 띄우고, 페이지(index.html)의 저장 요청을 받아 index.html 본문을 바꾼다.

실행: python3 docs_server.py [--port 8098] 후 브라우저로 http://<이 PC 주소>:8098/
본문은 <!--doc-start--><main id="doc" ... data-rev="N"> … </main><!--doc-end--> 사이.
저장할 때마다 이전 판을 doc_backups/ 에 남기고, 옛 판 위에서 고친 저장은 거절한다(409).
"""
import argparse
import json
import re
import shutil
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOC = HERE / "index.html"
BACKUPS = HERE / "doc_backups"
MAX_BYTES = 2 * 1024 * 1024
START, END = "<!--doc-start-->", "<!--doc-end-->"
BODY = re.compile(re.escape(START) + r'<main id="doc" class="wrap" data-rev="(\d+)">.*?</main>' + re.escape(END), re.S)


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _send(self, code, body, ctype="text/plain; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.split("?")[0] == "/__doc_api/ping":
            return self._send(200, b"ok")
        return super().do_GET()

    def do_POST(self):
        if self.path.split("?")[0] != "/__doc_api/save":
            return self._send(404, b"not found")
        n = int(self.headers.get("Content-Length", 0))
        if n <= 0 or n > MAX_BYTES:
            return self._send(413, b"size")
        try:
            req = json.loads(self.rfile.read(n).decode("utf-8"))
            base = int(self.headers.get("X-Base-Rev", "-1"))
        except ValueError:
            return self._send(400, b"bad json")
        html = req.get("html") if isinstance(req, dict) else None
        if not isinstance(html, str) or not html.strip() or START in html or END in html:
            return self._send(400, b"bad html")
        src = DOC.read_text(encoding="utf-8")
        m = BODY.search(src)
        if not m:
            return self._send(500, b"index.html has no doc markers")
        cur = int(m.group(1))
        if base != cur:
            return self._send(409, f"saved revision is {cur}, page was {base}".encode())
        if req.get("rev") != cur + 1:
            return self._send(400, b"rev must be base + 1")
        BACKUPS.mkdir(exist_ok=True)
        shutil.copy2(DOC, BACKUPS / f"index.rev{cur}.{time.strftime('%Y%m%d_%H%M%S')}.html")
        new = f'{START}<main id="doc" class="wrap" data-rev="{cur + 1}">{html}</main>{END}'
        tmp = DOC.with_suffix(".tmp")
        tmp.write_text(src[:m.start()] + new + src[m.end():], encoding="utf-8")
        tmp.replace(DOC)
        self._send(200, json.dumps({"rev": cur + 1}).encode(), "application/json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8098)
    ap.add_argument("--host", default="0.0.0.0")
    a = ap.parse_args()
    print(f"serving {HERE} on http://{a.host}:{a.port}/", flush=True)
    ThreadingHTTPServer((a.host, a.port), partial(Handler, directory=str(HERE))).serve_forever()
