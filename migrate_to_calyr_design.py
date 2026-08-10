"""
Migrate parvotec HTML pages to calyr.ai design system.
- Replaces inline <style> with link to shared css/main.css
- Injects calyr.ai header + footer
- Preserves all page content
"""
import re
from pathlib import Path

BASE = Path.home() / "workspace-active/parvotec/Machine learning for Rupert/transcripts"

CALYR_HEADER = '''  <header>
    <h1>calyr.aí</h1>
    <p>Adaptive Research Modeling · 2026</p>
  </header>'''

CALYR_FOOTER = '''  <footer>
    <p>calyr.aí Research · 2026</p>
    <p><a href="https://calyrai.ai">calyrai.ai</a></p>
  </footer>'''

# CSS variables only needed if page uses them via inline styles
COMPAT_VARS = '''<style>
  /* calyr.ai compat: page-specific overrides using shared variables */
  .wrap { max-width: min(1240px, 94vw); margin: 0 auto; padding: 3rem max(4vw, calc((100vw - 1240px)/2)); }
</style>'''


def migrate(filepath: Path, css_rel_path: str = "css/main.css"):
    html = filepath.read_text(encoding="utf-8")

    # 1. Replace <style>...</style> with link to shared CSS
    html = re.sub(r'<style>.*?</style>', '', html, flags=re.DOTALL)

    # 2. Insert link tag in <head>
    link_tag = f'<link rel="stylesheet" href="{css_rel_path}" />\n{COMPAT_VARS}\n'
    html = html.replace('</head>', f'{link_tag}</head>', 1)

    # 3. Inject calyr.ai header after <body>
    if '<header>' not in html and 'calyr.aí' not in html:
        html = re.sub(r'(<body[^>]*>)', f'\\1\n{CALYR_HEADER}', html, count=1)

    # 4. Inject calyr.ai footer before </body>
    if CALYR_FOOTER.strip()[:10] not in html:
        html = html.replace('</body>', f'{CALYR_FOOTER}\n</body>', 1)

    filepath.write_text(html, encoding="utf-8")
    print(f"  ✓ {filepath.name}")


def run():
    # Talk pages (css is one level up from talks/)
    talks = list((BASE / "talks").glob("*.html"))
    print(f"Migrating {len(talks)} talk pages...")
    for f in talks:
        migrate(f, css_rel_path="../css/main.css")

    # Workstation / app pages in transcripts root
    patterns = ["parvotec_app_*.html", "parvotec_workstation*.html",
                "parvotec_scientific_node.html", "parvotec_aorta*.html",
                "parvotec_asgct*.html", "parvotec_proposal*.html"]
    root_pages = []
    for pattern in patterns:
        root_pages.extend(BASE.glob(pattern))

    print(f"Migrating {len(root_pages)} root pages...")
    for f in root_pages:
        migrate(f, css_rel_path="css/main.css")

    print("Done.")


if __name__ == "__main__":
    run()
