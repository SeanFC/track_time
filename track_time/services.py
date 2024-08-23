from datetime import date, datetime, timedelta
from typing import Callable

import pandas as pd

from track_time.domain import (
    create_daily_zentum_timesheet,
    create_overall_dashboard,
    create_time_of_day_plot,
)
from track_time.repos import (
    TimesRepo,
    get_as_nearest_time_string,
    get_timedelta_minute_string,
)


def run_timer(
    repo: TimesRepo,
    input_service: Callable[[str], str] = input,
    now_time_service: Callable[[], datetime] = datetime.now,
):
    start_time = now_time_service()
    date_string = start_time.strftime("%y%m%d")
    project_name = input_service("Enter project name: ")

    time_spent_delta = now_time_service() - start_time
    time_spent = get_timedelta_minute_string(time_spent_delta)
    time_spent = 0 if time_spent_delta.seconds < 60 else time_spent
    nearest_time_string = get_as_nearest_time_string(start_time, 1)

    if not project_name and not time_spent:
        raise RuntimeError(
            f"ERROR: For event at {nearest_time_string} no time or project name has been given "
            + "and the event was less that 1 minute"
        )
        return
    elif not project_name:
        raise RuntimeError(
            f"ERROR: {nearest_time_string},{time_spent} event not saved since no project name given"
        )
    elif not time_spent:
        raise RuntimeError(
            f"ERROR: Event {nearest_time_string},0,{project_name} not saved since less than a "
            + "minute long"
        )

    repo.add(date_string, nearest_time_string, time_spent, project_name)


def create_zentum_spreadsheet(data: TimesRepo):
    create_daily_zentum_timesheet(data.get())


def show_time_of_day_plot(data: TimesRepo):
    create_time_of_day_plot(data.get(), date.today() - timedelta(days=365))


def show_overall_dashboard(data: TimesRepo, filter):
    create_overall_dashboard(data.get(), filter)
