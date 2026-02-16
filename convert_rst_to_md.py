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
        match_id = re.match(r'^\s*\.\.\s+_(doc_.*):', line)
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
            md_lines.append('')
            md_lines.append('<Tabs>')
            md_lines.append('')
            i += 1
            continue
        
        match_tab = re.match(r'^\s*\.\. tab::\s+(.*)', line)
        if match_tab:
            label = match_tab.group(1).strip()
            value = re.sub(r'[^a-z0-9_]', '_', label.lower())
            i += 1
            # Skip optional labels or other options
            while i < len(lines) and (lines[i].strip().startswith(':') or not lines[i].strip()):
                i += 1
            
            if i < len(lines):
                indent = len(lines[i]) - len(lines[i].lstrip())
                block = []
                while i < len(lines) and (not lines[i].strip() or (len(lines[i]) - len(lines[i].lstrip()) >= indent)):
                    block.append(lines[i])
                    i += 1
                md_lines.append('')
                md_lines.append(f'<TabItem value="{value}" label="{label}">')
                md_lines.append('')
                # Recursively process the block content
                processed_block = convert_rst_to_md("\n".join(l[indent:] for l in block))
                processed_lines = [l for l in processed_block.splitlines() if not l.startswith('import ')]
                md_lines.extend(processed_lines)
                md_lines.append('')
                md_lines.append('</TabItem>')
                md_lines.append('')
            continue

        match_code_tab = re.match(r'^\s*\.\. code-tab::\s+(\w+)(?:\s+(.*))?', line)
        if match_code_tab:
            lang = match_code_tab.group(1)
            label = match_code_tab.group(2) or lang.capitalize()
            # Use label for value to ensure uniqueness if multiple tabs have same language
            value = re.sub(r'[^a-z0-9_]', '_', label.lower())
            i += 1
            # Skip optional labels or other options
            while i < len(lines) and (lines[i].strip().startswith(':') or not lines[i].strip()):
                i += 1
            
            if i < len(lines):
                indent = len(lines[i]) - len(lines[i].lstrip())
                block = []
                while i < len(lines) and (not lines[i].strip() or (len(lines[i]) - len(lines[i].lstrip()) >= indent)):
                    block.append(lines[i])
                    i += 1
                md_lines.append('')
                md_lines.append(f'<TabItem value="{value}" label="{label}">')
                md_lines.append('')
                # Recursively process the block content
                processed_block = convert_rst_to_md("\n".join(l[indent:] for l in block))
                processed_lines = [l for l in processed_block.splitlines() if not l.startswith('import ')]
                md_lines.extend(processed_lines)
                md_lines.append('')
                md_lines.append('</TabItem>')
                md_lines.append('')
            continue
        
        if line.strip() == '' and i > 0 and md_lines and (md_lines[-1] == '</TabItem>' or (len(md_lines) > 1 and md_lines[-2] == '</TabItem>')):
            # Check if next tab follows or if we should close <Tabs>
            next_non_empty = i + 1
            while next_non_empty < len(lines) and not lines[next_non_empty].strip():
                next_non_empty += 1
            if next_non_empty >= len(lines) or not (re.match(r'^\s+\.\. code-tab::', lines[next_non_empty]) or re.match(r'^\s+\.\. tab::', lines[next_non_empty])):
                md_lines.append('')
                md_lines.append('</Tabs>')
                md_lines.append('')
            else:
                md_lines.append('')
            i += 1
            continue

        if '<Tabs>' in md_lines and '</Tabs>' not in md_lines:
             # Check if we should close Tabs because next line is not a tab
             if line.strip() and not (re.match(r'^\s*\.\. code-tab::', line) or re.match(r'^\s*\.\. tab::', line)):
                  # Close any open TabItem first (shouldn't happen with recursive, but safety)
                  # In recursive mode, this part should only be reached if we found a line
                  # that is NOT a tab directive while we have an open <Tabs>.
                  md_lines.append('')
                  md_lines.append('</Tabs>')
                  md_lines.append('')

        # Admonitions
        match_admonition = re.match(r'^\s*\.\.\s+(note|warning|seealso|important|tip)::', line, re.IGNORECASE)
        if match_admonition:
            adm_type = match_admonition.group(1).lower()
            if adm_type == 'seealso': adm_type = 'info'
            md_lines.append('')
            md_lines.append(f':::{adm_type}')
            md_lines.append('')
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines):
                # We need to process the admonition block as well.
                indent = len(lines[i]) - len(lines[i].lstrip())
                block = []
                while i < len(lines) and (not lines[i].strip() or (len(lines[i]) - len(lines[i].lstrip()) >= indent)):
                    block.append(lines[i]) 
                    i += 1
                
                # Recursively process the block content
                processed_block = convert_rst_to_md("\n".join(l[indent:] for l in block))
                # Skip any added Tabs import from recursion
                processed_lines = [l for l in processed_block.splitlines() if not l.startswith('import ')]
                md_lines.extend(processed_lines)

            md_lines.append('')
            md_lines.append(':::')
            md_lines.append('')
            continue

        # Handle generic code blocks (.. code-block::)
        match_code = re.match(r'^\s*\.\.\s+code-block::\s*(\w+)?', line)
        if match_code:
            lang = match_code.group(1) or ""
            i += 1
            # Skip optional captions or other options
            while i < len(lines) and (lines[i].strip().startswith(':') or not lines[i].strip()):
                i += 1
            
            if i < len(lines):
                indent = len(lines[i]) - len(lines[i].lstrip())
                block = []
                while i < len(lines) and (not lines[i].strip() or (len(lines[i]) - len(lines[i].lstrip()) >= indent)):
                    block.append(lines[i][indent:])
                    i += 1
                md_lines.append('')
                md_lines.append(f'```{lang}')
                md_lines.extend(block)
                md_lines.append('```')
                md_lines.append('')
            continue

        # Handle simple indented code blocks (marked by :: at end of previous line)
        if line.strip() == '::':
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines):
                indent = len(lines[i]) - len(lines[i].lstrip())
                block = []
                while i < len(lines) and (not lines[i].strip() or (len(lines[i]) - len(lines[i].lstrip()) >= indent)):
                    block.append(lines[i][indent:])
                    i += 1
                md_lines.append('')
                md_lines.append('```')
                md_lines.extend(block)
                md_lines.append('```')
                md_lines.append('')
            continue
        
        if line.endswith('::') and not line.strip().startswith('..'):
            md_lines.append(line[:-2].strip())
            md_lines.append('')
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines):
                indent = len(lines[i]) - len(lines[i].lstrip())
                block = []
                while i < len(lines) and (not lines[i].strip() or (len(lines[i]) - len(lines[i].lstrip()) >= indent)):
                    block.append(lines[i][indent:])
                    i += 1
                md_lines.append('')
                md_lines.append('```')
                md_lines.extend(block)
                md_lines.append('```')
                md_lines.append('')
            continue

        # Inline replacements
        # Escape angle brackets that are likely NOT part of JSX
        def escape_angle_brackets(text):
            # If the line contains known JSX tags, we need to be careful
            known_tags = ['Tabs', 'TabItem', '/Tabs', '/TabItem']
            
            # Escape all < and > except for known tags
            # First, temporarily replace known tags with placeholders
            for i, tag in enumerate(known_tags):
                text = text.replace(f'<{tag}>', f'__JSX_TAG_{i}__')
                # Handle attributes for TabItem
                if tag == 'TabItem' and '<TabItem ' in text:
                     # This is tricky with simple replace. Use regex for TabItem with attributes
                     text = re.sub(r'<TabItem\s+([^>]+)>', r'__JSX_TABITEM_ATTRS_START__\1__JSX_TABITEM_ATTRS_END__', text)

            # Special case for [doc_compiling_for_linuxbsd_oneliners](doc_compiling_for_linuxbsd_oneliners)
            # which might be in the text and contains <> in my thought, but wait.
            # Actually, I should just escape ALL < and > and then restore specific ones.
            
            text = text.replace('<', '&lt;').replace('>', '&gt;')

            # Restore placeholders
            for i, tag in enumerate(known_tags):
                text = text.replace(f'__JSX_TAG_{i}__', f'<{tag}>')
            
            text = re.sub(r'__JSX_TABITEM_ATTRS_START__(.*)__JSX_TABITEM_ATTRS_END__', r'<TabItem \1>', text)
            
            return text

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
            # Skip image options
            while i < len(lines) and (lines[i].strip().startswith(':') or (not lines[i].strip() and i+1 < len(lines) and lines[i+1].strip().startswith(':'))):
                i += 1
            continue

        md_lines.append(escape_angle_brackets(line))
        i += 1

    # Add Tabs import if used
    final_md = []
    if any('<Tabs' in l for l in md_lines):
        final_md.append('import Tabs from "@theme/Tabs";')
        final_md.append('import TabItem from "@theme/TabItem";')
        final_md.append('')
    
    # Filter out redundant imports if they were already added (e.g. by recursion)
    # Actually recursion shouldn't add them to md_lines.
    
    result = "\n".join(final_md + md_lines)
    # Ensure <Tabs> is closed if it wasn't
    open_tabs = result.count('<Tabs>')
    close_tabs = result.count('</Tabs>')
    if open_tabs > close_tabs:
        for _ in range(open_tabs - close_tabs):
            result += '\n\n</Tabs>\n'
        
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result

def main():
    parser = argparse.ArgumentParser(description='Convert RST files in a directory to Markdown.')
    parser.add_argument('directory', help='Relative path to the directory containing RST files')
    parser.add_argument('-r', '--recursive', action='store_true', help='Search for RST files recursively')
    args = parser.parse_args()

    directory = args.directory

    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        sys.exit(1)

    if args.recursive:
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.rst'):
                    process_file(root, filename)
    else:
        for filename in os.listdir(directory):
            if filename.endswith('.rst'):
                process_file(directory, filename)

def process_file(directory, filename):
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
