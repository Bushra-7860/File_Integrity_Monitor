import hashlib
import os
import json
from datetime import datetime

def log_event(event_type, filename):
    os.makedirs("logs", exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("logs/integrity.log", "a") as log_file:
        log_file.write(f"{timestamp} | {event_type} | {filename}\n")
def calculate_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(4096):
            sha256.update(chunk)

    return sha256.hexdigest()

#Test Function
if __name__ == "__main__":
    file_path = "test_files/example.txt"

    file_hash = calculate_hash(file_path)

    print("File:", file_path)
    print("SHA-256:", file_hash)

def create_baseline(directory):
    baseline = {}

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isfile(file_path):
            baseline[filename] = calculate_hash(file_path)

    baseline_path = os.path.join(os.getcwd(), "baseline.json")

    with open(baseline_path, "w") as file:
        json.dump(baseline, file, indent=4)

    print("\nBaseline created successfully!")
    print(f"Saved to: {baseline_path}")


def check_integrity(directory):
    try:
        with open("baseline.json", "r") as file:
            baseline = json.load(file)
    except FileNotFoundError:
        print("\nNo baseline found. Create a baseline first.")
        return

    print("\nChecking file integrity...\n")

    current_files = set()

    unchanged_count = 0
    modified_count = 0
    deleted_count = 0
    new_count = 0

    # Get all files currently in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        if os.path.isfile(file_path):
            current_files.add(filename)

    # Check files that were in the original baseline
    for filename, old_hash in baseline.items():
        file_path = os.path.join(directory, filename)

        if not os.path.exists(file_path):
            print(f"[!] DELETED: {filename}")
            log_event("DELETED", filename)
            deleted_count += 1
            continue

        current_hash = calculate_hash(file_path)

        if current_hash == old_hash:
            print(f"[+] UNCHANGED: {filename}")
            unchanged_count += 1
        else:
            print(f"[!] MODIFIED: {filename}")
            log_event("MODIFIED", filename)
            modified_count += 1

    # Check for new files
    for filename in current_files:
        if filename not in baseline:
            print(f"[!] NEW FILE: {filename}")
            log_event("NEW FILE", filename)
            new_count += 1

    # Display scan summary
    files_checked = unchanged_count + modified_count
    security_events = modified_count + deleted_count + new_count

    print("\n========== SCAN SUMMARY ==========")
    print(f"Files checked:    {files_checked}")
    print(f"Unchanged:        {unchanged_count}")
    print(f"Modified:         {modified_count}")
    print(f"Deleted:          {deleted_count}")
    print(f"New files:        {new_count}")
    print(f"\nSecurity events:  {security_events}")
    print("==================================")


def main():
    directory = "test_files"

    while True:
        print("\n==============================")
        print("      FILE INTEGRITY MONITOR")
        print("==============================")
        print("1. Create baseline")
        print("2. Check integrity")
        print("3. Exit")

        choice = input("\nEnter choice: ")

        if choice == "1":
            create_baseline(directory)

        elif choice == "2":
            check_integrity(directory)

        elif choice == "3":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

