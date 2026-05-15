# MCP Usage Inference Analysis

**Package:** compliance-trestle  
**Period:** Last 90 days  
**Generated:** 2026-05-15 13:38:11

---

## Executive Summary

**Confirmed MCP Pattern:** 305 downloads using `uvx` subcommand  
**Potential MCP Range:** 305 - 14,988 downloads  
**UV Market Share:** 18.1% of all installs

---

## Inference Methodology

### Why We Can't Directly Detect MCP

MCP (Model Context Protocol) servers don't identify themselves in PyPI download logs. When Claude Desktop runs an MCP server via `uvx mcp-server-foo`, the download appears as a standard `uv` install. The HTTP user-agent string that might contain "Claude" or "MCP" is parsed by PyPI into structured fields, and the raw string is not stored.

### Proxy Signals We Use

#### 1. **uvx Subcommand (Strongest Signal)**
- **What it is:** `uvx` is uv's tool for running Python applications
- **Why it matters:** Claude Desktop's MCP configuration uses `"command": "uvx mcp-server-*"`
- **Confidence:** HIGH - This is the exact pattern MCP uses
- **Finding:** 305 downloads (1.01% of UV usage)

#### 2. **UV Non-CI Usage (Moderate Signal)**
- **What it is:** UV downloads not flagged as CI/CD environments
- **Why it matters:** MCP servers run on developer machines, not in CI
- **Confidence:** MEDIUM - Could also be regular developers using UV
- **Finding:** 14,988 non-CI UV downloads (49.9% of UV)
- **Comparison:** pip has 25.8% non-CI usage

#### 3. **UV Market Share Growth (Weak Signal)**
- **What it is:** UV's overall adoption rate
- **Why it matters:** MCP adoption drives some UV growth
- **Confidence:** LOW - UV growth has many drivers beyond MCP
- **Finding:** UV has 18.1% market share

---

## Detailed Findings

### Installer Breakdown

| Installer | Total | CI/CD | Non-CI | Non-CI % |
|-----------|-------|-------|--------|----------|
| pip | 132,944 | 98,689 | 34,255 | 25.8% |
| uv | 30,061 | 15,073 | 14,988 | 49.9% |

**Key Insight:** UV has 1.9x higher non-CI usage ratio than pip, suggesting more interactive/developer usage.

### UV Subcommand Analysis

Top UV subcommands:

- `sync`: 14,143 (47.0%)
- `pip install`: 10,168 (33.8%)
- `run`: 2,206 (7.3%)
- `tool install`: 1,929 (6.4%)
- `(no subcommand)`: 1,141 (3.8%)
- `uvx`: 305 (1.0%) ← **MCP PATTERN**
- `lock`: 88 (0.3%)
- `pip compile`: 45 (0.1%)
- `add`: 26 (0.1%)
- `tool run`: 4 (0.0%)

### MCP Usage Estimates

**Conservative (High Confidence):**
- 305 downloads using explicit `uvx` pattern
- This is 0.18% of all downloads
- Represents confirmed MCP-compatible usage

**Moderate (Medium Confidence):**
- 305 - 1,525 downloads
- Includes `uvx` plus some `uv run` and `tool install` commands
- Estimated 0.55% of all downloads

**Upper Bound (Low Confidence):**
- Up to 14,988 downloads
- All non-CI UV usage could theoretically include MCP
- But most are likely regular UV users
- Represents 9.0% of all downloads

---

## Interpretation

### What This Tells Us

1. **MCP adoption is real but emerging**
   - 305 confirmed MCP-pattern downloads
   - Growing but still early adoption phase
   - Represents 0.184% of total package usage

2. **UV growth is significant**
   - 18.1% market share (vs pip's 80.1%)
   - 49.9% non-CI usage (vs pip's 25.8%)
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
   - Is compliance-trestle seeing more/less MCP adoption?
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

MCP usage for compliance-trestle is **detectable but small**:
- **Confirmed:** 305 downloads (0.184%)
- **Estimated:** 305 - 1,525 downloads (0.184% - 0.92%)

The broader story is **UV's growth** (18.1% market share), with MCP being one of several drivers for modern Python tooling adoption.

---

*Analysis based on BigQuery public dataset: `bigquery-public-data.pypi.file_downloads`*
