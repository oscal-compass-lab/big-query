# Deployment Environment Analysis

This document explains how to analyze and visualize PyPI download distribution beyond just country codes, using the real metadata available in BigQuery's PyPI dataset.

## Quick Start: Generate Charts

```bash
# Generate all deployment environment charts (30 days by default)
make viz-deploy

# Generate 30-day charts
make viz-deploy-30

# Generate 90-day charts
make viz-deploy-90
```

This creates 8 interactive HTML charts (and PNG images if kaleido is installed) in the `reports/` directory:
1. **Platform Distribution** - Pie chart of AWS, containers, enterprise, etc.
2. **Deployment Types** - Bar chart of container vs VM vs developer environments
3. **Architecture Distribution** - CPU architectures by platform
4. **Geographic Deployment** - Top 15 countries by deployment type
5. **Enterprise vs Cloud-Native** - Sunburst chart showing patterns
6. **libc Distribution** - Treemap of glibc vs musl (container signal)
7. **Compliance Use Cases** - Donut chart of C2P, AWS automation, etc.
8. **Summary Dashboard** - Multi-panel overview with key metrics

## What's Available

The BigQuery PyPI dataset **does NOT include**:
- City or state information
- IP addresses
- GPS coordinates
- Detailed user agent strings

The dataset **DOES include** powerful deployment signals:
- `details.distro.name` - Distribution name (Amazon Linux, Alpine, RHEL, etc.)
- `details.distro.libc.lib` - libc type (glibc vs musl = container signal)
- `details.cpu` - CPU architecture (x86_64, aarch64/arm64)
- `details.ci` - Boolean indicating CI/CD environment
- `details.system.name` - OS name (Linux, Darwin, Windows)
- `country_code` - 2-letter country code

## Key Insights You Can Extract

### 1. Cloud Provider Detection

**Via `details.distro.name`:**
- `Amazon Linux` / `Amazon Linux AMI` → AWS EC2
- `Alpine Linux` → Docker/Kubernetes containers
- `Red Hat Enterprise Linux` → Enterprise/OpenShift/DoD
- `Oracle Linux` → Oracle Cloud
- `Debian` → Often GCP Compute Engine
- `Ubuntu` + `ci=true` → GitHub Actions / standard CI

### 2. Container vs VM Detection

**Via `details.distro.libc.lib`:**
- `musl` → Alpine Linux containers (Docker/K8s)
- `glibc` → Standard Linux VMs and bare metal

### 3. Architecture Distribution

**Via `details.cpu`:**
- `aarch64` + `Amazon Linux` → AWS Graviton (cost-optimized ARM)
- `aarch64` + `Darwin` → Apple Silicon Macs (developers)
- `x86_64` → Traditional Intel/AMD infrastructure
- `arm64` on Linux → Cloud ARM instances

### 4. Enterprise vs Cloud-Native

**Combined signals:**
- RHEL + non-CI → Government/DoD enterprise deployments
- Alpine + CI → Containerized CI pipelines (C2P use case)
- Amazon Linux + CI → AWS CodePipeline / compliance automation
- macOS + non-CI → Local development

## Usage Examples

### Run All Deployment Analytics

```bash
make deploy-all PACKAGE=compliance-trestle DAYS=30
```

### Specific Analyses

```bash
# Cloud provider detection
make deploy-cloud

# Container vs VM breakdown
make deploy-containers

# CPU architecture distribution
make deploy-arch

# Enterprise vs cloud-native patterns
make deploy-enterprise

# Compliance-trestle specific use cases
make deploy-use-cases

# Geographic distribution by platform
make deploy-geographic

# libc analysis (container signal)
make deploy-libc

# High-level summary
make deploy-summary
```

### USA-Specific Analysis

While we can't get state-level data, we can infer regional patterns:

```bash
# All USA analytics
make usa-all

# USA totals and global share
make usa-total

# USA OS/distribution breakdown
make usa-os

# USA CI vs human usage
make usa-ci

# USA time patterns (infer East/West coast)
make usa-time

# USA enterprise indicators
make usa-enterprise
```

## Understanding the Results

### For compliance-trestle Specifically

**Alpine Linux + CI = C2P Pipeline Usage**
- Containerized Kyverno policy generation
- Kubernetes compliance automation

**Amazon Linux + CI = AWS Compliance Automation**
- Cloud compliance as code
- Automated OSCAL generation

**RHEL = Government/DoD Compliance**
- Enterprise OSCAL frameworks
- On-premise compliance tools

**macOS + non-CI = Compliance Development**
- Developers building compliance tools
- Local testing and exploration

### Regional Inference (USA)

**Time-based patterns:**
- Peak 14-18 UTC + Apple Silicon → West Coast tech (SF/Seattle)
- Peak 14-18 UTC + Windows → East Coast corporate (NYC/Boston/DC)
- Peak 17-22 UTC + macOS → West Coast developers
- 24/7 pattern + Linux → Data center/cloud deployments

**Platform patterns:**
- AWS + CI → Cloud regions (us-east-1, us-west-2, etc.)
- RHEL → Government facilities (distributed)
- Alpine → Cloud-native deployments (region-agnostic)

## Example Queries

The scripts use queries like:

```sql
-- Cloud provider detection
SELECT
    country_code,
    details.distro.name AS distro,
    details.ci AS is_ci,
    COUNT(*) AS download_count
FROM `bigquery-public-data.pypi.file_downloads`
WHERE file.project = 'compliance-trestle'
  AND details.distro.name IS NOT NULL
GROUP BY country_code, distro, is_ci
ORDER BY download_count DESC
```

```sql
-- Container detection via libc
SELECT
    details.distro.libc.lib AS libc,
    details.distro.name AS distro,
    COUNT(*) AS download_count
FROM `bigquery-public-data.pypi.file_downloads`
WHERE file.project = 'compliance-trestle'
  AND details.distro.libc.lib IS NOT NULL
GROUP BY libc, distro
ORDER BY download_count DESC
```

## Limitations

1. **No city/state data** - Only country codes available
2. **No IP addresses** - Privacy protection
3. **Inference only** - We infer deployment types from metadata
4. **CI flag noise** - Not all CI environments set the flag correctly
5. **Mirror downloads** - Some downloads via mirrors have incomplete metadata

## Alternative Approaches

If you need more detailed geographic distribution:

1. **Add telemetry to your package** - Collect opt-in usage data
2. **CDN logs** - If you control distribution
3. **Contact PyPI** - Request aggregated city/state data
4. **External enrichment** - Export and enrich with other data sources

## Generated Charts

The visualization script creates the following charts:

### 1. Platform Distribution (Pie Chart)
Shows the breakdown of AWS, Containers (Alpine), Enterprise (RHEL), Ubuntu, Debian, macOS, Windows, and Other Linux.

### 2. Deployment Types (Horizontal Bar Chart)
Detailed breakdown: Containers (musl/Alpine), AWS CI/CD, AWS VMs, Enterprise VMs, CI Pipelines, Developer Macs, Windows.

### 3. Architecture Distribution (Stacked Bar Chart)
CPU architectures (x86_64, aarch64, arm64) by platform - shows ARM adoption (Graviton, Apple Silicon).

### 4. Geographic Deployment (Stacked Bar Chart)
Top 15 countries showing deployment type distribution - reveals regional preferences.

### 5. Enterprise vs Cloud-Native (Sunburst Chart)
Hierarchical view of Enterprise (RHEL, Oracle, SUSE), Cloud-Native (Alpine, AWS CI, Ubuntu CI), Developer (macOS), and Corporate (Windows), each split by CI/CD vs Interactive.

### 6. libc Distribution (Treemap)
Shows glibc vs musl distribution (musl = containerized deployments), broken down by distro.

### 7. Compliance Use Cases (Donut Chart)
Specific to compliance-trestle: C2P Pipeline, AWS Automation, Gov/DoD Compliance, CI Compliance, Development, SDK Usage.

### 8. Summary Dashboard (Multi-Panel)
Key metrics with gauges: Container adoption, AWS usage, Enterprise deployment, CI/CD percentage, ARM architecture adoption, musl libc usage.

## Scripts

- `python/visualize_deployment.py` - Generate all deployment charts (HTML + PNG)
- `python/query_deployment_environments.py` - Main deployment analysis (text output)
- `python/query_usa_details.py` - USA-specific analysis (text output)
- `python/query_endpoint_distribution.py` - Alternative endpoint inference (experimental)

## Made with Bob

This analysis framework was created to maximize insights from the available BigQuery PyPI metadata, focusing on deployment environment patterns rather than geographic precision.