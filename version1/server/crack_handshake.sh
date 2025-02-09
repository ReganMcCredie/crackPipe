#!/bin/sh
repeat_seconds=4

# Create fileBin directory if it doesnt already exist
[ -d fileBin ] || mkdir fileBin
cd fileBin/
while true
do
    for file in $(ls)
        if [ $file = "targetBSSID.txt" ]; then
            aircrack-ng -b targetBSSID.txt handshake-01.cap > output_key.txt
            rm -f targetBSSID.txt targetESSID.txt handshake-01.cap
        fi
    sleep $repeat_seconds
done