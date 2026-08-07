#!/usr/bin/env python3
"""
Universal HTML generator for Parvotec + Aorta specifications.
Reads YAML config, generates styled HTML with auto-linking.

Usage:
  python3 build_specifications.py parvotec
  python3 build_specifications.py aorta
  python3 build_specifications.py all
"""

import sys
import yaml
import pathlib
from datetime import datetime

def load_yaml(yaml_path):
    """Load YAML config file."""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def generate_html(data, project_name):
    """Generate HTML from YAML config."""
    meta = data['meta']
    sections = data['sections']
    
    # Color scheme by project
    project_colors = {
        'parvotec': {'accent': '#f59e0b', 'accent_light': '#fcd34d', 'bg_header': '#78350f'},
        'aorta': {'accent': '#39bfff', 'accent_light': '#7dd3fc', 'bg_header': '#0c2540'},
    }
    colors = project_colors.get(project_name, {'accent': '#f59e0b', 'accent_light': '#fcd34d', 'bg_header': '#78350f'})
    
    # Navigation
    nav_html = ''.join([
        f'    <a href="{link["href"]}" style="color:var(--accent); text-decoration:none; padding:0.5rem 1rem; border-bottom:3px solid transparent; transition:all 0.3s;" onmouseover="this.style.borderBottomColor=\'var(--accent)\'" onmouseout="this.style.borderBottomColor=\'transparent\'">{link["label"]}</a>\n'
        for link in meta.get('nav_links', [])
    ])
    
    # Sections
    sections_html = ''.join([
        f'    <section id="{s["id"]}" style="scroll-margin-top:80px; padding:2rem 0; border-top:1px solid #e5e7eb;">\n'
        f'      <h2 style="color:var(--accent); margin-bottom:1.5rem;">{s["title"]}</h2>\n'
        f'      {s["content"]}\n'
        f'    </section>\n'
        for s in sections
    ])
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{meta['title']}</title>
    <style>
        :root {{
            --accent: {colors['accent']};
            --accent-light: {colors['accent_light']};
            --bg-header: {colors['bg_header']};
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background: #f9fafb;
        }}
        
        header {{
            background: linear-gradient(135deg, var(--bg-header) 0%, #1f2937 100%);
            color: white;
            padding: 3rem 1.5rem;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        header h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        
        header .subtitle {{
            font-size: 0.95rem;
            opacity: 0.9;
            margin-bottom: 0.25rem;
        }}
        
        header .description {{
            font-size: 0.85rem;
            opacity: 0.8;
        }}
        
        nav {{
            background: white;
            border-bottom: 2px solid var(--accent-light);
            padding: 0.5rem 1.5rem;
            display: flex;
            gap: 1rem;
            overflow-x: auto;
            flex-wrap: wrap;
        }}
        
        nav a {{
            white-space: nowrap;
            font-weight: 500;
        }}
        
        .container {{
            max-width: 1240px;
            margin: 0 auto;
            padding: 0 1.5rem;
        }}
        
        main {{
            padding: 2rem 0;
        }}
        
        section {{
            margin-bottom: 3rem;
        }}
        
        h2 {{
            font-size: 1.75rem;
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 3px solid var(--accent-light);
        }}
        
        h3 {{
            font-size: 1.25rem;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            color: #374151;
        }}
        
        h4 {{
            font-size: 1.05rem;
            margin-top: 1rem;
            margin-bottom: 0.75rem;
            color: var(--accent);
            font-weight: 600;
        }}
        
        p {{
            margin-bottom: 1rem;
            line-height: 1.8;
        }}
        
        ul, ol {{
            margin-left: 1.5rem;
            margin-bottom: 1rem;
        }}
        
        li {{
            margin-bottom: 0.5rem;
        }}
        
        code {{
            background: #f3f4f6;
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        pre {{
            background: #1f2937;
            color: #f3f4f6;
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1rem 0;
            font-size: 0.9em;
            line-height: 1.5;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
        }}
        
        table.spec-table {{
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }}
        
        thead {{
            background: var(--accent-light);
            color: var(--bg-header);
            font-weight: 600;
        }}
        
        th {{
            padding: 1rem;
            text-align: left;
            border-bottom: 2px solid var(--accent);
        }}
        
        td {{
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        tbody tr:hover {{
            background: #f9fafb;
        }}
        
        tbody tr:last-child td {{
            border-bottom: none;
        }}
        
        a {{
            color: var(--accent);
            text-decoration: none;
            border-bottom: 1px dotted var(--accent);
            transition: all 0.2s;
        }}
        
        a:hover {{
            text-decoration: underline;
        }}
        
        .spec-card {{
            background: #f9fafb;
            border-left: 4px solid var(--accent);
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-radius: 4px;
        }}
        
        .spec-card h4 {{
            margin-top: 0;
            color: var(--accent);
        }}
        
        strong {{
            color: var(--bg-header);
            font-weight: 600;
        }}
        
        footer {{
            background: #f3f4f6;
            border-top: 1px solid #e5e7eb;
            padding: 2rem 1.5rem;
            text-align: center;
            color: #6b7280;
            font-size: 0.9rem;
            margin-top: 4rem;
        }}
        
        .back-link {{
            display: inline-block;
            margin-bottom: 1rem;
            padding: 0.5rem 1rem;
            background: var(--accent-light);
            color: var(--bg-header);
            border-radius: 4px;
            text-decoration: none !important;
            border: none !important;
            font-weight: 500;
            transition: all 0.2s;
        }}
        
        .back-link:hover {{
            background: var(--accent);
            color: white;
        }}
        
        @media (max-width: 768px) {{
            header h1 {{ font-size: 1.5rem; }}
            h2 {{ font-size: 1.4rem; }}
            h3 {{ font-size: 1.1rem; }}
            nav {{ flex-direction: column; }}
            nav a {{ padding: 0.5rem 0; }}
            .container {{ padding: 0 1rem; }}
            main {{ padding: 1rem 0; }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>calyr.aí {project_name.upper()}</h1>
            <div class="subtitle">{meta.get('subtitle', '')}</div>
            <div class="description">{meta.get('description', '')}</div>
        </div>
    </header>
    
    <nav class="container">
        {nav_html}
        <a href="{meta.get('back_href', '#')}" style="color:var(--accent); text-decoration:none; padding:0.5rem 1rem; margin-left:auto;">{meta.get('back_label', '← Back')}</a>
    </nav>
    
    <main class="container">
        {sections_html}
    </main>
    
    <footer>
        <strong>{meta['title']}</strong><br>
        Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} · calyr.aí Research · Multi-project architecture<br>
        <a href="{meta.get('back_href', '#')}" style="color:var(--accent);">{meta.get('back_label', 'Back')}</a>
    </footer>
</body>
</html>
"""
    
    return html

def main():
    """Main entry point."""
    projects = ['parvotec', 'aorta']
    
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == 'all':
            projects_to_build = projects
        elif arg in projects:
            projects_to_build = [arg]
        else:
            print(f"Usage: {sys.argv[0]} [parvotec|aorta|all]")
            sys.exit(1)
    else:
        projects_to_build = projects
    
    for project in projects_to_build:
        if project == 'parvotec':
            yaml_file = pathlib.Path('data/workstation-scientific-node.yml')
            base_dir = pathlib.Path('.')
        else:  # aorta
            yaml_file = pathlib.Path('../aorta/data/macbook-mobile-frontend.yml')
            base_dir = pathlib.Path('../aorta')
        
        if not yaml_file.exists():
            print(f"❌ {project}: {yaml_file} not found")
            continue
        
        try:
            data = load_yaml(yaml_file)
            html = generate_html(data, project)
            output_path = base_dir / data['meta']['output']
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"✓ {project}: {output_path}")
        except Exception as e:
            print(f"❌ {project}: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()
