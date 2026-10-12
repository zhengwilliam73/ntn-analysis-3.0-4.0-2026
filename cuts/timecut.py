# 5/24/2026, Spring Quarter 2025-2026
# Used to effectively ignore any classifications under 6 seconds
# Last used 7/6/26

import csv
import json
from datetime import datetime

# ---- SETTINGS ---- #
MIN_SECONDS = 6
INPUT_FILE = "name-that-neutrino-classifications-you-decide.csv"       # <-- Change this to your input CSV filename
OUTPUT_FILE = f"name-that-neutrino-classifications-you-decide-timecut-{MIN_SECONDS}-seconds.csv"  # <-- This is the name of the output CSV file
# ------------------ #

# We'll use this to count how many rows were removed
rows_removed = 0

# Open the input file for reading
input_file = open(INPUT_FILE, "r", newline="", encoding="utf-8")
reader = csv.DictReader(input_file, delimiter=",")  # Zooniverse exports are tab-separated

# Open the output file for writing
output_file = open(OUTPUT_FILE, "w", newline="", encoding="utf-8")
writer = csv.DictWriter(output_file, fieldnames=reader.fieldnames, delimiter=",")

# Write the header row (column names) to the output file
writer.writeheader()

# Go through every row in the input file, one at a time
for row in reader:

    # The metadata column contains a JSON string — parse it into a dictionary
    metadata = json.loads(row["metadata"])

    # Pull out the start and end times from the metadata
    started_at  = metadata["started_at"]
    finished_at = metadata["finished_at"]

    # Convert the text timestamps into datetime objects so we can do math on them
    start_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    end_time   = datetime.fromisoformat(finished_at.replace("Z", "+00:00"))

    # Calculate the duration in seconds
    duration_seconds = (end_time - start_time).total_seconds()

    # Check the duration
    if duration_seconds >= MIN_SECONDS:
        # Duration is long enough — keep this row by writing it to the output file
        writer.writerow(row)
    else:
        # Duration is too short — skip this row and count it as removed
        rows_removed += 1

# Close both files when done
input_file.close()
output_file.close()

# Print a summary
print(f"Done!")
print(f"Rows removed (duration < {MIN_SECONDS} seconds): {rows_removed}")
print(f"Filtered data saved to: {OUTPUT_FILE}")
