import os

keywords = ["Therapist", "Consumables", "Dental", "Anomalies", "Batch Billing", "Time Overlap", "QA-CUST", "0/"]
search_dir = r"e:\chain\hello-agents\Co-creation-projects"

for root, dirs, files in os.walk(search_dir):
    if "node_modules" in root or "venv" in root or ".git" in root:
        continue
    for file in files:
        if file.endswith((".py", ".md", ".json", ".txt", ".csv", ".ipynb", ".html", ".js", ".ts", ".tsx", ".vue")):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                for kw in keywords:
                    if kw.lower() in content.lower():
                        print(f"Found '{kw}' in {filepath}")
            except Exception as e:
                pass
