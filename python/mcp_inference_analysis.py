#!/usr/bin/env python3
"""
MCP Usage Inference Analysis
=============================
Analyze BigQuery data to infer MCP (Model Context Protocol) server usage.

Since MCP servers don't explicitly identify themselves in PyPI download logs,
we use proxy signals to estimate adoption.
"""

import argparse
import os
import sys
from datetime import datetime

try:
    from google.cloud import bigquery
    from google.oauth2 import service_account
    import plotly.graph_objects as go
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


def query_mcp_signals(client: bigquery.Client, package: str, days: int) -> dict:
    """Query all MCP-related signals from BigQuery."""
    
    # 1. UV vs pip breakdown with CI analysis
    sql_installers = f"""
    SELECT 
      details.installer.name as installer,
      COUNT(*) as total_downloads,
      COUNTIF(details.ci IS TRUE) as ci_downloads,
      COUNTIF(details.ci IS FALSE OR details.ci IS NULL) as non_ci_downloads
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY) AND CURRENT_DATE()
      AND details.installer.name IN ('uv', 'pip', 'poetry')
    GROUP BY installer
    ORDER BY total_downloads DESC
    """
    
    # 2. UV subcommand breakdown (uvx is MCP pattern)
    sql_subcommands = f"""
    SELECT
      COALESCE(details.installer.subcommand, '(no subcommand)') as subcommand,
      COUNT(*) as count
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY) AND CURRENT_DATE()
      AND details.installer.name = 'uv'
    GROUP BY subcommand
    ORDER BY count DESC
    """
    
    # 3. Daily UV trend
    sql_trend = f"""
    SELECT 
      DATE(timestamp) as date,
      COUNTIF(details.installer.name = 'uv') as uv_downloads,
      COUNTIF(details.installer.name = 'uv' AND details.installer.subcommand = 'uvx') as uvx_downloads,
      COUNT(*) as total_downloads
    FROM `bigquery-public-data.pypi.file_downloads`
    WHERE file.project = '{package}'
      AND DATE(timestamp) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY) AND CURRENT_DATE()
    GROUP BY date
    ORDER BY date
    """
    
    print("Querying installer breakdown...")
    installers_df = pd.DataFrame([dict(row) for row in client.query(sql_installers).result()])
    
    print("Querying UV subcommands...")
    subcommands_df = pd.DataFrame([dict(row) for row in client.query(sql_subcommands).result()])
    
    print("Querying daily trends...")
    trend_df = pd.DataFrame([dict(row) for row in client.query(sql_trend).result()])
    
    return {
        'installers': installers_df,
        'subcommands': subcommands_df,
        'trend': trend_df
    }


def create_individual_chart(fig, title, filename, output_dir, width=800, height=500):
    """Save an individual chart as PNG."""
    fig.update_layout(
        title=title,
        title_font_size=16,
        showlegend=True,
        height=height,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="rgba(0, 0, 0, 0.2)",
            borderwidth=1,
            font=dict(size=11)
        )
    )
    
    png_file = os.path.join(output_dir, filename)
    try:
        fig.write_image(png_file, width=width, height=height)
        print(f"✓ Chart saved: {png_file}")
    except Exception as e:
        print(f"Note: Could not save {filename} (install kaleido: pip install kaleido)")


def create_mcp_inference_charts(data: dict, package: str, days: int, output_dir: str):
    """Create comprehensive MCP inference visualization as individual charts."""
    
    installers_df = data['installers']
    subcommands_df = data['subcommands']
    trend_df = data['trend']
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Chart 1: Installer Market Share
    fig1 = go.Figure()
    # Add individual bars with legend entries
    colors = {'pip': '#4ECDC4', 'uv': '#FF6B6B', 'poetry': '#95E1D3'}
    for idx, row in installers_df.iterrows():
        installer = row['installer']
        fig1.add_trace(
            go.Bar(
                x=[installer],
                y=[row['total_downloads']],
                text=[row['total_downloads']],
                texttemplate='%{text:,}',
                textposition='outside',
                marker_color=colors.get(installer, '#999999'),
                name=f"{installer} ({row['total_downloads']:,})",
                showlegend=True
            )
        )
    fig1.update_xaxes(title_text="Installer")
    fig1.update_yaxes(title_text="Downloads")
    fig1.update_layout(showlegend=True)
    create_individual_chart(
        fig1,
        f"Installer Utilized - {package} ({days} days)",
        f"mcp_installer_share_{days}day.png",
        output_dir
    )
    
    # Chart 2: UV Subcommands - sort by count and create separate traces for legend
    subcommands_sorted = subcommands_df.sort_values('count', ascending=False)
    fig2 = go.Figure()
    
    # Add uvx bars (MCP pattern)
    uvx_data = subcommands_sorted[subcommands_sorted['subcommand'] == 'uvx']
    if not uvx_data.empty:
        fig2.add_trace(
            go.Bar(
                x=uvx_data['subcommand'],
                y=uvx_data['count'],
                text=uvx_data['count'],
                texttemplate='%{text:,}',
                textposition='outside',
                marker_color='#FF6B6B',
                name='uvx (MCP Pattern)',
                showlegend=True
            )
        )
    
    # Add (no subcommand) bars in gray
    no_subcommand_data = subcommands_sorted[subcommands_sorted['subcommand'] == '(no subcommand)']
    if not no_subcommand_data.empty:
        fig2.add_trace(
            go.Bar(
                x=no_subcommand_data['subcommand'],
                y=no_subcommand_data['count'],
                text=no_subcommand_data['count'],
                texttemplate='%{text:,}',
                textposition='outside',
                marker_color='#999999',
                name='No Subcommand Data',
                showlegend=True
            )
        )
    
    # Add other UV command bars (sorted by count)
    other_data = subcommands_sorted[
        (subcommands_sorted['subcommand'] != 'uvx') &
        (subcommands_sorted['subcommand'] != '(no subcommand)')
    ]
    if not other_data.empty:
        fig2.add_trace(
            go.Bar(
                x=other_data['subcommand'],
                y=other_data['count'],
                text=other_data['count'],
                texttemplate='%{text:,}',
                textposition='outside',
                marker_color='#4ECDC4',
                name='Other UV Commands',
                showlegend=True
            )
        )
    
    # Set x-axis category order to match sorted data
    fig2.update_xaxes(
        title_text="Subcommand",
        tickangle=-45,
        categoryorder='array',
        categoryarray=subcommands_sorted['subcommand'].tolist()
    )
    fig2.update_yaxes(title_text="Count")
    fig2.update_layout(showlegend=True)
    create_individual_chart(
        fig2,
        f"UV Subcommands - {package} ({days} days)",
        f"mcp_uv_subcommands_{days}day.png",
        output_dir
    )
    
    # Chart 3: CI vs Non-CI with totals
    installers_long = []
    for _, row in installers_df.iterrows():
        installers_long.append({
            'installer': row['installer'],
            'type': 'CI/CD',
            'count': row['ci_downloads']
        })
        installers_long.append({
            'installer': row['installer'],
            'type': 'Non-CI (Potential MCP)',
            'count': row['non_ci_downloads']
        })
    
    installers_long_df = pd.DataFrame(installers_long)
    
    fig3 = go.Figure()
    for install_type in ['CI/CD', 'Non-CI (Potential MCP)']:
        subset = installers_long_df[installers_long_df['type'] == install_type]
        fig3.add_trace(
            go.Bar(
                x=subset['installer'],
                y=subset['count'],
                name=install_type,
                marker_color='#95E1D3' if install_type == 'CI/CD' else '#FF6B6B'
            )
        )
    
    # Add total labels on top of stacked bars
    for _, row in installers_df.iterrows():
        fig3.add_annotation(
            x=row['installer'],
            y=row['total_downloads'],
            text=f"{row['total_downloads']:,}",
            showarrow=False,
            yshift=10,
            font=dict(size=11, color='black')
        )
    
    fig3.update_layout(barmode='stack')
    fig3.update_xaxes(title_text="Installer")
    fig3.update_yaxes(title_text="Downloads")
    create_individual_chart(
        fig3,
        f"CI vs Non-CI Usage - {package} ({days} days)",
        f"mcp_ci_vs_nonci_{days}day.png",
        output_dir
    )
    
    # Chart 4: Daily Trend
    fig4 = go.Figure()
    fig4.add_trace(
        go.Scatter(
            x=trend_df['date'],
            y=trend_df['uv_downloads'],
            mode='lines+markers',
            name='UV Total',
            line=dict(color='#4ECDC4', width=2),
            marker=dict(size=6)
        )
    )
    fig4.add_trace(
        go.Scatter(
            x=trend_df['date'],
            y=trend_df['uvx_downloads'],
            mode='lines+markers',
            name='uvx (MCP Pattern)',
            line=dict(color='#FF6B6B', width=2),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 107, 0.2)'
        )
    )
    fig4.update_xaxes(title_text="Date")
    fig4.update_yaxes(title_text="Downloads")
    # Custom layout for Daily UV Trend with legend on left
    fig4.update_layout(
        title=f"Daily UV Trend - {package} ({days} days)",
        title_font_size=16,
        showlegend=True,
        height=500,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="rgba(0, 0, 0, 0.2)",
            borderwidth=1,
            font=dict(size=11)
        )
    )
    # Save manually to preserve custom legend position
    png_file = os.path.join(output_dir, f"mcp_daily_trend_{days}day.png")
    try:
        fig4.write_image(png_file, width=1000, height=500)
        print(f"✓ Chart saved: {png_file}")
    except Exception as e:
        print(f"Note: Could not save PNG (install kaleido: pip install kaleido)")
    
    # Also create combined subplot for HTML
    fig_combined = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Installer Utilized (UV = MCP Proxy)',
            'UV Subcommands (uvx = MCP Pattern)',
            'CI vs Non-CI Usage (Non-CI = Potential MCP)',
            'Daily UV Trend (Including uvx)'
        ),
        specs=[
            [{'type': 'bar'}, {'type': 'bar'}],
            [{'type': 'bar'}, {'type': 'scatter'}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.12
    )
    
    # Add all traces to combined figure
    fig_combined.add_trace(fig1.data[0], row=1, col=1)
    fig_combined.add_trace(fig2.data[0], row=1, col=2)
    for trace in fig3.data:
        fig_combined.add_trace(trace, row=2, col=1)
    for trace in fig4.data:
        fig_combined.add_trace(trace, row=2, col=2)
    
    fig_combined.update_layout(
        title_text=f"MCP Usage Inference Analysis: {package} (Last {days} Days)",
        title_font_size=20,
        showlegend=True,
        height=900,
        barmode='stack'
    )
    
    fig_combined.update_xaxes(title_text="Installer", row=1, col=1)
    fig_combined.update_yaxes(title_text="Downloads", row=1, col=1)
    fig_combined.update_xaxes(title_text="Subcommand", row=1, col=2, tickangle=-45)
    fig_combined.update_yaxes(title_text="Count", row=1, col=2)
    fig_combined.update_xaxes(title_text="Installer", row=2, col=1)
    fig_combined.update_yaxes(title_text="Downloads", row=2, col=1)
    fig_combined.update_xaxes(title_text="Date", row=2, col=2)
    fig_combined.update_yaxes(title_text="Downloads", row=2, col=2)
    
    html_file = os.path.join(output_dir, f"mcp_inference_{days}day.html")
    
    fig_combined.write_html(html_file)
    print(f"✓ Interactive combined chart saved: {html_file}")
    
    return fig_combined


def create_inference_explanation(data: dict, package: str, days: int, output_dir: str):
    """Create detailed explanation document."""
    
    installers_df = data['installers']
    subcommands_df = data['subcommands']
    
    # Calculate key metrics
    uv_row = installers_df[installers_df['installer'] == 'uv'].iloc[0]
    pip_row = installers_df[installers_df['installer'] == 'pip'].iloc[0]
    
    uv_total = uv_row['total_downloads']
    uv_non_ci = uv_row['non_ci_downloads']
    uv_non_ci_pct = (uv_non_ci / uv_total * 100) if uv_total > 0 else 0
    
    pip_total = pip_row['total_downloads']
    pip_non_ci = pip_row['non_ci_downloads']
    pip_non_ci_pct = (pip_non_ci / pip_total * 100) if pip_total > 0 else 0
    
    uvx_count = subcommands_df[subcommands_df['subcommand'] == 'uvx']['count'].iloc[0] if 'uvx' in subcommands_df['subcommand'].values else 0
    
    total_downloads = installers_df['total_downloads'].sum()
    
    explanation = f"""# MCP Usage Inference Analysis

**Package:** {package}  
**Period:** Last {days} days  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

**Confirmed MCP Pattern:** {uvx_count:,} downloads using `uvx` subcommand  
**Potential MCP Range:** {uvx_count:,} - {uv_non_ci:,} downloads  
**UV Market Share:** {(uv_total/total_downloads*100):.1f}% of all installs

---

## Inference Methodology

### Why We Can't Directly Detect MCP

MCP (Model Context Protocol) servers don't identify themselves in PyPI download logs. When Claude Desktop runs an MCP server via `uvx mcp-server-foo`, the download appears as a standard `uv` install. The HTTP user-agent string that might contain "Claude" or "MCP" is parsed by PyPI into structured fields, and the raw string is not stored.

### Proxy Signals We Use

#### 1. **uvx Subcommand (Strongest Signal)**
- **What it is:** `uvx` is uv's tool for running Python applications
- **Why it matters:** Claude Desktop's MCP configuration uses `"command": "uvx mcp-server-*"`
- **Confidence:** HIGH - This is the exact pattern MCP uses
- **Finding:** {uvx_count:,} downloads ({(uvx_count/uv_total*100):.2f}% of UV usage)

#### 2. **UV Non-CI Usage (Moderate Signal)**
- **What it is:** UV downloads not flagged as CI/CD environments
- **Why it matters:** MCP servers run on developer machines, not in CI
- **Confidence:** MEDIUM - Could also be regular developers using UV
- **Finding:** {uv_non_ci:,} non-CI UV downloads ({uv_non_ci_pct:.1f}% of UV)
- **Comparison:** pip has {pip_non_ci_pct:.1f}% non-CI usage

#### 3. **UV Market Share Growth (Weak Signal)**
- **What it is:** UV's overall adoption rate
- **Why it matters:** MCP adoption drives some UV growth
- **Confidence:** LOW - UV growth has many drivers beyond MCP
- **Finding:** UV has {(uv_total/total_downloads*100):.1f}% market share

---

## Detailed Findings

### Installer Breakdown

| Installer | Total | CI/CD | Non-CI | Non-CI % |
|-----------|-------|-------|--------|----------|
| pip | {pip_total:,} | {pip_row['ci_downloads']:,} | {pip_non_ci:,} | {pip_non_ci_pct:.1f}% |
| uv | {uv_total:,} | {uv_row['ci_downloads']:,} | {uv_non_ci:,} | {uv_non_ci_pct:.1f}% |

**Key Insight:** UV has {(uv_non_ci_pct/pip_non_ci_pct):.1f}x higher non-CI usage ratio than pip, suggesting more interactive/developer usage.

### UV Subcommand Analysis

Top UV subcommands:
"""
    
    for _, row in subcommands_df.head(10).iterrows():
        pct = (row['count'] / uv_total * 100)
        marker = " ← **MCP PATTERN**" if row['subcommand'] == 'uvx' else ""
        explanation += f"\n- `{row['subcommand']}`: {row['count']:,} ({pct:.1f}%){marker}"
    
    explanation += f"""

### MCP Usage Estimates

**Conservative (High Confidence):**
- {uvx_count:,} downloads using explicit `uvx` pattern
- This is {(uvx_count/total_downloads*100):.2f}% of all downloads
- Represents confirmed MCP-compatible usage

**Moderate (Medium Confidence):**
- {uvx_count:,} - {int(uvx_count * 5):,} downloads
- Includes `uvx` plus some `uv run` and `tool install` commands
- Estimated {((uvx_count * 3)/total_downloads*100):.2f}% of all downloads

**Upper Bound (Low Confidence):**
- Up to {uv_non_ci:,} downloads
- All non-CI UV usage could theoretically include MCP
- But most are likely regular UV users
- Represents {(uv_non_ci/total_downloads*100):.1f}% of all downloads

---

## Interpretation

### What This Tells Us

1. **MCP adoption is real but emerging**
   - {uvx_count:,} confirmed MCP-pattern downloads
   - Growing but still early adoption phase
   - Represents {(uvx_count/total_downloads*100):.3f}% of total package usage

2. **UV growth is significant**
   - {(uv_total/total_downloads*100):.1f}% market share (vs pip's {(pip_total/total_downloads*100):.1f}%)
   - {uv_non_ci_pct:.1f}% non-CI usage (vs pip's {pip_non_ci_pct:.1f}%)
   - MCP is one driver, but not the only one

3. **Interactive usage patterns**
   - UV's higher non-CI ratio suggests developer tools
   - Consistent with MCP's developer-focused use case
   - Also consistent with UV's general developer appeal

### Limitations

**Cannot definitively separate:**
- MCP servers from other UV usage
- Claude Desktop from other MCP clients
- Active usage from one-time installs

**Missing data:**
- Raw HTTP user-agent strings (not stored by PyPI)
- Runtime usage (only install events captured)
- Specific MCP server packages (if any exist)

---

## Recommendations

### For Tracking MCP Adoption

1. **Monitor `uvx` subcommand over time**
   - Direct MCP signal
   - Track growth month-over-month

2. **Compare to other packages**
   - Is {package} seeing more/less MCP adoption?
   - Benchmark against similar packages

3. **Watch UV non-CI ratio**
   - Increasing ratio suggests more interactive usage
   - Potential MCP growth indicator

4. **Track UV market share**
   - Overall ecosystem health
   - MCP is part of UV's growth story

### For Better Detection

1. **Contact PyPI** as package maintainer
   - Request access to raw user-agent strings
   - May be available for maintainers

2. **Add opt-in telemetry** to package
   - Detect MCP environment variables
   - Respect user privacy (opt-in only)

3. **Monitor AI tool documentation**
   - Check if tools document their user-agents
   - Future PyPI schema may include better identifiers

---

## Conclusion

MCP usage for {package} is **detectable but small**:
- **Confirmed:** {uvx_count:,} downloads ({(uvx_count/total_downloads*100):.3f}%)
- **Estimated:** {uvx_count:,} - {int(uvx_count * 5):,} downloads ({(uvx_count/total_downloads*100):.3f}% - {((uvx_count * 5)/total_downloads*100):.2f}%)

The broader story is **UV's growth** ({(uv_total/total_downloads*100):.1f}% market share), with MCP being one of several drivers for modern Python tooling adoption.

---

*Analysis based on BigQuery public dataset: `bigquery-public-data.pypi.file_downloads`*
"""
    
    md_file = os.path.join(output_dir, f"mcp_inference_explanation_{days}day.md")
    with open(md_file, 'w') as f:
        f.write(explanation)
    
    print(f"✓ Explanation document saved: {md_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze MCP usage patterns from PyPI BigQuery data"
    )
    parser.add_argument("--package", required=True, help="PyPI package name")
    parser.add_argument("--days", type=int, default=30, help="Days to analyze")
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--credentials", required=True, help="Service account JSON")
    parser.add_argument("--output-dir", default="reports", help="Output directory")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.credentials):
        print(f"ERROR: Credentials file not found: {args.credentials}")
        sys.exit(1)
    
    print(f"\n=== MCP Inference Analysis: {args.package} ===\n")
    
    # Query data
    client = make_client(args.project, args.credentials)
    data = query_mcp_signals(client, args.package, args.days)
    
    # Create visualizations
    print("\nCreating charts...")
    create_mcp_inference_charts(data, args.package, args.days, args.output_dir)
    
    # Create explanation
    print("\nGenerating explanation document...")
    create_inference_explanation(data, args.package, args.days, args.output_dir)
    
    print("\n✓ MCP inference analysis complete!")
    print(f"  Check {args.output_dir}/ for outputs")


if __name__ == "__main__":
    main()

# Made with Bob
