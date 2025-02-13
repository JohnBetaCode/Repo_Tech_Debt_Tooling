# Configuration flags for report generation:

# Whether to perform cleanup operations during report generation
export GENERATE_REPORT_CLEANUP=true

# Toggle for analyzing user-related metrics
export PERFORM_USER_ANALYSIS=true

# Toggle for analyzing score-related metrics
export PERFORM_SCORE_ANALYSIS=true

# Toggle for analyzing quantitative-related metrics
export PERFORM_QUANTITATIVE_ANALYSIS=true

# Whether to print analysis results to logs
export PRINT_LOGS_ANALYSIS_RESULTS=false

# Toggle for analyzing priority-related metrics
export PERFORM_PRIORITY_ANALYSIS=true

# Whether to delete previous report before generating new one
export DELETE_PREVIOUS_REPORT=true

# Whether to perform label analysis
export PERFORM_LABEL_ANALYSIS=true

# Whether to flush PRs metadata
export FLUSH_PRS_METADATA=false

# Verbose mode
export VERBOSE=true

# Date range for report generation (YYYY-MM-DD format)
# This is development, save a lot of time, comment out when done
export REPORT_START_DATE="2024-12-01"
export REPORT_END_DATE="2025-02-14"
