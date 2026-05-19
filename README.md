# PyPI Download Analytics for compliance-trestle

**Recent insights into PyPI package adoption and usage patterns**

This repository contains automated BigQuery analytics and reports for PyPI packages.

**Report Date:** 2026-05-19

---

## 📊 Version Adoption Trends

*Quarterly download trends by major version over the last 3 years. Shows version adoption patterns and migration trends across releases.*

![Quarterly Version Trends](reports/compliance-trestle_quarterly_versions.png)

---

## 🔑 Key Metrics Summary
<!-- METRICS_TABLE_START -->
| Metric | 30 Days | 90 Days |
|--------|---------|---------|
| **Total Downloads** | 85,961 | 187,679 |
| **Countries Reached** | 51 | 66 |
| **CI/CD Installs** | 69.9% | 63.7% |
| **UV Adoption** | 25.9% | 18.0% |
| **Confirmed MCP Usage** | 96 | 315 |
<!-- METRICS_TABLE_END -->

---

## 🌍 Geographic Distribution

<table>
<tr>
<td width="50%" align="center">

### 30-Day Analysis

</td>
<td width="50%" align="center">

### 90-Day Analysis

</td>
</tr>
<tr>
<td width="50%" align="center">

![30-Day Geographic Distribution](reports/compliance-trestle_map_30days.png)

</td>
<td width="50%" align="center">

![90-Day Geographic Distribution](reports/compliance-trestle_map_90days.png)

</td>
</tr>
<tr>
<td width="50%" valign="top">

**Top 10 Countries:**
<!-- COUNTRIES_30_START -->
| Country | Downloads | % |
|---------|-----------|---|
| <img src="https://flagcdn.com/16x12/us.png" alt="US" width="16" height="12"> United States | 78,353 | 91.1% |
| <img src="https://flagcdn.com/16x12/sg.png" alt="SG" width="16" height="12"> Singapore | 3,016 | 3.5% |
| <img src="https://flagcdn.com/16x12/ru.png" alt="RU" width="16" height="12"> Russian Federation | 888 | 1.0% |
| <img src="https://flagcdn.com/16x12/cn.png" alt="CN" width="16" height="12"> China | 788 | 0.9% |
| <img src="https://flagcdn.com/16x12/jp.png" alt="JP" width="16" height="12"> Japan | 618 | 0.7% |
| <img src="https://flagcdn.com/16x12/gb.png" alt="GB" width="16" height="12"> United Kingdom | 457 | 0.5% |
| <img src="https://flagcdn.com/16x12/de.png" alt="DE" width="16" height="12"> Germany | 270 | 0.3% |
| <img src="https://flagcdn.com/16x12/ae.png" alt="AE" width="16" height="12"> United Arab Emirates | 248 | 0.3% |
| <img src="https://flagcdn.com/16x12/tw.png" alt="TW" width="16" height="12"> Taiwan, Province of China | 200 | 0.2% |
| <img src="https://flagcdn.com/16x12/es.png" alt="ES" width="16" height="12"> Spain | 195 | 0.2% |
<!-- COUNTRIES_30_END -->

</td>
<td width="50%" valign="top">

**Top 10 Countries:**
<!-- COUNTRIES_90_START -->
| Country | Downloads | % |
|---------|-----------|---|
| <img src="https://flagcdn.com/16x12/us.png" alt="US" width="16" height="12"> United States | 171,859 | 91.6% |
| <img src="https://flagcdn.com/16x12/sg.png" alt="SG" width="16" height="12"> Singapore | 5,668 | 3.0% |
| <img src="https://flagcdn.com/16x12/cn.png" alt="CN" width="16" height="12"> China | 2,252 | 1.2% |
| <img src="https://flagcdn.com/16x12/gb.png" alt="GB" width="16" height="12"> United Kingdom | 1,383 | 0.7% |
| <img src="https://flagcdn.com/16x12/ru.png" alt="RU" width="16" height="12"> Russian Federation | 1,260 | 0.7% |
| <img src="https://flagcdn.com/16x12/jp.png" alt="JP" width="16" height="12"> Japan | 703 | 0.4% |
| <img src="https://flagcdn.com/16x12/kr.png" alt="KR" width="16" height="12"> Korea, Republic of | 595 | 0.3% |
| <img src="https://flagcdn.com/16x12/de.png" alt="DE" width="16" height="12"> Germany | 593 | 0.3% |
| <img src="https://flagcdn.com/16x12/in.png" alt="IN" width="16" height="12"> India | 380 | 0.2% |
| <img src="https://flagcdn.com/16x12/fr.png" alt="FR" width="16" height="12"> France | 368 | 0.2% |
<!-- COUNTRIES_90_END -->

</td>
</tr>
</table>

<!-- GEO_INSIGHTS_START -->
**Key Insights:**
- **<img src="https://flagcdn.com/16x12/us.png" alt="US" width="16" height="12"> United States dominance** (91.1% in 30d, 91.6% in 90d) consistent across periods
- **51 countries (30d), 66 countries (90d)** demonstrates global reach
<!-- GEO_INSIGHTS_END -->

---

## 🤖 MCP (Model Context Protocol) Usage Analysis

### What is MCP?

MCP (Model Context Protocol) is Anthropic's protocol for connecting AI assistants like Claude to external tools and data sources. When developers use Claude Desktop with MCP servers, they often install Python packages via `uvx` (uv's tool runner).

### Detection Methodology

Since MCP servers don't explicitly identify themselves in PyPI logs, we use **proxy signals** with significant limitations:

1. **HIGH Confidence:** `uvx` subcommand usage (MCP's recommended pattern, but also used for other tools)
2. **Contextual:** UV vs pip adoption trends (UV is MCP's recommended installer)
3. **Observational:** CI vs non-CI patterns (shows usage context, not MCP specifically)

**Important Limitations:**
- **Install vs Usage:** PyPI data shows package downloads, not actual execution - packages may be installed but never run
- **uvx Ambiguity:** The `uvx` command is used for many tools beyond MCP servers (any Python CLI tool can be run via uvx)
- **Non-CI Context:** Non-CI downloads don't isolate MCP usage - most PyPI downloads are non-CI regardless of use case
- **CI Detection Issues:** The `details.ci` field in BigQuery is heuristically derived from user-agent strings (checking for patterns like "github", "travis", "jenkins") and is unreliable - many CI systems don't identify themselves, and some non-CI tools may match the patterns
- **User-Agent Limitations:** Cannot distinguish MCP from other UV usage without access to raw user-agent strings, which are not available in the public BigQuery dataset
- **Proxy Signals Only:** All MCP detection relies on indirect signals (installer choice, subcommand usage) rather than explicit MCP identification

### MCP Analysis Charts

#### 1. Installer Utilized
*Shows which installer tool was used to download the package (pip, uv, or poetry). UV is a proxy for MCP since MCP clients use UV.*

<table><tr>
<td width="50%">

**30 Days**

![Installer Share 30d](reports/compliance-trestle_mcp_installer_30days.png)

<!-- UV_INSTALLER_30_START -->
UV: 25.9% of downloads (22,263)
<!-- UV_INSTALLER_30_END -->

</td>
<td width="50%">

**90 Days**

![Installer Share 90d](reports/compliance-trestle_mcp_installer_90days.png)

<!-- UV_INSTALLER_90_START -->
UV: 18.0% of downloads (33,858)
<!-- UV_INSTALLER_90_END -->

</td>
</tr></table>

#### 2. UV Subcommands (uvx = MCP Pattern)
*Breaks down all UV downloads by which UV subcommand was used. The `uvx` command is the standard pattern MCP clients use to run MCP servers (e.g., Claude Desktop, Cline, etc.).*

<table><tr>
<td width="50%">

**30 Days**

![UV Subcommands 30d](reports/compliance-trestle_mcp_subcommands_30days.png)

<!-- UVX_30_START -->
**96 uvx downloads** = HIGH confidence MCP
<!-- UVX_30_END -->

</td>
<td width="50%">

**90 Days**

![UV Subcommands 90d](reports/compliance-trestle_mcp_subcommands_90days.png)

<!-- UVX_90_START -->
**315 uvx downloads** = HIGH confidence MCP
<!-- UVX_90_END -->

</td>
</tr></table>

**UV Subcommand Meanings:**
- **`sync`** - Synchronize project dependencies → *CI/CD pipelines, developers syncing environments*
- **`pip install`** - UV's pip-compatible install command → *CI/CD, automated builds, legacy workflows*
- **no subcommand** - UV downloads without subcommand data → *Older UV versions or incomplete logging*
- **`run`** - Run a script in a virtual environment → *Developers, test runners, automation scripts*
- **`tool install`** - Install a tool globally → *Developers setting up their environment*
- **`uvx`** - Run a tool without installing it → ***MCP clients (Claude Desktop, Cline), developers trying tools***
- **`lock`** - Generate a lockfile for dependencies → *Developers, CI/CD for reproducible builds*
- **`pip compile`** - Compile requirements files → *CI/CD, dependency management workflows*
- **`add`** - Add a dependency to the project → *Developers adding new packages*
- **`tool run`** - Run an installed tool → *Developers, automation scripts*
- **`tool upgrade`** - Upgrade an installed tool → *Developers maintaining tools*

#### 3. CI vs Non-CI Usage
*Separates automated CI/CD installs from other downloads for pip, uv, poetry, and other installers.*

<table><tr>
<td width="50%">

**30 Days**

![CI vs Non-CI 30d](reports/compliance-trestle_mcp_ci_30days.png)

<!-- UV_NON_CI_30_START -->
UV: 35.7% non-CI (7,940 downloads)
<!-- UV_NON_CI_30_END -->

</td>
<td width="50%">

**90 Days**

![CI vs Non-CI 90d](reports/compliance-trestle_mcp_ci_90days.png)

<!-- UV_NON_CI_90_START -->
UV: 46.3% non-CI (15,688 downloads)
<!-- UV_NON_CI_90_END -->

</td>
</tr></table>

#### 4. Daily UV Trend
*Time series showing daily UV download trends. Highlights confirmed `uvx` subcommand usage (MCP pattern) alongside total UV downloads to visualize MCP adoption patterns over time.*

<table><tr>
<td width="50%">

**30 Days**

![Daily Trend 30d](reports/compliance-trestle_mcp_daily_30days.png)

<!-- DAILY_TREND_30_START -->
96 uvx downloads over 30 days
<!-- DAILY_TREND_30_END -->

</td>
<td width="50%">

**90 Days**

![Daily Trend 90d](reports/compliance-trestle_mcp_daily_90days.png)

<!-- DAILY_TREND_90_START -->
315 uvx downloads over 90 days
<!-- DAILY_TREND_90_END -->

</td>
</tr></table>

**Key Findings:**

<table><tr>
<td width="50%" valign="top">

**30-Day Analysis:**
<!-- MCP_FINDINGS_30_START -->
1. **Confirmed MCP Usage:** 96 downloads using `uvx` subcommand
2. **UV Adoption:** 25.9% of downloads
3. **Interactive Usage:** 35.7% of UV downloads are non-CI

MCP usage is detectable but small. The broader story is UV's growth as a modern Python installer.
<!-- MCP_FINDINGS_30_END -->

</td>
<td width="50%" valign="top">

**90-Day Analysis:**
<!-- MCP_FINDINGS_90_START -->
1. **Confirmed MCP Usage:** 315 downloads using `uvx` subcommand
2. **UV Adoption:** 18.0% of downloads
3. **Interactive Usage:** 46.3% of UV downloads are non-CI

MCP usage is detectable but small. The broader story is UV's growth as a modern Python installer.
<!-- MCP_FINDINGS_90_END -->

</td>
</tr></table>

---

## 🚀 Deployment Environment Analysis

### Platform Distribution

*Categorizes downloads by platform based on OS and distribution detection. Identifies AWS (Amazon Linux), Containers (Alpine), Enterprise (RHEL), Ubuntu, Debian, macOS, Windows, and other platforms. Shows the overall platform mix of package users.*

<table><tr>
<td width="50%">

**30 Days**

![Platform Distribution 30d](reports/compliance-trestle_platforms_30days.png)

</td>
<td width="50%">

**90 Days**

![Platform Distribution 90d](reports/compliance-trestle_platforms_90days.png)

</td>
</tr></table>

### Deployment Types

*Shows the distribution of downloads across different deployment environments, automatically categorized based on OS, distribution, libc type, and CI detection. Categories may include containers, cloud VMs, CI/CD pipelines, and developer workstations.*

<table><tr>
<td width="50%">

**30 Days**

![Deployment Types 30d](reports/deployment_types_30day.png)

</td>
<td width="50%">

**90 Days**

![Deployment Types 90d](reports/deployment_types_90day.png)

</td>
</tr></table>

### Architecture Distribution

*Shows CPU architecture breakdown (x86_64, ARM64, etc.) detected from download metadata. Tracks adoption of ARM-based systems like AWS Graviton and Apple Silicon.*

<table><tr>
<td width="50%">

**30 Days**

![Architecture Distribution 30d](reports/deployment_architecture_30day.png)

</td>
<td width="50%">

**90 Days**

![Architecture Distribution 90d](reports/deployment_architecture_90day.png)

</td>
</tr></table>

### Enterprise vs Cloud-Native

*Compares traditional enterprise Linux distributions (RHEL, CentOS) against cloud-native platforms (Amazon Linux, Alpine). Indicates adoption patterns in regulated vs cloud-first environments.*

<table><tr>
<td width="50%">

**30 Days**

![Enterprise vs Cloud-Native 30d](reports/deployment_enterprise_cloud_30day.png)

</td>
<td width="50%">

**90 Days**

![Enterprise vs Cloud-Native 90d](reports/deployment_enterprise_cloud_90day.png)

</td>
</tr></table>

### libc Distribution (Container Signal)

*Shows the distribution of C library implementations (glibc vs musl). musl libc is a strong indicator of containerized deployments, particularly Alpine Linux in Docker/Kubernetes.*

<table><tr>
<td width="50%">

**30 Days**

![libc Distribution 30d](reports/deployment_libc_30day.png)

</td>
<td width="50%">

**90 Days**

![libc Distribution 90d](reports/deployment_libc_90day.png)

</td>
</tr></table>

### Deployment Context

*Categorizes downloads by deployment scenario based on OS type, Linux distribution, and CI detection. Shows patterns like containerized pipelines (Alpine+CI), cloud automation (Amazon Linux+CI), enterprise Linux (RHEL), CI environments, developer workstations (macOS/Windows), and other contexts.*

<table><tr>
<td width="50%">

**30 Days**

![Use Cases 30d](reports/deployment_use_cases_30day.png)

</td>
<td width="50%">

**90 Days**

![Use Cases 90d](reports/deployment_use_cases_90day.png)

</td>
</tr></table>

### Deployment Summary

*Key deployment metrics at a glance: container adoption, cloud provider usage, enterprise deployment, CI/CD percentage, ARM architecture adoption, and musl libc usage.*

<table><tr>
<td width="50%">

**30 Days**

![Deployment Summary 30d](reports/deployment_summary_30day.png)

</td>
<td width="50%">

**90 Days**

![Deployment Summary 90d](reports/deployment_summary_90day.png)

</td>
</tr></table>

---

---

## 🔄 Automated Updates

This repository is automatically updated weekly by GitHub Actions:
- **Schedule:** Weekly on Mondays at 6 AM UTC (2 AM ET)
- **Authentication:** Service account JSON key stored in GitHub secrets
- **Manual trigger:** Available via GitHub Actions UI
- **Setup guide:** See [SETUP.md](docs/SETUP.md)

---

## 🔍 Data Sources & Methodology

**Data Source:** Google BigQuery public dataset `bigquery-public-data.pypi.file_downloads`

**Analysis Period:**
- 30-day reports: Last 30 days from data fetch date
- 90-day reports: Last 90 days from data fetch date

**Update Frequency:**
- **Automated:** Daily via GitHub Actions
- **Caching:** Data fetched once per day, cached locally to minimize BigQuery costs
- **Cache Management:** Old cache files automatically removed after successful new fetch
- **Manual trigger:** Available for on-demand updates

**Privacy:** All data comes from PyPI's public dataset. No personal information is collected or stored.

---

*Analytics powered by Google BigQuery and GitHub Actions*