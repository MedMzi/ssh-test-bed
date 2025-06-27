#!/bin/bash

# Target URL
URL="https://git.libssh.org/projects/libssh.git/refs/tags"

# Output file
OUTPUT_FILE="commits.txt"

# Step 1: Fetch the HTML
HTML=$(curl -s "$URL")

# Step 2: Extract tag names using grep and sed
echo "$HTML" | \
grep -oE "<a href='/projects/libssh.git/tag/\?h=[^']+'>([^<]+)</a>" | \
sed -E "s|.*'>([^<]+)</a>|\1|" > "$OUTPUT_FILE"

# Final output
echo "Tags saved to $OUTPUT_FILE:"
cat "$OUTPUT_FILE"
