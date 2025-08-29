# SSH Test Bed

This repository provides a comprehensive SSH test bed including various implementations of SSH. It allows testing different SSH versions, capturing network traffic, and fingerprinting supported algorithms.

---

## Directory Structure

- **{implementation}_template/**  
  Contains the Dockerfile for each SSH implementation.  
  For OpenSSH, there are additional subdirectories covering a range of versions.

- **fetch_tags.sh**  
  Fetches tags from the repository and saves them in `commits.txt` for later use during the build phase.

- **auto.sh**  
  Builds and runs the Dockerfile for a given version range, capturing output in `.pcap` files inside `capture/`.

- **OpenSSH / Dropbear Tools**  
  - **allsupportedalgos.sh** – Extracts supported algorithms by scanning the binary for recognizable names.  
  - **allsverslogin.sh** – Uses `expect` to test algorithm support across versions.  
  - **dropbearQ.sh** – Helper script for Dropbear algorithm extraction.  
  - **auto_checker.sh (OpenSSH only)** – More robust algorithm testing method, checking each algorithm individually.

- **Openssh_comparison/**  
  Compares algorithms supported versus advertised by OpenSSH over time using a Python script.  
  Timeline graphs visualize when each algorithm was introduced or became default.

- **Reference.json**  
  Contains a comprehensive list of SSH algorithms supported by all implementations, combining our results and IANA specifications.

- **Hasshlist.sh**  
  Parses implementation subdirectories and uses captured `.pcap` files to generate a complete list of `hassh` server fingerprints and supported algorithms.  
  - **datepull.sh** and **mergeandorder.py** – Handle date annotations and ordering of results.

- **Payloads**  
  The repository contains 13 different `{name}_payload.bin` files used in testing.  
  - **temp.py** – Creates some payloads; others are taken directly from real traffic.

---

## Fingerprinting Tool

To test the SSH fingerprinting tool:

```bash
python3 ssh_fingerprinting.py <docker_image> <container_port>
```
*results are currently appended to stateMachine_results/results.txt*
