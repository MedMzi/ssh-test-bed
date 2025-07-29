import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import matplotlib.patches as mpatches

# === Utility: Normalize version keys ===
def normalize_version_key(key):
    return key.replace("openssh_v_", "v_") if key.startswith("openssh_v_") else key

# === Load JSON files ===
with open("HasshList.json") as f:
    hasshlist = json.load(f)

with open("openssh_template/Supported_Algos.json") as f:
    supported_algos = json.load(f)

# === Parse hasshlist (announced algorithms) ===
hassh_data = []
for vkey, vdata in hasshlist.items():
    if not vkey.startswith("openssh_v_"):
        continue
    version = normalize_version_key(vkey)
    date = datetime.fromisoformat(vdata.get("date"))
    for category in ["KEX", "Encryption", "MAC", "Compression", "HostKeyAlgorithms"]:
        for algo in vdata.get(category, []):
            hassh_data.append({
                "version": version,
                "date": date,
                "category": category,
                "algorithm": algo,
                "source": "announced"
            })

# === Parse supported_algos (supported algorithms) ===
supported_data = []
for vkey, vdata in supported_algos.items():
    version = normalize_version_key(vkey)  # ✅ normalize here too!
    for category, key_name in [
        ("KEX", "KexAlgorithms"),
        ("Encryption", "Ciphers"),
        ("MAC", "MACs"),
        ("HostKeyAlgorithms", "HostKeyAlgorithms")
    ]:
        for algo in vdata.get(key_name, []):
            supported_data.append({
                "version": version,
                "date": None,
                "category": category,
                "algorithm": algo,
                "source": "supported"
            })

# === Combine into DataFrames ===
df_announced = pd.DataFrame(hassh_data)
df_supported = pd.DataFrame(supported_data)

# === Function: Classify algorithms ===
def classify_algorithms(version, category):
    announced_set = set(df_announced[(df_announced["version"] == version) & (df_announced["category"] == category)]["algorithm"])
    supported_set = set(df_supported[(df_supported["version"] == version) & (df_supported["category"] == category)]["algorithm"])
    all_algos = announced_set.union(supported_set)

    result = []
    for algo in all_algos:
        if algo in announced_set and algo in supported_set:
            status = "Supported & Announced"
        elif algo in announced_set:
            status = "Announced only"
        else:
            status = "Supported only"
        result.append({
            "version": version,
            "category": category,
            "algorithm": algo,
            "status": status
        })
    return result

# === Comparison: Focus on one category (e.g., KEX) ===
for category in ["KEX", "Encryption", "MAC", "HostKeyAlgorithms"]:
    all_versions = sorted(set(df_announced["version"]).union(df_supported["version"]))
    comparison_rows = []

    for version in all_versions:
        comparison_rows.extend(classify_algorithms(version, category))

    df_comparison = pd.DataFrame(comparison_rows)

    pivot = df_comparison.pivot(index="algorithm", columns="version", values="status").fillna("Not Present")

    color_map = {
        "Supported & Announced": "green",
        "Announced only": "red",
        "Supported only": "blue",
        "Not Present": "lightgrey"
    }
    color_matrix = pivot.applymap(lambda x: color_map.get(x, "lightgrey"))

    announced_order = [normalize_version_key(k) for k in hasshlist.keys() if k.startswith("openssh_v_")]
    supported_order = [normalize_version_key(k) for k in supported_algos.keys()]
    ordered_versions = []
    for v in announced_order + supported_order:
        if v not in ordered_versions:
            ordered_versions.append(v)

    pivot = pivot.reindex(columns=ordered_versions)
    color_matrix = color_matrix.reindex(columns=ordered_versions)

    fig, ax = plt.subplots(figsize=(16, 8))
    sns.heatmap(
        pd.DataFrame([[0]*len(pivot.columns)]*len(pivot.index), index=pivot.index, columns=pivot.columns),
        annot=False,
        cmap=["white"],
        cbar=False,
        linewidths=0.5,
        linecolor='gray',
        ax=ax
    )

    for y in range(color_matrix.shape[0]):
        for x in range(color_matrix.shape[1]):
            ax.add_patch(plt.Rectangle((x, y), 1, 1, fill=True, color=color_matrix.iat[y, x], alpha=0.5))

    legend_patches = [
        mpatches.Patch(color='green', label='Supported & Announced'),
        mpatches.Patch(color='red', label='Announced only'),
        mpatches.Patch(color='blue', label='Supported only'),
        mpatches.Patch(color='lightgrey', label='Not Present')
    ]
    ax.legend(handles=legend_patches, title="Algorithm Status", bbox_to_anchor=(1.05, 1), loc='upper left')

    ax.set_title(f"Comparison of {category} Algorithms: Announced vs Supported")
    plt.xticks(rotation=90, ha='center', fontsize=10)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()

