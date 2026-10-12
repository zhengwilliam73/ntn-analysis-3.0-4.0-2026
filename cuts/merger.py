# 7/6/2026

import pandas as pd

df1 = pd.read_csv("low_energy_quiz_events_answers.csv")
df2 = pd.read_csv("low_energy_quiz_gcd_features.csv")
new_filename = "low_energy_quiz_events_all_features.csv"

# Rename columns in df2 so they match df1's merge keys
df2 = df2.rename(columns={
    "RunID": "run_number",
    "EventID": "event_id"
})

# Select only the extra columns you want to add
extra_cols = [
    "DeepCoreQTotal",	"TotalQTotal_raw",	"DeepCoreFraction",
    "NHitDOMs", "NHitStrings", "TotalCharge", "Duration",
    "ChargePerDOM", "ChargePerString",
    "EarlyChargeFraction", "LateChargeFraction", "COM_X", "COM_Y", "COM_Z", "SpatialExtent", "RMSSpread", "LineLikeness"
]

# Perform a left merge so df1 rows are preserved
merged = df1.merge(
    df2[["run_number", "event_id"] + extra_cols],
    on=["run_number", "event_id"],
    how="left"
)

# Save to a new CSV file
merged.to_csv(new_filename, index=False)

print(f"Merged CSV created: {new_filename}")
