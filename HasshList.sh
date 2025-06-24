#!/bin/bash

# Create or clear the output files (text and CSV)
> HasshList.txt
echo "Server,HasshServer,KEX,Encryption,MAC,Compression" > HasshList.csv

# Find all directories named "capture"
find . -type d -name "capture" | sort | while read capture_dir; do

    # Find all subdirectories inside each "capture" directory
    find "$capture_dir" -mindepth 1 -maxdepth 1 -type d | sort | while read sub_dir; do

        ssh_log="$sub_dir/ssh.log"

        # Check if ssh.log exists in the subdirectory
        if [[ -f "$ssh_log" ]]; then
            echo "Processing: $ssh_log"

            # Extract fields
            server_list=$(zeek-cut server < "$ssh_log")
            hassh_list=$(zeek-cut hasshServer < "$ssh_log")
            algos_list=$(zeek-cut hasshServerAlgorithms < "$ssh_log")

            # Combine all three outputs line by line
            paste <(echo "$server_list") <(echo "$hassh_list") <(echo "$algos_list") | while IFS=$'\t' read -r server hasshServer algos; do
                IFS=";" read -r kex enc mac comp <<< "$algos"

                # Write to plain text file
                {
                    echo "$server   $hasshServer"
                    echo "KEX: $kex"
                    echo "Encryption: $enc"
                    echo "MAC: $mac"
                    echo "Compression: $comp"
                    echo ""
                } >> HasshList.txt

                # Write to CSV file
                echo "\"$server\",\"$hasshServer\",\"$kex\",\"$enc\",\"$mac\",\"$comp\"" >> HasshList.csv
            done

        else
            echo "No ssh.log in $sub_dir, skipping."
        fi

    done

done

echo "Done. Outputs saved to HasshList.txt and HasshList.csv"