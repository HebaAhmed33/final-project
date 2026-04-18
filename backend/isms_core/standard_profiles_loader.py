import json
import os


def load_standard_profiles(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), "..", "standards", "standard_profiles.json")
    profiles = load_standard_profiles(path)
    for p in profiles:
        print(f"{p['id']} | {p['name']}")
