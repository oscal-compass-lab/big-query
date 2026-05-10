#!/usr/bin/env python3
"""Convert query output to Markdown format."""
import sys
import re
from datetime import datetime

def convert_to_markdown(text):
    """Convert terminal output to Markdown."""
    lines = text.split('\n')
    md_lines = []
    
    # Add header
    md_lines.append(f"# PyPI Download Analytics Report")
    md_lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    in_table = False
    table_headers = []
    table_rows = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Remove ANSI color codes
        line = re.sub(r'\x1b\[[0-9;]*m', '', line)
        
        # Skip empty lines when not in table
        if not line.strip() and not in_table:
            i += 1
            continue
        
        # Detect section headers (lines with >>> or ━━━)
        if line.strip().startswith('>>>'):
            if in_table:
                # Finish previous table
                md_lines.extend(format_table(table_headers, table_rows))
                md_lines.append('')
                in_table = False
                table_headers = []
                table_rows = []
            
            header = line.replace('>>>', '').strip()
            md_lines.append(f"\n## {header}\n")
            i += 1
            continue
        
        # Skip separator lines
        if all(c in '═━─┼├┤│┃╋' or c.isspace() for c in line) and line.strip():
            i += 1
            continue
        
        # Detect table lines (contain │ or multiple spaces between words)
        if '│' in line or (line.strip() and '  ' in line and not line.strip().startswith('#')):
            # Clean up the line
            line = line.replace('│', '|').replace('┃', '|')
            
            # Split by | or multiple spaces
            if '|' in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
            else:
                # Split by multiple spaces (2 or more)
                parts = [p.strip() for p in re.split(r'\s{2,}', line.strip()) if p.strip()]
            
            if parts:
                if not in_table:
                    # First row is headers
                    table_headers = parts
                    in_table = True
                else:
                    # Data row
                    table_rows.append(parts)
        else:
            # Not a table line
            if in_table:
                # Finish the table
                md_lines.extend(format_table(table_headers, table_rows))
                md_lines.append('')
                in_table = False
                table_headers = []
                table_rows = []
            
            # Regular text line
            if line.strip():
                md_lines.append(line.strip())
        
        i += 1
    
    # Finish any remaining table
    if in_table and table_headers:
        md_lines.extend(format_table(table_headers, table_rows))
    
    return '\n'.join(md_lines)

def format_table(headers, rows):
    """Format headers and rows as a markdown table."""
    if not headers:
        return []
    
    table_lines = []
    
    # Header row
    table_lines.append('| ' + ' | '.join(headers) + ' |')
    
    # Separator row
    table_lines.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
    
    # Data rows
    for row in rows:
        # Pad row to match header length
        while len(row) < len(headers):
            row.append('')
        # Truncate if too long
        row = row[:len(headers)]
        table_lines.append('| ' + ' | '.join(row) + ' |')
    
    return table_lines

if __name__ == '__main__':
    text = sys.stdin.read()
    print(convert_to_markdown(text))

# Made with Bob
