"""The main entry point"""
import argparse

from track_time.services import run_timer
from track_time.settings import base_path, data_file_path

if __name__ == "__main__":
    # Set up the possible arguments to the command line
    parser = argparse.ArgumentParser(description="Set and save task related timers")
    parser.add_argument("-o", "--open", help="Open the database", action="store_true")
    args = parser.parse_args()

    if not path.exists(base_path):
        makedirs(base_path)

    if args.open:
        # Open the vim file of the database, the + here means we go to the end of the file,
        system(f"$EDITOR {data_file_path}")
        sys.exit()

    run_timer(data_file_path)
