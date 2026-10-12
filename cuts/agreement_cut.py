# 7/6/2026

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the CSV file
df = pd.read_csv("name-that-neutrino-classifications-you-decide-timecut-6-seconds-reduced.csv")

# --- Agreement Cut Parameters ---
cut_low  = 0.4
cut_high = 0.6

# --- Sort videos into two lists ---
kept_videos   = []
removed_videos = []

for i in range(len(df)):
    row = df.iloc[i]
    ratio = row['track_ratio']

    if ratio >= cut_low and ratio <= cut_high:
        removed_videos.append(row)
    else:
        kept_videos.append(row)

# --- Print removed videos ---
print("=" * 50)
print("REMOVED VIDEOS (fell within cut range):")
print("=" * 50)
if len(removed_videos) == 0:
    print("No videos were removed.")
else:
    for row in removed_videos:
        print(f"  Video: {row['video']}")
        print(f"  Track Ratio: {row['track_ratio']}")
        print("-" * 30)

# --- Print kept videos ---
print()
print("=" * 50)
print("KEPT VIDEOS (outside cut range):")
print("=" * 50)
if len(kept_videos) == 0:
    print("No videos were kept.")
else:
    for row in kept_videos:
        print(f"  Video: {row['video']}")
        print(f"  Track Ratio: {row['track_ratio']}")
        print("-" * 30)

# --- Print summary ---
print()
print("=" * 50)
print("SUMMARY:")
print("=" * 50)
print(f"  Total videos:   {len(df)}")
print(f"  Videos removed: {len(removed_videos)}  (track_ratio between {cut_low} and {cut_high})")
print(f"  Videos kept:    {len(kept_videos)}")

# --- Save kept videos to a new CSV ---
filtered_df = pd.DataFrame(kept_videos)
new_filename = "name-that-neutrino-classifications-you-decide-timecut-6-seconds-reduced-agreementcut-50~60.csv"
filtered_df.to_csv(new_filename, index=False)
print(f"\n  Filtered data saved to {new_filename}")

# =====================================================
# HISTOGRAM: Before and After the Cut
# To combine with the histogram, the only things needed
# are the track_ratio values from each list, then we
# plot two histograms side by side for comparison.
# =====================================================

# Pull track_ratio values out of each list
before_cut = df['track_ratio'].tolist()

after_cut = []
for row in kept_videos:
    after_cut.append(row['track_ratio'])

# Bin setup: 0 to 1 in steps of 2.5%
bins = np.arange(0, 1.025, 0.025)

# Create a figure with two side-by-side plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# --- Left plot: Before the cut ---
ax1.hist(before_cut, bins=bins, edgecolor='black', color='steelblue')
ax1.set_title('Before Agreement Cut', fontsize=14)
ax1.set_xlabel('Track Ratio', fontsize=12)
ax1.set_ylabel('Number of Videos', fontsize=12)
ax1.set_xticks(np.arange(0, 1.05, 0.10))
ax1.set_xticklabels([f'{int(x*100)}%' for x in np.arange(0, 1.05, 0.10)])
ax1.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
ax1.grid(axis='y', linestyle='--', alpha=0.6)

# Shade the cut region on the left plot so it's visible
ax1.axvspan(cut_low, cut_high, color='red', alpha=0.15, label=f'Cut region ({cut_low}–{cut_high})')
ax1.legend()

# --- Right plot: After the cut ---
ax2.hist(after_cut, bins=bins, edgecolor='black', color='steelblue')
ax2.set_title('After Agreement Cut', fontsize=14)
ax2.set_xlabel('Track Ratio', fontsize=12)
ax2.set_ylabel('Number of Videos', fontsize=12)
ax2.set_xticks(np.arange(0, 1.05, 0.10))
ax2.set_xticklabels([f'{int(x*100)}%' for x in np.arange(0, 1.05, 0.10)])
ax2.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
ax2.grid(axis='y', linestyle='--', alpha=0.6)

plt.suptitle('Track Ratio Distribution: Before vs. After Agreement Cut', fontsize=15)
plt.tight_layout()
plt.savefig('track_ratio_histogram_comparison.png', dpi=150)
plt.show()
