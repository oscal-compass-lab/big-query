# CI/CD Pipeline Setup Guide

This guide explains how to set up the automated CI/CD pipeline for BigQuery analytics updates.

---

## Overview

The CI/CD pipeline automatically:
- ✅ Fetches latest BigQuery data on a configurable schedule (default: weekly)
- ✅ Generates 30-day and 90-day reports
- ✅ Creates world maps showing geographic distribution
- ✅ Generates MCP inference analysis charts
- ✅ Creates deployment environment visualizations
- ✅ Commits and pushes updated reports to the repository

**Workflow File:** `.github/workflows/update-analytics.yml`

---

## Schedule Configuration

### Default Schedule
The pipeline runs **weekly on Mondays at 2 AM ET (6 AM UTC)**.

### Customizing the Schedule

Edit the `cron` expression in `.github/workflows/update-analytics.yml`:

```yaml
schedule:
  - cron: '0 6 * * 1'  # minute hour day-of-month month day-of-week
```

**Common schedules:**
- **Daily at 2 AM ET:** `'0 6 * * *'` - Every day at 6 AM UTC (2 AM ET)
- **Weekly (Monday) at 2 AM ET:** `'0 6 * * 1'` - Every Monday at 6 AM UTC (2 AM ET)
- **Bi-weekly at 2 AM ET:** `'0 6 1,15 * *'` - 1st and 15th of each month at 6 AM UTC (2 AM ET)
- **Monthly at 2 AM ET:** `'0 6 1 * *'` - First day of each month at 6 AM UTC (2 AM ET)

**Cron syntax:**
```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
* * * * *
```

**Helpful tool:** [crontab.guru](https://crontab.guru/) - Cron expression editor

---

## Required GitHub Secrets

The pipeline requires two secrets to be configured in your GitHub repository:

### 1. `GCP_CREDENTIALS`
**Description:** Google Cloud service account credentials in JSON format

**How to obtain:**
1. Follow the setup in [HOWTO.md](HOWTO.md) to create a GCP project
2. Run `make credentials` to generate `credentials.json`
3. Copy the entire contents of `credentials.json`

**How to add to GitHub:**
1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `GCP_CREDENTIALS`
5. Value: Paste the entire JSON content from `credentials.json`
6. Click **Add secret**

**Example format:**
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "pypi-analytics-sa@your-project-id.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

### 2. `GCP_PROJECT_ID`
**Description:** Your Google Cloud project ID

**How to obtain:**
```bash
gcloud config get-value project
```

**How to add to GitHub:**
1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `GCP_PROJECT_ID`
5. Value: Your project ID (e.g., `trestle-pypi-yourname`)
6. Click **Add secret**

---

## Manual Trigger

You can manually trigger the workflow from the GitHub UI:

1. Go to **Actions** tab in your repository
2. Select **Update BigQuery Analytics** workflow
3. Click **Run workflow** button
4. Choose options:
   - ✅ Generate 30-day reports (default: true)
   - ✅ Generate 90-day reports (default: true)
5. Click **Run workflow**

This is useful for:
- Testing the pipeline after setup
- Generating reports on-demand
- Updating reports after configuration changes

---

## Workflow Steps

The pipeline executes the following steps:

### 1. **Setup**
- Checks out the repository
- Sets up Python 3.12
- Installs required dependencies

### 2. **Authentication**
- Creates `credentials.json` from GitHub secret
- Verifies credentials file

### 3. **Data Fetching**
- Runs BigQuery queries for 30-day and 90-day periods
- Saves raw reports to `reports/YYYY.MM.DD.trestle.pypi.last-{30,90}.txt`

### 4. **Visualization Generation**
- **World Maps:** Geographic distribution (HTML + PNG)
- **MCP Analysis:** Model Context Protocol usage patterns
- **Deployment Charts:** 8 different deployment environment visualizations

### 5. **Update README**
- Extracts key metrics from generated reports
- Updates README.md with latest statistics
- Updates report date automatically

### 6. **Commit & Push**
- Checks for changes in `reports/` and `README.md`
- Commits with automated message
- Pushes to main branch

### 7. **Monthly Backup Branch**
- Creates/updates a monthly backup branch (e.g., `reports/05` for May)
- Uses month number (01-12) so branches rotate annually
- Force pushes to overwrite previous year's data
- Maintains 12 rotating monthly snapshots

### 8. **Cleanup**
- Removes credentials file (security)
- Displays summary of generated files

---

## Generated Files

Each run generates the following files in the `reports/` directory:

### Text Reports
- `YYYY.MM.DD.trestle.pypi.last-30.txt` - 30-day analytics report
- `YYYY.MM.DD.trestle.pypi.last-90.txt` - 90-day analytics report

### World Maps
- `YYYY.MM.DD.trestle.pypi.map-30.html` - Interactive 30-day map
- `YYYY.MM.DD.trestle.pypi.map-30.png` - Static 30-day map
- `YYYY.MM.DD.trestle.pypi.map-90.html` - Interactive 90-day map
- `YYYY.MM.DD.trestle.pypi.map-90.png` - Static 90-day map

### MCP Analysis
- `mcp_inference_30day.html` - Interactive 30-day MCP dashboard
- `mcp_inference_30day.png` - Static 30-day MCP chart
- `mcp_inference_90day.html` - Interactive 90-day MCP dashboard
- `mcp_inference_90day.png` - Static 90-day MCP chart
- `mcp_inference_explanation_30day.md` - 30-day methodology
- `mcp_inference_explanation_90day.md` - 90-day methodology
- `mcp_installer_share_30day.png` - Installer distribution
- `mcp_installer_share_90day.png` - Installer distribution
- `mcp_uv_subcommands_30day.png` - UV subcommand breakdown
- `mcp_uv_subcommands_90day.png` - UV subcommand breakdown
- `mcp_ci_vs_nonci_30day.png` - CI vs non-CI usage
- `mcp_ci_vs_nonci_90day.png` - CI vs non-CI usage
- `mcp_daily_trend_30day.png` - Daily UV trend
- `mcp_daily_trend_90day.png` - Daily UV trend

### Deployment Visualizations
- `deployment_platforms_30day.html/png` - Platform distribution
- `deployment_platforms_90day.html/png` - Platform distribution
- `deployment_types_30day.html/png` - Deployment types
- `deployment_types_90day.html/png` - Deployment types
- `deployment_architecture_30day.html/png` - CPU architecture
- `deployment_architecture_90day.html/png` - CPU architecture
- `deployment_geographic_30day.html/png` - Geographic deployment
- `deployment_geographic_90day.html/png` - Geographic deployment
- `deployment_enterprise_cloud_30day.html/png` - Enterprise vs cloud
- `deployment_enterprise_cloud_90day.html/png` - Enterprise vs cloud
- `deployment_libc_30day.html/png` - libc distribution
- `deployment_libc_90day.html/png` - libc distribution
- `deployment_use_cases_30day.html/png` - Compliance use cases
- `deployment_use_cases_90day.html/png` - Compliance use cases
- `deployment_summary_30day.html/png` - Summary dashboard
- `deployment_summary_90day.html/png` - Summary dashboard

---

## Monitoring

### View Workflow Runs
1. Go to **Actions** tab in your repository
2. Click on **Update BigQuery Analytics** workflow
3. View run history, logs, and status

### Workflow Status Badge
Add this badge to your README.md to show workflow status:

```markdown
[![Update Analytics](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/update-analytics.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/update-analytics.yml)
```

Replace `YOUR_USERNAME` and `YOUR_REPO` with your GitHub username and repository name.

### Email Notifications
GitHub automatically sends email notifications for workflow failures. Configure in:
**Settings** → **Notifications** → **Actions**

---

## Troubleshooting

### Workflow Fails with "Credentials not found"
**Solution:** Verify `GCP_CREDENTIALS` secret is set correctly:
1. Check secret exists in **Settings** → **Secrets and variables** → **Actions**
2. Ensure the JSON is valid (no extra spaces or line breaks)
3. Re-create the secret if needed

### Workflow Fails with "Permission denied" on BigQuery
**Solution:** Verify service account has correct roles:
```bash
# Check current roles
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:pypi-analytics-sa@*"

# Re-grant roles if needed
make credentials
```

### No Changes Committed
**Possible causes:**
- No new data available (reports identical to previous run)
- BigQuery returned same results
- This is normal if data hasn't changed

### Workflow Times Out
**Solution:** Increase timeout in workflow file:
```yaml
jobs:
  update-analytics:
    timeout-minutes: 30  # Default is 360 (6 hours)
```

### Rate Limiting
GitHub Actions has usage limits:
- **Public repos:** Unlimited minutes
- **Private repos:** 2,000 minutes/month (free tier)

BigQuery has quotas:
- **Free tier:** 1 TB queries/month
- **Typical usage:** ~500 MB per full run

---

## Cost Considerations

### GitHub Actions
- **Public repositories:** Free unlimited minutes
- **Private repositories:** 2,000 free minutes/month

### Google Cloud BigQuery
- **Free tier:** 1 TB queries/month
- **Typical usage per run:** ~500 MB
- **Monthly cost (weekly runs):** $0.00 (within free tier)
- **Estimated annual cost:** $0.00 (within free tier)

**Note:** The public PyPI dataset is free to query within the 1 TB/month limit.

---

## Security Best Practices

### ✅ DO
- Store credentials as GitHub secrets (never commit to repo)
- Use service accounts with minimal required permissions
- Rotate service account keys periodically
- Review workflow logs for sensitive data leaks
- Use `if: always()` for credential cleanup steps

### ❌ DON'T
- Commit `credentials.json` to the repository
- Share service account keys publicly
- Use personal Google accounts for automation
- Log credential contents in workflow output
- Skip the cleanup step

---

## Customization

### Change Package Name
Edit the `env` section in `.github/workflows/update-analytics.yml`:
```yaml
env:
  PACKAGE: your-package-name  # Change this
  PYTHON_VERSION: '3.12'
```

### Disable Specific Reports
Comment out steps you don't need:
```yaml
# - name: Generate MCP analysis
#   if: false  # Disable this step
#   env:
#     GOOGLE_APPLICATION_CREDENTIALS: credentials.json
#   run: |
#     ...
```

### Add Custom Reports
Add new steps after existing ones:
```yaml
- name: Generate custom report
  env:
    GOOGLE_APPLICATION_CREDENTIALS: credentials.json
  run: |
    python python/your_custom_script.py \
      --package ${{ env.PACKAGE }} \
      --days 30 \
      --project ${{ secrets.GCP_PROJECT_ID }} \
      --credentials credentials.json
```

---

## Testing the Pipeline

### Local Testing
Before enabling the workflow, test locally:
```bash
# Test data fetching
make fetch

# Test chart generation
make process

# Test full workflow
make all
```

### First Run
1. Set up GitHub secrets (see above)
2. Manually trigger the workflow
3. Monitor the run in Actions tab
4. Verify generated files in `reports/` directory
5. Check commit was pushed successfully

### Validation Checklist
- [ ] GitHub secrets configured correctly
- [ ] Workflow runs without errors
- [ ] Reports generated in `reports/` directory
- [ ] Charts (PNG/HTML) created successfully
- [ ] Changes committed and pushed to repository
- [ ] No credentials leaked in logs
- [ ] Workflow completes within reasonable time (<15 minutes)

---

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review workflow logs in GitHub Actions
3. Consult [HOWTO.md](HOWTO.md) for setup details
4. Open an issue in the repository

---

## Related Documentation

- **[HOWTO.md](HOWTO.md)** - Initial setup and local usage
- **[README.md](README.md)** - Project overview and analytics
- **[DEPLOYMENT_ANALYSIS.md](DEPLOYMENT_ANALYSIS.md)** - Deployment environment analysis
- **[BIGQUERY_SCHEMA.md](BIGQUERY_SCHEMA.md)** - BigQuery dataset schema

---

**Last Updated:** 2026-05-15

**Workflow Version:** 1.0