#!/bin/bash

# Create or clear the output file
> HasshList.txt

# Find all directories named "capture"
find . -type d -name "capture" | sort | while read capture_dir; do

    # Find all subdirectories inside each "capture" directory
    find "$capture_dir" -mindepth 1 -maxdepth 1 -type d | sort | while read sub_dir; do

        ssh_log="$sub_dir/ssh.log"

        # Check if ssh.log exists in the subdirectory
        if [[ -f "$ssh_log" ]]; then
            echo "Processing: $ssh_log"

            # Extract hasshServer values using zeek-cut and append to output
            zeek-cut server hasshServer < "$ssh_log" >> HasshList.txt
            zeek-cut hasshServerAlgorithms < "$ssh_log" >> HasshList.txt
            echo "" >> HasshList.txt
        else
            echo "No ssh.log in $sub_dir, skipping."
        fi

    done

done

echo "Done. Output saved to HasshList.txt"
