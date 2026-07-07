import os

search_dir = r"e:\chain\hello-agents"

for root, dirs, files in os.walk(search_dir):
    if any(ignore in root for ignore in ["venv", ".git", "node_modules", "temp_gorilla"]):
        continue
    level = root.replace(search_dir, '').count(os.sep)
    if level <= 3:
        for file in files:
            filepath = os.path.join(root, file)
            # Print if it looks like an evaluation script or has a name related to eval
            if any(term in file.lower() for term in ["eval", "score", "test", "metric", "judge", "run"]):
                print(f"File: {filepath}")
