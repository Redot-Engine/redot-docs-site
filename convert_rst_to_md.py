import os
import re
import sys
import argparse

def convert_rst_to_md(rst_content):
    lines = rst_content.splitlines()
    md_lines = []
    
    # Simple frontmatter based on first header or _doc_ reference
    title = ""
    doc_id = ""
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip rst-specific directives at the top
        if line.startswith(':allow_comments:') or line.startswith('.. meta::'):
            i += 1
            continue
            
        # Capture doc ID from .. _doc_...:
        match_id = re.match(r'^\.\. _(doc_.*):', line)
        if match_id:
            doc_id = match_id.group(1)
            i += 1
            continue
            
        # Handle Headers
        if i + 1 < len(lines):
            next_line = lines[i+1]
            if len(next_line) > 0 and all(c == '=' for c in next_line) and len(next_line) >= len(line):
                title = line.strip()
                md_lines.append(f"# {title}")
                i += 2
                continue
            elif len(next_line) > 0 and all(c == '-' for c in next_line) and len(next_line) >= len(line):
                md_lines.append(f"## {line.strip()}")
                i += 2
                continue
            elif len(next_line) > 0 and all(c == '~' for c in next_line) and len(next_line) >= len(line):
                md_lines.append(f"### {line.strip()}")
                i += 2
                continue
            elif len(next_line) > 0 and all(c == '^' for c in next_line) and len(next_line) >= len(line):
                md_lines.append(f"#### {line.strip()}")
                i += 2
                continue

        # Handle tabs and code-tabs
        if line.strip() == '.. tabs::':
            md_lines.append('<Tabs>')
            i += 1
            continue
        
        match_code_tab = re.match(r'^\s+\.\. code-tab::\s+(\w+)', line)
        if match_code_tab:
            lang = match_code_tab.group(1)
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            
            if i < len(lines):
                indent = len(lines[i]) - len(lines[i].lstrip())
                block = []
                while i < len(lines) and (not lines[i].strip() or (len(lines[i]) - len(lines[i].lstrip()) >= indent)):
                    block.append(lines[i][indent:])
                    i += 1
                md_lines.append(f'<TabItem value="{lang}" label="{lang.capitalize()}">')
                md_lines.append('')
                md_lines.append(f'```{lang}')
                md_lines.extend(block)
                md_lines.append('```')
                md_lines.append('')
                md_lines.append('</TabItem>')
            continue
        
        if line.strip() == '' and i > 0 and md_lines and md_lines[-1] == '</TabItem>':
            # Check if next tab follows or if we should close <Tabs>
            next_non_empty = i + 1
            while next_non_empty < len(lines) and not lines[next_non_empty].strip():
                next_non_empty += 1
            if next_non_empty >= len(lines) or not re.match(r'^\s+\.\. code-tab::', lines[next_non_empty]):
                md_lines.append('</Tabs>')
            else:
                md_lines.append('')
            i += 1
            continue

        if '<Tabs>' in md_lines and '</Tabs>' not in md_lines:
             # Check if we should close Tabs because next line is not a tab
             if line.strip() and not re.match(r'^\s+\.\. code-tab::', line):
                  md_lines.append('</Tabs>')
                  md_lines.append('')

        # Admonitions
        match_admonition = re.match(r'^\.\.\s+(note|warning|seealso|important|tip)::', line)
        if match_admonition:
            adm_type = match_admonition.group(1)
            if adm_type == 'seealso': adm_type = 'info'
            md_lines.append(f':::{adm_type}')
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines):
                indent = len(lines[i]) - len(lines[i].lstrip())
                while i < len(lines) and (not lines[i].strip() or (len(lines[i]) - len(lines[i].lstrip()) >= indent)):
                    md_lines.append(lines[i][indent:])
                    i += 1
            md_lines.append(':::')
            continue

        # Inline replacements
        line = re.sub(r':ref:`([^<]+)\s*<([^>]+)>`', r'[\1](\2)', line)
        line = re.sub(r':ref:`([^`]+)`', r'[\1](\1)', line)
        line = re.sub(r'`([^<]+)\s*<([^>]+)>`_', r'[\1](\2)', line)
        line = re.sub(r'`([^`]+)`_', r'[\1](\1)', line)
        
        # Multiline :ref:
        if i + 1 < len(lines) and ':ref:`' in line and '>`' not in line:
             next_line = lines[i+1].strip()
             if '>`' in next_line:
                 combined = line + ' ' + next_line
                 combined = re.sub(r':ref:`([^<]+)\s*<([^>]+)>`', r'[\1](\2)', combined)
                 md_lines.append(combined)
                 i += 2
                 continue
        line = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', line)
        line = re.sub(r'\*([^*]+)\*', r'*\1*', line)
        
        # Images
        match_img = re.match(r'^\.\.\s+(?:image|figure)::\s+(.*)', line)
        if match_img:
            img_path = match_img.group(1).strip()
            md_lines.append(f'![Image]({img_path})')
            i += 1
            continue

        md_lines.append(line)
        i += 1

    # Add Tabs import if used
    final_md = []
    if any('<Tabs>' in l for l in md_lines):
        final_md.append('import Tabs from "@theme/Tabs";')
        final_md.append('import TabItem from "@theme/TabItem";')
        final_md.append('')
    
    result = "\n".join(final_md + md_lines)
    # Ensure <Tabs> is closed if it wasn't
    if '<Tabs>' in result and '</Tabs>' not in result:
        result += '\n</Tabs>'
        
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result

def main():
    parser = argparse.ArgumentParser(description='Convert RST files in a directory to Markdown.')
    parser.add_argument('directory', help='Relative path to the directory containing RST files')
    args = parser.parse_args()

    directory = args.directory

    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        sys.exit(1)

    for filename in os.listdir(directory):
        if filename.endswith('.rst'):
            rst_path = os.path.join(directory, filename)
            md_path = os.path.join(directory, filename[:-4] + '.md')
            print(f"Converting {rst_path} to {md_path}")
            try:
                with open(rst_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                md_content = convert_rst_to_md(content)
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
            except Exception as e:
                print(f"Failed to convert {rst_path}: {e}")

if __name__ == '__main__':
    main()
