# 10/30/2026

# 4.0 version, the following detail the differences:
# 1.) The 4.0 Level 4 gcd features come as four files (one per group), so they are combined first
# 2.) The merge also uses the file number, because event IDs repeat across different files in a run
# 3.) PIDTrackScore is added as the "pid" column, which is what the confusion matrix and feature tracker use

import pandas as pd

df1 = pd.read_csv("4-0-level-4-classifications-timecut-6-seconds-reduced.csv")
new_filename = "4-0-level-4-classifications-timecut-6-seconds-reduced-additional-features.csv"

# Combine the four gcd feature files into one table
gcd_files = [
    "cascade_clumped_25_gcd_features.csv",
    "cascade_largespan_25_gcd_features.csv",
    "track_clumped_25_gcd_features.csv",
    "track_smallspan_25_gcd_features.csv",
]
df2 = pd.concat([pd.read_csv(f) for f in gcd_files], ignore_index=True)

# Event 4083 is in two groups, so it shows up twice in the gcd files with the same values, keep one copy
df2 = df2.drop_duplicates(subset=["RunID", "EventID", "FileNumber"])

# Rename columns in df2 so they match df1's merge keys
df2 = df2.rename(columns={
    "RunID": "run_number",
    "EventID": "event_id",
    "FileNumber": "file_number",
    "PIDTrackScore": "pid"
})

# File numbers can be read as "000017" or 17 depending on the file, so make them all plain numbers
df1["file_number"] = df1["file_number"].astype(int)
df2["file_number"] = df2["file_number"].astype(int)

# Select only the extra columns you want to add
extra_cols = [
    "pid",
    "DeepCoreQTotal",	"TotalQTotal_raw",	"DeepCoreFraction",
    "NHitDOMs", "NHitStrings", "TotalCharge", "Duration",
    "ChargePerDOM", "ChargePerString",
    "EarlyChargeFraction", "LateChargeFraction", "COM_X", "COM_Y", "COM_Z", "SpatialExtent", "RMSSpread", "LineLikeness"
]

# Perform a left merge so df1 rows are preserved
merged = df1.merge(
    df2[["run_number", "event_id", "file_number"] + extra_cols],
    on=["run_number", "event_id", "file_number"],
    how="left"
)

# Check that every video found its PID score
missing = merged["pid"].isna().sum()
if missing > 0:
    print(f"WARNING: {missing} videos did not find a PID score")

# Save to a new CSV file
merged.to_csv(new_filename, index=False)

print(f"Merged CSV created: {new_filename}")
