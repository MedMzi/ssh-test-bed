#!/bin/bash

# Base URL of the OpenSSH tags page
BASE_URL="https://github.com/ronf/asyncssh/tags"

# Output file for tags
TAG_FILE="commits.txt"

# Clear the output file
> $TAG_FILE

# Initialize the 'after' parameter
AFTER=""

while true; do
    echo "Fetching tags with after=$AFTER..."
    # Fetch the current page
    CONTENT=$(curl -s "${BASE_URL}?after=${AFTER}")

    # Extract tags from the page
    TAGS=$(echo "$CONTENT" | grep -oP '(?<=/ronf/asyncssh/releases/tag/)[^"]+')

    # Break the loop if no tags are found (end of pagination)
    if [[ -z "$TAGS" ]]; then
        echo "No more tags found. Exiting."
        break
    fi

    # Append filtered tags to the output file
    echo "$TAGS" | uniq >> $TAG_FILE

    # Update the 'after' parameter to the last tag fetched
    AFTER=$(echo "$TAGS" | tail -n 1)
done

# Display the results
echo "finished fetching tags."