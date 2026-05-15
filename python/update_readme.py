#!/usr/bin/env python3
"""
Update README.md with Latest Metrics
=====================================
Extracts key metrics from generated reports and updates README.md

Usage:
    python update_readme.py --report-30 reports/2026.05.15.trestle.pypi.last-30.txt \
                           --report-90 reports/2026.05.15.trestle.pypi.last-90.txt
"""

import argparse
import re
from datetime import datetime
from pathlib import Path


def extract_total_downloads(report_content: str) -> int:
    """Extract total downloads from report."""
    match = re.search(r'Total downloads.*?:\s*([\d,]+)', report_content, re.IGNORECASE)
    if match:
        return int(match.group(1).replace(',', ''))
    return 0


def extract_countries(report_content: str) -> int:
    """Extract number of countries from report."""
    match = re.search(
        r'(\d+)\s+countries?\s+total',
        report_content,
        re.IGNORECASE
    )
    if match:
        return int(match.group(1))

    match = re.search(
        r'countries?\s+reached.*?\(?up from\s+(\d+)',
        report_content,
        re.IGNORECASE
    )
    if match:
        return int(match.group(1))

    # Fallback: count rows in the countries table (excluding header and separators)
    lines = report_content.split('\n')
    in_countries = False
    country_count = 0
    
    for line in lines:
        if 'Downloads by Country' in line:
            in_countries = True
            continue
        if in_countries:
            if line.strip().startswith('│') and '│' in line[1:]:
                # Skip header row and separator lines
                if not any(x in line.lower() for x in ['country code', 'country_code', '─', '═']):
                    country_count += 1
            elif line.strip() and not line.strip().startswith('│'):
                break
    
    return country_count


def extract_ci_percentage(report_content: str) -> int:
    """Extract CI/CD percentage from report."""
    match = re.search(r'CI/CD Pipeline.*?│\s*([\d,]+).*?│\s*([\d.]+)', report_content)
    if match:
        return int(float(match.group(2)))
    return 0


def extract_uv_percentage(report_content: str) -> float:
    """Extract UV percentage of installer-attributed downloads from report."""
    lines = report_content.split('\n')
    in_installer = False
    total_downloads = 0
    uv_downloads = 0
    
    for line in lines:
        if 'Downloads by Installer' in line:
            in_installer = True
            continue
        if in_installer:
            if line.strip().startswith('│') and '│' in line[1:]:
                parts = [p.strip() for p in line.split('│')]
                if len(parts) >= 3 and parts[1]:
                    # Skip header and separator lines
                    if parts[1].lower() not in ['installer', '─', '═'] and '─' not in parts[1]:
                        try:
                            installer_name = parts[1].lower()
                            download_count = int(parts[2].replace(',', ''))
                            total_downloads += download_count
                            if installer_name == 'uv':
                                uv_downloads = download_count
                        except (ValueError, IndexError):
                            pass
            elif line.strip() and not line.strip().startswith('│'):
                break
    
    if total_downloads > 0:
        return round((uv_downloads / total_downloads) * 100, 1)
    return 0.0


def extract_mcp_usage(report_content: str) -> tuple[int, float]:
    """Extract MCP usage count and percentage from report."""
    # This would need to be extracted from MCP analysis files
    # For now, return placeholder that will be updated by actual MCP analysis
    return 0, 0.0


def update_readme(report_30_path: str, report_90_path: str, readme_path: str = 'README.md'):
    """Update README.md with latest metrics."""
    
    # Read reports
    with open(report_30_path, 'r') as f:
        report_30 = f.read()
    
    with open(report_90_path, 'r') as f:
        report_90 = f.read()
    
    # Extract metrics
    downloads_30 = extract_total_downloads(report_30)
    downloads_90 = extract_total_downloads(report_90)
    countries_30 = extract_countries(report_30)
    countries_90 = extract_countries(report_90)
    ci_30 = extract_ci_percentage(report_30)
    ci_90 = extract_ci_percentage(report_90)
    uv_30 = extract_uv_percentage(report_30)
    uv_90 = extract_uv_percentage(report_90)
    
    # Try to get MCP data from explanation files
    mcp_30_count = 0
    mcp_90_count = 0
    mcp_30_pct = 0.0
    mcp_90_pct = 0.0
    
    try:
        mcp_30_file = Path('reports/mcp_inference_explanation_30day.md')
        if mcp_30_file.exists():
            content = mcp_30_file.read_text()
            match = re.search(r'uvx.*?(\d+)', content)
            if match:
                mcp_30_count = int(match.group(1))
                if downloads_30 > 0:
                    mcp_30_pct = round((mcp_30_count / downloads_30) * 100, 2)
    except:
        pass
    
    try:
        mcp_90_file = Path('reports/mcp_inference_explanation_90day.md')
        if mcp_90_file.exists():
            content = mcp_90_file.read_text()
            match = re.search(r'uvx.*?(\d+)', content)
            if match:
                mcp_90_count = int(match.group(1))
                if downloads_90 > 0:
                    mcp_90_pct = round((mcp_90_count / downloads_90) * 100, 2)
    except:
        pass
    
    # Read current README
    with open(readme_path, 'r') as f:
        readme = f.read()
    
    # Update report date
    current_date = datetime.now().strftime('%B %d, %Y')
    readme = re.sub(
        r'\*\*Report Date:\*\* .*',
        f'**Report Date:** {current_date}',
        readme
    )
    
    # Update metrics table
    metrics_table = f"""| Metric | 30 Days | 90 Days |
|--------|---------|---------|
| **Total Downloads** | {downloads_30:,} | {downloads_90:,} |
| **Countries Reached** | {countries_30} | {countries_90} |
| **CI/CD Installs** | {ci_30}% | {ci_90}% |
| **UV Adoption** | {uv_30}% | {uv_90}% |
| **Confirmed MCP Usage** | {mcp_30_count} ({mcp_30_pct}%) | {mcp_90_count} ({mcp_90_pct}%) |"""
    
    # Replace the metrics table
    readme = re.sub(
        r'\| Metric \| 30 Days \| 90 Days \|.*?\n\| \*\*Confirmed MCP Usage\*\* \|.*?\|.*?\|',
        metrics_table,
        readme,
        flags=re.DOTALL
    )
    
    # Update Platform & Technology Analysis section
    readme = update_platform_analysis(readme, report_30, report_90)
    
    # Write updated README
    with open(readme_path, 'w') as f:
        f.write(readme)
    
    print(f"✓ README.md updated with latest metrics")
    print(f"  Report Date: {current_date}")
    print(f"  30-day downloads: {downloads_30:,}")
    print(f"  90-day downloads: {downloads_90:,}")
    print(f"  Countries (30d): {countries_30}")
    print(f"  Countries (90d): {countries_90}")


def extract_os_data(report_content: str) -> list[tuple[str, int, float]]:
    """Extract OS/Distribution data from report."""
    lines = report_content.split('\n')
    in_os_section = False
    os_data = []
    
    for line in lines:
        if 'Downloads by OS/Distro' in line:
            in_os_section = True
            continue
        if in_os_section:
            if line.strip().startswith('│') and '│' in line[1:]:
                parts = [p.strip() for p in line.split('│')]
                if len(parts) >= 4 and parts[1] and parts[1] not in ['os', 'distro', '─', '═']:
                    try:
                        # Combine OS and distro names
                        os_name = parts[2] if parts[2] and parts[2] != '—' else parts[1]
                        downloads = int(parts[3].replace(',', ''))
                        os_data.append((os_name, downloads))
                    except (ValueError, IndexError):
                        pass
            elif line.strip() and not line.strip().startswith('│'):
                break
    
    # Calculate percentages and return top 8
    total = sum(d for _, d in os_data)
    result = [(name, downloads, round((downloads/total)*100, 1)) for name, downloads in os_data[:8]]
    return result


def extract_python_data(report_content: str) -> list[tuple[str, int, float]]:
    """Extract Python version data from report."""
    lines = report_content.split('\n')
    in_python_section = False
    python_data = []
    
    for line in lines:
        if 'Downloads by Python Version' in line:
            in_python_section = True
            continue
        if in_python_section:
            if line.strip().startswith('│') and '│' in line[1:]:
                parts = [p.strip() for p in line.split('│')]
                if len(parts) >= 3 and parts[1] and parts[1] not in ['python_version', '─', '═']:
                    try:
                        version = parts[1]
                        downloads = int(parts[2].replace(',', ''))
                        python_data.append((version, downloads))
                    except (ValueError, IndexError):
                        pass
            elif line.strip() and not line.strip().startswith('│'):
                break
    
    # Calculate percentages and return top 5
    total = sum(d for _, d in python_data)
    result = [(ver, downloads, round((downloads/total)*100, 1)) for ver, downloads in python_data[:5]]
    return result


def extract_installer_data(report_content: str) -> list[tuple[str, int, float]]:
    """Extract installer data from report."""
    lines = report_content.split('\n')
    in_installer_section = False
    installer_data = []
    
    for line in lines:
        if 'Downloads by Installer' in line:
            in_installer_section = True
            continue
        if in_installer_section:
            if line.strip().startswith('│') and '│' in line[1:]:
                parts = [p.strip() for p in line.split('│')]
                if len(parts) >= 3 and parts[1] and parts[1] not in ['installer', '─', '═']:
                    try:
                        installer = parts[1]
                        downloads = int(parts[2].replace(',', ''))
                        installer_data.append((installer, downloads))
                    except (ValueError, IndexError):
                        pass
            elif line.strip() and not line.strip().startswith('│'):
                break
    
    # Calculate percentages and return top 4
    total = sum(d for _, d in installer_data)
    result = [(name, downloads, round((downloads/total)*100, 1)) for name, downloads in installer_data[:4]]
    return result


def update_platform_analysis(readme: str, report_30: str, report_90: str) -> str:
    """Update Platform & Technology Analysis section."""
    
    # Extract data
    os_30 = extract_os_data(report_30)
    os_90 = extract_os_data(report_90)
    python_30 = extract_python_data(report_30)
    python_90 = extract_python_data(report_90)
    installer_30 = extract_installer_data(report_30)
    installer_90 = extract_installer_data(report_90)
    
    # Build OS table
    os_table = "| OS/Distribution | 30 Days | % | 90 Days | % |\n"
    os_table += "|-----------------|---------|---|---------|---|\n"
    for i in range(min(len(os_30), len(os_90))):
        name_30, dl_30, pct_30 = os_30[i]
        name_90, dl_90, pct_90 = os_90[i]
        # Use name from 30-day (should be same)
        os_table += f"| {name_30} | {dl_30:,} | {pct_30}% | {dl_90:,} | {pct_90}% |\n"
    
    # Build Python table
    python_table = "| Python Version | 30 Days | % | 90 Days | % |\n"
    python_table += "|----------------|---------|---|---------|---|\n"
    for i in range(min(len(python_30), len(python_90))):
        ver_30, dl_30, pct_30 = python_30[i]
        ver_90, dl_90, pct_90 = python_90[i]
        python_table += f"| {ver_30} | {dl_30:,} | {pct_30}% | {dl_90:,} | {pct_90}% |\n"
    
    # Build Installer table
    installer_table = "| Installer | 30 Days | % | 90 Days | % |\n"
    installer_table += "|-----------|---------|---|---------|---|\n"
    for i in range(min(len(installer_30), len(installer_90))):
        name_30, dl_30, pct_30 = installer_30[i]
        name_90, dl_90, pct_90 = installer_90[i]
        installer_table += f"| {name_30} | {dl_30:,} | {pct_30}% | {dl_90:,} | {pct_90}% |\n"
    
    # Replace OS table
    readme = re.sub(
        r'\| OS/Distribution \| 30 Days.*?\n\*\*Key Insights:\*\*',
        os_table + '\n**Key Insights:**',
        readme,
        flags=re.DOTALL
    )
    
    # Replace Python table
    readme = re.sub(
        r'\| Python Version \| 30 Days.*?\n\*\*Key Insights:\*\*',
        python_table + '\n**Key Insights:**',
        readme,
        flags=re.DOTALL
    )
    
    # Replace Installer table
    readme = re.sub(
        r'\| Installer \| 30 Days.*?\n\*\*Key Insights:\*\*',
        installer_table + '\n**Key Insights:**',
        readme,
        flags=re.DOTALL
    )
    
    return readme


def main():
    parser = argparse.ArgumentParser(
        description="Update README.md with latest metrics from reports"
    )
    parser.add_argument('--report-30', required=True, help='Path to 30-day report')
    parser.add_argument('--report-90', required=True, help='Path to 90-day report')
    parser.add_argument('--readme', default='README.md', help='Path to README.md')
    
    args = parser.parse_args()
    
    update_readme(args.report_30, args.report_90, args.readme)


if __name__ == '__main__':
    main()

# Made with Bob
