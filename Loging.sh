#!/bin/bash
#Sets date varibule
Time="$(date +%m-%d_%H:%M) "
#Runs zfs list | Sed remove first lie | Sed timstamp to each line | replases blank space the ,
zfs list -t snapshot -o name,used,refer | sed '1d' | sed -e "s/^/${Time}/" | tr -s '[:blank:]' ',' >> $1
