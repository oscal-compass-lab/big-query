#!/usr/bin/env python3
"""
PyPI BigQuery Analytics Generator with Daily Caching
====================================================
Fetches PyPI download data from BigQuery and generates analytics reports.
Implements daily caching to avoid redundant BigQuery queries.

Usage:
    python generate_analytics.py --package PACKAGE_NAME --days 30 --project GCP_PROJECT_ID
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import pandas as pd
    import pycountry
    import flag
except ImportError:
    print("ERROR: Missing dependencies. Install with:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def make_client(project: str, credentials_path: str | None = None) -> bigquery.Client:
    """Create BigQuery client with optional credentials file."""
    if credentials_path:
        creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/bigquery"],
        )
        return bigquery.Client(project=project, credentials=creds)
    return bigquery.Client(project=project)


def get_cache_path(package: str, days: int | str) -> Path:
    """Get cache file path for today's data."""
    cache_dir = Path(".cache")
    cache_dir.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    return cache_dir / f"{package}_{days}day_{today}.parquet"


def load_cached_data(package: str, days: int | str) -> pd.DataFrame | None:
    """Load cached data if it exists for today."""
    cache_path = get_cache_path(package, days)
    if cache_path.exists():
        print(f"✓ Using cached data from: {cache_path}")
        return pd.read_parquet(cache_path)
    return None


def save_cached_data(df: pd.DataFrame, package: str, days: int | str):
    """Save data to cache."""
    cache_path = get_cache_path(package, days)
    df.to_parquet(cache_path, index=False)
    print(f"✓ Cached data saved to: {cache_path}")


def cleanup_old_cache(package: str, days: int | str):
    """Remove old cache files for this specific package/days combo AFTER successful new fetch."""
    cache_dir = Path(".cache")
    if not cache_dir.exists():
        return
    
    today = datetime.now().date()
    removed_count = 0
    
    # Only remove cache files for this specific package/days combination
    pattern = f"{package}_{days}day_*.parquet"
    for filepath in cache_dir.glob(pattern):
        # Get the date from filename
        try:
            date_str = filepath.stem.split('_')[-1]  # Extract YYYY-MM-DD
            file_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Remove if file is from a previous day
            if file_date < today:
                filepath.unlink()
                removed_count += 1
        except Exception as e:
            print(f"Warning: Could not process cache file {filepath}: {e}")
    
    if removed_count > 0:
        print(f"✓ Cleaned up {removed_count} old cache file(s)")


def get_cache_date(package: str, days: int | str) -> str:
    """Get the date of the current cache file, if it exists."""
    cache_path = get_cache_path(package, days)
    if cache_path.exists():
        # Extract date from filename: package_30day_YYYY-MM-DD.parquet
        return cache_path.stem.split('_')[-1]
    return datetime.now().strftime("%Y-%m-%d")


def query_all_data(client: bigquery.Client, package: str, days: int, use_cache: bool = True) -> tuple[pd.DataFrame, str]:
    """Single comprehensive query to get all data needed. Uses cache if available.
    Returns: (dataframe, cache_date_string)
    """
    
    # Try to load from cache first
    if use_cache:
        cached_df = load_cached_data(package, days)
        if cached_df is not None:
            cache_date = get_cache_date(package, days)
            print(f"✓ Loaded {len(cached_df):,} rows from cache (data from {cache_date})\n")
            return cached_df, cache_date
    
    print(f"\n{'='*70}")
    print(f"Querying BigQuery: {package} (last {days} days)")
    print(f"{'='*70}\n")
    
    sql = f"""
    SELECT
      DATE(timestamp) as date,
      country_code,
      details.system.name AS os,
      details.distro.name AS distro,
      details.distro.libc.lib AS libc,
      details.cpu AS cpu_arch,
      details.ci AS is_ci,
      details.installer.name AS installer,
      details.installer.subcommand AS subcommand,
      REGEXP_EXTRACT(details.python, r'^(\\d+\\.\\d+)') AS python_version,
      file.version as package_version,
      COUNT(*) as downloads
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY) AND CURRENT_DATE()
    GROUP BY date, country_code, os, distro, libc, cpu_arch, is_ci, installer, subcommand, python_version, package_version
    """
    
    job = client.query(sql)
    df = job.result().to_dataframe()
    
    mb = job.total_bytes_processed / 1_000_000 if job.total_bytes_processed else 0
    print(f"✓ Data processed: {mb:.1f} MB")
    print(f"✓ Retrieved {len(df):,} rows\n")
    
    # Save to cache and clean up old cache AFTER successful fetch
    today = datetime.now().strftime("%Y-%m-%d")
    if use_cache:
        save_cached_data(df, package, days)
        cleanup_old_cache(package, days)
    
    return df, today


def generate_text_report(df: pd.DataFrame, package: str, days: int, output_dir: Path, data_date: str) -> Path:
    """Generate text report."""
    print("Generating text report...")
    
    report_file = output_dir / f"{package}_last_{days}days.txt"
    
    total = df['downloads'].sum()
    countries = df['country_code'].nunique()
    
    # Calculate CI/CD percentage
    ci_total = df[df['is_ci'] == True]['downloads'].sum()
    ci_pct = (ci_total / total * 100) if total > 0 else 0
    
    # Calculate UV adoption
    installers = df.groupby('installer')['downloads'].sum()
    uv_total = installers.get('uv', 0)
    uv_pct = (uv_total / total * 100) if total > 0 else 0
    
    # Calculate MCP (uvx) usage
    uv_subcmds = df[df['installer'] == 'uv'].groupby('subcommand')['downloads'].sum()
    uvx_count = uv_subcmds.get('uvx', 0)
    
    with open(report_file, 'w') as f:
        f.write(f"PyPI Analytics: {package}\n")
        f.write(f"Period: Last {days} days\n")
        f.write(f"Data Date: {data_date}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"TOTAL DOWNLOADS: {total:,}\n")
        f.write(f"COUNTRIES REACHED: {countries}\n")
        f.write(f"CI/CD INSTALLS: {ci_pct:.1f}%\n")
        f.write(f"UV ADOPTION: {uv_pct:.1f}%\n")
        f.write(f"MCP (uvx): {uvx_count:,}\n\n")
        
        # Countries
        countries = df.groupby('country_code')['downloads'].sum().sort_values(ascending=False)
        f.write(f"COUNTRIES ({len(countries)} total):\n")
        for country, count in countries.head(20).items():
            pct = (count / total * 100)
            f.write(f"  {country:4s} {count:>10,} ({pct:5.1f}%)\n")
        
        # OS/Distro
        f.write("\nOS/DISTRO:\n")
        os_distro = df.groupby(['os', 'distro'])['downloads'].sum().sort_values(ascending=False)
        for (os_name, distro), count in os_distro.head(15).items():
            f.write(f"  {os_name or 'N/A':10s} {distro or 'N/A':30s} {count:>10,}\n")
        
        # Installers - Show ALL installers to ensure 100% coverage
        f.write("\nINSTALLERS:\n")
        installers = df.groupby('installer', dropna=False).agg({
            'downloads': 'sum',
        }).sort_values('downloads', ascending=False)
        
        for installer, row in installers.iterrows():
            count = row['downloads']
            pct = (count / total * 100)
            
            # Get CI breakdown for this installer
            installer_df = df[df['installer'] == installer] if pd.notna(installer) else df[df['installer'].isna()]
            # CI: only True, Non-CI: False + NULL (treating NULL as Non-CI)
            ci_count = installer_df[installer_df['is_ci'] == True]['downloads'].sum()
            non_ci_count = count - ci_count  # Everything that's not confirmed CI
            
            installer_name = installer if pd.notna(installer) else '(unknown)'
            f.write(f"  {installer_name:15s} {count:>10,} ({pct:5.1f}%) - CI: {ci_count:,}, Non-CI: {non_ci_count:,}\n")
        
        # UV subcommands - Show ALL subcommands
        uv_subcmds = df[df['installer'] == 'uv'].groupby('subcommand', dropna=False)['downloads'].sum().sort_values(ascending=False)
        if len(uv_subcmds) > 0:
            f.write("\nUV SUBCOMMANDS:\n")
            for subcmd, count in uv_subcmds.items():
                subcmd_name = subcmd if pd.notna(subcmd) else '(none)'
                f.write(f"  {subcmd_name:20s} {count:>10,}\n")
        
        # Python versions
        f.write("\nPYTHON VERSIONS:\n")
        py_versions = df.groupby('python_version')['downloads'].sum().sort_values(ascending=False)
        for version, count in py_versions.head(10).items():
            if version:
                pct = (count / total * 100)
                f.write(f"  {version:10s} {count:>10,} ({pct:5.1f}%)\n")
        
        # Verification section - ensure 100% coverage
        f.write("\nVERIFICATION:\n")
        installer_total = installers['downloads'].sum()
        f.write(f"  Total from installers: {installer_total:,}\n")
        f.write(f"  Total downloads:       {total:,}\n")
        coverage_pct = (installer_total / total * 100) if total > 0 else 0
        f.write(f"  Coverage:              {coverage_pct:.2f}%\n")
        if installer_total != total:
            f.write(f"  ⚠ Missing:             {total - installer_total:,} downloads\n")
        else:
            f.write(f"  ✓ 100% coverage achieved\n")
    
    print(f"✓ Text report: {report_file}\n")
    return report_file


def generate_top_countries_tables(df: pd.DataFrame, package: str, days: int, output_dir: Path):
    """Generate top 10 countries markdown tables with flags and full names (dynamic lookup)."""
    print("Generating top countries tables...")
    
    def get_country_flag_img(code: str) -> str:
        """Get flag image HTML for country code using flagcdn.com."""
        code_lower = code.lower()
        # Use flagcdn.com for high-quality SVG flags (16px height for inline display)
        return f'<img src="https://flagcdn.com/16x12/{code_lower}.png" alt="{code}" width="16" height="12">'
    
    def get_country_name(code: str) -> str:
        """Get full country name from ISO code using pycountry library."""
        try:
            country = pycountry.countries.get(alpha_2=code.upper())
            return country.name if country else code
        except (AttributeError, LookupError):
            return code  # Fallback to code if lookup fails
    
    # Get top 10 countries
    countries = df.groupby('country_code')['downloads'].sum().sort_values(ascending=False).head(10)
    total = df['downloads'].sum()
    
    # Create markdown table with flag images and full names (dynamically generated)
    table_lines = []
    for country_code, downloads in countries.items():
        pct = (downloads / total * 100) if total > 0 else 0
        flag_img = get_country_flag_img(country_code)
        name = get_country_name(country_code)
        table_lines.append(f"| {flag_img} {name} | {downloads:,} | {pct:.1f}% |")
    
    # Save to file
    md_file = output_dir / f"{package}_top_countries_{days}days.md"
    with open(md_file, 'w') as f:
        f.write('\n'.join(table_lines))
    
    print(f"✓ Top countries table: {md_file}\n")
    return table_lines

def generate_quarterly_version_trends(client: bigquery.Client, package: str, output_dir: Path):
    """Generate quarterly download trends by major version over last 3 years."""
    print("Generating quarterly version trends...")
    
    # Check cache first
    cache_path = get_cache_path(package, "quarterly_3yr")
    if cache_path.exists():
        cache_date = get_cache_date(package, "quarterly_3yr")
        df = load_cached_data(package, "quarterly_3yr")
        if df is not None:
            print(f"  ✓ Loaded {len(df):,} rows from cache (data from {cache_date})")
        else:
            df = None
    else:
        df = None
    
    # Query if no cache
    if df is None:
        sql = f"""
        WITH quarterly_data AS (
          SELECT
            EXTRACT(YEAR FROM DATE(timestamp)) AS year,
            EXTRACT(QUARTER FROM DATE(timestamp)) AS quarter,
            REGEXP_EXTRACT(file.version, r'^(\\d+)') AS major_version,
            COUNT(*) as downloads
          FROM `bigquery-public-data.pypi.file_downloads`
          WHERE file.project = '{package}'
            AND DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 YEAR)
          GROUP BY year, quarter, major_version
        )
        SELECT
          year,
          quarter,
          CONCAT(CAST(year AS STRING), ' Q', CAST(quarter AS STRING)) as quarter_label,
          major_version,
          downloads
        FROM quarterly_data
        ORDER BY year, quarter, major_version
        """
        
        job = client.query(sql)
        df = job.result().to_dataframe()
        
        mb = job.total_bytes_processed / 1_000_000 if job.total_bytes_processed else 0
        print(f"  Data processed: {mb:.1f} MB")
        print(f"  Retrieved {len(df):,} rows")
        
        # Save to cache
        save_cached_data(df, package, "quarterly_3yr")
        cleanup_old_cache(package, "quarterly_3yr")
    
    if df.empty:
        print("  Warning: No version data found")
        return
    
    # Pivot data for stacked bar chart
    pivot_data = {}
    
    # Sort by year and quarter columns to get proper chronological order
    df_sorted = df.sort_values(['year', 'quarter'])
    quarters = df_sorted['quarter_label'].drop_duplicates().tolist()
    versions = sorted(df['major_version'].dropna().unique(), key=lambda x: int(x) if x.isdigit() else 0)
    
    # Calculate days in each quarter for normalization
    from datetime import datetime
    current_date = datetime.now()
    current_year = current_date.year
    current_quarter = (current_date.month - 1) // 3 + 1
    
    def get_days_in_quarter(year, quarter):
        """Calculate actual days in a quarter, accounting for partial current quarter"""
        quarter_start_month = (quarter - 1) * 3 + 1
        if year == current_year and quarter == current_quarter:
            # For current quarter, calculate days from start to today
            quarter_start = datetime(year, quarter_start_month, 1)
            return (current_date - quarter_start).days + 1
        else:
            # For complete quarters, calculate full quarter length
            quarter_start = datetime(year, quarter_start_month, 1)
            if quarter == 4:
                quarter_end = datetime(year + 1, 1, 1)
            else:
                quarter_end = datetime(year, quarter_start_month + 3, 1)
            return (quarter_end - quarter_start).days
    
    # Average days per month
    AVG_DAYS_PER_MONTH = 30.4167
    
    for version in versions:
        version_data = df[df['major_version'] == version]
        monthly_averages = []
        for q in quarters:
            q_data = version_data[version_data['quarter_label'] == q]
            if not q_data.empty:
                # Use the actual year and quarter columns from the dataframe
                year = int(q_data['year'].iloc[0])
                quarter = int(q_data['quarter'].iloc[0])
                
                total_downloads = q_data['downloads'].sum()
                days_in_quarter = get_days_in_quarter(year, quarter)
                # Convert to monthly average: (total / days) * avg_days_per_month
                monthly_avg = (total_downloads / days_in_quarter) * AVG_DAYS_PER_MONTH
                monthly_averages.append(monthly_avg)
            else:
                monthly_averages.append(0)
        pivot_data[f'v{version}.x'] = monthly_averages
    
    # Generate CSV with year, month, total downloads, and per-version downloads
    csv_data = []
    for i, q in enumerate(quarters):
        # Parse quarter label (e.g., "2023 Q2")
        year_str, quarter_str = q.split(' Q')
        year = int(year_str)
        quarter_num = int(quarter_str)
        
        row = {
            'year': year,
            'quarter': quarter_num,
            'quarter_label': q
        }
        
        # Add downloads for each version
        total = 0
        for version in versions:
            version_label = f'v{version}.x'
            downloads = int(pivot_data[version_label][i])
            row[version_label] = downloads
            total += downloads
        
        row['total_downloads'] = total
        csv_data.append(row)
    
    # Write CSV file to top-level directory
    csv_file = Path(f"{package}_quarterly_versions.csv")
    import csv
    if csv_data:
        fieldnames = ['year', 'quarter', 'quarter_label'] + [f'v{v}.x' for v in versions] + ['total_downloads']
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)
        print(f"  ✓ CSV exported: {csv_file}")
    
    # Create stacked bar chart
    fig = go.Figure()
    
    # Identify current quarter for pattern marking
    current_quarter_label = f"{current_year} Q{current_quarter}"
    
    for version_label, values in pivot_data.items():
        # Create pattern list - noticeable transparent cross-hatch for current quarter (projected)
        patterns = []
        for q in quarters:
            if q == current_quarter_label:
                patterns.append('x')  # Cross-hatch (diagonal lines in both directions)
            else:
                patterns.append('')   # Solid fill for actual data
        
        fig.add_trace(go.Bar(
            name=version_label,
            x=quarters,
            y=values,
            text=[f'{int(v):,}' if v > 0 else '' for v in values],
            textposition='inside',
            textfont=dict(size=10),
            marker=dict(
                pattern=dict(
                    shape=patterns,
                    solidity=0.2,  # Increased solidity for more noticeable lines
                    fgcolor='rgba(255,255,255,0.6)'  # More opaque white lines
                )
            )
        ))
    
    # Add a dummy trace for the legend to show pattern meaning
    fig.add_trace(go.Bar(
        name='Projected (current quarter)',
        x=[None],
        y=[None],
        marker=dict(
            color='gray',
            pattern=dict(
                shape='x',
                solidity=0.2,
                fgcolor='rgba(255,255,255,0.6)'
            )
        ),
        showlegend=True
    ))
    
    fig.update_layout(
        title="Downloads Per Month (by quarter) Last 3 Years<br><sub>Current quarter shows projected monthly average (diagonal pattern)</sub>",
        xaxis_title="Quarter",
        yaxis_title="Downloads",
        barmode='stack',
        height=600,
        width=1200,
        showlegend=True,
        legend=dict(
            title="Version",
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    html_file = output_dir / f"{package}_quarterly_versions.html"
    png_file = output_dir / f"{package}_quarterly_versions.png"
    
    fig.write_html(html_file)
    try:
        fig.write_image(png_file, width=1200, height=600)
        print(f"✓ Quarterly version trends: {html_file} and {png_file}\n")
    except Exception as e:
        print(f"✓ Quarterly version trends: {html_file} (PNG export failed: {e})\n")



def generate_world_map(df: pd.DataFrame, package: str, days: int, output_dir: Path):
    """Generate world map."""
    print("Generating world map...")
    
    countries = df.groupby('country_code')['downloads'].sum().reset_index()
    countries.columns = ['country_code', 'downloads']
    
    # Convert 2-letter ISO codes to 3-letter ISO codes for proper choropleth rendering
    # Common mappings for top countries
    iso2_to_iso3 = {
        'US': 'USA', 'GB': 'GBR', 'DE': 'DEU', 'FR': 'FRA', 'CA': 'CAN',
        'AU': 'AUS', 'JP': 'JPN', 'IN': 'IND', 'BR': 'BRA', 'CN': 'CHN',
        'IT': 'ITA', 'ES': 'ESP', 'NL': 'NLD', 'SE': 'SWE', 'CH': 'CHE',
        'KR': 'KOR', 'PL': 'POL', 'BE': 'BEL', 'AT': 'AUT', 'NO': 'NOR',
        'DK': 'DNK', 'FI': 'FIN', 'IE': 'IRL', 'NZ': 'NZL', 'SG': 'SGP',
        'HK': 'HKG', 'IL': 'ISR', 'MX': 'MEX', 'AR': 'ARG', 'CL': 'CHL',
        'ZA': 'ZAF', 'RU': 'RUS', 'TR': 'TUR', 'TH': 'THA', 'MY': 'MYS',
        'ID': 'IDN', 'PH': 'PHL', 'VN': 'VNM', 'UA': 'UKR', 'RO': 'ROU',
        'CZ': 'CZE', 'PT': 'PRT', 'GR': 'GRC', 'HU': 'HUN', 'BG': 'BGR'
    }
    
    # Apply conversion, keep original if not in mapping
    countries['country_code_iso3'] = countries['country_code'].map(
        lambda x: iso2_to_iso3.get(x, x)
    )
    
    fig = go.Figure(data=go.Choropleth(
        locations=countries['country_code_iso3'].tolist(),
        z=countries['downloads'].tolist(),
        locationmode='ISO-3',  # KEY FIX: Use 3-letter ISO codes
        text=countries['country_code'].tolist(),
        colorscale='YlOrRd',
        marker_line_color='darkgray',
        marker_line_width=0.5,
        colorbar_title='Downloads',
    ))
    
    fig.update_layout(
        title_text='Downloads by Country',
        geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'),
        height=500, width=1000
    )
    
    html_file = output_dir / f"{package}_map_{days}days.html"
    png_file = output_dir / f"{package}_map_{days}days.png"
    
    fig.write_html(html_file)
    try:
        fig.write_image(png_file, width=1000, height=500)
        print(f"✓ World map: {html_file} and {png_file}\n")
    except Exception as e:
        print(f"✓ World map: {html_file} (PNG export failed: {e})\n")


def generate_mcp_analysis(df: pd.DataFrame, package: str, days: int, output_dir: Path):
    """Generate MCP analysis with separate side-by-side charts."""
    print("Generating MCP analysis...")
    
    total = df['downloads'].sum()
    
    # Get installer data
    installers = df.groupby('installer').agg({
        'downloads': 'sum'
    }).sort_values('downloads', ascending=False)
    
    uv_total = installers.loc['uv', 'downloads'] if 'uv' in installers.index else 0
    pip_total = installers.loc['pip', 'downloads'] if 'pip' in installers.index else 0
    poetry_total = installers.loc['poetry', 'downloads'] if 'poetry' in installers.index else 0
    
    if uv_total == 0:
        print("⚠ No UV data, skipping MCP analysis\n")
        return
    
    # UV subcommands (include NaN/None values with dropna=False)
    uv_subcmds = df[df['installer'] == 'uv'].groupby('subcommand', dropna=False)['downloads'].sum().sort_values(ascending=False)
    uvx_count = uv_subcmds.get('uvx', 0)
    
    # CI breakdown - treating NULL as Non-CI
    uv_df = df[df['installer'] == 'uv']
    uv_ci = uv_df[uv_df['is_ci'] == True]['downloads'].sum()
    uv_non_ci = uv_total - uv_ci  # Everything that's not confirmed CI
    
    pip_df = df[df['installer'] == 'pip']
    pip_ci = pip_df[pip_df['is_ci'] == True]['downloads'].sum()
    pip_non_ci = pip_total - pip_ci  # Everything that's not confirmed CI
    
    poetry_df = df[df['installer'] == 'poetry']
    poetry_ci = poetry_df[poetry_df['is_ci'] == True]['downloads'].sum()
    poetry_non_ci = poetry_total - poetry_ci  # Everything that's not confirmed CI
    
    # Daily trends
    daily_uv = df[df['installer'] == 'uv'].groupby('date')['downloads'].sum().sort_index()
    daily_uvx = df[(df['installer'] == 'uv') & (df['subcommand'] == 'uvx')].groupby('date')['downloads'].sum().sort_index()
    
    # Chart 1: Installer Utilized (Pie Chart) - pip, uv, poetry, other
    other_total = total - pip_total - uv_total - poetry_total
    fig1 = go.Figure(data=[go.Pie(
        labels=['pip', 'uv', 'poetry', 'other'],
        values=[pip_total, uv_total, poetry_total, other_total],
        marker=dict(colors=['#636EFA', '#EF553B', '#00CC96', '#FFA15A'])
    )])
    fig1.update_layout(
        title='Installer Utilized',
        height=400,
        width=500
    )
    
    html_file1 = output_dir / f"{package}_mcp_installer_{days}days.html"
    png_file1 = output_dir / f"{package}_mcp_installer_{days}days.png"
    fig1.write_html(html_file1)
    try:
        fig1.write_image(png_file1, width=500, height=400)
    except Exception as e:
        pass  # Silent fail for PNG
    
    # Chart 2: UV Subcommands (Bar Chart)
    # Show all subcommands (not just top 10) to ensure (none) is visible
    top_subcmds = uv_subcmds.head(15)  # Increased to show more subcommands
    
    # Color coding: uvx=red, no subcommand=gray, others=teal
    colors = []
    labels = []
    for s in top_subcmds.index:
        # Handle None, NaN, empty string, or pd.NA
        if pd.isna(s) or s is None or s == '':
            label = 'no subcommand'
            colors.append('#999999')  # Grey for no subcommand
        elif s == 'uvx':
            label = s
            colors.append('#EF553B')  # Red for uvx (MCP)
        else:
            label = s
            colors.append('#00CC96')  # Teal for other subcommands
        labels.append(label)
    
    fig2 = go.Figure(data=[go.Bar(
        x=labels,
        y=top_subcmds.values,
        marker_color=colors,
        showlegend=False,
        text=top_subcmds.values,
        textposition='outside',
        texttemplate='%{text:,}',
        textfont=dict(size=9, color='black'),
        cliponaxis=False
    )])
    fig2.update_layout(
        title='UV Subcommands (uvx = MCP Pattern)',
        xaxis_title='Subcommand',
        yaxis_title='Downloads',
        height=500,
        width=500,
        margin=dict(t=80, b=60, l=60, r=20),
        yaxis=dict(range=[0, top_subcmds.values.max() * 1.15]),
        annotations=[
            dict(
                x=0.98, y=0.98,
                xref='paper', yref='paper',
                text='<b>Legend:</b><br>🔴 uvx (MCP)<br>⚫ no subcommand<br>🟢 Other UV',
                showarrow=False,
                xanchor='right',
                yanchor='top',
                align='left',
                font=dict(size=9),
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='#999',
                borderwidth=1,
                borderpad=4
            )
        ]
    )
    
    html_file2 = output_dir / f"{package}_mcp_subcommands_{days}days.html"
    png_file2 = output_dir / f"{package}_mcp_subcommands_{days}days.png"
    fig2.write_html(html_file2)
    try:
        fig2.write_image(png_file2, width=500, height=500, scale=2)
    except Exception as e:
        pass  # Silent fail for PNG
    
    # Chart 3: CI vs Non-CI Usage (Stacked Bar Chart)
    # Calculate other installer stats - treating NULL as Non-CI
    other_total = total - pip_total - uv_total - poetry_total
    other_df = df[~df['installer'].isin(['pip', 'uv', 'poetry'])]
    other_ci = other_df[other_df['is_ci'] == True]['downloads'].sum()
    other_non_ci = other_total - other_ci  # Everything that's not confirmed CI
    
    fig3 = go.Figure(data=[
        go.Bar(
            name='CI',
            x=['pip', 'uv', 'poetry', 'other'],
            y=[pip_ci, uv_ci, poetry_ci, other_ci],
            marker_color='#00CC96',
            text=[pip_ci, uv_ci, poetry_ci, other_ci],
            texttemplate='%{text:,}',
            textposition='inside',
            textfont=dict(color='white', size=10)
        ),
        go.Bar(
            name='Non-CI',
            x=['pip', 'uv', 'poetry', 'other'],
            y=[pip_non_ci, uv_non_ci, poetry_non_ci, other_non_ci],
            marker_color='#EF553B',
            text=[pip_non_ci, uv_non_ci, poetry_non_ci, other_non_ci],
            texttemplate='%{text:,}',
            textposition='inside',
            textfont=dict(color='white', size=10)
        )
    ])
    fig3.update_layout(
        title='CI vs Non-CI Usage',
        xaxis_title='Installer',
        yaxis_title='Downloads',
        barmode='stack',
        height=450,
        width=500,
        legend=dict(
            x=0.98,
            y=0.98,
            xanchor='right',
            yanchor='top',
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='#999',
            borderwidth=1
        )
    )
    
    html_file3 = output_dir / f"{package}_mcp_ci_{days}days.html"
    png_file3 = output_dir / f"{package}_mcp_ci_{days}days.png"
    fig3.write_html(html_file3)
    try:
        fig3.write_image(png_file3, width=500, height=450, scale=2)
    except Exception as e:
        pass  # Silent fail for PNG
    
    # Chart 4: Daily UV Trend (Line Chart with Area Fill)
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=daily_uv.index,
        y=daily_uv.values,
        mode='lines',
        name='Total UV',
        line=dict(color='#00CC96', width=2)
    ))
    if len(daily_uvx) > 0:
        fig4.add_trace(go.Scatter(
            x=daily_uvx.index,
            y=daily_uvx.values,
            mode='lines',
            name='uvx (MCP)',
            fill='tozeroy',
            line=dict(color='#EF553B', width=2)
        ))
    fig4.update_layout(
        title='Daily UV Trend',
        xaxis_title='Date',
        yaxis_title='Downloads',
        height=400,
        width=500
    )
    
    html_file4 = output_dir / f"{package}_mcp_daily_{days}days.html"
    png_file4 = output_dir / f"{package}_mcp_daily_{days}days.png"
    fig4.write_html(html_file4)
    try:
        fig4.write_image(png_file4, width=500, height=400)
    except Exception as e:
        pass  # Silent fail for PNG
    
    print(f"✓ MCP analysis charts:")
    print(f"  - Installer: {html_file1} and {png_file1}")
    print(f"  - Subcommands: {html_file2} and {png_file2}")
    print(f"  - CI vs Non-CI: {html_file3} and {png_file3}")
    print(f"  - Daily Trend: {html_file4} and {png_file4}")
    
    # Explanation markdown
    md_file = output_dir / f"{package}_mcp_{days}days.md"
    with open(md_file, 'w') as f:
        f.write(f"# MCP Usage Inference - {package} ({days} days)\n\n")
        f.write(f"## Summary\n\n")
        f.write(f"- **Total Downloads:** {total:,}\n")
        f.write(f"- **UV Downloads:** {uv_total:,} ({uv_total/total*100:.1f}%)\n")
        f.write(f"- **uvx Downloads (MCP Pattern):** {uvx_count:,} ({uvx_count/total*100:.2f}%)\n")
        f.write(f"- **UV Non-CI:** {uv_non_ci:,} ({uv_non_ci/uv_total*100:.1f}% of UV)\n\n")
        f.write(f"## Key Findings\n\n")
        f.write(f"1. **Confirmed MCP Usage:** {uvx_count:,} downloads using `uvx` subcommand\n")
        f.write(f"2. **UV Adoption:** {uv_total/total*100:.1f}% market share\n")
        f.write(f"3. **Interactive Usage:** {uv_non_ci/uv_total*100:.1f}% of UV downloads are non-CI\n\n")
        f.write(f"MCP usage is detectable but small. The broader story is UV's growth as a modern Python installer.\n")
    
    print(f"✓ MCP explanation: {md_file}\n")


def generate_deployment_chart(df: pd.DataFrame, package: str, days: int, output_dir: Path):
    """Generate deployment platform chart."""
    print("Generating deployment chart...")
    
    # Load or create color cache for platform distribution
    cache_file = output_dir / ".color_cache_platforms.json"
    color_cache = {}
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            color_cache = json.load(f)
    
    # Categorize platforms
    platform_map = {}
    for _, row in df.iterrows():
        distro = str(row['distro']) if pd.notna(row['distro']) else ''
        os_name = str(row['os']) if pd.notna(row['os']) else ''
        
        if 'Amazon' in distro:
            platform = 'AWS'
        elif 'Alpine' in distro:
            platform = 'Containers'
        elif 'Red Hat' in distro or 'RHEL' in distro:
            platform = 'Enterprise'
        elif 'Ubuntu' in distro:
            platform = 'Ubuntu'
        elif 'Debian' in distro:
            platform = 'Debian'
        elif os_name == 'Darwin':
            platform = 'macOS'
        elif os_name == 'Windows':
            platform = 'Windows'
        else:
            platform = 'Other'
        
        platform_map[platform] = platform_map.get(platform, 0) + row['downloads']
    
    # Assign colors consistently using cache
    import hashlib
    labels = list(platform_map.keys())
    colors = []
    for label in labels:
        if label not in color_cache:
            # Generate consistent color from hash
            hash_val = int(hashlib.md5(label.encode()).hexdigest()[:6], 16)
            hue = (hash_val % 360)
            saturation = 65 + (hash_val % 20)
            lightness = 50 + (hash_val % 15)
            color_cache[label] = f'hsl({hue}, {saturation}%, {lightness}%)'
        colors.append(color_cache[label])
    
    # Save updated color cache
    with open(cache_file, 'w') as f:
        json.dump(color_cache, f, indent=2)
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=list(platform_map.values()),
        hole=0.3,
        marker=dict(colors=colors)
    )])
    fig.update_layout(title="Platform Distribution", height=600, width=800)
    
    html_file = output_dir / f"{package}_platforms_{days}days.html"
    png_file = output_dir / f"{package}_platforms_{days}days.png"
    
    fig.write_html(html_file)
    try:
        fig.write_image(png_file, width=800, height=600)
        print(f"✓ Deployment chart: {html_file} and {png_file}\n")
    except Exception as e:
        print(f"✓ Deployment chart: {html_file} (PNG export failed: {e})\n")


def generate_deployment_types(df: pd.DataFrame, package: str, days: int, output_dir: Path):
    """Generate deployment types bar chart (Container vs VM vs Developer)."""
    print("Generating deployment types chart...")
    
    deployment_types = {}
    
    for _, row in df.iterrows():
        distro = str(row['distro']) if pd.notna(row['distro']) else ''
        os_name = str(row['os']) if pd.notna(row['os']) else ''
        libc = str(row['libc']) if pd.notna(row['libc']) else ''
        is_ci = pd.notna(row['is_ci']) and row['is_ci'] == True
        downloads = row['downloads']
        
        # Categorize deployment types
        if 'musl' in libc or 'Alpine' in distro:
            dtype = 'Containers (Alpine/musl)'
        elif 'Amazon' in distro and is_ci:
            dtype = 'AWS CI/CD'
        elif 'Amazon' in distro:
            dtype = 'AWS VMs'
        elif 'Red Hat' in distro or 'RHEL' in distro:
            dtype = 'Enterprise VMs'
        elif is_ci:
            dtype = 'CI Pipelines'
        elif os_name == 'Darwin':
            dtype = 'Developer Macs'
        elif os_name == 'Windows':
            dtype = 'Windows'
        elif os_name == 'Linux' or distro:  # Has Linux OS or any distro info
            dtype = 'Other Linux'
        else:
            dtype = 'Other OS'  # z/OS, FreeBSD, etc.
        
        deployment_types[dtype] = deployment_types.get(dtype, 0) + downloads
    
    # Validate that all downloads are accounted for
    total_categorized = sum(deployment_types.values())
    total_actual = df['downloads'].sum()
    if abs(total_categorized - total_actual) > 0.01:  # Allow for floating point errors
        print(f"  Warning: Download count mismatch! Categorized: {total_categorized:,}, Actual: {total_actual:,}")
    
    # Sort by value
    sorted_types = sorted(deployment_types.items(), key=lambda x: x[1], reverse=True)
    labels = [t[0] for t in sorted_types]
    values = [t[1] for t in sorted_types]
    
    # Print summary for verification
    print(f"  Total downloads: {total_actual:,}")
    print(f"  Categories: {len(deployment_types)}")
    for label, value in sorted_types:
        pct = (value / total_actual * 100) if total_actual > 0 else 0
        print(f"    {label}: {value:,} ({pct:.1f}%)")
    
    # Create a custom color palette similar to Set3 (qualitative colors)
    set3_colors = [
        '#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3',
        '#fdb462', '#b3de69', '#fccde5', '#d9d9d9', '#bc80bd',
        '#ccebc5', '#ffed6f'
    ]
    # Assign colors cyclically if we have more categories than colors
    bar_colors = [set3_colors[i % len(set3_colors)] for i in range(len(labels))]
    
    fig = go.Figure(data=[go.Bar(
        y=labels,
        x=values,
        orientation='h',
        marker=dict(
            color=bar_colors  # Use custom Set3-like colors
        ),
        text=[f'{v:,}' for v in values],  # Add formatted numbers as text
        textposition='outside',  # Position text outside the bars
        textfont=dict(size=12),  # Set font size for readability
        showlegend=False  # No legend needed since y-axis labels the categories
    )])
    
    # Calculate appropriate x-axis range with buffer for text labels
    max_value = max(values) if values else 0
    x_range_max = max_value * 1.15  # Add 15% buffer for text labels
    
    fig.update_layout(
        title="Deployment Types",
        xaxis_title="Downloads",
        yaxis_title="Deployment Type",
        height=600,
        width=1000,
        xaxis=dict(range=[0, x_range_max])  # Set x-axis range with buffer
    )
    
    html_file = output_dir / f"deployment_types_{days}day.html"
    png_file = output_dir / f"deployment_types_{days}day.png"
    
    fig.write_html(html_file)
    try:
        fig.write_image(png_file, width=1000, height=600)
        print(f"✓ Deployment types: {html_file} and {png_file}\n")
    except Exception as e:
        print(f"✓ Deployment types: {html_file} (PNG export failed: {e})\n")


def generate_architecture_distribution(df: pd.DataFrame, package: str, days: int, output_dir: Path):
    """Generate CPU architecture distribution by platform."""
    print("Generating architecture distribution chart...")
    
    # Group by platform and architecture
    arch_data = {}
    
    for _, row in df.iterrows():
        distro = str(row['distro']) if pd.notna(row['distro']) else ''
        os_name = str(row['os']) if pd.notna(row['os']) else ''
        cpu_arch = str(row['cpu_arch']) if pd.notna(row['cpu_arch']) else 'unknown'
        downloads = row['downloads']
        
        # Categorize platform
        if 'Amazon' in distro:
            platform = 'AWS'
        elif 'Alpine' in distro:
            platform = 'Containers'
        elif 'Red Hat' in distro or 'RHEL' in distro:
            platform = 'Enterprise'
        elif 'Ubuntu' in distro:
            platform = 'Ubuntu'
        elif os_name == 'Darwin':
            platform = 'macOS'
        elif os_name == 'Windows':
            platform = 'Windows'
        else:
            platform = 'Other'
        
        if platform not in arch_data:
            arch_data[platform] = {}
        arch_data[platform][cpu_arch] = arch_data[platform].get(cpu_arch, 0) + downloads
    
    # Create stacked bar chart with architectures on x-axis
    platforms = list(arch_data.keys())
    architectures = set()
    for platform_archs in arch_data.values():
        architectures.update(platform_archs.keys())
    architectures = sorted(architectures)
    
    fig = go.Figure()
    
    # Add trace for each platform (stacked by platform)
    for platform in platforms:
        values = [arch_data[platform].get(arch, 0) for arch in architectures]
        fig.add_trace(go.Bar(
            name=platform,
            x=architectures,
            y=values,
            text=[f'{v:,}' if v > 0 else '' for v in values],  # Add formatted numbers, hide zeros
            textposition='inside',  # Position text inside stacked bars
            textfont=dict(size=11, color='white'),  # White text for visibility on colored bars
        ))
    
    # Calculate max stack height for y-axis range
    stack_totals = [sum(arch_data[p].get(arch, 0) for p in platforms) for arch in architectures]
    max_stack = max(stack_totals) if stack_totals else 0
    y_range_max = max_stack * 1.1  # Add 10% buffer at top
    
    fig.update_layout(
        title="Architecture Distribution by Platform",
        xaxis_title="CPU Architecture",
        yaxis_title="Downloads",
        barmode='stack',
        height=600,
        width=1000,
        yaxis=dict(range=[0, y_range_max])  # Set y-axis range with buffer
    )
    
    html_file = output_dir / f"deployment_architecture_{days}day.html"
    png_file = output_dir / f"deployment_architecture_{days}day.png"
    
    fig.write_html(html_file)
    try:
        fig.write_image(png_file, width=1000, height=600)
        print(f"✓ Architecture distribution: {html_file} and {png_file}\n")
    except Exception as e:
        print(f"✓ Architecture distribution: {html_file} (PNG export failed: {e})\n")


def generate_enterprise_cloud_analysis(df: pd.DataFrame, package: str, days: int, output_dir: Path):
    """Generate enterprise vs cloud-native sunburst chart."""
    print("Generating enterprise vs cloud-native analysis...")
    
    categories = {
        'Enterprise': {'CI': 0, 'Interactive': 0},
        'Cloud-Native': {'CI': 0, 'Interactive': 0},
        'Developer': {'CI': 0, 'Interactive': 0},
        'Corporate': {'CI': 0, 'Interactive': 0}
    }
    
    for _, row in df.iterrows():
        distro = str(row['distro']) if pd.notna(row['distro']) else ''
        os_name = str(row['os']) if pd.notna(row['os']) else ''
        is_ci = pd.notna(row['is_ci']) and row['is_ci'] == True
        downloads = row['downloads']
        
        ci_type = 'CI' if is_ci else 'Interactive'
        
        # Categorize
        if 'Red Hat' in distro or 'RHEL' in distro or 'Oracle' in distro or 'SUSE' in distro:
            categories['Enterprise'][ci_type] += downloads
        elif 'Alpine' in distro or ('Amazon' in distro and is_ci) or ('Ubuntu' in distro and is_ci):
            categories['Cloud-Native'][ci_type] += downloads
        elif os_name == 'Darwin':
            categories['Developer'][ci_type] += downloads
        elif os_name == 'Windows':
            categories['Corporate'][ci_type] += downloads
    
    # Build sunburst data
    labels = []
    parents = []
    values = []
    
    for category, subcats in categories.items():
        total = sum(subcats.values())
        if total > 0:
            labels.append(category)
            parents.append('')
            values.append(total)
            
            for subcat, value in subcats.items():
                if value > 0:
                    labels.append(f"{category} - {subcat}")
                    parents.append(category)
                    values.append(value)
    
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total"
    ))
    
    fig.update_layout(
        title="Enterprise vs Cloud-Native",
        height=700,
        width=900
    )
    
    html_file = output_dir / f"deployment_enterprise_cloud_{days}day.html"
    png_file = output_dir / f"deployment_enterprise_cloud_{days}day.png"
    
    fig.write_html(html_file)
    try:
        fig.write_image(png_file, width=900, height=700)
        print(f"✓ Enterprise vs cloud-native: {html_file} and {png_file}\n")
    except Exception as e:
        print(f"✓ Enterprise vs cloud-native: {html_file} (PNG export failed: {e})\n")


def generate_libc_distribution(df: pd.DataFrame, package: str, days: int, output_dir: Path):
    """Generate libc distribution chart (glibc vs musl = container signal)."""
    print("Generating libc distribution chart...")
    
    # Aggregate downloads by libc type
    libc_totals = {}
    total_rows = len(df)
    
    for _, row in df.iterrows():
        libc = str(row['libc']) if pd.notna(row['libc']) else 'unknown'
        downloads = row['downloads']
        libc_totals[libc] = libc_totals.get(libc, 0) + downloads
    
    # Debug output
    print(f"  Processed {total_rows} rows")
    print(f"  Found {len(libc_totals)} libc types:")
    total_downloads = sum(libc_totals.values())
    for libc, count in sorted(libc_totals.items(), key=lambda x: x[1], reverse=True):
        print(f"    {libc}: {count:,} downloads ({count/total_downloads*100:.1f}%)")
    
    # Check if we have meaningful data
    if not libc_totals or (len(libc_totals) == 1 and 'unknown' in libc_totals):
        print("  Warning: No meaningful libc data found (all unknown)!")
        # Create a placeholder chart
        fig = go.Figure()
        fig.add_annotation(
            text="No libc data available in dataset",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=20)
        )
        fig.update_layout(
            title="libc Distribution (musl = Containers)",
            height=600,
            width=1000,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
    else:
        # Sort by downloads
        sorted_libc = sorted(libc_totals.items(), key=lambda x: x[1], reverse=True)
        labels = [item[0] for item in sorted_libc]
        values = [item[1] for item in sorted_libc]
        
        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            textinfo='label+percent',
            textposition='auto',
            hovertemplate='<b>%{label}</b><br>Downloads: %{value:,}<br>Percentage: %{percent}<extra></extra>',
            marker=dict(
                colors=['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4B51'],
                line=dict(color='white', width=2)
            )
        )])
        
        fig.update_layout(
            title="libc Distribution (musl = Containers)",
            height=600,
            width=1000,
            showlegend=True,
            margin=dict(l=20, r=20, t=60, b=20)
        )
    
    html_file = output_dir / f"deployment_libc_{days}day.html"
    png_file = output_dir / f"deployment_libc_{days}day.png"
    
    fig.write_html(html_file)
    try:
        fig.write_image(png_file, width=1000, height=600)
        print(f"✓ libc distribution: {html_file} and {png_file}\n")
    except Exception as e:
        print(f"✓ libc distribution: {html_file} (PNG export failed: {e})\n")


def generate_deployment_use_cases(df: pd.DataFrame, package: str, days: int, output_dir: Path):
    """Generate compliance-trestle specific use cases donut chart."""
    print("Generating deployment use cases chart...")
    
    use_cases = {
        'C2P Pipeline (Alpine+CI)': 0,
        'AWS Automation (Amazon+CI)': 0,
        'Gov/DoD Compliance (RHEL)': 0,
        'CI Compliance (Other CI)': 0,
        'Development (macOS)': 0,
        'SDK Usage (Windows)': 0,
        'Other': 0
    }
    
    for _, row in df.iterrows():
        distro = str(row['distro']) if pd.notna(row['distro']) else ''
        os_name = str(row['os']) if pd.notna(row['os']) else ''
        is_ci = pd.notna(row['is_ci']) and row['is_ci'] == True
        downloads = row['downloads']
        
        if 'Alpine' in distro and is_ci:
            use_cases['C2P Pipeline (Alpine+CI)'] += downloads
        elif 'Amazon' in distro and is_ci:
            use_cases['AWS Automation (Amazon+CI)'] += downloads
        elif 'Red Hat' in distro or 'RHEL' in distro:
            use_cases['Gov/DoD Compliance (RHEL)'] += downloads
        elif is_ci:
            use_cases['CI Compliance (Other CI)'] += downloads
        elif os_name == 'Darwin':
            use_cases['Development (macOS)'] += downloads
        elif os_name == 'Windows':
            use_cases['SDK Usage (Windows)'] += downloads
        else:
            use_cases['Other'] += downloads
    
    # Filter out zero values
    use_cases = {k: v for k, v in use_cases.items() if v > 0}
    
    fig = go.Figure(data=[go.Pie(
        labels=list(use_cases.keys()),
        values=list(use_cases.values()),
        hole=0.4
    )])
    
    fig.update_layout(
        title="Compliance Use Cases",
        height=600,
        width=900
    )
    
    html_file = output_dir / f"deployment_use_cases_{days}day.html"
    png_file = output_dir / f"deployment_use_cases_{days}day.png"
    md_file = output_dir / f"deployment_use_cases_{days}day.md"
    
    fig.write_html(html_file)
    try:
        fig.write_image(png_file, width=900, height=600)
    except Exception as e:
        pass
    
    # Write explanation markdown
    total = sum(use_cases.values())
    with open(md_file, 'w') as f:
        f.write(f"# Compliance Use Cases Analysis\n\n")
        f.write(f"This chart categorizes compliance-trestle downloads by their inferred use case based on deployment environment characteristics.\n\n")
        f.write(f"## How Categories Are Determined\n\n")
        f.write(f"Categories are inferred from OS, distribution, and CI/CD indicators:\n\n")
        f.write(f"- **C2P Pipeline (Alpine+CI)**: Alpine Linux + CI environment\n")
        f.write(f"  - Indicates Compliance-to-Policy automation pipelines in containers\n")
        f.write(f"  - Typical for cloud-native compliance workflows\n\n")
        f.write(f"- **AWS Automation (Amazon+CI)**: Amazon Linux + CI environment\n")
        f.write(f"  - AWS-based compliance automation\n")
        f.write(f"  - Often used in AWS CodePipeline or similar services\n\n")
        f.write(f"- **Gov/DoD Compliance (RHEL)**: Red Hat Enterprise Linux\n")
        f.write(f"  - Government and DoD environments typically use RHEL\n")
        f.write(f"  - Indicates compliance work in regulated sectors\n\n")
        f.write(f"- **CI Compliance (Other CI)**: Other Linux distributions + CI\n")
        f.write(f"  - General CI/CD compliance workflows\n")
        f.write(f"  - Includes GitHub Actions, GitLab CI, Jenkins, etc.\n\n")
        f.write(f"- **Development (macOS)**: macOS systems\n")
        f.write(f"  - Local development and testing\n")
        f.write(f"  - Developers working on compliance automation\n\n")
        f.write(f"- **SDK Usage (Windows)**: Windows systems\n")
        f.write(f"  - Windows-based SDK integration\n")
        f.write(f"  - Enterprise Windows environments\n\n")
        f.write(f"- **Other**: All other deployment scenarios\n\n")
        f.write(f"## Current Distribution\n\n")
        for use_case, count in sorted(use_cases.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total * 100) if total > 0 else 0
            f.write(f"- **{use_case}**: {count:,} downloads ({pct:.1f}%)\n")
        f.write(f"\n**Total**: {total:,} downloads\n\n")
        f.write(f"## Interpretation\n\n")
        f.write(f"These categories help understand how compliance-trestle is being deployed:\n")
        f.write(f"- High CI percentages indicate automation adoption\n")
        f.write(f"- RHEL usage suggests government/regulated sector adoption\n")
        f.write(f"- Container usage (Alpine) shows cloud-native practices\n")
        f.write(f"- macOS usage indicates active development community\n")
    
    print(f"✓ Deployment use cases: {html_file}, {png_file}, and {md_file}\n")


def generate_deployment_summary(df: pd.DataFrame, package: str, days: int, output_dir: Path):
    """Generate deployment summary dashboard with key metrics."""
    print("Generating deployment summary dashboard...")
    
    total = df['downloads'].sum()
    
    # Calculate metrics
    container_count = df[df['libc'].str.contains('musl', na=False) |
                        df['distro'].str.contains('Alpine', na=False)]['downloads'].sum()
    aws_count = df[df['distro'].str.contains('Amazon', na=False)]['downloads'].sum()
    enterprise_count = df[df['distro'].str.contains('Red Hat|RHEL', na=False, regex=True)]['downloads'].sum()
    ci_count = df[df['is_ci'] == True]['downloads'].sum()
    arm_count = df[df['cpu_arch'].str.contains('aarch64|arm64', na=False, regex=True)]['downloads'].sum()
    musl_count = df[df['libc'].str.contains('musl', na=False)]['downloads'].sum()
    
    # Calculate percentages
    metrics = {
        'Container Adoption': (container_count / total * 100) if total > 0 else 0,
        'AWS Usage': (aws_count / total * 100) if total > 0 else 0,
        'Enterprise Deployment': (enterprise_count / total * 100) if total > 0 else 0,
        'CI/CD Percentage': (ci_count / total * 100) if total > 0 else 0,
        'ARM Architecture': (arm_count / total * 100) if total > 0 else 0,
        'musl libc (Containers)': (musl_count / total * 100) if total > 0 else 0
    }
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=list(metrics.keys()),
            y=list(metrics.values()),
            text=[f'{v:.1f}%' for v in metrics.values()],
            textposition='auto',
            marker=dict(
                color=list(metrics.values()),
                colorscale='Teal',
                showscale=True,
                colorbar=dict(title="Percentage")
            )
        )
    ])
    
    fig.update_layout(
        title="Deployment Summary Dashboard",
        xaxis_title="Deployment Metrics",
        yaxis_title="Percentage (%)",
        yaxis=dict(range=[0, 100]),
        height=600,
        width=1400,
        showlegend=False
    )
    
    html_file = output_dir / f"deployment_summary_{days}day.html"
    png_file = output_dir / f"deployment_summary_{days}day.png"
    
    fig.write_html(html_file)
    try:
        fig.write_image(png_file, width=1400, height=800)
        print(f"✓ Deployment summary: {html_file} and {png_file}\n")
    except Exception as e:
        print(f"✓ Deployment summary: {html_file} (PNG export failed: {e})\n")
        print(f"✓ Deployment chart: {html_file} (PNG export failed: {e})\n")


def update_readme(package: str, data_date: str, output_dir: Path):
    """Update README.md using HTML comment markers from docs/README.template."""
    template_path = Path("docs/README.template")
    readme_wip_path = Path("README.wip")
    readme_path = Path("README.md")
    
    if not template_path.exists():
        print("⚠ docs/README.template not found, skipping update")
        return
    
    # Step 1: Copy template to README.wip (fresh start, eliminates cross-contamination)
    print("✓ Copying docs/README.template to README.wip (fresh start)")
    template_content = template_path.read_text()
    readme_wip_path.write_text(template_content)
    
    # Load the 30-day and 90-day reports to extract metrics
    report_30 = output_dir / f"{package}_last_30days.txt"
    report_90 = output_dir / f"{package}_last_90days.txt"
    
    # Load pre-generated country tables
    countries_30_file = output_dir / f"{package}_top_countries_30days.md"
    countries_90_file = output_dir / f"{package}_top_countries_90days.md"
    
    def extract_metrics(report_path):
        """Extract key metrics from a text report."""
        if not report_path.exists():
            return None
        
        content = report_path.read_text()
        metrics = {}
        
        import re
        # Extract total downloads
        match = re.search(r'TOTAL DOWNLOADS:\s+([\d,]+)', content)
        if match:
            metrics['downloads'] = match.group(1)
            metrics['total_downloads'] = int(match.group(1).replace(',', ''))  # Store as int for calculations
        
        # Extract countries reached
        match = re.search(r'COUNTRIES REACHED:\s+(\d+)', content)
        if match:
            metrics['countries'] = match.group(1)
        
        # Extract CI/CD percentage
        match = re.search(r'CI/CD INSTALLS:\s+([\d.]+)%', content)
        if match:
            metrics['ci_pct'] = match.group(1)
        
        # Extract UV adoption
        match = re.search(r'UV ADOPTION:\s+([\d.]+)%', content)
        if match:
            metrics['uv_pct'] = match.group(1)
        
        # Extract MCP (uvx) count
        match = re.search(r'MCP \(uvx\):\s+([\d,]+)', content)
        if match:
            metrics['mcp_count'] = match.group(1)
            metrics['uvx_count'] = int(match.group(1).replace(',', ''))  # Also store as int for calculations
        
        # Extract UV CI/Non-CI breakdown from INSTALLERS section
        match = re.search(r'^\s*uv\s+.*?CI:\s+([\d,]+),\s+Non-CI:\s+([\d,]+)', content, re.MULTILINE)
        if match:
            uv_ci = match.group(1).replace(',', '')
            uv_non_ci = match.group(2).replace(',', '')
            uv_total = int(uv_ci) + int(uv_non_ci)
            metrics['uv_total'] = uv_total  # Store UV total for calculations
            if uv_total > 0:
                uv_non_ci_pct = (int(uv_non_ci) / uv_total * 100)
                metrics['uv_non_ci'] = match.group(2)  # Keep comma formatting
                metrics['uv_non_ci_pct'] = f"{uv_non_ci_pct:.1f}"
        
        return metrics
    
    metrics_30 = extract_metrics(report_30)
    metrics_90 = extract_metrics(report_90)
    
    # Step 2: Work with README.wip
    content = readme_wip_path.read_text()
    import re
    
    # Update the Report Date line
    updated_content = re.sub(
        r'\*\*Report Date:\*\* .*',
        f'**Report Date:** {data_date}',
        content
    )
    
    # Update metrics table using markers
    if metrics_30 or metrics_90:
        downloads_30 = metrics_30.get('downloads', '*Pending*') if metrics_30 else '*Pending*'
        downloads_90 = metrics_90.get('downloads', '*Pending*') if metrics_90 else '*Pending*'
        countries_30 = metrics_30.get('countries', '-') if metrics_30 else '-'
        countries_90 = metrics_90.get('countries', '-') if metrics_90 else '-'
        ci_30 = f"{metrics_30.get('ci_pct', '-')}%" if metrics_30 and 'ci_pct' in metrics_30 else '-'
        ci_90 = f"{metrics_90.get('ci_pct', '-')}%" if metrics_90 and 'ci_pct' in metrics_90 else '-'
        uv_30 = f"{metrics_30.get('uv_pct', '-')}%" if metrics_30 and 'uv_pct' in metrics_30 else '-'
        uv_90 = f"{metrics_90.get('uv_pct', '-')}%" if metrics_90 and 'uv_pct' in metrics_90 else '-'
        mcp_30 = metrics_30.get('mcp_count', '-') if metrics_30 else '-'
        mcp_90 = metrics_90.get('mcp_count', '-') if metrics_90 else '-'
        
        # Replace metrics table between markers
        metrics_table = f'''| Metric | 30 Days | 90 Days |
|--------|---------|---------|
| **Total Downloads** | {downloads_30} | {downloads_90} |
| **Countries Reached** | {countries_30} | {countries_90} |
| **CI/CD Installs** | {ci_30} | {ci_90} |
| **UV Adoption** | {uv_30} | {uv_90} |
| **Confirmed MCP Usage** | {mcp_30} | {mcp_90} |'''
        
        updated_content = re.sub(
            r'<!-- METRICS_TABLE_START -->.*?<!-- METRICS_TABLE_END -->',
            f'<!-- METRICS_TABLE_START -->\n{metrics_table}\n<!-- METRICS_TABLE_END -->',
            updated_content,
            flags=re.DOTALL
        )
        
        # Generate geographic insights from actual country data
        if countries_30_file.exists() and countries_90_file.exists():
            # Parse country data from the markdown tables
            countries_30_data = countries_30_file.read_text().strip().split('\n')
            countries_90_data = countries_90_file.read_text().strip().split('\n')
            
            # Extract top country and percentage from first row
            if len(countries_30_data) > 0:
                parts_30 = countries_30_data[0].split('|')
                top_country_30 = parts_30[1].strip() if len(parts_30) > 1 else 'US'
                top_pct_30 = parts_30[3].strip() if len(parts_30) > 3 else '~90%'
            else:
                top_country_30, top_pct_30 = 'US', '~90%'
            
            if len(countries_90_data) > 0:
                parts_90 = countries_90_data[0].split('|')
                top_pct_90 = parts_90[3].strip() if len(parts_90) > 3 else '~90%'
            else:
                top_pct_90 = '~90%'
            
            # Get region representation from top 10
            asia_pacific = []
            europe = []
            for row in countries_30_data[:10]:
                parts = row.split('|')
                if len(parts) > 1:
                    country = parts[1].strip()
                    if country in ['SG', 'CN', 'JP', 'TW', 'KR', 'IN', 'HK']:
                        asia_pacific.append(country)
                    elif country in ['GB', 'DE', 'FR', 'ES', 'IT', 'NL', 'SE', 'CH', 'PT', 'IE']:
                        europe.append(country)
            
            countries_30_val = int(metrics_30.get('countries', '0')) if metrics_30 else 0
            countries_90_val = int(metrics_90.get('countries', '0')) if metrics_90 else 0
            
            insights = ['**Key Insights:**']
            insights.append(f'- **{top_country_30} dominance** ({top_pct_30} in 30d, {top_pct_90} in 90d) consistent across periods')
            
            if asia_pacific:
                insights.append(f'- **Asia-Pacific presence** ({", ".join(asia_pacific)}) shows international adoption')
            
            if europe:
                insights.append(f'- **European adoption** across {", ".join(europe)}')
            
            insights.append(f'- **{countries_30_val} countries (30d), {countries_90_val} countries (90d)** demonstrates global reach')
            
            geo_insights = '\n'.join(insights)
            
            updated_content = re.sub(
                r'<!-- GEO_INSIGHTS_START -->.*?<!-- GEO_INSIGHTS_END -->',
                f'<!-- GEO_INSIGHTS_START -->\n{geo_insights}\n<!-- GEO_INSIGHTS_END -->',
                updated_content,
                flags=re.DOTALL
            )
        
        # Update 30-day countries table from pre-generated file
        if countries_30_file.exists():
            countries_rows_30 = countries_30_file.read_text().strip()
            countries_table_30 = f'''| Country | Downloads | % |
|---------|-----------|---|
{countries_rows_30}'''
            updated_content = re.sub(
                r'<!-- COUNTRIES_30_START -->.*?<!-- COUNTRIES_30_END -->',
                f'<!-- COUNTRIES_30_START -->\n{countries_table_30}\n<!-- COUNTRIES_30_END -->',
                updated_content,
                flags=re.DOTALL
            )
        
        # Update 90-day countries table from pre-generated file
        if countries_90_file.exists():
            countries_rows_90 = countries_90_file.read_text().strip()
            countries_table_90 = f'''| Country | Downloads | % |
|---------|-----------|---|
{countries_rows_90}'''
            updated_content = re.sub(
                r'<!-- COUNTRIES_90_START -->.*?<!-- COUNTRIES_90_END -->',
                f'<!-- COUNTRIES_90_START -->\n{countries_table_90}\n<!-- COUNTRIES_90_END -->',
                updated_content,
                flags=re.DOTALL
            )
        
        # Update UV non-CI stats for 30-day
        if metrics_30 and 'uv_non_ci' in metrics_30:
            uv_non_ci_30 = f"UV: {metrics_30['uv_non_ci_pct']}% non-CI ({metrics_30['uv_non_ci']} downloads)"
            updated_content = re.sub(
                r'<!-- UV_NON_CI_30_START -->.*?<!-- UV_NON_CI_30_END -->',
                f'<!-- UV_NON_CI_30_START -->\n{uv_non_ci_30}\n<!-- UV_NON_CI_30_END -->',
                updated_content,
                flags=re.DOTALL
            )
        
        # Update UV non-CI stats for 90-day
        if metrics_90 and 'uv_non_ci' in metrics_90:
            uv_non_ci_90 = f"UV: {metrics_90['uv_non_ci_pct']}% non-CI ({metrics_90['uv_non_ci']} downloads)"
            updated_content = re.sub(
                r'<!-- UV_NON_CI_90_START -->.*?<!-- UV_NON_CI_90_END -->',
                f'<!-- UV_NON_CI_90_START -->\n{uv_non_ci_90}\n<!-- UV_NON_CI_90_END -->',
                updated_content,
                flags=re.DOTALL
            )
        
        # Update UVX download counts for 30-day
        if metrics_30 and 'uvx_count' in metrics_30:
            uvx_30 = f"**{metrics_30['uvx_count']:,} uvx downloads** = HIGH confidence MCP"
            updated_content = re.sub(
                r'<!-- UVX_30_START -->.*?<!-- UVX_30_END -->',
                f'<!-- UVX_30_START -->\n{uvx_30}\n<!-- UVX_30_END -->',
                updated_content,
                flags=re.DOTALL
            )
        
        # Update UVX download counts for 90-day
        if metrics_90 and 'uvx_count' in metrics_90:
            uvx_90_count = metrics_90['uvx_count']
            uvx_90 = f"**{uvx_90_count:,} uvx downloads** = HIGH confidence MCP"
            
            updated_content = re.sub(
                r'<!-- UVX_90_START -->.*?<!-- UVX_90_END -->',
                f'<!-- UVX_90_START -->\n{uvx_90}\n<!-- UVX_90_END -->',
                updated_content,
                flags=re.DOTALL
            )
        
        # Update UV installer percentages for 30-day
        if metrics_30 and 'uv_total' in metrics_30 and 'total_downloads' in metrics_30:
            uv_count = metrics_30['uv_total']
            total = metrics_30['total_downloads']
            uv_pct = (uv_count / total * 100) if total > 0 else 0
            uv_installer_30 = f"UV: {uv_pct:.1f}% of downloads ({uv_count:,})"
            updated_content = re.sub(
                r'<!-- UV_INSTALLER_30_START -->.*?<!-- UV_INSTALLER_30_END -->',
                f'<!-- UV_INSTALLER_30_START -->\n{uv_installer_30}\n<!-- UV_INSTALLER_30_END -->',
                updated_content,
                flags=re.DOTALL
            )
        
        # Update UV installer percentages for 90-day
        if metrics_90 and 'uv_total' in metrics_90 and 'total_downloads' in metrics_90:
            uv_count = metrics_90['uv_total']
            total = metrics_90['total_downloads']
            uv_pct = (uv_count / total * 100) if total > 0 else 0
            uv_installer_90 = f"UV: {uv_pct:.1f}% of downloads ({uv_count:,})"
            updated_content = re.sub(
                r'<!-- UV_INSTALLER_90_START -->.*?<!-- UV_INSTALLER_90_END -->',
                f'<!-- UV_INSTALLER_90_START -->\n{uv_installer_90}\n<!-- UV_INSTALLER_90_END -->',
                updated_content,
                flags=re.DOTALL
            )
        
        # Update MCP findings for 30-day
        if metrics_30 and 'uvx_count' in metrics_30 and 'uv_total' in metrics_30 and 'total_downloads' in metrics_30:
            uvx = metrics_30['uvx_count']
            uv_total = metrics_30['uv_total']
            total = metrics_30['total_downloads']
            uv_pct = (uv_total / total * 100) if total > 0 else 0
            uv_non_ci_pct = metrics_30.get('uv_non_ci_pct', 0)
            
            mcp_findings_30 = f'''1. **Confirmed MCP Usage:** {uvx:,} downloads using `uvx` subcommand
2. **UV Adoption:** {uv_pct:.1f}% of downloads
3. **Interactive Usage:** {uv_non_ci_pct}% of UV downloads are non-CI

MCP usage is detectable but small. The broader story is UV's growth as a modern Python installer.'''
            
            updated_content = re.sub(
                r'<!-- MCP_FINDINGS_30_START -->.*?<!-- MCP_FINDINGS_30_END -->',
                f'<!-- MCP_FINDINGS_30_START -->\n{mcp_findings_30}\n<!-- MCP_FINDINGS_30_END -->',
                updated_content,
                flags=re.DOTALL
            )
        
        # Update MCP findings for 90-day
        if metrics_90 and 'uvx_count' in metrics_90 and 'uv_total' in metrics_90 and 'total_downloads' in metrics_90:
            uvx = metrics_90['uvx_count']
            uv_total = metrics_90['uv_total']
            total = metrics_90['total_downloads']
            uv_pct = (uv_total / total * 100) if total > 0 else 0
            uv_non_ci_pct = metrics_90.get('uv_non_ci_pct', 0)
            
            mcp_findings_90 = f'''1. **Confirmed MCP Usage:** {uvx:,} downloads using `uvx` subcommand
2. **UV Adoption:** {uv_pct:.1f}% of downloads
3. **Interactive Usage:** {uv_non_ci_pct}% of UV downloads are non-CI

MCP usage is detectable but small. The broader story is UV's growth as a modern Python installer.'''
            
            updated_content = re.sub(
                r'<!-- MCP_FINDINGS_90_START -->.*?<!-- MCP_FINDINGS_90_END -->',
                f'<!-- MCP_FINDINGS_90_START -->\n{mcp_findings_90}\n<!-- MCP_FINDINGS_90_END -->',
                updated_content,
                flags=re.DOTALL
            )
        
        # Update daily trend descriptions for 30-day
        if metrics_30 and 'uvx_count' in metrics_30:
            uvx_30 = metrics_30['uvx_count']
            daily_trend_30 = f"{uvx_30:,} uvx downloads over 30 days"
            updated_content = re.sub(
                r'<!-- DAILY_TREND_30_START -->.*?<!-- DAILY_TREND_30_END -->',
                f'<!-- DAILY_TREND_30_START -->\n{daily_trend_30}\n<!-- DAILY_TREND_30_END -->',
                updated_content,
                flags=re.DOTALL
            )
        
        # Update daily trend descriptions for 90-day
        if metrics_90 and 'uvx_count' in metrics_90:
            uvx_90 = metrics_90['uvx_count']
            daily_trend_90 = f"{uvx_90:,} uvx downloads over 90 days"
            updated_content = re.sub(
                r'<!-- DAILY_TREND_90_START -->.*?<!-- DAILY_TREND_90_END -->',
                f'<!-- DAILY_TREND_90_START -->\n{daily_trend_90}\n<!-- DAILY_TREND_90_END -->',
                updated_content,
                flags=re.DOTALL
            )
    
    if updated_content != content:
        # Step 3: Write updated content to README.wip
        readme_wip_path.write_text(updated_content)
        print(f"✓ Updated README.wip with data date, metrics, top countries, UV stats, and MCP findings")
        
        # Step 4: Leave README.wip in place for atomic swap by workflow
        print(f"✓ README.wip updated and ready for atomic swap\n")
    else:
        print("⚠ Could not update README.wip\n")
        # Clean up README.wip on failure
        if readme_wip_path.exists():
            readme_wip_path.unlink()


def print_summary(df: pd.DataFrame, package: str, days: int):
    """Print summary metrics."""
    total = df['downloads'].sum()
    countries = df['country_code'].nunique()
    
    installers = df.groupby('installer')['downloads'].sum().sort_values(ascending=False)
    uv_total = installers.get('uv', 0)
    uv_pct = (uv_total / total * 100) if total > 0 else 0
    
    uv_subcmds = df[df['installer'] == 'uv'].groupby('subcommand')['downloads'].sum()
    uvx_count = uv_subcmds.get('uvx', 0)
    
    ci_total = df[df['is_ci'] == True]['downloads'].sum()
    ci_pct = (ci_total / total * 100) if total > 0 else 0
    
    print(f"\n{'='*70}")
    print(f"SUMMARY METRICS")
    print(f"{'='*70}")
    print(f"Total Downloads:    {total:>12,}")
    print(f"Countries Reached:  {countries:>12,}")
    print(f"UV Adoption:        {uv_pct:>11.1f}%")
    print(f"CI/CD Installs:     {ci_pct:>11.1f}%")
    print(f"MCP (uvx):          {uvx_count:>12,} ({uvx_count/total*100:.2f}%)")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description="Generate PyPI analytics from BigQuery with daily caching")
    parser.add_argument("--package", required=True, help="PyPI package name")
    parser.add_argument("--days", type=int, default=30, help="Days to analyze (default: 30)")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--credentials", default=None, help="Service account JSON path (optional)")
    parser.add_argument("--output-dir", default="reports", help="Output directory (default: reports)")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching (force fresh query)")
    
    args = parser.parse_args()
    
    if args.credentials and not os.path.exists(args.credentials):
        print(f"ERROR: Credentials file not found: {args.credentials}")
        sys.exit(1)
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Query data (will use cache if available for today)
    client = make_client(args.project, args.credentials)
    df, data_date = query_all_data(client, args.package, args.days, use_cache=not args.no_cache)
    
    # Generate all outputs
    generate_text_report(df, args.package, args.days, output_dir, data_date)
    generate_quarterly_version_trends(client, args.package, output_dir)
    generate_world_map(df, args.package, args.days, output_dir)
    generate_top_countries_tables(df, args.package, args.days, output_dir)
    generate_mcp_analysis(df, args.package, args.days, output_dir)
    generate_deployment_chart(df, args.package, args.days, output_dir)
    
    # Generate deployment environment analysis
    generate_deployment_types(df, args.package, args.days, output_dir)
    generate_architecture_distribution(df, args.package, args.days, output_dir)
    generate_enterprise_cloud_analysis(df, args.package, args.days, output_dir)
    generate_libc_distribution(df, args.package, args.days, output_dir)
    generate_deployment_use_cases(df, args.package, args.days, output_dir)
    generate_deployment_summary(df, args.package, args.days, output_dir)
    
    # Update README only on 90-day run (after both 30 and 90 day reports exist)
    if args.days == 90:
        update_readme(args.package, data_date, output_dir)
    
    # Print summary
    print_summary(df, args.package, args.days)
    
    print(f"✓ All analytics generated in: {output_dir}/\n")


if __name__ == "__main__":
    main()

# Made with Bob
