#!/usr/bin/env python3
"""
Advanced PyPI BigQuery Analytics
=================================
Extended queries to extract detailed download information including:
- User agent analysis (MCP servers, automation tools, endpoints)
- Implementation details (libraries, frameworks)
- Referrer information
- Download patterns and anomalies

Usage:
    python query_advanced.py user_agents --package compliance-trestle --days 30 \
        --project my-project-id --credentials credentials.json
"""

import argparse
import os
import sys
import re
from collections import Counter

try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    from rich.console import Console
    from rich.table import Table
    from rich import box
    import pandas as pd
except ImportError:
    print("ERROR: Missing dependencies. Run: make venv")
    sys.exit(1)

console = Console()

# ── BigQuery client ───────────────────────────────────────────────────────────

def make_client(project: str, credentials_path: str) -> bigquery.Client:
    creds = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=["https://www.googleapis.com/auth/bigquery"],
    )
    return bigquery.Client(project=project, credentials=creds)


# ── Query runner ──────────────────────────────────────────────────────────────

def run_query(client: bigquery.Client, sql: str) -> list[dict]:
    console.print(f"[dim]Querying BigQuery...[/dim]")
    job = client.query(sql)
    rows = list(job.result())
    mb = job.total_bytes_processed / 1_000_000 if job.total_bytes_processed else 0
    console.print(f"[dim]Data processed: {mb:.1f} MB[/dim]\n")
    return [dict(row) for row in rows]


# ── Pretty printer ────────────────────────────────────────────────────────────

def print_table(title: str, rows: list[dict], highlight_col: str = None):
    if not rows:
        console.print(f"[yellow]No data returned for: {title}[/yellow]")
        return

    table = Table(title=title, box=box.ROUNDED, show_lines=False,
                  title_style="bold cyan")

    columns = list(rows[0].keys())
    for col in columns:
        style = "bold green" if col == highlight_col else ""
        table.add_column(col.replace("_", " ").title(), style=style)

    for row in rows:
        table.add_row(*[str(v) if v is not None else "—" for v in row.values()])

    console.print(table)


def fmt_count(rows: list[dict]) -> list[dict]:
    """Add comma formatting to download_count column."""
    for row in rows:
        if "download_count" in row:
            row["download_count"] = f"{row['download_count']:,}"
    return rows


# ── Advanced queries ──────────────────────────────────────────────────────────

def query_user_agents(client, package, days):
    """Analyze user agent strings to identify tools, automation, and endpoints."""
    sql = f"""
    SELECT
        details.installer.user_agent AS user_agent,
        COUNT(*) AS download_count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
      AND details.installer.user_agent IS NOT NULL
    GROUP BY user_agent
    ORDER BY download_count DESC
    LIMIT 100
    """
    rows = fmt_count(run_query(client, sql))
    
    # Analyze user agents for patterns
    console.print(f"[bold cyan]User Agent Analysis — {package} (last {days} days)[/bold cyan]\n")
    
    # Categorize user agents
    categories = {
        'MCP/AI Tools': [],
        'CI/CD Systems': [],
        'Package Managers': [],
        'Automation/Scripts': [],
        'Browsers': [],
        'Other': []
    }
    
    for row in rows:
        ua = row.get('user_agent', '').lower()
        count = row.get('download_count', '0').replace(',', '')
        
        if any(x in ua for x in ['mcp', 'claude', 'anthropic', 'openai', 'copilot', 'cursor']):
            categories['MCP/AI Tools'].append((row['user_agent'], count))
        elif any(x in ua for x in ['github', 'gitlab', 'jenkins', 'circleci', 'travis', 'azure']):
            categories['CI/CD Systems'].append((row['user_agent'], count))
        elif any(x in ua for x in ['pip', 'uv', 'poetry', 'conda', 'pipenv']):
            categories['Package Managers'].append((row['user_agent'], count))
        elif any(x in ua for x in ['python-requests', 'urllib', 'curl', 'wget', 'httpx']):
            categories['Automation/Scripts'].append((row['user_agent'], count))
        elif any(x in ua for x in ['mozilla', 'chrome', 'safari', 'firefox', 'edge']):
            categories['Browsers'].append((row['user_agent'], count))
        else:
            categories['Other'].append((row['user_agent'], count))
    
    # Print categorized results
    for category, items in categories.items():
        if items:
            console.print(f"\n[bold yellow]{category}:[/bold yellow]")
            for ua, count in items[:10]:  # Top 10 per category
                console.print(f"  {count:>10} - {ua[:80]}")
    
    print_table(f"Top User Agents — {package} (last {days} days)", rows[:50])


def query_implementation_details(client, package, days):
    """Extract implementation details from user agents and system info."""
    sql = f"""
    SELECT
        details.implementation.name AS implementation,
        details.implementation.version AS impl_version,
        COUNT(*) AS download_count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
      AND details.implementation.name IS NOT NULL
    GROUP BY implementation, impl_version
    ORDER BY download_count DESC
    LIMIT 30
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"Python Implementation Details — {package} (last {days} days)", rows)


def query_download_patterns(client, package, days):
    """Identify unusual download patterns that might indicate specific use cases."""
    sql = f"""
    SELECT
        EXTRACT(HOUR FROM timestamp) AS hour_of_day,
        EXTRACT(DAYOFWEEK FROM timestamp) AS day_of_week,
        COUNT(*) AS download_count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY hour_of_day, day_of_week
    ORDER BY download_count DESC
    LIMIT 50
    """
    rows = fmt_count(run_query(client, sql))
    
    # Convert day_of_week to names
    day_names = {1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 
                 5: 'Thursday', 6: 'Friday', 7: 'Saturday'}
    for row in rows:
        if 'day_of_week' in row:
            row['day_name'] = day_names.get(row['day_of_week'], 'Unknown')
    
    print_table(f"Download Patterns by Time — {package} (last {days} days)", rows)


def query_endpoint_analysis(client, package, days):
    """Analyze download endpoints and file types."""
    sql = f"""
    SELECT
        file.filename AS filename,
        file.type AS file_type,
        COUNT(*) AS download_count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY filename, file_type
    ORDER BY download_count DESC
    LIMIT 30
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"File Downloads by Type — {package} (last {days} days)", rows)


def query_tls_versions(client, package, days):
    """Analyze TLS versions used for downloads (security insight)."""
    sql = f"""
    SELECT
        details.tls_protocol AS tls_version,
        details.tls_cipher AS tls_cipher,
        COUNT(*) AS download_count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
      AND details.tls_protocol IS NOT NULL
    GROUP BY tls_version, tls_cipher
    ORDER BY download_count DESC
    LIMIT 20
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"TLS Protocol Usage — {package} (last {days} days)", rows)


def query_cpu_architecture(client, package, days):
    """Analyze CPU architectures downloading the package."""
    sql = f"""
    SELECT
        details.system.name AS os,
        details.cpu AS cpu_arch,
        COUNT(*) AS download_count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
      AND details.cpu IS NOT NULL
    GROUP BY os, cpu_arch
    ORDER BY download_count DESC
    LIMIT 25
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"CPU Architecture Distribution — {package} (last {days} days)", rows)


def query_setuptools_version(client, package, days):
    """Analyze setuptools versions (indicates environment maturity)."""
    sql = f"""
    SELECT
        REGEXP_EXTRACT(details.setuptools_version, r'^(\\d+\\.\\d+)') AS setuptools_major,
        COUNT(*) AS download_count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
      AND details.setuptools_version IS NOT NULL
    GROUP BY setuptools_major
    ORDER BY download_count DESC
    LIMIT 20
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"Setuptools Version Distribution — {package} (last {days} days)", rows)


def query_unique_ips(client, package, days):
    """Estimate unique downloaders by IP (rough proxy for unique users)."""
    sql = f"""
    SELECT
        COUNT(DISTINCT details.installer.user_agent) AS unique_user_agents,
        COUNT(*) AS total_downloads,
        ROUND(COUNT(*) / COUNT(DISTINCT details.installer.user_agent), 1) AS avg_downloads_per_agent
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
      AND details.installer.user_agent IS NOT NULL
    """
    rows = run_query(client, sql)
    
    if rows:
        console.print(f"\n[bold cyan]Unique Downloader Estimate — {package} (last {days} days)[/bold cyan]")
        console.print(f"  Unique User Agents: [green]{rows[0]['unique_user_agents']:,}[/green]")
        console.print(f"  Total Downloads: [yellow]{rows[0]['total_downloads']:,}[/yellow]")
        console.print(f"  Avg Downloads per Agent: [blue]{rows[0]['avg_downloads_per_agent']}[/blue]")
        console.print(f"\n[dim]Note: This is a rough estimate. Same user agent can represent multiple users.[/dim]\n")


def query_raw_sample(client, package, days, limit=10):
    """Get raw sample records to see all available fields."""
    sql = f"""
    SELECT *
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    LIMIT {limit}
    """
    rows = run_query(client, sql)
    
    console.print(f"\n[bold cyan]Sample Raw Records — {package}[/bold cyan]")
    console.print(f"[dim]Showing {len(rows)} sample records with all available fields[/dim]\n")
    
    for i, row in enumerate(rows, 1):
        console.print(f"[bold yellow]Record {i}:[/bold yellow]")
        for key, value in sorted(row.items()):
            if value is not None:
                console.print(f"  {key}: {value}")
        console.print()


# ── CLI ───────────────────────────────────────────────────────────────────────

QUERIES = {
    "user_agents":      query_user_agents,
    "implementation":   query_implementation_details,
    "patterns":         query_download_patterns,
    "endpoints":        query_endpoint_analysis,
    "tls":              query_tls_versions,
    "cpu":              query_cpu_architecture,
    "setuptools":       query_setuptools_version,
    "unique":           query_unique_ips,
    "raw_sample":       query_raw_sample,
}

ALL_ORDER = ["unique", "user_agents", "implementation", "endpoints", 
             "cpu", "patterns", "tls", "setuptools"]


def main():
    parser = argparse.ArgumentParser(
        description="Advanced PyPI download analytics via Google BigQuery"
    )
    parser.add_argument(
        "report",
        choices=list(QUERIES.keys()) + ["all"],
        help="Which report to run"
    )
    parser.add_argument("--package",     required=True, help="PyPI package name")
    parser.add_argument("--days",        type=int, default=30,
                        help="Number of days to look back (default: 30)")
    parser.add_argument("--project",     required=True, help="GCP project ID")
    parser.add_argument("--credentials", required=True,
                        help="Path to service account JSON key file")

    args = parser.parse_args()

    if not os.path.exists(args.credentials):
        console.print(f"[red]ERROR:[/red] Credentials file not found: {args.credentials}")
        console.print("  Run: [bold]make credentials[/bold]")
        sys.exit(1)

    console.rule(f"[bold cyan]Advanced PyPI Analytics: {args.package}[/bold cyan]")
    client = make_client(args.project, args.credentials)

    if args.report == "all":
        for name in ALL_ORDER:
            console.rule(f"[dim]{name}[/dim]")
            QUERIES[name](client, args.package, args.days)
    else:
        QUERIES[args.report](client, args.package, args.days)


if __name__ == "__main__":
    main()

# Made with Bob
