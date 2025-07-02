import json
import re
from packaging import version

def parse_version(server_string):
    """Extract version number from server string"""
    # Remove SSH-2.0- prefix
    clean_name = server_string.replace('SSH-2.0-', '')
    
    # Handle different library naming patterns
    patterns = [
        r'AsyncSSH[_-](\d+\.\d+\.\d+)',
        r'libssh[_-](\d+\.\d+\.\d+)',
        r'OpenSSH[_-](\d+\.\d+)',
        r'dropbear[_-](\d+\.\d+)',
        r'wolfSSHv(\d+\.\d+\.\d+)',  # Fixed: wolfSSH uses 'v' not '_' or '-'
        r'wolfSSH[_-](\d+\.\d+\.\d+)',
        # Generic patterns for various formats
        r'[a-zA-Z]+v(\d+\.\d+(?:\.\d+)?)',  # For libraries using 'v' (like wolfSSHv1.4.15)
        r'[a-zA-Z]+[_-](\d+\.\d+(?:\.\d+)?)'  # For libraries using '_' or '-'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, clean_name, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # If no version found, return None
    return None

def get_library_name(server_string):
    """Extract library name from server string"""
    clean_name = server_string.replace('SSH-2.0-', '').lower()
    
    if 'asyncssh' in clean_name:
        return 'asyncssh'
    elif 'libssh' in clean_name:
        return 'libssh'
    elif 'openssh' in clean_name:
        return 'openssh'
    elif 'dropbear' in clean_name:
        return 'dropbear'
    elif 'wolfssh' in clean_name:
        return 'wolfssh'
    else:
        return 'unknown'

def find_latest_versions_common_algorithms(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Group by library and find latest version
    libraries = {
        'asyncssh': [],
       # 'libssh': [], 
        'openssh': [],
        'dropbear': [],
        'wolfssh': []
    }
    
    # Categorize servers by library
    for entry in data:
        lib_name = get_library_name(entry['Server'])
        if lib_name in libraries:
            entry['parsed_version'] = parse_version(entry['Server'])
            libraries[lib_name].append(entry)
    
    # Find latest version for each library
    latest_versions = {}
    
    print("=== LIBRARY ANALYSIS ===")
    for lib_name, entries in libraries.items():
        if entries:
            print(f"\n{lib_name.upper()}:")
            print(f"  Total entries: {len(entries)}")
            
            # Find entry with highest version
            valid_entries = [e for e in entries if e['parsed_version']]
            
            if valid_entries:
                # Sort by version number
                try:
                    sorted_entries = sorted(valid_entries, 
                                          key=lambda x: version.parse(x['parsed_version']), 
                                          reverse=True)
                    latest_entry = sorted_entries[0]
                    latest_versions[lib_name] = latest_entry
                    print(f"  Latest version: {latest_entry['Server']}")
                except Exception as e:
                    # Fallback to string comparison if version parsing fails
                    latest_entry = max(valid_entries, key=lambda x: x['parsed_version'])
                    latest_versions[lib_name] = latest_entry
                    print(f"  Latest version (string sort): {latest_entry['Server']}")
            else:
                print(f"  No valid version entries found")
                # Show available entries for debugging
                for entry in entries[:3]:  # Show first 3
                    print(f"    - {entry['Server']}")
    
    print(f"\n=== LATEST VERSIONS SELECTED ===")
    for lib_name, entry in latest_versions.items():
        print(f"{lib_name}: {entry['Server']}")
    
    # Algorithm types to check
    algorithm_types = ['KEX', 'Encryption', 'MAC', 'Compression', 'HostKeyAlgorithms']
    
    if len(latest_versions) < 2:
        print(f"\n=== INSUFFICIENT DATA ===")
        print(f"Need at least 2 libraries for comparison. Found: {len(latest_versions)}")
        return
    
    print(f"\n=== COMMON ALGORITHMS ACROSS ALL LATEST VERSIONS ===")
    print(f"Comparing {len(latest_versions)} libraries\n")
    
    # Find common algorithms across all latest versions
    for alg_type in algorithm_types:
        # Get algorithm sets from all latest versions
        algorithm_sets = []
        for lib_name, entry in latest_versions.items():
            alg_set = set(entry.get(alg_type, []))
            algorithm_sets.append((lib_name, alg_set))
        
        # Find intersection of all sets
        if algorithm_sets:
            common_algorithms = algorithm_sets[0][1]
            for lib_name, alg_set in algorithm_sets[1:]:
                common_algorithms &= alg_set
            
            print(f"{alg_type} ({len(common_algorithms)} common across all):")
            if common_algorithms:
                for alg in sorted(list(common_algorithms)):
                    print(f"  - {alg}")
            else:
                print("  - No common algorithms found")

            print()

def analyze_library_coverage(json_file):
    """Additional analysis to show library coverage"""
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    library_counts = {}
    for entry in data:
        lib_name = get_library_name(entry['Server'])
        library_counts[lib_name] = library_counts.get(lib_name, 0) + 1
    
    print("=== LIBRARY COVERAGE IN DATASET ===")
    for lib_name, count in sorted(library_counts.items()):
        print(f"{lib_name}: {count} entries")
    print()

if __name__ == "__main__":
    try:
        # First show what's in the dataset
        analyze_library_coverage('HasshList.json')
        
        # Then find common algorithms among latest versions
        find_latest_versions_common_algorithms('HasshList.json')
        
    except FileNotFoundError:
        print("Error: HasshList.json file not found")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in HasshList.json")
    except Exception as e:
        print(f"Error: {e}")