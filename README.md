# GitHub Issues Analysis Tool

A comprehensive tool for analyzing and visualizing GitHub issues data, with a focus on technical debt tracking and team performance metrics.

## Description
This tool provides detailed analysis and visualization of GitHub issues data, enabling teams to track technical debt, monitor team performance, and generate comprehensive reports. It supports various types of analysis including issue activity, priority-based scoring, and per-user metrics.

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

## Configuration

### Environment Variables
Create `configs/env_vars.sh` with desired settings:
```bash
# Analysis toggles
export PERFORM_USER_ANALYSIS=true
export PERFORM_SCORE_ANALYSIS=true
export PERFORM_QUANTITATIVE_ANALYSIS=true
export PERFORM_PRIORITY_ANALYSIS=true

# Report generation settings
export GENERATE_REPORT_CLEANUP=true
export DELETE_PREVIOUS_REPORT=false
export PRINT_LOGS_ANALYSIS_RESULTS=false
```

### User Exclusions
Create `configs/exclude_users.yaml` to specify users to exclude from analysis:
```yaml
excluded_users:
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

## Installation

### Using Dev Container
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
│   ├── env_vars.sh    # Configuration flags
│   ├── secrets.sh     # GitHub credentials
│   └── scores.yaml    # Priority scoring configuration
├── scripts/
│   ├── generate_report.sh  # Main execution script
│   └── utils.py           # Analysis utilities
├── tmp/                   # Generated files
└── .devcontainer/
    └── Dockerfile        # Development container configuration
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

## License
[Add your license information here]
