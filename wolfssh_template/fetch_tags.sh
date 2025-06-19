#!/bin/bash

# Base URL of the OpenSSH tags page
BASE_URL="https://github.com/wolfSSL/wolfssh/tags"

# Output file for tags
TAG_FILE="commits.txt"
WOLFSSL="v5.8.0-stable"

# Clear the output file
> $TAG_FILE

# Initialize the 'after' parameter
AFTER=""

while true; do
    echo "Fetching tags with after=$AFTER..."
    # Fetch the current page
    CONTENT=$(curl -s "${BASE_URL}?after=${AFTER}")

    # Extract tags from the page
    TAGS=$(echo "$CONTENT" | grep -oP '(?<=/wolfSSL/wolfssh/releases/tag/)[^"]+')

    # Break the loop if no tags are found (end of pagination)
    if [[ -z "$TAGS" ]]; then
        echo "No more tags found. Exiting."
        break
    fi

    while IFS= read -r tag; do
        # ending the loop at this version
        if [[ "$tag" == "v1.4.13-stable" ]]; then
            echo "$tag $WOLFSSL" >> "$TAG_FILE"
            echo "Reached v1.4.13-stable. Stopping."
            break 2  # Exit both inner and outer loop
        fi

        # Check if we need to switch the tag format
        if [[ "$tag" == "v1.4.14-stable" ]]; then
            WOLFSSL="v5.0.0-stable"
        fi
        echo "$tag $WOLFSSL" >> "$TAG_FILE"

    done <<< "$TAGS"

    # Update the 'after' parameter to the last tag fetched
    AFTER=$(echo "$TAGS" | tail -n 1)
done

# Remove duplicate lines from the tag file
awk '!seen[$0]++' "$TAG_FILE" > tmpfile && mv tmpfile "$TAG_FILE"


# Display the results
echo "finished fetching tags."