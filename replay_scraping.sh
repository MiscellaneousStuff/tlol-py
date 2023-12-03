#!/bin/bash

# Set the parameters
champs="Ezreal"
max_workers=10
target_patch="13_23"

# Loop from page 41 to 1000 in increments of 10
for ((start_page=61; start_page<=1000; start_page+=10)); do
    end_page=$((start_page+9))  # Calculate the end page

    # Run the replay_downloader command
    python -m tlol.bin.replay_downloader \
        --champs "$champs" \
        --max_workers "$max_workers" \
        --target_patch "$target_patch" \
        --start_page "$start_page" \
        --last_page "$end_page"

    # Optional: Add a delay between iterations to avoid overloading the server
    sleep 5  # You can adjust the sleep duration as needed
done