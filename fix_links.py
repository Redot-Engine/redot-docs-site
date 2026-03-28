import os
import re

def main():
    docs_dir = 'docs'
    rst_to_ref = {} # rst_path -> reference_id
    ref_to_md = {}  # reference_id -> md_path

    # Step 1: Enumerate all .rst files and extract reference
    # Assuming each .rst file has a primary reference at the top like ".. _doc_name:"
    ref_pattern = re.compile(r'^\.\.\s+_([a-zA-Z0-9_-]+):')

    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.rst'):
                rst_path = os.path.join(root, file)
                md_path = rst_path[:-4] + '.md'
                
                if not os.path.exists(md_path):
                    # We only care about .rst files that have a corresponding .md file
                    continue

                try:
                    with open(rst_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            match = ref_pattern.match(line.strip())
                            if match:
                                ref_id = match.group(1)
                                # Map the reference ID to the .md file path
                                ref_to_md[ref_id] = md_path
                                # We'll just take the first reference found as the primary one for the file
                                break
                except Exception as e:
                    print(f"Error reading {rst_path}: {e}")

    print(f"Built database with {len(ref_to_md)} references.")

    # Step 2: Go through all .md files and identify links
    # Link format: [text](ref_id)
    # We want to catch links where ref_id is one of our keys in ref_to_md
    # and it doesn't already look like a path (e.g. doesn't have .md or /)
    
    # regex for [text](link)
    # This regex is a bit simple but should work for the requested format
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    for root, dirs, files in os.walk(docs_dir):
        for file in files:
            if file.endswith('.md'):
                md_path = os.path.join(root, file)
                
                try:
                    with open(md_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = content
                    modified = False
                    
                    # Find all matches
                    matches = link_pattern.findall(content)
                    for text, link in matches:
                        if link in ref_to_md:
                            target_md = ref_to_md[link]
                            
                            # Calculate relative path from current md_path to target_md
                            rel_path = os.path.relpath(target_md, root)
                            
                            # Docusaurus usually uses paths without .md or relative paths starting with ./
                            # But standard markdown relative path should work.
                            # Let's see if we should keep .md extension. 
                            # If it was [text](doc_gdscript), and doc_gdscript maps to docs/About/gdscript.md
                            # from docs/About/faq.md, the rel_path would be 'gdscript.md'
                            
                            old_link = f'[{text}]({link})'
                            new_link = f'[{text}]({rel_path})'
                            
                            if old_link in new_content:
                                new_content = new_content.replace(old_link, new_link)
                                modified = True
                                print(f"Updated link in {md_path}: {link} -> {rel_path}")

                    if modified:
                        with open(md_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                            
                except Exception as e:
                    print(f"Error processing {md_path}: {e}")

if __name__ == '__main__':
    main()
