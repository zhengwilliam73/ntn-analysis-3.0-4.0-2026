# Last used 6/29/26

import csv
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

INPUT_FILE = "name-that-neutrino-classifications-you-decide-without-stacey.csv"


# Opening the input file for reading
input_file = open(INPUT_FILE, "r", newline="", encoding="utf-8")
reader = csv.DictReader(input_file, delimiter=",")  # Zooniverse exports are tab-separated

duration_list = []

for row in reader:

    # Parsing a JSON string into a dictionary
    metadata = json.loads(row["metadata"])

    # Pulling out start and end times from the metadata
    started_at = metadata["started_at"]
    finished_at = metadata["finished_at"]

    # Convert the text timestamps into datetime objects so we can do math on them
    start_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    end_time   = datetime.fromisoformat(finished_at.replace("Z", "+00:00"))

    # Calculating the duration in seconds
    duration_seconds = (end_time - start_time).total_seconds()
    duration_list.append(duration_seconds)

df = pd.DataFrame(duration_list, columns = ["time"])
bins = np.arange(0, 62, 2)
clipped_data = np.clip(df, 0, 60)

# Creating the histogram
fig, ax = plt.subplots(figsize=(12, 6))

ax.hist(clipped_data, bins=bins, edgecolor="black", color="steelblue")

# Labels and formatting
ax.set_xlabel('Time (seconds)', fontsize=13)
ax.set_ylabel('Number of Videos', fontsize=13)
ax.set_title('Distribution of time across all classifications', fontsize=15)

# X-axis: show ticks every 10% from 50% to 100%
ax.set_xticks(np.arange(0, 62, 2))
# ax.set_xticklabels([f'{round(x*100)}%' for x in np.arange(0.50, 1.05, 0.10)])

# Y-axis: only whole numbers
ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

ax.grid(axis='y', linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig('winning_ratio_histogram.png', dpi=150)
plt.show()

