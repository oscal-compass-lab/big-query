#!/usr/bin/env python3
"""
Deployment Environment Visualization
=====================================
Generate charts showing deployment environment insights from BigQuery data:
- Cloud provider distribution
- Container vs VM breakdown
- Architecture distribution
- Enterprise vs cloud-native
- Geographic deployment patterns
- libc distribution (container signal)

Usage:
    python visualize_deployment.py --package compliance-trestle --days 30 \
        --project my-project-id --credentials credentials.json \
        --output-dir reports
"""

import argparse
import os
import sys
from datetime import datetime

try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import pandas as pd
except ImportError:
    print("ERROR: Missing dependencies. Run: make venv")
    sys.exit(1)


def make_client(project: str, credentials_path: str) -> bigquery.Client:
    """Create BigQuery client."""
    creds = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=["https://www.googleapis.com/auth/bigquery"],
    )
    return bigquery.Client(project=project, credentials=creds)


def run_query(client: bigquery.Client, sql: str) -> pd.DataFrame:
    """Run query and return as DataFrame."""
    print(f"Querying BigQuery...")
    job = client.query(sql)
    df = job.result().to_dataframe()
    mb = job.total_bytes_processed / 1_000_000 if job.total_bytes_processed else 0
    print(f"Data processed: {mb:.1f} MB\n")
    return df


def chart_cloud_providers(client, package, days, output_dir):
    """Chart cloud provider distribution."""
    sql = f"""
    SELECT
        CASE
            WHEN details.distro.name LIKE '%Amazon%' OR details.distro.name LIKE '%amzn%' THEN 'AWS'
            WHEN details.distro.name LIKE '%Alpine%' THEN 'Containers (Alpine)'
            WHEN details.distro.name LIKE '%Red Hat%' OR details.distro.name LIKE '%RHEL%' THEN 'Enterprise (RHEL)'
            WHEN details.distro.name LIKE '%Ubuntu%' THEN 'Ubuntu'
            WHEN details.distro.name LIKE '%Debian%' THEN 'Debian'
            WHEN details.distro.name = 'macOS' THEN 'macOS'
            WHEN details.system.name = 'Windows' THEN 'Windows'
            WHEN details.distro.name LIKE '%Oracle%' THEN 'Oracle Cloud'
            ELSE 'Other Linux'
        END AS platform,
        COUNT(*) AS downloads
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY) AND CURRENT_DATE()
    GROUP BY platform
    ORDER BY downloads DESC
    """
    
    df = run_query(client, sql)
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=df['platform'],
        values=df['downloads'],
        hole=0.3,
        marker=dict(colors=px.colors.qualitative.Set3)
    )])
    
    fig.update_layout(
        title=f'Platform Distribution — {package} (Last {days} Days)',
        font=dict(size=14),
        height=500
    )
    
    filename = f"{output_dir}/deployment_platforms_{days}day"
    fig.write_html(f"{filename}.html")
    try:
        fig.write_image(f"{filename}.png", width=1000, height=600)
        print(f"✓ Saved: {filename}.png")
    except:
        pass
    print(f"✓ Saved: {filename}.html")


def chart_container_vs_vm(client, package, days, output_dir):
    """Chart container vs VM deployment."""
    sql = f"""
    SELECT
        CASE
            WHEN details.distro.libc.lib = 'musl' THEN 'Containers (musl)'
            WHEN details.distro.name LIKE '%Alpine%' THEN 'Containers (Alpine)'
            WHEN details.distro.name LIKE '%Amazon%' AND details.ci = TRUE THEN 'AWS CI/CD'
            WHEN details.distro.name LIKE '%Amazon%' THEN 'AWS VMs'
            WHEN details.distro.name LIKE '%Red Hat%' OR details.distro.name LIKE '%RHEL%' THEN 'Enterprise VMs'
            WHEN details.distro.name LIKE '%Ubuntu%' AND details.ci = TRUE THEN 'CI Pipelines'
            WHEN details.distro.name LIKE '%Ubuntu%' THEN 'Ubuntu VMs'
            WHEN details.distro.name = 'macOS' THEN 'Developer Macs'
            WHEN details.system.name = 'Windows' THEN 'Windows'
            ELSE 'Other'
        END AS deployment_type,
        COUNT(*) AS downloads
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY) AND CURRENT_DATE()
    GROUP BY deployment_type
    ORDER BY downloads DESC
    """
    
    df = run_query(client, sql)
    
    # Create horizontal bar chart with colorbar
    fig = go.Figure(data=[go.Bar(
        y=df['deployment_type'],
        x=df['downloads'],
        orientation='h',
        marker=dict(
            color=df['downloads'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title="Downloads",
                thickness=15,
                len=0.5,
                x=1.02,
                xanchor='left'
            )
        ),
        text=df['downloads'].apply(lambda x: f'{x:,}'),
        textposition='auto'
    )])
    
    fig.update_layout(
        title=f'Deployment Types — {package} (Last {days} Days)',
        xaxis_title='Downloads',
        yaxis_title='',
        font=dict(size=12),
        height=500,
        showlegend=False
    )
    
    filename = f"{output_dir}/deployment_types_{days}day"
    fig.write_html(f"{filename}.html")
    try:
        fig.write_image(f"{filename}.png", width=1000, height=600)
        print(f"✓ Saved: {filename}.png")
    except:
        pass
    print(f"✓ Saved: {filename}.html")


def chart_architecture_distribution(client, package, days, output_dir):
    """Chart CPU architecture distribution."""
    sql = f"""
    SELECT
        details.cpu AS architecture,
        CASE
            WHEN details.distro.name LIKE '%Amazon%' THEN 'AWS'
            WHEN details.distro.name LIKE '%Alpine%' THEN 'Containers'
            WHEN details.distro.name = 'macOS' THEN 'macOS'
            WHEN details.system.name = 'Windows' THEN 'Windows'
            ELSE 'Other Linux'
        END AS platform,
        COUNT(*) AS downloads
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY) AND CURRENT_DATE()
      AND details.cpu IS NOT NULL
    GROUP BY architecture, platform
    ORDER BY downloads DESC
    """
    
    df = run_query(client, sql)
    
    # Create stacked bar chart
    fig = px.bar(df, x='architecture', y='downloads', color='platform',
                 title=f'CPU Architecture by Platform — {package} (Last {days} Days)',
                 labels={'downloads': 'Downloads', 'architecture': 'CPU Architecture'},
                 color_discrete_sequence=px.colors.qualitative.Set2)
    
    fig.update_layout(
        font=dict(size=12),
        height=500,
        xaxis_title='CPU Architecture',
        yaxis_title='Downloads'
    )
    
    filename = f"{output_dir}/deployment_architecture_{days}day"
    fig.write_html(f"{filename}.html")
    try:
        fig.write_image(f"{filename}.png", width=1000, height=600)
        print(f"✓ Saved: {filename}.png")
    except:
        pass
    print(f"✓ Saved: {filename}.html")


def chart_geographic_deployment(client, package, days, output_dir):
    """Chart geographic distribution by deployment type."""
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
        COUNT(*) AS downloads
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY) AND CURRENT_DATE()
      AND country_code IN (
          SELECT country_code
          FROM `bigquery-public-data.pypi.file_downloads`
          WHERE file.project = '{package}'
            AND DATE(timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY) AND CURRENT_DATE()
          GROUP BY country_code
          ORDER BY COUNT(*) DESC
          LIMIT 15
      )
    GROUP BY country_code, platform
    ORDER BY downloads DESC
    """
    
    df = run_query(client, sql)
    
    # Create grouped bar chart
    fig = px.bar(df, x='country_code', y='downloads', color='platform',
                 title=f'Top 15 Countries by Deployment Type — {package} (Last {days} Days)',
                 labels={'downloads': 'Downloads', 'country_code': 'Country'},
                 color_discrete_sequence=px.colors.qualitative.Pastel,
                 barmode='stack')
    
    fig.update_layout(
        font=dict(size=12),
        height=500,
        xaxis_title='Country Code',
        yaxis_title='Downloads'
    )
    
    filename = f"{output_dir}/deployment_geographic_{days}day"
    fig.write_html(f"{filename}.html")
    try:
        fig.write_image(f"{filename}.png", width=1200, height=600)
        print(f"✓ Saved: {filename}.png")
    except:
        pass
    print(f"✓ Saved: {filename}.html")


def chart_enterprise_vs_cloud(client, package, days, output_dir):
    """Chart enterprise vs cloud-native patterns."""
    sql = f"""
    SELECT
        CASE
            WHEN details.distro.name LIKE '%Red Hat%' OR details.distro.name LIKE '%RHEL%' THEN 'Enterprise'
            WHEN details.distro.name LIKE '%Oracle%' THEN 'Enterprise'
            WHEN details.distro.name LIKE '%SUSE%' THEN 'Enterprise'
            WHEN details.distro.name LIKE '%Alpine%' THEN 'Cloud-Native'
            WHEN details.distro.name LIKE '%Amazon%' AND details.ci = TRUE THEN 'Cloud-Native'
            WHEN details.distro.name LIKE '%Ubuntu%' AND details.ci = TRUE THEN 'Cloud-Native'
            WHEN details.distro.name = 'macOS' THEN 'Developer'
            WHEN details.system.name = 'Windows' THEN 'Corporate'
            ELSE 'Other'
        END AS category,
        details.ci AS is_ci,
        COUNT(*) AS downloads
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY) AND CURRENT_DATE()
    GROUP BY category, is_ci
    ORDER BY downloads DESC
    """
    
    df = run_query(client, sql)
    # Convert is_ci boolean to string labels
    df['ci_label'] = df['is_ci'].astype(str).replace({'True': 'CI/CD', 'False': 'Interactive', '<NA>': 'Unknown', 'None': 'Unknown'})
    
    # Filter out rows with empty category
    df = df[(df['category'].notna()) & (df['category'] != '')]
    
    # Create sunburst chart
    fig = px.sunburst(df, path=['category', 'ci_label'], values='downloads',
                      title=f'Enterprise vs Cloud-Native — {package} (Last {days} Days)',
                      color='downloads',
                      color_continuous_scale='RdYlGn')
    
    fig.update_layout(
        font=dict(size=12),
        height=600
    )
    
    filename = f"{output_dir}/deployment_enterprise_cloud_{days}day"
    fig.write_html(f"{filename}.html")
    try:
        fig.write_image(f"{filename}.png", width=1000, height=700)
        print(f"✓ Saved: {filename}.png")
    except:
        pass
    print(f"✓ Saved: {filename}.html")


def chart_libc_distribution(client, package, days, output_dir):
    """Chart libc distribution (container signal)."""
    sql = f"""
    SELECT
        details.distro.libc.lib AS libc,
        details.distro.name AS distro,
        COUNT(*) AS downloads
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY) AND CURRENT_DATE()
      AND details.distro.libc.lib IS NOT NULL
    GROUP BY libc, distro
    ORDER BY downloads DESC
    LIMIT 20
    """
    
    df = run_query(client, sql)
    
    if df.empty:
        print("No libc data available")
        return
    
    # Create treemap
    fig = px.treemap(df, path=['libc', 'distro'], values='downloads',
                     title=f'libc Distribution (Container Signal) — {package} (Last {days} Days)',
                     color='downloads',
                     color_continuous_scale='Blues')
    
    fig.update_layout(
        font=dict(size=12),
        height=600
    )
    
    filename = f"{output_dir}/deployment_libc_{days}day"
    fig.write_html(f"{filename}.html")
    try:
        fig.write_image(f"{filename}.png", width=1000, height=700)
        print(f"✓ Saved: {filename}.png")
    except:
        pass
    print(f"✓ Saved: {filename}.html")


def chart_compliance_use_cases(client, package, days, output_dir):
    """Chart compliance-trestle specific use cases."""
    sql = f"""
    SELECT
        CASE
            WHEN details.distro.name LIKE '%Alpine%' AND details.ci = TRUE THEN 'C2P Pipeline'
            WHEN details.distro.name LIKE '%Amazon%' AND details.ci = TRUE THEN 'AWS Automation'
            WHEN details.distro.name LIKE '%Red Hat%' THEN 'Gov/DoD Compliance'
            WHEN details.distro.name LIKE '%Ubuntu%' AND details.ci = TRUE THEN 'CI Compliance'
            WHEN details.distro.name = 'macOS' THEN 'Development'
            WHEN details.system.name = 'Windows' THEN 'SDK Usage'
            ELSE 'Other'
        END AS use_case,
        COUNT(*) AS downloads
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY) AND CURRENT_DATE()
    GROUP BY use_case
    ORDER BY downloads DESC
    """
    
    df = run_query(client, sql)
    
    # Create donut chart
    fig = go.Figure(data=[go.Pie(
        labels=df['use_case'],
        values=df['downloads'],
        hole=0.4,
        marker=dict(colors=px.colors.qualitative.Pastel1)
    )])
    
    fig.update_layout(
        title=f'Compliance Use Cases — {package} (Last {days} Days)',
        font=dict(size=14),
        height=500,
        annotations=[dict(text='Use Cases', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    filename = f"{output_dir}/deployment_use_cases_{days}day"
    fig.write_html(f"{filename}.html")
    try:
        fig.write_image(f"{filename}.png", width=1000, height=600)
        print(f"✓ Saved: {filename}.png")
    except:
        pass
    print(f"✓ Saved: {filename}.html")


def create_summary_dashboard(client, package, days, output_dir):
    """Create a summary dashboard with bar charts."""
    # Get summary stats
    sql = f"""
    SELECT
        COUNT(*) AS total_downloads,
        COUNTIF(details.distro.name LIKE '%Alpine%') AS alpine,
        COUNTIF(details.distro.name LIKE '%Amazon%') AS aws,
        COUNTIF(details.distro.name LIKE '%Red Hat%' OR details.distro.name LIKE '%RHEL%') AS rhel,
        COUNTIF(details.ci = TRUE) AS ci,
        COUNTIF(details.cpu IN ('aarch64', 'arm64')) AS arm,
        COUNTIF(details.distro.libc.lib = 'musl') AS musl
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY) AND CURRENT_DATE()
    """
    
    stats = run_query(client, sql).iloc[0]
    total = stats['total_downloads']
    
    # Create data for visualization
    metrics = {
        'Containers (Alpine)': stats['alpine'],
        'AWS (Amazon Linux)': stats['aws'],
        'Enterprise (RHEL)': stats['rhel'],
        'CI/CD Pipelines': stats['ci'],
        'ARM Architecture': stats['arm'],
        'Containers (musl)': stats['musl']
    }
    
    # Calculate percentages
    df = pd.DataFrame([
        {'Metric': k, 'Downloads': v, 'Percentage': (v/total*100) if total > 0 else 0}
        for k, v in metrics.items()
    ])
    
    # Create horizontal bar chart with percentages
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df['Metric'],
        x=df['Percentage'],
        orientation='h',
        text=[f"{row['Downloads']:,} ({row['Percentage']:.1f}%)"
              for _, row in df.iterrows()],
        textposition='auto',
        marker=dict(
            color=df['Percentage'],
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="Percentage")
        ),
        hovertemplate='<b>%{y}</b><br>Downloads: %{text}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'Deployment Summary — {package} (Last {days} Days)<br>Total Downloads: {total:,}',
        xaxis_title='Percentage of Total Downloads',
        yaxis_title='',
        font=dict(size=12),
        height=500,
        showlegend=False,
        xaxis=dict(range=[0, max(df['Percentage']) * 1.1])
    )
    
    filename = f"{output_dir}/deployment_summary_{days}day"
    fig.write_html(f"{filename}.html")
    try:
        fig.write_image(f"{filename}.png", width=1000, height=600)
        print(f"✓ Saved: {filename}.png")
    except:
        pass
    print(f"✓ Saved: {filename}.html")


def main():
    parser = argparse.ArgumentParser(
        description="Generate deployment environment visualizations"
    )
    parser.add_argument("--package", required=True, help="PyPI package name")
    parser.add_argument("--days", type=int, default=30, help="Days to look back")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--credentials", required=True, help="Service account JSON")
    parser.add_argument("--output-dir", default="reports", help="Output directory")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.credentials):
        print(f"ERROR: Credentials file not found: {args.credentials}")
        sys.exit(1)
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"\n{'='*70}")
    print(f"Deployment Environment Visualization")
    print(f"Package: {args.package}")
    print(f"Period: Last {args.days} days")
    print(f"Output: {args.output_dir}/")
    print(f"{'='*70}\n")
    
    client = make_client(args.project, args.credentials)
    
    # Generate all charts
    print("1. Creating platform distribution chart...")
    chart_cloud_providers(client, args.package, args.days, args.output_dir)
    
    print("\n2. Creating deployment types chart...")
    chart_container_vs_vm(client, args.package, args.days, args.output_dir)
    
    print("\n3. Creating architecture distribution chart...")
    chart_architecture_distribution(client, args.package, args.days, args.output_dir)
    
    print("\n4. Creating geographic deployment chart...")
    chart_geographic_deployment(client, args.package, args.days, args.output_dir)
    
    print("\n5. Creating enterprise vs cloud-native chart...")
    chart_enterprise_vs_cloud(client, args.package, args.days, args.output_dir)
    
    print("\n6. Creating libc distribution chart...")
    chart_libc_distribution(client, args.package, args.days, args.output_dir)
    
    print("\n7. Creating compliance use cases chart...")
    chart_compliance_use_cases(client, args.package, args.days, args.output_dir)
    
    print("\n8. Creating summary dashboard...")
    create_summary_dashboard(client, args.package, args.days, args.output_dir)
    
    print(f"\n{'='*70}")
    print(f"✓ All charts generated in: {args.output_dir}/")
    print(f"  - deployment_platforms_{args.days}day.html/png")
    print(f"  - deployment_types_{args.days}day.html/png")
    print(f"  - deployment_architecture_{args.days}day.html/png")
    print(f"  - deployment_geographic_{args.days}day.html/png")
    print(f"  - deployment_enterprise_cloud_{args.days}day.html/png")
    print(f"  - deployment_libc_{args.days}day.html/png")
    print(f"  - deployment_use_cases_{args.days}day.html/png")
    print(f"  - deployment_summary_{args.days}day.html/png")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()

# Made with Bob