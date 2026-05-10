#!/usr/bin/env python3
"""
Generate a world map visualization of PyPI downloads by country.
"""
import argparse
import os
import sys

try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    import plotly.express as px
    import pandas as pd
except ImportError:
    print("ERROR: Missing dependencies.")
    print("Install: pip install plotly pandas kaleido")
    sys.exit(1)


def make_client(project: str, credentials_path: str) -> bigquery.Client:
    """Create BigQuery client."""
    creds = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=["https://www.googleapis.com/auth/bigquery"],
    )
    return bigquery.Client(project=project, credentials=creds)


def query_country_downloads(client: bigquery.Client, package: str, days: int) -> pd.DataFrame:
    """Query download counts by country."""
    sql = f"""
    SELECT
        country_code,
        COUNT(*) AS download_count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
      AND country_code IS NOT NULL
    GROUP BY country_code
    ORDER BY download_count DESC
    """
    
    print(f"Querying downloads by country for {package} (last {days} days)...")
    job = client.query(sql)
    rows = list(job.result())
    
    if not rows:
        print("No data returned!")
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame([dict(row) for row in rows])
    
    # Convert 2-letter codes to 3-letter ISO codes for plotly
    # Plotly uses ISO 3166-1 alpha-3 codes
    df['iso_alpha'] = df['country_code'].apply(convert_to_iso3)
    
    print(f"Found data for {len(df)} countries")
    print(f"Total downloads: {df['download_count'].sum():,}")
    
    return df


def convert_to_iso3(code2: str) -> str:
    """Convert 2-letter country code to 3-letter ISO code."""
    # Common mappings (add more as needed)
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


def create_map(df: pd.DataFrame, package: str, days: int, output_file: str):
    """Create choropleth map visualization."""
    if df.empty:
        print("No data to visualize!")
        return
    
    fig = px.choropleth(
        df,
        locations='iso_alpha',
        color='download_count',
        hover_name='country_code',
        hover_data={'iso_alpha': False, 'download_count': ':,'},
        color_continuous_scale='Blues',
        title=f'PyPI Downloads: {package} (Last {days} Days)',
        labels={'download_count': 'Downloads'},
    )
    
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth'
        ),
        height=600,
        font=dict(size=14),
    )
    
    # Save as HTML (interactive)
    html_file = output_file.replace('.png', '.html')
    fig.write_html(html_file)
    print(f"✓ Interactive map saved: {html_file}")
    
    # Try to save as PNG (requires kaleido)
    try:
        fig.write_image(output_file, width=1400, height=700)
        print(f"✓ Static map saved: {output_file}")
    except Exception as e:
        print(f"Note: Could not save PNG (install kaleido for PNG export)")
        print(f"  pip install kaleido")


def main():
    parser = argparse.ArgumentParser(
        description="Generate world map of PyPI downloads by country"
    )
    parser.add_argument("--package", required=True, help="PyPI package name")
    parser.add_argument("--days", type=int, default=30, help="Days to look back")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--credentials", required=True, help="Service account JSON")
    parser.add_argument("--output", default="downloads_map.png", help="Output filename")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.credentials):
        print(f"ERROR: Credentials file not found: {args.credentials}")
        sys.exit(1)
    
    # Query data
    client = make_client(args.project, args.credentials)
    df = query_country_downloads(client, args.package, args.days)
    
    if df.empty:
        print("No data to visualize!")
        sys.exit(1)
    
    # Create map
    create_map(df, args.package, args.days, args.output)
    print("\nDone!")


if __name__ == "__main__":
    main()

# Made with Bob
