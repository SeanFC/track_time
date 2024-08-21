from datetime import datetime

import pandas as pd

from track_time.collect import (
    get_as_nearest_time_string,
    get_timedelta_minute_string,
    save_timed_project,
)


def run_timer(data_file_path):
    project_name = input("Enter project name: ")
    time_spent_delta = datetime.now() - start_time
    time_spent = get_timedelta_minute_string(time_spent_delta)
    time_spent = 0 if time_spent_delta.seconds < 60 else time_spent

    nearest_time_string = get_as_nearest_time_string(start_time, 1)
    if not project_name and not time_spent:
        print(
            f"ERROR: For event at {nearest_time_string} no time or project name has been given and the event was less that 1 minute"
        )
        exit()
    elif not project_name:
        print(
            f"ERROR: {nearest_time_string},{time_spent} event not saved since no project name given"
        )
        exit()
    elif not time_spent:
        print(
            f"ERROR: Event {nearest_time_string},0,{project_name} not saved since less than a minute long"
        )
        exit()

    save_timed_project(
        data_file_path,
        date_string,
        newest_time_String,
        time_spent,
        project_name,
    )
