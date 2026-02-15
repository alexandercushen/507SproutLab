#!/usr/bin/env python3

import json
import os
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(PROJECT_ROOT, "data", "sowing_history.json")

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def main():
    plant_id = input("Plant ID: ").strip()
    variety = input("Variety: ").strip()
    sowing_date = input("Sowing date (YYYY-MM-DD), or enter for today: ").strip()

    # Validate date
    if sowing_date == "":
        sowing_date = datetime.today().strftime("%Y-%m-%d")
    else:
        try:
            datetime.strptime(sowing_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return

    data = load_data()

    new_entry = {
        "plant_id": plant_id,
        "variety": variety,
        "sowing_date": sowing_date
    }

    data.append(new_entry)
    save_data(data)

    print("✅ Entry added successfully.")

if __name__ == "__main__":
    main()

