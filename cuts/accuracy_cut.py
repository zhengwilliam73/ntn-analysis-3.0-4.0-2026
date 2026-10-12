import csv
import json

# ---- SETTINGS ---- #
INPUT_FILE       = "name-that-neutrino-classifications-you-decide-timecut-6-seconds.csv"        # <-- Change this to your original raw data file
OUTPUT_FILE      = "name-that-neutrino-classifications-you-decide-timecut-6-seconds-accuracycut-50-percent.csv" # <-- Output file with only valid users' classifications
ACCURACY_THRESHOLD = 0.50               # <-- Minimum accuracy to keep a user (60%)
MIN_CLASSIFICATIONS = 5                   # <-- Only apply the cut if user has at least this many classifications
# ------------------ #

# --- PASS 1: Read through the entire file and calculate each user's accuracy ---

# We'll track each user's correct and total classification counts
user_stats = {}  # { username: {"correct": 0, "total": 0} }

input_file = open(INPUT_FILE, "r", newline="", encoding="utf-8")
reader = csv.DictReader(input_file, delimiter=",")

for row in reader:

    username = row["user_name"]

    # Parse subject_data to get the ground truth (InteractionType)
    subject_data = json.loads(row["subject_data"])
    subject_id   = list(subject_data.keys())[0]
    subject_info = subject_data[subject_id]
    interaction_type = subject_info.get("#InteractionType", "unknown")

    # Convert InteractionType to the label we expect
    # 1 = Track, 2 = Cascade
    if interaction_type == "1":
        true_answer = "Track"
    elif interaction_type == "2":
        true_answer = "Cascade"
    else:
        true_answer = "unknown"

    # Parse annotations to get what the user answered
    annotations = json.loads(row["annotations"])
    user_answer = "unknown"
    for task in annotations:
        if task.get("task") == "T1":
            user_answer = task.get("value", "unknown")
            break

    # Set up this user in the dictionary if we haven't seen them before
    if username not in user_stats:
        user_stats[username] = {"correct": 0, "total": 0}

    # Tally up their result
    user_stats[username]["total"] += 1
    if user_answer == true_answer:
        user_stats[username]["correct"] += 1

input_file.close()

# --- Decide which users are valid ---
# A user is invalid only if they have >= MIN_CLASSIFICATIONS and accuracy < ACCURACY_THRESHOLD

valid_users   = []
invalid_users = []

for username, stats in user_stats.items():
    total   = stats["total"]
    correct = stats["correct"]
    accuracy = correct / total if total > 0 else 0

    if total >= MIN_CLASSIFICATIONS and accuracy < ACCURACY_THRESHOLD:
        invalid_users.append(username)
    else:
        valid_users.append(username)

# Print a summary of who passed and who didn't
print(f"Total unique users: {len(user_stats)}")
print(f"Users kept:   {len(valid_users)}")
print(f"Users removed: {len(invalid_users)}")
print()

if invalid_users:
    print("Removed users and their accuracy:")
    for username in invalid_users:
        stats    = user_stats[username]
        total    = stats["total"]
        correct  = stats["correct"]
        accuracy = round(correct / total, 4)
        print(f"  {username}: {correct}/{total} correct ({accuracy*100:.1f}%)")
else:
    print("No users were removed.")
print()

# --- PASS 2: Read through the file again and write only valid users' rows ---

input_file  = open(INPUT_FILE, "r", newline="", encoding="utf-8")
reader      = csv.DictReader(input_file, delimiter=",")

output_file = open(OUTPUT_FILE, "w", newline="", encoding="utf-8")
writer      = csv.DictWriter(output_file, fieldnames=reader.fieldnames, delimiter=",")
writer.writeheader()

rows_written = 0
rows_skipped = 0

for row in reader:
    if row["user_name"] in valid_users:
        writer.writerow(row)
        rows_written += 1
    else:
        rows_skipped += 1

input_file.close()
output_file.close()

print(f"Rows written to output: {rows_written}")
print(f"Rows skipped: {rows_skipped}")
print(f"Output saved to: {OUTPUT_FILE}")
