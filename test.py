import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Load JSON files (replace with your file paths)
with open("HasshList.json") as f:
    hasshlist = json.load(f)

with open("openssh_template/Supported_Algos.json") as f:
    supported_algos = json.load(f)

def normalize_version_key(key):
    # Normalize keys like openssh_v_5_2_p1 -> v_5_2_p1
    if key.startswith("openssh_v_"):
        return "v_" + key[len("openssh_v_"):]
    return key

# Parse hasshlist versions and extract algorithms + date
hassh_data = []
for vkey, vdata in hasshlist.items():
    if not vkey.startswith("openssh_v_"):
        continue
    version = normalize_version_key(vkey)
    date = datetime.fromisoformat(vdata.get("date"))
    for category in ["KEX", "Encryption", "MAC", "Compression", "HostKeyAlgorithms"]:
        algos = vdata.get(category, [])
        for algo in algos:
            hassh_data.append({
                "version": version,
                "date": date,
                "category": category,
                "algorithm": algo,
                "source": "announced"
            })

# Parse supported_algos versions and extract algorithms (no dates here, so set to None)
supported_data = []
for vkey, vdata in supported_algos.items():
    version = vkey  # keys already like v_10_0_p2
    for category, key_name in [("KEX", "KexAlgorithms"),
                               ("Encryption", "Ciphers"),
                               ("MAC", "MACs"),
                               ("HostKeyAlgorithms", "HostKeyAlgorithms")]:
        algos = vdata.get(key_name, [])
        for algo in algos:
            supported_data.append({
                "version": version,
                "date": None,  # no date in supported JSON
                "category": category,
                "algorithm": algo,
                "source": "supported"
            })

# Combine and create a DataFrame
df_announced = pd.DataFrame(hassh_data)
df_supported = pd.DataFrame(supported_data)

# Merge announced and supported on version, category, algorithm to classify them
# We'll create sets per version+category for announced and supported algos
def classify_algorithms(version, category):
    announced_set = set(df_announced[(df_announced["version"]==version) & (df_announced["category"]==category)]["algorithm"])
    supported_set = set(df_supported[(df_supported["version"]==version) & (df_supported["category"]==category)]["algorithm"])
    all_algos = announced_set.union(supported_set)
    result = []
    for algo in all_algos:
        if algo in announced_set and algo in supported_set:
            status = "Supported & Announced"
        elif algo in announced_set and algo not in supported_set:
            status = "Announced only"
        else:
            status = "Supported only"
        result.append({"version": version, "category": category, "algorithm": algo, "status": status})
    return result

# Get all versions (union)
all_versions = set(df_announced["version"]).union(set(df_supported["version"]))

# We'll focus on one category for the example: KEX
category = "KEX"
comparison_rows = []
for version in all_versions:
    comparison_rows.extend(classify_algorithms(version, category))

df_comparison = pd.DataFrame(comparison_rows)

# For visualization, pivot so rows=algorithms, columns=versions, values=status
pivot = df_comparison.pivot(index="algorithm", columns="version", values="status").fillna("Not Present")

# Map status to colors
color_map = {
    "Supported & Announced": "green",
    "Announced only": "red",
    "Supported only": "blue",
    "Not Present": "lightgrey"
}

# Create a color matrix for the heatmap
color_matrix = pivot.applymap(lambda x: color_map.get(x, "lightgrey"))

# Step 1
announced_versions_order = [normalize_version_key(k) for k in hasshlist.keys() if k.startswith("openssh_v_")]
supported_versions_order = list(supported_algos.keys())

# Step 2
all_versions_ordered = announced_versions_order[:]
for v in supported_versions_order:
    if v not in all_versions_ordered:
        all_versions_ordered.append(v)

# Step 3
pivot = df_comparison.pivot(index="algorithm", columns="version", values="status").fillna("Not Present")
pivot = pivot.reindex(columns=all_versions_ordered)  # preserve JSON order

# Step 4
fig, ax = plt.subplots(figsize=(16, 8))
sns.heatmap(
    pd.isna(pivot),
    annot=False,
    cmap=["white"],
    cbar=False,
    linewidths=0.5,
    linecolor='gray',
    ax=ax
)

for y in range(color_matrix.shape[0]):
    for x in range(color_matrix.shape[1]):
        ax.add_patch(plt.Rectangle((x, y), 1, 1, fill=True, color=color_matrix.iat[y, x], alpha=0.3))

import matplotlib.patches as mpatches
legend_patches = [
    mpatches.Patch(color='green', label='Supported & Announced'),
    mpatches.Patch(color='red', label='Announced only'),
    mpatches.Patch(color='blue', label='Supported only'),
    mpatches.Patch(color='lightgrey', label='Not Present'),
]
ax.legend(handles=legend_patches, title="Algorithm Status", bbox_to_anchor=(1.05, 1), loc='upper left')

ax.set_title(f"Comparison of {category} Algorithms: Announced vs Supported")
plt.xticks(rotation=90, ha='center', fontsize=10)
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()
