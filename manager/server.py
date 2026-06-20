"""
server.py — HTTP 服务器
按 /prd/ 路径提供 PRD 页面和后台管理
"""
import http.server
import socketserver
import threading
import json
import os
import urllib.parse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PRD_ROOT = PROJECT_ROOT / "prd" if (PROJECT_ROOT / "prd").exists() else PROJECT_ROOT
PORT = 18900


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, f, *a): pass

    def _send(self, data, ct="application/json; charset=utf-8", code=200):
        self.send_response(code)
        self.send_header("Content-Type", ct)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        if isinstance(data, str): data = data.encode("utf-8")
        elif isinstance(data, bytes): pass
        else: data = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.wfile.write(data)

    def _read_body(self):
        n = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(n).decode("utf-8") if n else ""

    def _query(self, name):
        qs = urllib.parse.urlparse(self.path).query
        return urllib.parse.parse_qs(qs).get(name, [None])[0]

    def _serve_file(self, path):
        fp = PRD_ROOT / path
        if not fp.exists():
            return self.send_error(404)
        ct = {".html":"text/html",".css":"text/css",".js":"application/javascript",".json":"application/json",".md":"text/markdown",".txt":"text/plain"}.get(fp.suffix, "application/octet-stream")
        self._send(fp.read_bytes(), ct)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        p = urllib.parse.urlparse(self.path).path

        # API
        if p == "/prd/api/config":
            try: data = json.loads((PRD_ROOT / "config.json").read_text(encoding="utf-8"))
            except: data = {}
            return self._send(data)
        if p == "/prd/api/content":
            f = self._query("file") or ""
            return self._send({"content": (PRD_ROOT / f).read_text(encoding="utf-8") if (PRD_ROOT / f).exists() else ""})
        if p == "/prd/api/scan":
            folder = self._query("folder") or "tabs"
            fp = PRD_ROOT / folder
            files = [str(f.relative_to(PRD_ROOT)) for f in sorted(fp.glob("*")) if f.is_file() and not f.name.startswith(".")] if fp.exists() else []
            return self._send({"files": files})
        if p == "/prd/api/delete":
            f = self._query("file") or ""
            try: (PRD_ROOT / f).unlink(); return self._send({"ok": True})
            except Exception as e: return self._send({"ok": False, "error": str(e)})

        # Pages
        if p == "/prd/" or p == "/prd":
            return self._serve_file("index.html")
        if p == "/prd/manager" or p == "/prd/manager/":
            return self._serve_file("manager/index.html")
        if p.startswith("/prd/"):
            return self._serve_file(p[5:])  # strip /prd/ prefix

        # Project root static files
        fp = PROJECT_ROOT / p.lstrip("/")
        if fp.exists() and fp.is_file():
            return self._send(fp.read_bytes(), "application/octet-stream")
        self.send_error(404)

    def do_POST(self):
        p = urllib.parse.urlparse(self.path).path
        body = self._read_body()
        if p == "/prd/api/config":
            (PRD_ROOT / "config.json").write_text(body, encoding="utf-8")
            return self._send({"ok": True})
        if p == "/prd/api/content":
            f = self._query("file") or ""
            (PRD_ROOT / f).parent.mkdir(parents=True, exist_ok=True)
            (PRD_ROOT / f).write_text(body, encoding="utf-8")
            return self._send({"ok": True})
        if p == "/prd/api/rename":
            try:
                d = json.loads(body); o, n = PRD_ROOT / d["old"], PRD_ROOT / d["new"]
                if o.exists(): o.rename(n)
                return self._send({"ok": True})
            except Exception as e: return self._send({"ok": False, "error": str(e)})
        self.send_error(404)


class Server:
    def __init__(self, port=PORT): self.port = port; self._srv = None; self._t = None; self._run = False
    @property
    def url(self): return f"http://127.0.0.1:{self.port}"
    @property
    def is_running(self): return self._run
    def start(self):
        if self._run: return
        os.chdir(str(PROJECT_ROOT))
        self._srv = socketserver.TCPServer(("127.0.0.1", self.port), Handler)
        self._srv.allow_reuse_address = True
        self._t = threading.Thread(target=self._srv.serve_forever, daemon=True)
        self._t.start(); self._run = True
    def stop(self):
        if self._srv: self._srv.shutdown(); self._srv.server_close(); self._run = False

_srv = None
def get_server(port=PORT):
    global _srv
    if not _srv: _srv = Server(port)
    return _srv
def start():
    s = get_server(); s.start()
    print(f"PRD: {s.url}/prd/")
    print(f"后台: {s.url}/prd/manager/")
    return s
