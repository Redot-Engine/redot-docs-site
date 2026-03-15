import os
import json
import re

SPECIAL_LABELS = {
    'i18n': 'Internationalization (i18n)',
    'xr': 'XR (AR/VR)',
    '2d': '2D',
    '3d': '3D',
    'io': 'Input/Output (IO)',
    'ui': 'User Interface (UI)',
    'ios': 'iOS',
    'android': 'Android',
    'gdextension': 'GDExtension',
    'gdscript': 'GDScript',
    'c_sharp': 'C#',
    'math': 'Math',
    'physics': 'Physics',
    'shaders': 'Shaders',
    'rendering': 'Rendering',
    'networking': 'Networking',
    'navigation': 'Navigation',
    'audio': 'Audio',
    'animation': 'Animation',
    'platform': 'Platform',
    'assets_pipeline': 'Assets Pipeline',
    'export': 'Export',
    'editor': 'Editor',
    'plugins': 'Plugins',
    'best_practices': 'Best Practices',
    'migrating': 'Migrating',
    'performance': 'Performance',
}

def get_label(folder_name):
    if folder_name in SPECIAL_LABELS:
        return SPECIAL_LABELS[folder_name]
    return folder_name.replace('_', ' ').capitalize()

def get_md_title(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('# '):
                    return line[2:].strip()
    except Exception:
        pass
    return None

def process_directory(root_dir):
    for root, dirs, files in os.walk(root_dir):
        # Filter out img and files directories
        dirs[:] = [d for d in dirs if d not in ('img', 'files') and not d.startswith('.')]
        
        if root == root_dir:
            continue
        
        folder_name = os.path.basename(root)
        label = get_label(folder_name)
        
        # 1. Create _category_.json
        category_json_path = os.path.join(root, '_category_.json')
        category_data = {
            "label": label,
            "link": {
                "type": "doc",
                "id": os.path.relpath(os.path.join(root, "index"), "docs").replace("\\", "/")
            }
        }
        with open(category_json_path, 'w', encoding='utf-8') as f:
            json.dump(category_data, f, indent=2)
            
        # 2. Create index.md
        index_md_path = os.path.join(root, 'index.md')
        
        # Prepare contents list
        articles = []
        for file in sorted(files):
            if file.endswith('.md') and file != 'index.md':
                title = get_md_title(os.path.join(root, file))
                if not title:
                    title = file[:-3].replace('_', ' ').capitalize()
                
                # Docusaurus link is relative to the current doc or ID
                # Since this is index.md in the same folder, we can just use the filename without extension
                link = file[:-3]
                articles.append(f"- [{title}]({link})")
        
        subcategories = []
        for d in sorted(dirs):
            sub_label = get_label(d)
            # Link to the subfolder's index
            link = f"./{d}/index"
            subcategories.append(f"- [{sub_label}]({link})")
            
        with open(index_md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {label}\n\n")
            f.write(f"This section contains tutorials and documentation about {label.lower()} in Redot Engine.\n\n")
            
            if articles:
                f.write("## Articles\n\n")
                for art in articles:
                    f.write(f"{art}\n")
                f.write("\n")
                
            if subcategories:
                f.write("## Subcategories\n\n")
                for sub in subcategories:
                    f.write(f"{sub}\n")
                f.write("\n")

if __name__ == "__main__":
    process_directory('docs/tutorials')
