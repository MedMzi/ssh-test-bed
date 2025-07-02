import json

def find_common_algorithms(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Group by library type
    libraries = {
        'asyncssh': [],
        'libssh': [], 
        'openssh': [],
        'dropbear': [],
        'wolfssh': []
    }
    
    # Categorize servers by library
    for entry in data:
        server_name = entry['Server'].lower()
        if 'asyncssh' in server_name:
            libraries['asyncssh'].append(entry)
        elif 'libssh' in server_name:
            libraries['libssh'].append(entry)
        elif 'openssh' in server_name:
            libraries['openssh'].append(entry)
        elif 'dropbear' in server_name:
            libraries['dropbear'].append(entry)
        elif 'wolfssh' in server_name:
            libraries['wolfssh'].append(entry)
    
    # Show what we found
    print("=== LIBRARIES FOUND ===")
    for lib_name, entries in libraries.items():
        if entries:
            print(f"{lib_name}: {len(entries)} entries")
    print()
    
    # Algorithm types to check
    algorithm_types = ['KEX', 'Encryption', 'MAC', 'Compression', 'HostKeyAlgorithms']
    
    # Find common algorithms within each library first
    library_commons = {}
    for lib_name, entries in libraries.items():
        if entries:
            library_commons[lib_name] = {}
            for alg_type in algorithm_types:
                # Start with first entry's algorithms
                common = set(entries[0].get(alg_type, []))
                # Find intersection with all other entries in this library
                for entry in entries[1:]:
                    common &= set(entry.get(alg_type, []))
                library_commons[lib_name][alg_type] = common
    
    print("=== COMMON ALGORITHMS PER LIBRARY ===\n")
    for lib_name, alg_dict in library_commons.items():
        print(f"{lib_name.upper()}:")
        for alg_type in algorithm_types:
            algorithms = sorted(list(alg_dict[alg_type]))
            print(f"  {alg_type} ({len(algorithms)}): {algorithms}")
        print()
    
    # Find universal algorithms across ALL libraries
    if len(library_commons) > 1:
        print("=== UNIVERSAL ALGORITHMS (ACROSS ALL LIBRARIES) ===\n")
        for alg_type in algorithm_types:
            # Get sets from all libraries for this algorithm type
            lib_sets = [alg_dict[alg_type] for alg_dict in library_commons.values()]
            
            # Find intersection
            universal = lib_sets[0]
            for s in lib_sets[1:]:
                universal &= s
            
            print(f"{alg_type} ({len(universal)} universal):")
            for alg in sorted(list(universal)):
                print(f"  - {alg}")
            print()
    else:
        print("=== NEED DATA FROM MULTIPLE LIBRARIES FOR UNIVERSAL ANALYSIS ===\n")

# For the current data (AsyncSSH only)
def find_asyncssh_common(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    algorithm_types = ['KEX', 'Encryption', 'MAC', 'Compression', 'HostKeyAlgorithms']
    
    print("=== COMMON ALGORITHMS ACROSS ALL ASYNCSSH VERSIONS ===\n")
    
    for alg_type in algorithm_types:
        # Start with first entry's algorithms
        common = set(data[0].get(alg_type, []))
        
        # Find intersection with all other entries
        for entry in data[1:]:
            common &= set(entry.get(alg_type, []))
        
        print(f"{alg_type} ({len(common)} common):")
        for alg in sorted(list(common)):
            print(f"  - {alg}")
        print()

if __name__ == "__main__":
    # Run the full analysis for all libraries
    find_common_algorithms('HasshList.json')