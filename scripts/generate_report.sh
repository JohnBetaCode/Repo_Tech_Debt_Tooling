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
source configs/secrets.sh

# You can either pass arguments directly to the script
# or use default values
START_WEEK=${1:-$(date +%V)}  # Default to current week if no argument provided
END_WEEK=${2:-$(date +%V)}    # Default to current week if no argument provided

# Execute the Python script with the week parameters
python3 scripts/utils.py --start-week "$START_WEEK" --end-week