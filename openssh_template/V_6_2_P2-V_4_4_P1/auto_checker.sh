#!/bin/bash

# Input files
COMMIT_FILE="commits.txt"
REFERENCE_FILE="Reference.json"
OUTPUT_JSON="Supported_Algos.json"

# Read commits
mapfile -t COMMITS < "$COMMIT_FILE"

# SSH login credentials
HOST="127.0.0.1"
SSH_USER="testuser"
SSH_PASSWORD="root"

# Init output
echo "{}" > "$OUTPUT_JSON"

# Loop through all commits
for COMMIT in "${COMMITS[@]}"; do
    echo "Processing COMMIT: $COMMIT"
    COMMIT_LOWER=$(echo "$COMMIT" | tr '[:upper:]' '[:lower:]')

    # Build and run Docker
    echo "Building image..."
    docker build --build-arg COMMIT="$COMMIT" -t openssh-"$COMMIT_LOWER" .

    echo "Cleaning old SSH key..."
    ssh-keygen -f ~/.ssh/known_hosts -R "[${HOST}]:2222"

    echo "Running container..."
    CONTAINER_ID=$(docker run --rm -d -p 2222:22 openssh-"$COMMIT_LOWER")

    # Prepare temporary JSON content for this commit
    TEMP_JSON="{}"

    # Loop through each key in Reference.json (e.g., KexAlgorithms, Ciphers, etc.)
    for KEY in $(jq -r 'keys[]' "$REFERENCE_FILE"); do
        echo "Checking $KEY..."
        ALGO_ARRAY=$(jq -r --arg key "$KEY" '.[$key][]' "$REFERENCE_FILE")

        SUPPORTED_ALGOS=()

        while IFS= read -r ALGO; do
            echo "  Trying $KEY: $ALGO"

            OUTPUT=$(./login_checker.sh "$HOST" "$SSH_USER" "$SSH_PASSWORD" "$KEY" "$ALGO")
            #echo "$OUTPUT"

            if echo "$OUTPUT" | grep -q "betise: Name or service not known"; then
                #echo "match!"
                SUPPORTED_ALGOS+=("$ALGO")
            fi

        done <<< "$ALGO_ARRAY"

        # Convert bash array to JSON array properly using jq
        SUPPORTED_JSON=$(printf '%s\n' "${SUPPORTED_ALGOS[@]}" | jq -R . | jq -s .)

        # Add to temporary JSON for this commit
        TEMP_JSON=$(echo "$TEMP_JSON" | jq --arg key "$KEY" --argjson val "$SUPPORTED_JSON" '. + {($key): $val}')

    done

    # Merge this commit's results into the final output JSON
    jq --arg commit "$COMMIT_LOWER" --argjson data "$TEMP_JSON" '. + {($commit): $data}' "$OUTPUT_JSON" > tmp.json && mv tmp.json "$OUTPUT_JSON"

    echo "Stopping container..."
    docker kill "$CONTAINER_ID"

    echo "Finished $COMMIT"
    echo "-----------------------------"
done

echo "All commits processed. Output saved to $OUTPUT_JSON."

echo "Manually updating kex for the last few verisons that don't allow -o option"
python3 ManualUpdater.py
