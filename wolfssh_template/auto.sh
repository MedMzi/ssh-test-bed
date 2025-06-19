#!/bin/bash

# List of COMMIT versions
COMMIT_FILE="commits.txt"

#COMMITS=(
#    "V_10_0_P2"
#    "V_10_0_P1"
#)

# SSH login details
HOST="127.0.0.1"
SSH_USER="testuser"
SSH_PASSWORD="root"

# Output file for results
RESULT_FILE="results.txt"
echo "WolfSSH Versions:" > $RESULT_FILE

# Loop through each COMMIT version
while IFS= read -r line || [ -n "$line" ]; do
    # Split line into COMMIT and WOLFSSL_VERSION
    COMMIT=$(echo "$line" | awk '{print $1}')
    WOLFSSL_VERSION=$(echo "$line" | awk '{print $2}')
    
    echo "Processing COMMIT: $COMMIT with WOLFSSL_VERSION: $WOLFSSL_VERSION"

    # Convert COMMIT to lowercase
    COMMIT_LOWER=$(echo "$COMMIT" | tr '[:upper:]' '[:lower:]')

    # Build the Docker image with both build arguments
    echo "Building Docker image for $COMMIT..."
    docker build \
        --build-arg COMMIT="$COMMIT" \
        --build-arg WOLFSSL_VERSION="$WOLFSSL_VERSION" \
        -t "wolfssh-$COMMIT_LOWER" .

    # Remove old host key to avoid issues
    echo "Removing old host key for $HOST:2222..."
    ssh-keygen -f ~/.ssh/known_hosts -R "[${HOST}]:2222"

    # Run the container
    echo "Running container for $COMMIT..."
    CONTAINER_ID=$(docker run --rm -d -p 2222:11111 wolfssh-$COMMIT_LOWER)

    # Call login.sh and capture the output
    echo "Calling login.sh for $COMMIT..."
    OUTPUT=$(./login.sh $HOST $SSH_USER $SSH_PASSWORD)

    # Extract the last line of the output
    LAST_LINE=$(echo "$OUTPUT" | grep "#define")

    # Save the result to the file
    echo "$COMMIT: $LAST_LINE" >> $RESULT_FILE

    # Kill the container
    echo "Stopping container for $COMMIT..."
    docker kill $CONTAINER_ID

    echo "Finished processing $COMMIT."
    echo "-----------------------------------"
done < "$COMMIT_FILE"

echo "All COMMITs processed! Results saved to $RESULT_FILE."