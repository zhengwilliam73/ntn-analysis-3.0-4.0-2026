# 5/24/2026, Spring Quarter 2025-2026
# Used to reduce 800 or so classifications into 50 rows of 50 videos; preperation of agreement cuts
# Last used 7/6/26

import csv
import json

# ---- SETTINGS ---- #
INPUT_FILE  = "name-that-neutrino-classifications-you-decide-timecut-6-seconds.csv"   # <-- Your filtered input file from the last script
OUTPUT_FILE = "name-that-neutrino-classifications-you-decide-timecut-6-seconds-reduced.csv"   # <-- The new summary file with one row per video
# ------------------ #

# This dictionary will hold the data we collect for each video.
# The video filename will be the key, and the value will be a dict of info about it.
videos = {}

# Open and read the filtered data file
input_file = open(INPUT_FILE, "r", newline="", encoding="utf-8")
reader = csv.DictReader(input_file, delimiter=",")

for row in reader:

    # --- Parse the metadata JSON ---
    metadata = json.loads(row["metadata"])

    # --- Parse the subject_data JSON ---
    # subject_data looks like: {"120079826": {"video": "...", "#PID": "...", ...}}
    # There is one key (the subject ID) wrapping all the fields, so we grab the inner dict
    subject_data = json.loads(row["subject_data"])
    subject_id   = list(subject_data.keys())[0]        # e.g. "120079826"
    subject_info = subject_data[subject_id]             # the inner dict with video, PID, etc.

    # --- Pull out the fields we care about ---
    video            = subject_info.get("video", "unknown")
    pid              = subject_info.get("#PID", "unknown")
    interaction_type = subject_info.get("#InteractionType", "unknown")
    event_id         = subject_info.get("#EventID", "unknown")
    run_number       = subject_info.get("#Run_Number", "unknown")
    deepcore_qtotal  = subject_info.get("#DeepCoreQTotal", "uknown")

    # --- Parse the annotations JSON to get the user's answer (Track or Cascade) ---
    annotations = json.loads(row["annotations"])
    answer = "unknown"
    for task in annotations:
        if task.get("task") == "T1":
            answer = task.get("value", "unknown")
            break

    # --- If we haven't seen this video before, set it up in our dictionary ---
    if video not in videos:
        videos[video] = {
            "video":            video,
            "subject_id":       subject_id,
            "event_id":         event_id,
            "run_number":       run_number,
            "pid":              pid,
            "interaction_type": interaction_type,
            "deepcore_qtotal":  deepcore_qtotal,
            "track_count":      0,
            "cascade_count":    0,
        }

    # --- Add this user's answer to the running tally ---
    if answer == "Track":
        videos[video]["track_count"] += 1
    elif answer == "Cascade":
        videos[video]["cascade_count"] += 1

input_file.close()

# --- Now write the summary file, one row per video ---
output_file = open(OUTPUT_FILE, "w", newline="", encoding="utf-8")

fieldnames = [
    "video",
    "subject_id",
    "event_id",
    "run_number",
    "pid",
    "deepcore_qtotal",
    "interaction_type",
    "track_count",
    "cascade_count",
    "total_classifications",
    "track_ratio",
]

writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=",")
writer.writeheader()

for video, data in videos.items():

    track_count   = data["track_count"]
    cascade_count = data["cascade_count"]
    total         = track_count + cascade_count

    # Calculate track ratio, avoiding division by zero
    if total > 0:
        track_ratio = round(track_count / total, 4)
    else:
        track_ratio = 0.0

    writer.writerow({
        "video":                 data["video"],
        "subject_id":            data["subject_id"],
        "event_id":              data["event_id"],
        "run_number":            data["run_number"],
        "pid":                   data["pid"],
        "deepcore_qtotal":       data["deepcore_qtotal"],
        "interaction_type":      data["interaction_type"],
        "track_count":           track_count,
        "cascade_count":         cascade_count,
        "total_classifications": total,
        "track_ratio":           track_ratio,
    })

output_file.close()

print(f"Done!")
print(f"Total unique videos found: {len(videos)}")
print(f"Summary saved to: {OUTPUT_FILE}")
