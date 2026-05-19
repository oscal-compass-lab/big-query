# How to Add Secrets to GitHub Repository

Follow these steps to add the required secrets for Google Cloud authentication.

## Step 1: Navigate to Repository Settings

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/big-query-pypi`
2. Click on **Settings** tab (top right of the repository page)
3. In the left sidebar, click on **Secrets and variables**
4. Click on **Actions**

## Step 2: Add GCP_SERVICE_ACCOUNT_KEY Secret

1. Click the **New repository secret** button
2. In the **Name** field, enter exactly: `GCP_SERVICE_ACCOUNT_KEY`
3. In the **Secret** field:
   - Open your JSON key file in a text editor
   - Copy the **ENTIRE** contents (including the opening `{` and closing `}`)
   - Paste it into the Secret field
   
   The content should look like this:
   ```json
   {
     "type": "service_account",
     "project_id": "your-project-id",
     "private_key_id": "abc123...",
     "private_key": "-----BEGIN PRIVATE KEY-----\nMIIE...\n-----END PRIVATE KEY-----\n",
     "client_email": "service-account@project.iam.gserviceaccount.com",
     "client_id": "123456789",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
   }
   ```

4. Click **Add secret**

## Step 3: Add GCP_PROJECT_ID Secret

1. Click the **New repository secret** button again
2. In the **Name** field, enter exactly: `GCP_PROJECT_ID`
3. In the **Secret** field:
   - Enter your Google Cloud project ID (found in the JSON key as `project_id`)
   - Example: `my-project-12345`
4. Click **Add secret**

## Step 4: Verify Secrets

After adding both secrets, you should see them listed:
- ✅ `GCP_SERVICE_ACCOUNT_KEY`
- ✅ `GCP_PROJECT_ID`

**Note:** You won't be able to view the secret values after creation (GitHub hides them for security).

## Step 5: Test the Workflow

### Option A: Manual Trigger (Recommended for First Test)

1. Go to the **Actions** tab in your repository
2. Click on **Update PyPI Analytics** workflow
3. Click **Run workflow** button (on the right)
4. Leave the default values or customize:
   - Package name (optional)
   - Days to analyze (optional)
5. Click **Run workflow**
6. Watch the workflow run and check for any errors

### Option B: Wait for Scheduled Run

The workflow will automatically run daily at 6 AM UTC (2 AM ET).

## Troubleshooting

### If the workflow fails with authentication errors:

1. **Check JSON format**: Make sure you copied the entire JSON key including `{` and `}`
2. **Check for extra spaces**: Don't add any extra spaces or newlines
3. **Verify project ID**: Ensure `GCP_PROJECT_ID` matches the `project_id` in your JSON key
4. **Check service account permissions**: Ensure the service account has:
   - `roles/bigquery.dataViewer`
   - `roles/bigquery.jobUser`

### View detailed error logs:

1. Go to **Actions** tab
2. Click on the failed workflow run
3. Click on the **generate-analytics** job
4. Expand the failed step to see error details

## Security Reminders

- ✅ Secrets are encrypted by GitHub
- ✅ Secrets are not visible in logs
- ✅ Only repository collaborators with write access can add/edit secrets
- ⚠️ Delete the local JSON key file after adding to GitHub:
  ```bash
  rm path/to/your-key.json
  ```
- 🔄 Rotate keys every 90 days for best security practices

## Quick Command Reference

If you need to get your project ID from the command line:
```bash
# View your JSON key file
cat path/to/your-key.json

# Extract just the project ID
cat path/to/your-key.json | grep project_id
```

## Next Steps

After adding secrets:
1. ✅ Trigger a manual workflow run to test
2. ✅ Check the Actions tab for results
3. ✅ Verify reports are generated in the `reports/` directory
4. ✅ Delete your local JSON key file for security

---

Need help? Check the [SETUP.md](SETUP.md) for more details or open an issue.