#!/bin/bash

# Temp file to collect JSON entries
TEMP_JSON=$(mktemp)

# Empty the temp file
> "$TEMP_JSON"

find . -type f -name 'commits.txt' | while read -r COMMIT_FILE; do
    echo "Processing: $COMMIT_FILE"

    DIR=$(dirname "$COMMIT_FILE")
    PREFIX=$(echo "$COMMIT_FILE" | grep -oP '[^/]+_template' | head -1 | sed 's/_template$//')

    DOCKERFILE=$(find "$DIR" -maxdepth 1 -type f -iname 'dockerfile' | head -n1)

    if [[ -z "$DOCKERFILE" ]]; then
        echo "No dockerfile found in $DIR, skipping."
        continue
    fi

    if [[ "$DOCKERFILE" == *wolfssh* ]]; then
        REPO_URL=$(grep -oP 'git clone[^\n]*https?://[^\s]+' "$DOCKERFILE" | sed -n 2p | grep -oP 'https?://[^\s]+')
    else
        REPO_URL=$(grep -oP 'git clone[^\n]*https?://[^\s]+' "$DOCKERFILE" | head -n1 | grep -oP 'https?://[^\s]+')
    fi

    if [[ -z "$REPO_URL" ]]; then
        echo "No git repo URL found in $DOCKERFILE, skipping."
        continue
    fi

    while read -r TAG_ORIGINAL; do
        [[ -z "$TAG_ORIGINAL" ]] && continue
        TAG_ORIGINAL=$(echo "$TAG_ORIGINAL" | awk '{print $1}')
        TAG_LOWER=$(echo "$TAG_ORIGINAL" | tr '[:upper:]' '[:lower:]')

        TMP_DIR=$(mktemp -d)
        git clone --depth=1 --branch "$TAG_ORIGINAL" "$REPO_URL" "$TMP_DIR" || { echo "Failed to clone $REPO_URL branch $TAG_ORIGINAL"; rm -rf "$TMP_DIR"; continue; }

        COMMIT_DATE=$(git -C "$TMP_DIR" log -1 --format=%cI)

        # Append JSON entry to temp file (no trailing comma here)
        echo "\"${PREFIX}_${TAG_LOWER}\": { \"date\": \"$COMMIT_DATE\" }," >> "$TEMP_JSON"

        rm -rf "$TMP_DIR"
    done < "$COMMIT_FILE"
done

# Remove trailing comma from last line
sed -i '$ s/,$//' "$TEMP_JSON"

# Wrap in braces and save to final json file
echo "{" > commit_dates.json
cat "$TEMP_JSON" >> commit_dates.json
echo "}" >> commit_dates.json

# Remove temp file
rm "$TEMP_JSON"
