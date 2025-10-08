#!/usr/bin/env python3
"""
Fix malformed image references in Hugo posts
"""
import os
import re
import glob

def fix_malformed_images():
    """Fix malformed image references in all markdown files"""
    
    # Get all markdown files in content/posts
    md_files = glob.glob("content/posts/*.md")
    
    for file_path in md_files:
        print(f"Processing {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix malformed image references
        # Pattern: ![](/images/\1"some text"
        content = re.sub(r'!\[\]\(/images/\\1"[^"]*"', '', content)
        
        # Pattern: ![](/images/\1"some text" with more text
        content = re.sub(r'!\[\]\(/images/\\1"[^"]*"[^)]*\)', '', content)
        
        # Clean up any remaining malformed references
        content = re.sub(r'!\[\]\(/images/\\1[^)]*\)', '', content)
        content = re.sub(r'!\[\]\(/images/\\2[^)]*\)', '', content)
        
        # Clean up WordPress shortcode artifacts
        content = re.sub(r'<pre class="wp-block-preformatted[^"]*">', '```', content)
        content = re.sub(r'</pre>', '```', content)
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed {file_path}")

if __name__ == "__main__":
    fix_malformed_images()
    print("Image fixing complete!")
