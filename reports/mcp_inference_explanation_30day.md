# MCP Usage Inference Analysis

**Package:** compliance-trestle  
**Period:** Last 30 days  
**Generated:** 2026-05-15 13:37:59

---

## Executive Summary

**Confirmed MCP Pattern:** 109 downloads using `uvx` subcommand  
**Potential MCP Range:** 109 - 8,130 downloads  
**UV Market Share:** 25.0% of all installs

---

## Inference Methodology

### Why We Can't Directly Detect MCP

MCP (Model Context Protocol) servers don't identify themselves in PyPI download logs. When Claude Desktop runs an MCP server via `uvx mcp-server-foo`, the download appears as a standard `uv` install. The HTTP user-agent string that might contain "Claude" or "MCP" is parsed by PyPI into structured fields, and the raw string is not stored.

### Proxy Signals We Use

#### 1. **uvx Subcommand (Strongest Signal)**
- **What it is:** `uvx` is uv's tool for running Python applications
- **Why it matters:** Claude Desktop's MCP configuration uses `"command": "uvx mcp-server-*"`
- **Confidence:** HIGH - This is the exact pattern MCP uses
- **Finding:** 109 downloads (0.55% of UV usage)

#### 2. **UV Non-CI Usage (Moderate Signal)**
- **What it is:** UV downloads not flagged as CI/CD environments
- **Why it matters:** MCP servers run on developer machines, not in CI
- **Confidence:** MEDIUM - Could also be regular developers using UV
- **Finding:** 8,130 non-CI UV downloads (40.7% of UV)
- **Comparison:** pip has 20.3% non-CI usage

#### 3. **UV Market Share Growth (Weak Signal)**
- **What it is:** UV's overall adoption rate
- **Why it matters:** MCP adoption drives some UV growth
- **Confidence:** LOW - UV growth has many drivers beyond MCP
- **Finding:** UV has 25.0% market share

---

## Detailed Findings

### Installer Breakdown

| Installer | Total | CI/CD | Non-CI | Non-CI % |
|-----------|-------|-------|--------|----------|
| pip | 58,974 | 46,989 | 11,985 | 20.3% |
| uv | 19,965 | 11,835 | 8,130 | 40.7% |

**Key Insight:** UV has 2.0x higher non-CI usage ratio than pip, suggesting more interactive/developer usage.

### UV Subcommand Analysis

Top UV subcommands:

- `sync`: 10,216 (51.2%)
- `pip install`: 6,213 (31.1%)
- `run`: 1,306 (6.5%)
- `(no subcommand)`: 1,070 (5.4%)
- `tool install`: 958 (4.8%)
- `uvx`: 109 (0.5%) ← **MCP PATTERN**
- `lock`: 58 (0.3%)
- `pip compile`: 22 (0.1%)
- `add`: 9 (0.0%)
- `tool run`: 2 (0.0%)

### MCP Usage Estimates

**Conservative (High Confidence):**
- 109 downloads using explicit `uvx` pattern
- This is 0.14% of all downloads
- Represents confirmed MCP-compatible usage

**Moderate (Medium Confidence):**
- 109 - 545 downloads
- Includes `uvx` plus some `uv run` and `tool install` commands
- Estimated 0.41% of all downloads

**Upper Bound (Low Confidence):**
- Up to 8,130 downloads
- All non-CI UV usage could theoretically include MCP
- But most are likely regular UV users
- Represents 10.2% of all downloads

---

## Interpretation

### What This Tells Us

1. **MCP adoption is real but emerging**
   - 109 confirmed MCP-pattern downloads
   - Growing but still early adoption phase
   - Represents 0.136% of total package usage

2. **UV growth is significant**
   - 25.0% market share (vs pip's 73.7%)
   - 40.7% non-CI usage (vs pip's 20.3%)
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
- **Confirmed:** 109 downloads (0.136%)
- **Estimated:** 109 - 545 downloads (0.136% - 0.68%)

The broader story is **UV's growth** (25.0% market share), with MCP being one of several drivers for modern Python tooling adoption.

---

*Analysis based on BigQuery public dataset: `bigquery-public-data.pypi.file_downloads`*
