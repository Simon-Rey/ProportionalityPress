import os
import json
import re

# === CONFIG ===
FOLDER_PATH = "data/polis"  # <-- change this to your folder path

# Regex to match "User <number>"
user_pattern = re.compile(r"User\s+(\d+)")

# Iterate through all JSON files in the folder
for filename in os.listdir(FOLDER_PATH):
    if filename.endswith(".json"):
        file_path = os.path.join(FOLDER_PATH, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Update each comment's author
        if "comments" in data:
            for comment in data["comments"]:
                author = comment.get("author", "")
                match = user_pattern.match(author)
                if match:
                    user_id = int(match.group(1))
                    comment["author"] = f"User {user_id + 1}"

        # Save changes back to the same file (with nice formatting)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Updated authors in: {filename}")

print("🎉 All JSON files updated successfully!")
