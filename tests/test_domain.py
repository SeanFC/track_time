from datetime import date, time

import numpy as np
import pandas as pd

from track_time.domain import create_overall_dashboard


def test_overall_dashboard():

    columns = ["date", " start_time", " time_spent", " group_name", " project_name", " extra"]
    raw_data = np.array(
        [
            [date(2019, 5, 21), time(14, 5), 20, "first", "cool", "meeting"],
            [date(2019, 5, 21), time(14, 25), 20, "second", "cool", "coding"],
            [date(2019, 5, 21), time(14, 45), 20, "first", "cool", "meeting"],
            [date(2019, 5, 21), time(15, 5), 20, "second", "cool", "meeting"],
            [date(2019, 5, 21), time(15, 25), 20, "first", "boring", "coding"],
        ]
    )

    data = pd.DataFrame(raw_data, columns=columns)

    filter = {
        "start_time": None,
        "detail_level": "group_name",
        "higher_level_selection_filter": None,
    }

    create_overall_dashboard(data, filter)
