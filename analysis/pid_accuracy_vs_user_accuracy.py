import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load data
df = pd.read_csv("low_energy_quiz_gcd_features.csv")

# ==============================================================================
# NEW (optional) STEP: Filter by Subject IDs
# ==============================================================================
# 1. Paste your list of Subject IDs here (as integers or strings, depending on your CSV)
# my_subject_ids = [9525, 19567, 36681, 8358, 8957, 40808, 8824, 16481, 27187, 8911, 9961, 28476, 15932]  # old data

# 2. Filter the dataframe. 
# This keeps only the rows where 'subject_id' is in your list.
# Note: Make sure the column name matches your CSV. If it's called 'subject_id' or 'id', change it here.
# df = df[df['event_id'].isin(my_subject_ids)]

# 3. Print to confirm it worked
print(f"Filtered dataset now contains {len(df)} video entries.")

# If the filtered dataset is empty, check your column name or the IDs you pasted!
if len(df) == 0:
    print("WARNING: No videos matched your Subject IDs. Check your column name and ID list.")
# ==============================================================================


# Map truth to different numbers: 
# If InteractionType is 1, this means a track. Keep this number at 1
# If InteractionType is 2, this means a cascade. Change this number to 0 to make the math easier
df['truth_binary'] = df['interaction_type'].map({1: 1, 2: 0})

# Compute PID error: |PID - truth_binary|
df['pid_error'] = np.abs(df['pid'] - df['truth_binary'])

# # Compute user fraction correct: for a true track, fraction_correct = track_ratio
# # for a true cascade, fraction_correct = 1 - track_ratio
# df['user_fraction_correct'] = np.where(
#     df['interaction_type'] == 1,  # Track
#     df['track_ratio'],            # fraction that voted track
#     1 - df['track_ratio']         # for cascade, fraction that voted cascade
# )

# For the binary user error metric (to mirror pid_error):
# user_error = 1 - fraction_correct
df['user_error'] = 1 - df['user_fraction_correct']

# ---------- Figure 1: User Accuracy vs. PID Accuracy (scatter) ----------
fig, ax = plt.subplots(figsize=(8, 6))

# Compute PID accuracy: 1 - pid_error (so 1 = perfectly correct, 0 = perfectly wrong)
df['pid_accuracy'] = 1 - df['pid_error']

for truth_val, color, label in [(1, 'blue', 'True Track'), (2, 'darkorange', 'True Cascade')]:
    mask = df['interaction_type'] == truth_val
    ax.scatter(df.loc[mask, 'pid_accuracy'], df.loc[mask, 'user_fraction_correct'],
               c=color, label=label, alpha=0.7, edgecolors='black', linewidth=0.5, s=60)

# Add diagonal line: if user accuracy exactly equals PID accuracy
ax.plot([0, 1], [0, 1], 'k--', alpha=0.4, label='User accuracy = PID accuracy')

ax.set_xlabel('PID Accuracy (1 - |PID - Truth|)', fontsize=12)
ax.set_ylabel('User Accuracy (fraction correct)', fontsize=12)
ax.set_title('User Accuracy vs. PID Accuracy per Video', fontsize=14)
ax.legend()
ax.set_xlim(-0.05, 1.05)
ax.set_ylim(-0.05, 1.05)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
