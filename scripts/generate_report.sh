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

# Run the Python script
python3 scripts/utils.py