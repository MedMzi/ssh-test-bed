import json

def find_common_algorithms(json_file):
    with open(json_file, 'r') as f:
        raw_data = json.load(f)

    # Flatten the version-keyed structure into a list of entries
    data = list(raw_data.values())

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

    print("=== LIBRARIES FOUND ===")
    for lib_name, entries in libraries.items():
        if entries:
            print(f"{lib_name}: {len(entries)} entries")
    print()

    algorithm_types = ['KEX', 'Encryption', 'MAC', 'Compression', 'HostKeyAlgorithms']

    # Find common algorithms within each library
    library_commons = {}
    for lib_name, entries in libraries.items():
        if entries:
            library_commons[lib_name] = {}
            for alg_type in algorithm_types:
                common = set(entries[0].get(alg_type, []))
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

    # Find universal algorithms across all libraries
    if len(library_commons) > 1:
        print("=== UNIVERSAL ALGORITHMS (ACROSS ALL LIBRARIES) ===\n")
        for alg_type in algorithm_types:
            lib_sets = [alg_dict[alg_type] for alg_dict in library_commons.values()]
            universal = lib_sets[0]
            for s in lib_sets[1:]:
                universal &= s
            print(f"{alg_type} ({len(universal)} universal):")
            for alg in sorted(list(universal)):
                print(f"  - {alg}")
            print()
    else:
        print("=== NEED DATA FROM MULTIPLE LIBRARIES FOR UNIVERSAL ANALYSIS ===\n")

# For AsyncSSH-only JSON (optional helper)
def find_asyncssh_common(json_file):
    with open(json_file, 'r') as f:
        raw_data = json.load(f)
    
    data = list(raw_data.values())
    algorithm_types = ['KEX', 'Encryption', 'MAC', 'Compression', 'HostKeyAlgorithms']

    print("=== COMMON ALGORITHMS ACROSS ALL ASYNCSSH VERSIONS ===\n")
    for alg_type in algorithm_types:
        common = set(data[0].get(alg_type, []))
        for entry in data[1:]:
            common &= set(entry.get(alg_type, []))
        print(f"{alg_type} ({len(common)} common):")
        for alg in sorted(list(common)):
            print(f"  - {alg}")
        print()

if __name__ == "__main__":
    find_common_algorithms('HasshList.json')
