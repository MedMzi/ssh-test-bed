#!/bin/bash

# Create or clear output files
> HasshList.txt
echo "Server,HasshServer,KEX,Encryption,MAC,Compression,Host Key Algorithms" > HasshList.csv
> HasshList.tmpjson

# Function to convert comma-separated strings to JSON arrays
json_array() {
  local input="$1"
  if [[ -z "$input" ]]; then
    echo "[]"
  else
    IFS=',' read -ra items <<< "$input"
    echo "["
    for i in "${!items[@]}"; do
      printf '    "%s"' "${items[i]}"
      if [[ $i -lt $((${#items[@]} - 1)) ]]; then
        echo ","
      else
        echo
      fi
    done
    echo "  ]"
  fi
}

# Find all "capture" directories
find . -type d -name "capture" | sort | while read capture_dir; do
  find "$capture_dir" -mindepth 1 -maxdepth 1 -type d | sort | while read sub_dir; do

    ssh_log="$sub_dir/ssh.log"

    if [[ -f "$ssh_log" ]]; then
      echo "Processing: $ssh_log"

      server_list=$(zeek-cut server < "$ssh_log")
      hassh_list=$(zeek-cut hasshServer < "$ssh_log")
      algos_list=$(zeek-cut hasshServerAlgorithms < "$ssh_log")
      sshka_list=$(zeek-cut sshka < "$ssh_log")

      paste <(echo "$server_list") <(echo "$hassh_list") <(echo "$algos_list") <(echo "$sshka_list") | while IFS=$'\t' read -r server hasshServer algos sshka; do
        IFS=";" read -r kex enc mac comp <<< "$algos"

        # Write to plain text
        {
          echo "$server   $hasshServer"
          echo "KEX: $kex"
          echo "Encryption: $enc"
          echo "MAC: $mac"
          echo "Compression: $comp"
          echo "Host Key Algorithms: $sshka"
          echo ""
        } >> HasshList.txt

        # Write to CSV
        echo "\"$server\",\"$hasshServer\",\"$kex\",\"$enc\",\"$mac\",\"$comp\",\"$sshka\"" >> HasshList.csv

        # Write to JSON temp file
        {
          echo "  {"
          echo "    \"Server\": \"${server}\","
          echo "    \"HasshServer\": \"${hasshServer}\","
          echo "    \"KEX\": $(json_array "$kex"),"
          echo "    \"Encryption\": $(json_array "$enc"),"
          echo "    \"MAC\": $(json_array "$mac"),"
          echo "    \"Compression\": $(json_array "$comp"),"
          echo "    \"HostKeyAlgorithms\": $(json_array "$sshka")"
          echo "  }"
        } >> HasshList.tmpjson

      done
    else
      echo "No ssh.log in $sub_dir, skipping."
    fi
  done
done

# Join JSON entries into a JSON array
echo "[" > HasshList.json
awk 'NR==1{print $0; next} {print "," $0}' RS='}\n' ORS='}\n' HasshList.tmpjson >> HasshList.json
echo "]" >> HasshList.json

# Pretty-print final JSON (overwrite original)
jq '.' HasshList.json > HasshList.tmp && mv HasshList.tmp HasshList.json

# Clean up
rm -f HasshList.tmpjson

echo "Done. Outputs saved to HasshList.txt, HasshList.csv, and HasshList.json"
