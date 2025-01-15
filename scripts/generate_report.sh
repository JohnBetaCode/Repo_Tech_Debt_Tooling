#!/bin/bash

git pull
clear

# Define the directories
directories=("tmp" "configs")

# Loop through each directory and check if it exists
for dir in "${directories[@]}"; do
  if [ ! -d "$dir" ]; then
    echo "Directory $dir does not exist. Creating..."
    mkdir "$dir"
  else
    :
    # echo "Directory $dir already exists."
  fi
done

secrets_file="configs/secrets.sh"
# Check if secrets.sh exists in the configs directory, and create it if it doesn't
if [ ! -f "$secrets_file" ]; then
  echo "File $secrets_file does not exist. Creating..."
  touch "$secrets_file"
else
  :
  # echo "File $secrets_file already exists."
fi

# Source environment variables from secrets.sh
if [ ! -f "configs/secrets.sh" ]; then
    echo "Error: configs/secrets.sh does not exist. Please create it with the required environment variables."
    exit 1
fi
source configs/secrets.sh
source configs/env_vars.sh

# Check if DELETE_PREVIOUS_REPORT is defined and true
if [[ -n "${DELETE_PREVIOUS_REPORT}" ]] && [[ "${DELETE_PREVIOUS_REPORT}" == "true" ]]; then
    echo "Deleting previous PDF reports..."
    rm -rf tmp/*.pdf
fi

# Add function to get dates
get_date_range() {
    if [[ -n "${REPORT_START_DATE}" ]] && [[ -n "${REPORT_END_DATE}" ]]; then
        start_date="${REPORT_START_DATE}"
        end_date="${REPORT_END_DATE}"
    else
        read -p "Enter start date (YYYY-MM-DD) or press enter for today: " start_date
        read -p "Enter end date (YYYY-MM-DD) or press enter for today: " end_date
        # Set default dates to today if not specified
        start_date=${start_date:-$(date +%Y-%m-%d)}
        end_date=${end_date:-$(date +%Y-%m-%d)}
    fi
    # Validate date format
    date_regex="^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
    if ! [[ $start_date =~ $date_regex ]] || ! [[ $end_date =~ $date_regex ]]; then
        echo "Error: Dates must be in YYYY-MM-DD format"
        exit 1
    fi
}

# Update menu function
show_menu() {
    echo "Please select an option:"
    echo "1. Generate PDF reports (User reports and total report)"
    echo "2. Generate/Print PR and Issues report between dates"
    echo "3. Search PR and Issues by label"
    echo "4. Analyze PR rejections for all users between two dates"
    echo "5. Check labels in PRs and Issues"
    echo "6. Exit"
    read -p "Enter your choice (1-6): " choice
}

# Update help function
show_help() {
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  -h, --help    Show this help message"
    echo "  -d            Delete temporary files after execution"
    echo
    echo "The script will prompt for additional options based on your selection."
    echo
    echo "Example: $0 -d"
    exit 1
}

# Check for delete flag and delete files if set
if [[ "$1" == "-d" ]]; then
    echo "Deleting all files in the tmp directory..."
    rm -rf tmp/*
    shift
fi

# Update help flag check
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    show_help
fi

# Show menu and handle user input
show_menu
case $choice in
    1)
        echo "Generating PDF reports..."
        get_date_range
        python3 scripts/utils.py --report-type pdf --start-date "$start_date" --end-date "$end_date"
        ;;
    2)
        echo "Generating PR and Issues report..."
        get_date_range
        python3 scripts/utils.py --report-type pr-issues --start-date "$start_date" --end-date "$end_date"
        ;;
    3)
        echo "Searching PR and Issues by label..."
        read -p "Enter label name: " label_name
        get_date_range
        python3 scripts/utils.py --report-type label-search --label "$label_name" --start-date "$start_date" --end-date "$end_date"
        ;;
    4)
        echo "Analyzing PR rejections for a users..."
        get_date_range
        python3 scripts/utils.py --report-type pr-rejections --start-date "$start_date" --end-date "$end_date"
        ;;
    5)
        echo "Checking labels in PRs and Issues..."
        get_date_range
        python3 scripts/utils.py --report-type label-check --start-date "$start_date" --end-date "$end_date"
        ;;
    6)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option. Please select 1-6."
        exit 1
        ;;
esac

# Check if GENERATE_REPORT_CLEANUP is defined and true
if [[ -n "${GENERATE_REPORT_CLEANUP}" ]] && [[ "${GENERATE_REPORT_CLEANUP}" == "true" ]]; then
    echo "Cleaning up temporary files..."
    rm -rf tmp/*.png
fi
