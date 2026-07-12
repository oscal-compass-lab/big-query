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

- **CI Compliance (Other CI)**: 206,548 downloads (70.5%)
- **Other**: 74,270 downloads (25.3%)
- **Gov/DoD Compliance (RHEL)**: 9,214 downloads (3.1%)
- **SDK Usage (Windows)**: 1,309 downloads (0.4%)
- **Development (macOS)**: 1,141 downloads (0.4%)
- **C2P Pipeline (Alpine+CI)**: 665 downloads (0.2%)
- **AWS Automation (Amazon+CI)**: 28 downloads (0.0%)

**Total**: 293,175 downloads

## Interpretation

These categories help understand how compliance-trestle is being deployed:
- High CI percentages indicate automation adoption
- RHEL usage suggests government/regulated sector adoption
- Container usage (Alpine) shows cloud-native practices
- macOS usage indicates active development community
