#!/usr/bin/env python3
"""Swiss Design HTML Generator - No external deps"""

import re
from pathlib import Path
from datetime import datetime

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def simple_markdown_to_html(text):
    """Minimal markdown conversion without external library"""
    # Headers
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
    
    # Italic
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'_(.*?)_', r'<em>\1</em>', text)
    
    # Links
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    
    # Lists
    text = re.sub(r'^\- (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'((?:<li>.*?</li>\n?)+)', r'<ul>\1</ul>', text, flags=re.DOTALL)
    
    # Paragraphs
    paragraphs = text.split('\n\n')
    text = '\n\n'.join([f'<p>{p}</p>' if p and not p.startswith('<') else p for p in paragraphs])
    
    return text

def extract_section(md_content, section_id):
    """Extract section content from markdown"""
    pattern = rf"## {section_id}\n\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, md_content, re.DOTALL)
    return match.group(1) if match else ""

base_path = Path("/Users/rtscheliessnig/workspace-active/parvotec/Machine learning for Rupert/transcripts")

md_content = read_file(base_path / "parvotec_analysis.md")

# Navigation items
nav_items = [
    ("1. Parvotec", "parvotec"),
    ("2. ML Framework", "framework"),
    ("3. Lir Presentation", "lir"),
    ("4. Videos", "videos"),
    ("5. Papers", "papers"),
    ("6. Glossary", "glossary"),
]

# Section titles
sections_config = [
    ("parvotec", "Parvotec Project"),
    ("framework", "ML Framework & Strategies"),
    ("lir", "Lir_AAV_LLM Presentation"),
    ("videos", "ASGCT 2026 Videos"),
    ("papers", "Research Papers"),
    ("glossary", "Glossary"),
]

# Generate nav HTML
nav_html = "\n".join([f'<a href="#{sid}" class="nav-link">{label}</a>' for label, sid in nav_items])

# Generate sections HTML
sections_html = ""
for section_id, title in sections_config:
    content = extract_section(md_content, section_id)
    content_html = simple_markdown_to_html(content)
    sections_html += f'''
    <section id="{section_id}" class="section">
        <h2>{title}</h2>
        <div class="section-content">
            {content_html}
        </div>
    </section>
    '''

# Full HTML with Swiss Design CSS
html_output = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Parvotec Analysis | ASGCT 2026</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: "Helvetica Neue", Arial, sans-serif;
            color: #1a1a1a;
            background: #ffffff;
            line-height: 1.6;
        }}
        
        .header {{
            background: #ffffff;
            border-bottom: 1px solid #e5e5e5;
            padding: 60px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 48px;
            font-weight: 300;
            letter-spacing: -1px;
            color: #0a0e27;
            margin-bottom: 8px;
        }}
        
        .subtitle {{
            font-size: 18px;
            color: #666666;
            margin-bottom: 12px;
            font-weight: 300;
        }}
        
        .navigation {{
            background: #ffffff;
            border-bottom: 1px solid #e5e5e5;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .nav-content {{
            max-width: 1100px;
            margin: 0 auto;
            display: flex;
            gap: 40px;
            padding: 16px 60px;
            flex-wrap: wrap;
        }}
        
        .nav-link {{
            text-decoration: none;
            color: #666666;
            font-size: 13px;
            font-weight: 500;
            transition: color 0.3s;
            letter-spacing: 0.3px;
        }}
        
        .nav-link:hover {{
            color: #0a0e27;
        }}
        
        main {{
            max-width: 1100px;
            margin: 0 auto;
        }}
        
        .section {{
            padding: 60px;
            border-bottom: 1px solid #e5e5e5;
        }}
        
        .section:last-of-type {{
            border-bottom: none;
        }}
        
        .section h2 {{
            font-size: 28px;
            font-weight: 400;
            letter-spacing: -0.5px;
            margin-bottom: 24px;
            color: #0a0e27;
        }}
        
        .section h3 {{
            font-size: 16px;
            font-weight: 600;
            margin-top: 24px;
            margin-bottom: 12px;
            color: #0a0e27;
        }}
        
        .section h3:first-child {{
            margin-top: 0;
        }}
        
        .section-content {{
            color: #1a1a1a;
            line-height: 1.8;
        }}
        
        .section-content p {{
            margin-bottom: 16px;
        }}
        
        .section-content ul {{
            margin-left: 20px;
            margin-bottom: 16px;
        }}
        
        .section-content li {{
            margin-bottom: 8px;
        }}
        
        .section-content strong {{
            font-weight: 600;
            color: #0a0e27;
        }}
        
        .section-content em {{
            font-style: italic;
            color: #666666;
        }}
        
        .section-content a {{
            color: #0a0e27;
            text-decoration: underline;
        }}
        
        .footer {{
            background: #f5f5f5;
            padding: 60px;
            text-align: center;
            color: #666666;
            font-size: 13px;
            border-top: 1px solid #e5e5e5;
        }}
        
        .footer strong {{
            color: #0a0e27;
        }}
        
        @media (max-width: 768px) {{
            .header {{ padding: 40px 24px; }}
            .nav-content {{ gap: 16px; padding: 16px 24px; }}
            .section {{ padding: 40px 24px; }}
            .header h1 {{ font-size: 32px; }}
            .section h2 {{ font-size: 20px; }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>Parvotec Analysis</h1>
        <p class="subtitle">AAV Capsid Engineering × Machine Learning × Pain Therapy</p>
    </header>
    
    <nav class="navigation">
        <div class="nav-content">
            {nav_html}
        </div>
    </nav>
    
    <main>
        {sections_html}
    </main>
    
    <footer class="footer">
        <p><strong>Parvotec | ASGCT 2026 Analysis</strong></p>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")} | YAML + Markdown → Swiss Design</p>
    </footer>
</body>
</html>
"""

output_file = base_path / "parvotec_analysis.html"
with open(output_file, 'w') as f:
    f.write(html_output)

print(f"✓ Generated: {output_file}")
