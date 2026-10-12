Python scripts used for NtN 3.0 and 4.0 analysis

- Folders:
    - cuts:
      - Contains scripts involved with either setting up csv files or doing cuts on the data
    analysis: 
      Contains scripts involved with analyzing csv files

  - Files:
    - cuts/accuracy_cut.py: 
      - Executes an accuracy cut. An accuracy cut will calculate the accuracy percentage of one user, compare it to a set threshold (i.e. 50%), and will remove all of the user's classifications if their accuracy is below this threshold.
      
    - cuts/agreement_cut.py:
      - Executes an agreement cut. An agreement cut will look at individual videos and decide whether or not to cut that video if the users do not seem to agree enough (i.e. if 50% of users said cascade and 50% of users said track, this video would probably get cut as the users did not come up with a strong answer). This code specifically uses the ratio of usrs who selected track vs total user votes. In the sample parameters in the code, 40% to 60% is used.

    - cuts/merger.py:
      - The 3.0/4.0 zooniverse manifests contain very little information about the events to avoid clutter since it is not necessary to be included in a zooniverse manifest. However, each neutrino event has lots of data that can be extracted from an .i3 file (i.e. time duration of event, number of strings hit, qtotal, etc). This python file merges data on how users voted on each video with neutrino event data.

    - cuts/reducer.py:
      - In order to analyze videos, we need to compress down the thousands of user votes into a csv file where one row represents one video. This is the job of reducer.py

    - cuts/timecut.py:
      - Executes a time cut. Time cuts will remove any cut that took less time than the allowed threshold (i.e. 6 seconds). This is to remove cuts that we think were either made by mistake or made by people who did not watch the entire video


    - analysis/confusion_matrix.py:
      - Outputs a confusion matrix showing how accurate users are when it comes to tracks and cascades.
      - Requires a csv file that has been ran through reducer.py Cuts are highly reccomended but not required.

    - analysis/feature_tracker.py:
      - This script was used quite heavily when analyzing NtN 3.0. This code makes three different graphs for each feature of a neutrino event (i.e. time duration of event, number of strings hit, qtoatl, etc). The first graph splits the videos into two groups: One group of videos where outperform the PID and one group of videos where users match or do worse than the PID. These two groups are then plotted together on a histogram against a feature, with the intention of seeing if this feature has any impact on user performance. The second graph is the same as the first graph with the exception of the two groups being tracks and cascades instead of being dependent on user/PID performance. The third graph is an accuracy curve with the blue line showing the accuracy of the people (with error bars) along with a red line shwoing the accuracy of the PID.
      - Requites a csv file that has been ran through reducer.py AND merger.py. Cuts are highly reccomended but not required.

    - analysis/pid_accuracy_vs_user_accuracy.py:
      - This script outputs a single scatterplot. The x axis is the accuracy of the PID, the y axis is the accuracy of the people. Each dot represents one video. If a video is above the x=y diagonal, it means the humans outperformed the PID on that one video. This script will likely not be useful if analyzing hundreds of videos, as the dots will clutter everywhere. A 2-D histogram would be better suited instead.
      - Requites a csv file that has been ran through reducer.py. Cuts are highly reccomended but not required.

    - analysis/time_distrubution.py:
      - This script produces one histogram that shows how much time users spent on classifying videos.
      - Requires a csv file that has individual user classifications. Cuts should not be used.

  - How to use:
    - Step 1.) Request a classification export off of zooniverse. Find all of the votes you want to analyze and copy it over to a new csv file. This csv file should have thousands upon thousands of individual user votes.
    - At this point, you can use time_distrubution.py
    - Step 2.) (Optional but highly reccomended) If you want to implement a time cut, now is the time to do so with cuts/timecut.py
    - Step 3.) (Optional but highly reccomended) If you want to implement an accuracy cut, now is the time to do so with cuts/accuracy_cut.py
    - Step 4.) Now, reduce the file using reducer.py
    - Step 5.) (Optional but highly reccomended) If you want to implement an agreement cut, now is the time to do so with cuts/agreement_cut.py
    - At this point, you can use confusion_matrix.py and pid_accuracy_vs_user_accuracy.py
    - Step 6.) Now, use the merger.py file to combine your current csv file with another csv file that contains more information about each neutrino event.
    - At this point, you can use feature_tracker.py
