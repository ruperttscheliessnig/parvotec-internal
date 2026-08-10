"""
Build unified slide+transcript viewer for each ASGCT 2026 talk.
Generates one self-contained HTML per talk with:
  - Scrollable segments (90s windows)
  - Highlighted key sentence per segment
  - VTT text for that segment
  - Reference: link to related paper slide deck
"""
import re
from pathlib import Path

BASE      = Path.home() / "workspace-active/parvotec/Machine learning for Rupert/transcripts"
VTT_DIR   = BASE / "vtt"
OUT_DIR   = BASE / "talks"
CSS_REL   = "../css/main.css"

TALKS = {
    "Lir_AAV_LLM": {
        "title": "Lir Therapeutics — Corsair PLM for AAV Capsid Design",
        "speaker": "Thomas Peacock (Lir Therapeutics)",
        "color": "#39bfff",
        "related_paper": "../slides/4_FINAL-Voyager-ASGCT-2023-Hoffman_05_16_23/index.html",
        "related_label": "Voyager ASGCT 2023 — Slides",
    },
    "AAV_Engineering_III": {
        "title": "AAV Engineering III — Capsid Engineering Session",
        "speaker": "ASGCT 2026",
        "color": "#39bfff",
        "related_paper": "../slides/Deep_diversification_of_an_AAV_capsid_protein_by_machine_lea/index.html",
        "related_label": "Deep Diversification AAV Capsid — Slides",
    },
    "AAV_Engineering_IV": {
        "title": "AAV Engineering IV — Capsid Engineering Session",
        "speaker": "ASGCT 2026",
        "color": "#39bfff",
        "related_paper": "../slides/Systematic_multi-trait_AAV_capsid_engineering_for_efficient_/index.html",
        "related_label": "Systematic Multi-trait AAV Engineering — Slides",
    },
    "AAV_Trafficking": {
        "title": "AAV Trafficking",
        "speaker": "ASGCT 2026",
        "color": "#39bfff",
        "related_paper": "../slides/Applying_machine_learning_to_predict_viral_assembly_for_aden/index.html",
        "related_label": "ML for AAV Assembly Prediction — Slides",
    },
    "ShapeTX_AAV5engineering": {
        "title": "ShapeTX — AAV5 Engineering",
        "speaker": "ASGCT 2026",
        "color": "#00d4ff",
        "related_paper": "../slides/Comprehensive_AAV_capsid_fitness_landscape_reveals_a_viral_g/index.html",
        "related_label": "AAV Fitness Landscape — Slides",
    },
    "TuningReceptorInteractions_Caltech": {
        "title": "Tuning Receptor Interactions (Caltech)",
        "speaker": "ASGCT 2026",
        "color": "#a78bfa",
        "related_paper": "../slides/Generative_AAV_capsid_diversification_by_latent_interpolatio/index.html",
        "related_label": "Generative AAV Capsid (Latent Interpolation) — Slides",
    },
}

KEYWORDS = {
    "language model","protein language","esm","esm-2","corsair","fine-tun",
    "bayesian","variational","autoencoder","latent","embedding","fitness",
    "directed evolution","surrogate","active learning","spearman",
    "transduction","tropism","tissue specificity","liver","heart",
    "capsid","serotype","aav2","aav9","aav5","variant","library",
    "msa","multiple sequence","training data","benchmark",
    "immune evasion","immunogenicity","potency","detargeting",
    "outperform","improve","significant","correlation","accuracy",
    "we found","we show","our model","our approach","key insight",
}

SKIP_STARTS = (
    "my name is", "our next speaker", "thank you", "good morning", "good afternoon",
    "i'm happy", "i would like", "let me", "so today",
)


def parse_vtt(path: Path) -> list[dict]:
    """Return list of {start_s, end_s, text} dicts from VTT."""
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r'\n\n+', text.strip())
    entries = []
    for block in blocks:
        lines = block.strip().splitlines()
        ts_line = next((l for l in lines if "-->" in l), None)
        if not ts_line:
            continue
        def to_s(t):
            parts = t.strip().replace(",", ".").split(":")
            try:
                if len(parts) == 3:
                    return int(parts[0])*3600 + int(parts[1])*60 + float(parts[2])
                return int(parts[0])*60 + float(parts[1])
            except Exception:
                return 0
        start, end = ts_line.split("-->")
        txt = " ".join(l for l in lines if "-->" not in l and not l.isdigit() and l != "WEBVTT")
        if txt.strip():
            entries.append({"s": to_s(start), "e": to_s(end), "t": txt.strip()})
    return entries


def group_segments(entries: list[dict], window: int = 90) -> list[dict]:
    """Group VTT entries into ~window-second segments."""
    if not entries:
        return []
    segments, current, boundary = [], [], entries[0]["s"] + window
    for e in entries:
        if e["s"] > boundary and current:
            segments.append(current)
            current = []
            boundary = e["s"] + window
        current.append(e)
    if current:
        segments.append(current)
    return segments


def key_sentence(seg: list[dict]) -> str:
    text = " ".join(e["t"] for e in seg)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    def score(s):
        sl = s.lower()
        if any(sl.startswith(skip) for skip in SKIP_STARTS):
            return -1
        return sum(1 for kw in KEYWORDS if kw in sl)
    ranked = sorted(sentences, key=score, reverse=True)
    best = next((s for s in ranked if score(s) > 0 and len(s) > 50), None)
    return best or (sentences[0] if sentences else "")


def fmt_time(s: float) -> str:
    m, sec = divmod(int(s), 60)
    return f"{m}:{sec:02d}"


def build_html(stem: str, meta: dict, segments: list[list[dict]]) -> str:
    color = meta["color"]

    # Build JSON data with frame paths
    import json
    import os
    frames_dir = Path.home() / f"workspace-active/parvotec/Machine learning for Rupert/transcripts/talks/frames/{stem}"
    frame_files = sorted(frames_dir.glob("*.jpg")) if frames_dir.exists() else []

    slides_data = []
    for i, seg in enumerate(segments, 1):
        t_start = fmt_time(seg[0]["s"])
        t_end   = fmt_time(seg[-1]["e"])
        full    = " ".join(e["t"] for e in seg)
        key     = key_sentence(seg)
        # Match frame by index (frame i corresponds to segment i)
        frame_path = f"frames/{stem}/f{i:04d}.jpg" if i <= len(frame_files) else ""
        slides_data.append({"n": i, "ts": f"{t_start}–{t_end}", "key": key, "full": full, "img": frame_path})

    slides_json = json.dumps(slides_data, ensure_ascii=False)
    total = len(segments)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{meta["title"]} — calyr.aí</title>
<link rel="stylesheet" href="{CSS_REL}" />
<style>
:root {{ --c: {color}; }}
body {{ display:flex; flex-direction:column; height:100dvh; overflow:hidden; }}
.pres-nav {{
  padding:.75rem max(4vw,calc((100vw - 1240px)/2));
  border-bottom:1px solid var(--line);
  display:flex; align-items:center; gap:1.5rem;
  flex-shrink:0;
}}
.pres-nav h1 {{ font-size:.8rem; font-weight:400; letter-spacing:.04em; color:var(--soft); flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.pres-counter {{ font-size:.65rem; font-family:monospace; color:var(--c); white-space:nowrap; }}
.pres-btn {{
  background:none; border:1px solid var(--line); color:var(--ink);
  padding:.3rem .8rem; font-family:inherit; font-size:.7rem;
  letter-spacing:.08em; text-transform:uppercase; cursor:pointer;
}}
.pres-btn:hover {{ background:var(--ink); color:var(--paper); }}
.pres-btn:disabled {{ opacity:.25; cursor:default; }}

.slide-view {{
  flex:1; display:grid; grid-template-columns:1fr 1fr; gap:0;
  overflow:hidden;
}}
.slide-img-col {{
  border-right:1px solid var(--line);
  display:flex; align-items:center; justify-content:center;
  padding:0; background:var(--card);
  overflow:hidden; position:relative; cursor:grab;
}}
.slide-img-col.dragging {{ cursor:grabbing; }}
.slide-img-col img {{
  width:100%; max-height:100%; object-fit:contain;
  border:1px solid var(--line);
  transform-origin:center center;
  user-select:none; pointer-events:none;
  will-change:transform;
}}
.zoom-bar {{
  position:absolute; bottom:.5rem; right:.5rem;
  display:flex; gap:.3rem; z-index:10;
}}
.zoom-btn {{
  background:rgba(10,10,10,.85); border:1px solid var(--line);
  color:var(--ink); font-family:inherit; font-size:.65rem;
  letter-spacing:.06em; padding:.2rem .5rem; cursor:pointer;
}}
.zoom-btn:hover {{ background:var(--ink); color:var(--paper); }}
.slide-img-col .no-img {{
  font-size:.65rem; color:var(--soft); letter-spacing:.08em;
  text-transform:uppercase; text-align:center;
}}
.slide-text-col {{
  display:flex; flex-direction:column;
  justify-content:center;
  padding:2.5rem 3rem;
  overflow:hidden;
}}
.slide-ts {{ font-size:.6rem; font-family:monospace; color:var(--c); margin-bottom:1.5rem; letter-spacing:.1em; }}
.slide-key {{
  font-family:Georgia,'Times New Roman',serif;
  font-size:clamp(1rem,2vw,1.5rem);
  line-height:1.6; color:var(--ink);
  border-left:4px solid var(--c); padding-left:1.25rem;
  margin-bottom:1.75rem;
}}
.slide-full {{
  font-size:.8rem; color:var(--soft); line-height:1.75;
  overflow-y:auto; max-height:40vh;
  padding-left:calc(1.25rem + 4px);
}}
@media(max-width:900px) {{
  .slide-view {{ grid-template-columns:1fr; }}
  .slide-img-col {{ border-right:none; border-bottom:1px solid var(--line); max-height:40vh; }}
}}

.progress-bar {{
  height:2px; background:var(--line); flex-shrink:0;
}}
.progress-fill {{
  height:100%; background:var(--c); transition:width .25s;
}}

.pres-footer {{
  padding:.6rem max(4vw,calc((100vw - 1240px)/2));
  border-top:1px solid var(--line);
  display:flex; gap:2rem; flex-shrink:0;
}}
.pres-footer a {{ font-size:.65rem; color:var(--soft); letter-spacing:.06em; }}
.pres-footer a:hover {{ color:var(--ink); }}
</style>
</head>
<body>

<div class="pres-nav">
  <h1>{meta["title"]}</h1>
  <span class="pres-counter" id="counter">01 / {total:02d}</span>
  <button class="pres-btn" id="prev" onclick="go(-1)" disabled>← Prev</button>
  <button class="pres-btn" id="next" onclick="go(1)">Next →</button>
</div>

<div class="progress-bar"><div class="progress-fill" id="prog" style="width:{100/total:.1f}%"></div></div>

<div class="slide-view">
  <div class="slide-img-col" id="imgcol">
    <img id="simg" src="" alt="slide" style="display:none;" />
    <div class="no-img" id="noimg">No frame available</div>
    <div class="zoom-bar">
      <button class="zoom-btn" onclick="zoom(1.25)">＋</button>
      <button class="zoom-btn" onclick="zoom(0.8)">－</button>
      <button class="zoom-btn" onclick="resetZoom()">↺</button>
    </div>
  </div>
  <div class="slide-text-col">
    <div class="slide-ts"   id="ts"></div>
    <div class="slide-key"  id="key"></div>
    <div class="slide-full" id="full"></div>
  </div>
</div>

<div class="pres-footer">
  <a href="{meta["related_paper"]}">{meta["related_label"]} ↗</a>
  <a href="../../index.html">← Transcripts</a>
  <a href="/">← calyr.aí</a>
</div>

<script>
const DATA = {slides_json};
let cur = 0;
function render() {{
  const s = DATA[cur];
  document.getElementById('ts').textContent   = s.ts;
  document.getElementById('key').textContent  = s.key || '—';
  document.getElementById('full').textContent = s.full;
  document.getElementById('counter').textContent = String(cur+1).padStart(2,'0') + ' / {total:02d}';
  document.getElementById('prog').style.width = ((cur+1)/{total}*100).toFixed(1)+'%';
  document.getElementById('prev').disabled = cur === 0;
  document.getElementById('next').disabled = cur === DATA.length-1;
  const img = document.getElementById('simg');
  const noimg = document.getElementById('noimg');
  if (s.img) {{
    img.src = s.img; img.style.display = 'block'; noimg.style.display = 'none';
  }} else {{
    img.style.display = 'none'; noimg.style.display = 'block';
  }}
}}
function go(d) {{ cur = Math.max(0, Math.min(DATA.length-1, cur+d)); render(); }}
render();

// ── Zoom + Pan ──────────────────────────────────────────────
let sc=1, tx=0, ty=0, dragging=false, startX, startY;
const col = document.getElementById('imgcol');

function applyT() {{
  const img = document.getElementById('simg');
  img.style.transform = `scale(${{sc}}) translate(${{tx}}px,${{ty}}px)`;
}}
function zoom(f) {{ sc = Math.min(8, Math.max(1, sc*f)); if(sc===1){{tx=0;ty=0;}} applyT(); }}
function resetZoom() {{ sc=1; tx=0; ty=0; applyT(); }}

col.addEventListener('wheel', e => {{
  e.preventDefault(); zoom(e.deltaY < 0 ? 1.15 : 0.87);
}}, {{passive:false}});
col.addEventListener('mousedown', e => {{
  if(sc<=1) return;
  dragging=true; startX=e.clientX-tx; startY=e.clientY-ty;
  col.classList.add('dragging');
}});
window.addEventListener('mouseup', () => {{ dragging=false; col.classList.remove('dragging'); }});
window.addEventListener('mousemove', e => {{
  if(!dragging) return; tx=e.clientX-startX; ty=e.clientY-startY; applyT();
}});
let lastDist=0;
col.addEventListener('touchstart', e => {{ if(e.touches.length===2) lastDist=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY); }});
col.addEventListener('touchmove', e => {{
  if(e.touches.length!==2) return; e.preventDefault();
  const d=Math.hypot(e.touches[0].clientX-e.touches[1].clientX,e.touches[0].clientY-e.touches[1].clientY);
  zoom(d/lastDist); lastDist=d;
}},{{passive:false}});
</script>
</body>
</html>"""


def run():
    for stem, meta in TALKS.items():
        vtt = VTT_DIR / f"{stem}.vtt"
        out = OUT_DIR / f"{stem}.html"
        if not vtt.exists():
            print(f"  ✗ {stem}.vtt missing")
            continue
        entries  = parse_vtt(vtt)
        segments = group_segments(entries, window=90)
        html     = build_html(stem, meta, segments)
        out.write_text(html, encoding="utf-8")
        print(f"  ✓ {stem}.html — {len(segments)} segments")
    print("Done.")


if __name__ == "__main__":
    run()
