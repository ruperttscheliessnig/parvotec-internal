#!/usr/bin/env python3
"""
Parvotec Analysis HTML Generator
Converts YAML config + Markdown content → Clean Swiss Design HTML
"""

import yaml
import markdown
import re
from pathlib import Path
from datetime import datetime

def load_yaml(path):
    """Load YAML configuration file"""
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def load_markdown(path):
    """Load Markdown content file"""
    with open(path, 'r') as f:
        return f.read()

def extract_section_content(markdown_content, section_id):
    """Extract content for specific section from markdown"""
    pattern = rf"## {section_id}\n\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, markdown_content, re.DOTALL)
    return match.group(1) if match else ""

def markdown_to_html(text):
    """Convert markdown to HTML"""
    return markdown.markdown(text, extensions=['extra', 'nl2br'])

def generate_header_html(config):
    """Generate header section"""
    meta = config['metadata']
    colors = config['design']['colors']
    typo = config['design']['typography']
    
    stats_html = "\n".join([
        f'<div class="stat"><div class="stat-value">{s["value"]}</div><div class="stat-label">{s["label"]}</div></div>'
        for s in config['stats']
    ])
    
    return f"""
    <header class="header">
        <div class="header-content">
            <h1>{meta['title']}</h1>
            <p class="subtitle">{meta['subtitle']}</p>
            <p class="description">{meta['description']}</p>
            <div class="stats">
                {stats_html}
            </div>
        </div>
    </header>
    """

def generate_navigation_html(config):
    """Generate navigation"""
    nav_items = "\n".join([
        f'<a href="#{item["id"]}" class="nav-link">{item["label"]}</a>'
        for item in config['navigation']['items']
    ])
    
    return f"""
    <nav class="navigation">
        <div class="nav-content">
            {nav_items}
        </div>
    </nav>
    """

def generate_section_html(section, markdown_content, config):
    """Generate single section"""
    section_id = section['id']
    title = section['title']
    
    # Extract content from markdown
    content = extract_section_content(markdown_content, section_id)
    content_html = markdown_to_html(content)
    
    return f"""
    <section id="{section_id}" class="section">
        <h2>{title}</h2>
        <div class="section-content">
            {content_html}
        </div>
    </section>
    """

def generate_footer_html(config):
    """Generate footer"""
    meta = config['metadata']
    return f"""
    <footer class="footer">
        <p><strong>{meta['title']}</strong></p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Analysis based on ASGCT 2026 materials</p>
    </footer>
    """

def generate_css(config):
    """Generate CSS from config"""
    colors = config['design']['colors']
    typo = config['design']['typography']
    spacing = config['design']['spacing']
    
    return f"""
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: {config['design']['font_family']};
            color: {colors['gray_dark']};
            background: {colors['white']};
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}
        
        /* HEADER */
        .header {{
            background: {colors['white']};
            border-bottom: 1px solid {colors['gray_light']};
            padding: {spacing['content_padding']}px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: {typo['h1']['size']};
            font-weight: {typo['h1']['weight']};
            letter-spacing: {typo['h1']['letter_spacing']};
            margin-bottom: 8px;
            color: {colors['navy']};
        }}
        
        .subtitle {{
            font-size: 18px;
            color: {colors['gray_medium']};
            margin-bottom: 12px;
            font-weight: 300;
        }}
        
        .description {{
            font-size: 14px;
            color: {colors['gray_medium']};
            max-width: 700px;
            margin: 20px auto;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: {spacing['element_gap']}px;
            margin-top: 40px;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .stat {{
            text-align: center;
            padding: 16px;
            border: 1px solid {colors['gray_light']};
            background: {colors['gray_light']};
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: 600;
            color: {colors['navy']};
        }}
        
        .stat-label {{
            font-size: 12px;
            color: {colors['gray_medium']};
            margin-top: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        /* NAVIGATION */
        .navigation {{
            background: {colors['white']};
            border-bottom: 1px solid {colors['gray_light']};
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        
        .nav-content {{
            max-width: 1100px;
            margin: 0 auto;
            display: flex;
            gap: 40px;
            padding: 16px {spacing['content_padding']}px;
        }}
        
        .nav-link {{
            text-decoration: none;
            color: {colors['gray_medium']};
            font-size: 13px;
            font-weight: 500;
            transition: color 0.3s;
            letter-spacing: 0.3px;
        }}
        
        .nav-link:hover {{
            color: {colors['navy']};
        }}
        
        /* SECTIONS */
        .section {{
            max-width: 1100px;
            margin: 0 auto;
            padding: {spacing['section_gap']}px {spacing['content_padding']}px;
            border-bottom: 1px solid {colors['gray_light']};
        }}
        
        .section:last-of-type {{
            border-bottom: none;
        }}
        
        .section h2 {{
            font-size: {typo['h2']['size']};
            font-weight: {typo['h2']['weight']};
            letter-spacing: {typo['h2']['letter_spacing']};
            margin-bottom: 24px;
            color: {colors['navy']};
        }}
        
        .section h3 {{
            font-size: 16px;
            font-weight: 600;
            margin-top: 24px;
            margin-bottom: 12px;
            color: {colors['navy']};
        }}
        
        .section h3:first-child {{
            margin-top: 0;
        }}
        
        .section-content {{
            color: {colors['gray_dark']};
            line-height: 1.8;
        }}
        
        .section-content p {{
            margin-bottom: 16px;
        }}
        
        .section-content ul, .section-content ol {{
            margin-left: 20px;
            margin-bottom: 16px;
        }}
        
        .section-content li {{
            margin-bottom: 8px;
        }}
        
        .section-content strong {{
            font-weight: 600;
            color: {colors['navy']};
        }}
        
        .section-content em {{
            font-style: italic;
            color: {colors['gray_medium']};
        }}
        
        /* FOOTER */
        .footer {{
            background: {colors['gray_light']};
            padding: {spacing['content_padding']}px;
            text-align: center;
            color: {colors['gray_medium']};
            font-size: 13px;
        }}
        
        .footer strong {{
            color: {colors['navy']};
        }}
        
        /* RESPONSIVE */
        @media (max-width: 768px) {{
            .stats {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .nav-content {{
                gap: 16px;
                overflow-x: auto;
                padding-left: 16px;
                padding-right: 16px;
            }}
            
            .section {{
                padding: {spacing['section_gap']}px 24px;
            }}
            
            .header {{
                padding: 40px 24px;
            }}
        }}
    </style>
    """

def generate_html(yaml_path, md_path, output_path):
    """Main generator: YAML + Markdown → HTML"""
    
    # Load files
    config = load_yaml(yaml_path)
    md_content = load_markdown(md_path)
    
    # Generate components
    css = generate_css(config)
    header = generate_header_html(config)
    nav = generate_navigation_html(config)
    sections = "\n".join([
        generate_section_html(section, md_content, config)
        for section in config['sections']
    ])
    footer = generate_footer_html(config)
    
    # Assemble HTML
    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config['metadata']['title']}</title>
    {css}
</head>
<body>
    {header}
    {nav}
    <main>
        {sections}
    </main>
    {footer}
</body>
</html>
"""
    
    # Write output
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"✓ Generated: {output_path}")
    return output_path

if __name__ == "__main__":
    base_path = Path("/Users/rtscheliessnig/workspace-active/parvotec/Machine learning for Rupert/transcripts")
    
    yaml_file = base_path / "parvotec_analysis.yml"
    md_file = base_path / "parvotec_analysis.md"
    output_file = base_path / "parvotec_analysis.html"
    
    generate_html(yaml_file, md_file, output_file)
