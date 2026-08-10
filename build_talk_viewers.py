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
    seg_blocks = []
    for i, seg in enumerate(segments, 1):
        t_start = fmt_time(seg[0]["s"])
        t_end   = fmt_time(seg[-1]["e"])
        full    = " ".join(e["t"] for e in seg)
        key     = key_sentence(seg)
        seg_blocks.append(f"""
<div class="seg" id="s{i}">
  <div class="seg-num" style="color:{color};">{i:02d}<br><span class="seg-ts">{t_start}–{t_end}</span></div>
  <div class="seg-body">
    <p class="seg-key">"{key}"</p>
    <p class="seg-full">{full}</p>
  </div>
</div>""")

    segs_html = "\n".join(seg_blocks)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{meta["title"]} — calyr.aí</title>
<link rel="stylesheet" href="{CSS_REL}" />
<style>
.talk-header {{ padding:52px max(4vw,calc((100vw - 1240px)/2)) 32px; border-bottom:1px solid var(--line); }}
.talk-header h1 {{ font-size:clamp(1.4rem,3.5vw,2.4rem); font-weight:400; letter-spacing:-.04em; line-height:1.1; }}
.talk-header .speaker {{ font-size:.68rem; color:var(--soft); letter-spacing:.1em; text-transform:uppercase; margin-top:10px; }}
.talk-meta {{ font-size:.7rem; color:var(--soft); margin-top:1.5rem; display:flex; gap:1.5rem; flex-wrap:wrap; }}
.talk-meta a {{ color:{color}; }}
.seg {{ display:grid; grid-template-columns:4rem 1fr; gap:0;
        padding:2rem max(4vw,calc((100vw - 1240px)/2));
        border-bottom:1px solid var(--line); }}
.seg:hover {{ background:var(--card); }}
.seg-num {{ font-size:.58rem; font-weight:700; font-family:monospace; letter-spacing:.08em;
            line-height:1.4; padding-top:.2rem; }}
.seg-ts {{ font-size:.5rem; color:var(--soft); font-weight:400; }}
.seg-key {{ font-family:Georgia,'Times New Roman',serif; font-size:.95rem; color:var(--ink);
            line-height:1.65; margin:0 0 .75rem; border-left:3px solid {color};
            padding-left:1rem; }}
.seg-full {{ font-size:.78rem; color:var(--soft); line-height:1.7; margin:0; }}
</style>
</head>
<body>
  <header>
    <h1>calyr.aí</h1>
    <p>Adaptive Research Modeling · 2026</p>
  </header>
  <div class="talk-header">
    <h1>{meta["title"]}</h1>
    <p class="speaker">{meta["speaker"]}</p>
    <div class="talk-meta">
      <span>{len(segments)} segments · {fmt_time(segments[-1][-1]["e"] if segments else 0)} total</span>
      <a href="{meta["related_paper"]}">{meta["related_label"]} ↗</a>
      <a href="../../index.html">← Transcripts</a>
      <a href="/">← calyr.aí</a>
    </div>
  </div>
{segs_html}
  <footer>
    <p>calyr.aí Research · 2026</p>
    <p><a href="{meta["related_paper"]}">{meta["related_label"]}</a></p>
  </footer>
  <script src="/js/main.js" defer></script>
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
