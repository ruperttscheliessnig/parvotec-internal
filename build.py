#!/usr/bin/env python3
"""
Parvotec Build System — YAML + MD → HTML
Usage: python3 build.py [--all | --drg | --aorta]
"""
import yaml, sys, re, textwrap
from pathlib import Path

# ── Design tokens (shared across all generated files) ────────────────────────
CSS = """
      :root {
        --paper: #050505;
        --card:  #090909;
        --ink:   #f5f5f2;
        --soft:  #a7abb0;
        --line:  #343434;
        --accent:%(accent)s;
        --ms:    #fbbf24;
      }
      *{margin:0;padding:0;box-sizing:border-box;}
      html{scroll-behavior:smooth;}
      body{font-family:'Helvetica Neue','Helvetica','Arial',sans-serif;background:var(--paper);color:var(--ink);line-height:1.62;font-size:16px;}
      header{background:var(--paper);padding:76px max(4vw,calc((100vw - 1240px)/2)) 54px;border-bottom:1px solid var(--line);}
      header h1{font-size:clamp(2.4rem,5vw,4.8rem);font-weight:400;letter-spacing:-0.06em;color:var(--ink);margin-bottom:8px;}
      header p{font-size:.88rem;color:var(--soft);letter-spacing:.08em;margin-top:12px;}
      nav{position:sticky;top:0;z-index:100;background:rgba(5,5,5,.96);backdrop-filter:blur(10px);border-bottom:1px solid var(--line);display:flex;align-items:center;flex-wrap:wrap;gap:28px;padding:0 max(4vw,calc((100vw - 1240px)/2));min-height:56px;}
      nav a{color:var(--soft);text-decoration:none;font-size:.8rem;font-weight:500;letter-spacing:.06em;text-transform:uppercase;padding:18px 0;border-bottom:2px solid transparent;transition:color .2s,border-color .2s;}
      nav a:hover,nav a.active{color:var(--ink);border-bottom-color:var(--accent);}
      nav a.back{color:var(--accent);margin-left:auto;}
      .content{width:min(1240px,94vw);margin:0 auto;border-left:1px solid var(--line);border-right:1px solid var(--line);}
      section{padding:72px 48px;border-bottom:1px solid var(--line);scroll-margin-top:56px;}
      section:last-child{border-bottom:none;}
      h2{font-size:clamp(1.8rem,3.5vw,3rem);font-weight:400;letter-spacing:-.05em;color:var(--ink);margin-bottom:28px;line-height:1.1;}
      h3{font-size:1.3rem;font-weight:500;color:var(--ink);margin-top:36px;margin-bottom:14px;letter-spacing:-.01em;}
      h4{margin-top:24px;margin-bottom:10px;letter-spacing:.05em;text-transform:uppercase;font-size:.78rem;font-weight:600;color:var(--accent);}
      p{font-size:1rem;color:var(--ink);margin-bottom:18px;line-height:1.65;max-width:78ch;}
      ul,ol{margin-left:28px;margin-bottom:18px;color:var(--ink);}
      li{margin-bottom:10px;line-height:1.62;}
      strong{color:var(--ink);font-weight:600;}
      code{font-family:'Menlo','Monaco','Courier New',monospace;font-size:.85em;background:var(--card);border:1px solid var(--line);padding:2px 6px;color:var(--accent);}
      a{color:var(--accent);text-decoration:none;}
      a:hover{opacity:.8;}
      .wp-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:1px;margin-top:28px;}
      .wp-card{background:var(--card);border:1px solid var(--line);padding:28px 32px;position:relative;overflow:hidden;}
      .wp-card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:%(accent)s;}
      .wp-tag{font-size:.68rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;margin-bottom:10px;display:block;color:%(accent)s;}
      .wp-card h3{margin-top:0;font-size:1.1rem;}
      .wp-meta{display:flex;gap:20px;margin-top:16px;font-size:.75rem;color:var(--soft);flex-wrap:wrap;}
      .wp-meta span{display:flex;flex-direction:column;gap:2px;}
      .wp-meta strong{color:var(--ink);font-size:.82rem;}
      .deliverables{margin-top:14px;padding-top:14px;border-top:1px solid var(--line);font-size:.82rem;color:var(--soft);}
      .deliverables strong{color:var(--ink);}
      .g-wrap{overflow-x:auto;margin-top:28px;}
      .g-chart{min-width:760px;border:1px solid var(--line);}
      .g-head{display:grid;grid-template-columns:160px 1fr;border-bottom:2px solid var(--line);}
      .g-head-label{background:var(--card);border-right:1px solid var(--line);padding:8px 14px;font-size:.62rem;color:var(--soft);letter-spacing:.1em;text-transform:uppercase;display:flex;align-items:flex-end;}
      .g-head-track{position:relative;background:var(--card);height:44px;}
      .g-tick{position:absolute;top:0;bottom:0;border-left:1px solid #1e1e1e;display:flex;flex-direction:column;justify-content:flex-end;padding-bottom:6px;padding-left:4px;font-size:.6rem;color:#555;letter-spacing:.04em;}
      .g-tick.q{border-left:1px solid var(--line);color:var(--soft);}
      .g-tick.q span{color:var(--accent);font-weight:700;font-size:.7rem;}
      .g-row{display:grid;grid-template-columns:160px 1fr;border-bottom:1px solid var(--line);min-height:52px;}
      .g-row:last-child{border-bottom:none;}
      .g-rlabel{background:var(--card);border-right:1px solid var(--line);padding:0 14px;display:flex;flex-direction:column;justify-content:center;gap:2px;}
      .g-rlabel strong{font-size:.8rem;color:var(--ink);font-weight:600;}
      .g-rlabel span{font-size:.64rem;color:var(--soft);}
      .g-track{position:relative;background:var(--paper);}
      .g-track::before{content:'';position:absolute;inset:0;background:repeating-linear-gradient(to right,transparent 0,transparent calc(12.5% - 1px),#1c1c1c calc(12.5% - 1px),#1c1c1c 12.5%);pointer-events:none;}
      .g-bar{position:absolute;top:50%;transform:translateY(-50%);height:20px;border-radius:0;display:flex;align-items:center;padding:0 8px;font-size:.62rem;font-weight:700;color:rgba(0,0,0,.75);letter-spacing:.05em;white-space:nowrap;overflow:hidden;}
      .g-ms{position:absolute;top:50%;transform:translate(-50%,-50%) rotate(45deg);width:10px;height:10px;background:var(--ms);z-index:4;box-shadow:0 0 0 2px var(--paper);}
      .g-ms-lbl{position:absolute;top:2px;transform:translateX(-50%);font-size:.58rem;color:var(--ms);white-space:nowrap;font-weight:700;letter-spacing:.04em;z-index:5;}
      .g-legend{display:flex;flex-wrap:wrap;gap:20px;margin-top:20px;font-size:.78rem;}
      .g-leg{display:flex;align-items:center;gap:8px;}
      .g-dot{width:20px;height:10px;border-radius:0;flex-shrink:0;}
      .g-diamond{width:9px;height:9px;transform:rotate(45deg);background:var(--ms);flex-shrink:0;}
      .arch-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;border:1px solid var(--line);margin:24px 0;}
      .arch-block{background:var(--card);padding:20px 18px;border-right:1px solid var(--line);position:relative;}
      .arch-block:last-child{border-right:none;}
      .arch-arrow{position:absolute;right:-12px;top:50%;transform:translateY(-50%);font-size:1rem;color:var(--accent);z-index:2;}
      .arch-num{font-size:.65rem;color:var(--accent);font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:6px;}
      .arch-block h4{font-size:.82rem;color:var(--ink);font-weight:600;margin:0 0 6px;text-transform:none;letter-spacing:0;}
      .arch-block p{font-size:.76rem;color:var(--soft);margin:0;max-width:none;}
      .spec-table{width:100%;border-collapse:collapse;margin:20px 0;font-size:.9rem;}
      .spec-table th{background:var(--card);color:var(--accent);padding:12px 16px;text-align:left;border-bottom:1px solid var(--line);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;font-weight:600;}
      .spec-table td{padding:12px 16px;border-bottom:1px solid var(--line);color:var(--ink);}
      .spec-table tr:hover{background:var(--card);}
      .callout{border-left:2px solid var(--accent);padding:16px 20px;margin:20px 0;background:var(--card);}
      .callout p{margin:0;font-size:.9rem;}
      footer{color:var(--soft);padding:48px max(4vw,calc((100vw - 1240px)/2));font-size:.75rem;letter-spacing:.08em;border-top:1px solid var(--line);}
      footer p{font-size:.75rem;margin:6px 0;color:var(--soft);}
      @media(max-width:500px){section{padding:48px 20px;}.wp-cards{grid-template-columns:1fr;}.arch-grid{grid-template-columns:1fr 1fr;}.arch-arrow{display:none;}}
"""

JS = """
    const sections = document.querySelectorAll('section[id]');
    const navLinks  = document.querySelectorAll('nav a:not(.back)');
    window.addEventListener('scroll', () => {
        let cur = '';
        sections.forEach(s => { if (window.scrollY >= s.offsetTop - 70) cur = s.id; });
        navLinks.forEach(a => { a.classList.remove('active'); if (a.getAttribute('href') === '#' + cur) a.classList.add('active'); });
    }, { passive: true });
"""

# ── Helper: markdown-lite bold + newlines ────────────────────────────────────
def md(text: str) -> str:
    """Convert **bold** and newlines to HTML."""
    t = str(text).strip()
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = t.replace('\n', '<br>')
    return t

def li_list(items: list) -> str:
    return '<ul>' + ''.join(f'<li>{md(i)}</li>' for i in items) + '</ul>'

def params_table(params: dict) -> str:
    rows = ''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k, v in params.items())
    return f'<table class="spec-table"><thead><tr><th>Parameter</th><th>Wert</th></tr></thead><tbody>{rows}</tbody></table>'

# ── Section builders ──────────────────────────────────────────────────────────
def build_gantt_ticks() -> str:
    ticks = [
        ('q', '0%',     'Q1'), ('', '4.17%', 'M2'), ('', '8.33%', 'M3'),
        ('q', '12.5%',  'Q2'), ('', '16.67%','M5'), ('', '20.83%','M6'),
        ('q', '25%',    'Q3'), ('', '29.17%','M8'), ('', '33.33%','M9'),
        ('q', '37.5%',  'Q4'), ('', '41.67%','M11'),('', '45.83%','M12'),
        ('q', '50%',    'Q5'), ('', '54.17%','M14'),('', '58.33%','M15'),
        ('q', '62.5%',  'Q6'), ('', '66.67%','M17'),('', '70.83%','M18'),
        ('q', '75%',    'Q7'), ('', '79.17%','M20'),('', '83.33%','M21'),
        ('q', '87.5%',  'Q8'), ('', '91.67%','M23'),('', '95.83%','M24'),
    ]
    out = ''
    for cls, left, lbl in ticks:
        if cls == 'q':
            out += f'<div class="g-tick q" style="left:{left}"><span>{lbl}</span></div>'
        else:
            out += f'<div class="g-tick" style="left:{left}">{lbl}</div>'
    return out

def build_wp_row(wp: dict, idx: int) -> str:
    color = wp['color']
    left  = wp['gantt_left']
    width = wp['gantt_width']
    lbl   = wp.get('gantt_label', f"WP{idx+1}")
    bar_text = f"{lbl} — {wp['title']}"
    milestones = ''.join(
        f'<div class="g-ms" style="left:{m["pct"]}%"></div>'
        f'<div class="g-ms-lbl" style="left:{m["pct"]}%">{m["label"]}</div>'
        for m in wp.get('milestones', [])
    )
    return f'''
        <div class="g-row">
          <div class="g-rlabel"><strong>WP{idx+1}</strong><span>{wp["title"]}</span></div>
          <div class="g-track">
            <div class="g-bar" style="background:{color};left:{left}%;width:{width}%">{bar_text}</div>
            {milestones}
          </div>
        </div>'''

def build_wp_card(wp: dict, idx: int) -> str:
    color = wp['color']
    tasks = li_list(wp['tasks'])
    return f'''
        <div class="wp-card">
            <span class="wp-tag" style="color:{color}">{wp["label"]}</span>
            <h3>{wp["title"]}</h3>
            <p>{md(wp["description"])}</p>
            <h4>Aufgaben</h4>
            {tasks}
            <div class="wp-meta">
                <span><strong>Ressourcen</strong>{wp["resources"]}</span>
                <span><strong>Budget (est.)</strong>{wp["budget"]}</span>
                <span><strong>Risiko</strong>{wp["risk"]}</span>
            </div>
            <div class="deliverables"><strong>Deliverables:</strong> {wp["deliverables"]}</div>
        </div>'''

def build_budget_row(wp: dict, idx: int, start: str, end: str) -> str:
    period = f'M{wp["gantt_left"]//4+1}–M{int((wp["gantt_left"]+wp["gantt_width"])//4+1)}'
    return f'<tr><td>WP{idx+1} — {wp["title"]}</td><td>{period}</td><td>{wp["budget"]}</td><td>{wp["deliverables"].split("·")[0].strip()}</td></tr>'

def build_milestone_rows(milestones: list) -> str:
    return ''.join(
        f'<tr><td>{m["month"]}</td><td>{m["milestone"]}</td><td>{m["deliverable"]}</td><td>{m["wp"]}</td></tr>'
        for m in milestones
    )

def build_risk_rows(risks: list) -> str:
    return ''.join(
        f'<tr><td>{r["risk"]}</td><td>{r["probability"]}</td><td>{r["impact"]}</td><td>{r["mitigation"]}</td></tr>'
        for r in risks
    )

def build_oracle_layers(layers: list) -> str:
    blocks = ''
    for i, layer in enumerate(layers):
        arrow = '<span class="arch-arrow">→</span>' if i < len(layers)-1 else ''
        desc_html = '<br>'.join(layer['desc'].strip().split('\n'))
        blocks += f'''
        <div class="arch-block">
            {arrow}
            <div class="arch-num">{layer["num"]}</div>
            <h4>{layer["title"]}</h4>
            <p>{desc_html}</p>
        </div>'''
    return f'<div class="arch-grid">{blocks}</div>'

def build_oracle_outputs(outputs: list) -> str:
    rows = ''.join(
        f'<tr><td><strong>{o["name"]}</strong></td><td><code>{o["range"]}</code></td>'
        f'<td>{int(o["weight"]*100)}%</td><td>{o["description"]}</td></tr>'
        for o in outputs
    )
    return f'''<table class="spec-table">
        <thead><tr><th>Output</th><th>Range</th><th>Loss Weight</th><th>Beschreibung</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>'''

# ── Main proposal generator ───────────────────────────────────────────────────
def generate_proposal(data: dict, base_dir: Path) -> str:
    m    = data['meta']
    acc  = m['accent']
    ex   = data['executive']
    wps  = data['work_packages']
    ora  = data['oracle']
    ms   = data.get('milestones_table', [])
    risk = data.get('risks', [])
    bud  = data.get('budget_total', {})

    nav_links = ''.join(f'<a href="{l["href"]}">{l["label"]}</a>' for l in m['nav_links'])
    wp_cards  = ''.join(build_wp_card(wp, i) for i, wp in enumerate(wps))
    gantt_rows = ''.join(build_wp_row(wp, i) for i, wp in enumerate(wps))
    gantt_legend = ''.join(
        f'<div class="g-leg"><div class="g-dot" style="background:{wp["color"]}"></div>WP{i+1} — {wp["title"]}</div>'
        for i, wp in enumerate(wps)
    )
    budget_rows = ''.join(
        f'<tr><td>WP{i+1} — {wp["title"]}</td><td>{wp["budget"]}</td></tr>'
        for i, wp in enumerate(wps)
    )
    callout_html = f'<div class="callout"><p>{md(ex["callout"])}</p></div>'
    headline_html = f'<p>{md(ex["headline"])}</p>'

    html = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Parvotec | {m["title"]}</title>
    <style>{CSS.replace("%(accent)s", acc)}</style>
</head>
<body>
<header>
    <div style="margin-bottom:14px;">
        <span style="font-size:2em;font-weight:700;">calyr.aí</span>
        <span style="font-size:.72em;color:{acc};font-weight:600;margin-left:8px;vertical-align:super;">RESEARCH</span>
    </div>
    <h1>{m["title"]}</h1>
    <h1 style="font-size:clamp(1.2rem,2.5vw,2rem);color:var(--soft);font-weight:400;letter-spacing:-.02em;margin-top:4px;">{m["subtitle"]}</h1>
    <p>{m["description"]}</p>
</header>
<nav>
    {nav_links}
    <a href="{m["back_href"]}" class="back">{m["back_label"]}</a>
</nav>
<div class="content">

<section id="executive">
    <h2>Executive Summary</h2>
    {headline_html}
    {callout_html}
    <h3>Projektzeitraum &amp; Umfang</h3>
    {params_table(ex["params"])}
</section>

<section id="workpackages">
    <h2>Work Packages</h2>
    <div class="wp-cards">{wp_cards}</div>
    <h3>Budget-Übersicht</h3>
    <table class="spec-table">
        <thead><tr><th>Work Package</th><th>Budget</th></tr></thead>
        <tbody>
        {budget_rows}
        <tr style="font-weight:600;border-top:2px solid var(--line)">
            <td><strong>Total — {bud.get("duration","24 Monate")} · {bud.get("ftes","6–8 FTE peak")}</strong></td>
            <td><strong>{bud.get("range","—")}</strong></td>
        </tr>
        </tbody>
    </table>
</section>

<section id="gantt">
    <h2>Gantt Chart — 24 Monate</h2>
    <div class="g-legend">
        {gantt_legend}
        <div class="g-leg"><div class="g-diamond"></div>Meilenstein</div>
    </div>
    <div class="g-wrap"><div class="g-chart">
        <div class="g-head">
            <div class="g-head-label">Work Package</div>
            <div class="g-head-track">{build_gantt_ticks()}</div>
        </div>
        {gantt_rows}
    </div></div>
</section>

<section id="oracle-arch">
    <h2>{ora["type"]} — Systemarchitektur</h2>
    {build_oracle_layers(ora["layers"])}
    <h3>Oracle Outputs</h3>
    {build_oracle_outputs(ora["outputs"])}
</section>

<section id="oracle-data">
    <h2>{ora["type"]} — Datenpipeline</h2>
    <p>Das Oracle wird auf experimentellen DMS-Daten trainiert. Jede Variante erhält Labels für alle Outputs. Fehlende Labels (z.B. SAXS nur für Top-100) werden als NaN geführt — der Task-specific Loss maskiert NaN-Werte automatisch.</p>
    <div class="callout"><p><strong>Composite Score:</strong> Gewichteter Score aller Outputs gemäß Loss-Weighting. Ranking aller Kandidaten vor BO-Selektion.</p></div>
</section>

<section id="oracle-model">
    <h2>{ora["type"]} — Modell</h2>
    <div class="callout"><p><strong>Architektur:</strong> ESM-2 650M → 1280-dim Embedding → Feed-Forward NN (1280→512→256→128, ReLU, Dropout=0.15) → Task-spezifische Heads → Multi-task MSE Loss. Training: AdamW, CosineAnnealing, Early Stopping (patience=15).</p></div>
</section>

<section id="oracle-run">
    <h2>{ora["type"]} — Betrieb &amp; API</h2>
    <p>Jede Optimierungsrunde folgt einem fixierten 5-Schritt Protokoll: (1) cVAE Kandidaten-Generierung mit Constraint-Filter, (2) BO-Selektion via EHVI, (3) Experimentelle Validierung (28d), (4) Data Integration, (5) Oracle Re-Training auf kumulativen Daten.</p>
    <div class="callout"><p><strong>API:</strong> <code>oracle.predict(sequence)</code> · <code>oracle.generate(targets, n, strategy)</code> · <code>oracle.pareto_front(objectives)</code></p></div>
</section>

<section id="milestones">
    <h2>Meilensteine &amp; Deliverables</h2>
    <table class="spec-table">
        <thead><tr><th>Monat</th><th>Meilenstein</th><th>Deliverable</th><th>WP</th></tr></thead>
        <tbody>{build_milestone_rows(ms)}</tbody>
    </table>
    <h3>Risiko-Register</h3>
    <table class="spec-table">
        <thead><tr><th>Risiko</th><th>Wahrscheinlichkeit</th><th>Impact</th><th>Mitigation</th></tr></thead>
        <tbody>{build_risk_rows(risk)}</tbody>
    </table>
</section>

</div>
<footer>
    <p><strong>Parvotec — {m["title"]}</strong></p>
    <p>Generated by build.py from data/{Path(m["output"]).stem.replace("parvotec_","").replace("_proposal","")}.yml · calyr.aí Research · August 2026</p>
</footer>
<script>{JS}</script>
</body>
</html>'''
    return html

# ── Entry point ───────────────────────────────────────────────────────────────
def build(source: str, base_dir: Path):
    yml_path = base_dir / 'data' / f'{source}.yml'
    if not yml_path.exists():
        print(f"  ✗ {yml_path} not found"); return
    with open(yml_path) as f:
        data = yaml.safe_load(f)
    out_path = base_dir / data['meta']['output']
    out_path.parent.mkdir(parents=True, exist_ok=True)
    html = generate_proposal(data, base_dir)
    out_path.write_text(html, encoding='utf-8')
    print(f"  ✓ {out_path.relative_to(base_dir)}  ({len(html)//1024}KB)")

if __name__ == '__main__':
    base = Path(__file__).parent
    targets = sys.argv[1:] or ['--all']
    sources = ['drg', 'aorta'] if '--all' in targets else [t.lstrip('-') for t in targets]
    print(f"Building {sources}...")
    for s in sources:
        build(s, base)
    print("Done.")
