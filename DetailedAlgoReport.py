import json
from collections import defaultdict
import re

def parse_version(version_str):
    # Convert version string "1.4.13" into tuple (1, 4, 13)
    return tuple(int(p) for p in version_str.split('.'))

def analyze_ssh_evolution(json_file, ssh_impl='openssh'):
    with open(json_file, 'r') as f:
        raw_data = json.load(f)
        if isinstance(raw_data, dict):
            data = list(raw_data.values())
        else:
            data = raw_data

    
    ssh_impl_lower = ssh_impl.lower()
    ssh_entries = [entry for entry in data if ssh_impl_lower in entry['Server'].lower()]
    
    versioned_entries = []
    for entry in ssh_entries:
        server_string = entry['Server']
        
        if ssh_impl_lower == 'wolfssh':
            version_match = re.search(r'wolfSSHv(\d+\.\d+\.\d+)', server_string, re.IGNORECASE)
            if version_match:
                version_str = version_match.group(1)
                version_tuple = parse_version(version_str)
                versioned_entries.append((version_tuple, version_str, entry))
        else:
            # Regex matches versions like 7.9 or 7.9.1 (optional patch)
            version_match = re.search(r'{0}[_-]?(\d+\.\d+(?:\.\d+)?)'.format(ssh_impl_lower), server_string, re.IGNORECASE)
            if version_match:
                version_str = version_match.group(1)
                version_tuple = parse_version(version_str)
                versioned_entries.append((version_tuple, version_str, entry))
    
    if not versioned_entries:
        print(f"No versioned entries found for {ssh_impl.upper()}")
        return
    
    # Sort by parsed version tuple (major, minor, patch)
    versioned_entries.sort(key=lambda x: x[0])
    
    print(f"=== ANALYZING {len(versioned_entries)} {ssh_impl.upper()} ENTRIES ===\n")
    print("Version range:", f"{versioned_entries[0][1]} to {versioned_entries[-1][1]}\n")
    
    algorithm_types = ['KEX', 'Encryption', 'MAC', 'Compression', 'HostKeyAlgorithms']
    
    for alg_type in algorithm_types:
        print(f"=== {alg_type.upper()} EVOLUTION ===")
        analyze_algorithm_evolution(versioned_entries, alg_type)
        print()

def analyze_algorithm_evolution(versioned_entries, alg_type):
    # Track when each algorithm first appears and last appears
    algorithm_lifecycle = defaultdict(lambda: {'first': None, 'last': None, 'versions': []})
    
    for version_tuple, version_str, entry in versioned_entries:
        algorithms = entry.get(alg_type, [])
        for alg in algorithms:
            if algorithm_lifecycle[alg]['first'] is None:
                algorithm_lifecycle[alg]['first'] = version_tuple
                algorithm_lifecycle[alg]['first_str'] = version_str
            algorithm_lifecycle[alg]['last'] = version_tuple
            algorithm_lifecycle[alg]['last_str'] = version_str
            algorithm_lifecycle[alg]['versions'].append(version_tuple)
    
    categories = {
        'legacy': [],
        'stable': [],
        'modern': [],
        'deprecated': [],
        'experimental': []
    }
    
    min_version = versioned_entries[0][0]
    max_version = versioned_entries[-1][0]
    # To compare tuples as versions, calculate version_span as a rough float difference
    def version_to_float(v):
        # e.g. (7,9,1) => 7 + 0.09 + 0.001 = 7.091
        return v[0] + v[1]/100 + (v[2]/10000 if len(v) > 2 else 0)
    
    min_vf = version_to_float(min_version)
    max_vf = version_to_float(max_version)
    version_span = max_vf - min_vf
    
    total_versions = len(versioned_entries)
    
    for alg, lifecycle in algorithm_lifecycle.items():
        first_ver = lifecycle['first']
        last_ver = lifecycle['last']
        first_ver_str = lifecycle['first_str']
        last_ver_str = lifecycle['last_str']
        version_count = len(lifecycle['versions'])
        
        presence_ratio = version_count / total_versions
        
        first_vf = version_to_float(first_ver)
        last_vf = version_to_float(last_ver)
        
        if first_vf <= min_vf + version_span * 0.2:
            if last_vf >= max_vf - version_span * 0.2:
                if presence_ratio >= 0.7:
                    categories['stable'].append((alg, first_ver_str, last_ver_str, presence_ratio))
                else:
                    categories['deprecated'].append((alg, first_ver_str, last_ver_str, presence_ratio))
            else:
                categories['legacy'].append((alg, first_ver_str, last_ver_str, presence_ratio))
        else:
            if last_vf >= max_vf - version_span * 0.2:
                categories['modern'].append((alg, first_ver_str, last_ver_str, presence_ratio))
            else:
                if version_count <= total_versions * 0.3:
                    categories['experimental'].append((alg, first_ver_str, last_ver_str, presence_ratio))
                else:
                    categories['deprecated'].append((alg, first_ver_str, last_ver_str, presence_ratio))
    
    print(f"STABLE ALGORITHMS (present across most versions):")
    for alg, first, last, ratio in sorted(categories['stable'], key=lambda x: -x[3]):
        print(f"  • {alg}")
        print(f"    └─ v{first} → v{last} ({ratio:.1%} of versions)")
    
    if categories['modern']:
        print(f"\nMODERN ADDITIONS (added in later versions):")
        for alg, first, last, ratio in sorted(categories['modern'], key=lambda x: x[1], reverse=True):
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
    with open(json_file, 'r') as f:
        raw_data = json.load(f)
        if isinstance(raw_data, dict):
            data = list(raw_data.values())
        else:
            data = raw_data

    
    ssh_impl_lower = ssh_impl.lower()
    ssh_entries = [entry for entry in data if ssh_impl_lower in entry['Server'].lower()]
    
    versioned_entries = []
    for entry in ssh_entries:
        server_string = entry['Server']
        
        if ssh_impl_lower == 'wolfssh':
            version_match = re.search(r'wolfSSHv(\d+\.\d+\.\d+)', server_string, re.IGNORECASE)
            if version_match:
                version_str = version_match.group(1)
                version_tuple = parse_version(version_str)
                versioned_entries.append((version_tuple, version_str, entry))
        else:
            version_match = re.search(r'{0}[_-]?(\d+\.\d+(?:\.\d+)?)'.format(ssh_impl_lower), server_string, re.IGNORECASE)
            if version_match:
                version_str = version_match.group(1)
                version_tuple = parse_version(version_str)
                versioned_entries.append((version_tuple, version_str, entry))
    
    if not versioned_entries:
        print(f"No versioned entries found for {ssh_impl.upper()}")
        return
    
    versioned_entries.sort(key=lambda x: x[0])
    
    print(f"=== MAJOR ALGORITHM CHANGES BETWEEN {ssh_impl.upper()} VERSIONS ===\n")
    
    algorithm_types = ['KEX', 'Encryption', 'MAC', 'HostKeyAlgorithms']
    
    for i in range(1, len(versioned_entries)):
        prev_version, prev_version_str, prev_entry = versioned_entries[i-1]
        curr_version, curr_version_str, curr_entry = versioned_entries[i]
        
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
            print(f"v{prev_version_str} → v{curr_version_str}:")
            for change in changes:
                print(change)
            print()

if __name__ == "__main__":
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
