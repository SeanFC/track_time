from datetime import date, datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

_DETAIL_LEVELS = ["group_name", "project_name", "extra"]


def map_bin(x, bins, base):
    kwargs = {}
    if x == max(bins):
        kwargs["right"] = True

    return np.digitize((x - base).total_seconds(), bins, **kwargs)


def stacked_bar_chart(ax, in_data, bar_labels):
    stack_data = np.cumsum(in_data, axis=0)
    n_proj, n_group = stack_data.shape

    # Change times to % relative of longest bar
    max_time = stack_data.max()
    stack_data /= max_time / 100
    in_data /= max_time / 100

    stack_data = np.vstack((np.zeros((1, n_group)), stack_data))
    for proj_idx in range(n_proj):
        ax.bar(
            np.arange(n_group),
            in_data[proj_idx, :],
            bottom=stack_data[proj_idx, :],
            label=bar_labels[proj_idx],
        )


def monthly_weekly_daily_plots(
    proj_data,
    plot_type,
    figax=None,
    start_time=None,
    detail_level=_DETAIL_LEVELS[0],
    higher_level_selection_filter=None,
):
    # Restrict to starting at the start time
    if start_time is not None:
        proj_data = proj_data[proj_data["date"] >= pd.Timestamp(start_time)]

    # Filter none relevant selections
    if detail_level != _DETAIL_LEVELS[0] and higher_level_selection_filter is not None:
        higher_level_index = _DETAIL_LEVELS.index(detail_level) - 1
        proj_data = proj_data[
            proj_data[_DETAIL_LEVELS[higher_level_index]] == higher_level_selection_filter
        ]

    # Turn all the detail levels to lower case
    for level in _DETAIL_LEVELS:
        proj_data[level] = proj_data[level].str.lower()

    proj_data = proj_data.sort_values(by="date")

    if plot_type == "monthly":
        base_time = datetime(
            year=proj_data["date"].iloc[0].year,
            month=proj_data["date"].iloc[0].month,
            day=1,
        )

        # TODO: Unsure why +2 needed here
        amount_of_months = int((proj_data["date"].iloc[-1] - base_time).days / 31 + 2)
        date_list = [
            datetime(
                year=base_time.year
                + (
                    (base_time.month + x) // 12
                    if (base_time.month + x) // 12 != (base_time.month + x) / 12
                    else (base_time.month + x - 1) // 12
                ),
                month=(base_time.month + x) % 12 if (base_time.month + x) % 12 != 0 else 12,
                day=1,
            )
            for x in range(amount_of_months)
        ]
    elif plot_type == "all_week" or plot_type == "daily":
        # The first day is the first month before a month ago
        base_time = pd.Timestamp(date.today() - timedelta(days=31 - date.today().weekday() - 1))

        amount_of_days = (proj_data["date"].iloc[-1] - base_time).days + 1
        date_list = [base_time + timedelta(days=x) for x in range(amount_of_days)]
    else:
        print("Please enter valid plot type")
        # TODO: Poor design flow
        exit()

    if not figax:
        fig, ax = plt.subplots(1, 1)
    else:
        fig, ax = figax

    proj_names = proj_data[detail_level].unique()
    proj_time_by_group = np.zeros((len(proj_names), len(date_list)))

    proj_data["Grouping"] = proj_data["date"].apply(
        lambda x, bins: map_bin(x, bins, base_time),
        bins=[(x - base_time).total_seconds() for x in date_list],
    )
    grouped_data = proj_data.groupby("Grouping")
    for group_idx, g in enumerate(grouped_data):
        cur_group = g[1]
        for proj_idx, proj_name in enumerate(proj_names):
            proj_time_by_group[proj_idx, g[0] - 1] = np.sum(
                cur_group[cur_group[detail_level] == proj_name]["time_spent"].to_numpy(dtype="int")
            )

    if plot_type == "monthly":
        stacked_bar_chart(ax, proj_time_by_group / 60, proj_names)
        ax.xaxis.set_major_locator(mticker.FixedLocator(range(len(date_list))))
        ax.set_xticklabels(list(map(lambda x: x.strftime("%b"), date_list)))
    elif plot_type == "daily":
        stacked_bar_chart(ax, proj_time_by_group, proj_names)
    elif plot_type == "all_week":
        weekly_proj_times = np.zeros((proj_time_by_group.shape[0], 7))

        for i in np.arange(7):
            datelist[i].weekday()
            weekly_proj_times[:, day_of_week_number] = (
                np.sum(proj_time_by_group[:, i::7], axis=1) / proj_time_by_group.shape[1] * 7 / 60
            )
        stacked_bar_chart(ax, weekly_proj_times, proj_names)

        ax.xaxis.set_major_locator(mticker.FixedLocator(np.arange(0, 7)))
        ax.set_xticklabels(["Mon", "Tues", "Wed", "Thu", "Fri", "Sat", "Sun"])

    ax.set_ylabel("Time Spent (% Rel to Max)")

    ax.legend()
    return ax


def graph_month_in_group_split(proj_data, cur_group=None, figax=None, project_name=None):
    if not figax:
        fig, ax = plt.subplots(1, 1)
    else:
        fig, ax = figax

    if not cur_group is None:
        proj_data = proj_data[proj_data["group_name"] == cur_group]

    min_date = datetime.today() - timedelta(days=31)  # TOOD: 31 should change based on month
    proj_data = proj_data[proj_data["date"] >= min_date]

    # If we're given a project name then display the graph for the extra column, otherwise we show all the projects
    column_name = "project_name"
    if project_name is not None:
        proj_data = proj_data[proj_data["project_name"] == project_name]
        column_name = "extra"

    task_names = proj_data[column_name].unique()
    task_times = [
        proj_data[proj_data[column_name] == tn]["time_spent"].astype(float).sum()
        for tn in task_names
    ]
    ax.pie(task_times, labels=task_names)

    pie_graph_title = cur_group
    if project_name is not None:
        pie_graph_title += " - " + project_name
    ax.text(
        0.05,
        0.95,
        pie_graph_title,
        transform=ax.transAxes,
        bbox={"boxstyle": "square", "facecolor": "white"},
    )


# TODO: Output shuuld be configurable
def create_daily_zentum_timesheet(proj_data):
    cur_group = "zentum"
    proj_data = proj_data[proj_data["group_name"] == cur_group]

    days_to_run = 150
    min_date = date.today() - timedelta(days=days_to_run)

    daily_table = pd.DataFrame(
        columns=[
            "Date",
            "Time Worked",
            "SEER",
            "Safeflight",
            "SEER 8h",
            "Safeflight 8h",
        ]
    )
    for days_since_start in range(days_to_run + 1):
        cur_day = min_date + timedelta(days=days_since_start)
        cur_data = proj_data[cur_day == proj_data["date"].apply(lambda x: x.date())]

        seer_time = (
            cur_data[
                (cur_data["project_name"] == "seer")
                | (cur_data["project_name"] == "web tool")
                | (cur_data["project_name"] == "rie")
                | (cur_data["project_name"] == "via")
            ]["time_spent"]
            .astype(float)
            .sum()
        )
        safeflight_time = (
            cur_data[
                (cur_data["project_name"] == "safeflight")
                | (cur_data["project_name"] == "alias")
                | (cur_data["project_name"] == "flyte")
                | (cur_data["project_name"] == "linny")
                | (cur_data["project_name"] == "all")
            ]["time_spent"]
            .astype(float)
            .sum()
        )

        all_time = cur_data["time_spent"].astype(float).sum()

        def print_hour(time_s):
            if np.isnan(time_s):
                return "00:00"
            return str(int(time_s / 60)) + ":" + str(int(np.mod(time_s, 60)))

        ratio_denominator = safeflight_time + seer_time
        if ratio_denominator != 0:
            ratio_seer_time = seer_time / ratio_denominator
            ratio_safeflight_time = safeflight_time / ratio_denominator
        else:
            ratio_seer_time = 0
            ratio_safeflight_time = 0

        daily_table = pd.concat(
            [
                daily_table,
                pd.DataFrame(
                    [
                        {
                            "Date": cur_day,
                            "Time Worked": print_hour(all_time),
                            "SEER": print_hour(seer_time),
                            "Safeflight": print_hour(safeflight_time),
                            "SEER 8h": print_hour(8 * 60 * ratio_seer_time),
                            "Safeflight 8h": print_hour(8 * 60 * ratio_safeflight_time),
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    with pd.option_context(
        "display.max_rows",
        None,
        "display.max_columns",
        None,
        "display.width",
        1000,
        "display.precision",
        3,
        "display.colheader_justify",
        "center",
    ):
        daily_table.T.to_csv("/tmp/cur.csv")


def create_time_of_day_plot(proj_data, start_time: datetime):
    """
    Plot the time of day that work is getting done

    :param proj_data: TODO
    :param start_time: The starting time in the dataset. Data before this time is ignored.
    """
    # Restrict to starting at the start time
    if start_time is not None:
        proj_data = proj_data[proj_data["date"] >= pd.Timestamp(start_time)]

    minutes_in_day = 24 * 60
    time_spent_in_minute = np.zeros(minutes_in_day)

    for idx, row in proj_data.iterrows():
        split_time = row["start_time"].split(":")
        start_time = int(split_time[0]) * 60 + int(split_time[1])
        duration = int(row["time_spent"])
        # minutes_indices = np.arange(duration)+start_time
        time_spent_in_minute[start_time : (start_time + duration)] += 1

    # plt.bar(np.arange(24*60)/60, time_spent_in_minute)
    plt.bar(
        np.arange(minutes_in_day) / 60,
        time_spent_in_minute / np.sum(time_spent_in_minute),
    )
    plt.xlabel("Time of day (hours)")
    plt.ylabel("Minutes spent working (density)")
    plt.xlim([0, 24])

    plt.gca().xaxis.set_major_locator(mticker.FixedLocator(range(24)))
    plt.grid()

    plt.show()


def create_overall_dashboard(proj_data, current_filter):
    fig, axes = plt.subplots(2, 3)
    axes[0, 0].set_title("All time")
    monthly_weekly_daily_plots(proj_data, "all_week", (fig, axes[0, 0]), **current_filter)
    monthly_weekly_daily_plots(proj_data, "monthly", (fig, axes[1, 0]), **current_filter)
    # monthly_weekly_daily_plots('monthly')
    # raster_plot_last_time_period(7)

    # TODO: These should be on the biggest groups worked on
    axes[0, 1].set_title("Last Month")
    axes[0, 2].set_title("Last Month")

    group = current_filter["higher_level_selection_filter"]
    graph_month_in_group_split(proj_data, group, (fig, axes[0, 1]), project_name="all")
    graph_month_in_group_split(proj_data, group, (fig, axes[1, 1]), project_name="rad")
    graph_month_in_group_split(proj_data, group, (fig, axes[0, 2]), project_name="dynamo")
    graph_month_in_group_split(proj_data, group, (fig, axes[1, 2]), project_name="flyte")
    plt.show()
