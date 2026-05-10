# BigQuery PyPI Dataset Schema

Based on actual data from `bigquery-public-data.pypi.file_downloads`

## Available Fields

### Top-Level Fields
- `timestamp` - Download timestamp (datetime)
- `country_code` - 2-letter country code (string)
- `project` - Package name (string)
- `tls_protocol` - TLS version (e.g., "TLSv1.3")
- `tls_cipher` - TLS cipher suite (e.g., "TLS_AES_128_GCM_SHA256")
- `url` - Download URL path (string)

### file (STRUCT)
- `file.filename` - Full filename with extension
- `file.project` - Package name
- `file.version` - Package version
- `file.type` - File type (e.g., "bdist_wheel")

### details (STRUCT)

#### details.installer (STRUCT)
- `details.installer.name` - Installer name (pip, uv, poetry, Nexus, etc.)
- `details.installer.version` - Installer version
- `details.installer.subcommand` - Subcommand used (e.g., "pip install")

#### details.implementation (STRUCT)
- `details.implementation.name` - Python implementation (CPython, PyPy, etc.)
- `details.implementation.version` - Implementation version

#### details.distro (STRUCT)
- `details.distro.name` - Distribution name (Ubuntu, RHEL, macOS, etc.)
- `details.distro.version` - Distribution version
- `details.distro.id` - Distribution ID (e.g., "noble", "Plow")
- `details.distro.libc` - STRUCT with lib and version

#### details.system (STRUCT)
- `details.system.name` - OS name (Linux, Darwin, Windows)
- `details.system.release` - Kernel/OS release version

#### Other details fields
- `details.python` - Python version string
- `details.cpu` - CPU architecture (x86_64, arm64, etc.)
- `details.openssl_version` - OpenSSL version string
- `details.setuptools_version` - Setuptools version
- `details.rustc_version` - Rust compiler version (if applicable)
- `details.ci` - Boolean indicating CI/CD environment (or NULL)

## Sample Record

```json
{
  "timestamp": "2026-05-08 20:22:11+00:00",
  "country_code": "US",
  "project": "compliance-trestle",
  "tls_protocol": "TLSv1.3",
  "tls_cipher": "TLS_AES_128_GCM_SHA256",
  "url": "/packages/.../compliance_trestle-4.0.2-py3-none-any.whl",
  "file": {
    "filename": "compliance_trestle-4.0.2-py3-none-any.whl",
    "project": "compliance-trestle",
    "version": "4.0.2",
    "type": "bdist_wheel"
  },
  "details": {
    "installer": {
      "name": "pip",
      "version": "26.1.1",
      "subcommand": null
    },
    "python": "3.14.2",
    "implementation": {
      "name": "CPython",
      "version": "3.14.2"
    },
    "distro": {
      "name": "macOS",
      "version": "15.7.3",
      "id": null,
      "libc": null
    },
    "system": {
      "name": "Darwin",
      "release": "24.6.0"
    },
    "cpu": "arm64",
    "openssl_version": "OpenSSL 3.6.0 1 Oct 2025",
    "setuptools_version": null,
    "rustc_version": null,
    "ci": null
  }
}
```

## Important Notes

1. **No User-Agent Field**: The dataset does NOT include HTTP user-agent strings, so we cannot detect:
   - MCP servers
   - AI tools (Claude, Copilot, etc.)
   - Browser types
   - Custom automation tools

2. **What We CAN Detect**:
   - Installer tools (pip, uv, poetry, etc.)
   - CI/CD environments (via `details.ci` boolean)
   - Operating systems and distributions
   - Python versions and implementations
   - CPU architectures
   - Geographic distribution
   - TLS/security protocols

3. **NULL Values**: Many fields can be NULL, especially for:
   - Mirror downloads (bandersnatch, Nexus)
   - Older download records
   - Incomplete metadata

## Useful Queries

See the working queries in:
- `python/query.py` - Basic analytics (countries, OS, versions, CI, installer, Python version, trend)
- `python/query_advanced.py` - Advanced analytics (implementation, CPU, TLS, setuptools)

The queries that work with the current schema:
- ✅ Total downloads
- ✅ CI vs Human breakdown
- ✅ Countries
- ✅ OS/Distro
- ✅ Package versions
- ✅ Installer tools
- ✅ Python versions
- ✅ Daily trends
- ✅ Implementation details
- ✅ CPU architecture
- ✅ TLS protocols
- ✅ Setuptools versions
- ✅ Download patterns by time
- ✅ File type analysis

Queries that DON'T work:
- ❌ User agent analysis (field doesn't exist)
- ❌ MCP server detection (no user agent)
- ❌ Browser detection (no user agent)