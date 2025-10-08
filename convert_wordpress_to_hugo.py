#!/usr/bin/env python3
"""
WordPress to Hugo Converter
Converts WordPress XML export to Hugo Markdown posts
"""

import xml.etree.ElementTree as ET
import re
import os
import shutil
from datetime import datetime
from pathlib import Path
import html

def clean_html_content(html_content):
    """Clean and convert HTML content to Markdown-friendly format"""
    if not html_content:
        return ""
    
    # Decode HTML entities
    content = html.unescape(html_content)
    
    # Remove WordPress-specific shortcodes and blocks
    content = re.sub(r'<!-- wp:[^>]*-->', '', content)
    content = re.sub(r'<!-- /wp:[^>]*-->', '', content)
    content = re.sub(r'<!--more-->', '', content)
    
    # Convert WordPress image blocks to Markdown - handle complex cases
    content = re.sub(r'<figure[^>]*class="wp-block-image[^"]*"[^>]*>.*?<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*/?>.*?<figcaption>(.*?)</figcaption>.*?</figure>', 
                     r'![\2](\1)\n*\3*', content, flags=re.DOTALL)
    
    # Convert WordPress image blocks without captions
    content = re.sub(r'<figure[^>]*class="wp-block-image[^"]*"[^>]*>.*?<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*/?>.*?</figure>', 
                     r'![\2](\1)', content, flags=re.DOTALL)
    
    # Convert regular img tags to Markdown
    content = re.sub(r'<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*/?>', r'![\2](\1)', content)
    
    # Handle WordPress attachment shortcodes and malformed content
    content = re.sub(r'\[caption[^\]]*\].*?<img[^>]*src="([^"]*)"[^>]*alt="([^"]*)"[^>]*/?>.*?\[/caption\]', 
                     r'![\2](\1)', content, flags=re.DOTALL)
    
    # Clean up any remaining malformed image references
    content = re.sub(r'!\[\]\(/images/\\1[^)]*\)', '', content)
    content = re.sub(r'!\[\]\(/images/\\2[^)]*\)', '', content)
    
    # Handle the specific malformed WordPress content we're seeing
    content = re.sub(r'\[caption[^\]]*\]!\[\]\(/images/\\1[^)]*\)\[/caption\]', '', content)
    content = re.sub(r'!\[\]\(/images/\\1[^)]*\)', '', content)
    
    # Clean up any remaining WordPress shortcode artifacts
    content = re.sub(r'\[caption[^\]]*\].*?\[/caption\]', '', content, flags=re.DOTALL)
    
    # Convert code blocks
    content = re.sub(r'<pre[^>]*class="wp-block-code"[^>]*><code>(.*?)</code></pre>', 
                     r'```\n\1\n```', content, flags=re.DOTALL)
    
    # Convert inline code
    content = re.sub(r'<code>(.*?)</code>', r'`\1`', content)
    
    # Convert links
    content = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', r'[\2](\1)', content)
    
    # Convert paragraphs
    content = re.sub(r'<p>(.*?)</p>', r'\1\n\n', content, flags=re.DOTALL)
    
    # Convert headings
    for i in range(1, 7):
        content = re.sub(f'<h{i}[^>]*>(.*?)</h{i}>', f'{"#" * i} \1', content, flags=re.DOTALL)
    
    # Convert lists
    content = re.sub(r'<ul>(.*?)</ul>', r'\1', content, flags=re.DOTALL)
    content = re.sub(r'<ol>(.*?)</ol>', r'\1', content, flags=re.DOTALL)
    content = re.sub(r'<li>(.*?)</li>', r'- \1', content, flags=re.DOTALL)
    
    # Convert strong/bold
    content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', content)
    content = re.sub(r'<b>(.*?)</b>', r'**\1**', content)
    
    # Convert emphasis/italic
    content = re.sub(r'<em>(.*?)</em>', r'*\1*', content)
    content = re.sub(r'<i>(.*?)</i>', r'*\1*', content)
    
    # Convert line breaks
    content = re.sub(r'<br\s*/?>', '\n', content)
    
    # Clean up extra whitespace
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    content = content.strip()
    
    return content

def convert_image_urls(content, base_url="https://malfind.com"):
    """Convert WordPress image URLs to local Hugo static paths"""
    # Convert WordPress upload URLs to local static paths
    content = re.sub(
        r'https?://malfind\.com/wp-content/uploads/([^"]*)',
        r'/images/\\1',
        content
    )
    return content

def create_hugo_post(post_data, output_dir):
    """Create a Hugo Markdown post from WordPress post data"""
    
    # Extract post information
    title = post_data.get('title', 'Untitled')
    content = post_data.get('content', '')
    date = post_data.get('date', '')
    slug = post_data.get('slug', '')
    categories = post_data.get('categories', [])
    tags = post_data.get('tags', [])
    
    # Clean and convert content
    clean_content = clean_html_content(content)
    clean_content = convert_image_urls(clean_content)
    
    # Create Hugo front matter
    front_matter = f"""---
title: "{title}"
date: {date}
draft: false
"""
    
    if categories:
        front_matter += f"categories: {categories}\n"
    
    if tags:
        front_matter += f"tags: {tags}\n"
    
    front_matter += "---\n\n"
    
    # Create the full post content
    post_content = front_matter + clean_content
    
    # Create output file
    filename = f"{date[:10]}-{slug}.md"
    output_path = os.path.join(output_dir, filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(post_content)
    
    print(f"Created: {filename}")
    return filename

def parse_wordpress_xml(xml_file):
    """Parse WordPress XML export and extract blog posts"""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    posts = []
    
    # Find all items with post_type="post"
    for item in root.findall('.//item'):
        post_type = item.find('wp:post_type', {'wp': 'http://wordpress.org/export/1.2/'})
        if post_type is not None and post_type.text == 'post':
            # Extract post data
            title_elem = item.find('title')
            title = title_elem.text if title_elem is not None else 'Untitled'
            
            content_elem = item.find('content:encoded', {'content': 'http://purl.org/rss/1.0/modules/content/'})
            content = content_elem.text if content_elem is not None else ''
            
            date_elem = item.find('wp:post_date', {'wp': 'http://wordpress.org/export/1.2/'})
            date = date_elem.text if date_elem is not None else ''
            
            slug_elem = item.find('wp:post_name', {'wp': 'http://wordpress.org/export/1.2/'})
            slug = slug_elem.text if slug_elem is not None else ''
            
            # Extract categories
            categories = []
            for category in item.findall('category[@domain="category"]'):
                if category.text:
                    categories.append(category.text)
            
            # Extract tags
            tags = []
            for tag in item.findall('category[@domain="post_tag"]'):
                if tag.text:
                    tags.append(tag.text)
            
            post_data = {
                'title': title,
                'content': content,
                'date': date,
                'slug': slug,
                'categories': categories,
                'tags': tags
            }
            
            posts.append(post_data)
    
    return posts

def copy_images(wordpress_uploads_dir, hugo_static_dir):
    """Copy images from WordPress uploads to Hugo static directory"""
    if not os.path.exists(wordpress_uploads_dir):
        print(f"WordPress uploads directory not found: {wordpress_uploads_dir}")
        return
    
    # Create images directory in Hugo static
    images_dir = os.path.join(hugo_static_dir, 'images')
    os.makedirs(images_dir, exist_ok=True)
    
    # Copy all files from WordPress uploads
    for root, dirs, files in os.walk(wordpress_uploads_dir):
        for file in files:
            src_path = os.path.join(root, file)
            # Calculate relative path from uploads directory
            rel_path = os.path.relpath(src_path, wordpress_uploads_dir)
            dst_path = os.path.join(images_dir, rel_path)
            
            # Create destination directory if needed
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            
            # Copy file
            shutil.copy2(src_path, dst_path)
            print(f"Copied: {rel_path}")

def main():
    # Configuration
    xml_file = r"e:\Documents\wordpress-backup\malfind.WordPress.2024-05-12.xml"
    wordpress_uploads_dir = r"E:\Documents\backup\wordpress\html\wordpress\wp-content\uploads"
    hugo_content_dir = r"C:\Users\Lasq\Documents\code\malfind.com\content\posts"
    hugo_static_dir = r"C:\Users\Lasq\Documents\code\malfind.com\static"
    
    # Create output directory
    os.makedirs(hugo_content_dir, exist_ok=True)
    
    print("Parsing WordPress XML...")
    posts = parse_wordpress_xml(xml_file)
    print(f"Found {len(posts)} blog posts")
    
    print("\nConverting posts to Hugo Markdown...")
    for post in posts:
        create_hugo_post(post, hugo_content_dir)
    
    print("\nCopying images...")
    copy_images(wordpress_uploads_dir, hugo_static_dir)
    
    print("\nConversion complete!")
    print(f"Posts saved to: {hugo_content_dir}")
    print(f"Images saved to: {hugo_static_dir}/images")

if __name__ == "__main__":
    main()

