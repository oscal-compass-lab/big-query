# PyPI BigQuery Analytics

Query Google BigQuery's public PyPI download dataset to analyze package downloads. This tool helps you understand who is downloading your package, from where, and how.

---

## ⚠️ Important: Credentials Required

**This repository does NOT include Google Cloud credentials.** You must create your own credentials after cloning this repository.

The `credentials.json` file is required to run queries but is excluded from version control for security. Follow the setup instructions below to create your credentials.

---

## Prerequisites

- **Linux** (tested on Fedora 38+, should work on other distributions)
- **Python 3** and pip (usually pre-installed)
- **A Google account** (free Gmail account works)
- **Credit card linked to Google Cloud** (required for billing, but querying the public PyPI dataset is **free up to 1 TB/month** — typical queries cost essentially nothing)

---

## Quick Start Setup

Follow these steps in order:

### 1. Install System Dependencies

```bash
make deps
```

This installs the **Google Cloud SDK** (`gcloud`) via the official Google repository.

### 2. Create Python Virtual Environment

```bash
make venv
```

This creates `.venv.bq/` and installs required Python packages:
- `google-cloud-bigquery` — BigQuery client
- `google-auth` — authentication
- `pandas`, `db-dtypes` — data handling
- `rich` — pretty terminal output
- `plotly`, `kaleido` — map generation

### 3. Authenticate with Google Cloud

```bash
make gcloud-login
```

This opens your browser **twice**:
1. First for your user account login
2. Then for Application Default Credentials

Use the same Google account for both.

### 4. Create a GCP Project

```bash
make create-project
```

This creates a project named `trestle-pypi-<username>` and sets it as active.

> **First time?** If you see "Callers must accept Terms of Service" error:
> 1. Visit https://console.cloud.google.com/projectcreate
> 2. Accept the Google Cloud Terms of Service
> 3. Close the browser tab (don't create a project there)
> 4. Run `make create-project` again

> **Billing required:** After creating the project, go to https://console.cloud.google.com/billing and link a billing account. You won't be charged for querying the public PyPI dataset within the 1 TB free tier.

**Alternative:** Use an existing project:
```bash
make list-projects              # See your projects
make set-project PROJECT=my-id  # Set active project
```

### 5. Enable BigQuery API

```bash
make enable-api
```

Takes about 30 seconds. Only needs to be done once per project.

### 6. Create Service Account Credentials

```bash
make credentials
```

This:
1. Creates a service account named `pypi-analytics-sa`
2. Grants it `BigQuery Data Viewer` and `BigQuery Job User` roles
3. Downloads a key to `credentials.json`

> ⚠️ **IMPORTANT:** Keep `credentials.json` private! It's already in `.gitignore`. Never commit it to git or share it publicly.

---

## Running Queries

Once setup is complete, run any of these:

### Basic Reports

```bash
# All reports at once (recommended first run)
make query-all

# Individual reports
make countries       # Top countries by download count
make os              # OS and Linux distro breakdown
make ci              # CI/CD pipeline vs human installs
make installer       # pip vs poetry vs uv etc.
make python-ver      # Python version distribution
make versions        # Which package versions are being used
make trend           # Daily download sparkline + table
```

### Advanced Analytics

```bash
# All advanced reports
make advanced-all

# Individual advanced reports
make user-agents     # Analyze user agents (MCP, CI/CD, automation)
make implementation  # Python implementation details
make patterns        # Download patterns by time
make endpoints       # File download analysis
make tls             # TLS protocol usage
make cpu             # CPU architecture distribution
make setuptools      # Setuptools version distribution
make unique          # Unique downloader estimates
make raw-sample      # View raw sample records
```

### Generate Reports and Maps

```bash
# Generate timestamped reports
make reports         # Both 30-day and 90-day reports
make report-last-30  # 30-day report only
make report-last-90  # 90-day report only

# Generate world maps from reports
make maps            # Both 30-day and 90-day maps
make map-30          # 30-day map only
make map-90          # 90-day map only
```

Reports are saved to `reports/` directory with timestamps like:
- `2026.05.10.trestle.pypi.last-30.txt`
- `2026.05.10.trestle.pypi.map-30.html`
- `2026.05.10.trestle.pypi.map-30.png`

### Customize Queries

Override the package name or time window:

```bash
# Query a different package
PACKAGE=my-package make query-all

# Look back 90 days instead of 30
DAYS=90 make trend

# Both
PACKAGE=my-package DAYS=60 make countries
```

---

## Understanding the Output

### CI vs Human Installs
This is the most important report for understanding *real* adoption. A large share of PyPI downloads for DevSecOps tools come from CI/CD pipelines re-installing on every build — not unique users. Check this first.

### Countries
Country is derived from the downloader's IP address by PyPI's CDN (Fastly). `None` means the country could not be determined (often corporate proxies).

### OS / Distro
- **Alpine Linux** → almost certainly Docker containers
- **Amazon Linux** → AWS EC2 or Lambda
- **Ubuntu / Debian** → developer workstations or GitHub Actions runners
- **Red Hat / RHEL** → enterprise environments

### Installer
- `pip` → standard install
- `uv` → fast modern installer, growing fast
- `poetry` → dependency management
- `bandersnatch` / `None` → mirrors, often inflating counts

### Versions
Old versions still being downloaded means users haven't upgraded, or old versions are pinned in CI pipelines.

---

## Cost Estimate

Each query scans a portion of the PyPI dataset. Rough estimates for a typical package:

| Query | Data Scanned | Cost |
|-------|-------------|------|
| countries (30 days) | ~50–200 MB | $0.00 |
| query-all (30 days) | ~500 MB | $0.00 |
| query-all (365 days) | ~2–5 GB | $0.01 |

Google's free tier covers **1 TB per month**, so you can run these queries hundreds of times before paying anything.

---

## Troubleshooting

**`gcloud: command not found`**
→ Run `make deps` again, or restart your shell: `source ~/.bashrc`

**`Permission denied` on BigQuery query**
→ Re-run `make credentials` to ensure the service account has the right roles.

**`credentials.json not found`**
→ Run `make credentials` — this file must be created by you after cloning the repo.

**`PROJECT_ID not set`**
→ Run `gcloud config set project YOUR_PROJECT_ID` or `make set-project PROJECT=your-id`

**Billing error on API enable**
→ Go to https://console.cloud.google.com/billing and add a payment method. You won't be charged within the free tier.

**`403 Access Denied` on bigquery-public-data**
→ This usually means billing isn't enabled on your project. Even free-tier queries require a billing account to be linked.

---

## Project Structure

```
.
├── Makefile              # All automation and commands
├── README.md             # This file
├── python/               # Python scripts
│   ├── query.py          # Basic BigQuery queries
│   ├── query_advanced.py # Advanced analytics queries
│   ├── map_downloads.py  # Generate maps from live queries
│   ├── map_from_reports.py # Generate maps from saved reports
│   └── to_markdown.py    # Convert output to Markdown
├── credentials.json      # ⚠️ YOU MUST CREATE THIS (not in repo)
├── .venv.bq/             # Virtual environment (created by make venv)
└── reports/              # Generated reports and maps
```

---

## Security Notes

- **Never commit `credentials.json`** to version control
- The `.gitignore` file is configured to exclude credentials
- Service account keys should be treated as passwords
- Rotate keys periodically via Google Cloud Console
- Delete unused service accounts

---

## Cleanup

Remove virtual environment and cached files:

```bash
make clean
```

This keeps `credentials.json` intact. To remove credentials, delete the file manually.

---

## License

See [LICENSE](LICENSE) file for details.

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Google Cloud BigQuery documentation
3. Open an issue in this repository

---

**Made with ❤️ for the open source community**
