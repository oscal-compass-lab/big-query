#!/usr/bin/env python3
"""
Deployment Environment Analysis
================================
Analyze deployment environments using real BigQuery signals:
- Cloud provider detection via distro.name (Amazon Linux, Alpine, etc.)
- Container vs VM vs bare metal inference
- Enterprise vs cloud-native patterns
- Architecture distribution (x86_64 vs aarch64/Graviton)
- CI/CD pipeline types

Optimized for compliance-trestle's C2P/Kyverno use cases.

Usage:
    python query_deployment_environments.py all --package compliance-trestle --days 30 \
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

def print_table(title: str, rows: list[dict], highlight_col: str | None = None):
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


# ── Deployment environment queries ────────────────────────────────────────────

def query_cloud_providers(client, package, days):
    """Detect cloud providers via distro.name signatures."""
    sql = f"""
    SELECT
        country_code,
        details.distro.name AS distro,
        details.ci AS is_ci,
        COUNT(*) AS download_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
      AND details.distro.name IS NOT NULL
    GROUP BY country_code, distro, is_ci
    ORDER BY download_count DESC
    LIMIT 50
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"Cloud Provider Detection (via distro.name) — {package} (last {days} days)", rows)
    
    console.print("\n[bold yellow]Cloud Provider Signals:[/bold yellow]")
    console.print("[dim]Amazon Linux / Amazon Linux AMI → AWS EC2[/dim]")
    console.print("[dim]Alpine Linux → Docker/Kubernetes containers[/dim]")
    console.print("[dim]Red Hat Enterprise Linux → Enterprise/OpenShift/DoD[/dim]")
    console.print("[dim]Oracle Linux → Oracle Cloud[/dim]")
    console.print("[dim]Debian → Often GCP Compute Engine[/dim]")
    console.print("[dim]Ubuntu + CI → GitHub Actions / standard CI[/dim]\n")


def query_container_vs_vm(client, package, days):
    """Infer containerized vs VM/bare metal deployments."""
    sql = f"""
    SELECT
        country_code,
        CASE
            WHEN details.distro.name LIKE '%Alpine%' THEN 'Container (Alpine)'
            WHEN details.distro.libc.lib = 'musl' THEN 'Container (musl libc)'
            WHEN details.distro.name LIKE '%Amazon%' AND details.ci = TRUE THEN 'AWS CI/CD'
            WHEN details.distro.name LIKE '%Amazon%' THEN 'AWS EC2 VM'
            WHEN details.distro.name LIKE '%Red Hat%' OR details.distro.name LIKE '%RHEL%' THEN 'Enterprise VM/Bare Metal'
            WHEN details.distro.name LIKE '%Ubuntu%' AND details.ci = TRUE THEN 'CI Pipeline (Ubuntu)'
            WHEN details.distro.name LIKE '%Ubuntu%' THEN 'Ubuntu VM/Desktop'
            WHEN details.distro.name LIKE '%Debian%' THEN 'Debian VM'
            WHEN details.distro.name = 'macOS' THEN 'macOS Developer'
            WHEN details.system.name = 'Windows' THEN 'Windows Desktop/Server'
            ELSE 'Other/Unknown'
        END AS deployment_type,
        COUNT(*) AS download_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY country_code, deployment_type
    ORDER BY download_count DESC
    LIMIT 40
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"Container vs VM Deployment — {package} (last {days} days)", rows)
    
    console.print("\n[bold yellow]Deployment Type Insights:[/bold yellow]")
    console.print("[dim]Alpine/musl → Containerized (Docker/K8s) - C2P use case[/dim]")
    console.print("[dim]AWS CI/CD → Automated compliance pipelines[/dim]")
    console.print("[dim]RHEL → Government/DoD enterprise deployments[/dim]")
    console.print("[dim]macOS → Local development/testing[/dim]\n")


def query_architecture_distribution(client, package, days):
    """Analyze CPU architecture by deployment type."""
    sql = f"""
    SELECT
        details.cpu AS architecture,
        details.distro.name AS distro,
        details.ci AS is_ci,
        country_code,
        COUNT(*) AS download_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
      AND details.cpu IS NOT NULL
    GROUP BY architecture, distro, is_ci, country_code
    ORDER BY download_count DESC
    LIMIT 40
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"Architecture Distribution — {package} (last {days} days)", rows)
    
    console.print("\n[bold yellow]Architecture Insights:[/bold yellow]")
    console.print("[dim]aarch64 + Amazon Linux → AWS Graviton (cost-optimized)[/dim]")
    console.print("[dim]aarch64 + macOS → Apple Silicon developers[/dim]")
    console.print("[dim]x86_64 dominance → Traditional Intel/AMD infrastructure[/dim]")
    console.print("[dim]aarch64 growth → Cloud-native ARM adoption[/dim]\n")


def query_enterprise_indicators(client, package, days):
    """Identify enterprise vs cloud-native patterns."""
    sql = f"""
    SELECT
        country_code,
        CASE
            WHEN details.distro.name LIKE '%Red Hat%' OR details.distro.name LIKE '%RHEL%' THEN 'Enterprise (RHEL)'
            WHEN details.distro.name LIKE '%Oracle%' THEN 'Enterprise (Oracle)'
            WHEN details.distro.name LIKE '%SUSE%' THEN 'Enterprise (SUSE)'
            WHEN details.distro.name LIKE '%Amazon%' AND details.ci = TRUE THEN 'Cloud-Native (AWS CI)'
            WHEN details.distro.name LIKE '%Alpine%' THEN 'Cloud-Native (Containers)'
            WHEN details.distro.name LIKE '%Ubuntu%' AND details.ci = TRUE THEN 'Cloud-Native (CI)'
            WHEN details.distro.name = 'macOS' THEN 'Developer Workstation'
            WHEN details.system.name = 'Windows' AND details.ci = FALSE THEN 'Corporate Desktop'
            ELSE 'Other'
        END AS environment_category,
        COUNT(*) AS download_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY country_code, environment_category
    ORDER BY download_count DESC
    LIMIT 30
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"Enterprise vs Cloud-Native — {package} (last {days} days)", rows)


def query_compliance_use_cases(client, package, days):
    """Infer compliance-trestle specific use cases."""
    sql = f"""
    SELECT
        country_code,
        CASE
            WHEN details.distro.name LIKE '%Alpine%' AND details.ci = TRUE THEN 'C2P Pipeline (Containerized)'
            WHEN details.distro.name LIKE '%Amazon%' AND details.ci = TRUE THEN 'AWS Compliance Automation'
            WHEN details.distro.name LIKE '%Red Hat%' THEN 'Government/DoD Compliance'
            WHEN details.distro.name LIKE '%Ubuntu%' AND details.ci = TRUE THEN 'CI/CD Compliance Checks'
            WHEN details.distro.name = 'macOS' AND details.ci = FALSE THEN 'Compliance Development'
            WHEN details.system.name = 'Windows' AND details.ci = FALSE THEN 'Compliance SDK Usage'
            ELSE 'Other Compliance Use'
        END AS use_case,
        details.installer.name AS installer,
        COUNT(*) AS download_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY country_code, use_case, installer
    ORDER BY download_count DESC
    LIMIT 40
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"Compliance-Trestle Use Cases — {package} (last {days} days)", rows)
    
    console.print("\n[bold yellow]Use Case Insights:[/bold yellow]")
    console.print("[dim]C2P Pipeline → Kyverno policy generation in K8s[/dim]")
    console.print("[dim]AWS Automation → Cloud compliance as code[/dim]")
    console.print("[dim]Government/DoD → OSCAL compliance frameworks[/dim]")
    console.print("[dim]Development → Building compliance tools[/dim]\n")


def query_geographic_deployment(client, package, days):
    """Geographic distribution by deployment type."""
    sql = f"""
    SELECT
        country_code,
        CASE
            WHEN details.distro.name LIKE '%Alpine%' THEN 'Containers'
            WHEN details.distro.name LIKE '%Amazon%' THEN 'AWS'
            WHEN details.distro.name LIKE '%Red Hat%' OR details.distro.name LIKE '%RHEL%' THEN 'Enterprise'
            WHEN details.distro.name = 'macOS' THEN 'Developer'
            WHEN details.system.name = 'Windows' THEN 'Windows'
            ELSE 'Other Linux'
        END AS platform,
        details.ci AS is_ci,
        COUNT(*) AS download_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    GROUP BY country_code, platform, is_ci
    ORDER BY download_count DESC
    LIMIT 50
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"Geographic Distribution by Platform — {package} (last {days} days)", rows)


def query_libc_analysis(client, package, days):
    """Analyze libc distribution (glibc vs musl = container signal)."""
    sql = f"""
    SELECT
        details.distro.libc.lib AS libc,
        details.distro.name AS distro,
        country_code,
        COUNT(*) AS download_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
      AND details.distro.libc.lib IS NOT NULL
    GROUP BY libc, distro, country_code
    ORDER BY download_count DESC
    LIMIT 30
    """
    rows = fmt_count(run_query(client, sql))
    print_table(f"libc Distribution (Container Signal) — {package} (last {days} days)", rows)
    
    console.print("\n[bold yellow]libc Insights:[/bold yellow]")
    console.print("[dim]musl → Alpine Linux containers (Docker/K8s)[/dim]")
    console.print("[dim]glibc → Standard Linux VMs and bare metal[/dim]")
    console.print("[dim]High musl % → Strong containerized deployment[/dim]\n")


def query_summary_stats(client, package, days):
    """High-level deployment environment summary."""
    sql = f"""
    SELECT
        COUNT(*) AS total_downloads,
        COUNT(DISTINCT country_code) AS unique_countries,
        COUNT(DISTINCT details.distro.name) AS unique_distros,
        COUNTIF(details.distro.name LIKE '%Alpine%') AS alpine_downloads,
        COUNTIF(details.distro.name LIKE '%Amazon%') AS aws_downloads,
        COUNTIF(details.distro.name LIKE '%Red Hat%' OR details.distro.name LIKE '%RHEL%') AS rhel_downloads,
        COUNTIF(details.ci = TRUE) AS ci_downloads,
        COUNTIF(details.cpu = 'aarch64' OR details.cpu = 'arm64') AS arm_downloads,
        COUNTIF(details.distro.libc.lib = 'musl') AS musl_downloads
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN
          DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY)
          AND CURRENT_DATE()
    """
    rows = run_query(client, sql)
    
    if rows:
        r = rows[0]
        total = r['total_downloads']
        
        console.print(f"\n[bold cyan]Deployment Environment Summary — {package} (last {days} days)[/bold cyan]\n")
        console.print(f"  Total Downloads: [green]{total:,}[/green]")
        console.print(f"  Unique Countries: [yellow]{r['unique_countries']:,}[/yellow]")
        console.print(f"  Unique Distributions: [blue]{r['unique_distros']:,}[/blue]\n")
        
        console.print("[bold]Deployment Types:[/bold]")
        console.print(f"  Containers (Alpine): [cyan]{r['alpine_downloads']:,}[/cyan] ({r['alpine_downloads']/total*100:.1f}%)")
        console.print(f"  AWS (Amazon Linux): [cyan]{r['aws_downloads']:,}[/cyan] ({r['aws_downloads']/total*100:.1f}%)")
        console.print(f"  Enterprise (RHEL): [cyan]{r['rhel_downloads']:,}[/cyan] ({r['rhel_downloads']/total*100:.1f}%)")
        console.print(f"  CI/CD Pipelines: [cyan]{r['ci_downloads']:,}[/cyan] ({r['ci_downloads']/total*100:.1f}%)")
        console.print(f"  ARM Architecture: [cyan]{r['arm_downloads']:,}[/cyan] ({r['arm_downloads']/total*100:.1f}%)")
        console.print(f"  musl libc (Containers): [cyan]{r['musl_downloads']:,}[/cyan] ({r['musl_downloads']/total*100:.1f}%)\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

QUERIES = {
    "summary":     query_summary_stats,
    "cloud":       query_cloud_providers,
    "containers":  query_container_vs_vm,
    "arch":        query_architecture_distribution,
    "enterprise":  query_enterprise_indicators,
    "use_cases":   query_compliance_use_cases,
    "geographic":  query_geographic_deployment,
    "libc":        query_libc_analysis,
}

ALL_ORDER = ["summary", "cloud", "containers", "arch", "enterprise", 
             "use_cases", "geographic", "libc"]


def main():
    parser = argparse.ArgumentParser(
        description="Deployment environment analysis via Google BigQuery"
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

    console.rule(f"[bold cyan]Deployment Environment Analysis: {args.package}[/bold cyan]")
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