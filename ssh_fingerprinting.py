#!/usr/bin/env python3
import os
import socket
import select
import time
import subprocess
from graphviz import Digraph
import statemachine
from itertools import product
import hashlib
import json
import sys

if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} <docker_image> <container_port>")
    sys.exit(1)

HOST = "localhost"
PORT = 2222
MESSAGE_DIR = "."  # directory with .bin payloads
SEQUENCE_LENGTH = 3
NUM_SEQUENCES = 10
banner = "SSH-2.0-betiseSSH\r\n"

container_port = int(sys.argv[2]) 
docker_image = sys.argv[1] 


# Load binary messages into memory
messages = {}
for fname in os.listdir(MESSAGE_DIR):
    if fname.endswith(".bin"):
        with open(os.path.join(MESSAGE_DIR, fname), "rb") as f:
            messages[fname.removesuffix("_payload.bin")] = f.read()
print(f"Loaded {len(messages)} messages.")

# Docker container tracking
docker_container_id = None

def kill_docker():
    global docker_container_id
    if docker_container_id:
        print(f"[System] Stopping old Docker container {docker_container_id}")
        subprocess.run(["docker", "kill", docker_container_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["docker", "rm", docker_container_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        docker_container_id = None



def start_docker():
    """Start docker container detached. If an old container id exists, remove it first."""
    global docker_container_id
    kill_docker()  # ensure no old container is running

    print("[System] Starting Docker container...")
    # detached (-d), publish 2222:22, do NOT use --rm so container remains if it exits
    result = subprocess.run(
        ["docker", "run", "-d", "-p", f"2222:{container_port}", docker_image],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"Failed to start docker: {result.stderr.strip()}")
    docker_container_id = result.stdout.strip()
    print(f"[System] Docker started: {docker_container_id}")
    # give sshd a short time to come up
    time.sleep(1)

def connect_to_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((HOST, PORT))
    return sock


skip = False
def send_banner(sock):
    global skip
    server_banner = sock.recv(4096).decode(errors='ignore').strip()
    print(f"[Client] Received server banner: {server_banner}")

    # Send banner and receive server banner
    print(f"[Client] Sending banner: {banner.strip()}")
    sock.sendall(banner.encode())
    if not skip:
        try:
            kex = sock.recv(4096)
            print(f"[Client] Received KEX init message ({len(kex)} bytes)")
        except TimeoutError:
            print("[Client] Timeout waiting for KEX init message (probably in banner)")
            skip = True
    


#run_all_sequences(messages)
#kill_docker()

#x = list(product(["A", "B"], repeat=2))[0]
#for sequence in product(messages.keys(), repeat=2)

 


def run_one_sequence(messages, seq, sm, state):
    start_docker()
    sock = connect_to_server()
    send_banner(sock)
    result = []
    ancestry = hashlib.sha256()
    for i, msg_name in enumerate(seq):
        if i != len(seq) - 1:        
            ancestry.update(msg_name.encode())
        else:
            ancestry.update(b"final")

        payload = messages[msg_name]
        print(f"[Client] Sending message: {msg_name} ({len(payload)} bytes)")
        sock.sendall(payload)

        ready, _, _ = select.select([sock], [], [], 0.5)
        if ready:
            response = sock.recv(4096)
            if response == b'': # FIN
                result.append(f"terminated")
                newState = sm.add_state(f"terminated\n{ancestry.hexdigest()}")
                state.add_transition(newState, msg_name)
                break
            else:   #payload
                result.append(f"{response[5]}")
                newState = sm.add_state(f"{response[5]}\n{ancestry.hexdigest()}")
                state.add_transition(newState, msg_name)
                state = newState
        else:   # no response likely ACK
            result.append("no response")
            newState = sm.add_state(f"no response\n{ancestry.hexdigest()}")
            state.add_transition(newState, msg_name)
            state = newState
    
    
    sock.close()
    kill_docker()
    print(f"[Client] Finished sequence: {seq} with result: {result}")
    return result

def run_all_sequences(messages):
    sm = statemachine.StateMachine()
    Start = sm.add_state("Start")
    results = []
    i= 0
    for sequence in product(messages.keys(), repeat=2):
        print(f"[System] Running sequence: {sequence}")
        results += run_one_sequence(messages, sequence, sm, Start)
        i += 1
        print(f"*******{i}/{len(list(product(messages.keys(), repeat=2)))}*******")

    sm.export_graphviz(filename = f"stateMachine_results/{docker_image}", view=True)
    return results

results = run_all_sequences(messages)
encoded = json.dumps(results).encode()
fingerprint = hashlib.sha256(encoded).hexdigest()

print("Hash of the result for ",  docker_image , " is " , fingerprint)

with open("stateMachine_results/results.txt", "a") as f:  
    f.write(f"{docker_image} = {fingerprint}\n")
