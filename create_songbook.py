#!/usr/bin/env python3
"""
Campfire Songbook Generator

Creates a professional campfire songbook PDF with:
- Cover page from static/coverpage.pdf
- Table of contents/index
- Each song on a new page
- Proper formatting and organization
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['weasyprint', 'PyPDF2', 'markdown']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('pypdf2', 'PyPDF2'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Installing missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
        print("✓ Dependencies installed")

def extract_song_title(file_path):
    """Extract song title from markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for first heading
        heading_match = re.search(r'^#\s*(.+)$', content, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()
        
        # Fallback to filename without extension
        return file_path.stem.replace('_', ' ').replace('-', ' ').title()
    
    except Exception as e:
        print(f"Warning: Could not extract title from {file_path}: {e}")
        return file_path.stem.replace('_', ' ').replace('-', ' ').title()

def get_song_files():
    """Get all song markdown files, organized by category"""
    song_files = []
    
    # Define song categories based on your file structure
    categories = {
        'Action Songs': [
            'heads_shoulders.md', 'one_finger_one_thumb.md', 'lean_forwards,_lean_backwards.md'
        ],
        'Animal Songs': [
            'alice.md', 'animal_fair.md', 'bearhunt.md', 'bingo.md', 'bumblebee.md',
            'flea_fly.md', 'jellyfish.md', 'kookabura.md', 'penguin.md', 'tarzan.md',
            'the_shark_song.md', 'three_little_bees_in_the_garden.md', 'zombie.md'
        ],
        'Traditional Songs': [
            'angels.md', 'kumbyya.md', 'sweet_chariot.md', 'singing_in_the_rain.md',
            'campfiresburning.md', 'rule_britania.md'
        ],
        'Fun Songs': [
            'an_austrian_went_yodelling.md', 'bannana.md', 'bung_it_through_the_window.md',
            'bungalow.md', 'fred.md', 'ging_gang_gooli.md', 'he_aint_gona_jump_no_more.md',
            'international_car_song.md', 'irishsea.md', 'isawabird.md', 'joe.md',
            'mexican_canoe_song.md', 'mow.md', 'my-poor-meatball.md', 'oh_youll_never_get_to_heaven.md',
            'pizza_hut.md', 'pushbike.md', 'runners.md', 'swimmingpool.md', 'what_is_that_thing.md'
        ],
           }
    
    # Collect songs by category
    categorized_songs = {}
    used_files = set()
    
    for category, filenames in categories.items():
        category_songs = []
        for filename in filenames:
            file_path = Path(filename)
            if file_path.exists():
                title = extract_song_title(file_path)
                category_songs.append((title, file_path))
                used_files.add(filename)
        
        if category_songs:
            categorized_songs[category] = category_songs
    
    # Add any remaining .md files that weren't categorized
    remaining_songs = []
    for md_file in Path('.').glob('*.md'):
        if (md_file.name not in used_files and 
            md_file.name not in ['README.md', 'SUMMARY.md', 'combined.md'] and
            'venv' not in str(md_file)):
            title = extract_song_title(md_file)
            remaining_songs.append((title, md_file))
    
    if remaining_songs:
        categorized_songs['Additional Songs'] = remaining_songs
    
    return categorized_songs

def create_songbook_html(categorized_songs):
    """Create HTML content for the songbook"""
    # Import markdown here to ensure it's available when needed
    import markdown
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Campfire Songbook</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
            @bottom-center {{
                content: counter(page);
                font-family: Arial, sans-serif;
                font-size: 10pt;
            }}
        }}
        
        body {{
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            color: #333;
        }}
        
        .page-break {{
            page-break-before: always;
        }}
        
        .toc {{
            page-break-after: always;
        }}
        
        .toc h1 {{
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 2em;
            color: #8B4513;
            border-bottom: 3px solid #8B4513;
            padding-bottom: 0.5em;
        }}
        
        .toc-category {{
            margin: 1.5em 0;
        }}
        
        .toc-category h2 {{
            color: #D2691E;
            font-size: 1.3em;
            margin-bottom: 0.5em;
            border-left: 4px solid #D2691E;
            padding-left: 10px;
        }}
        
        .toc-songs {{
            margin-left: 20px;
        }}
        
        .toc-song {{
            margin: 0.3em 0;
            font-size: 1.1em;
        }}
        
        .song {{
            page-break-before: always;
            min-height: 80vh;
        }}
        
        .song h1 {{
            color: #8B4513;
            font-size: 2.2em;
            text-align: center;
            margin-bottom: 1.5em;
            border-bottom: 2px solid #D2691E;
            padding-bottom: 0.5em;
        }}
        
        .song-content {{
            font-size: 1.2em;
            line-height: 1.4;
        }}
        
        .song-content p {{
            margin: 0.5em 0;
            line-height: 1.5;
        }}
        
        .song-content br {{
            line-height: 1.2;
        }}
        
        /* Better formatting for lists within songs */
        .song-content ul {{
            margin: 0.6em 0;
            padding-left: 1.5em;
        }}
        
        .song-content li {{
            margin: 0.1em 0;
            line-height: 1.3;
        }}
        
        /* Ensure proper spacing between verses and lists */
        .song-content p + ul {{
            margin-top: 0.3em;
        }}
        
        .song-content strong {{
            font-weight: bold;
            color: #8B4513;
        }}
        
        .song-content em {{
            font-style: italic;
            color: #D2691E;
        }}
        
        .song-content ul, .song-content ol {{
            margin: 1em 0;
            padding-left: 2em;
        }}
        
        .song-content blockquote {{
            border-left: 4px solid #D2691E;
            margin: 1em 0;
            padding-left: 1em;
            font-style: italic;
            color: #666;
        }}
        
        .category-divider {{
            page-break-before: always;
            text-align: center;
            padding: 3em 0;
        }}
        
        .category-divider h1 {{
            font-size: 3em;
            color: #8B4513;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 3px;
        }}
        
        .intro {{
            text-align: center;
            font-style: italic;
            color: #666;
            margin: 2em 0;
            font-size: 1.1em;
        }}
    </style>
</head>
<body>
"""
    
    # Table of Contents
    html_content += """
    <div class="toc">
        <h1>🔥 Campfire Songbook 🔥</h1>
        <div class="intro">
            A collection of songs for campfires, gatherings, and good times<br>
            <em>Generated on """ + datetime.now().strftime("%B %d, %Y") + """</em>
        </div>
"""
    
    for category, songs in categorized_songs.items():
        html_content += f"""
        <div class="toc-category">
            <h2>{category}</h2>
            <div class="toc-songs">
"""
        for title, _ in songs:
            html_content += f'                <div class="toc-song">• {title}</div>\n'
        
        html_content += """
            </div>
        </div>
"""
    
    html_content += "    </div>\n"
    
    # Songs content
    for category, songs in categorized_songs.items():
        # Category divider page
        html_content += f"""
    <div class="category-divider">
        <h1>{category}</h1>
    </div>
"""
        
        # Songs in this category
        for title, file_path in songs:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remove the first heading if it exists (we'll use our own)
                content = re.sub(r'^#\s*.*\n', '', content, count=1)
                
                # Process backslash line breaks first
                content = re.sub(r'\s*\\\s*$', '<br>', content, flags=re.MULTILINE)
                
                # Remove "_Additional Verses_" text that interferes with list formatting
                content = re.sub(r'_Additional Verses_\s*\n', '\n**Animals:**\n', content)
                
                # Handle the "With a<br>" pattern - ensure proper list formatting
                content = re.sub(r'With a<br>\s*\n(-\s*.*?)\n\n', r'With a:\n\n\1\n\n', content, flags=re.MULTILINE | re.DOTALL)
                
                # Convert markdown to HTML using proper markdown library
                md = markdown.Markdown(extensions=[
                    'extra',      # Enable extra features (tables, footnotes, etc.)
                    'smarty'      # Smart quotes and dashes
                ])
                html_content_converted = md.convert(content)
                
                html_content += f"""
    <div class="song">
        <h1>{title}</h1>
        <div class="song-content">{html_content_converted}</div>
    </div>
"""
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")
    
    html_content += """
</body>
</html>
"""
    return html_content

def create_songbook_pdf():
    """Create the campfire songbook PDF"""
    print("🔥 Creating Campfire Songbook...")
    
    # Check dependencies
    check_dependencies()
    
    # Import after installation
    try:
        import weasyprint
        from PyPDF2 import PdfWriter, PdfReader
        import markdown
    except ImportError as e:
        print(f"❌ Error importing dependencies: {e}")
        return
    
    # Get organized song files
    print("📚 Organizing songs...")
    categorized_songs = get_song_files()
    
    total_songs = sum(len(songs) for songs in categorized_songs.values())
    print(f"Found {total_songs} songs in {len(categorized_songs)} categories")
    
    # Create HTML content
    print("📝 Generating songbook content...")
    html_content = create_songbook_html(categorized_songs)
    
    # Save HTML for debugging
    with open('songbook_temp.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Convert HTML to PDF
    print("🔄 Converting to PDF...")
    try:
        # Create main content PDF
        html_pdf = weasyprint.HTML(string=html_content)
        main_pdf_path = 'songbook_main.pdf'
        html_pdf.write_pdf(main_pdf_path)
        
        # Combine with cover page if it exists
        cover_path = Path('static/coverpage.pdf')
        final_pdf_path = 'CampfireSongbook.pdf'
        
        if cover_path.exists():
            print("📄 Adding cover page...")
            pdf_writer = PdfWriter()
            
            # Add cover page
            with open(cover_path, 'rb') as cover_file:
                cover_reader = PdfReader(cover_file)
                for page in cover_reader.pages:
                    pdf_writer.add_page(page)
            
            # Add main content
            with open(main_pdf_path, 'rb') as main_file:
                main_reader = PdfReader(main_file)
                for page in main_reader.pages:
                    pdf_writer.add_page(page)
            
            # Write final PDF
            with open(final_pdf_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            # Clean up temporary files
            os.remove(main_pdf_path)
        else:
            # No cover page, just rename the main PDF
            os.rename(main_pdf_path, final_pdf_path)
            print("⚠️  No cover page found at static/coverpage.pdf")
        
        # Clean up temporary HTML
        os.remove('songbook_temp.html')
        
        # Show results
        file_size = Path(final_pdf_path).stat().st_size
        print(f"✅ Songbook created successfully!")
        print(f"📖 File: {final_pdf_path}")
        print(f"📏 Size: {file_size:,} bytes")
        print(f"🎵 Contains {total_songs} songs in {len(categorized_songs)} categories")
        
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        print("Make sure you have the required dependencies installed:")
        print("  pip install weasyprint PyPDF2")

def main():
    """Main function"""
    try:
        create_songbook_pdf()
    except KeyboardInterrupt:
        print("\n❌ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()