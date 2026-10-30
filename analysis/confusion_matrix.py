# 10/30/2026
# Same exact purpose as confusion_matrix.py (majority votes), the following detail the differences for 4.0:
# 1.) PREDICTION = "pid" makes the same matrix for the PID instead of the users
#     (pid >= 0.5 -> Track, otherwise Cascade). Run it once with "user" and once with "pid"
# 2.) Cascade is first on both axes, the y-axis is "User Agreement" (or "PID") and the x-axis is "MC Truth Label"
# 3.) Bigger text so it can be read on a slide, and the title is one line
# ============================================================
# Neutrino Confusion Matrix
# ============================================================
# This script reads a spreadsheet of IceCube neutrino events
# and builds a confusion matrix based on the majority vote
# for each of the videos.
#
# Instead of counting every individual user vote, we classify
# each video into a single prediction using the majority vote:
#   - If more users voted Track than Cascade -> predicted Track
#   - If more users voted Cascade than Track -> predicted Cascade
#   - If it's a tie -> we skip that video
#
# Each video's single prediction is then sorted into one of
# four cells based on whether it matches the true answer:
#
#   true_positive:  predicted Track,   true answer was Track   (correct)
#   false_positive: predicted Track,   true answer was Cascade (wrong)
#   false_negative: predicted Cascade, true answer was Track   (wrong)
#   true_negative:  predicted Cascade, true answer was Cascade (correct)
#
# At the end, the four cells add up to the number of videos.
# ============================================================
# --- IMPORTS ---
import pandas as pd              # lets us read and work with spreadsheets
import matplotlib.pyplot as plt  # lets us draw charts and figures
import matplotlib.cm as cm       # gives us access to colourmaps (Blues, Reds, etc.)
import matplotlib.colors as mcolors  # lets us map a number (0-1) to a colour
import numpy as np               # lets us build arrays for the matrix

# ---- SETTINGS ---- #
PREDICTION = "user"     # <-- "user" for the majority vote, "pid" for the PID
PID_THRESHOLD = 0.5     # <-- pid at or above this counts as the PID saying Track
# ------------------ #

# ============================================================
# STEP 1: LOAD THE DATA
# ============================================================
df = pd.read_csv("4-0-level-4-classifications-timecut-6-seconds-reduced-additional-features-track-clumped.csv")
# df = pd.read_csv("4-0-level-4-classifications.csv")

titleName = "NtN 4.0 Level 4, time cut (6 s), no agreement cut, clumped tracks"
print(f"Loaded {len(df)} videos.")
# ============================================================
# STEP 2: COUNT VIDEOS INTO THE FOUR CELLS
# ============================================================
# We start all four cells at zero, then loop through every
# video and give it a single prediction.
#
# The majority vote works like this:
#   - More Track votes than Cascade votes   -> predicted Track
#   - More Cascade votes than Track votes   -> predicted Cascade
#   - Equal votes (a tie)                   -> skip this video
#
# The PID works like this:
#   - pid at or above PID_THRESHOLD -> predicted Track
#   - pid below PID_THRESHOLD       -> predicted Cascade
#
# We then compare that prediction to the true answer:
#
#   Predicted Track, true answer Track     -> true_positive
#   Predicted Track, true answer Cascade   -> false_positive
#   Predicted Cascade, true answer Track   -> false_negative
#   Predicted Cascade, true answer Cascade -> true_negative

true_positive  = 0
false_positive = 0
false_negative = 0
true_negative  = 0
ties_skipped   = 0   # keeps track of any tied videos we skip


# Loop through every row (video) in the spreadsheet.
# iterrows() gives us each row one at a time as a variable called "row".
for index, row in df.iterrows():
    track_votes   = row["track_count"]      # number of users who voted Track
    cascade_votes = row["cascade_count"]    # number of users who voted Cascade
    true_label    = row["interaction_type"] # the true Monte Carlo answer (1 or 2)

    # Determine the prediction for this video
    if PREDICTION == "pid":
        if row["pid"] >= PID_THRESHOLD:
            predicted = "Track"
        else:
            predicted = "Cascade"
    elif track_votes > cascade_votes:
        predicted = "Track"
    elif cascade_votes > track_votes:
        predicted = "Cascade"
    else:
        # It's a tie -- we can't make a majority prediction, so skip
        ties_skipped += 1
        continue

    # Now sort this video's prediction into the right cell
    if true_label == 1:
        # This video was truly a Track.
        if predicted == "Track":
            true_positive += 1    # predicted Track, was Track (correct)
        else:
            false_negative += 1   # predicted Cascade, was Track (wrong)
    elif true_label == 2:
        # This video was truly a Cascade.
        if predicted == "Cascade":
            true_negative += 1    # predicted Cascade, was Cascade (correct)
        else:
            false_positive += 1   # predicted Track, was Cascade (wrong)

total = true_positive + false_positive + false_negative + true_negative

# Print a summary to the console
print(f"\nPrediction: {PREDICTION}")
print(f"Total videos counted: {total}  (ties skipped: {ties_skipped})")
print(f"true_positive  = {true_positive} (predicted Track,   was Track)")
print(f"false_positive = {false_positive} (predicted Track,   was Cascade)")
print(f"false_negative = {false_negative} (predicted Cascade, was Track)")
print(f"true_negative  = {true_negative} (predicted Cascade, was Cascade)")

# ============================================================
# STEP 3: CALCULATE ACCURACY
# ============================================================
# Accuracy: of all videos, what fraction were predicted correctly?
accuracy = (true_positive + true_negative) / total
print(f"\n  Accuracy:  {true_positive + true_negative}/{total} = {accuracy:.1%}")

# ============================================================
# STEP 4: CALCULATE COLUMN PERCENTAGES AND FRACTIONS
# ============================================================
# The rows represent PREDICTED LABELS
# and the columns represent TRUE LABELS (MC truth).
#
# Layout:
#
#                      True Cascade      True Track
#   Pred. Cascade    [ true_negative,    false_negative ]
#   Pred. Track      [ false_positive,   true_positive  ]
#
# Percentages are normalised by TRUE LABEL (column totals),
# meaning each column sums to 100%:
#
#   Column 0 denominator = total true Cascades
#   Column 1 denominator = total true Tracks

# Raw counts
counts = np.array([
    [true_negative,  false_negative],   # Row 0 = Predicted Cascade
    [false_positive, true_positive]     # Row 1 = Predicted Track
])

# Column totals (how many TRUE Cascades vs TRUE Tracks exist)
total_true_cascade = true_negative + false_positive
total_true_track   = false_negative + true_positive

column_totals = np.array([
    [total_true_cascade, total_true_track],
    [total_true_cascade, total_true_track]
])

# Percentages normalized by TRUE LABEL (column normalization)
percentages = counts / column_totals * 100

# ============================================================
# STEP 5: DRAW THE CONFUSION MATRIX MANUALLY
# ============================================================
# Because we want percentage-based colouring and fraction text,
# we draw the matrix ourselves using matplotlib instead of
# using scikit's ConfusionMatrixDisplay.
#
# The matrix is drawn on a coordinate grid where:
#   x goes from 0 to 2 (left to right: True Cascade | True Track)
#   y goes from 0 to 2 (bottom to top: Pred. Track | Pred. Cascade)
#
# Each cell is a 1x1 square. We colour it based on its percentage,
# then write two lines of text inside it:
#   Line 1: the percentage (large)
#   Line 2: the fraction  count / column_total

# Create the figure and axes (the blank canvas)
fig, ax = plt.subplots(figsize=(8.5, 7.5))

# Choose the "Blues" colourmap. A colourmap maps a number between
# 0.0 and 1.0 to a colour. 0.0 = lightest blue, 1.0 = darkest blue.
colormap = plt.get_cmap("Blues")

# We also need a "normaliser", this tells matplotlib what range
# of values maps to the full colourmap (0% to 100% here).
normaliser = mcolors.Normalize(vmin=0, vmax=100)

# Loop through every cell in the 2x2 grid.
# "row" goes 0 or 1 (0 = Predicted Cascade row, 1 = Predicted Track row)
# "col" goes 0 or 1 (0 = True Cascade column, 1 = True Track column)
for row in range(2):
    for col in range(2):
        # Get the values for this specific cell
        count      = counts[row, col]
        percentage = percentages[row, col]

        # --- Draw the coloured rectangle for this cell ---
        # The colour comes from mapping the percentage into the Blues colourmap.
        cell_colour = colormap(normaliser(percentage))

        # Rectangle bottom-left corner: (col, 1 - row)
        # This places Predicted Cascade on top (row=0 -> y=1) and Pred. Track below.
        ax.add_patch(plt.Rectangle(
            (col, 1 - row),   # bottom-left corner (x, y)
            1, 1,             # width and height
            color=cell_colour
        ))

        # --- Choose text colour ---
        # Dark text on light backgrounds, white text on dark backgrounds.
        # Percentages above 60% produce dark enough colours to need white text.
        if percentage > 60:
            text_colour = "white"
        else:
            text_colour = "black"

        # --- Line 1: percentage ---
        ax.text(
            col + 0.5,          # x position: centre of this column
            1 - row + 0.56,     # y position: upper area of this row
            f"{percentage:.1f}%",
            ha="center", va="center",
            fontsize=28,
            color=text_colour
        )

        # --- Line 2: fraction count / column_total ---
        # e.g. "18/25" meaning 18 out of 25 TRUE Cascade videos landed here
        ax.text(
            col + 0.5,
            1 - row + 0.40,
            f"{count}/{column_totals[row, col]}",
            ha="center", va="center",
            fontsize=22,
            color=text_colour
        )

# ============================================================
# STEP 6: ADD THE COLOUR BAR
# ============================================================
# The colour bar is a legend on the side showing what colour
# corresponds to what percentage.
scalar_mappable = cm.ScalarMappable(cmap=colormap, norm=normaliser)
colorbar = plt.colorbar(scalar_mappable, ax=ax)
colorbar.set_label("Percentage", fontsize=20)
colorbar.ax.tick_params(labelsize=16)

# ============================================================
# STEP 7: LABELS, TITLE, AND FORMATTING
# ============================================================
# Set the x-axis tick positions and labels (the TRUE classes)
ax.set_xticks([0.5, 1.5])
ax.set_xticklabels(["Cascade", "Track"], fontsize=22)

# Set the y-axis tick positions and labels (the PREDICTED classes, bottom to top)
ax.set_yticks([0.5, 1.5])
ax.set_yticklabels(["Track", "Cascade"], fontsize=22, rotation=90, va="center")

# Axis titles
ax.set_xlabel("MC Truth Label", fontsize=24)
if PREDICTION == "pid":
    ax.set_ylabel("PID", fontsize=24)
else:
    ax.set_ylabel("User Agreement", fontsize=24)

# Overall title
ax.set_title(titleName, fontsize=18, pad=12)

# Set the plot boundaries so our rectangles fill the space neatly
ax.set_xlim(0, 2)
ax.set_ylim(0, 2)

# Remove the default border around the plot
for spine in ax.spines.values():
    spine.set_visible(False)

# Remove the small tick marks on the axes
ax.tick_params(length=0)

plt.tight_layout()

# Save and display
plot_name = f"confusion_matrix_4_0_{PREDICTION}.png"
plt.savefig(plot_name, dpi=150, bbox_inches="tight")
plt.show()
print(f"\nDone! Plot saved as {plot_name}")
