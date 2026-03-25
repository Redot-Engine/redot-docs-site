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
    is_tabs_open = False

    def apply_inline_replacements(text):
        text = re.sub(r':ref:`([^<`]+?)\s*<([^>]+)>`', r'[\1](\2)', text)
        text = re.sub(r':ref:`([^`]+)`', r'[\1](\1)', text)
        text = re.sub(r':kbd:`([^`]+)`', r'`\1`', text)
        text = re.sub(r'`([^<`]+?)\s*<([^>]+)>`_', r'[\1](\2)', text)
        text = re.sub(r'`([^`]+)`_', r'[\1](\1)', text)
        text = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', text)
        text = re.sub(r'\*([^*]+)\*', r'*\1*', text)
        return text

    # Escape angle brackets that are likely NOT part of JSX
    def escape_angle_brackets(text):
        # First, apply inline replacements that involve angle brackets to avoid escaping them
        text = re.sub(r':ref:`([^<`]+?)\s*<([^>]+)>`', r'[\1](\2)', text)
        text = re.sub(r'`([^<`]+?)\s*<([^>]+)>`_', r'[\1](\2)', text)

        # If the line contains known JSX tags, we need to be careful
        known_tags = ['Tabs', 'TabItem', '/Tabs', '/TabItem']
        
        # Escape all < and > except for known tags
        # First, temporarily replace known tags with placeholders
        for idx, tag in enumerate(known_tags):
            text = text.replace(f'<{tag}>', f'__JSX_TAG_{idx}__')
            # Handle attributes for TabItem
            if tag == 'TabItem' and '<TabItem ' in text:
                 # This is tricky with simple replace. Use regex for TabItem with attributes
                 text = re.sub(r'<TabItem\s+([^>]+)>', r'__JSX_TABITEM_ATTRS_START__\1__JSX_TABITEM_ATTRS_END__', text)

        # Special case for [doc_compiling_for_linuxbsd_oneliners](doc_compiling_for_linuxbsd_oneliners)
        # which might be in the text and contains <> in my thought, but wait.
        # Actually, I should just escape ALL < and > and then restore specific ones.
        
        text = text.replace('<', '&lt;').replace('>', '&gt;')

        # Restore placeholders
        for idx, tag in enumerate(known_tags):
            text = text.replace(f'__JSX_TAG_{idx}__', f'<{tag}>')
        
        text = re.sub(r'__JSX_TABITEM_ATTRS_START__(.*)__JSX_TABITEM_ATTRS_END__', r'<TabItem \1>', text)
        
        return text

    while i < len(lines):
        line = lines[i]

        if is_tabs_open:
            # Check if we should close Tabs because next line is not a tab
            is_tab_directive = re.match(r'^\s*\.\. (code-tab|tab|group-tab)::', line)
            
            # If the current line is an empty line, check if the NEXT non-empty line is a tab directive
            if not line.strip():
                next_non_empty = i + 1
                while next_non_empty < len(lines) and not lines[next_non_empty].strip():
                    next_non_empty += 1
                if next_non_empty < len(lines):
                    is_tab_directive = re.match(r'^\s*\.\. (code-tab|tab|group-tab)::', lines[next_non_empty])
                else:
                    is_tab_directive = False
            
            if not is_tab_directive:
                # If we're inside <Tabs> and the next logical content is NOT a tab directive, close it
                # We should only close if we've already emitted at least one TabItem
                if md_lines and (md_lines[-1] == '</TabItem>' or (len(md_lines) > 1 and md_lines[-2] == '</TabItem>')):
                    md_lines.append('')
                    md_lines.append('</Tabs>')
                    md_lines.append('')
                    is_tabs_open = False
                    # Don't continue here, we still need to process the current line

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

        # Handle tabs, code-tabs, and group-tabs
        if line.strip() == '.. tabs::':
            md_lines.append('')
            md_lines.append('<Tabs>')
            md_lines.append('')
            is_tabs_open = True
            i += 1
            continue
        
        match_tab = re.match(r'^\s*\.\. (tab|group-tab)::\s+(.*)', line)
        if match_tab:
            label = match_tab.group(2).strip()
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
                    block.append(lines[i][indent:])
                    i += 1
                md_lines.append('')
                md_lines.append(f'<TabItem value="{value}" label="{label}">')
                md_lines.append('')
                md_lines.append(f'```{lang}')
                md_lines.extend(block)
                md_lines.append('```')
                md_lines.append('')
                md_lines.append('</TabItem>')
                md_lines.append('')
            continue
        

        # Admonitions
        match_admonition = re.match(r'^\s*\.\.\s+(note|warning|seealso|important|tip)::\s*(.*)', line, re.IGNORECASE)
        if match_admonition:
            adm_type = match_admonition.group(1).lower()
            content_on_same_line = match_admonition.group(2).strip()
            if adm_type == 'seealso': adm_type = 'info'
            md_lines.append('')
            md_lines.append(f':::{adm_type}')
            if content_on_same_line:
                md_lines.append(content_on_same_line)
            else:
                md_lines.append('')
            i += 1
            
            # Find the first non-empty line to determine indentation
            next_i = i
            while next_i < len(lines) and not lines[next_i].strip():
                next_i += 1
            
            if next_i < len(lines):
                indent = len(lines[next_i]) - len(lines[next_i].lstrip())
                if indent > 0:
                    i = next_i
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

        # Handle generic code blocks (.. code-block:: and .. code::)
        match_code = re.match(r'^\s*\.\.\s+(?:code-block|code)::\s*(\w+)?', line)
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

        # Handle math blocks (.. math::)
        match_math = re.match(r'^\s*\.\.\s+math::\s*(.*)?', line)
        if match_math:
            content_on_same_line = match_math.group(1).strip()
            i += 1
            # Skip optional labels or other options
            while i < len(lines) and (lines[i].strip().startswith(':') or not lines[i].strip()):
                i += 1
            
            block = []
            if content_on_same_line:
                block.append(content_on_same_line)

            if i < len(lines):
                # Check if the next non-empty line is indented
                if lines[i].strip() and (len(lines[i]) - len(lines[i].lstrip()) > 0):
                    indent = len(lines[i]) - len(lines[i].lstrip())
                    while i < len(lines) and (not lines[i].strip() or (len(lines[i]) - len(lines[i].lstrip()) >= indent)):
                        block.append(lines[i][indent:])
                        i += 1
            
            if block:
                md_lines.append('')
                md_lines.append('$$')
                md_lines.extend(block)
                md_lines.append('$$')
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

        line = apply_inline_replacements(escape_angle_brackets(line))
        
        # Multiline :ref:
        
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

        # Video directive
        match_video = re.match(r'^\.\.\s+video::\s+(.*)', line)
        if match_video:
            video_path = match_video.group(1).strip()
            i += 1
            options = {}
            while i < len(lines):
                if not lines[i].strip():
                    i += 1
                    continue
                match_opt = re.match(r'^\s+:([^:]+):\s*(.*)', lines[i])
                if match_opt:
                    opt_name = match_opt.group(1).strip()
                    opt_val = match_opt.group(2).strip()
                    options[opt_name] = opt_val
                    i += 1
                else:
                    break
            
            # Construct <video> tag
            video_attrs = [f'src="/{video_path}"', 'controls']
            if 'autoplay' in options: video_attrs.append('autoplay')
            if 'loop' in options: video_attrs.append('loop')
            if 'muted' in options: video_attrs.append('muted')
            
            # Add alt as a separate attribute if it exists
            # Note: <video> doesn't have an 'alt' attribute, usually it's used for accessibility
            # but we can include it as a comment or fallback text.
            # Docusaurus/MDX might prefer a specific way, but a standard <video> tag is safe.
            
            attr_str = " ".join(video_attrs)
            md_lines.append('')
            md_lines.append(f'<video {attr_str}>')
            if 'alt' in options:
                md_lines.append(f'  {options["alt"]}')
            md_lines.append('</video>')
            md_lines.append('')
            continue

        # Handle comments (.. )
        match_comment = re.match(r'^\s*\.\.\s+(?![a-zA-Z0-9_-]+::)(.*)', line)
        if match_comment or line.strip() == '..':
            i += 1
            # Check for indented block if it's a multi-line comment
            # BUT only if it wasn't a single line comment with content
            # wait, RST comments can have content on the same line and then more lines indented.
            
            # If the next line is indented, skip it too.
            while i < len(lines):
                if not lines[i].strip():
                    i += 1
                    continue
                
                # Check indentation of the first non-empty line after ".."
                indent = len(lines[i]) - len(lines[i].lstrip())
                if indent > 0:
                    # It's an indented block, skip it all
                    while i < len(lines) and (not lines[i].strip() or (len(lines[i]) - len(lines[i].lstrip()) >= indent)):
                        i += 1
                    break
                else:
                    # Not indented, end of comment
                    break
            continue

        # Handle tables (grid tables)
        if line.strip().startswith('+') and i + 1 < len(lines) and lines[i+1].strip().startswith('|'):
            table_lines = []
            while i < len(lines) and (line.strip().startswith('+') or line.strip().startswith('|')):
                table_lines.append(line.strip())
                i += 1
                if i < len(lines):
                    line = lines[i]
                else:
                    break
            
            if table_lines:
                # Process table_lines to Markdown
                md_table = []
                header_sep_idx = -1
                for idx, tl in enumerate(table_lines):
                    if tl.startswith('+') and '=' in tl:
                        header_sep_idx = idx
                        break
                
                # Extract rows
                rows = []
                current_row = []
                for idx, tl in enumerate(table_lines):
                    if tl.startswith('|'):
                        # Extract cells, handle multiple | 
                        cells = [c.strip() for c in tl.split('|')[1:-1]]
                        if not current_row:
                            current_row = cells
                        else:
                            # Handle multi-line cells by appending
                            for c_idx, cell in enumerate(cells):
                                if c_idx < len(current_row):
                                    if cell:
                                        current_row[c_idx] += " " + cell
                                else:
                                    current_row.append(cell)
                    elif tl.startswith('+'):
                        if current_row:
                            rows.append(current_row)
                            current_row = []
                
                if rows:
                    md_table.append('')
                    # Header
                    header = rows[0]
                    escaped_header = [apply_inline_replacements(escape_angle_brackets(cell)) for cell in header]
                    md_table.append('| ' + ' | '.join(escaped_header) + ' |')
                    # Separator
                    md_table.append('| ' + ' | '.join(['---'] * len(header)) + ' |')
                    # Data rows
                    for r in rows[1:]:
                        escaped_r = [apply_inline_replacements(escape_angle_brackets(cell)) for cell in r]
                        md_table.append('| ' + ' | '.join(escaped_r) + ' |')
                    md_table.append('')
                    md_lines.extend(md_table)
            continue

        md_lines.append(apply_inline_replacements(escape_angle_brackets(line)))
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
