#!/usr/bin/env python3
"""Debug script to test Old MacDonald formatting"""

import re
import markdown

# Read the Old MacDonald file
with open('Old Macdonald.md', 'r') as f:
    content = f.read()

print("=== ORIGINAL CONTENT ===")
print(repr(content))

# Remove heading
content = re.sub(r'^#\s*.*\n', '', content, count=1)
print("\n=== AFTER HEADING REMOVAL ===")
print(repr(content))

# Process backslashes first
content = re.sub(r'\s*\\\s*$', '<br>', content, flags=re.MULTILINE)
print("\n=== AFTER BACKSLASH PROCESSING ===")
print(repr(content))

# Handle the "With a<br>" pattern - ensure proper list formatting
content = re.sub(r'With a<br>\s*\n(-\s*.*)', r'With a:\n\n\1', content, flags=re.MULTILINE | re.DOTALL)
print("\n=== AFTER WITH A PATTERN ===")
print(repr(content))

# Remove "_Additional Verses_" text
content = re.sub(r'_Additional Verses_\s*\n', '', content)
print("\n=== AFTER REMOVING ADDITIONAL VERSES ===")
print(repr(content))
print("\n=== AFTER BACKSLASH PROCESSING ===")
print(repr(content))

# Clean up
content = re.sub(r'<br>\s*<br>', '<br>', content)
print("\n=== AFTER CLEANUP ===")
print(repr(content))

# Convert with markdown
md = markdown.Markdown(extensions=['extra', 'smarty'])
html_result = md.convert(content)
print("\n=== FINAL HTML ===")
print(html_result)