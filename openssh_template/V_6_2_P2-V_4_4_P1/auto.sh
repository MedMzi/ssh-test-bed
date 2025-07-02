#!/bin/bash

echo "Please enter your sudo password to begin (necessary for capture)..."
sudo -v

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
RESULT_FILE="results.txt"
echo "OpenSSH Versions:" > $RESULT_FILE

# Loop through each COMMIT version
for COMMIT in "${COMMITS[@]}"; do
    echo "Processing COMMIT: $COMMIT"

    # Convert COMMIT to lowercase (avoid errors)
    COMMIT_LOWER=$(echo "$COMMIT" | tr '[:upper:]' '[:lower:]')

    # Build the Docker image with the current COMMIT passed as a build argument
    echo "Building Docker image for $COMMIT..."
    docker build --build-arg COMMIT=$COMMIT -t openssh-$COMMIT_LOWER .

    # Remove old host key to avoid issues
    echo "Removing old host key for $HOST:2222..."
    ssh-keygen -f ~/.ssh/known_hosts -R "[${HOST}]:2222"

    # Run tcpdump in background
    PCAP_FILE="capture/${COMMIT_LOWER}.pcap"
    echo "Starting tcpdump, saving to $PCAP_FILE..."
    sudo tcpdump -i lo port 2222 -w "$PCAP_FILE" &
    TCPDUMP_PID=$!

    # Run the container
    echo "Running container for $COMMIT..."
    CONTAINER_ID=$(docker run --rm -d -p 2222:22 openssh-$COMMIT_LOWER)

    # Call login.sh and capture the output
    echo "Calling login.sh for $COMMIT..."
    OUTPUT=$(./login.sh $HOST $SSH_USER $SSH_PASSWORD)

    # Extract the last line of the output
    LAST_LINE=$(echo "$OUTPUT" | tail -n 1)

    # Save the result to the file
    echo "$COMMIT: $LAST_LINE" >> $RESULT_FILE

    # Kill the container
    echo "Stopping container for $COMMIT..."
    docker kill $CONTAINER_ID

    # Stop tcpdump
    echo "Stopping tcpdump..."
    sleep 2
    sudo kill -SIGINT $TCPDUMP_PID
    wait $TCPDUMP_PID 2>/dev/null

    echo "Finished processing $COMMIT."
    echo "-----------------------------------"
done

echo "All COMMITs processed! Results saved to $RESULT_FILE."