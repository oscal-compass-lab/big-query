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

- **CI Compliance (Other CI)**: 60,078 downloads (69.9%)
- **Other**: 21,329 downloads (24.8%)
- **Gov/DoD Compliance (RHEL)**: 3,337 downloads (3.9%)
- **SDK Usage (Windows)**: 741 downloads (0.9%)
- **Development (macOS)**: 438 downloads (0.5%)
- **C2P Pipeline (Alpine+CI)**: 31 downloads (0.0%)
- **AWS Automation (Amazon+CI)**: 7 downloads (0.0%)

**Total**: 85,961 downloads

## Interpretation

These categories help understand how compliance-trestle is being deployed:
- High CI percentages indicate automation adoption
- RHEL usage suggests government/regulated sector adoption
- Container usage (Alpine) shows cloud-native practices
- macOS usage indicates active development community
