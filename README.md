# GitHub Issues Analysis Tool

A comprehensive tool for analyzing and visualizing GitHub issues data, with a focus on technical debt tracking and team performance metrics.

## Description
This tool provides detailed analysis and visualization of GitHub issues data, enabling teams to track technical debt, monitor team performance, and generate comprehensive reports. It supports various types of analysis including issue activity, priority-based scoring, and per-user metrics.

Key use cases:
- Technical debt monitoring and management
- Sprint planning and capacity analysis
- Team performance tracking and reporting
- Issue prioritization insights
- Historical trend analysis for process improvement

## Motivation

## Example Report
![Example Report](https://github.com/user-attachments/assets/c99c43c9-fe16-4309-9f57-9f3c0ff6636a)

![Example Report](https://github.com/user-attachments/assets/e6a10325-84d5-4d89-82e1-2a63cfcf9008)

![Example Report](https://github.com/user-attachments/assets/ec353487-0125-4e3f-a71c-a12ab2785879)

![Example Report](https://github.com/user-attachments/assets/de3e2b49-b514-4fea-af23-2efc59fd28c9)

## Features

### Core Analysis
- **Issue Activity Tracking**
  - Weekly created/closed/open issues visualization
  - Historical trend analysis
  - Dual-axis graphs showing both weekly and monthly data

### Priority-Based Analysis
- **Scoring System**
  - PRIORITY_LOW: 1 point
  - PRIORITY_MEDIUM: 2 points
  - PRIORITY_HIGH: 3 points
  - PRIORITY_SATANIC: 5 points
  - UNCATEGORIZED: 0 points

### Visualization Types
- **Activity Graphs**
  - Overall issue activity trends
  - Priority-level distribution with dual-axis (weeks/months)
  - Per-user activity metrics
- **Score Analysis**
  - Technical debt score tracking
  - Priority-based issue distribution
  - User performance metrics

### Report Generation
- Multiple PDF reports:
  - Main report with overall metrics
  - Separate user-specific report
- Configurable date ranges
- Multiple visualization types
- Automatic cleanup options

### Additional Analysis Types
- **Sprint Analysis**
  - Sprint velocity tracking
  - Completion rate metrics
  - Story point distribution
- **Team Metrics**
  - Response time analysis
  - Resolution time tracking
  - Workload distribution
- **Label Analysis**
  - Custom label tracking
  - Label correlation insights
  - Category-based grouping
  - Rejection label analysis for PRs

## Configuration

### Environment Variables
Create `configs/env_vars.sh` with desired settings:
```bash
# Analysis toggles
export PERFORM_USER_ANALYSIS=true
export PERFORM_SCORE_ANALYSIS=true
export PERFORM_QUANTITATIVE_ANALYSIS=true
export PERFORM_PRIORITY_ANALYSIS=true
export PERFORM_LABEL_ANALYSIS=true

# Report generation settings
export GENERATE_REPORT_CLEANUP=true
export DELETE_PREVIOUS_REPORT=true
export PRINT_LOGS_ANALYSIS_RESULTS=false
export FLUSH_PRS_METADATA=false
export VERBOSE=true

# Date range for report generation (YYYY-MM-DD format)
# This is development, save a lot of time, comment out when done
export REPORT_START_DATE="2024-12-01"
export REPORT_END_DATE="2025-02-14"
```

### User Exclusions
Create `configs/exclude_users.yaml` to specify users to exclude from analysis:
```yaml
excluded_users:
  - user1
  - user2
```

Alternatively, you can specify users to include in the analysis by adding them to the `included_users` list:
```yaml
included_users:
  - user1
  - user2
```

### Authentication
Create `configs/secrets.sh` with your GitHub credentials or ask to your manager for it:
```bash
export GITHUB_TOKEN="your_github_token"
export GITHUB_API_URL_ISSUES="https://api.github.com/repos/owner/repo/issues"
export GITHUB_ACCEPT="application/vnd.github.v3+json"
```

### Additional Configuration
Create `configs/analysis_config.yaml` for custom analysis settings:
```yaml
sprint:
  length_weeks: 2
  start_day: "Monday"
  
labels:
  technical_debt: ["tech-debt", "refactor"]
  bugs: ["bug", "defect"]
  features: ["feature", "enhancement"]

metrics:
  response_time_threshold: 48  # hours
  resolution_time_target: 168  # hours
```

## Configuration and Script Files

This project relies on several configuration files and scripts to customize the analysis and report generation. Below is a brief overview of each:

### Configuration Files

- **`configs/env_vars.sh`**: Contains environment variables that control various aspects of the analysis and report generation, such as toggles for different types of analysis and cleanup operations.

- **`configs/color_scale_config.yaml`**: Defines the color scales used in visualizations to represent different ranges of priority scores, helping to quickly identify areas of concern.

- **`configs/scores.yaml`**: Specifies the scoring system for issue priorities, including weights and colors for each priority level.

- **`configs/label_check.yaml`**: Lists the required labels for issues and pull requests, categorized by type, priority, and other attributes. This file is used to ensure that all items are properly labeled.

### Script Files

- **`scripts/utils.py`**: Contains utility functions for data analysis and visualization. Key functions include creating graphs for issue scores, user distribution, and label analysis. It also handles data loading and filtering based on the provided configurations.

- **`scripts/generate_report.sh`**: A shell script that orchestrates the report generation process. It provides a menu-driven interface to select different types of reports and handles the setup of necessary directories and environment variables.

### Usage

To customize the analysis, modify the configuration files as needed. For example, adjust the `env_vars.sh` to enable or disable specific analyses, or update `scores.yaml` to change the priority scoring system.

Run the `generate_report.sh` script to generate reports based on the selected options. The script will use the configurations to determine the scope and details of the analysis.

```shell
./scripts/generate_report.sh
```

This command will prompt you to select the type of report you wish to generate and guide you through the process.

## Installation

### Using Dev Container (recommended)

1. Open the project in VS Code
2. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
3. Type "Dev Containers: Reopen in Container" and select it
4. Wait for the container to build and start
5. Run the analysis:

```bash
./scripts/generate_report.sh
```

### Using Docker
1. Build the container:

```bash
docker build -f .devcontainer/Dockerfile -t github-issues-analysis .
```

2. Run the analysis:

```bash
docker run -v $(pwd):/workspace github-issues-analysis ./scripts/generate_report.sh
```

### Manual Installation

1. Install Python dependencies:
```bash
pip install matplotlib pandas numpy fpdf requests PyYAML tabulate
```

2. Run the analysis script:

```bash
./scripts/generate_report.sh [start_week] [end_week]
```

## Usage

### Basic Usage

```bash
./scripts/generate_report.sh 1 52  # Analyze entire year
```

### Script Options

```bash
Usage: generate_report.sh [options] [start_week] [end_week]

Options:
  -h, --help    Show help message
  -d            Delete temporary files after execution

Arguments:
  start_week    Week number (1-52), default: 1
  end_week      Week number (1-52), default: current week
```

## Output Files

### Generated Reports
- `issues_activity.png`: Overall issue activity visualization
- `issues_score.png`: Priority-based score tracking
- `issues_priority_levels.png`: Priority level distribution with dual-axis
- User-specific files in `tmp/users/{username}/`:
  - `{username}_activity.png`: Per-user activity graphs
  - `{username}_score.png`: Per-user score tracking
- PDF Reports:
  - Main report with overall metrics
  - User-specific report containing all user graphs

### Data Files
- `tmp/issues.json`: Cached GitHub issues data
- Generated visualizations in `tmp/` directory
- User-specific visualizations in `tmp/users/{username}/` directories

## Project Structure
```
.
├── configs/
│   ├── env_vars.sh          # Configuration flags
│   ├── secrets.sh           # GitHub credentials
│   ├── scores.yaml          # Priority scoring configuration
│   ├── exclude_users.yaml   # User exclusion list
│   ├── analysis_config.yaml # Custom analysis settings
│   └── color_scale_config.yaml # Visualization color scales
├── scripts/
│   ├── generate_report.sh   # Main execution script
│   └── utils.py             # Analysis utilities
├── tmp/                     # Generated files
│   ├── issues.json          # Cached GitHub issues data
│   └── users/               # User-specific visualizations
├── .devcontainer/
│   └── Dockerfile           # Development container configuration
└── README.md                # Project documentation
```

## Dependencies
- Python 3.x
- Required Python packages:
  - matplotlib
  - pandas
  - numpy
  - fpdf
  - requests
  - PyYAML
  - tabulate
  - Pillow (for PDF generation)

## Contributing
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Best Practices

### Data Collection
- Ensure consistent issue labeling
- Maintain regular sprint cadence
- Document priority changes
- Keep issue descriptions updated

### Analysis
- Review trends monthly
- Compare metrics across sprints
- Track technical debt accumulation
- Monitor team velocity changes

### Reporting
- Share reports in team retrospectives
- Use insights for sprint planning
- Track long-term trends
- Identify process improvements

## Troubleshooting
Common issues and solutions:
- **Rate Limiting**: Use token authentication and respect GitHub API limits
- **Missing Data**: Ensure proper issue labeling and consistent sprint management
- **Performance**: Enable caching for large repositories
- **Report Generation**: Check file permissions and disk space

