import os

keywords = ["darwin"]
search_dir = r"e:\chain\hello-agents"

for root, dirs, files in os.walk(search_dir):
    if "venv" in root or ".git" in root or "node_modules" in root:
        continue
    for file in files:
        filepath = os.path.join(root, file)
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            for kw in keywords:
                if kw.lower() in content.lower():
                    print(f"Found '{kw}' in {filepath}")
        except Exception as e:
            pass
