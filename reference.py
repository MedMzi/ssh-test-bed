import json
from collections import defaultdict

# Load the JSON data
with open("HasshList.json", "r") as f:
    data = json.load(f)

# Store unique values for each array field
unique_values = defaultdict(set)

# Fields to extract
fields = ["KEX", "Encryption", "MAC", "Compression", "HostKeyAlgorithms"]

# Iterate over each object in the list
for entry in data:
    for field in fields:
        unique_values[field].update(entry.get(field, []))

# Print the results
for field in fields:
    print(f"\nAll unique values in '{field}':")
    for value in sorted(unique_values[field]):
        print(f"  {value}")
