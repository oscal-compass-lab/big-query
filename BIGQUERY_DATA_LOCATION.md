# BigQuery Data Location

The BigQuery data is located in **Google's public BigQuery dataset**:

**Dataset Location:** `bigquery-public-data.pypi.file_downloads`

This is a publicly accessible dataset hosted by Google Cloud that contains PyPI (Python Package Index) download statistics.

## Key Points

### 1. Public Dataset
The data is hosted by Google Cloud and is publicly accessible to anyone with a Google Cloud account.

### 2. Access Method
You query this data using Google BigQuery's SQL interface through:
- The Python scripts in the `python/` directory
- Google Cloud credentials (`credentials.json` - which you must create yourself)
- The BigQuery API (enabled via `make enable-api`)

### 3. Data Contents
The dataset includes:
- Download timestamps
- Country codes (from IP addresses)
- Package names and versions
- Installer information (pip, uv, poetry, etc.)
- Operating system and distribution details
- Python versions
- CPU architectures
- CI/CD indicators
- TLS protocols

### 4. Local Reports
Generated reports and visualizations are saved locally in the `reports/` directory after running queries.

### 5. No Raw Data Storage
This repository doesn't store the raw BigQuery data locally - it only queries the public dataset and saves the analysis results.

## Getting Started

To access the data, follow the setup instructions in [HOWTO.md](HOWTO.md) to:
1. Create Google Cloud credentials
2. Enable the BigQuery API
3. Run queries against the public dataset

## Related Documentation

- [HOWTO.md](HOWTO.md) - Complete setup and usage guide
- [BIGQUERY_SCHEMA.md](BIGQUERY_SCHEMA.md) - Dataset schema documentation
- [README.md](README.md) - Project overview and analytics results