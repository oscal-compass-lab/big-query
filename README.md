# PyPI Download Analytics for compliance-trestle

**Recent insights into PyPI package adoption and usage patterns**

This repository contains automated BigQuery analytics and reports for PyPI packages.

**Report Date:** 2026-11-15

---

## 📊 Version Adoption Trends

*Quarterly download trends by major version over the last 3 years. Shows version adoption patterns and migration trends across releases.*

![Quarterly Version Trends](reports/compliance-trestle_quarterly_versions.png)

---

## 🔑 Key Metrics Summary
<!-- METRICS_TABLE_START -->
| Metric | Last 30 Days (Actual) | Last 90 Days (Actual) |
|--------|----------------------|----------------------|
| **Total Downloads** | 80,288 | 235,832 |
| **Countries Reached** | 57 | 77 |
| **CI/CD Installs** | 63.9% | 59.9% |
| **UV Adoption** | 40.6% | 44.9% |
| **MCP Usage** | 820 | 956 |
<!-- METRICS_TABLE_END -->

---

## ⚠️ Important download tracking history change

An architectural shift implemented on <i><b>August 24, 2026</b></i> represents one of the most significant corrections to PyPI's download tracking history.
Prior to this update, PyPI's logging infrastructure tracked downloads by matching a broad storage prefix (/packages/<xx>/<yy>/...). This meant any request for any file associated with a package release was logged as a full package download.
The [official PyPI Blog post](https://blog.pypi.org/posts/2026-08-31-download-counts/) details exactly what was bloating those numbers, how severe the drop was, and how it impacts historical data:

<b>What Was Artificially Inflating the Data?</b>

The primary culprit was the adoption of PEP 658 metadata sidecars. Modern Python package installers (like pip or uv) often fetch just the lightweight .metadata file of a wheel to resolve dependencies before deciding whether they actually need to download the massive wheel itself.
PyPI discovered that these metadata requests accounted for roughly 40% of all logged traffic. Other non-distribution files that were being erroneously counted included:

.asc files: Legacy GPG signatures (deprecated for new uploads in 2023 but still served).
Legacy formats: Leftover .egg, .exe, .msi, and .rpm files from older packaging eras.

<b>The Scale of the "Downward Shift"</b>

The impact of filtering out these files was immediate and permanent. Across all of PyPI, daily baseline downloads historically fluctuated between 4.5 billion on weekends to over 7 billion midweek. After the August 24 patch, that entire curve stepped down sharply because only files ending in .whl, .tar.gz, or .zip are now recorded.
For a real-world example, PyPI administrators tracked urllib3 traffic during the transition week:

Before August 24: urllib3 averaged ~74 million logged "downloads" a day, but 39% of those were actually metadata or accessory files, not the actual package.
After August 25: The "other" file count dropped to exactly 0%, shrinking the package's daily download metric overnight to reflect only real distribution file downloads.

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
| <img src="https://flagcdn.com/16x12/us.png" alt="US" width="16" height="12"> United States | 62,570 | 77.9% |
| <img src="https://flagcdn.com/16x12/sg.png" alt="SG" width="16" height="12"> Singapore | 8,489 | 10.6% |
| <img src="https://flagcdn.com/16x12/hk.png" alt="HK" width="16" height="12"> Hong Kong | 1,389 | 1.7% |
| <img src="https://flagcdn.com/16x12/se.png" alt="SE" width="16" height="12"> Sweden | 1,201 | 1.5% |
| <img src="https://flagcdn.com/16x12/gb.png" alt="GB" width="16" height="12"> United Kingdom | 1,118 | 1.4% |
| <img src="https://flagcdn.com/16x12/ca.png" alt="CA" width="16" height="12"> Canada | 947 | 1.2% |
| <img src="https://flagcdn.com/16x12/de.png" alt="DE" width="16" height="12"> Germany | 926 | 1.2% |
| <img src="https://flagcdn.com/16x12/kr.png" alt="KR" width="16" height="12"> South Korea | 490 | 0.6% |
| <img src="https://flagcdn.com/16x12/cn.png" alt="CN" width="16" height="12"> China | 459 | 0.6% |
| <img src="https://flagcdn.com/16x12/kw.png" alt="KW" width="16" height="12"> Kuwait | 423 | 0.5% |
| <img src="https://flagcdn.com/16x12/fi.png" alt="FI" width="16" height="12"> Finland | 412 | 0.5% |
| <img src="https://flagcdn.com/16x12/in.png" alt="IN" width="16" height="12"> India | 237 | 0.3% |
| <img src="https://flagcdn.com/16x12/mx.png" alt="MX" width="16" height="12"> Mexico | 217 | 0.3% |
| <img src="https://flagcdn.com/16x12/nl.png" alt="NL" width="16" height="12"> Netherlands | 170 | 0.2% |
| <img src="https://flagcdn.com/16x12/fr.png" alt="FR" width="16" height="12"> France | 164 | 0.2% |
| <img src="https://flagcdn.com/16x12/au.png" alt="AU" width="16" height="12"> Australia | 121 | 0.2% |
| <img src="https://flagcdn.com/16x12/lu.png" alt="LU" width="16" height="12"> Luxembourg | 113 | 0.1% |
| <img src="https://flagcdn.com/16x12/nz.png" alt="NZ" width="16" height="12"> New Zealand | 106 | 0.1% |
| <img src="https://flagcdn.com/16x12/jp.png" alt="JP" width="16" height="12"> Japan | 100 | 0.1% |
| <img src="https://flagcdn.com/16x12/ae.png" alt="AE" width="16" height="12"> United Arab Emirates | 100 | 0.1% |
| <img src="https://flagcdn.com/16x12/pk.png" alt="PK" width="16" height="12"> Pakistan | 97 | 0.1% |
| <img src="https://flagcdn.com/16x12/cl.png" alt="CL" width="16" height="12"> Chile | 77 | 0.1% |
| <img src="https://flagcdn.com/16x12/vn.png" alt="VN" width="16" height="12"> Vietnam | 62 | 0.1% |
| <img src="https://flagcdn.com/16x12/no.png" alt="NO" width="16" height="12"> Norway | 50 | 0.1% |
| <img src="https://flagcdn.com/16x12/es.png" alt="ES" width="16" height="12"> Spain | 31 | 0.0% |
| <img src="https://flagcdn.com/16x12/ru.png" alt="RU" width="16" height="12"> Russia | 26 | 0.0% |
| <img src="https://flagcdn.com/16x12/cz.png" alt="CZ" width="16" height="12"> Czechia | 25 | 0.0% |
| <img src="https://flagcdn.com/16x12/it.png" alt="IT" width="16" height="12"> Italy | 18 | 0.0% |
| <img src="https://flagcdn.com/16x12/tr.png" alt="TR" width="16" height="12"> Türkiye | 15 | 0.0% |
| <img src="https://flagcdn.com/16x12/pl.png" alt="PL" width="16" height="12"> Poland | 14 | 0.0% |
| <img src="https://flagcdn.com/16x12/ie.png" alt="IE" width="16" height="12"> Ireland | 13 | 0.0% |
| <img src="https://flagcdn.com/16x12/il.png" alt="IL" width="16" height="12"> Israel | 12 | 0.0% |
| <img src="https://flagcdn.com/16x12/pt.png" alt="PT" width="16" height="12"> Portugal | 11 | 0.0% |
| <img src="https://flagcdn.com/16x12/ch.png" alt="CH" width="16" height="12"> Switzerland | 8 | 0.0% |
| <img src="https://flagcdn.com/16x12/tw.png" alt="TW" width="16" height="12"> Taiwan | 7 | 0.0% |
| <img src="https://flagcdn.com/16x12/za.png" alt="ZA" width="16" height="12"> South Africa | 7 | 0.0% |
| <img src="https://flagcdn.com/16x12/be.png" alt="BE" width="16" height="12"> Belgium | 7 | 0.0% |
| <img src="https://flagcdn.com/16x12/dk.png" alt="DK" width="16" height="12"> Denmark | 6 | 0.0% |
| <img src="https://flagcdn.com/16x12/ro.png" alt="RO" width="16" height="12"> Romania | 6 | 0.0% |
| <img src="https://flagcdn.com/16x12/my.png" alt="MY" width="16" height="12"> Malaysia | 5 | 0.0% |
| <img src="https://flagcdn.com/16x12/at.png" alt="AT" width="16" height="12"> Austria | 5 | 0.0% |
| <img src="https://flagcdn.com/16x12/br.png" alt="BR" width="16" height="12"> Brazil | 4 | 0.0% |
| <img src="https://flagcdn.com/16x12/sa.png" alt="SA" width="16" height="12"> Saudi Arabia | 4 | 0.0% |
| <img src="https://flagcdn.com/16x12/is.png" alt="IS" width="16" height="12"> Iceland | 4 | 0.0% |
| <img src="https://flagcdn.com/16x12/lt.png" alt="LT" width="16" height="12"> Lithuania | 3 | 0.0% |
| <img src="https://flagcdn.com/16x12/id.png" alt="ID" width="16" height="12"> Indonesia | 3 | 0.0% |
| <img src="https://flagcdn.com/16x12/ee.png" alt="EE" width="16" height="12"> Estonia | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/hu.png" alt="HU" width="16" height="12"> Hungary | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/gr.png" alt="GR" width="16" height="12"> Greece | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/ir.png" alt="IR" width="16" height="12"> Iran | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/sk.png" alt="SK" width="16" height="12"> Slovakia | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/bd.png" alt="BD" width="16" height="12"> Bangladesh | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/am.png" alt="AM" width="16" height="12"> Armenia | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/co.png" alt="CO" width="16" height="12"> Colombia | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/eg.png" alt="EG" width="16" height="12"> Egypt | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/pa.png" alt="PA" width="16" height="12"> Panama | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/th.png" alt="TH" width="16" height="12"> Thailand | 1 | 0.0% |
<!-- COUNTRIES_30_END -->

</td>
<td width="50%" valign="top">

**Countries:**
<!-- COUNTRIES_90_START -->
| Country | Downloads | % |
|---------|-----------|---|
| <img src="https://flagcdn.com/16x12/us.png" alt="US" width="16" height="12"> United States | 190,753 | 80.9% |
| <img src="https://flagcdn.com/16x12/sg.png" alt="SG" width="16" height="12"> Singapore | 22,330 | 9.5% |
| <img src="https://flagcdn.com/16x12/de.png" alt="DE" width="16" height="12"> Germany | 4,135 | 1.8% |
| <img src="https://flagcdn.com/16x12/hk.png" alt="HK" width="16" height="12"> Hong Kong | 3,348 | 1.4% |
| <img src="https://flagcdn.com/16x12/ca.png" alt="CA" width="16" height="12"> Canada | 1,878 | 0.8% |
| <img src="https://flagcdn.com/16x12/se.png" alt="SE" width="16" height="12"> Sweden | 1,747 | 0.7% |
| <img src="https://flagcdn.com/16x12/gb.png" alt="GB" width="16" height="12"> United Kingdom | 1,732 | 0.7% |
| <img src="https://flagcdn.com/16x12/cn.png" alt="CN" width="16" height="12"> China | 1,561 | 0.7% |
| <img src="https://flagcdn.com/16x12/mx.png" alt="MX" width="16" height="12"> Mexico | 947 | 0.4% |
| <img src="https://flagcdn.com/16x12/kr.png" alt="KR" width="16" height="12"> South Korea | 900 | 0.4% |
| <img src="https://flagcdn.com/16x12/fr.png" alt="FR" width="16" height="12"> France | 728 | 0.3% |
| <img src="https://flagcdn.com/16x12/in.png" alt="IN" width="16" height="12"> India | 552 | 0.2% |
| <img src="https://flagcdn.com/16x12/fi.png" alt="FI" width="16" height="12"> Finland | 485 | 0.2% |
| <img src="https://flagcdn.com/16x12/ru.png" alt="RU" width="16" height="12"> Russia | 447 | 0.2% |
| <img src="https://flagcdn.com/16x12/kw.png" alt="KW" width="16" height="12"> Kuwait | 423 | 0.2% |
| <img src="https://flagcdn.com/16x12/es.png" alt="ES" width="16" height="12"> Spain | 357 | 0.2% |
| <img src="https://flagcdn.com/16x12/nl.png" alt="NL" width="16" height="12"> Netherlands | 355 | 0.2% |
| <img src="https://flagcdn.com/16x12/jp.png" alt="JP" width="16" height="12"> Japan | 349 | 0.1% |
| <img src="https://flagcdn.com/16x12/nz.png" alt="NZ" width="16" height="12"> New Zealand | 323 | 0.1% |
| <img src="https://flagcdn.com/16x12/pk.png" alt="PK" width="16" height="12"> Pakistan | 309 | 0.1% |
| <img src="https://flagcdn.com/16x12/au.png" alt="AU" width="16" height="12"> Australia | 308 | 0.1% |
| <img src="https://flagcdn.com/16x12/cl.png" alt="CL" width="16" height="12"> Chile | 261 | 0.1% |
| <img src="https://flagcdn.com/16x12/tw.png" alt="TW" width="16" height="12"> Taiwan | 253 | 0.1% |
| <img src="https://flagcdn.com/16x12/ir.png" alt="IR" width="16" height="12"> Iran | 218 | 0.1% |
| <img src="https://flagcdn.com/16x12/no.png" alt="NO" width="16" height="12"> Norway | 198 | 0.1% |
| <img src="https://flagcdn.com/16x12/lu.png" alt="LU" width="16" height="12"> Luxembourg | 118 | 0.1% |
| <img src="https://flagcdn.com/16x12/ae.png" alt="AE" width="16" height="12"> United Arab Emirates | 105 | 0.0% |
| <img src="https://flagcdn.com/16x12/vn.png" alt="VN" width="16" height="12"> Vietnam | 83 | 0.0% |
| <img src="https://flagcdn.com/16x12/il.png" alt="IL" width="16" height="12"> Israel | 78 | 0.0% |
| <img src="https://flagcdn.com/16x12/ie.png" alt="IE" width="16" height="12"> Ireland | 62 | 0.0% |
| <img src="https://flagcdn.com/16x12/at.png" alt="AT" width="16" height="12"> Austria | 44 | 0.0% |
| <img src="https://flagcdn.com/16x12/pl.png" alt="PL" width="16" height="12"> Poland | 38 | 0.0% |
| <img src="https://flagcdn.com/16x12/ch.png" alt="CH" width="16" height="12"> Switzerland | 35 | 0.0% |
| <img src="https://flagcdn.com/16x12/it.png" alt="IT" width="16" height="12"> Italy | 35 | 0.0% |
| <img src="https://flagcdn.com/16x12/cz.png" alt="CZ" width="16" height="12"> Czechia | 28 | 0.0% |
| <img src="https://flagcdn.com/16x12/id.png" alt="ID" width="16" height="12"> Indonesia | 26 | 0.0% |
| <img src="https://flagcdn.com/16x12/pt.png" alt="PT" width="16" height="12"> Portugal | 22 | 0.0% |
| <img src="https://flagcdn.com/16x12/my.png" alt="MY" width="16" height="12"> Malaysia | 21 | 0.0% |
| <img src="https://flagcdn.com/16x12/dk.png" alt="DK" width="16" height="12"> Denmark | 20 | 0.0% |
| <img src="https://flagcdn.com/16x12/ee.png" alt="EE" width="16" height="12"> Estonia | 20 | 0.0% |
| <img src="https://flagcdn.com/16x12/tr.png" alt="TR" width="16" height="12"> Türkiye | 20 | 0.0% |
| <img src="https://flagcdn.com/16x12/be.png" alt="BE" width="16" height="12"> Belgium | 17 | 0.0% |
| <img src="https://flagcdn.com/16x12/za.png" alt="ZA" width="16" height="12"> South Africa | 16 | 0.0% |
| <img src="https://flagcdn.com/16x12/sa.png" alt="SA" width="16" height="12"> Saudi Arabia | 13 | 0.0% |
| <img src="https://flagcdn.com/16x12/br.png" alt="BR" width="16" height="12"> Brazil | 12 | 0.0% |
| <img src="https://flagcdn.com/16x12/ro.png" alt="RO" width="16" height="12"> Romania | 12 | 0.0% |
| <img src="https://flagcdn.com/16x12/cr.png" alt="CR" width="16" height="12"> Costa Rica | 10 | 0.0% |
| <img src="https://flagcdn.com/16x12/is.png" alt="IS" width="16" height="12"> Iceland | 9 | 0.0% |
| <img src="https://flagcdn.com/16x12/al.png" alt="AL" width="16" height="12"> Albania | 9 | 0.0% |
| <img src="https://flagcdn.com/16x12/hu.png" alt="HU" width="16" height="12"> Hungary | 8 | 0.0% |
| <img src="https://flagcdn.com/16x12/bd.png" alt="BD" width="16" height="12"> Bangladesh | 6 | 0.0% |
| <img src="https://flagcdn.com/16x12/lv.png" alt="LV" width="16" height="12"> Latvia | 6 | 0.0% |
| <img src="https://flagcdn.com/16x12/am.png" alt="AM" width="16" height="12"> Armenia | 5 | 0.0% |
| <img src="https://flagcdn.com/16x12/ng.png" alt="NG" width="16" height="12"> Nigeria | 5 | 0.0% |
| <img src="https://flagcdn.com/16x12/lt.png" alt="LT" width="16" height="12"> Lithuania | 5 | 0.0% |
| <img src="https://flagcdn.com/16x12/ad.png" alt="AD" width="16" height="12"> Andorra | 5 | 0.0% |
| <img src="https://flagcdn.com/16x12/sk.png" alt="SK" width="16" height="12"> Slovakia | 4 | 0.0% |
| <img src="https://flagcdn.com/16x12/lb.png" alt="LB" width="16" height="12"> Lebanon | 4 | 0.0% |
| <img src="https://flagcdn.com/16x12/co.png" alt="CO" width="16" height="12"> Colombia | 4 | 0.0% |
| <img src="https://flagcdn.com/16x12/si.png" alt="SI" width="16" height="12"> Slovenia | 3 | 0.0% |
| <img src="https://flagcdn.com/16x12/eg.png" alt="EG" width="16" height="12"> Egypt | 3 | 0.0% |
| <img src="https://flagcdn.com/16x12/gr.png" alt="GR" width="16" height="12"> Greece | 3 | 0.0% |
| <img src="https://flagcdn.com/16x12/ps.png" alt="PS" width="16" height="12"> Palestine, State of | 3 | 0.0% |
| <img src="https://flagcdn.com/16x12/th.png" alt="TH" width="16" height="12"> Thailand | 3 | 0.0% |
| <img src="https://flagcdn.com/16x12/az.png" alt="AZ" width="16" height="12"> Azerbaijan | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/ke.png" alt="KE" width="16" height="12"> Kenya | 2 | 0.0% |
| <img src="https://flagcdn.com/16x12/bs.png" alt="BS" width="16" height="12"> Bahamas | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/dz.png" alt="DZ" width="16" height="12"> Algeria | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/gl.png" alt="GL" width="16" height="12"> Greenland | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/jo.png" alt="JO" width="16" height="12"> Jordan | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/ph.png" alt="PH" width="16" height="12"> Philippines | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/pa.png" alt="PA" width="16" height="12"> Panama | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/ma.png" alt="MA" width="16" height="12"> Morocco | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/ml.png" alt="ML" width="16" height="12"> Mali | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/pe.png" alt="PE" width="16" height="12"> Peru | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/qa.png" alt="QA" width="16" height="12"> Qatar | 1 | 0.0% |
| <img src="https://flagcdn.com/16x12/zw.png" alt="ZW" width="16" height="12"> Zimbabwe | 1 | 0.0% |
<!-- COUNTRIES_90_END -->

</td>
</tr>
</table>

<!-- GEO_INSIGHTS_START -->
**Key Insights:**
- **<img src="https://flagcdn.com/16x12/us.png" alt="US" width="16" height="12"> United States dominance** (77.9% in 30d, 80.9% in 90d) consistent across periods
- **57 countries (30d), 77 countries (90d)** demonstrates global reach
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
UV: 40.6% of downloads (32,606)
<!-- UV_INSTALLER_30_END -->

</td>
<td width="50%">

**90 Days**

![Installer Share 90d](reports/compliance-trestle_mcp_installer_90days.png)

<!-- UV_INSTALLER_90_START -->
UV: 44.9% of downloads (105,820)
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
**820 uvx downloads** = HIGH confidence MCP
<!-- UVX_30_END -->

</td>
<td width="50%">

**90 Days**

![UV Subcommands 90d](reports/compliance-trestle_mcp_subcommands_90days.png)

<!-- UVX_90_START -->
**956 uvx downloads** = HIGH confidence MCP
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
UV: 26.2% non-CI (8,538 downloads)
<!-- UV_NON_CI_30_END -->

</td>
<td width="50%">

**90 Days**

![CI vs Non-CI 90d](reports/compliance-trestle_mcp_ci_90days.png)

<!-- UV_NON_CI_90_START -->
UV: 39.6% non-CI (41,922 downloads)
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
820 uvx downloads over 30 days
<!-- DAILY_TREND_30_END -->

</td>
<td width="50%">

**90 Days**

![Daily Trend 90d](reports/compliance-trestle_mcp_daily_90days.png)

<!-- DAILY_TREND_90_START -->
956 uvx downloads over 90 days
<!-- DAILY_TREND_90_END -->

</td>
</tr></table>

**Key Findings:**

<table><tr>
<td width="50%" valign="top">

**30-Day Analysis:**
<!-- MCP_FINDINGS_30_START -->
1. **Confirmed MCP Usage:** 820 downloads using `uvx` subcommand
2. **UV Adoption:** 40.6% of downloads
3. **Interactive Usage:** 26.2% of UV downloads are non-CI

MCP usage is detectable but small. The broader story is UV's growth as a modern Python installer.
<!-- MCP_FINDINGS_30_END -->

</td>
<td width="50%" valign="top">

**90-Day Analysis:**
<!-- MCP_FINDINGS_90_START -->
1. **Confirmed MCP Usage:** 956 downloads using `uvx` subcommand
2. **UV Adoption:** 44.9% of downloads
3. **Interactive Usage:** 39.6% of UV downloads are non-CI

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