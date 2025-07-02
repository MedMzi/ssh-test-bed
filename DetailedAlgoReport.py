import json
from collections import defaultdict
import re
from datetime import datetime

def analyze_ssh_evolution(json_file, ssh_impl='openssh'):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Filter for selected SSH implementation entries only
    ssh_impl_lower = ssh_impl.lower()
    ssh_entries = [entry for entry in data if ssh_impl_lower in entry['Server'].lower()]
    
    print(f"=== ANALYZING {len(ssh_entries)} {ssh_impl.upper()} ENTRIES ===\n")
    
    # Extract version numbers and sort chronologically
    versioned_entries = []
    for entry in ssh_entries:
        server_string = entry['Server']
        # Try to extract version number (e.g., "OpenSSH_8.9" -> 8.9)
        version_match = re.search(r'{0}[_-]?(\d+\.\d+)'.format(ssh_impl_lower), server_string, re.IGNORECASE)
        if version_match:
            version = float(version_match.group(1))
            versioned_entries.append((version, entry))
    
    # Sort by version
    versioned_entries.sort(key=lambda x: x[0])
    
    if versioned_entries:
        print("Version range:", f"{versioned_entries[0][0]} to {versioned_entries[-1][0]}")
    else:
        print("No versioned entries found for", ssh_impl.upper())
        return
    
    print()
    
    algorithm_types = ['KEX', 'Encryption', 'MAC', 'Compression', 'HostKeyAlgorithms']
    
    for alg_type in algorithm_types:
        print(f"=== {alg_type.upper()} EVOLUTION ===")
        analyze_algorithm_evolution(versioned_entries, alg_type)
        print()

def analyze_algorithm_evolution(versioned_entries, alg_type):
    # Track when each algorithm first appears and last appears
    algorithm_lifecycle = defaultdict(lambda: {'first': None, 'last': None, 'versions': []})
    
    # Build lifecycle data
    for version, entry in versioned_entries:
        algorithms = entry.get(alg_type, [])
        for alg in algorithms:
            if algorithm_lifecycle[alg]['first'] is None:
                algorithm_lifecycle[alg]['first'] = version
            algorithm_lifecycle[alg]['last'] = version
            algorithm_lifecycle[alg]['versions'].append(version)
    
    # Categorize algorithms by their lifecycle patterns
    categories = {
        'legacy': [],      # Present in very old versions, disappeared
        'stable': [],      # Present across most/all versions
        'modern': [],      # Appeared in newer versions, still present
        'deprecated': [],  # Present in middle versions, disappeared
        'experimental': [] # Appeared briefly then disappeared
    }
    
    min_version = versioned_entries[0][0]
    max_version = versioned_entries[-1][0]
    version_span = max_version - min_version
    
    for alg, lifecycle in algorithm_lifecycle.items():
        first_ver = lifecycle['first']
        last_ver = lifecycle['last']
        version_count = len(lifecycle['versions'])
        total_versions = len(versioned_entries)
        
        # Calculate presence ratio
        presence_ratio = version_count / total_versions
        
        # Categorize based on lifecycle pattern
        if first_ver <= min_version + version_span * 0.2:  # Started in first 20% of timeline
            if last_ver >= max_version - version_span * 0.2:  # Still present in last 20%
                if presence_ratio >= 0.7:
                    categories['stable'].append((alg, first_ver, last_ver, presence_ratio))
                else:
                    categories['deprecated'].append((alg, first_ver, last_ver, presence_ratio))
            else:  # Disappeared
                categories['legacy'].append((alg, first_ver, last_ver, presence_ratio))
        else:  # Started later
            if last_ver >= max_version - version_span * 0.2:  # Still present
                categories['modern'].append((alg, first_ver, last_ver, presence_ratio))
            else:  # Disappeared
                if version_count <= total_versions * 0.3:
                    categories['experimental'].append((alg, first_ver, last_ver, presence_ratio))
                else:
                    categories['deprecated'].append((alg, first_ver, last_ver, presence_ratio))
    
    # Display results
    print(f"STABLE ALGORITHMS (present across most versions):")
    for alg, first, last, ratio in sorted(categories['stable'], key=lambda x: -x[3]):
        print(f"  • {alg}")
        print(f"    └─ v{first} → v{last} ({ratio:.1%} of versions)")
    
    if categories['modern']:
        print(f"\nMODERN ADDITIONS (added in later versions):")
        for alg, first, last, ratio in sorted(categories['modern'], key=lambda x: -x[1]):
            print(f"  • {alg}")
            print(f"    └─ v{first} → v{last} ({ratio:.1%} of versions)")
    
    if categories['deprecated']:
        print(f"\nDEPRECATED (removed or rarely used):")
        for alg, first, last, ratio in sorted(categories['deprecated'], key=lambda x: x[2]):
            print(f"  • {alg}")
            print(f"    └─ v{first} → v{last} ({ratio:.1%} of versions)")
    
    if categories['legacy']:
        print(f"\nLEGACY (old algorithms no longer supported):")
        for alg, first, last, ratio in sorted(categories['legacy'], key=lambda x: x[2]):
            print(f"  • {alg}")
            print(f"    └─ v{first} → v{last} ({ratio:.1%} of versions)")
    
    if categories['experimental']:
        print(f"\nEXPERIMENTAL (briefly supported):")
        for alg, first, last, ratio in sorted(categories['experimental'], key=lambda x: x[1]):
            print(f"  • {alg}")
            print(f"    └─ v{first} → v{last} ({ratio:.1%} of versions)")

def find_version_transitions(json_file, ssh_impl='openssh'):
    """Find major algorithm changes between consecutive versions"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    ssh_impl_lower = ssh_impl.lower()
    ssh_entries = [entry for entry in data if ssh_impl_lower in entry['Server'].lower()]
    
    versioned_entries = []
    for entry in ssh_entries:
        server_string = entry['Server']
        version_match = re.search(r'{0}[_-]?(\d+\.\d+)'.format(ssh_impl_lower), server_string, re.IGNORECASE)
        if version_match:
            version = float(version_match.group(1))
            versioned_entries.append((version, entry))
    
    versioned_entries.sort(key=lambda x: x[0])
    
    print(f"=== MAJOR ALGORITHM CHANGES BETWEEN {ssh_impl.upper()} VERSIONS ===\n")
    
    algorithm_types = ['KEX', 'Encryption', 'MAC', 'HostKeyAlgorithms']
    
    for i in range(1, len(versioned_entries)):
        prev_version, prev_entry = versioned_entries[i-1]
        curr_version, curr_entry = versioned_entries[i]
        
        has_changes = False
        changes = []
        
        for alg_type in algorithm_types:
            prev_algs = set(prev_entry.get(alg_type, []))
            curr_algs = set(curr_entry.get(alg_type, []))
            
            added = curr_algs - prev_algs
            removed = prev_algs - curr_algs
            
            if added or removed:
                has_changes = True
                if added:
                    changes.append(f"  {alg_type} ADDED: {', '.join(sorted(added))}")
                if removed:
                    changes.append(f"  {alg_type} REMOVED: {', '.join(sorted(removed))}")
        
        if has_changes:
            print(f"v{prev_version} → v{curr_version}:")
            for change in changes:
                print(change)
            print()

if __name__ == "__main__":
    # Default to OpenSSH but allow changing via command line
    import sys
    ssh_impl = 'openssh'
    if len(sys.argv) > 1:
        ssh_impl = sys.argv[1].lower()
        valid_impls = ['openssh', 'asyncssh', 'libssh', 'wolfssh', 'dropbear']
        if ssh_impl not in valid_impls:
            print(f"Invalid SSH implementation. Choose from: {', '.join(valid_impls)}")
            sys.exit(1)
    
    analyze_ssh_evolution('HasshList.json', ssh_impl)
    print("\n" + "="*60 + "\n")
    find_version_transitions('HasshList.json', ssh_impl)