#!/usr/bin/env python3
'''
Main script for editing the sowing log. Run from scripts/ as:
> ./manage_sow_data.py
And follow the menu inscructions
'''

import json
import os
from datetime import datetime

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
        
def sort_data_by_id():
    '''
    Sort the sowing_history.json by plant_id

    Returns
    -------
    None.

    '''
    
    data = load_data()
    # Sort in-place by plant_id (numerically if IDs are numbers, else lexicographically)
    try:
        # If plant_id can be converted to int, sort numerically
        data.sort(key=lambda x: int(x["plant_id"]))
    except ValueError:
        # Fallback: sort as strings
        data.sort(key=lambda x: x["plant_id"])
    
    # Save the sorted data back to the file
    save_data(data)


# -----------------------------
# Actions
# -----------------------------

def list_entries():
    '''
    List all of the plants saved in sowing_history.json

    Returns
    -------
    None.

    '''
    # First sort the entries
    sort_data_by_id()
    
    data = load_data()

    if not data:
        print("\nNo sowing entries found.\n")
        return

    print("\nSowing Entries (ID, species, variety, sowing date):")
    print("-" * 40)

    for entry in data:
        print(f"{entry['plant_id']}: {entry['species']}, {entry['varietal']}, {entry['sowing_date']}")
        #print(f"Plant ID: {entry['plant_id']}")
        #print(f"species: {entry['species']}")
        #print(f"varietal: {entry['varietal']}")
        #print(f"Sowing Date: {entry['sowing_date']}")
        #print("-" * 40)
        
    print("-" * 40)
        
def new_sow():
    '''
    Add a new entry to sowing_history.json

    Returns
    -------
    None.

    '''
    data = load_data()
    
    plant_id = input("Plant ID: ").strip()
    
    # Check id is available
    while plant_id in [entry["plant_id"] for entry in data]:
        plant_id = input("Plant ID taken, enter another: ").strip()
    
    species = input("Species: ").strip()
    varietal = input("Varietal: ").strip()
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
        "species": species,
        "varietal": varietal,
        "sowing_date": sowing_date
    }

    data.append(new_entry)
    save_data(data)
    
    # Sort the entries
    sort_data_by_id()

    print("✅ Entry added successfully.")


def delete_entry_by_id():
    '''
    Remove an entry from sowing_history.json

    Returns
    -------
    None.

    '''
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
    
def list_species():
    '''
    List the species currently added to the log, as well as all of their varietals

    Returns
    -------
    None.

    '''
    data = load_data()
    
    if not data:
        print("\nNo sowing entries found.\n")
        return

    # Build a dict: species -> set of varietals
    species_dict = {}
    for entry in data:
        species = entry.get("species", "").strip()
        varietal = entry.get("varietal", "").strip()
        if not species or not varietal:
            continue  # skip incomplete entries

        species_dict.setdefault(species, set()).add(varietal)

    # Sort species alphabetically
    for species in sorted(species_dict.keys()):
        varietals = sorted(species_dict[species])
        print(f"\n{species}:")
        for v in varietals:
            print(f"  - {v}")
    print()  # extra newline
    

# -----------------------------
# Menu
# -----------------------------

def main():
    
    choice = ""
    
    while choice != "q":
        
        print("\nSproutLab Data Manager")
        print("0: List sowing entries")
        print("1: Add new plant sowing")
        print("2: Delete entry by ID")
        print("3: List plant species + varietals")
        print("q: Quit")
    
        choice = input("\nSelect an option: ").strip()
    
        if choice == "0":
            list_entries()
        elif choice == "1":
            new_sow()
        elif choice == "2":
            delete_entry_by_id()
        elif choice == "3":
            list_species()
        elif choice == "q":
            print("Goodbye.")
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()


