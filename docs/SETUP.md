# Setup Guide

Complete setup instructions for running the PyPI BigQuery Analytics pipeline with GitHub Actions.

## Prerequisites

1. **Google Cloud Project** with BigQuery API enabled
2. **Service Account** with BigQuery Data Viewer role and JSON key
3. **GitHub Repository**

## Google Cloud Setup

### 1. Create a Google Cloud Project

```bash
# Create project (if you don't have one)
gcloud projects create YOUR-PROJECT-ID

# Set as default
gcloud config set project YOUR-PROJECT-ID
```

### 2. Enable Required APIs

```bash
gcloud services enable bigquery.googleapis.com
gcloud services enable iamcredentials.googleapis.com
gcloud services enable sts.googleapis.com
```

### 3. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create pypi-analytics \
    --display-name="PyPI Analytics Service Account"

# Grant BigQuery Data Viewer role
gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
    --member="serviceAccount:pypi-analytics@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataViewer"

# Grant BigQuery Job User role (to run queries)
gcloud projects add-iam-policy-binding YOUR-PROJECT-ID \
    --member="serviceAccount:pypi-analytics@YOUR-PROJECT-ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.jobUser"
```

### 4. Create Service Account Key

```bash
# Create and download service account key
gcloud iam service-accounts keys create pypi-analytics-key.json \
  --iam-account=pypi-analytics@YOUR-PROJECT-ID.iam.gserviceaccount.com

# Display the key content (you'll need this for GitHub secrets)
cat pypi-analytics-key.json
```

**Important Security Notes:**
- Keep this JSON key file secure and never commit it to version control
- The key will be stored as a GitHub secret
- Consider rotating keys periodically for security
- Delete the local key file after adding it to GitHub secrets

## GitHub Setup

### 1. Fork/Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/big-query-pypi.git
cd big-query-pypi
```

### 2. Configure GitHub Secrets

Go to your repository: **Settings → Secrets and variables → Actions → New repository secret**

Add these two secrets:

#### `GCP_SERVICE_ACCOUNT_KEY`

The entire contents of your service account JSON key file (from step 4 above).

Copy the entire JSON content including the curly braces:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "pypi-analytics@your-project-id.iam.gserviceaccount.com",
  ...
}
```

#### `GCP_PROJECT_ID`

Your Google Cloud project ID:
```
YOUR-PROJECT-ID
```

**Security Note:** After adding the key to GitHub secrets, delete the local JSON file:
```bash
rm pypi-analytics-key.json
```

### 3. Customize Configuration

Edit `.github/workflows/update-analytics.yml`:

```yaml
env:
  DEFAULT_PACKAGE: 'your-package-name'  # Change to your PyPI package
  DEFAULT_DAYS_30: 30
  DEFAULT_DAYS_90: 90

on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC - adjust as needed
```

### 4. Understand the Template System

The pipeline uses a template-based approach to prevent cross-contamination between runs:

- **README.template** - Clean template with no data numbers, only structure and placeholders
- **README.wip** - Temporary work file (auto-generated and cleaned up, gitignored)
- **README.md** - Final output file with populated data

**How it works:**
1. Each run copies `README.template` to `README.wip` (fresh start)
2. Data is populated into `README.wip`
3. `README.wip` is copied to `README.md` (atomic replacement)
4. `README.wip` is automatically deleted

**Important:** Do not manually edit `README.md` - your changes will be overwritten. Instead:
- Edit `README.template` for structural changes
- The pipeline will regenerate `README.md` from the template

### 5. Update README Template

Edit `README.template` (not README.md) to customize:
- Package name references
- GitHub username/repo in badge URL
- Section descriptions
- Any structural content

The template contains placeholders like `PLACEHOLDER` that will be replaced with actual data.

### 6. Enable GitHub Actions

1. Go to **Actions** tab in your repository
2. Click "I understand my workflows, go ahead and enable them"
3. The workflow will run on the schedule or can be triggered manually

## Caching Mechanism

### How It Works

1. **Cache Location:** `.cache/` directory (gitignored)
2. **Cache Format:** Parquet files named `{package}_{days}day_{YYYY-MM-DD}.parquet`
3. **Daily Refresh:**
   - First run each day queries BigQuery and caches results
   - Subsequent runs use cached data
   - Old cache files removed AFTER successful new fetch
4. **Fallback:** If BigQuery query fails, uses previous day's cache
5. **Data Date Tracking:** README is updated with the date of the cached data

### Benefits

- **Cost Savings:** Only 1 BigQuery query per day per configuration
- **Faster Execution:** Cached runs complete in seconds
- **Reliability:** Falls back to previous cache if new fetch fails
- **Consistent Data:** Same data used for all reports generated on the same day

## Customization

### Change Package Name

Edit `.github/workflows/update-analytics.yml`:

```yaml
env:
  DEFAULT_PACKAGE: 'your-package-name'
```

### Change Schedule

Edit the cron expression in `.github/workflows/update-analytics.yml`:

```yaml
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
    # Examples:
    # - cron: '0 */6 * * *'  # Every 6 hours
    # - cron: '0 0 * * 0'    # Weekly on Sunday
    # - cron: '0 0 1 * *'    # Monthly on 1st
```

### Change Analysis Periods

Edit `.github/workflows/update-analytics.yml`:

```yaml
env:
  DEFAULT_DAYS_30: 30  # Change to 7, 14, 30, etc.
  DEFAULT_DAYS_90: 90  # Change to 60, 90, 180, etc.
```

## Manual Workflow Trigger

You can manually trigger the workflow with custom parameters:

1. Go to **Actions** tab
2. Select "Update PyPI Analytics"
3. Click "Run workflow"
4. Optional: Override package name and/or days to analyze
5. Click "Run workflow"

## Troubleshooting

### Authentication Errors

Common issues:
- **Invalid JSON key format** - Ensure the entire JSON content is copied correctly
- **Missing permissions** - Verify service account has BigQuery Data Viewer and Job User roles
- **Expired key** - Service account keys don't expire by default, but can be disabled
- **Wrong project ID** - Ensure GCP_PROJECT_ID matches the project in the JSON key

### BigQuery Quota Errors

If you hit BigQuery quotas:
- Reduce query frequency (change cron schedule)
- Use caching (enabled by default)
- Check your GCP project quotas

### GitHub Actions Failures

1. Check Actions tab for error logs
2. Verify secrets are set correctly:
   - `GCP_SERVICE_ACCOUNT_KEY` - Complete JSON key content
   - `GCP_PROJECT_ID` - Project ID
3. Ensure service account has required permissions:
   - `roles/bigquery.dataViewer`
   - `roles/bigquery.jobUser`
4. Check if BigQuery API is enabled
5. Verify the JSON key is valid and not disabled

### PNG Export Failures

If PNG generation fails (kaleido issues):
- HTML files will still be generated
- This is a known issue with kaleido in some environments
- Charts are still viewable in HTML format

### Cache Issues

If cache seems stale:
- Check `.cache/` directory exists and is writable
- Verify cache files have today's date in filename
- Old cache is only removed AFTER successful new fetch
- Manual trigger with `--no-cache` flag not available in GitHub Actions (always uses cache)

## Security Best Practices

### Service Account Key Security

- ⚠️ **Protect JSON Keys:** Never commit keys to version control
- ✅ **Use GitHub Secrets:** Store keys securely in GitHub repository secrets
- ✅ **Minimal Permissions:** Only grant BigQuery Data Viewer and Job User roles
- ✅ **Key Rotation:** Rotate service account keys periodically (every 90 days recommended)
- ✅ **Monitor Usage:** Check Cloud Audit Logs regularly
- ✅ **Delete Unused Keys:** Remove old keys after rotation

### Key Rotation Process

```bash
# Create new key
gcloud iam service-accounts keys create new-key.json \
  --iam-account=pypi-analytics@YOUR-PROJECT-ID.iam.gserviceaccount.com

# Update GitHub secret with new key content

# List existing keys
gcloud iam service-accounts keys list \
  --iam-account=pypi-analytics@YOUR-PROJECT-ID.iam.gserviceaccount.com

# Delete old key (after verifying new one works)
gcloud iam service-accounts keys delete KEY-ID \
  --iam-account=pypi-analytics@YOUR-PROJECT-ID.iam.gserviceaccount.com
```

### Additional Security

1. **Minimal Permissions:** Only grant required BigQuery roles
2. **Monitor Usage:** Check Cloud Audit Logs regularly
3. **Review Access:** Periodically review service account permissions
4. **Restrict Key Usage:** Consider using key restrictions if available

## Cost Estimation

### BigQuery Costs

- **Public Dataset:** Free to query (no storage costs)
- **Query Processing:** First 1 TB/month free, then $5/TB
- **Typical Query:** ~100-500 MB per package per period
- **Daily Cost:** Essentially free for most use cases (well within free tier)

### GitHub Actions

- **Public Repos:** Free unlimited minutes
- **Private Repos:** 2,000 minutes/month free, then $0.008/minute
- **Typical Run:** 2-5 minutes per execution
- **Daily Cost:** Free for public repos, ~$0.01-0.04/day for private repos

## Monitoring

### Check Workflow Status

1. Go to **Actions** tab
2. View recent workflow runs
3. Click on a run to see detailed logs
4. Check for errors or warnings

### Verify Reports

After workflow runs:
1. Check `reports/` directory for new files
2. Verify README.md "Report Date" is updated
3. View generated charts (HTML files work in any browser)
4. Check text reports for data completeness

## Support

For issues or questions:
1. Check existing GitHub Issues
2. Review BigQuery documentation
3. Review Workload Identity Federation docs
4. Open a new issue with:
   - Error messages from Actions logs
   - Steps to reproduce
   - Expected vs actual behavior

## References

- [Service Account Keys](https://cloud.google.com/iam/docs/creating-managing-service-account-keys)
- [BigQuery Public Datasets](https://cloud.google.com/bigquery/public-data)
- [PyPI BigQuery Dataset](https://packaging.python.org/guides/analyzing-pypi-package-downloads/)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Actions Cron Syntax](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#schedule)

## License

See [LICENSE](../LICENSE) file.