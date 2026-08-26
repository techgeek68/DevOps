#!/usr/bin/env python3
import sys
from urllib.parse import parse_qs

SUBJECTS = ["English", "Nepali", "Mathematics", "Computer Science", "Applied Physics"]
PASS_MARK = 40

GRADE_SCALE = [
    (90, "A+", 4.0),
    (80, "A", 3.6),
    (70, "B+", 3.2),
    (60, "B", 2.8),
    (50, "C+", 2.4),
    (40, "C", 2.0),
    (35, "D", 1.6),
    (0, "NG", 0.0),
]

SCALE_BANDS = [
    "90 and above", "80 to 89", "70 to 79", "60 to 69",
    "50 to 59", "40 to 49", "35 to 39", "Below 35",
]


def grade_for(mark):
    for floor, letter, point in GRADE_SCALE:
        if mark >= floor:
            return letter, point
    return "NG", 0.0


def read_form(environ):
    try:
        length = int(environ.get('CONTENT_LENGTH', 0) or 0)
    except ValueError:
        length = 0
    body = environ['wsgi.input'].read(length) if length else b''
    return parse_qs(body.decode('utf-8', errors='replace'))


def build_sheet(form):
    symbol = (form.get('symbol', [''])[0] or '').strip()
    student = (form.get('student', [''])[0] or '').strip()
    errors = []
    subject_rows = []
    grade_points = []

    for subject in SUBJECTS:
        raw = form.get(subject, [''])[0].strip()
        if raw == '':
            errors.append(f"Marks for {subject} were not entered.")
            continue
        try:
            mark = float(raw)
        except ValueError:
            errors.append(f"Marks for {subject} must be a number.")
            continue
        if mark < 0 or mark > 100:
            errors.append(f"Marks for {subject} must fall between 0 and 100.")
            continue
        letter, point = grade_for(mark)
        grade_points.append(point)
        subject_rows.append((subject, mark, letter, point))

    gpa = round(sum(grade_points) / len(grade_points), 2) if grade_points else None
    failed_any = any(mark < PASS_MARK for _, mark, _, _ in subject_rows)
    overall = None
    if subject_rows and not errors:
        overall = "Failed" if failed_any else "Passed"

    return symbol, student, subject_rows, errors, gpa, overall


def render_rows(subject_rows):
    if not subject_rows:
        return '<tr><td colspan="4" class="empty">No subjects evaluated yet.</td></tr>'
    out = []
    for subject, mark, letter, point in subject_rows:
        status_class = "low" if mark < PASS_MARK else ""
        out.append(
            f'<tr class="{status_class}"><td>{subject}</td>'
            f'<td>{mark:.1f}</td><td>{letter}</td><td>{point:.1f}</td></tr>'
        )
    return "".join(out)


def render_errors(errors):
    if not errors:
        return ""
    items = "".join(f"<li>{e}</li>" for e in errors)
    return f'<div class="notice"><strong>Could not finalize the sheet.</strong><ul>{items}</ul></div>'


def render_form(subject_rows_lookup=None):
    subject_rows_lookup = subject_rows_lookup or {}
    fields = []
    for subject in SUBJECTS:
        existing = subject_rows_lookup.get(subject, "")
        field_id = subject.lower().replace(" ", "_")
        fields.append(
            f'<label for="{field_id}">{subject}</label>'
            f'<input type="text" id="{field_id}" name="{subject}" value="{existing}" '
            f'placeholder="0 to 100" autocomplete="off">'
        )
    return "".join(fields)


def render_scale_rail():
    rows = []
    for band, (_, letter, point) in zip(SCALE_BANDS, GRADE_SCALE):
        rows.append(
            f'<li><span class="band">{band}</span>'
            f'<span class="letter">{letter}</span>'
            f'<span class="point">{point:.1f}</span></li>'
        )
    return "".join(rows)


def application(environ, start_response):
    method = environ.get('REQUEST_METHOD', 'GET')
    form = read_form(environ) if method == 'POST' else {}

    symbol, student, subject_rows, errors, gpa, overall = build_sheet(form) if method == 'POST' else ('', '', [], [], None, None)
    lookup = {s: f"{m:.0f}" for s, m, _, _ in subject_rows}

    result_block = ""
    if method == 'POST':
        if errors:
            result_block = render_errors(errors)
        elif overall:
            stamp_class = "stamp-pass" if overall == "Passed" else "stamp-fail"
            result_block = f"""
            <div class="verdict {stamp_class}">
                <span class="verdict-label">{overall}</span>
                <span class="gpa">GPA {gpa:.2f}</span>
            </div>
            """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Examination Cell | Shree Himal Polytechnic Institute</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@500;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --blue: #2f6690;
    --blue-deep: #1c3f57;
    --sky: #87ceeb;
    --gold: #e0983f;
    --gold-soft: #f6cf9a;
    --sheet: #ffffff;
    --line: #bcdcec;
    --ink: #1f2d3a;
    --fail: #b23a2e;
    --pass: #1f7a4c;
    --rail-bg: #1c3f57;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ height: 100%; }}
  body {{
    margin: 0;
    font-family: 'IBM Plex Mono', monospace;
    color: var(--ink);
    background: var(--sky);
  }}
  .site-band {{
    background: linear-gradient(90deg, var(--blue) 0%, #3a7ba8 100%);
    border-bottom: 4px solid var(--gold);
  }}
  .site-band-inner {{
    max-width: 1240px;
    margin: 0 auto;
    padding: 22px 32px;
    display: flex;
    align-items: center;
    gap: 18px;
  }}
  .mark {{
    width: 52px;
    height: 52px;
    flex: none;
    border: 2px solid var(--gold);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Roboto Slab', serif;
    font-weight: 700;
    color: var(--gold-soft);
    letter-spacing: 0.02em;
  }}
  .titles h1 {{
    margin: 0;
    font-family: 'Roboto Slab', serif;
    font-size: 1.2rem;
    color: #ffffff;
  }}
  .titles p {{
    margin: 3px 0 0;
    font-size: 0.78rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--gold-soft);
  }}
  .session-tag {{
    margin-left: auto;
    font-size: 0.72rem;
    color: #eaf6fc;
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 999px;
    padding: 5px 14px;
    white-space: nowrap;
  }}
  .workspace {{
    max-width: 1240px;
    margin: 0 auto;
    padding: 34px 32px 70px;
    display: grid;
    grid-template-columns: 268px 1fr;
    gap: 30px;
    align-items: start;
  }}
  .rail {{
    background: var(--rail-bg);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 6px;
    padding: 22px 20px;
    position: sticky;
    top: 24px;
  }}
  .rail h2 {{
    margin: 0 0 12px;
    font-family: 'Roboto Slab', serif;
    font-size: 0.85rem;
    color: var(--gold-soft);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    border-bottom: 1px solid rgba(255, 255, 255, 0.22);
    padding-bottom: 8px;
  }}
  .rail-block + .rail-block {{
    margin-top: 24px;
  }}
  ul.scale-list {{
    list-style: none;
    margin: 0;
    padding: 0;
    font-size: 0.76rem;
  }}
  ul.scale-list li {{
    display: grid;
    grid-template-columns: 1fr 34px 34px;
    gap: 6px;
    padding: 5px 0;
    color: #e4f2f9;
    border-bottom: 1px dashed rgba(255,255,255,0.14);
  }}
  ul.scale-list .letter {{ color: var(--gold-soft); text-align: center; }}
  ul.scale-list .point {{ color: #9fc2d6; text-align: right; }}
  ul.notes-list {{
    margin: 0;
    padding: 0 0 0 16px;
    font-size: 0.78rem;
    color: #d5e9f3;
    line-height: 1.55;
  }}
  .sheet {{
    width: 100%;
    background: var(--sheet);
    border: 1px solid var(--line);
    border-radius: 4px;
    position: relative;
    padding: 34px 40px 40px;
    box-shadow: 0 24px 50px -30px rgba(15, 55, 80, 0.35);
  }}
  .sheet::after {{
    content: "OFFICIAL COPY";
    position: absolute;
    top: 46%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-18deg);
    font-family: 'Roboto Slab', serif;
    font-size: 3.6rem;
    font-weight: 700;
    color: rgba(47, 102, 144, 0.05);
    pointer-events: none;
    white-space: nowrap;
  }}
  .crest {{
    text-align: center;
    border-bottom: 3px double var(--blue);
    padding-bottom: 14px;
    margin-bottom: 22px;
  }}
  .crest h1 {{
    font-family: 'Roboto Slab', serif;
    font-size: 1.15rem;
    margin: 0 0 4px;
    color: var(--blue);
  }}
  .crest p {{
    margin: 0;
    font-size: 0.75rem;
    letter-spacing: 0.14em;
    color: var(--gold);
    text-transform: uppercase;
  }}
  .identity {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 18px;
  }}
  .identity input {{
    width: 100%;
    padding: 7px 9px;
    border: 1px solid var(--line);
    background: #fff;
    font-family: inherit;
    font-size: 0.85rem;
  }}
  .identity label {{
    display: block;
    font-size: 0.68rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--blue);
    margin-bottom: 3px;
  }}
  .marks-grid {{
    display: grid;
    grid-template-columns: 1fr 100px 1fr 100px;
    row-gap: 10px;
    column-gap: 16px;
    align-items: center;
    margin-bottom: 22px;
  }}
  @media (max-width: 760px) {{
    .workspace {{ grid-template-columns: 1fr; }}
    .rail {{ position: static; }}
    .marks-grid {{ grid-template-columns: 1fr 100px; }}
  }}
  .marks-grid label {{
    font-size: 0.82rem;
  }}
  .marks-grid input {{
    padding: 6px 8px;
    border: 1px solid var(--line);
    background: #fff;
    font-family: inherit;
    text-align: right;
  }}
  button.submit {{
    width: 100%;
    padding: 11px;
    background: var(--blue);
    color: var(--gold-soft);
    border: none;
    font-family: 'Roboto Slab', serif;
    font-weight: 700;
    font-size: 0.9rem;
    letter-spacing: 0.06em;
    cursor: pointer;
  }}
  button.submit:hover {{ background: var(--blue-deep); }}
  table.marksheet {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 22px;
    font-size: 0.82rem;
  }}
  table.marksheet th {{
    background: var(--blue);
    color: #ffffff;
    text-align: left;
    padding: 7px 8px;
  }}
  table.marksheet td {{
    padding: 7px 8px;
    border-top: 1px solid var(--line);
  }}
  table.marksheet tr.low td {{
    color: var(--fail);
    font-weight: 600;
  }}
  table.marksheet .empty {{
    text-align: center;
    color: #7d94a3;
    font-style: italic;
  }}
  .notice {{
    margin-top: 18px;
    padding: 12px 14px;
    border: 1px solid var(--fail);
    background: #fbeceb;
    font-size: 0.8rem;
  }}
  .notice ul {{ margin: 6px 0 0 18px; padding: 0; }}
  .verdict {{
    margin-top: 20px;
    padding: 14px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 2px solid;
  }}
  .stamp-pass {{ border-color: var(--pass); color: var(--pass); }}
  .stamp-fail {{ border-color: var(--fail); color: var(--fail); }}
  .verdict-label {{
    font-family: 'Roboto Slab', serif;
    font-weight: 700;
    font-size: 1.1rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }}
  .gpa {{ font-size: 0.9rem; }}
  .site-foot {{
    border-top: 1px solid rgba(255, 255, 255, 0.4);
    padding: 16px 32px 22px;
    max-width: 1240px;
    margin: 0 auto;
    font-size: 0.72rem;
    color: #2c5773;
    text-align: right;
  }}
</style>
</head>
<body>
  <header class="site-band">
    <div class="site-band-inner">
      <div class="mark">SH</div>
      <div class="titles">
        <h1>Shree Himal Polytechnic Institute</h1>
        <p>Examination Cell &middot; First Terminal Examination</p>
      </div>
      <div class="session-tag">Kaski, Nepal &middot; Session 2082</div>
    </div>
  </header>

  <div class="workspace">
    <aside class="rail">
      <div class="rail-block">
        <h2>Grading Scale</h2>
        <ul class="scale-list">
          {render_scale_rail()}
        </ul>
      </div>
      <div class="rail-block">
        <h2>Before You Submit</h2>
        <ul class="notes-list">
          <li>Symbol number is mandatory for every sheet.</li>
          <li>Marks below 40 in any subject fail that subject.</li>
          <li>GPA is the mean of the five grade points.</li>
          <li>A sheet with any blank or invalid mark cannot be finalized.</li>
        </ul>
      </div>
    </aside>

    <section class="sheet">
      <div class="crest">
        <h1>Mark Sheet</h1>
        <p>To be filled by the subject examiner</p>
      </div>

      <form method="POST">
        <div class="identity">
          <div>
            <label for="symbol">Symbol Number</label>
            <input type="text" id="symbol" name="symbol" value="{symbol}" autocomplete="off">
          </div>
          <div>
            <label for="student">Student Name</label>
            <input type="text" id="student" name="student" value="{student}" autocomplete="off">
          </div>
        </div>

        <div class="marks-grid">
          {render_form(lookup)}
        </div>

        <button type="submit" class="submit">Finalize Mark Sheet</button>
      </form>

      {result_block}

      <table class="marksheet">
        <thead>
          <tr><th>Subject</th><th>Marks</th><th>Grade</th><th>Grade Point</th></tr>
        </thead>
        <tbody>
          {render_rows(subject_rows)}
        </tbody>
      </table>
    </section>
  </div>

  <footer class="site-foot">Served by Python {sys.version.split()[0]} under mod_wsgi daemon mode</footer>
</body>
</html>"""

    status = '200 OK'
    headers = [('Content-Type', 'text/html; charset=utf-8')]
    start_response(status, headers)
    return [html.encode('utf-8')]
