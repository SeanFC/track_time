"""Add data to the data base"""

from math import ceil

import pandas as pd

from track_time.settings import base_path, data_file_path


# TODO: Give better name
def get_as_nearest_time_string(time, nearest_time_interval=5):
    cur_start_hour = time.hour
    cur_start_minute = round(time.minute / nearest_time_interval) * nearest_time_interval

    # TODO:Near midnight problem, try and have python lib handle this time stuff
    if cur_start_minute > 60 - nearest_time_interval:
        cur_start_hour += 1
        cur_start_minute = 0

    time_indicator = str(cur_start_hour) + ":" + str(cur_start_minute)

    if cur_start_minute < 10:
        time_indicator = str(cur_start_hour) + ":0" + str(cur_start_minute)
    if cur_start_hour < 10:
        time_indicator = "0" + time_indicator

    return time_indicator


def get_timedelta_minute_string(td):
    return str(ceil(td.total_seconds() / 60))


def save_timed_project(file_path, date_string, start_time_string, minutes_to_wait, name_string):
    split_name = name_string.split(",")

    group_name = split_name[0].strip()
    project_name = split_name[1].strip() if len(split_name) > 1 else None
    extra = split_name[2].strip() if len(split_name) > 2 else None

    dat = {
        "date": [date_string],
        "start_time": [start_time_string],
        "time_spend": [minutes_to_wait],
        "group_name": [group_name],
        "project_name": [project_name],
        "extra": [extra],
    }
    new_data = pd.DataFrame(data=dat)

    with open(file_path, "a") as csv_file_handler:
        new_data.to_csv(csv_file_handler, mode="a", header=False, index=False)
