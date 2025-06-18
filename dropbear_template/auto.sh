#!/bin/bash

# List of COMMIT versions
COMMIT_FILE="commits.txt"
mapfile -t COMMITS < $COMMIT_FILE


# SSH login details
HOST="127.0.0.1"
SSH_USER="testuser"
SSH_PASSWORD="root"

# Output file for results
RESULT_FILE="results.txt"
echo "Dropbear Versions:" > $RESULT_FILE

# Loop through each COMMIT version
for COMMIT in "${COMMITS[@]}"; do
    echo "Processing COMMIT: $COMMIT"

    # Convert COMMIT to lowercase (avoid errors when naming Docker images)
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
    OUTPUT=$(./login.sh $HOST $SSH_USER $SSH_PASSWORD)

    # Extract the last line of the output
    LAST_LINE=$(echo "$OUTPUT" | grep -m 1 -E 'Dropbear (SSH )?client v[0-9]+(\.[0-9]+)*')
    #LAST_LINE="$OUTPUT"

    # Save the result to the file
    echo "$COMMIT: $LAST_LINE" >> $RESULT_FILE

    # Kill the container
    echo "Stopping container for $COMMIT..."
    docker kill $CONTAINER_ID

    echo "Finished processing $COMMIT."
    echo "-----------------------------------"
done

echo "All COMMITs processed! Results saved to $RESULT_FILE."