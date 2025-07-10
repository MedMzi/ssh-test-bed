import json

# Keys to update (exact keys from AllSupportedAlgos)
keys_to_update = ["V_4_7_P1", "V_4_6_P1", "V_4_5_P1", "V_4_4_P1"]

# Load AllSupportedAlgos.json
with open("AllSupportedAlgos.json", "r") as f:
    all_supported = json.load(f)

# Load Supported_Algos.json
with open("Supported_Algos.json", "r") as f:
    supported_algos = json.load(f)

for key in keys_to_update:
    key_lower = key.lower()
    if key in all_supported and key_lower in supported_algos:
        # Update only KexAlgorithms from kex
        if "kex" in all_supported[key]:
            supported_algos[key_lower]["KexAlgorithms"] = all_supported[key]["kex"]

# Save back to Supported_Algos.json
with open("Supported_Algos.json", "w") as f:
    json.dump(supported_algos, f, indent=2)

print("Updated KexAlgorithms for keys:", keys_to_update)
