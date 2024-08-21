"""The main entry point"""
import argparse
from datetime import date, timedelta
from os import system
from pathlib import Path

from track_time.repos import TimesRepo
from track_time.services import (
    create_zentum_spreadsheet,
    run_timer,
    show_overall_dashboard,
    show_time_of_day_plot,
)

data_file_path = Path.home() / "projects" / "track_time" / "data" / "tt_db.csv"

ZENTUM_FILTER = {
    "start_time": date.today() - timedelta(days=365),
    "detail_level": "project_name",
    "higher_level_selection_filter": "zentum",
}
PERSONAL_FILTER = {
    "start_time": None,
    "detail_level": "group_name",
    "higher_level_selection_filter": None,
}

current_filter = ZENTUM_FILTER
# current_filter = PERSONAL_FILTER


if __name__ == "__main__":
    # Set up the possible arguments to the command line
    parser = argparse.ArgumentParser(description="Set and save task related timers")
    group_ex = parser.add_mutually_exclusive_group()
    group_ex.add_argument("-o", "--open", help="Open the database", action="store_true")
    group_ex.add_argument("-d", "--dashboard", help="Open the dashboard", action="store_true")
    args = parser.parse_args()

    repo = TimesRepo(data_file_path)

    if args.open:
        # Open the vim file of the database, the + here means we go to the end of the file,
        system(f"$EDITOR + {data_file_path}")
    elif args.dashboard:
        # create_zentum_spreadsheet(repo)
        # show_time_of_day_plot(repo)

        show_overall_dashboard(repo, current_filter)
    else:
        run_timer(repo)
