#!/bin/bash

temp1='Storage'
temp2='./zpool.txt'


#scrubs the spesified ZFS Pool
zpool scrub $temp1
#dosnothing gor x seconds
sleep 5
#Gets spesified ZFS Pool status
zpool status -v $temp1 > $temp2
while $X eq 1; do
  sleep $amount
  if "$(grep 'scan: scrub in progress' $temp2)" eq 0; then
    echo "test"
    elif "$(grep 'scan: scrub in progress' $temp2)" eq 1; then
    x=0
    cp temp2 to permnet file
  fi
done


pool: Media
 state: ONLINE
  scan: scrub repaired 0B in 0 days 00:04:03 with 0 errors on Tue May  4 12:48:15 2021
config:

        NAME                                           STATE     READ WRITE CKSUM
        Media                                          ONLINE       0     0     0
          mirror-0                                     ONLINE       0     0     0
            nvme-INTEL_SSDPEKNW010T8_BTNH0015088S1P0B  ONLINE       0     0     0
            nvme-INTEL_SSDPEKNW010T8_BTNH005407HX1P0B  ONLINE       0     0     0

errors: No known data errors

sudo zpool status Storage 
  pool: Storage
 state: ONLINE
  scan: resilvered 5.52G in 0 days 00:10:31 with 0 errors on Tue Apr 27 14:50:50 2021
config:

