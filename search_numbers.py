import os

keywords = ["14,500", "15,000", "18,500", "19,000", "14500", "15000", "18500", "19000"]
search_dir = r"e:\chain\hello-agents"

for root, dirs, files in os.walk(search_dir):
    if "venv" in root or ".git" in root:
        continue
    for file in files:
        if file.endswith((".py", ".md", ".json", ".txt", ".csv")):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                for kw in keywords:
                    if kw in content:
                        print(f"Found '{kw}' in {filepath}")
            except Exception as e:
                pass
