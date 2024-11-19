# Repo Tech Debt Tooling

A tool for analyzing and visualizing technical debt based on GitHub issues.

## Description
This tool enables the analysis and generation of reports on a project's technical debt, using GitHub issues as the data source. The system classifies and scores issues according to their priority, allowing temporal tracking of technical debt evolution.

## Features
- Automatic issue retrieval from GitHub API
- Weekly period analysis
- Priority-based scoring system:
  - PRIORITY_LOW: 1 point
  - PRIORITY_MEDIUM: 2 points
  - PRIORITY_HIGH: 3 points
  - PRIORITY_CRITICAL: 5 points
- Generation of key metric reports including:
  - Issues activity visualization (created/closed/open)
  - Priority-based score tracking
  - Per-user activity analysis
  - Weekly PDF reports with all visualizations
  - Issue age tracking and analysis
  - Label-based categorization
- User-specific analysis and tracking
- Configurable user exclusions
- Export capabilities to CSV and JSON formats

## Project Structure
- `scripts/`
  - `generate_report.sh`: Main script for generating reports
  - `utils.py`: Utility functions for data processing and visualization
- `configs/`
  - `secrets.sh`: Configuration file for credentials
  - `exclude_users.yaml`: List of users to exclude from analysis
- `tmp/`: Directory for temporary data storage and generated reports

## Dependencies
- Python 3.8 or higher
- Python Libraries:
  - requests>=2.25.0
  - matplotlib>=3.3.0
  - pandas>=1.2.0
  - numpy>=1.19.0
  - fpdf>=1.7.2
  - PyYAML>=5.4.0
  - Pillow>=8.0.0
- Docker (optional for containerized execution)
- GitHub API access (token required)

## Setup
1. Create `configs/secrets.sh` file with the following variables:
   ```bash
   export GITHUB_API_URL_ISSUES="https://api.github.com/repos/owner/repo/issues"
   export GITHUB_ACCEPT="application/vnd.github.v3+json"
   export GITHUB_TOKEN="your_github_token"
   ```

2. (Optional) Configure user exclusions in `configs/exclude_users.yaml`

3. Run using Docker:
   ```bash
   docker build -t tech-debt-tool .
   docker run -v $(pwd):/workspace tech-debt-tool
   ```
   Or run directly with Python:
   ```bash
   source configs/secrets.sh
   python3 scripts/utils.py --start-week 1 --end-week 52
   ```

## Output
The tool generates:
- `issues_activity.png`: Weekly visualization of issue creation/closure
- `issues_score.png`: Weekly visualization of technical debt score
- Per-user activity and score graphs (if PERFORM_USER_ANALYSIS=true)
- Consolidated PDF report containing all visualizations

## Troubleshooting
Common issues and solutions:
- Rate limiting: If you hit GitHub API rate limits, ensure your token has appropriate permissions
- Memory issues: For large repositories, increase Docker container memory limits
- Missing data: Verify GitHub token permissions include issue access
