import json
import re
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from collections import defaultdict

def clamp(val, min_val, max_val):
    return max(min_val, min(val, max_val))

def parse_version(version_str):
    # Split by '.' and convert to int
    return tuple(map(int, version_str.split('.')))

def load_versioned_entries(json_file, ssh_impl='openssh', alg_type='KEX'):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    ssh_impl_lower = ssh_impl.lower()
    entries = []

    for tag, entry in data.items():
        if not isinstance(entry, dict):
            continue

        server = entry.get('Server', '')
        if ssh_impl_lower not in server.lower():
            continue

        # Match version from Server string
        if ssh_impl_lower == 'wolfssh':
            match = re.search(r'wolfSSHv(\d+\.\d+\.\d+)', server, re.IGNORECASE)
        else:
            # The version might be x.y or x.y.z — allow optional third part
            match = re.search(rf'{ssh_impl_lower}[_-]?(\d+\.\d+(?:\.\d+)?)', server, re.IGNORECASE)

        if not match:
            continue

        version_str = match.group(1)
        version_tuple = parse_version(version_str)

        alg_list = entry.get(alg_type, [])
        if not isinstance(alg_list, list):
            # Safety check if alg_type is missing or malformed
            alg_list = []

        entries.append((version_tuple, version_str, alg_list, tag))

    # Sort entries by version tuple
    entries.sort(key=lambda x: x[0])
    return entries

def plot_algorithm_timeline(versioned_entries, alg_type='KEX', ssh_impl='openssh'):
    # Label with tag and version: "tag (version)"
    versions = [f"{tag} ({version_str})" for _, version_str, _, tag in versioned_entries]

    # Get all unique algorithms across all entries
    all_algos = sorted(set(alg for _, _, algs, _ in versioned_entries for alg in algs))
    algo_index = {alg: i for i, alg in enumerate(all_algos)}

    width = clamp(len(versions) * 0.5, 10, 40)     # X-axis width depends on version count
    height = clamp(len(all_algos) * 0.4, 6, 30)    # Y-axis height depends on alg count

    fig, ax = plt.subplots(figsize=(width, height))

    algo_positions = defaultdict(list)

    for x_idx, (_, _, algos, _) in enumerate(versioned_entries):
        for alg in algos:
            algo_positions[alg].append(x_idx)

    # Draw lines and markers per algorithm
    for alg, x_indices in algo_positions.items():
        y_val = algo_index[alg]
        x_vals = []
        y_vals = []

        for i, x in enumerate(x_indices):
            # Break line if non-continuous
            if i > 0 and x_indices[i] != x_indices[i-1] + 1:
                ax.plot(x_vals, y_vals, color='tab:blue', linewidth=2)
                x_vals, y_vals = [], []

            x_vals.append(x)
            y_vals.append(y_val)

        # Final segment
        if x_vals:
            ax.plot(x_vals, y_vals, color='tab:blue', linewidth=2)

        # Mark each version where algorithm appears
        for x in x_indices:
            ax.plot(x, y_val, 's', color='dodgerblue', markersize=8)

    ax.set_xticks(range(len(versions)))
    ax.set_xticklabels(versions, rotation=90, fontsize=8)
    ax.set_yticks(range(len(all_algos)))
    ax.set_yticklabels(all_algos, fontsize=8)

    ax.set_xlabel("Tag (Version)")
    ax.set_ylabel(f"{alg_type} Algorithms")
    ax.set_title(f"{ssh_impl.upper()} {alg_type} Algorithm Timeline")
    ax.grid(True, linestyle=':', alpha=0.5)

    plt.tight_layout()
    plt.savefig(f"timeline_graphs/{ssh_impl}_{alg_type}_timeline.png", dpi=300)
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ssh_timeline.py <ssh_impl> <algorithm_type>")
        print("Example: python ssh_timeline.py openssh Encryption")
        sys.exit(1)

    ssh_impl = sys.argv[1]
    alg_type = sys.argv[2]

    valid_types = ['KEX', 'Encryption', 'MAC', 'HostKeyAlgorithms', 'Compression']
    if alg_type not in valid_types:
        print(f"Invalid algorithm type. Choose from: {', '.join(valid_types)}")
        sys.exit(1)

    entries = load_versioned_entries('HasshList.json', ssh_impl, alg_type)
    if not entries:
        print("No data found for that SSH implementation.")
        sys.exit(1)

    plot_algorithm_timeline(entries, alg_type, ssh_impl)
