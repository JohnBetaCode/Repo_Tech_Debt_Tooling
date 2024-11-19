#!/bin/bash
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

# Update help function to include new -d flag
show_help() {
    echo "Usage: $0 [options] [start_week] [end_week]"
    echo
    echo "Options:"
    echo "  -h, --help    Show this help message"
    echo "  -d            Delete temporary files after execution"
    echo
    echo "Arguments:"
    echo "  start_week    Week number (1-52), default: 1"
    echo "  end_week      Week number (1-52), default: current week"
    echo
    echo "Example: $0 -d 1 52"
    exit 1
}

# Add delete flag check and shift arguments if needed
DELETE_FILES=false
if [[ "$1" == "-d" ]]; then
    DELETE_FILES=true
    shift
fi

# Update help flag check
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    show_help
fi

# You can either pass arguments directly to the script
# or use default values
START_WEEK=${1:-1}           # Default to first week of year (1) if no argument provided
END_WEEK=${2:-$(date +%V)}   # Default to current week if no argument provided

# Execute the Python script with the week parameters
python3 scripts/utils.py --start-week "$START_WEEK" --end-week "$END_WEEK"

# Check if GENERATE_REPORT_CLEANUP is defined and true
if [[ -n "${GENERATE_REPORT_CLEANUP}" ]] && [[ "${GENERATE_REPORT_CLEANUP}" == "true" ]]; then
    echo "Cleaning up temporary files..."
    rm -rf tmp/*.png
fi
