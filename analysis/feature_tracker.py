# Last used 7/13/2026

# Same overall purpose as version 1, the following detail the differences:
# 1.) Instead of histograms with correct events vs incorrect events, do histograms with events better than PID and events worse than PID
# 2.) Keep the track vs cascade histograms the same.
# 3.) Change the difficulty curve to use JJ's style of making plots. The y axis will be accuracy, the x-axis will be the characteristic we are studying,
# and there will be two lines: One line is for the humans and will include error bars while one line is for the PID
# 4.) This code uses percentage based normalization instead of density = True
# 5.) This code overlaps the two plots on top of each other instead of displaying them side by side

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as stats
import os

def plot_feature_analysis(
    df,
    feature,
    label=None,
    track_col="track_count",
    cascade_col="cascade_count",
    truth_col="interaction_type",
    iscut="",
    normalize=False,
    n_bins=4,
):
    """
    Generate:
      1. User more accurate than PID vs User same/less accurate than PID histograms
      2. Track vs Cascade histograms
      3. Accuracy curve with human (with error bars) and PID lines

    Parameters:
        df: pandas DataFrame
        feature: column name of the feature to analyze
        label: pretty label for plots (optional)
        track_col: column with user track votes
        cascade_col: column with user cascade votes
        truth_col: column with true interaction type (1=track, 2=cascade)
        iscut: string identifier for plot titles
        normalize: whether to use percentile-based bins (True) or equal-width bins (False)
        n_bins: number of bins for the accuracy curve (default: 15)
    """

    if label is None:
        label = feature

    if normalize:
        normal_description = "Normalized"
    else:
        normal_description = "Not normalized"
    
    # -----------------------------
    # Compute necessary columns if not already present
    # -----------------------------
    # Map truth to binary: 1=Track -> 1, 2=Cascade -> 0
    df['truth_binary'] = df['interaction_type'].map({1: 1, 2: 0})
    
    # Compute PID error: |PID - truth_binary|
    df['pid_error'] = np.abs(df['pid'] - df['truth_binary'])
    
    # Compute user fraction correct
    df['user_fraction_correct'] = np.where(
        df['interaction_type'] == 1,  # Track
        df['track_ratio'],            # fraction that voted track
        1 - df['track_ratio']         # for cascade, fraction that voted cascade
    )

    
    # Compute PID accuracy: 1 - pid_error
    df['pid_accuracy'] = 1 - df['pid_error']
    
    # -----------------------------
    # Determine user vs PID accuracy comparison
    # -----------------------------
    user_more_accurate = []  # User accuracy > PID accuracy
    user_less_or_equal = []  # User accuracy <= PID accuracy
    track_vals = []
    cascade_vals = []

    event_ids = []

    # Testing
    user_more_accurate_tracks = 0
    user_more_accurate_cascades = 0
    user_less_or_equal_tracks = 0
    user_less_or_equal_cascades = 0

    for _, row in df.iterrows():
        track_votes = row[track_col]
        cascade_votes = row[cascade_col]
        true_label = row[truth_col]
        value = row[feature]
        event_id = row["event_id"]
        
        # Skip ties in user votes
        if track_votes == cascade_votes:
            continue

        # Get user and PID accuracies
        user_acc = row['user_fraction_correct']
        pid_acc = row['pid_accuracy']
        
        # Compare user vs PID accuracy
        if user_acc > pid_acc:
            user_more_accurate.append(value)
            event_ids.append(event_id)
            if true_label == 1:
                user_more_accurate_tracks += 1
            else:
                user_more_accurate_cascades += 1

        else:  # user_acc <= pid_acc
            user_less_or_equal.append(value)
            if true_label == 1:
                user_less_or_equal_tracks += 1
            else:
                user_less_or_equal_cascades += 1

        # Track vs cascade distributions (keep this from original)
        if true_label == 1:
            track_vals.append(value)
        elif true_label == 2:
            cascade_vals.append(value)

    print(event_ids)
    # Testing
    user_more_accurate_total = user_more_accurate_tracks + user_more_accurate_cascades
    user_less_or_equal_total = user_less_or_equal_tracks + user_less_or_equal_cascades

    print(f"User (more accurate than PID) picking track {user_more_accurate_tracks}/{user_more_accurate_total} = {(user_more_accurate_tracks/user_more_accurate_total)*100:.1f}%")
    print(f"User (more accurate than PID) picking cascade {user_more_accurate_cascades}/{user_more_accurate_total} = {(user_more_accurate_cascades/user_more_accurate_total)*100:.1f}%")
    print(f"User (less accurate than PID) picking track {user_less_or_equal_tracks}/{user_less_or_equal_total} = {(user_less_or_equal_tracks/user_less_or_equal_total)*100:.1f}%")
    print(f"User (less accurate than PID) picking cascade {user_less_or_equal_cascades}/{user_less_or_equal_total} = {(user_less_or_equal_cascades/user_less_or_equal_total)*100:.1f}%")

    # -----------------------------
    # Histograms: User more accurate vs User less/equal accurate
    # -----------------------------
    total_vals = user_more_accurate + user_less_or_equal
    if len(total_vals) > 0:
        bins = np.linspace(min(total_vals), max(total_vals), 30)
    else:
        print("No data to plot!")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    # Both normalized as percentages
    if len(user_more_accurate) > 0:
        weights_more = np.ones(len(user_more_accurate)) / len(user_more_accurate) * 100
        ax.hist(user_more_accurate, bins=bins, edgecolor='black', color='steelblue', 
                weights=weights_more, alpha=0.5, label='User > PID Accuracy')
    
    if len(user_less_or_equal) > 0:
        weights_less = np.ones(len(user_less_or_equal)) / len(user_less_or_equal) * 100
        ax.hist(user_less_or_equal, bins=bins, edgecolor='black', color='indianred', 
                weights=weights_less, alpha=0.5, label='User <= PID Accuracy')

    ax.set_title(f"Distribution Comparison: User vs PID Accuracy ({label}) - ({iscut})")
    ax.set_xlabel(label)
    ax.set_ylabel("Percentage of Group (%)")
    ax.legend(loc = "center", bbox_to_anchor = (0.5, 0.94))
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_ylim(0,50)  # Fixed scale for all plots

    more_accurate = np.array(user_more_accurate)
    less_or_equal = np.array(user_less_or_equal)
    more_accuracy_text = f"Users > PID Acccuracy\nEvent #: {len(more_accurate)}\nMean:    {np.mean(more_accurate):.2f}\nMedian:  {np.median(more_accurate):.2f}"
    less_accuracy_text = f"Users <= PID Accuracy\nEvent #: {len(less_or_equal)}\nMean:    {np.mean(less_or_equal):.2f}\nMedian:  {np.median(less_or_equal):.2f}"
    ax.text(0.01, 0.975, more_accuracy_text, transform=ax.transAxes, fontsize=11,verticalalignment='top', bbox=dict(boxstyle='round', facecolor='steelblue', alpha=0.3))
    ax.text(0.79, 0.975, less_accuracy_text, transform=ax.transAxes, fontsize=11,verticalalignment='top', bbox=dict(boxstyle='round', facecolor='indianred', alpha=0.3))

    plt.tight_layout()
    plt.show()



    # -----------------------------
    # Histograms: Tracks vs Cascades
    # ----------------------------- 
    if len(cascade_vals) > 0 and len(track_vals) > 0:
        all_vals = cascade_vals + track_vals
        bins = np.linspace(min(all_vals), max(all_vals), 30)

        fig, ax = plt.subplots(figsize=(10, 6))

        # Both normalized as percentages
        weights_cascade = np.ones(len(cascade_vals)) / len(cascade_vals) * 100
        weights_track = np.ones(len(track_vals)) / len(track_vals) * 100

        ax.hist(cascade_vals, bins=bins, edgecolor='black', color='green', 
                weights=weights_cascade, alpha=0.5, label='Cascades')
        ax.hist(track_vals, bins=bins, edgecolor='black', color='purple', 
                weights=weights_track, alpha=0.5, label='Tracks')

        ax.set_title(f"Distribution Comparison: Cascades vs Tracks ({label}) - ({iscut})")
        ax.set_xlabel(label)
        ax.set_ylabel("Percentage of Group (%)")
        ax.legend(loc = "center", bbox_to_anchor = (0.5, 0.94))
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_ylim(0, 50)  # Fixed scale for all plots

        cascade = np.array(cascade_vals)
        track = np.array(track_vals)
        cascade_text = f"Cascades\nEvent #: {len(cascade)}\nMean:    {np.mean(cascade):.2f}\nMedian:  {np.median(cascade):.2f}"
        track_text = f"Tracks\nEvent #: {len(track)}\nMean:    {np.mean(track):.2f}\nMedian:  {np.median(track):.2f}"
        ax.text(0.01, 0.975, cascade_text, transform=ax.transAxes, fontsize=11,verticalalignment='top', bbox=dict(boxstyle='round', facecolor='green', alpha=0.3))
        ax.text(0.855, 0.975, track_text, transform=ax.transAxes, fontsize=11,verticalalignment='top', bbox=dict(boxstyle='round', facecolor='purple', alpha=0.3))
 
        plt.tight_layout()
        plt.show()
    else:
        print("Skipping Track vs Cascade histogram - insufficient data")




    # -----------------------------
    # NEW: Accuracy Curve (Human vs PID)
    # -----------------------------
    print("\n" + "=" * 80)
    print("ACCURACY CURVE: Human vs PID")
    print("=" * 80)
    
    # Get all feature values for binning
    all_feature_vals = np.array(total_vals)  # Use total_vals from earlier
    
    if len(all_feature_vals) == 0:
        print("No data for accuracy curve!")
        return
    
    # Create bins based on feature distribution
    min_val = all_feature_vals.min()
    max_val = all_feature_vals.max()
    
    # Use either percentile-based or equal-width bins
    if normalize:
        # Use percentiles for more balanced bins
        bin_edges = np.percentile(all_feature_vals, np.linspace(0, 100, n_bins + 1))
    else:
        # Use equal-width bins
        bin_edges = np.linspace(min_val, max_val, n_bins + 1)
    
    # Get z-score for 95% confidence interval
    z = stats.norm.ppf(0.975)
    
    # Compute accuracies per bin
    bin_centers = []
    human_acc = []
    human_err = []
    pid_acc = []
    bin_counts = []
    
    # Store the bin indices for each data point to compute accuracies
    # Create a list of (value, is_human_better) pairs
    value_accuracy_pairs = []
    
    # Re-loop through the dataframe to get the data with bin assignments
    for _, row in df.iterrows():
        track_votes = row[track_col]
        cascade_votes = row[cascade_col]
        
        # Skip ties in user votes
        if track_votes == cascade_votes:
            continue
            
        value = row[feature]
        user_acc = row['user_fraction_correct']
        pid_acc_val = row['pid_accuracy']
        
        value_accuracy_pairs.append((value, user_acc, pid_acc_val))
    
    # Bin the data
    for i in range(len(bin_edges) - 1):
        # Get data in this bin
        if i < len(bin_edges) - 2:
            bin_data = [(v, u, p) for v, u, p in value_accuracy_pairs 
                       if v >= bin_edges[i] and v < bin_edges[i + 1]]
        else:
            bin_data = [(v, u, p) for v, u, p in value_accuracy_pairs 
                       if v >= bin_edges[i] and v <= bin_edges[i + 1]]
        
        n = len(bin_data)
        bin_counts.append(n)
        
        if n >= 3:
            # Calculate human accuracy and error
            human_accuracies = [u for _, u, _ in bin_data]
            pid_accuracies = [p for _, _, p in bin_data]
            
            p_human = np.mean(human_accuracies)
            err_human = z * np.sqrt(p_human * (1 - p_human) / n)
            
            p_pid = np.mean(pid_accuracies)
        else:
            p_human = np.nan
            err_human = np.nan
            p_pid = np.nan
        
        # Bin center
        center = 0.5 * (bin_edges[i] + bin_edges[i + 1])
        
        bin_centers.append(center)
        human_acc.append(p_human)
        human_err.append(err_human)
        pid_acc.append(p_pid)
    
    # Print debugging information
    print(f"Number of bins: {len(bin_edges) - 1}")
    print(f"Feature range: [{min_val:.3f}, {max_val:.3f}]")
    print("Bin centers:", [round(x, 3) for x in bin_centers])
    print("Bin counts:", bin_counts)
    print("Human accuracy:", [
        None if np.isnan(x) else round(x, 3) 
        for x in human_acc
    ])
    print("PID accuracy:", [
        None if np.isnan(x) else round(x, 3) 
        for x in pid_acc
    ])
    print("=" * 80 + "\n")
    
    # Filter out NaN values for plotting
    valid_indices = [i for i, x in enumerate(human_acc) if not np.isnan(x)]
    
    if len(valid_indices) == 0:
        print("No valid bins with enough data for accuracy curve!")
        return
    
    valid_centers = [bin_centers[i] for i in valid_indices]
    valid_human = [human_acc[i] for i in valid_indices]
    valid_human_err = [human_err[i] for i in valid_indices]
    valid_pid = [pid_acc[i] for i in valid_indices]
    
    # Create the accuracy curve plot
    plt.figure(figsize=(10, 6))
    
    # Plot human accuracy with error bars
    plt.errorbar(
        valid_centers,
        valid_human,
        yerr=valid_human_err,
        fmt='o-',
        label='Human',
        color='blue',
        linewidth=1.5,
        markersize=6,
        capsize=3,
        elinewidth=1.5,
        capthick=1.5,
        markerfacecolor='white',
        markeredgewidth=1.5
    )
    
    # Plot PID accuracy - make it more visible
    plt.errorbar(
        valid_centers,
        valid_pid,
        yerr=None,
        fmt='s--',
        label='PID',
        color='red',
        linewidth=1.5,
        markersize=6,
        markerfacecolor='white',
        markeredgewidth=1.5,
        alpha=0.8
    )
    
    # Set labels and title
    plt.xlabel(label)
    plt.ylabel("Average Accuracy")
    plt.title(f"Average Human vs PID Accuracy by {label} - ({iscut})")
    
    # Set axis limits
    plt.ylim(-0.05, 1.10)
    if len(valid_centers) > 0:
        x_min = min(valid_centers) - 0.1 * (max(valid_centers) - min(valid_centers))
        x_max = max(valid_centers) + 0.1 * (max(valid_centers) - min(valid_centers))
        plt.xlim(x_min, x_max)
    
    # Add a horizontal line at 0.5 for random chance
    plt.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5, label='Random Chance')
    
    # Add legend
    plt.legend(
        loc="upper right",
        fontsize=10,
        frameon=True,
        framealpha=0.8,
        borderpad=0.5,
        labelspacing=0.4,
        handlelength=2
    )
    
    # Add grid
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Tight layout
    plt.tight_layout()
    plt.show()

    return bin_edges

def explore_bin_events(df, feature, bin_edges, bin_idx):
    """
    Show all events in a specific bin from your accuracy plot.
    
    Parameters:
        df: Your data
        feature: The column name you're analyzing (e.g., "NHitStrings")
        bin_edges: The bin boundaries from your plot
        bin_idx: Which bin to look at (0, 1, 2, or 3)
    """
    event_id_list = []
    
    # 1. Find the range of values for this bin
    low = bin_edges[bin_idx]
    high = bin_edges[bin_idx + 1]
    
    # 2. Get all events that fall in this bin
    # For last bin, include both boundaries
    if bin_idx == len(bin_edges) - 2:  # Last bin
        mask = (df[feature] >= low) & (df[feature] <= high)
    else:
        mask = (df[feature] >= low) & (df[feature] < high)
    
    events = df[mask].copy()
    
    # 3. Calculate the difference column
    events['human_minus_pid'] = events['user_fraction_correct'] - events['pid_accuracy']
    
    # 4. Print summary
    print("\n" + "="*70)
    print(f"BIN {bin_idx}: {feature} between {low:.2f} and {high:.2f}")
    print(f"Number of events: {len(events)}")
    print("="*70)
    
    if len(events) == 0:
        print("No events in this bin!")
        return events
    
    # 5. Show statistics
    print("\nQUICK STATISTICS:")
    print(f"  Average Human Accuracy: {events['user_fraction_correct'].mean():.3f}")
    print(f"  Average PID Accuracy:   {events['pid_accuracy'].mean():.3f}")
    print(f"  Average Difference:     {events['human_minus_pid'].mean():.3f}")
    print(f"  Human better than PID:  {(events['human_minus_pid'] > 0).sum()} out of {len(events)} events")
    
    # 6. Show each event
    print("\nINDIVIDUAL EVENTS:")
    print("-"*70)
    
    for i, row in events.iterrows():
        print(f"\nEvent {i}:")
        print(f"  Event ID: {row['event_id']}")
        event_id_list.append(row['event_id'])
        print(f"  PID: {row['pid']}")
        print(f"  {feature}: {row[feature]:.2f}")
        print(f"  Human accuracy: {row['user_fraction_correct']:.3f}")
        print(f"  PID accuracy:   {row['pid_accuracy']:.3f}")
        print(f"  Difference:     {row['human_minus_pid']:+.3f}")  # + shows sign
        # print(f"  Track votes: {row['track_count']}, Cascade votes: {row['cascade_count']}")
        print(f"  True type: {'Track' if row['interaction_type'] == 1 else 'Cascade'}")
    
    # 7. Show a clean table
    print("\n" + "="*70)
    print("SUMMARY TABLE (Key columns only)")
    print("="*70)
    
    # Pick only the most useful columns
    columns_to_show = [
        'event_id',
        feature, 
        'user_fraction_correct', 
        'pid',
        'pid_accuracy', 
        'human_minus_pid',
        # 'track_count', 
        # 'cascade_count', 
        'interaction_type'
    ]
    
    # Only use columns that actually exist
    existing_cols = [col for col in columns_to_show if col in events.columns]
    print(events[existing_cols].to_string())
    
    print(f"\n{event_id_list}")
    return events


# Main
# df_no_cut = pd.read_csv("name-that-neutrino-classifications-mini-beta-timecut-0-seconds-accuracycut-0percent-reduced-qtotal-additional-features.csv")
# df_cut = pd.read_csv("name-that-neutrino-classifications-mini-beta-timecut-2-seconds-accuracycut-50percent-reduced-qtotal-agreementcut40~60-additional-features.csv")
# df_cut = pd.read_csv("name-that-neutrino-classifications-you-decide-without-stacey-timecut-2-seconds-accuracycut-50-percent-reduced-agreementcut-50~60-additional-features.csv")
# df_cut = pd.read_csv("name-that-neutrino-classifications-you-decide-timecut-6-seconds-accuracycut-50-percent-reduced-agreementcut-50~60-additional-features.csv")
df_cut = pd.read_csv("name-that-neutrino-classifications-you-decide-timecut-6-seconds-accuracycut-50-percent-reduced-additional-features.csv")
# bin_edges = plot_feature_analysis(df_cut, feature="deepcore_qtotal", label="DeepCore QTotal", iscut = "Cuts applied", normalize = True)
# last_bin_events_df = explore_bin_events(df_cut, "deepcore_qtotal", bin_edges, 3)

# bin_edges = plot_feature_analysis(df_cut, feature="TotalCharge", label="Total QTotal", iscut = "Cuts applied", normalize = True)
# last_bin_events_df = explore_bin_events(df_cut, "TotalCharge", bin_edges, 3)

bin_edges = plot_feature_analysis(df_cut, feature="NHitStrings", label="Number of strings hit", iscut = "Cuts applied", normalize = True)
last_bin_events_df = explore_bin_events(df_cut, "NHitStrings", bin_edges, 3)

# bin_edges = plot_feature_analysis(df_cut, feature="Duration", label="Time (in nanoseconds)", iscut = "Cuts applied", normalize = True)
# last_bin_events_df = explore_bin_events(df_cut, "Duration", bin_edges, 3)

# bin_edges = plot_feature_analysis(df_cut, feature="ChargePerString", label="Charge per string", iscut = "Cuts applied", normalize = True)
# last_bin_events_df = explore_bin_events(df_cut, "ChargePerString", bin_edges, 3)

# plot_feature_analysis(df_cut, feature="EarlyChargeFraction", label="Early charge fraction", iscut = "Cuts applied", normalize = True)

# bin_edges =  plot_feature_analysis(df_cut, feature="SpatialExtent", label="Spatial extent", iscut = "Cuts applied", normalize = True)
# last_bin_events_df = explore_bin_events(df_cut, "SpatialExtent", bin_edges, 3)

# bin_edges =  plot_feature_analysis(df_cut, feature="RMSSpread", label="RMS Spread", iscut = "Cuts applied", normalize = True)
# last_bin_events_df = explore_bin_events(df_cut, "RMSSpread", bin_edges, 3)

# plot_feature_analysis(df_cut, feature="LineLikeness", label="Line likeness", iscut = "Cuts applied", normalize = True)

# plot_feature_analysis(df_cut, feature="pid", label="PID", iscut = "Cuts applied", normalize = True)

# plot_feature_analysis(df_cut, feature="COM_X", label="COM - X axis", iscut = "Cuts applied", normalize = True)

# plot_feature_analysis(df_cut, feature="COM_Y", label="COM - Y axis", iscut = "Cuts applied", normalize = True)

# plot_feature_analysis(df_cut, feature="COM_Z", label="COM - Z axis", iscut = "Cuts applied", normalize = True)
