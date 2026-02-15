#!/usr/bin/env python3

import json
import os

# Locate project root and data file
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FILE = os.path.join(PROJECT_ROOT, "data", "sowing_history.json")

# -----------------------------
# Data Handling
# -----------------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        print("Could not find sowing_history.json!")
        return []

    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# -----------------------------
# Actions
# -----------------------------

def list_entries():
    data = load_data()
    
    print(data)

    if not data:
        print("\nNo sowing entries found.\n")
        return

    print("\nSowing Entries:")
    print("-" * 40)

    for entry in data:
        print(f"Plant ID: {entry['plant_id']}")
        print(f"Variety: {entry['variety']}")
        print(f"Sowing Date: {entry['sowing_date']}")
        print("-" * 40)


def delete_entry_by_id():
    data = load_data()

    if not data:
        print("\nNo entries to delete.\n")
        return

    plant_id = input("Enter Plant ID to delete: ").strip()

    # Correct list comprehension here
    new_data = [entry for entry in data if entry["plant_id"] != plant_id]

    if len(new_data) == len(data):
        print(f"\nNo entry found with Plant ID {plant_id}\n")
        return

    save_data(new_data)
    print(f"\nEntry with Plant ID {plant_id} deleted.\n")
    

# -----------------------------
# Menu
# -----------------------------

def main():
    
    choice = ""
    
    while choice != "q":
        
        print("\nSproutLab Data Manager")
        print("0: List sowing entries")
        print("1: Delete entry by ID")
        print("q: Quit")
    
        choice = input("\nSelect an option: ").strip()
    
        if choice == "0":
            list_entries()
        elif choice == "1":
            delete_entry_by_id()
        else:
            print("Invalid option.")

    print("Goodbye.")

if __name__ == "__main__":
    main()


