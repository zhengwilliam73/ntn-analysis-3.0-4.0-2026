# Last used 7/2/26
# Same exact purpose as confusion_matrix_v3a.py, but majority votes are used instead of individial votes
# ============================================================
# Neutrino Confusion Matrix
# ============================================================
# This script reads a spreadsheet of IceCube neutrino events
# and builds a confusion matrix based on the majority vote
# for each of the 50 videos.
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
# At the end, the four cells add up to (at most) 50 videos.
# ============================================================
# --- IMPORTS ---
import pandas as pd              # lets us read and work with spreadsheets
import matplotlib.pyplot as plt  # lets us draw charts and figures
import matplotlib.cm as cm       # gives us access to colourmaps (Blues, Reds, etc.)
import matplotlib.colors as mcolors  # lets us map a number (0-1) to a colour
import numpy as np               # lets us build arrays for the matrix
# ============================================================
# STEP 1: LOAD THE DATA
# ============================================================
# df = pd.read_csv("name-that-neutrino-classifications-you-decide-without-stacey-timecut-2-seconds-accuracycut-50-percent-reduced-agreementcut-50~60.csv")
# df = pd.read_csv("name-that-neutrino-classifications-you-decide-timecut-6-seconds-accuracycut-50-percent-reduced-agreementcut-50~60-additional-features.csv")
df = pd.read_csv("name-that-neutrino-classifications-you-decide-timecut-6-seconds-reduced-agreementcut-50~60.csv")

titleName = "Matrix with only 6 second time cut and agreement cut"
print(f"Loaded {len(df)} videos.")
# ============================================================
# STEP 2: COUNT VIDEOS INTO THE FOUR CELLS
# ============================================================
# We start all four cells at zero, then loop through every
# video and give it a single majority-vote prediction.
#
# The majority vote works like this:
#   - More Track votes than Cascade votes   -> predicted Track
#   - More Cascade votes than Track votes   -> predicted Cascade
#   - Equal votes (a tie)                   -> skip this video
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
    subject_id = row["subject_id"]

    # Determine the majority-vote prediction for this video
    if track_votes > cascade_votes:
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
            # print(subject_id)
        else:
            false_positive += 1   # predicted Track, was Cascade (wrong)

total = true_positive + false_positive + false_negative + true_negative

# Print a summary to the console
print(f"\nTotal videos counted: {total}  (ties skipped: {ties_skipped})")
print(f"true_positive  = {true_positive} (predicted Track,   was Track)")
print(f"false_positive = {false_positive} (predicted Track,   was Cascade)")
print(f"false_negative = {false_negative} (predicted Cascade, was Track)")
print(f"true_negative  = {true_negative} (predicted Cascade, was Cascade)")

# ============================================================
# STEP 3: CALCULATE PERFORMANCE METRICS
# ============================================================
# Accuracy: of all videos, what fraction were predicted correctly?
accuracy = (true_positive + true_negative) / total

# Precision: of all videos predicted Track, what fraction were truly Tracks?
precision = true_positive / (true_positive + false_positive)

# Recall: of all truly Track videos, what fraction were predicted Track?
recall = true_positive / (true_positive + false_negative)

# F1 Score: balances precision and recall into one number (0 = worst, 1 = best)
f1 = 2 * precision * recall / (precision + recall)

print(f"\nPerformance metrics:")
print(f"  Accuracy:  {accuracy:.1%}")
print(f"  Precision: {precision:.1%}")
print(f"  Recall:    {recall:.1%}")
print(f"  F1 Score:  {f1:.3f}")

# ============================================================
# STEP 4: CALCULATE COLUMN PERCENTAGES AND FRACTIONS
# ============================================================
# Now the rows represent PREDICTED LABELS
# and the columns represent TRUE LABELS (MC truth).
#
# Layout:
#
#                      True Track        True Cascade
#   Predicted Track  [ true_positive,    false_positive ]
#   Pred. Cascade    [ false_negative,   true_negative  ]
#
# Percentages are normalised by TRUE LABEL (column totals),
# meaning each column sums to 1.0:
#
#   Column 0 denominator = total true Tracks
#   Column 1 denominator = total true Cascades

# Raw counts in the new orientation
counts = np.array([
    [true_positive,  false_positive],   # Row 0 = Predicted Track
    [false_negative, true_negative]     # Row 1 = Predicted Cascade
])

# Column totals (how many TRUE Tracks vs TRUE Cascades exist)
total_true_track   = true_positive + false_negative
total_true_cascade = false_positive + true_negative

column_totals = np.array([
    [total_true_track,   total_true_cascade],
    [total_true_track,   total_true_cascade]
])

# Percentages normalized by TRUE LABEL (column normalization)
percentages = counts / column_totals

# ============================================================
# STEP 5: DRAW THE CONFUSION MATRIX MANUALLY
# ============================================================
# Because we want percentage-based colouring and fraction text,
# we draw the matrix ourselves using matplotlib instead of
# using scikit's ConfusionMatrixDisplay.
#
# The matrix is drawn on a coordinate grid where:
#   x goes from 0 to 2 (left to right: True Track | True Cascade)
#   y goes from 0 to 2 (bottom to top: Pred. Cascade | Pred. Track)
#
# Each cell is a 1x1 square. We colour it based on its percentage,
# then write three lines of text inside it:
#   Line 1: the percentage (large, bold)
#   Line 2: the fraction  count / column_total
#   Line 3: the raw count

# Create the figure and axes (the blank canvas)
fig, ax = plt.subplots(figsize=(7, 6))

# Choose the "Blues" colourmap. A colourmap maps a number between
# 0.0 and 1.0 to a colour. 0.0 = lightest blue, 1.0 = darkest blue.
colormap = plt.get_cmap("Blues")

# We also need a "normaliser" — this tells matplotlib what range
# of values maps to the full colourmap (0% to 100% here).
normaliser = mcolors.Normalize(vmin=0.0, vmax=1.0)

# Loop through every cell in the 2x2 grid.
# "row" goes 0 or 1 (0 = Predicted Track row, 1 = Predicted Cascade row)
# "col" goes 0 or 1 (0 = True Track column, 1 = True Cascade column)
for row in range(2):
    for col in range(2):
        # Get the values for this specific cell
        count      = counts[row, col]
        percentage = percentages[row, col]

        # --- Draw the coloured rectangle for this cell ---
        # The colour comes from mapping the percentage into the Blues colourmap.
        cell_colour = colormap(normaliser(percentage))

        # Rectangle bottom-left corner: (col, 1 - row)
        # This places Predicted Track on top (row=0 -> y=1) and Pred. Cascade below.
        ax.add_patch(plt.Rectangle(
            (col, 1 - row),   # bottom-left corner (x, y)
            1, 1,             # width and height
            color=cell_colour
        ))

        # --- Choose text colour ---
        # Dark text on light backgrounds, white text on dark backgrounds.
        # Percentages above 60% produce dark enough colours to need white text.
        if percentage > 0.60:
            text_colour = "white"
        else:
            text_colour = "black"

        percentage_text = f"{percentage:.1%}"

        # --- Line 1: percentage (large, bold) ---
        ax.text(
            col + 0.5,          # x position: centre of this column
            1 - row + 0.65,     # y position: upper area of this row
            percentage_text,
            ha="center", va="center",
            fontsize=26, fontweight="bold",
            color=text_colour
        )

        # --- Line 2: fraction count / column_total ---
        # The fraction shows:  count / column_total
        # e.g. "18 / 25" meaning 18 out of 25 TRUE Track videos landed here
        fraction_text = f"{count} / {column_totals[row, col]}"
        ax.text(
            col + 0.5,
            1 - row + 0.42,
            fraction_text,
            ha="center", va="center",
            fontsize=11,
            color=text_colour
        )

# ============================================================
# STEP 6: ADD THE COLOUR BAR
# ============================================================
# The colour bar is a legend on the side showing what colour
# corresponds to what percentage.
#
# To add it, we create a "ScalarMappable" — this is just an
# object that links the colourmap and normaliser together so
# matplotlib knows how to draw the bar.
scalar_mappable = cm.ScalarMappable(cmap=colormap, norm=normaliser)

# Add the colour bar to the figure, attached to our axes (ax)
colorbar = plt.colorbar(scalar_mappable, ax=ax)

# Label the colour bar and format its tick marks as percentages
colorbar.set_label("Percentage of true-label videos in each column", fontsize=10)
colorbar.set_ticks([0.0, 0.25, 0.50, 0.75, 1.0])
colorbar.set_ticklabels(["0%", "25%", "50%", "75%", "100%"])

# ============================================================
# STEP 7: LABELS, TITLE, AND FORMATTING
# ============================================================
# Set the x-axis tick positions and labels (the TRUE classes)
ax.set_xticks([0.5, 1.5])
ax.set_xticklabels(["True Track", "True Cascade"], fontsize=11)

# Set the y-axis tick positions and labels (the PREDICTED classes)
ax.set_yticks([0.5, 1.5])
ax.set_yticklabels(["Pred. Cascade", "Pred. Track"], fontsize=11)

# Move the x-axis labels to the top (common for confusion matrices)
ax.xaxis.set_label_position("top")
ax.xaxis.tick_top()

# Axis titles
ax.set_xlabel("True Label  (Monte Carlo Interaction Type)", fontsize=11, labelpad=12)
ax.set_ylabel("Majority-Vote Prediction", fontsize=11, labelpad=12)

# Overall title
plt.title(
    f"{titleName}\n"
    f"n={total} videos   Accuracy={accuracy:.1%}",
    fontsize=12,
    pad=30
)

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
plt.savefig("neutrino_confusion_matrix_v3.png", dpi=150, bbox_inches="tight")
plt.show()
print("\nDone! Plot saved as neutrino_confusion_matrix_v3.png")
