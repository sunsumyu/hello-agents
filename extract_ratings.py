import json

file_path = r"e:\chain\hello-agents\temp_gorilla\agent-arena\evalutation\agent_ratings_V0.json"
print("Loading JSON...")
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Type of data: {type(data)}")
if isinstance(data, dict):
    print(f"Keys: {list(data.keys())[:10]}")
elif isinstance(data, list):
    print(f"Length: {len(data)}")
    print(f"First element: {data[0]}")

# Let's search for "Therapist" or "Consumables" or "Dental" in keys or values
def search_nested(obj, query):
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if query.lower() in str(k).lower():
                results.append((k, type(v)))
            res = search_nested(v, query)
            if res:
                results.extend(res)
    elif isinstance(obj, list):
        for item in obj:
            res = search_nested(item, query)
            if res:
                results.extend(res)
    elif isinstance(obj, str):
        if query.lower() in obj.lower():
            results.append(obj)
    return results

print("Searching Therapist...")
print(search_nested(data, "Therapist")[:5])
print("Searching Consumables...")
print(search_nested(data, "Consumables")[:5])
