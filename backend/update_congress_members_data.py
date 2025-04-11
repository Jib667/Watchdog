import requests
import os
import sys

# --- Configuration ---
# Base URL for the raw files in the repository's main branch
RAW_BASE_URL = "https://raw.githubusercontent.com/unitedstates/congress-legislators/main/"

# List of YAML files to download
FILES_TO_DOWNLOAD = [
    "committee-membership-current.yaml",
    "committees-current.yaml",
    "committees-historical.yaml",
    "executive.yaml",
    "legislators-current.yaml",
    "legislators-district-offices.yaml",
    "legislators-historical.yaml",
    "legislators-social-media.yaml",
]

# Determine the absolute path of the directory containing this script
# (Assumes the script is in /Users/jibranhutchins/Developer/Watchdog/backend/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the target directory relative to the script's location
TARGET_DIR = os.path.join(SCRIPT_DIR, "app", "static", "congress_data")
# --- End Configuration ---

def download_files():
    """Downloads specified YAML files from GitHub and saves them locally."""
    print(f"Target directory: {TARGET_DIR}")

    # Ensure the target directory exists
    try:
        print("Ensuring target directory exists...")
        os.makedirs(TARGET_DIR, exist_ok=True)
        print(f"Directory ready.")
    except OSError as e:
        print(f"Error: Could not create directory {TARGET_DIR}. {e}")
        sys.exit(1) # Exit if directory cannot be created

    print("-" * 40)
    print("Starting download process...")
    print("-" * 40)

    success_count = 0
    error_count = 0

    for filename in FILES_TO_DOWNLOAD:
        download_url = RAW_BASE_URL + filename
        save_path = os.path.join(TARGET_DIR, filename)

        print(f"\nAttempting to download: {filename}")
        print(f"From URL: {download_url}")

        try:
            # Make the request to download the file
            response = requests.get(download_url, timeout=60) # Increased timeout for potentially large files
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

            # Save the content to the local file
            print(f"Saving to: {save_path}")
            with open(save_path, 'wb') as f: # Write in binary mode
                f.write(response.content)
            print(f"[SUCCESS] Downloaded and saved {filename}")
            success_count += 1

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to download {filename}: {e}")
            error_count += 1
        except IOError as e:
            print(f"[ERROR] Failed to save {filename} to {save_path}: {e}")
            error_count += 1
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred for {filename}: {e}")
            error_count += 1

    print("-" * 40)
    print("Download process finished.")
    print(f"Summary: {success_count} files downloaded successfully, {error_count} errors.")
    print("-" * 40)

if __name__ == "__main__":
    # Check if requests library is installed
    try:
        import requests
    except ImportError:
        print("Error: The 'requests' library is not installed.")
        print("Please install it by running: pip install requests")
        sys.exit(1)

    download_files() 