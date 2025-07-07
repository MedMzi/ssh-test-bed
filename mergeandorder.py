import json
from datetime import datetime, timezone

# Load the JSON files
with open('commit_dates.json') as f:
    commit_dates = json.load(f)

with open('HasshList.json') as f:
    hassh_list = json.load(f)

# Merge date info from commit_dates.json into hassh_list
for key, date_info in commit_dates.items():
    if key in hassh_list:
        hassh_list[key]['date'] = date_info.get('date')
    else:
        # If the key is not in hassh_list, add it with only the date info
        hassh_list[key] = date_info

# Function to parse date safely and consistently (aware datetime)
def parse_date(item):
    date_str = item.get('date')
    if not date_str:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)

# Sort by first letter of key and by date
sorted_items = sorted(
    hassh_list.items(),
    key=lambda x: (x[0][0].lower(), parse_date(x[1]))
)

# Create ordered dict again (dict keeps order in Python 3.7+)
sorted_hassh_list = {k: v for k, v in sorted_items}

# Save back into HasshList.json
with open('HasshList.json', 'w') as f:
    json.dump(sorted_hassh_list, f, indent=2)

print("HasshList.json has been updated with dates and sorted.")
