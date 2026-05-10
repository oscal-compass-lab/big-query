#!/usr/bin/env python3
"""
PyPI BigQuery Analytics
=======================
Query Google BigQuery's public PyPI download dataset.

Usage (via Makefile):
    make countries
    make ci
    make query-all

Direct usage:
    python query.py all --package compliance-trestle --days 30 \
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


# ── Individual queries ────────────────────────────────────────────────────────

def query_total(client, package, days):
    sql = f"""
    SELECT COUNT(*) AS total_downloads
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    """
    rows = run_query(client, sql)
    total = rows[0]["total_downloads"] if rows else 0
    console.print(
        f"[bold]Total downloads of [cyan]{package}[/cyan] "
        f"in the last {days} days:[/bold] [bold green]{total:,}[/bold green]\n"
    )


def query_countries(client, package, days):
    sql = f"""
    SELECT
        country_code,
        COUNT(*) AS download_count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY country_code
    ORDER BY download_count DESC
    LIMIT 200
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"Downloads by Country — {package} (last {days} days)", rows,
                highlight_col="download_count")


def query_os(client, package, days):
    sql = f"""
    SELECT
        details.system.name   AS os,
        details.distro.name   AS distro,
        COUNT(*) AS download_count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY os, distro
    ORDER BY download_count DESC
    LIMIT 20
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"Downloads by OS/Distro — {package} (last {days} days)", rows)


def query_versions(client, package, days):
    sql = f"""
    SELECT
        file.version AS version,
        COUNT(*) AS download_count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY version
    ORDER BY download_count DESC
    LIMIT 20
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"Downloads by Package Version — {package} (last {days} days)", rows)


def query_ci(client, package, days):
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
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY details.ci
    ORDER BY download_count DESC
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"CI vs Human Downloads — {package} (last {days} days)", rows)
    console.print(
        "[dim]Tip: CI/CD installs from pipelines inflate raw download counts.[/dim]\n"
    )


def query_installer(client, package, days):
    sql = f"""
    SELECT
        COALESCE(details.installer.name, 'Unknown') AS installer,
        COUNT(*) AS download_count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY installer
    ORDER BY download_count DESC
    LIMIT 15
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"Downloads by Installer — {package} (last {days} days)", rows)


def query_python_version(client, package, days):
    sql = f"""
    SELECT
        REGEXP_EXTRACT(details.python, r'^(\\d+\\.\\d+)') AS python_version,
        COUNT(*) AS download_count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
      AND details.python IS NOT NULL
    GROUP BY python_version
    ORDER BY download_count DESC
    LIMIT 15
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"Downloads by Python Version — {package} (last {days} days)", rows)


def query_trend(client, package, days):
    sql = f"""
    SELECT
        DATE(timestamp) AS date,
        COUNT(*) AS download_count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
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

        console.print(f"[bold cyan]Daily Trend — {package} (last {days} days)[/bold cyan]")
        console.print("[dim](most recent → oldest)[/dim]")

        spark = "".join(blocks[int(c / max_c * 8)] for c in counts)
        console.print(f"\n  {spark}\n")
        console.print(f"  Peak: [green]{max(counts):,}[/green]  "
                      f"Min: [red]{min(counts):,}[/red]  "
                      f"Avg: [yellow]{sum(counts)//len(counts):,}[/yellow]\n")

    fmt_count(rows)
    print_table(f"Daily Downloads — {package}", rows)  # show all days


# ── CLI ───────────────────────────────────────────────────────────────────────

QUERIES = {
    "total":          query_total,
    "countries":      query_countries,
    "os":             query_os,
    "versions":       query_versions,
    "ci":             query_ci,
    "installer":      query_installer,
    "python_version": query_python_version,
    "trend":          query_trend,
}

ALL_ORDER = ["total", "ci", "countries", "os", "installer",
             "python_version", "versions", "trend"]


def main():
    parser = argparse.ArgumentParser(
        description="Query PyPI download stats via Google BigQuery"
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

    console.rule(f"[bold cyan]PyPI Analytics: {args.package}[/bold cyan]")
    client = make_client(args.project, args.credentials)

    if args.report == "all":
        for name in ALL_ORDER:
            console.rule(f"[dim]{name}[/dim]")
            QUERIES[name](client, args.package, args.days)
    else:
        QUERIES[args.report](client, args.package, args.days)


if __name__ == "__main__":
    main()
