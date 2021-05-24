# Loging
  This will create a massive file over time that may cause issues

  ## How to use
  ./Loging.sh where ever u want the output to be setup to use .csv files.

# Scrubing 
  Work in progress. Its ment to runs the zfs scrub comand and notify once its done.

# Snapshot
  This is desined to take snapshots of a zfs dataset It Timestamps the dataset and logs it its setup to save and many as you want. Its set up with discord notifications for problems

  ## How to use
  ./ZFS_Snapshot.sh 'Name of snapshot' 'Name of pool' 'Name of dataset' 'Log file' 'Number of Backps' 'Discord URL'
