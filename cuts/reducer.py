# 10/30/2026
# 4.0 version, the following detail the differences:
# 1.) 4.0 uses task "T0" for the Track/Cascade question (3.0 used "T1")
# 2.) 4.0 subject metadata keys are filename, Event_ID, Run, File_number, #InteractionType, #group
# 3.) Videos are grouped by subject_id instead of the video filename. Event 4083 has the same filename
#     in two subject sets (track_clumped and track_smallspan) and should stay as two videos
# 4.) FIRST_CLASSIFICATION_ONLY: only each user's first classification of each video is counted
#     (some users classified the same video many times)
# 5.) RETIRED_ONLY: only videos that are retired are kept
# 6.) The group and file number are kept so the PID can be added with merger_4_0.py

import csv
import json

csv.field_size_limit(10**9)

# ---- SETTINGS ---- #
INPUT_FILE  = "4-0-level-4-classifications-timecut-6-seconds.csv"   # <-- Your filtered input file from the last script (use the raw export for no time cut)
OUTPUT_FILE = "4-0-level-4-classifications-timecut-6-seconds-reduced.csv"   # <-- The new summary file with one row per video
FIRST_CLASSIFICATION_ONLY = True   # <-- True: only each user's first classification of a video counts. False: every classification counts
RETIRED_ONLY = True                # <-- True: only keep videos that are retired
# ------------------ #

# This dictionary will hold the data we collect for each video.
# The subject ID will be the key, and the value will be a dict of info about it.
videos = {}

# Keeps track of which (user, video) pairs we already counted, for FIRST_CLASSIFICATION_ONLY
seen_user_video = set()
repeats_skipped = 0
not_retired_skipped = 0

# Open and read the filtered data file
input_file = open(INPUT_FILE, "r", newline="", encoding="utf-8")
reader = csv.DictReader(input_file, delimiter=",")

# Sort by time so that "first classification" really is the earliest one
rows = sorted(reader, key=lambda row: (row["created_at"], int(row["classification_id"])))

for row in rows:

    # --- Parse the metadata JSON ---
    metadata = json.loads(row["metadata"])

    # --- Parse the subject_data JSON ---
    # subject_data looks like: {"125999504": {"filename": "...", "#InteractionType": "...", ...}}
    # There is one key (the subject ID) wrapping all the fields, so we grab the inner dict
    subject_data = json.loads(row["subject_data"])
    subject_id   = list(subject_data.keys())[0]        # e.g. "125999504"
    subject_info = subject_data[subject_id]             # the inner dict with filename, InteractionType, etc.

    # --- Skip videos that are not retired ---
    # "retired" is empty if the video is not retired
    if RETIRED_ONLY and not subject_info.get("retired"):
        not_retired_skipped += 1
        continue

    # --- Only keep the first classification of each video by each user ---
    # Users who are not logged in have no user_id, so their user_name is used instead
    if FIRST_CLASSIFICATION_ONLY:
        user = row["user_id"] if row["user_id"] else row["user_name"]
        if (user, subject_id) in seen_user_video:
            repeats_skipped += 1
            continue
        seen_user_video.add((user, subject_id))

    # --- Pull out the fields we care about ---
    video            = subject_info.get("filename", "unknown")
    interaction_type = subject_info.get("#InteractionType", "unknown")
    event_id         = subject_info.get("Event_ID", "unknown")
    run_number       = subject_info.get("Run", "unknown")
    file_number      = subject_info.get("File_number", "unknown")
    group            = subject_info.get("#group", "unknown")

    # --- Parse the annotations JSON to get the user's answer (Track or Cascade) ---
    annotations = json.loads(row["annotations"])
    answer = "unknown"
    for task in annotations:
        if task.get("task") == "T0":
            answer = task.get("value", "unknown")
            break

    # --- If we haven't seen this video before, set it up in our dictionary ---
    if subject_id not in videos:
        videos[subject_id] = {
            "video":            video,
            "subject_id":       subject_id,
            "event_id":         event_id,
            "run_number":       run_number,
            "file_number":      file_number,
            "group":            group,
            "interaction_type": interaction_type,
            "track_count":      0,
            "cascade_count":    0,
        }

    # --- Add this user's answer to the running tally ---
    if answer == "Track":
        videos[subject_id]["track_count"] += 1
    elif answer == "Cascade":
        videos[subject_id]["cascade_count"] += 1

input_file.close()

# --- Now write the summary file, one row per video ---
output_file = open(OUTPUT_FILE, "w", newline="", encoding="utf-8")

fieldnames = [
    "video",
    "subject_id",
    "event_id",
    "run_number",
    "file_number",
    "group",
    "interaction_type",
    "track_count",
    "cascade_count",
    "total_classifications",
    "track_ratio",
]

writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter=",")
writer.writeheader()

for subject_id, data in videos.items():

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
        "file_number":           data["file_number"],
        "group":                 data["group"],
        "interaction_type":      data["interaction_type"],
        "track_count":           track_count,
        "cascade_count":         cascade_count,
        "total_classifications": total,
        "track_ratio":           track_ratio,
    })

output_file.close()

print(f"Done!")
print(f"Total unique videos found: {len(videos)}")
if RETIRED_ONLY:
    print(f"Classifications skipped (video not retired): {not_retired_skipped}")
if FIRST_CLASSIFICATION_ONLY:
    print(f"Repeat classifications skipped (same user, same video): {repeats_skipped}")
print(f"Summary saved to: {OUTPUT_FILE}")
