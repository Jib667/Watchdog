import os
import subprocess
import sys
import shutil
from datetime import date # Import date

# --- Configuration ---
# Repository to clone
CONGRESS_REPO_URL = "https://github.com/unitedstates/congress.git"

# Determine the Watchdog project root directory (where the backend/ folder resides)
WATCHDOG_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Target directory for cloning the congress repo (within Watchdog project)
CONGRESS_TOOLS_DIR = os.path.join(WATCHDOG_ROOT_DIR, "congress_tools")

# Virtual environment name within the congress_tools directory
VENV_NAME = "env"

# Start Congress number for historical data
HISTORICAL_START_CONGRESS = 101

# Data types to fetch
DATA_TYPES = ["bills", "votes"]

# Target directory for Watchdog's data
WATCHDOG_DATA_DIR = os.path.join(WATCHDOG_ROOT_DIR, "backend", "app", "static", "congress_data")

# Define colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
NC = '\033[0m' # No Color
# --- End Configuration ---

def print_color(color, message):
    """Prints a message in a specific color."""
    print(f"{color}{message}{NC}")

def run_command(command, cwd=None, venv_path=None, capture_output=False):
    """Runs a shell command, optionally in a specific directory and venv."""
    env = os.environ.copy()
    cmd_str = " ".join(command)
    print_color(YELLOW, f"Running command: {cmd_str}" + (f" in {cwd}" if cwd else ""))

    if venv_path:
        # Modify PATH to prioritize the venv's bin directory
        venv_bin = os.path.join(venv_path, 'bin')
        env['PATH'] = f"{venv_bin}:{env.get('PATH', '')}"
        env['VIRTUAL_ENV'] = venv_path # Also set VIRTUAL_ENV for convention

    try:
        process = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            check=True, # Raise exception on non-zero exit code
            capture_output=capture_output,
            text=True
        )
        if capture_output:
            print(process.stdout)
            if process.stderr:
                print_color(YELLOW, f"Stderr:\n{process.stderr}")
        print_color(GREEN, f"Command successful: {cmd_str}")
        return True
    except FileNotFoundError as e:
        print_color(RED, f"Error: Command not found - {command[0]}. Is it installed and in PATH? {e}")
        return False
    except subprocess.CalledProcessError as e:
        print_color(RED, f"Error: Command failed with exit code {e.returncode}: {cmd_str}")
        if e.stdout:
            print_color(RED, f"Stdout:\n{e.stdout}")
        if e.stderr:
            print_color(RED, f"Stderr:\n{e.stderr}")
        return False
    except Exception as e:
        print_color(RED, f"An unexpected error occurred running command {cmd_str}: {e}")
        return False

def check_system_dependencies():
    """Performs basic checks for known system dependencies."""
    print_color(YELLOW, "Checking for essential system dependencies...")
    dependencies = ["git", "python3", "pip3", "wget"] # Add others if known
    all_found = True
    for dep in dependencies:
        if shutil.which(dep) is None:
            print_color(RED, f"Error: System dependency '{dep}' not found in PATH.")
            all_found = False

    if not all_found:
        print_color(RED, "Please install the missing system dependencies before proceeding.")
        print_color(RED, "(e.g., using 'apt-get install git python3 python3-pip wget' on Debian/Ubuntu")
        print_color(RED, " or 'brew install wget' on macOS if needed).")
        print_color(RED, "Also ensure libxml2-dev, libxslt1-dev, libz-dev are installed (Debian/Ubuntu names)." )
        return False
    print_color(GREEN, "Basic system dependencies seem to be present.")
    return True

def copy_generated_data(congress_number):
    """Copies generated data from congress_tools/data to the watchdog data dir."""
    source_data_dir = os.path.join(CONGRESS_TOOLS_DIR, 'data', congress_number)
    target_data_dir = os.path.join(WATCHDOG_DATA_DIR, 'congress', congress_number)

    print_color(YELLOW, f"\n--- Copying Generated Data --- ")
    print_color(YELLOW, f"Source: {source_data_dir}")
    print_color(YELLOW, f"Target: {target_data_dir}")

    if not os.path.isdir(source_data_dir):
        print_color(RED, f"Error: Source data directory {source_data_dir} not found. Did usc-run succeed?")
        return False

    try:
        # Ensure target subdirectory exists (e.g., backend/app/static/congress_data/congress/119)
        os.makedirs(target_data_dir, exist_ok=True)
        # Copy the entire contents of the source congress directory
        # shutil.copytree is suitable for copying directory contents
        # dirs_exist_ok=True allows overwriting/merging into the target directory
        shutil.copytree(source_data_dir, target_data_dir, dirs_exist_ok=True)
        print_color(GREEN, f"Successfully copied data to {target_data_dir}")
        return True
    except Exception as e:
        print_color(RED, f"Error copying data from {source_data_dir} to {target_data_dir}: {e}")
        return False

def calculate_current_congress() -> int:
    """Calculates the current Congress number based on today's date."""
    today = date.today()
    year = today.year
    month = today.month
    day = today.day

    # Determine the starting year of the current Congress term
    if year % 2 != 0: # Odd year
        if month == 1 and day < 3:
            # It's early Jan of an odd year, the previous Congress is just ending
            start_year = year - 2
        else:
            # It's later in an odd year, this Congress started this year
            start_year = year
    else: # Even year
        # The current Congress started the previous odd year
        start_year = year - 1

    # Calculate Congress number (1st Congress started in 1789)
    # N = floor((start_year - 1789) / 2) + 1
    congress_number = ((start_year - 1789) // 2) + 1
    return congress_number

def main():
    print_color(GREEN, "--- Starting Bill/Vote Data Update Process ---")

    if not check_system_dependencies():
        sys.exit(1)

    # --- Step 1: Clone or Update congress repository ---
    print_color(YELLOW, f"\n--- Step 1: Ensuring '{CONGRESS_TOOLS_DIR}' exists and is up-to-date ---")
    if not os.path.isdir(CONGRESS_TOOLS_DIR):
        print_color(YELLOW, f"Cloning {CONGRESS_REPO_URL} into {CONGRESS_TOOLS_DIR}...")
        if not run_command(["git", "clone", CONGRESS_REPO_URL, CONGRESS_TOOLS_DIR]):
            print_color(RED, "Failed to clone the repository.")
            sys.exit(1)
    else:
        print_color(YELLOW, f"Updating existing repository in {CONGRESS_TOOLS_DIR}...")
        if not run_command(["git", "pull"], cwd=CONGRESS_TOOLS_DIR):
            # Don't exit on pull failure, maybe repo is usable anyway?
            print_color(YELLOW, "Warning: 'git pull' failed. Trying to proceed anyway...")

    # --- Step 2: Set up Virtual Environment --- 
    print_color(YELLOW, f"\n--- Step 2: Setting up Python Virtual Environment in {CONGRESS_TOOLS_DIR} ---")
    venv_path = os.path.join(CONGRESS_TOOLS_DIR, VENV_NAME)
    if not os.path.isdir(venv_path):
        print_color(YELLOW, f"Creating virtual environment '{VENV_NAME}'...")
        if not run_command(["python3", "-m", "venv", VENV_NAME], cwd=CONGRESS_TOOLS_DIR):
            print_color(RED, "Failed to create virtual environment.")
            sys.exit(1)
    else:
        print_color(YELLOW, f"Virtual environment '{VENV_NAME}' already exists.")

    # --- Step 3: Install Dependencies --- 
    print_color(YELLOW, f"\n--- Step 3: Installing dependencies using pip install . ---")
    # Construct pip path within the venv
    pip_executable = os.path.join(venv_path, 'bin', 'pip')
    if not run_command([pip_executable, "install", "."], cwd=CONGRESS_TOOLS_DIR):
        print_color(RED, "Failed to install dependencies via 'pip install .'.")
        sys.exit(1)

    # --- Determine Congresses to Process --- 
    actual_current_congress = calculate_current_congress()
    actual_current_congress_str = str(actual_current_congress)
    print_color(YELLOW, f"Calculated current Congress: {actual_current_congress_str}")

    # Define the full historical range dynamically up to the current calculated Congress
    full_historical_congress_numbers = [str(i) for i in range(HISTORICAL_START_CONGRESS, actual_current_congress + 1)]

    marker_dir = os.path.join(WATCHDOG_DATA_DIR, 'congress', actual_current_congress_str)
    
    congresses_to_process = []
    if os.path.isdir(marker_dir):
        print_color(YELLOW, f"Marker directory for current Congress ('{marker_dir}') found. Assuming subsequent run.")
        print_color(YELLOW, f"Updating only the current Congress: {actual_current_congress_str}")
        congresses_to_process = [actual_current_congress_str]
    else:
        print_color(YELLOW, f"Marker directory '{marker_dir}' not found. Performing initial historical run.")
        print_color(YELLOW, f"Processing Congresses: {full_historical_congress_numbers[0]} through {actual_current_congress_str}")
        congresses_to_process = full_historical_congress_numbers # Process the full range

    # --- Step 4: Run Data Collection --- 
    print_color(YELLOW, f"\n--- Step 4: Running data collection for designated Congresses ---")
    usc_run_executable = os.path.join(venv_path, 'bin', 'usc-run')
    collection_success = True # Overall success flag

    # Loop through the determined list of Congress numbers
    for congress_num in congresses_to_process:
        print_color(YELLOW, f"\n--- Processing Congress {congress_num} ---")
        congress_data_found_for_this_session = False # Reset for each session
        for data_type in DATA_TYPES:
            print_color(YELLOW, f"Running for data type: {data_type}")
            cmd = [usc_run_executable, data_type, f"--congress={congress_num}", "--collections"]
            if not run_command(cmd, cwd=CONGRESS_TOOLS_DIR):
                print_color(RED, f"Failed to collect '{data_type}' data for Congress {congress_num}.")
                collection_success = False # Mark overall failure if any command fails
            else:
                congress_data_found_for_this_session = True 
        
        # --- Step 5: Copy Generated Data (Inside Congress Loop) --- 
        if congress_data_found_for_this_session:
            copy_generated_data(congress_num)
        else:
             print_color(YELLOW, f"Skipping data copy for Congress {congress_num} as collection commands failed or yielded no data.")

    # --- Step 6: Finish --- 
    print_color(GREEN, "\n--- Bill/Vote Data Update Process Finished ---")
    if collection_success:
        print_color(GREEN, "Data collection and copying process completed.")
        print_color(GREEN, f"Check logs above for details on individual Congress sessions.")
        print_color(GREEN, f"Generated data should be located in subdirectories within: {os.path.join(WATCHDOG_DATA_DIR, 'congress')}")
    else:
        print_color(RED, "One or more collection or copying steps failed. Please review the errors above.")

if __name__ == "__main__":
    main() 