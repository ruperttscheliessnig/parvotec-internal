"""
Rebuild all paper slide viewers as click-through presenters.
Same layout as talk viewers: slide image (left) + key text (right), arrow nav.
"""
import json
import re
from pathlib import Path

SLIDES_BASE = Path.home() / "workspace-active/parvotec/Machine learning for Rupert/transcripts/slides"
CSS_REL = "../../css/main.css"


def parse_slide_viewer(idx: Path):
    """Extract slide data from existing index.html."""
    html = idx.read_text(encoding="utf-8")
    slides = []
    # Match each .slide block: image src + text content
    blocks = re.findall(
        r'<div class="slide(?:-left)?"[^>]*>.*?<img[^>]+src="([^"]+)".*?'
        r'<div class="slide-(?:right|text)[^"]*"[^>]*>(.*?)</div>\s*</div>',
        html, re.DOTALL
    )
    if not blocks:
        # Fallback: simpler pattern
        imgs  = re.findall(r'<img[^>]+src="(img/s\d+\.png)"', html)
        texts = re.findall(r'<div class="slide-(?:right|text)[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
        blocks = list(zip(imgs, texts))

    for i, (img, raw_text) in enumerate(blocks, 1):
        text = re.sub(r'<[^>]+>', ' ', raw_text).strip()
        text = re.sub(r'\s+', ' ', text)
        slides.append({"n": i, "img": img, "text": text})
    return slides


def get_title(idx: Path) -> str:
    html = idx.read_text(encoding="utf-8")
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    return idx.parent.name.replace('_', ' ')


def build_presenter(folder: Path, slides: list[dict], title: str) -> str:
    total = len(slides)
    color = "#39bfff"
    slides_json = json.dumps(slides, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — calyr.aí</title>
<link rel="stylesheet" href="{CSS_REL}" />
<style>
:root {{ --c: {color}; }}
body {{ display:flex; flex-direction:column; height:100dvh; overflow:hidden; }}
.pres-nav {{
  padding:.75rem max(4vw,calc((100vw - 1240px)/2));
  border-bottom:1px solid var(--line);
  display:flex; align-items:center; gap:1.5rem; flex-shrink:0;
}}
.pres-nav h1 {{ font-size:.8rem; font-weight:400; letter-spacing:.04em; color:var(--soft); flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.pres-counter {{ font-size:.65rem; font-family:monospace; color:var(--c); white-space:nowrap; }}
.pres-btn {{ background:none; border:1px solid var(--line); color:var(--ink); padding:.3rem .8rem; font-family:inherit; font-size:.7rem; letter-spacing:.08em; text-transform:uppercase; cursor:pointer; }}
.pres-btn:hover {{ background:var(--ink); color:var(--paper); }}
.pres-btn:disabled {{ opacity:.25; cursor:default; }}
.slide-view {{ flex:1; display:grid; grid-template-columns:1fr 1fr; gap:0; overflow:hidden; }}
.slide-img-col {{
  border-right:1px solid var(--line); display:flex; align-items:center;
  justify-content:center; padding:0; background:var(--card);
  overflow:hidden; position:relative; cursor:grab;
}}
.slide-img-col.dragging {{ cursor:grabbing; }}
.slide-img-col img {{ width:100%; max-height:100%; object-fit:contain; transform-origin:center center; user-select:none; pointer-events:none; will-change:transform; }}
.slide-img-col .no-img {{ font-size:.65rem; color:var(--soft); letter-spacing:.08em; text-transform:uppercase; }}
.zoom-bar {{ position:absolute; bottom:.5rem; right:.5rem; display:flex; gap:.3rem; z-index:10; }}
.zoom-btn {{ background:rgba(10,10,10,.85); border:1px solid var(--line); color:var(--ink); font-family:inherit; font-size:.65rem; letter-spacing:.06em; padding:.2rem .5rem; cursor:pointer; }}
.zoom-btn:hover {{ background:var(--ink); color:var(--paper); }}
.slide-text-col {{ display:flex; flex-direction:column; justify-content:center; padding:2.5rem 3rem; overflow:hidden; }}
.slide-num {{ font-size:.6rem; font-family:monospace; color:var(--c); margin-bottom:1.5rem; letter-spacing:.1em; }}
.slide-text {{
  font-family:Georgia,'Times New Roman',serif;
  font-size:clamp(.9rem,1.6vw,1.25rem);
  line-height:1.65; color:var(--ink);
  overflow-y:auto; max-height:80vh;
}}
.progress-bar {{ height:2px; background:var(--line); flex-shrink:0; }}
.progress-fill {{ height:100%; background:var(--c); transition:width .25s; }}
.pres-footer {{ padding:.6rem max(4vw,calc((100vw - 1240px)/2)); border-top:1px solid var(--line); display:flex; gap:2rem; flex-shrink:0; }}
.pres-footer a {{ font-size:.65rem; color:var(--soft); letter-spacing:.06em; }}
.pres-footer a:hover {{ color:var(--ink); }}
@media(max-width:900px) {{ .slide-view {{ grid-template-columns:1fr; }} .slide-img-col {{ border-right:none; border-bottom:1px solid var(--line); max-height:45vh; }} }}
</style>
</head>
<body>

<div class="pres-nav">
  <h1>{title}</h1>
  <span class="pres-counter" id="counter">01 / {total:02d}</span>
  <button class="pres-btn" id="prev" onclick="go(-1)" disabled>← Prev</button>
  <button class="pres-btn" id="next" onclick="go(1)">Next →</button>
</div>

<div class="progress-bar"><div class="progress-fill" id="prog" style="width:{100/total:.1f}%"></div></div>

<div class="slide-view">
  <div class="slide-img-col" id="imgcol">
    <img id="simg" src="" alt="" style="display:none;" />
    <div class="no-img" id="noimg">—</div>
    <div class="zoom-bar">
      <button class="zoom-btn" onclick="zoom(1.25)">＋</button>
      <button class="zoom-btn" onclick="zoom(0.8)">－</button>
      <button class="zoom-btn" onclick="resetZoom()">↺</button>
    </div>
  </div>
  <div class="slide-text-col">
    <div class="slide-num" id="snum"></div>
    <div class="slide-text" id="stext"></div>
  </div>
</div>

<div class="pres-footer">
  <a href="../../index.html">← Transcripts</a>
  <a href="/">← calyr.aí</a>
</div>

<script>
const DATA = {slides_json};
let cur = 0;
function render() {{
  const s = DATA[cur];
  document.getElementById('snum').textContent = `Slide ${{String(s.n).padStart(2,'0')}} / {total:02d}`;
  document.getElementById('stext').textContent = s.text || '—';
  document.getElementById('counter').textContent = String(cur+1).padStart(2,'0') + ' / {total:02d}';
  document.getElementById('prog').style.width = ((cur+1)/{total}*100).toFixed(1)+'%';
  document.getElementById('prev').disabled = cur === 0;
  document.getElementById('next').disabled = cur === DATA.length-1;
  const img = document.getElementById('simg');
  const noimg = document.getElementById('noimg');
  if (s.img) {{ img.src = s.img; img.style.display='block'; noimg.style.display='none'; resetZoom(); }}
  else {{ img.style.display='none'; noimg.style.display='block'; }}
}}
function go(d) {{ cur=Math.max(0,Math.min(DATA.length-1,cur+d)); render(); }}
document.addEventListener('keydown', e => {{
  if (e.key==='ArrowRight'||e.key===' ') go(1);
  if (e.key==='ArrowLeft') go(-1);
}});
render();

let sc=1,tx=0,ty=0,dragging=false,startX,startY;
const col=document.getElementById('imgcol');
function applyT(){{ document.getElementById('simg').style.transform=`scale(${{sc}}) translate(${{tx}}px,${{ty}}px)`; }}
function zoom(f){{ sc=Math.min(8,Math.max(1,sc*f)); if(sc===1){{tx=0;ty=0;}} applyT(); }}
function resetZoom(){{ sc=1;tx=0;ty=0;applyT(); }}
col.addEventListener('wheel',e=>{{ e.preventDefault(); zoom(e.deltaY<0?1.15:0.87); }},{{passive:false}});
col.addEventListener('mousedown',e=>{{ if(sc<=1)return; dragging=true; startX=e.clientX-tx; startY=e.clientY-ty; col.classList.add('dragging'); }});
window.addEventListener('mouseup',()=>{{ dragging=false; col.classList.remove('dragging'); }});
window.addEventListener('mousemove',e=>{{ if(!dragging)return; tx=e.clientX-startX; ty=e.clientY-startY; applyT(); }});
</script>
</body>
</html>"""


def run():
    for folder in sorted(SLIDES_BASE.iterdir()):
        idx = folder / "index.html"
        if not idx.exists():
            continue
        slides = parse_slide_viewer(idx)
        if not slides:
            print(f"  ✗ {folder.name} — no slides parsed")
            continue
        title = get_title(idx)
        html = build_presenter(folder, slides, title)
        idx.write_text(html, encoding="utf-8")
        print(f"  ✓ {folder.name[:55]} — {len(slides)} slides")
    print("Done.")


if __name__ == "__main__":
    run()
