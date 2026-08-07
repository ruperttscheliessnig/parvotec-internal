#!/usr/bin/env python3
"""Parvotec Workstation Spec — YAML → HTML (Simplified)"""
import yaml
from pathlib import Path

CSS = """
      :root {
        --paper: #050505;
        --card:  #090909;
        --ink:   #f5f5f2;
        --soft:  #a7abb0;
        --line:  #343434;
        --accent: #f59e0b;
        --good:  #34d399;
      }
      *{margin:0;padding:0;box-sizing:border-box;}
      html{scroll-behavior:smooth;}
      body{font-family:'Helvetica Neue','Helvetica','Arial',sans-serif;background:var(--paper);color:var(--ink);line-height:1.62;font-size:16px;}
      header{background:var(--paper);padding:76px max(4vw,calc((100vw - 1240px)/2)) 54px;border-bottom:1px solid var(--line);}
      header h1{font-size:clamp(2.4rem,5vw,4.8rem);font-weight:400;letter-spacing:-0.06em;color:var(--ink);margin-bottom:8px;}
      header p{font-size:.88rem;color:var(--soft);letter-spacing:.08em;margin-top:12px;}
      nav{position:sticky;top:0;z-index:100;background:rgba(5,5,5,.96);backdrop-filter:blur(10px);border-bottom:1px solid var(--line);display:flex;gap:28px;padding:0 max(4vw,calc((100vw - 1240px)/2));min-height:56px;}
      nav a{color:var(--soft);text-decoration:none;font-size:.8rem;font-weight:500;letter-spacing:.06em;text-transform:uppercase;padding:18px 0;border-bottom:2px solid transparent;transition:color .2s,border-color .2s;}
      nav a:hover,nav a.active{color:var(--ink);border-bottom-color:var(--accent);}
      nav a.back{margin-left:auto;color:var(--accent);}
      .content{width:min(1240px,94vw);margin:0 auto;border-left:1px solid var(--line);border-right:1px solid var(--line);}
      section{padding:72px 48px;border-bottom:1px solid var(--line);scroll-margin-top:56px;}
      h2{font-size:clamp(1.8rem,3.5vw,3rem);font-weight:400;letter-spacing:-.05em;color:var(--ink);margin-bottom:28px;line-height:1.1;}
      h3{font-size:1.3rem;font-weight:500;color:var(--ink);margin-top:36px;margin-bottom:14px;}
      h4{margin:18px 0 8px;font-size:.8rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);}
      p{font-size:1rem;margin-bottom:16px;max-width:78ch;line-height:1.65;}
      strong{font-weight:600;color:var(--ink);}
      code{font-family:monospace;font-size:.85em;background:var(--card);border:1px solid var(--line);padding:2px 6px;color:var(--accent);}
      a{color:var(--accent);text-decoration:none;}
      a:hover{opacity:.8;}
      .spec-table{width:100%;border-collapse:collapse;margin:20px 0;font-size:.9rem;}
      .spec-table th{background:var(--card);color:var(--accent);padding:12px 16px;text-align:left;border-bottom:1px solid var(--line);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;font-weight:600;}
      .spec-table td{padding:14px 16px;border-bottom:1px solid var(--line);color:var(--ink);vertical-align:top;}
      .spec-table tr:hover{background:var(--card);}
      .spec-table td:first-child{font-weight:600;color:var(--accent);}
      .tier{background:var(--card);border:1px solid var(--line);padding:18px 20px;border-left:2px solid var(--accent);margin:12px 0;}
      .tier strong{color:var(--accent);display:block;margin-bottom:6px;}
      .tier p{margin:6px 0;font-size:.9rem;}
      ul,ol{margin-left:24px;margin-bottom:16px;}
      li{margin-bottom:8px;line-height:1.6;}
      .deployment-option{background:var(--card);border:1px solid var(--line);padding:20px;margin:12px 0;}
      footer{padding:48px max(4vw,calc((100vw - 1240px)/2));border-top:1px solid var(--line);color:var(--soft);font-size:.75rem;}
      @media(max-width:500px){section{padding:48px 20px;}.spec-table{font-size:.8rem;}}
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

def generate_workstation_spec(data):
    m = data['meta']
    nav_links = ''.join(f'<a href="{l["href"]}">{l["label"]}</a>' for l in m['nav_links'])
    
    # Build sections from data
    sections_html = ''
    for section in data['sections']:
        sec_id = section['id']
        title = section['title']
        content = section['content']
        sections_html += f'<section id="{sec_id}"><h2>{title}</h2>{content}</section>'
    
    html = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Parvotec | {m["title"]}</title>
    <style>{CSS}</style>
</head>
<body>
<header>
    <div style="margin-bottom:14px;">
        <span style="font-size:2em;font-weight:700;">calyr.aí</span>
        <span style="font-size:.72em;color:var(--accent);font-weight:600;margin-left:8px;vertical-align:super;">INFRASTRUCTURE</span>
    </div>
    <h1>{m["title"]}</h1>
    <p style="color:var(--soft);font-size:.95rem;margin-top:8px;">{m["subtitle"]}</p>
    <p style="color:var(--soft);font-size:.85rem;margin-top:6px;">{m["description"]}</p>
</header>
<nav>
    {nav_links}
    <a href="{m["back_href"]}" class="back">{m["back_label"]}</a>
</nav>
<div class="content">
{sections_html}
</div>
<footer>
    <p><strong>Parvotec Workstation Specification</strong></p>
    <p>Generated from data/workstation.yml · calyr.aí Research · August 2026</p>
</footer>
<script>{JS}</script>
</body>
</html>'''
    return html

if __name__ == '__main__':
    base = Path(__file__).parent
    yml = base / 'data' / 'workstation.yml'
    with open(yml) as f:
        data = yaml.safe_load(f)
    out = base / data['meta']['output']
    out.parent.mkdir(parents=True, exist_ok=True)
    html = generate_workstation_spec(data)
    out.write_text(html)
    print(f"✓ {out.relative_to(base)}")
