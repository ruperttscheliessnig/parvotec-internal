"""
Extract key passages from VTT transcripts and inject as highlighted
"Key Ideas" section into each talk HTML page.

Key idea selection: sentences with highest density of biomedical/ML terms.
"""
import re
from pathlib import Path

BASE = Path.home() / "workspace-active/parvotec/Machine learning for Rupert/transcripts"
VTT_DIR = BASE / "vtt"
TALKS_DIR = BASE / "talks"

# High-value terms for scoring sentence importance
KEYWORDS = {
    # ML/AI methods
    "language model", "protein language", "esm", "esm-2", "corsair", "fine-tun",
    "bayesian", "variational", "autoencoder", "latent", "embedding", "fitness",
    "directed evolution", "surrogate", "active learning", "spearman",
    "transduction", "tropism", "tissue specificity", "liver", "heart",
    # AAV specifics
    "capsid", "serotype", "aav2", "aav9", "aav5", "variant", "library",
    "msa", "multiple sequence", "training data", "benchmark",
    "immune evasion", "immunogenicity", "potency", "detargeting",
    # Results language
    "outperform", "improve", "significant", "correlation", "accuracy",
    "we found", "we show", "our model", "our approach", "key insight",
    "importantly", "notably", "in summary", "conclusion"
}

TALK_MAP = {
    "AAV_Engineering_III":          "AAV Engineering III — Capsid Engineering Session",
    "AAV_Engineering_IV":           "AAV Engineering IV — Capsid Engineering Session",
    "AAV_Trafficking":              "AAV Trafficking",
    "Lir_AAV_LLM":                  "Lir Therapeutics — Corsair PLM for AAV",
    "ShapeTX_AAV5engineering":      "ShapeTX — AAV5 Engineering",
    "TuningReceptorInteractions_Caltech": "Tuning Receptor Interactions (Caltech)",
}


def parse_vtt(path: Path) -> list[str]:
    """Return list of spoken sentences from VTT."""
    text = path.read_text(encoding="utf-8")
    # Remove timestamps and WEBVTT header
    lines = [l.strip() for l in text.splitlines()]
    sentences = []
    for line in lines:
        if line.startswith("WEBVTT") or "-->" in line or line.isdigit() or not line:
            continue
        sentences.append(line)
    # Join into one text and split on sentence boundaries
    full = " ".join(sentences)
    full = re.sub(r'\s+', ' ', full)
    parts = re.split(r'(?<=[.!?])\s+', full)
    return [p.strip() for p in parts if len(p.strip()) > 40]


def score(sentence: str) -> int:
    s = sentence.lower()
    return sum(1 for kw in KEYWORDS if kw in s)


def top_passages(sentences: list[str], n: int = 6) -> list[str]:
    scored = [(score(s), s) for s in sentences]
    scored.sort(key=lambda x: -x[0])
    return [s for sc, s in scored if sc > 0][:n]


def inject_highlights(html_path: Path, passages: list[str], talk_title: str) -> None:
    if not passages:
        print(f"  ⚠ No passages found for {html_path.name}")
        return

    html = html_path.read_text(encoding="utf-8")

    # Build highlights HTML block
    items = "\n".join(
        f'    <div class="key-idea">'
        f'<span class="ki-num">{i+1:02d}</span>'
        f'<p>{p}</p>'
        f'</div>'
        for i, p in enumerate(passages)
    )

    block = f'''
<!-- Key Ideas injected by extract_key_ideas.py -->
<style>
.key-ideas-section {{ margin: 3rem max(4vw,calc((100vw - 1240px)/2)); }}
.key-ideas-section .section-label {{ font-size:.6rem; letter-spacing:.16em; text-transform:uppercase; color:var(--soft); margin-bottom:1rem; display:block; }}
.key-idea {{ display:grid; grid-template-columns:2rem 1fr; gap:1rem; padding:1rem 0; border-bottom:1px solid var(--line); }}
.key-idea:last-child {{ border-bottom:none; }}
.ki-num {{ font-size:.6rem; color:#39bfff; font-weight:700; font-family:monospace; padding-top:.25rem; }}
.key-idea p {{ font-size:.88rem; color:var(--ink); line-height:1.65; margin:0; }}
</style>
<div class="key-ideas-section">
  <span class="section-label">Key Ideas — {talk_title}</span>
{items}
</div>
<!-- end key ideas -->
'''

    # Inject after <body> opening (before existing content)
    if '<!-- Key Ideas' in html:
        # Already injected — replace
        html = re.sub(r'<!-- Key Ideas.*?<!-- end key ideas -->', block.strip(), html, flags=re.DOTALL)
    else:
        html = re.sub(r'(<header>)', block + r'\1', html, count=1)

    html_path.write_text(html, encoding="utf-8")
    print(f"  ✓ {html_path.name} — {len(passages)} key ideas")


def run():
    for stem, title in TALK_MAP.items():
        vtt = VTT_DIR / f"{stem}.vtt"
        html = TALKS_DIR / f"{stem}.html"
        if not vtt.exists():
            print(f"  ✗ {stem}.vtt not found")
            continue
        if not html.exists():
            print(f"  ✗ {stem}.html not found")
            continue
        sentences = parse_vtt(vtt)
        passages = top_passages(sentences, n=6)
        inject_highlights(html, passages, title)
    print("Done.")


if __name__ == "__main__":
    run()
