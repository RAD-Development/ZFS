#!/bin/bash

#Sets file name
Time="$1"_$(date +%m-%d_%H:%M)

Msg_Dis() {
	## formats message
	msg_content=\"$1\"
	## Messages diccord
	curl -H "Content-Type: application/json" -X POST -d "{\"content\": $msg_content}" $2
}

if [[ $(wc -w < "$4") -ge "$5" ]]; then
	Old=$(head -n 1 "$4")
	#Destroys old snapshot
	if [[ $(zfs destroy "$2"/"$3"@"$Old") -eq 0 ]]; then
		#Deleats old snapshot  name after destroyed
		sed -i '1d' $4

	else
		#Msges discord if destroy fails
		Msg_Dis "@everyone "$2"/"$3" destroy Failed $?" "$6"
	fi
fi
	echo $Time"" >> $4

#Creats new Snapshot and send discord ms if it fails
if [[ $(zfs snapshot "$2"/"$3"@"$Time") -ne 0 ]]; then
	Msg_Dis "@everyone "$2"/"$3" Failed $?" "$6"
fi 
