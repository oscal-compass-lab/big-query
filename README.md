# PyPI Download Analytics for compliance-trestle

**Recent insights into PyPI package adoption and usage patterns**

This repository contains automated BigQuery analytics and reports for PyPI packages.

**Report Date:** 2026-06-01

---

## 📊 Version Adoption Trends

*Quarterly download trends by major version over the last 3 years. Shows version adoption patterns and migration trends across releases.*

![Quarterly Version Trends](reports/compliance-trestle_quarterly_versions.png)

---

## 🔑 Key Metrics Summary
<!-- METRICS_TABLE_START -->
| Metric | 30 Days | 90 Days |
|--------|---------|---------|
| **Total Downloads** | 83,475 | 210,993 |
| **Countries Reached** | 55 | 69 |
| **CI/CD Installs** | 68.8% | 66.5% |
| **UV Adoption** | 25.1% | 18.9% |
| **Confirmed MCP Usage** | 129 | 379 |
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

**Countries:**
<!-- COUNTRIES_30_START -->
| Country | Downloads | % |
|---------|-----------|---|
| <img src="https://flagcdn.com/16x12/us.png" alt="US" width="16" height="12"> United States | 73,257 | 87.8% |
| <img src="https://flagcdn.com/16x12/sg.png" alt="SG" width="16" height="12"> Singapore | 3,466 | 4.2% |
| <img src="https://flagcdn.com/16x12/ru.png" alt="RU" width="16" height="12"> Russian Federation | 1,494 | 1.8% |
| <img src="https://flagcdn.com/16x12/ae.png" alt="AE" width="16" height="12"> United Arab Emirates | 951 | 1.1% |
| <img src="https://flagcdn.com/16x12/cn.png" alt="CN" width="16" height="12"> China | 901 | 1.1% |
| <img src="https://flagcdn.com/16x12/gb.png" alt="GB" width="16" height="12"> United Kingdom | 554 | 0.7% |
| <img src="https://flagcdn.com/16x12/jp.png" alt="JP" width="16" height="12"> Japan | 538 | 0.6% |
| <img src="https://flagcdn.com/16x12/es.png" alt="ES" width="16" height="12"> Spain | 438 | 0.5% |
| <img src="https://flagcdn.com/16x12/hk.png" alt="HK" width="16" height="12"> Hong Kong | 303 | 0.4% |
| <img src="https://flagcdn.com/16x12/de.png" alt="DE" width="16" height="12"> Germany | 263 | 0.3% |
| <img src="https://flagcdn.com/16x12/se.png" alt="SE" width="16" height="12"> Sweden | 216 | 0.3% |
| <img src="https://flagcdn.com/16x12/ca.png" alt="CA" width="16" height="12"> Canada | 183 | 0.2% |
| <img src="https://flagcdn.com/16x12/ch.png" alt="CH" width="16" height="12"> Switzerland | 153 | 0.2% |
| <img src="https://flagcdn.com/16x12/fr.png" alt="FR" width="16" height="12"> France | 127 | 0.2% |
| <img src="https://flagcdn.com/16x12/ie.png" alt="IE" width="16" height="12"> Ireland | 97 | 0.1% |
| <img src="https://flagcdn.com/16x12/au.png" alt="AU" width="16" height="12"> Australia | 95 | 0.1% |
| <img src="https://flagcdn.com/16x12/in.png" alt="IN" width="16" height="12"> India | 77 | 0.1% |
| <img src="https://flagcdn.com/16x12/nl.png" alt="NL" width="16" height="12"> Netherlands | 68 | 0.1% |
| <img src="https://flagcdn.com/16x12/kr.png" alt="KR" width="16" height="12"> Korea, Republic of | 47 | 0.1% |
| <img src="https://flagcdn.com/16x12/at.png" alt="AT" width="16" height="12"> Austria | 31 | 0.0% |
| <img src="https://flagcdn.com/16x12/pl.png" alt="PL" width="16" height="12"> Poland | 30 | 0.0% |
| <img src="https://flagcdn.com/16x12/fi.png" alt="FI" width="16" height="12"> Finland | 25 | 0.0% |
| <img src="https://flagcdn.com/16x12/no.png" alt="NO" width="16" height="12"> Norway | 18 | 0.0% |
| <img src="https://flagcdn.com/16x12/dk.png" alt="DK" width="16" height="12"> Denmark | 16 | 0.0% |
| <img src="https://flagcdn.com/16x12/pk.png" alt="PK" width="16" height="12"> Pakistan | 15 | 0.0% |
| <img src="https://flagcdn.com/16x12/sa.png" alt="SA" width="16" height="12"> Saudi Arabia | 12 | 0.0% |
| <img src="https://flagcdn.com/16x12/ee.png" alt="EE" width="16" height="12"> Estonia | 10 | 0.0% |
| <img src="https://flagcdn.com/16x12/it.png" alt="IT" width="16" height="12"> Italy | 10 | 0.0% |
| <img src="https://flagcdn.com/16x12/be.png" alt="BE" width="16" height="12"> Belgium | 10 | 0.0% |
| <img src="https://flagcdn.com/16x12/pt.png" alt="PT" width="16" height="12"> Portugal | 8 | 0.0% |
| <img src="https://flagcdn.com/16x12/il.png" alt="IL" width="16" height="12"> Israel | 8 | 0.0% |
| <img src="https://flagcdn.com/16x12/vn.png" alt="VN" width="16" height="12"> Viet Nam | 7 | 0.0% |
| <img src="https://flagcdn.com/16x12/qa.png" alt="QA" width="16" height="12"> Qatar | 6 | 0.0% |
| <img src="https://flagcdn.com/16x12/bd.png" alt="BD" width="16" height="12"> Bangladesh | 4 | 0.0% |
| <img src="https://flagcdn.com/16x12/ro.png" alt="RO" width="16" height="12"> Romania | 4 | 0.0% |
| <img src="https://flagcdn.com/16x12/za.png" alt="ZA" width="16" height="12"> South Africa | 3 | 0.0% |
| <img src="https://flagcdn.com/16x12/br.png" alt="BR" width="16" height="12"> Brazil | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/bg.png" alt="BG" width="16" height="12"> Bulgaria | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/co.png" alt="CO" width="16" height="12"> Colombia | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/rs.png" alt="RS" width="16" height="12"> Serbia | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/pr.png" alt="PR" width="16" height="12"> Puerto Rico | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/th.png" alt="TH" width="16" height="12"> Thailand | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/cz.png" alt="CZ" width="16" height="12"> Czechia | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/cl.png" alt="CL" width="16" height="12"> Chile | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/nz.png" alt="NZ" width="16" height="12"> New Zealand | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/id.png" alt="ID" width="16" height="12"> Indonesia | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/gh.png" alt="GH" width="16" height="12"> Ghana | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/ge.png" alt="GE" width="16" height="12"> Georgia | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/cr.png" alt="CR" width="16" height="12"> Costa Rica | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/ad.png" alt="AD" width="16" height="12"> Andorra | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/mx.png" alt="MX" width="16" height="12"> Mexico | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/pe.png" alt="PE" width="16" height="12"> Peru | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/li.png" alt="LI" width="16" height="12"> Liechtenstein | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/md.png" alt="MD" width="16" height="12"> Moldova, Republic of | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/tw.png" alt="TW" width="16" height="12"> Taiwan, Province of China | 1 | 0.0% |
<!-- COUNTRIES_30_END -->

</td>
<td width="50%" valign="top">

**Countries:**
<!-- COUNTRIES_90_START -->
| Country | Downloads | % |
|---------|-----------|---|
| <img src="https://flagcdn.com/16x12/us.png" alt="US" width="16" height="12"> United States | 191,730 | 90.9% |
| <img src="https://flagcdn.com/16x12/sg.png" alt="SG" width="16" height="12"> Singapore | 6,248 | 3.0% |
| <img src="https://flagcdn.com/16x12/cn.png" alt="CN" width="16" height="12"> China | 2,366 | 1.1% |
| <img src="https://flagcdn.com/16x12/ru.png" alt="RU" width="16" height="12"> Russian Federation | 1,885 | 0.9% |
| <img src="https://flagcdn.com/16x12/gb.png" alt="GB" width="16" height="12"> United Kingdom | 1,617 | 0.8% |
| <img src="https://flagcdn.com/16x12/ae.png" alt="AE" width="16" height="12"> United Arab Emirates | 960 | 0.5% |
| <img src="https://flagcdn.com/16x12/jp.png" alt="JP" width="16" height="12"> Japan | 852 | 0.4% |
| <img src="https://flagcdn.com/16x12/de.png" alt="DE" width="16" height="12"> Germany | 678 | 0.3% |
| <img src="https://flagcdn.com/16x12/kr.png" alt="KR" width="16" height="12"> Korea, Republic of | 610 | 0.3% |
| <img src="https://flagcdn.com/16x12/hk.png" alt="HK" width="16" height="12"> Hong Kong | 594 | 0.3% |
| <img src="https://flagcdn.com/16x12/es.png" alt="ES" width="16" height="12"> Spain | 472 | 0.2% |
| <img src="https://flagcdn.com/16x12/fr.png" alt="FR" width="16" height="12"> France | 428 | 0.2% |
| <img src="https://flagcdn.com/16x12/ca.png" alt="CA" width="16" height="12"> Canada | 362 | 0.2% |
| <img src="https://flagcdn.com/16x12/in.png" alt="IN" width="16" height="12"> India | 341 | 0.2% |
| <img src="https://flagcdn.com/16x12/au.png" alt="AU" width="16" height="12"> Australia | 280 | 0.1% |
| <img src="https://flagcdn.com/16x12/se.png" alt="SE" width="16" height="12"> Sweden | 257 | 0.1% |
| <img src="https://flagcdn.com/16x12/tw.png" alt="TW" width="16" height="12"> Taiwan, Province of China | 219 | 0.1% |
| <img src="https://flagcdn.com/16x12/ie.png" alt="IE" width="16" height="12"> Ireland | 184 | 0.1% |
| <img src="https://flagcdn.com/16x12/ch.png" alt="CH" width="16" height="12"> Switzerland | 178 | 0.1% |
| <img src="https://flagcdn.com/16x12/nl.png" alt="NL" width="16" height="12"> Netherlands | 124 | 0.1% |
| <img src="https://flagcdn.com/16x12/at.png" alt="AT" width="16" height="12"> Austria | 58 | 0.0% |
| <img src="https://flagcdn.com/16x12/fi.png" alt="FI" width="16" height="12"> Finland | 53 | 0.0% |
| <img src="https://flagcdn.com/16x12/pk.png" alt="PK" width="16" height="12"> Pakistan | 52 | 0.0% |
| <img src="https://flagcdn.com/16x12/it.png" alt="IT" width="16" height="12"> Italy | 51 | 0.0% |
| <img src="https://flagcdn.com/16x12/pt.png" alt="PT" width="16" height="12"> Portugal | 44 | 0.0% |
| <img src="https://flagcdn.com/16x12/pl.png" alt="PL" width="16" height="12"> Poland | 41 | 0.0% |
| <img src="https://flagcdn.com/16x12/dk.png" alt="DK" width="16" height="12"> Denmark | 39 | 0.0% |
| <img src="https://flagcdn.com/16x12/sa.png" alt="SA" width="16" height="12"> Saudi Arabia | 38 | 0.0% |
| <img src="https://flagcdn.com/16x12/no.png" alt="NO" width="16" height="12"> Norway | 31 | 0.0% |
| <img src="https://flagcdn.com/16x12/qa.png" alt="QA" width="16" height="12"> Qatar | 19 | 0.0% |
| <img src="https://flagcdn.com/16x12/ro.png" alt="RO" width="16" height="12"> Romania | 19 | 0.0% |
| <img src="https://flagcdn.com/16x12/il.png" alt="IL" width="16" height="12"> Israel | 17 | 0.0% |
| <img src="https://flagcdn.com/16x12/be.png" alt="BE" width="16" height="12"> Belgium | 17 | 0.0% |
| <img src="https://flagcdn.com/16x12/vn.png" alt="VN" width="16" height="12"> Viet Nam | 14 | 0.0% |
| <img src="https://flagcdn.com/16x12/ee.png" alt="EE" width="16" height="12"> Estonia | 14 | 0.0% |
| <img src="https://flagcdn.com/16x12/cz.png" alt="CZ" width="16" height="12"> Czechia | 12 | 0.0% |
| <img src="https://flagcdn.com/16x12/tg.png" alt="TG" width="16" height="12"> Togo | 10 | 0.0% |
| <img src="https://flagcdn.com/16x12/cr.png" alt="CR" width="16" height="12"> Costa Rica | 9 | 0.0% |
| <img src="https://flagcdn.com/16x12/mx.png" alt="MX" width="16" height="12"> Mexico | 7 | 0.0% |
| <img src="https://flagcdn.com/16x12/nz.png" alt="NZ" width="16" height="12"> New Zealand | 4 | 0.0% |
| <img src="https://flagcdn.com/16x12/cl.png" alt="CL" width="16" height="12"> Chile | 4 | 0.0% |
| <img src="https://flagcdn.com/16x12/br.png" alt="BR" width="16" height="12"> Brazil | 4 | 0.0% |
| <img src="https://flagcdn.com/16x12/bd.png" alt="BD" width="16" height="12"> Bangladesh | 4 | 0.0% |
| <img src="https://flagcdn.com/16x12/co.png" alt="CO" width="16" height="12"> Colombia | 3 | 0.0% |
| <img src="https://flagcdn.com/16x12/pr.png" alt="PR" width="16" height="12"> Puerto Rico | 3 | 0.0% |
| <img src="https://flagcdn.com/16x12/za.png" alt="ZA" width="16" height="12"> South Africa | 3 | 0.0% |
| <img src="https://flagcdn.com/16x12/pe.png" alt="PE" width="16" height="12"> Peru | 3 | 0.0% |
| <img src="https://flagcdn.com/16x12/th.png" alt="TH" width="16" height="12"> Thailand | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/az.png" alt="AZ" width="16" height="12"> Azerbaijan | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/gh.png" alt="GH" width="16" height="12"> Ghana | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/bg.png" alt="BG" width="16" height="12"> Bulgaria | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/cy.png" alt="CY" width="16" height="12"> Cyprus | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/kz.png" alt="KZ" width="16" height="12"> Kazakhstan | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/my.png" alt="MY" width="16" height="12"> Malaysia | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/tn.png" alt="TN" width="16" height="12"> Tunisia | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/rs.png" alt="RS" width="16" height="12"> Serbia | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/id.png" alt="ID" width="16" height="12"> Indonesia | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/lu.png" alt="LU" width="16" height="12"> Luxembourg | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/ph.png" alt="PH" width="16" height="12"> Philippines | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/py.png" alt="PY" width="16" height="12"> Paraguay | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/ad.png" alt="AD" width="16" height="12"> Andorra | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/li.png" alt="LI" width="16" height="12"> Liechtenstein | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/ge.png" alt="GE" width="16" height="12"> Georgia | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/eg.png" alt="EG" width="16" height="12"> Egypt | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/ma.png" alt="MA" width="16" height="12"> Morocco | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/lt.png" alt="LT" width="16" height="12"> Lithuania | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/md.png" alt="MD" width="16" height="12"> Moldova, Republic of | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/tr.png" alt="TR" width="16" height="12"> Türkiye | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/ve.png" alt="VE" width="16" height="12"> Venezuela, Bolivarian Republic of | 1 | 0.0% |
<!-- COUNTRIES_90_END -->

</td>
</tr>
</table>

<!-- GEO_INSIGHTS_START -->
**Key Insights:**
- **<img src="https://flagcdn.com/16x12/us.png" alt="US" width="16" height="12"> United States dominance** (87.8% in 30d, 90.9% in 90d) consistent across periods
- **55 countries (30d), 69 countries (90d)** demonstrates global reach
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
UV: 25.1% of downloads (20,943)
<!-- UV_INSTALLER_30_END -->

</td>
<td width="50%">

**90 Days**

![Installer Share 90d](reports/compliance-trestle_mcp_installer_90days.png)

<!-- UV_INSTALLER_90_START -->
UV: 18.9% of downloads (39,821)
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
**129 uvx downloads** = HIGH confidence MCP
<!-- UVX_30_END -->

</td>
<td width="50%">

**90 Days**

![UV Subcommands 90d](reports/compliance-trestle_mcp_subcommands_90days.png)

<!-- UVX_90_START -->
**379 uvx downloads** = HIGH confidence MCP
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
UV: 32.9% non-CI (6,898 downloads)
<!-- UV_NON_CI_30_END -->

</td>
<td width="50%">

**90 Days**

![CI vs Non-CI 90d](reports/compliance-trestle_mcp_ci_90days.png)

<!-- UV_NON_CI_90_START -->
UV: 43.3% non-CI (17,256 downloads)
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
129 uvx downloads over 30 days
<!-- DAILY_TREND_30_END -->

</td>
<td width="50%">

**90 Days**

![Daily Trend 90d](reports/compliance-trestle_mcp_daily_90days.png)

<!-- DAILY_TREND_90_START -->
379 uvx downloads over 90 days
<!-- DAILY_TREND_90_END -->

</td>
</tr></table>

**Key Findings:**

<table><tr>
<td width="50%" valign="top">

**30-Day Analysis:**
<!-- MCP_FINDINGS_30_START -->
1. **Confirmed MCP Usage:** 129 downloads using `uvx` subcommand
2. **UV Adoption:** 25.1% of downloads
3. **Interactive Usage:** 32.9% of UV downloads are non-CI

MCP usage is detectable but small. The broader story is UV's growth as a modern Python installer.
<!-- MCP_FINDINGS_30_END -->

</td>
<td width="50%" valign="top">

**90-Day Analysis:**
<!-- MCP_FINDINGS_90_START -->
1. **Confirmed MCP Usage:** 379 downloads using `uvx` subcommand
2. **UV Adoption:** 18.9% of downloads
3. **Interactive Usage:** 43.3% of UV downloads are non-CI

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