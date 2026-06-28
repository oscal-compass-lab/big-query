# Compliance Use Cases Analysis

This chart categorizes compliance-trestle downloads by their inferred use case based on deployment environment characteristics.

## How Categories Are Determined

Categories are inferred from OS, distribution, and CI/CD indicators:

- **C2P Pipeline (Alpine+CI)**: Alpine Linux + CI environment
  - Indicates Compliance-to-Policy automation pipelines in containers
  - Typical for cloud-native compliance workflows

- **AWS Automation (Amazon+CI)**: Amazon Linux + CI environment
  - AWS-based compliance automation
  - Often used in AWS CodePipeline or similar services

- **Gov/DoD Compliance (RHEL)**: Red Hat Enterprise Linux
  - Government and DoD environments typically use RHEL
  - Indicates compliance work in regulated sectors

- **CI Compliance (Other CI)**: Other Linux distributions + CI
  - General CI/CD compliance workflows
  - Includes GitHub Actions, GitLab CI, Jenkins, etc.

- **Development (macOS)**: macOS systems
  - Local development and testing
  - Developers working on compliance automation

- **SDK Usage (Windows)**: Windows systems
  - Windows-based SDK integration
  - Enterprise Windows environments

- **Other**: All other deployment scenarios

## Current Distribution

- **CI Compliance (Other CI)**: 61,515 downloads (67.3%)
- **Other**: 26,317 downloads (28.8%)
- **Gov/DoD Compliance (RHEL)**: 2,451 downloads (2.7%)
- **C2P Pipeline (Alpine+CI)**: 550 downloads (0.6%)
- **Development (macOS)**: 311 downloads (0.3%)
- **SDK Usage (Windows)**: 211 downloads (0.2%)
- **AWS Automation (Amazon+CI)**: 21 downloads (0.0%)

**Total**: 91,376 downloads

## Interpretation

These categories help understand how compliance-trestle is being deployed:
- High CI percentages indicate automation adoption
- RHEL usage suggests government/regulated sector adoption
- Container usage (Alpine) shows cloud-native practices
- macOS usage indicates active development community
