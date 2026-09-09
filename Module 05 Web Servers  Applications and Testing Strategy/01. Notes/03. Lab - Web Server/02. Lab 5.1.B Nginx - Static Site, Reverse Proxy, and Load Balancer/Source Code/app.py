#!/usr/bin/env python3
"""Real-time server monitoring dashboard.

Origin backend for the Nginx reverse proxy lab. Binds 0.0.0.0:5000 and serves:

  /              live dashboard, updated once per second over Server-Sent Events
  /events        the metrics stream (text/event-stream)
  /api/metrics   one-shot JSON snapshot, for curl verification through the proxy
  /favicon.ico   204

Every response still carries the lab's reverse-proxy evidence: the TCP peer
and the headers Nginx injected (X-Real-IP, X-Forwarded-For, Via). Metrics are
read from /proc with the standard library only. No third-party packages.
"""

import json
import os
import shutil
import socket
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LISTEN = ("0.0.0.0", 5000)
TICK = 1.0                     # seconds between stream updates
PROXY_HEADERS = ("Host", "X-Real-IP", "X-Forwarded-For", "X-Forwarded-Proto", "Via")

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>backend.test - live monitor</title>
<style>
 body { font-family: monospace; background: #1e1e1e; color: #d4d4d4; padding: 1.5em; max-width: 64em; margin: auto; }
 h1 { color: #4ec9b0; font-size: 20px; }
 h1 small { color: #888; font-size: 12px; }
 #dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #f44747; margin-right: 6px; }
 #dot.on { background: #4ec9b0; }
 .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(11em, 1fr)); gap: 10px; margin: 1em 0; }
 .card { background: #252526; border: 1px solid #333; border-radius: 6px; padding: 10px 12px; }
 .k { color: #9cdcfe; font-size: 12px; }
 .v { font-size: 20px; margin-top: 4px; }
 #ev { background: #252526; border: 1px solid #333; border-radius: 6px; padding: 10px 12px; font-size: 13px; }
 #ev td { padding: 2px 10px 2px 0; color: #ce9178; }
 #ev td:first-child { color: #9cdcfe; }
 canvas { width: 100%; height: 90px; background: #252526; border: 1px solid #333; border-radius: 6px; }
</style>
</head>
<body>
<h1><span id="dot"></span>backend.test &mdash; live server monitor <small id="clock"></small></h1>
<div id="ev"><table>
<tr><td>served by</td><td id="host">-</td><td>socket</td><td id="sock">-</td></tr>
<tr><td>TCP peer</td><td id="peer">-</td><td>X-Real-IP</td><td id="xri">-</td></tr>
<tr><td>X-Forwarded-For</td><td id="xff">-</td><td>Via</td><td id="via">-</td></tr>
</table></div>
<div class="grid">
 <div class="card"><div class="k">CPU</div><div class="v" id="cpu">-</div></div>
 <div class="card"><div class="k">Memory</div><div class="v" id="mem">-</div></div>
 <div class="card"><div class="k">Disk /</div><div class="v" id="disk">-</div></div>
 <div class="card"><div class="k">Load 1 / 5 / 15</div><div class="v" id="load">-</div></div>
 <div class="card"><div class="k">Net rx / tx KB/s</div><div class="v" id="net">-</div></div>
 <div class="card"><div class="k">Uptime</div><div class="v" id="up">-</div></div>
 <div class="card"><div class="k">Processes</div><div class="v" id="proc">-</div></div>
</div>
<canvas id="chart" width="900" height="90"></canvas>
<script>
var hist = [];
function put(id, txt) { document.getElementById(id).textContent = txt; }
function draw() {
  var c = document.getElementById('chart'), g = c.getContext('2d');
  g.clearRect(0, 0, c.width, c.height);
  var w = c.width / 90;
  for (var i = 0; i < hist.length; i++) {
    var h = Math.min(100, hist[i]) / 100 * c.height;
    g.fillStyle = hist[i] > 80 ? '#f44747' : '#4ec9b0';
    g.fillRect(i * w, c.height - h, Math.max(1, w - 1), h);
  }
}
var es = new EventSource('/events');
es.onopen  = function () { document.getElementById('dot').className = 'on'; };
es.onerror = function () { document.getElementById('dot').className = ''; };
es.onmessage = function (e) {
  var d = JSON.parse(e.data), m = d.metrics, r = d.request;
  put('clock', m.time);
  put('host', m.hostname); put('sock', r.socket);
  put('peer', r.peer);
  put('xri', r.headers['X-Real-IP']);
  put('xff', r.headers['X-Forwarded-For']);
  put('via', r.headers['Via']);
  put('cpu', m.cpu + ' %');
  put('mem', m.mem.used_mb + ' / ' + m.mem.total_mb + ' MB (' + m.mem.percent + ' %)');
  put('disk', m.disk.used_gb + ' / ' + m.disk.total_gb + ' GB (' + m.disk.percent + ' %)');
  put('load', m.load['1m'] + '  ' + m.load['5m'] + '  ' + m.load['15m']);
  put('net', m.net.rx_kbps + ' / ' + m.net.tx_kbps);
  put('up', m.uptime);
  put('proc', m.procs);
  hist.push(m.cpu); if (hist.length > 90) hist.shift(); draw();
};
</script>
</body>
</html>
"""


# ---------------------------------------------------------------- metrics ---

def _cpu_times():
    with open("/proc/stat") as f:
        fields = f.readline().split()[1:]
    values = [int(x) for x in fields]
    idle = values[3] + values[4]          # idle + iowait
    return idle, sum(values)


def _net_bytes():
    rx = tx = 0
    with open("/proc/net/dev") as f:
        for line in f:
            if ":" not in line:
                continue
            iface, data = line.split(":", 1)
            if iface.strip() == "lo":
                continue
            cols = data.split()
            rx += int(cols[0])
            tx += int(cols[8])
    return rx, tx


def _memory():
    info = {}
    with open("/proc/meminfo") as f:
        for line in f:
            key, val = line.split(":", 1)
            info[key] = int(val.split()[0])          # kB
    total = info["MemTotal"]
    used = total - info["MemAvailable"]
    return {"total_mb": total // 1024, "used_mb": used // 1024,
            "percent": round(100.0 * used / total, 1)}


def _disk():
    usage = shutil.disk_usage("/")
    return {"total_gb": round(usage.total / 2**30, 1),
            "used_gb": round(usage.used / 2**30, 1),
            "percent": round(100.0 * usage.used / usage.total, 1)}


def _uptime():
    with open("/proc/uptime") as f:
        secs = int(float(f.read().split()[0]))
    days, rem = divmod(secs, 86400)
    hours, rem = divmod(rem, 3600)
    return ("%dd %02d:%02d" % (days, hours, rem // 60)) if days else ("%02d:%02d" % (hours, rem // 60))


class Meter:
    """Rate metrics (CPU %, network KB/s) from successive counter samples.

    Results are cached for just under one tick so multiple connected
    dashboards share one measurement instead of racing the counters.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._cpu = _cpu_times()
        rx, tx = _net_bytes()
        self._net = (rx, tx, time.monotonic())
        self._cache = None
        self._cache_t = 0.0

    def sample(self):
        with self._lock:
            now = time.monotonic()
            if self._cache is not None and now - self._cache_t < TICK - 0.1:
                return self._cache

            idle, total = _cpu_times()
            p_idle, p_total = self._cpu
            d_idle, d_total = idle - p_idle, total - p_total
            cpu = 0.0 if d_total <= 0 else round(100.0 * (1.0 - d_idle / d_total), 1)
            self._cpu = (idle, total)

            rx, tx = _net_bytes()
            p_rx, p_tx, p_t = self._net
            dt = now - p_t
            net = {"rx_kbps": round((rx - p_rx) / 1024.0 / dt, 1) if dt > 0 else 0.0,
                   "tx_kbps": round((tx - p_tx) / 1024.0 / dt, 1) if dt > 0 else 0.0}
            self._net = (rx, tx, now)

            load = os.getloadavg()
            metrics = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "hostname": socket.gethostname(),
                "uptime": _uptime(),
                "cpu": cpu,
                "load": {"1m": round(load[0], 2), "5m": round(load[1], 2), "15m": round(load[2], 2)},
                "mem": _memory(),
                "disk": _disk(),
                "net": net,
                "procs": sum(1 for name in os.listdir("/proc") if name.isdigit()),
            }
            self._cache, self._cache_t = metrics, now
            return metrics


METER = Meter()


def request_info(handler):
    """The lab evidence: who opened the TCP connection, and what Nginx added."""
    return {
        "peer": handler.client_address[0],
        "socket": "%s:%d" % handler.connection.getsockname()[:2],
        "headers": {name: handler.headers.get(name) or "not set" for name in PROXY_HEADERS},
    }


# ---------------------------------------------------------------- handler ---

class Handler(BaseHTTPRequestHandler):
    server_version = "monitor-backend/1.0"
    protocol_version = "HTTP/1.1"          # required for upstream keepalive

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD" and body:
            self.wfile.write(body)

    def _events(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")   # ask Nginx not to buffer this stream
        self.end_headers()
        self.close_connection = True
        peer = self.client_address[0]
        print("[backend] peer=%s stream opened" % peer, flush=True)
        try:
            while True:
                payload = json.dumps({"metrics": METER.sample(), "request": request_info(self)})
                self.wfile.write(b"data: " + payload.encode("utf-8") + b"\n\n")
                self.wfile.flush()
                time.sleep(TICK)
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            print("[backend] peer=%s stream closed" % peer, flush=True)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/favicon.ico":
            self._send(204, b"")
        elif path == "/events":
            self._events()
        elif path == "/api/metrics":
            snapshot = {"metrics": METER.sample(), "request": request_info(self)}
            self._send(200, json.dumps(snapshot, indent=2), "application/json")
        elif path in ("/", "/index.html"):
            self._send(200, PAGE)
        else:
            self._send(404, "not found\n", "text/plain; charset=utf-8")

    def do_HEAD(self):
        self._send(200, PAGE)

    def log_message(self, fmt, *args):
        print("[backend] peer=%s %s" % (self.client_address[0], fmt % args), flush=True)


if __name__ == "__main__":
    server = ThreadingHTTPServer(LISTEN, Handler)
    server.daemon_threads = True
    print("listening on %s:%d" % LISTEN, flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
