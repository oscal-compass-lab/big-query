#!/usr/bin/env python3
"""
USA-Specific PyPI Download Analytics
=====================================
Detailed breakdown of downloads from the United States, including:
- OS/Distribution breakdown within USA
- CI vs Human usage in USA
- Installer preferences in USA
- Python version adoption in USA
- CPU architecture distribution in USA
- Time-based patterns for USA downloads
- Regional inference from distro/OS patterns

Usage:
    python query_usa_details.py all --package compliance-trestle --days 30 \
        --project my-project-id --credentials credentials.json
"""

import argparse
import os
import sys

try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    from rich.console import Console
    from rich.table import Table
    from rich import box
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


# ── USA-specific queries ──────────────────────────────────────────────────────

def query_usa_total(client, package, days):
    """Total downloads from USA with percentage of global downloads."""
    sql_usa = f"""
    SELECT COUNT(*) AS usa_downloads
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND country_code = 'US'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    """
    
    sql_global = f"""
    SELECT COUNT(*) AS global_downloads
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    """
    
    usa_rows = run_query(client, sql_usa)
    global_rows = run_query(client, sql_global)
    
    usa_count = usa_rows[0]["usa_downloads"] if usa_rows else 0
    global_count = global_rows[0]["global_downloads"] if global_rows else 0
    pct = (usa_count / global_count * 100) if global_count > 0 else 0
    
    console.print(
        f"[bold]USA Downloads of [cyan]{package}[/cyan] "
        f"in the last {days} days:[/bold]\n"
        f"  USA: [bold green]{usa_count:,}[/bold green]\n"
        f"  Global: [yellow]{global_count:,}[/yellow]\n"
        f"  USA Share: [bold blue]{pct:.1f}%[/bold blue]\n"
    )


def query_usa_os_distro(client, package, days):
    """Detailed OS and distribution breakdown for USA downloads."""
    sql = f"""
    SELECT
        details.system.name AS os,
        details.distro.name AS distro,
        details.distro.version AS distro_version,
        COUNT(*) AS download_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND country_code = 'US'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY os, distro, distro_version
    ORDER BY download_count DESC
    LIMIT 30
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"USA: OS/Distribution Breakdown — {package} (last {days} days)", rows)
    
    # Regional inference
    console.print("\n[bold yellow]Regional Insights:[/bold yellow]")
    console.print("[dim]Linux distros may indicate cloud/enterprise usage[/dim]")
    console.print("[dim]macOS suggests developer/corporate environments[/dim]")
    console.print("[dim]Windows indicates enterprise/desktop usage[/dim]\n")


def query_usa_ci_breakdown(client, package, days):
    """CI vs Human usage specifically in USA."""
    sql = f"""
    SELECT
        CASE
            WHEN details.ci IS NULL THEN 'Unknown'
            WHEN details.ci = TRUE  THEN 'CI/CD Pipeline'
            ELSE 'Human / Interactive'
        END AS source,
        COUNT(*) AS download_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND country_code = 'US'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY details.ci
    ORDER BY download_count DESC
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"USA: CI vs Human Downloads — {package} (last {days} days)", rows)


def query_usa_installer(client, package, days):
    """Installer tool preferences in USA."""
    sql = f"""
    SELECT
        COALESCE(details.installer.name, 'Unknown') AS installer,
        details.installer.version AS version,
        COUNT(*) AS download_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND country_code = 'US'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY installer, version
    ORDER BY download_count DESC
    LIMIT 20
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"USA: Installer Tools — {package} (last {days} days)", rows)


def query_usa_python_version(client, package, days):
    """Python version adoption in USA."""
    sql = f"""
    SELECT
        REGEXP_EXTRACT(details.python, r'^(\\d+\\.\\d+)') AS python_version,
        COUNT(*) AS download_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND country_code = 'US'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
      AND details.python IS NOT NULL
    GROUP BY python_version
    ORDER BY download_count DESC
    LIMIT 15
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"USA: Python Version Distribution — {package} (last {days} days)", rows)


def query_usa_cpu_arch(client, package, days):
    """CPU architecture distribution in USA."""
    sql = f"""
    SELECT
        details.cpu AS cpu_arch,
        details.system.name AS os,
        COUNT(*) AS download_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND country_code = 'US'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
      AND details.cpu IS NOT NULL
    GROUP BY cpu_arch, os
    ORDER BY download_count DESC
    LIMIT 20
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"USA: CPU Architecture — {package} (last {days} days)", rows)
    
    console.print("\n[bold yellow]Architecture Insights:[/bold yellow]")
    console.print("[dim]arm64 on Darwin = Apple Silicon Macs[/dim]")
    console.print("[dim]x86_64 dominance = Traditional Intel/AMD systems[/dim]")
    console.print("[dim]arm64 on Linux = Cloud ARM instances (AWS Graviton, etc.)[/dim]\n")


def query_usa_time_patterns(client, package, days):
    """Download patterns by time of day and day of week in USA."""
    sql = f"""
    SELECT
        EXTRACT(HOUR FROM timestamp) AS hour_utc,
        EXTRACT(DAYOFWEEK FROM timestamp) AS day_of_week,
        COUNT(*) AS download_count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND country_code = 'US'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY hour_utc, day_of_week
    ORDER BY download_count DESC
    LIMIT 30
    """
    rows = fmt_count(run_query(client, sql))
    
    # Convert day_of_week to names
    day_names = {1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 
                 5: 'Thursday', 6: 'Friday', 7: 'Saturday'}
    for row in rows:
        if 'day_of_week' in row:
            row['day_name'] = day_names.get(row['day_of_week'], 'Unknown')
    
    print_table(f"USA: Download Patterns by Time — {package} (last {days} days)", rows)
    
    console.print("\n[bold yellow]Time Pattern Insights:[/bold yellow]")
    console.print("[dim]Note: Times are in UTC. USA spans UTC-5 to UTC-8[/dim]")
    console.print("[dim]Business hours (9am-5pm ET) = 14:00-22:00 UTC[/dim]")
    console.print("[dim]Business hours (9am-5pm PT) = 17:00-01:00 UTC[/dim]\n")


def query_usa_package_versions(client, package, days):
    """Package version adoption in USA."""
    sql = f"""
    SELECT
        file.version AS version,
        COUNT(*) AS download_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND country_code = 'US'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY version
    ORDER BY download_count DESC
    LIMIT 20
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"USA: Package Version Distribution — {package} (last {days} days)", rows)


def query_usa_daily_trend(client, package, days):
    """Daily download trend for USA."""
    sql = f"""
    SELECT
        DATE(timestamp) AS date,
        COUNT(*) AS download_count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND country_code = 'US'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY date
    ORDER BY date DESC
    """
    rows = run_query(client, sql)

    # ASCII sparkline
    if rows:
        counts = [r["download_count"] for r in rows]
        max_c = max(counts) or 1
        blocks = " ▁▂▃▄▅▆▇█"

        console.print(f"[bold cyan]USA Daily Trend — {package} (last {days} days)[/bold cyan]")
        console.print("[dim](most recent → oldest)[/dim]")

        spark = "".join(blocks[int(c / max_c * 8)] for c in counts)
        console.print(f"\n  {spark}\n")
        console.print(f"  Peak: [green]{max(counts):,}[/green]  "
                      f"Min: [red]{min(counts):,}[/red]  "
                      f"Avg: [yellow]{sum(counts)//len(counts):,}[/yellow]\n")

    fmt_count(rows)
    print_table(f"USA Daily Downloads — {package}", rows)


def query_usa_enterprise_indicators(client, package, days):
    """Indicators of enterprise vs individual usage in USA."""
    sql = f"""
    SELECT
        CASE
            WHEN details.distro.name LIKE '%Red Hat%' OR details.distro.name LIKE '%RHEL%' THEN 'Enterprise Linux (RHEL)'
            WHEN details.distro.name LIKE '%Ubuntu%' THEN 'Ubuntu'
            WHEN details.distro.name LIKE '%Debian%' THEN 'Debian'
            WHEN details.distro.name LIKE '%Amazon%' THEN 'Amazon Linux (AWS)'
            WHEN details.distro.name = 'macOS' THEN 'macOS'
            WHEN details.system.name = 'Windows' THEN 'Windows'
            WHEN details.system.name = 'Linux' THEN 'Other Linux'
            ELSE 'Other/Unknown'
        END AS platform_category,
        details.ci AS is_ci,
        COUNT(*) AS download_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND country_code = 'US'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY platform_category, is_ci
    ORDER BY download_count DESC
    LIMIT 25
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"USA: Enterprise vs Individual Indicators — {package} (last {days} days)", rows)
    
    console.print("\n[bold yellow]Enterprise Indicators:[/bold yellow]")
    console.print("[dim]RHEL/Amazon Linux + CI = Enterprise cloud deployments[/dim]")
    console.print("[dim]macOS + non-CI = Individual developers[/dim]")
    console.print("[dim]Windows + non-CI = Corporate desktops[/dim]")
    console.print("[dim]Ubuntu + CI = Startup/SMB cloud infrastructure[/dim]\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

QUERIES = {
    "total":       query_usa_total,
    "os":          query_usa_os_distro,
    "ci":          query_usa_ci_breakdown,
    "installer":   query_usa_installer,
    "python":      query_usa_python_version,
    "cpu":         query_usa_cpu_arch,
    "time":        query_usa_time_patterns,
    "versions":    query_usa_package_versions,
    "trend":       query_usa_daily_trend,
    "enterprise":  query_usa_enterprise_indicators,
}

ALL_ORDER = ["total", "os", "ci", "installer", "python", "cpu", 
             "enterprise", "time", "versions", "trend"]


def main():
    parser = argparse.ArgumentParser(
        description="USA-specific PyPI download analytics via Google BigQuery"
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

    console.rule(f"[bold cyan]USA PyPI Analytics: {args.package}[/bold cyan]")
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