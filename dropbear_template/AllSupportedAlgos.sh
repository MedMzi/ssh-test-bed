#!/bin/bash

# List of COMMIT versions
COMMIT_FILE="commits.txt"
mapfile -t COMMITS < $COMMIT_FILE

#COMMITS=(
#    "V_10_0_P2"
#    "V_10_0_P1"
#)

# SSH login details
HOST="127.0.0.1"
SSH_USER="testuser"
SSH_PASSWORD="root"

# Output file for results
RESULT_FILE="AllSupportedAlgos.json"

# Loop through each COMMIT version
for COMMIT in "${COMMITS[@]}"; do
    echo "Processing COMMIT: $COMMIT"

    # Convert COMMIT to lowercase (avoid errors)
    COMMIT_LOWER=$(echo "$COMMIT" | tr '[:upper:]' '[:lower:]')

    # Build the Docker image with the current COMMIT passed as a build argument
    echo "Building Docker image for $COMMIT..."
    docker build --build-arg COMMIT=$COMMIT -t dropbear-$COMMIT_LOWER .

    # Remove old host key to avoid issues
    echo "Removing old host key for $HOST:2222..."
    ssh-keygen -f ~/.ssh/known_hosts -R "[${HOST}]:2222"

    # Run the container
    echo "Running container for $COMMIT..."
    CONTAINER_ID=$(docker run --rm -d -p 2222:22 dropbear-$COMMIT_LOWER)

    # Call login.sh and capture the output
    echo "Calling login.sh for $COMMIT..."
    #OUTPUT=$(./AllVersLogin.sh $HOST $SSH_USER $SSH_PASSWORD)
    #OUTPUT=$(echo "$OUTPUT" | tr -d '\r')
    RAW_OUTPUT=$(./AllVersLogin.sh $HOST $SSH_USER $SSH_PASSWORD)
    OUTPUT=$(echo "$RAW_OUTPUT" | awk '/password:/,0' | tail -n +2 | tr -d '\r')


    # Extract all algorithm sections into variables
    KEX=$(echo "$OUTPUT" | awk '/^kex:\r?$/ {flag=1; next} /testuser@/ {flag=0} flag')
    CIPHER=$(echo "$OUTPUT" | awk '/^cipher:\r?$/ {flag=1; next} /testuser@/ {flag=0} flag')
    MAC=$(echo "$OUTPUT" | awk '/^mac:\r?$/ {flag=1; next} /testuser@/ {flag=0} flag')
    COMPRESSION=$(echo "$OUTPUT" | awk '/^compression:\r?$/ {flag=1; next} /testuser@/ {flag=0} flag')
    KEY=$(echo "$OUTPUT" | awk '/^key:\r?$/ {flag=1; next} /testuser@/ {flag=0} flag')


    # Build JSON string
    LAST_LINE=$(jq -n \
    --argjson kex       "$(printf '%s\n' "$KEX" | jq -R . | jq -s .)" \
    --argjson cipher    "$(printf '%s\n' "$CIPHER" | jq -R . | jq -s .)" \
    --argjson mac       "$(printf '%s\n' "$MAC" | jq -R . | jq -s .)" \
    --argjson compression "$(printf '%s\n' "$COMPRESSION" | jq -R . | jq -s .)" \
    --argjson key       "$(printf '%s\n' "$KEY" | jq -R . | jq -s .)" \
    '{kex: $kex, cipher: $cipher, mac: $mac, compression: $compression, key: $key}'
    )

    # Save the result to the file
    ALL_JSON+="\"$COMMIT\": $LAST_LINE,"$'\n'
    FINAL_JSON="{${ALL_JSON%,*}}"
    echo "$FINAL_JSON" > "$RESULT_FILE"

    # Kill the container
    echo "Stopping container for $COMMIT..."
    docker kill $CONTAINER_ID

    echo "Finished processing $COMMIT."
    echo "-----------------------------------"
done

echo "All COMMITs processed! Results saved to $RESULT_FILE."