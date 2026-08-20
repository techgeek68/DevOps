#!/usr/bin/env python3
import sys

def application(environ, start_response):
    """A minimal WSGI application."""
    status = '200 OK'
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    start_response(status, headers)

    rows = [
        ("Python version", sys.version.split()[0]),
        ("Server software", environ.get('SERVER_SOFTWARE', 'unknown')),
        ("Client address", environ.get('REMOTE_ADDR', 'unknown')),
        ("Request method", environ.get('REQUEST_METHOD', 'unknown')),
        ("Script name", environ.get('SCRIPT_NAME', '/')),
    ]
    rows_html = "".join(
        f'<div class="row"><span class="key">{k}</span><span class="val">{v}</span></div>'
        for k, v in rows
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>WSGI Daemon</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #e9ece6;
    --panel: #ffffff;
    --ink: #232a26;
    --muted: #6b7a70;
    --rule: #d6ddd0;
    --pine: #3f6b52;
    --pine-soft: #e3ece5;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    min-height: 100vh;
    padding: 48px 20px;
    background: var(--bg);
    color: var(--ink);
    font-family: 'Inter', sans-serif;
    display: flex;
    justify-content: center;
  }}
  .panel {{
    width: 100%;
    max-width: 460px;
    background: var(--panel);
    border: 1px solid var(--rule);
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 14px 34px -24px rgba(35, 42, 38, 0.5);
  }}
  .bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    background: var(--pine-soft);
    border-bottom: 1px solid var(--rule);
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--pine);
    letter-spacing: 0.02em;
  }}
  .bar .dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--pine);
    display: inline-block;
    margin-right: 6px;
  }}
  .body {{
    padding: 24px 24px 26px;
  }}
  h1 {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.2rem;
    font-weight: 600;
    margin: 0 0 6px;
  }}
  .lead {{
    color: var(--muted);
    font-size: 0.92rem;
    margin: 0 0 20px;
  }}
  .row {{
    display: flex;
    justify-content: space-between;
    gap: 12px;
    padding: 10px 0;
    border-top: 1px solid var(--rule);
    font-size: 0.88rem;
  }}
  .row:first-of-type {{ border-top: none; }}
  .key {{
    color: var(--muted);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
  }}
  .val {{
    font-weight: 500;
    text-align: right;
    word-break: break-word;
  }}
</style>
</head>
<body>
  <div class="panel">
    <div class="bar"><span><span class="dot"></span>wsgi.application</span><span>daemon mode</span></div>
    <div class="body">
      <h1>Application running</h1>
      <p class="lead">Deployed behind Apache using mod_wsgi in daemon mode.</p>
      {rows_html}
    </div>
  </div>
</body>
</html>"""
    return [html.encode('utf-8')]
