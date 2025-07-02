#!/bin/bash

for pcapfile in ./*.pcap; do
    base=$(basename "$pcapfile" .pcap)
    echo "Processing $pcapfile..."

    # Create a directory for the logs
    mkdir -p "$base"

    # Run Zeek on the pcap (outputs logs in current dir)
    zeek -C -r "$pcapfile" local

    # Move all .log files into the directory
    for logfile in *.log; do
        if [ -f "$logfile" ]; then
            mv "$logfile" "$base/"
        fi
    done

    echo "Logs moved to directory $base"
done

echo "All pcaps processed."


