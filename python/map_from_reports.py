#!/usr/bin/env python3
"""
Generate world map visualization from existing report files.
Reads country data from reports/*.txt files.
"""
import argparse
import re
import sys
from pathlib import Path

try:
    import plotly.express as px
    import pandas as pd
except ImportError:
    print("ERROR: Missing dependencies.")
    print("Install: pip install plotly kaleido")
    sys.exit(1)


def parse_country_data(report_file: str) -> pd.DataFrame:
    """Extract country download data from report text file."""
    with open(report_file, 'r') as f:
        content = f.read()
    
    # Find the "Downloads by Country" section
    country_section = re.search(
        r'Downloads by Country.*?\n.*?\n(.*?)(?=╰|$)',
        content,
        re.DOTALL
    )
    
    if not country_section:
        print(f"Could not find country data in {report_file}")
        return pd.DataFrame()
    
    lines = country_section.group(1).strip().split('\n')
    
    countries = []
    downloads = []
    
    for line in lines:
        # Skip empty lines and border lines (╭─┬─╮, ├─┼─┤, ╰─┴─╯)
        if not line.strip():
            continue
        if any(char in line for char in ['╭', '╮', '├', '┤', '╰', '╯', '┬', '┴', '┼']):
            continue
        if '─' in line and '│' not in line:
            continue
        
        # Parse data rows like: "│ US           │ 74,684         │"
        if '│' in line:
            parts = [p.strip() for p in line.split('│') if p.strip()]
            
            if len(parts) >= 2:
                country = parts[0].strip()
                download_str = parts[1].strip().replace(',', '')
                
                # Skip header row
                if country.lower() in ['country', 'country_code', 'country code']:
                    continue
                
                try:
                    download_count = int(download_str)
                    countries.append(country)
                    downloads.append(download_count)
                except ValueError:
                    continue
    
    if not countries:
        print(f"No country data parsed from {report_file}")
        return pd.DataFrame()
    
    df = pd.DataFrame({
        'country_code': countries,
        'download_count': downloads
    })
    
    # Convert 2-letter codes to 3-letter ISO codes
    df['iso_alpha'] = df['country_code'].apply(convert_to_iso3)
    
    return df


def convert_to_iso3(code2: str) -> str:
    """Convert 2-letter country code to 3-letter ISO code."""
    mapping = {
        'US': 'USA', 'GB': 'GBR', 'DE': 'DEU', 'FR': 'FRA', 'CA': 'CAN',
        'AU': 'AUS', 'JP': 'JPN', 'CN': 'CHN', 'IN': 'IND', 'BR': 'BRA',
        'RU': 'RUS', 'IT': 'ITA', 'ES': 'ESP', 'NL': 'NLD', 'SE': 'SWE',
        'CH': 'CHE', 'PL': 'POL', 'BE': 'BEL', 'AT': 'AUT', 'NO': 'NOR',
        'DK': 'DNK', 'FI': 'FIN', 'IE': 'IRL', 'PT': 'PRT', 'CZ': 'CZE',
        'GR': 'GRC', 'HU': 'HUN', 'RO': 'ROU', 'NZ': 'NZL', 'SG': 'SGP',
        'HK': 'HKG', 'KR': 'KOR', 'TW': 'TWN', 'ZA': 'ZAF', 'MX': 'MEX',
        'AR': 'ARG', 'CL': 'CHL', 'CO': 'COL', 'IL': 'ISR', 'TR': 'TUR',
        'UA': 'UKR', 'TH': 'THA', 'MY': 'MYS', 'ID': 'IDN', 'PH': 'PHL',
        'VN': 'VNM', 'PK': 'PAK', 'BD': 'BGD', 'EG': 'EGY', 'NG': 'NGA',
        'KE': 'KEN', 'SA': 'SAU', 'AE': 'ARE', 'QA': 'QAT', 'KW': 'KWT',
    }
    return mapping.get(code2, code2)


def create_map(df: pd.DataFrame, title: str, output_file: str):
    """Create choropleth map visualization with vibrant colors."""
    if df.empty:
        print("No data to visualize!")
        return
    
    print(f"Creating map with {len(df)} countries")
    print(f"Total downloads: {df['download_count'].sum():,}")
    
    # Use YlOrRd (Yellow-Orange-Red) - bright, no dark colors
    # Goes from light yellow -> orange -> bright red
    fig = px.choropleth(
        df,
        locations='iso_alpha',
        color='download_count',
        hover_name='country_code',
        hover_data={'iso_alpha': False, 'download_count': ':,'},
        color_continuous_scale='YlOrRd',  # Yellow-Orange-Red, no dark colors
        title=title,
        labels={'download_count': 'Downloads'},
    )
    
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth',
            bgcolor='rgba(240,240,240,1)'  # Light gray background
        ),
        height=700,
        font=dict(size=14),
        paper_bgcolor='white',
    )
    
    # Save as HTML (interactive)
    html_file = output_file.replace('.png', '.html')
    fig.write_html(html_file)
    print(f"✓ Interactive map saved: {html_file}")
    
    # Try to save as PNG
    try:
        fig.write_image(output_file, width=1600, height=900)
        print(f"✓ Static map saved: {output_file}")
    except Exception as e:
        print(f"Note: Could not save PNG (install kaleido: pip install kaleido)")


def main():
    parser = argparse.ArgumentParser(
        description="Generate world map from report files"
    )
    parser.add_argument("--report-dir", default="reports", help="Reports directory")
    parser.add_argument("--days", type=int, choices=[30, 90], required=True,
                        help="Which report to use (30 or 90 days)")
    
    args = parser.parse_args()
    
    # Find the most recent report file for the specified days
    report_dir = Path(args.report_dir)
    if not report_dir.exists():
        print(f"ERROR: Report directory not found: {report_dir}")
        print("Run 'make reports' first to generate reports")
        sys.exit(1)
    
    pattern = f"*.trestle.pypi.last-{args.days}.txt"
    report_files = sorted(report_dir.glob(pattern), reverse=True)
    
    if not report_files:
        print(f"ERROR: No report files found matching: {pattern}")
        print(f"Run 'make report-last-{args.days}' first")
        sys.exit(1)
    
    report_file = report_files[0]
    print(f"Reading data from: {report_file}")
    
    # Parse country data
    df = parse_country_data(str(report_file))
    
    if df.empty:
        print("No data to visualize!")
        sys.exit(1)
    
    # Create output filename
    date_part = report_file.stem.split('.')[0:3]  # YYYY.MM.DD
    output_base = report_dir / f"{'.'.join(date_part)}.trestle.pypi.map-{args.days}"
    output_file = f"{output_base}.png"
    
    # Create map
    title = f"PyPI Downloads: compliance-trestle (Last {args.days} Days)"
    create_map(df, title, output_file)
    print("\nDone!")


if __name__ == "__main__":
    main()

# Made with Bob
