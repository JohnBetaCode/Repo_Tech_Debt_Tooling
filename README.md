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

## Example Report

![Example Report](https://github.com/user-attachments/assets/ec353487-0125-4e3f-a71c-a12ab2785879)

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

### Authentication
Create `configs/secrets.sh` with your GitHub credentials:
```bash
export GITHUB_TOKEN="your_github_token"
export GITHUB_API_URL_ISSUES="https://api.github.com/repos/owner/repo/issues"
export GITHUB_ACCEPT="application/vnd.github.v3+json"
```

### Label Configuration
Create `configs/label_check.yaml` to define required labels for issues and PRs:

For example

```yaml
issues:
  category:
    - sys_nav2
    - sys_wireless_station
    - sys_teleop
    - sys_other
    - sys_cicd
  type:
    - type_feature
    - type_bug
    - type_enhancement
    - type_hotfix
  priority:
    - PRIORITY_LOW
    - PRIORITY_MEDIUM
    - PRIORITY_HIGH
    - PRIORITY_SATANIC
  departments:
    - by_AI
    - by_HW
    - by_IT
    - by_DATA
    - by_MTO
    - by_OPS
    - by_SD
    - by_OTHERS
prs:
  priority:
    - PRIORITY_LOW
    - PRIORITY_MEDIUM
    - PRIORITY_HIGH
    - PRIORITY_SATANIC
  category:
    - sys_nav2
    - sys_wireless_station
    - sys_teleop
    - sys_other
    - sys_cicd
  documentation:
    - doc_done
    - doc_no_req
    - doc_req
  status:
    - state_ready_to_test
    - state_testing
    - state_tech_check
    - state_qa_check
    - state_in_progress
  rejection:
    - Rejected_Checks
    - Rejected_Traceback
    - Rejected_Unforeseen
```

### Priority Scoring
Create `configs/scores.yaml` to define the scoring system:
```yaml
priority_scores:
  PRIORITY_LOW: 
    weight: 1
    color: "#FFFF00"
  PRIORITY_MEDIUM:
    weight: 2
    color: "#FFA500"
  PRIORITY_HIGH: 
    weight: 3
    color: "#F35325"
  PRIORITY_SATANIC: 
    weight: 5
    color: "#8B0000"
  UNCATEGORIZED: 
    weight: 0
    color: "#A9A9A9"
```

### Color Scale Configuration
Create `configs/color_scale_config.yaml` to define visualization color scales:
```yaml
color_scale:
  - range: [0, 20]
    color: "#90EE90"    # Light green
    name: "Healthy"
    
  - range: [20, 50]
    color: "#FFD700"    # Gold
    name: "Moderate"
    
  - range: [50, 80]
    color: "#FFA07A"    # Light salmon
    name: "High"
    
  - range: [80, 120]
    color: "#FF6B6B"    # Light red
    name: "Critical"
```

## Configuration and Script Files

This project relies on several configuration files and scripts to customize the analysis and report generation:

### Configuration Files

- **`configs/env_vars.sh`**: Contains environment variables that control various aspects of the analysis and report generation, such as toggles for different types of analysis and cleanup operations.

- **`configs/color_scale_config.yaml`**: Defines the color scales used in visualizations to represent different ranges of priority scores, helping to quickly identify areas of concern.

- **`configs/scores.yaml`**: Specifies the scoring system for issue priorities, including weights and colors for each priority level.

- **`configs/label_check.yaml`**: Lists the required labels for issues and pull requests, categorized by type, priority, and other attributes. This file is used to ensure that all items are properly labeled.

- **`configs/exclude_users.yaml`**: Specifies users to exclude from or include in the analysis.

### Script Files

- **`scripts/utils.py`**: Contains utility functions for data analysis and visualization. Key functions include:
  - Fetching and processing GitHub issues and PRs
  - Creating various visualization graphs (activity, scores, priority levels)
  - Generating PDF reports
  - Analyzing issues by user, priority, and label
  - Calculating metrics like time-to-close by priority

- **`scripts/generate_report.sh`**: A shell script that orchestrates the report generation process. It provides a menu-driven interface to select different types of reports:
  1. Generate Issues PDF reports (User reports and total report)
  2. Generate/Print PR and Issues report between dates
  3. Search PR and Issues by label
  4. Generate PRs PDF reports
  5. Check labels in PRs and Issues

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
pip install matplotlib pandas numpy fpdf requests PyYAML tabulate tqdm
```

2. Run the analysis script:

```bash
./scripts/generate_report.sh
```

## Usage

### Basic Usage

```bash
./scripts/generate_report.sh
```

The script will prompt you to select an analysis option and enter date ranges.

### Script Options

```bash
Usage: generate_report.sh [options]

Options:
  -h, --help    Show help message
  -d            Delete temporary files after execution
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
├── configs/
│ ├── env_vars.sh # Configuration flags
│ ├── dev_env_vars.sh # Development environment variables (optional)
│ ├── secrets.sh # GitHub credentials
│ ├── scores.yaml # Priority scoring configuration
│ ├── exclude_users.yaml # User exclusion list
│ ├── label_check.yaml # Required labels configuration
│ └── color_scale_config.yaml # Visualization color scales
├── scripts/
│ ├── generate_report.sh # Main execution script
│ └── utils.py # Analysis utilities
├── tmp/ # Generated files
│ ├── issues.json # Cached GitHub issues data
│ └── users/ # User-specific visualizations
├── .devcontainer/
│ ├── Dockerfile # Development container configuration
│ ├── docker-compose.yml # Docker Compose configuration
│ └── devcontainer.json # VS Code Dev Container configuration
└── README.md # Project documentation
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
  - tqdm

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