#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime
import html
import re
import socket

LISTEN = ("127.0.0.1", 5000)          # loopback only: unreachable from outside
SHOW = ("Host", "X-Real-IP", "X-Forwarded-For", "X-Forwarded-Proto",
        "X-Server-Addr", "Connection", "User-Agent")

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Request waybill &mdash; backend behind Nginx</title>
<style>
  :root{
    --desk:#2B2D26; --paper:#E4E2D7; --ink:#23241E;
    --rule:#B7B5A6; --faint:#6E6D60; --stamp:#5A3E9B;
    --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;
    --cond:"Arial Narrow","Helvetica Neue Condensed",Impact,system-ui,sans-serif;
  }
  *{box-sizing:border-box;margin:0}
  body{background:var(--desk);color:var(--ink);font-family:var(--mono);
       padding:40px 16px 64px;display:flex;justify-content:center}
  .sheet{position:relative;width:100%;max-width:680px;background:var(--paper);
         box-shadow:0 18px 40px rgba(0,0,0,.45)}
  .sheet::before{content:"";position:absolute;left:0;right:0;top:-9px;height:9px;
    background:radial-gradient(circle at 6px 9px,var(--desk) 4.5px,var(--paper) 5px) 0 0/12px 9px repeat-x}
  .masthead{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;
            padding:26px 26px 14px;border-bottom:2px solid var(--ink)}
  .issuer{font-size:10px;letter-spacing:.22em;text-transform:uppercase;color:var(--faint)}
  h1{font-family:var(--cond);font-weight:700;font-size:34px;line-height:.95;
     letter-spacing:.04em;text-transform:uppercase}
  .serial{font-size:11px;letter-spacing:.12em;color:var(--faint);text-align:right;white-space:nowrap}
  .route{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 10px;
         padding:14px 26px;border-bottom:1px solid var(--rule);font-size:12px}
  .route i{font-style:normal;color:var(--faint)}
  .route b{font-weight:500}
  .route .last{color:var(--stamp)}
  .note{padding:22px 26px 6px;font-size:12.5px;line-height:1.75;color:#3E4038;max-width:56ch}
  .note em{font-style:normal;background:rgba(90,62,155,.12);padding:0 3px}
  .cap{padding:24px 26px 0;font-family:var(--cond);font-size:13px;font-weight:700;
       letter-spacing:.2em;text-transform:uppercase}
  .fields{padding:8px 26px 26px}
  .f{display:grid;grid-template-columns:minmax(0,15rem) 1fr;align-items:baseline;
     column-gap:12px;padding:9px 0;border-bottom:1px dotted var(--rule)}
  .k{font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--faint)}
  .v{font-size:13px;word-break:break-all}
  .v.off{color:#9C9A8C}
  .v.off::before{content:"\2014 ";color:var(--rule)}
  .stamp{position:absolute;right:22px;bottom:74px;transform:rotate(-7deg);
    padding:8px 14px 7px;border:2px solid var(--stamp);outline:1px solid var(--stamp);
    outline-offset:2px;color:var(--stamp);opacity:.82;mix-blend-mode:multiply;
    font-family:var(--cond);text-transform:uppercase;text-align:center;pointer-events:none}
  .stamp b{display:block;font-size:17px;font-weight:700;letter-spacing:.13em}
  .stamp span{display:block;font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;margin-top:3px}
  .foot{display:flex;flex-wrap:wrap;gap:4px 28px;padding:12px 26px;
        border-top:2px solid var(--ink);font-size:10.5px;letter-spacing:.1em;
        text-transform:uppercase;color:var(--faint)}
  .foot b{font-weight:500;color:var(--ink);text-transform:none;letter-spacing:.04em}
  @media(max-width:560px){
    h1{font-size:26px}
    .masthead{flex-direction:column;align-items:flex-start;gap:8px}
    .serial{text-align:left}
    .f{grid-template-columns:1fr;gap:2px}
    .stamp{position:static;transform:rotate(-2deg);display:block;margin:0 26px 22px}
  }
</style>
</head>
<body>
  <div class="sheet">
    <div class="masthead">
      <div>
        <div class="issuer">Issued by nginx &middot; upstream copy</div>
        <h1>Request<br>waybill</h1>
      </div>
      <div class="serial">delivered {{TIME}}<br>{{HOSTNAME}}</div>
    </div>
    <div class="route">
      <i>from</i> <b>{{CLIENT}}</b>
      <i>via</i> <b>{{EDGE}}</b>
      <i>to</i> <b class="last">127.0.0.1:{{PORT}}</b>
    </div>
    <p class="note">Your browser never opened a socket to this process. It is bound to
      <em>127.0.0.1:{{PORT}}</em> and answers nothing else. Everything below is what actually
      arrived at the application &mdash; Nginx either carried it along or wrote it itself.</p>
    <p class="cap">Headers received</p>
    <div class="fields">
      {{ROWS}}
    </div>
    <div class="stamp"><b>Received<br>via proxy</b><span>port {{PORT}}</span></div>
    <div class="foot">
      <span>status <b>200</b></span>
      <span>path <b>{{PATH}}</b></span>
      <span>sheet 03 / proxied</span>
    </div>
  </div>
</body>
</html>"""

# render pipeline
# Values that never change are baked in once, at import time.
PAGE = (PAGE.replace("{{PORT}}", str(LISTEN[1]))
            .replace("{{HOSTNAME}}", html.escape(socket.gethostname())))

# The rest is split once into literal chunks and placeholder names, so each
# request is a single str.join instead of a chain of full-string copies.
_PARTS = re.split(r"\{\{(\w+)\}\}", PAGE)   # even = literal, odd = key


def render(values):
    out = _PARTS[:]
    for i in range(1, len(out), 2):
        out[i] = values[out[i]]
    return "".join(out)


# Header names and row numbers are static, so pre-build everything around
# the value: only the value itself is escaped per request.
_ROW_HEAD = tuple(
    '<div class="f"><span class="k">%s</span><span class="v' % html.escape(name)
    for name in SHOW
)


class Handler(BaseHTTPRequestHandler):
    server_version = "demo-backend/1.0"
    protocol_version = "HTTP/1.1"      # required for upstream keepalive
    disable_nagle_algorithm = True

    def _page(self):
        get = self.headers.get
        rows = []
        for head, name in zip(_ROW_HEAD, SHOW):
            value = get(name)
            if value:
                rows.append('%s">%s</span></div>' % (head, html.escape(value)))
            else:
                rows.append('%s off">not set</span></div>' % head)

        return render({
            "ROWS": "".join(rows),
            "CLIENT": html.escape(get("X-Real-IP") or self.client_address[0]),
            "EDGE": html.escape(get("X-Server-Addr") or "direct, no proxy"),
            "PATH": html.escape(self.path),
            "TIME": datetime.now().strftime("%H:%M:%S"),
        }).encode("utf-8")

    def _respond(self, payload, body=True):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if body:
            self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self._respond(self._page())

    def do_HEAD(self):
        self._respond(self._page(), body=False)

    def log_message(self, fmt, *args):
        print("[backend] " + fmt % args, flush=True)


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    server = Server(LISTEN, Handler)
    print("listening on %s:%d" % LISTEN, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down", flush=True)
    finally:
        server.server_close()
