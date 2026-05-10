# ==============================================================================
# PyPI Download Analytics via Google BigQuery
# Target OS: Fedora Linux
# Usage: make help
# ==============================================================================

PACKAGE       ?= compliance-trestle
DAYS          ?= 30
PROJECT_ID    ?= $(shell gcloud config get-value project 2>/dev/null)
VENV          := .venv.bq
PYTHON        := $(VENV)/bin/python
PIP           := $(VENV)/bin/pip
QUERY_SCRIPT        := python/query.py
QUERY_ADVANCED      := python/query_advanced.py
QUERY_USA           := python/query_usa_details.py
QUERY_DEPLOYMENT    := python/query_deployment_environments.py
VISUALIZE_DEPLOY    := python/visualize_deployment.py
MAP_DOWNLOADS       := python/map_downloads.py
MAP_FROM_REPORTS    := python/map_from_reports.py
TO_MARKDOWN         := python/to_markdown.py
CREDS_FILE          := credentials.json

.DEFAULT_GOAL := all

# ------------------------------------------------------------------------------
# Main Targets
# ------------------------------------------------------------------------------
.PHONY: all
all: fetch process
	@echo ""
	@echo "=========================================="
	@echo "✓ All data fetched and charts generated!"
	@echo "=========================================="
	@echo ""

.PHONY: fetch
fetch: check-creds venv
	@echo ""
	@echo "=========================================="
	@echo "Fetching data from BigQuery..."
	@echo "=========================================="
	@echo ""
	@$(MAKE) report-last-30
	@$(MAKE) report-last-90
	@echo ""
	@echo "✓ Data fetch complete"
	@echo ""

.PHONY: process
process: venv
	@echo ""
	@echo "=========================================="
	@echo "Processing data and generating charts..."
	@echo "=========================================="
	@echo ""
	@$(MAKE) maps
	@$(MAKE) mcp-analysis DAYS=30
	@$(MAKE) mcp-analysis DAYS=90
	@$(MAKE) viz-deploy-30
	@$(MAKE) viz-deploy-90
	@echo ""
	@echo "✓ Chart generation complete"
	@echo ""

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------
.PHONY: help
help:
	@echo ""
	@echo "  PyPI BigQuery Analytics — Makefile"
	@echo "  ==================================="
	@echo ""
	@echo "  MAIN WORKFLOW:"
	@echo "    make                       Fetch all data and generate all charts (default)"
	@echo "    make fetch                 Download data from BigQuery (30 & 90 day reports)"
	@echo "    make process               Generate all charts from downloaded data"
	@echo ""
	@echo "  SETUP (run these in order the first time):"
	@echo "    make deps                      Install system packages (gcloud SDK)"
	@echo "    make venv                      Create Python virtual environment"
	@echo "    make gcloud-login              Authenticate with Google Cloud"
	@echo "    make create-project            Create GCP project via CLI"
	@echo "    make use-trestle-project       Set trestle-pypi-<user> as active project"
	@echo "    make list-projects             List your GCP projects"
	@echo "    make set-project PROJECT=...   Set any project by ID"
	@echo "    make enable-api                Enable the BigQuery API on your project"
	@echo "    make credentials               Create a service account and download key"
	@echo ""
	@echo "  QUERIES (after setup):"
	@echo "    make query-all          Run all reports for PACKAGE (default: compliance-trestle)"
	@echo "    make reports            Generate both 30-day and 90-day reports in reports/"
	@echo "    make report-last-30     Generate: reports/YYYY.MM.DD.trestle.pypi.last-30.txt"
	@echo "    make report-last-90     Generate: reports/YYYY.MM.DD.trestle.pypi.last-90.txt"
	@echo "    make maps               Generate world maps from both reports (HTML + PNG)"
	@echo "    make map-30             Generate world map from 30-day report"
	@echo "    make map-90             Generate world map from 90-day report"
	@echo "    make countries          Downloads by country"
	@echo "    make os                 Downloads by OS / distro"
	@echo "    make versions           Downloads by package version"
	@echo "    make ci                 CI vs human installs breakdown"
	@echo "    make installer          Downloads by installer (pip, poetry, uv...)"
	@echo "    make python-ver         Downloads by Python version"
	@echo "    make trend              Daily download trend (last N days)"
	@echo ""
	@echo "  DEPLOYMENT VISUALIZATIONS:"
	@echo "    make viz-deploy         Generate all deployment environment charts"
	@echo "    make viz-deploy-30      Generate 30-day deployment charts"
	@echo "    make viz-deploy-90      Generate 90-day deployment charts"
	@echo ""
	@echo "  DEPLOYMENT ENVIRONMENT ANALYSIS:"
	@echo "    make deploy-all         Run all deployment environment analytics"
	@echo "    make deploy-summary     High-level deployment summary"
	@echo "    make deploy-cloud       Cloud provider detection (AWS, GCP, Azure)"
	@echo "    make deploy-containers  Container vs VM analysis"
	@echo "    make deploy-arch        CPU architecture distribution"
	@echo "    make deploy-enterprise  Enterprise vs cloud-native patterns"
	@echo "    make deploy-use-cases   Compliance-trestle specific use cases"
	@echo "    make deploy-geographic  Geographic distribution by platform"
	@echo "    make deploy-libc        libc analysis (container signal)"
	@echo ""
	@echo "  USA-SPECIFIC ANALYSIS:"
	@echo "    make usa-all            Run all USA-specific analytics"
	@echo "    make usa-total          USA download totals and share"
	@echo "    make usa-os             USA OS/distribution breakdown"
	@echo "    make usa-ci             USA CI vs human usage"
	@echo "    make usa-installer      USA installer preferences"
	@echo "    make usa-python         USA Python version distribution"
	@echo "    make usa-cpu            USA CPU architecture"
	@echo "    make usa-time           USA download time patterns"
	@echo "    make usa-enterprise     USA enterprise indicators"
	@echo ""
	@echo "  ADVANCED ANALYTICS:"
	@echo "    make advanced-all       Run all advanced analytics"
	@echo "    make user-agents        Analyze user agents (MCP, CI/CD, automation)"
	@echo "    make implementation     Python implementation details"
	@echo "    make patterns           Download patterns by time"
	@echo "    make endpoints          File download analysis"
	@echo "    make tls                TLS protocol usage"
	@echo "    make cpu                CPU architecture distribution"
	@echo "    make setuptools         Setuptools version distribution"
	@echo "    make unique             Unique downloader estimates"
	@echo "    make raw-sample         View raw sample records"
	@echo ""
	@echo "  MCP INFERENCE ANALYSIS:"
	@echo "    make mcp-analysis       Analyze MCP server usage patterns (charts + explanation)"
	@echo ""
	@echo "  VARIABLES (override on command line):"
	@echo "    PACKAGE=my-pkg make countries"
	@echo "    DAYS=90 make trend"
	@echo ""
	@echo "  CLEANUP:"
	@echo "    make clean         Remove venv and cached files"
	@echo ""

# ------------------------------------------------------------------------------
# 1. System dependencies (Fedora)
# ------------------------------------------------------------------------------
.PHONY: deps
deps:
	@echo ">>> Installing Google Cloud SDK (gcloud)..."
	@if ! command -v gcloud &>/dev/null; then \
		echo "[google-cloud-cli]" | sudo tee /etc/yum.repos.d/google-cloud-sdk.repo > /dev/null; \
		echo "name=Google Cloud CLI" | sudo tee -a /etc/yum.repos.d/google-cloud-sdk.repo > /dev/null; \
		echo "baseurl=https://packages.cloud.google.com/yum/repos/cloud-sdk-el9-x86_64" | sudo tee -a /etc/yum.repos.d/google-cloud-sdk.repo > /dev/null; \
		echo "enabled=1" | sudo tee -a /etc/yum.repos.d/google-cloud-sdk.repo > /dev/null; \
		echo "gpgcheck=1" | sudo tee -a /etc/yum.repos.d/google-cloud-sdk.repo > /dev/null; \
		echo "repo_gpgcheck=0" | sudo tee -a /etc/yum.repos.d/google-cloud-sdk.repo > /dev/null; \
		echo "gpgkey=https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg" | sudo tee -a /etc/yum.repos.d/google-cloud-sdk.repo > /dev/null; \
		sudo dnf install -y google-cloud-cli; \
	else \
		echo "  gcloud already installed: $$(gcloud version | head -1)"; \
	fi
	@echo ">>> Done. Run 'make venv' next."

# ------------------------------------------------------------------------------
# 2. Python virtual environment
# ------------------------------------------------------------------------------
.PHONY: venv
venv: $(VENV)/bin/activate

$(VENV)/bin/activate:
	@echo ">>> Creating Python virtual environment..."
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip --quiet
	$(PIP) install \
		google-cloud-bigquery \
		google-auth \
		pandas \
		db-dtypes \
		tabulate \
		rich \
		plotly \
		kaleido
	@echo ">>> Venv ready. Run 'make gcloud-login' next."

# ------------------------------------------------------------------------------
# 3. Google Cloud authentication
# ------------------------------------------------------------------------------
.PHONY: gcloud-login
gcloud-login:
	@echo ">>> Opening browser for Google login..."
	@echo "    (This authenticates your user account — separate from service account)"
	gcloud auth login
	gcloud auth application-default login
	@echo ">>> Logged in. Run 'make create-project' or 'make list-projects' next."

# ------------------------------------------------------------------------------
# 4. Create / select a GCP project
# ------------------------------------------------------------------------------
.PHONY: create-project
create-project:
	@echo ">>> Creating GCP project for Trestle PyPI Analytics..."
	@echo ""
	@echo "  If you see 'Callers must accept Terms of Service' error:"
	@echo "  1. Visit: https://console.cloud.google.com/projectcreate"
	@echo "  2. Accept the Terms of Service"
	@echo "  3. Close the browser tab (don't create project there)"
	@echo "  4. Run 'make create-project' again"
	@echo ""
	gcloud projects create trestle-pypi-$(USER) --name='Trestle PyPI Analytics'
	gcloud config set project trestle-pypi-$(USER)
	@echo ""
	@echo ">>> Project created: trestle-pypi-$(USER)"
	@echo ""
	@echo "  NEXT STEPS:"
	@echo "  1. Link billing account: https://console.cloud.google.com/billing"
	@echo "     (Required, but querying PyPI dataset is free up to 1 TB/month)"
	@echo "  2. Run: make enable-api"
	@echo "  3. Run: make credentials"
	@echo "  4. Run: make query-all"

.PHONY: list-projects
list-projects:
	@echo ">>> Your Google Cloud projects:"
	@gcloud projects list --format="table(projectId,name,projectNumber)" 2>/dev/null || echo "No projects found or not logged in"
	@echo ""
	@echo "  Current project: $$(gcloud config get-value project 2>/dev/null || echo 'none set')"
	@echo ""
	@echo "  To set a project as active:"
	@echo "    make set-project PROJECT=your-project-id"

.PHONY: set-project
set-project:
	@if [ -z "$(PROJECT)" ]; then \
		echo "ERROR: PROJECT variable not set"; \
		echo "Usage: make set-project PROJECT=your-project-id"; \
		echo ""; \
		echo "To find your project ID:"; \
		echo "  1. Go to: https://console.cloud.google.com/home/dashboard"; \
		echo "  2. Look at the top bar - it shows 'Project: NAME (project-id-here)'"; \
		echo "  3. Use the project-id, not the name or number"; \
		exit 1; \
	fi
	@echo ">>> Setting active project to: $(PROJECT)"
	gcloud config set project $(PROJECT)
	@echo ">>> Project set. Run 'make enable-api' next."

.PHONY: use-trestle-project
use-trestle-project:
	@echo ">>> Setting project to: trestle-pypi-$(USER)"
	gcloud config set project trestle-pypi-$(USER)
	@echo ">>> Project set. Run 'make enable-api' next."

# ------------------------------------------------------------------------------
# 5. Enable BigQuery API
# ------------------------------------------------------------------------------
.PHONY: enable-api
enable-api:
	@echo ">>> Enabling BigQuery API on project: $(PROJECT_ID)"
	gcloud services enable bigquery.googleapis.com \
		--project=$(PROJECT_ID)
	@echo ">>> API enabled. Run 'make credentials' next."

# ------------------------------------------------------------------------------
# 6. Create service account + credentials JSON
# ------------------------------------------------------------------------------
SA_NAME := pypi-analytics-sa

.PHONY: credentials
credentials:
	@if [ -z "$(PROJECT_ID)" ]; then \
		echo "ERROR: PROJECT_ID not set. Run: gcloud config set project YOUR_PROJECT_ID"; \
		exit 1; \
	fi
	@echo ">>> Creating service account '$(SA_NAME)' in project '$(PROJECT_ID)'..."
	@gcloud iam service-accounts create $(SA_NAME) \
		--display-name="PyPI Analytics" \
		--project=$(PROJECT_ID) 2>/dev/null || \
		echo "  (service account may already exist, continuing...)"
	@echo ">>> Granting BigQuery Data Viewer role..."
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:$(SA_NAME)@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/bigquery.dataViewer" \
		--quiet
	@echo ">>> Granting BigQuery Job User role..."
	gcloud projects add-iam-policy-binding $(PROJECT_ID) \
		--member="serviceAccount:$(SA_NAME)@$(PROJECT_ID).iam.gserviceaccount.com" \
		--role="roles/bigquery.jobUser" \
		--quiet
	@echo ">>> Downloading credentials to $(CREDS_FILE)..."
	gcloud iam service-accounts keys create $(CREDS_FILE) \
		--iam-account=$(SA_NAME)@$(PROJECT_ID).iam.gserviceaccount.com \
		--project=$(PROJECT_ID)
	@echo ">>> Credentials saved to $(CREDS_FILE)"
	@echo "    Keep this file private — it's already in .gitignore!"

# ------------------------------------------------------------------------------
# Ensure credentials exist before running queries
# ------------------------------------------------------------------------------
.PHONY: check-creds
check-creds:
	@if [ ! -f "$(CREDS_FILE)" ]; then \
		echo "ERROR: $(CREDS_FILE) not found."; \
		echo "  Run: make credentials"; \
		exit 1; \
	fi
	@if [ -z "$(PROJECT_ID)" ]; then \
		echo "ERROR: PROJECT_ID not set."; \
		echo "  Run: gcloud config set project YOUR_PROJECT_ID"; \
		exit 1; \
	fi

# ------------------------------------------------------------------------------
# Query targets
# ------------------------------------------------------------------------------
.PHONY: query-all
query-all: check-creds venv
	@echo ">>> Running all reports for package: $(PACKAGE)"
	$(PYTHON) $(QUERY_SCRIPT) all \
		--package $(PACKAGE) \
		--days $(DAYS) \
		--project $(PROJECT_ID) \
		--credentials $(CREDS_FILE)

.PHONY: reports
reports: report-last-30 report-last-90

.PHONY: report-last-30
report-last-30: check-creds venv
	@REPORT_DIR="reports"; \
	mkdir -p "$$REPORT_DIR"; \
	FILENAME="$$REPORT_DIR/$$(date +%Y.%m.%d).trestle.pypi.last-30.txt"; \
	echo ">>> Generating 30-day report: $$FILENAME"; \
	echo ">>> Running all reports for package: $(PACKAGE) (last 30 days)"; \
	$(PYTHON) $(QUERY_SCRIPT) all \
		--package $(PACKAGE) \
		--days 30 \
		--project $(PROJECT_ID) \
		--credentials $(CREDS_FILE) > "$$FILENAME"; \
	cat "$$FILENAME"; \
	echo ""; \
	echo ">>> Report saved to: $$FILENAME"

.PHONY: report-last-90
report-last-90: check-creds venv
	@REPORT_DIR="reports"; \
	mkdir -p "$$REPORT_DIR"; \
	FILENAME="$$REPORT_DIR/$$(date +%Y.%m.%d).trestle.pypi.last-90.txt"; \
	echo ">>> Generating 90-day report: $$FILENAME"; \
	echo ">>> Running all reports for package: $(PACKAGE) (last 90 days)"; \
	$(PYTHON) $(QUERY_SCRIPT) all \
		--package $(PACKAGE) \
		--days 90 \
		--project $(PROJECT_ID) \
		--credentials $(CREDS_FILE) > "$$FILENAME"; \
	cat "$$FILENAME"; \
	echo ""; \
	echo ">>> Report saved to: $$FILENAME"

.PHONY: countries
countries: check-creds venv
	$(PYTHON) $(QUERY_SCRIPT) countries \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: os
os: check-creds venv
	$(PYTHON) $(QUERY_SCRIPT) os \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: versions
versions: check-creds venv
	$(PYTHON) $(QUERY_SCRIPT) versions \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: ci
ci: check-creds venv
	$(PYTHON) $(QUERY_SCRIPT) ci \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: installer
installer: check-creds venv
	$(PYTHON) $(QUERY_SCRIPT) installer \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: python-ver
python-ver: check-creds venv
	$(PYTHON) $(QUERY_SCRIPT) python_version \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: trend
trend: check-creds venv
	$(PYTHON) $(QUERY_SCRIPT) trend \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

# ------------------------------------------------------------------------------
# Advanced query targets
# ------------------------------------------------------------------------------
.PHONY: advanced-all
advanced-all: check-creds venv
	@echo ">>> Running all advanced analytics for package: $(PACKAGE)"
	$(PYTHON) $(QUERY_ADVANCED) all \
		--package $(PACKAGE) \
		--days $(DAYS) \
		--project $(PROJECT_ID) \
		--credentials $(CREDS_FILE)

.PHONY: user-agents
user-agents: check-creds venv
	$(PYTHON) $(QUERY_ADVANCED) user_agents \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: implementation
implementation: check-creds venv
	$(PYTHON) $(QUERY_ADVANCED) implementation \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: patterns
patterns: check-creds venv
	$(PYTHON) $(QUERY_ADVANCED) patterns \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: endpoints
endpoints: check-creds venv
	$(PYTHON) $(QUERY_ADVANCED) endpoints \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: tls
tls: check-creds venv
	$(PYTHON) $(QUERY_ADVANCED) tls \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: cpu
cpu: check-creds venv
	$(PYTHON) $(QUERY_ADVANCED) cpu \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: setuptools
setuptools: check-creds venv
	$(PYTHON) $(QUERY_ADVANCED) setuptools \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: unique
unique: check-creds venv
	$(PYTHON) $(QUERY_ADVANCED) unique \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: raw-sample
raw-sample: check-creds venv
	$(PYTHON) $(QUERY_ADVANCED) raw_sample \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

# ------------------------------------------------------------------------------
# Map generation
# ------------------------------------------------------------------------------
.PHONY: map-30
map-30: venv
	@echo ">>> Generating world map from 30-day report"
	$(PYTHON) $(MAP_FROM_REPORTS) --days 30
	@echo ">>> Map saved to reports/"

.PHONY: map-90
map-90: venv
	@echo ">>> Generating world map from 90-day report"
	$(PYTHON) $(MAP_FROM_REPORTS) --days 90
	@echo ">>> Map saved to reports/"

.PHONY: maps
maps: map-30 map-90

# ------------------------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------------------------
.PHONY: clean
clean:
	rm -rf $(VENV) __pycache__ python/__pycache__ *.pyc .pytest_cache
	@echo ">>> Cleaned. Credentials file kept (remove manually if needed)."

# Made with Bob

# ------------------------------------------------------------------------------
# MCP Inference Analysis
# ------------------------------------------------------------------------------
.PHONY: mcp-analysis
mcp-analysis: check-creds venv
	@echo ">>> Running MCP inference analysis for package: $(PACKAGE)"
	$(PYTHON) python/mcp_inference_analysis.py \
		--package $(PACKAGE) \
		--days $(DAYS) \
		--project $(PROJECT_ID) \
		--credentials $(CREDS_FILE) \
		--output-dir reports

# ------------------------------------------------------------------------------
# Deployment Environment Analysis
# ------------------------------------------------------------------------------
DEPLOY_SCRIPT := python/query_deployment_environments.py

.PHONY: deploy-all
deploy-all: check-creds venv
	@echo ">>> Running all deployment environment analytics for package: $(PACKAGE)"
	$(PYTHON) $(DEPLOY_SCRIPT) all \
		--package $(PACKAGE) \
		--days $(DAYS) \
		--project $(PROJECT_ID) \
		--credentials $(CREDS_FILE)

.PHONY: deploy-summary
deploy-summary: check-creds venv
	$(PYTHON) $(DEPLOY_SCRIPT) summary \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: deploy-cloud
deploy-cloud: check-creds venv
	$(PYTHON) $(DEPLOY_SCRIPT) cloud \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: deploy-containers
deploy-containers: check-creds venv
	$(PYTHON) $(DEPLOY_SCRIPT) containers \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: deploy-arch
deploy-arch: check-creds venv
	$(PYTHON) $(DEPLOY_SCRIPT) arch \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: deploy-enterprise
deploy-enterprise: check-creds venv
	$(PYTHON) $(DEPLOY_SCRIPT) enterprise \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: deploy-use-cases
deploy-use-cases: check-creds venv
	$(PYTHON) $(DEPLOY_SCRIPT) use_cases \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: deploy-geographic
deploy-geographic: check-creds venv
	$(PYTHON) $(DEPLOY_SCRIPT) geographic \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: deploy-libc
deploy-libc: check-creds venv
	$(PYTHON) $(DEPLOY_SCRIPT) libc \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

# ------------------------------------------------------------------------------
# USA-Specific Analysis
# ------------------------------------------------------------------------------
.PHONY: usa-all
usa-all: check-creds venv
	@echo ">>> Running all USA-specific analytics for package: $(PACKAGE)"
	$(PYTHON) $(QUERY_USA) all \
		--package $(PACKAGE) \
		--days $(DAYS) \
		--project $(PROJECT_ID) \
		--credentials $(CREDS_FILE)

.PHONY: usa-total
usa-total: check-creds venv
	$(PYTHON) $(QUERY_USA) total \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: usa-os
usa-os: check-creds venv
	$(PYTHON) $(QUERY_USA) os \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: usa-ci
usa-ci: check-creds venv
	$(PYTHON) $(QUERY_USA) ci \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: usa-installer
usa-installer: check-creds venv
	$(PYTHON) $(QUERY_USA) installer \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: usa-python
usa-python: check-creds venv
	$(PYTHON) $(QUERY_USA) python \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: usa-cpu
usa-cpu: check-creds venv
	$(PYTHON) $(QUERY_USA) cpu \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: usa-time
usa-time: check-creds venv
	$(PYTHON) $(QUERY_USA) time \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

.PHONY: usa-enterprise
usa-enterprise: check-creds venv
	$(PYTHON) $(QUERY_USA) enterprise \
		--package $(PACKAGE) --days $(DAYS) \
		--project $(PROJECT_ID) --credentials $(CREDS_FILE)

# ------------------------------------------------------------------------------
# Deployment Visualizations
# ------------------------------------------------------------------------------
.PHONY: viz-deploy
viz-deploy: check-creds venv
	@echo ">>> Generating deployment environment charts for package: $(PACKAGE)"
	$(PYTHON) $(VISUALIZE_DEPLOY) \
		--package $(PACKAGE) \
		--days $(DAYS) \
		--project $(PROJECT_ID) \
		--credentials $(CREDS_FILE) \
		--output-dir reports

.PHONY: viz-deploy-30
viz-deploy-30: check-creds venv
	@echo ">>> Generating 30-day deployment charts"
	$(PYTHON) $(VISUALIZE_DEPLOY) \
		--package $(PACKAGE) \
		--days 30 \
		--project $(PROJECT_ID) \
		--credentials $(CREDS_FILE) \
		--output-dir reports

.PHONY: viz-deploy-90
viz-deploy-90: check-creds venv
	@echo ">>> Generating 90-day deployment charts"
	$(PYTHON) $(VISUALIZE_DEPLOY) \
		--package $(PACKAGE) \
		--days 90 \
		--project $(PROJECT_ID) \
		--credentials $(CREDS_FILE) \
		--output-dir reports
