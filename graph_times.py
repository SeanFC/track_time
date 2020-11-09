import settings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt

def map_bin(x, bins, base):
    kwargs = {}
    if x == max(bins):
        kwargs['right'] = True

    return np.digitize((x-base).total_seconds(), bins, **kwargs)

def stacked_bar_chart(ax, in_data, bar_labels):
    stack_data = np.cumsum(in_data, axis=0)
    n_proj, n_group = stack_data.shape

    stack_data = np.vstack((np.zeros((1, n_group)), stack_data))

    for proj_idx in range(n_proj):
        ax.bar(np.arange(n_group), in_data[proj_idx, :], bottom=stack_data[proj_idx, :], label=bar_labels[proj_idx])


def monthly_weekly_daily_plots(plot_type):
    # Pull in project data
    parser = lambda date: pd.datetime.strptime(date, '%y%m%d')
    proj_data = pd.read_csv(settings.data_file_path, parse_dates=['date'], date_parser=parser)
    proj_data['project_name'] = proj_data['project_name'].str.lower()

    if plot_type == "monthly":
        base_time = dt.datetime(year = proj_data['date'][0].year, month = proj_data['date'][0].month, day=1)

        amount_of_months = int((proj_data['date'].iloc[-1] - base_time).days/31 + 1)
        date_list = [
                dt.datetime(
                    year = base_time.year + ((base_time.month +x)//12 if (base_time.month +x)//12 != (base_time.month +x)/12 else (base_time.month +x-1)//12), 
                    month = (base_time.month + x)%12 if (base_time.month + x)%12 != 0 else 12, 
                    day=1) 
                for x in range(amount_of_months)
                ]
    elif plot_type == "all_week" or plot_type == "daily":
        base_time = proj_data['date'][0]
        amount_of_days = (proj_data['date'].iloc[-1] - base_time).days + 1
        date_list = [ base_time + dt.timedelta(days=x) for x in range(amount_of_days) ]
    else:
        print("Please enter valid plot type")
        exit()

    fig, ax = plt.subplots(1,1)

    proj_names = proj_data['project_name'].unique()
    proj_time_by_group = np.zeros((len(proj_names), len(date_list)))

    proj_data['Grouping'] = proj_data['date'].apply(lambda x, bins: map_bin(x,bins,base_time), bins=[(x-base_time).total_seconds() for x in date_list])
    grouped_data = proj_data.groupby('Grouping')
    for group_idx, g in enumerate(grouped_data):
        cur_group = g[1]
        time_per_proj = {}
        for proj_idx, proj_name in enumerate(proj_names):
            proj_time_by_group[proj_idx, g[0]-1] = np.sum(cur_group[cur_group['project_name'] == proj_name]['time_spent'].to_numpy(dtype='int'))

    if plot_type == "monthly":
        stacked_bar_chart(ax, proj_time_by_group, proj_names)
        ax.set_xticklabels(list(map(lambda x: x.strftime("%B"), date_list)))
        ax.set_xticks(range(len(date_list)))
        ax.set_ylabel("Longed Time (m)")
    elif plot_type == "daily":
        stacked_bar_chart(ax, proj_time_by_group, proj_names)
    elif plot_type == "all_week":
        weekly_proj_times = np.zeros((proj_time_by_group.shape[0], 7))

        for i in np.arange(7):
            weekly_proj_times[:, i] = np.sum(proj_time_by_group[:, i::7], axis=1)/proj_time_by_group.shape[1]*7/60
        stacked_bar_chart(ax, weekly_proj_times[:, [-1, *(np.arange(6))]], proj_names)
        ax.set_xticklabels(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        ax.set_xticks(np.arange(0, 7))
        ax.set_ylabel('Time Spent (h)')
    
    ax.legend()
    plt.show()

def raster_plot_last_time_period(days_past=7):
    group = 'somnus'
    import datetime as dt

    parser = lambda date: dt.datetime.strptime(date, '%y%m%d')
    proj_data = pd.read_csv(settings.data_file_path, parse_dates=['date'], date_parser=parser)
    import somnia.visualise as vis
    
    cur_data = proj_data[
        (dt.date.today() - proj_data['date'].dt.date < np.timedelta64(days_past, 'D')) &
        (dt.date.today() - proj_data['date'].dt.date > np.timedelta64(-1, 'D')) &
        (proj_data['project_name'] == group)
        ].copy()
    cur_data['Full Time'] = cur_data.apply(lambda x: dt.datetime(year=x['date'].year, month=x['date'].month, day=x['date'].day, hour=int(x['start_time'].split(':')[0]), minute=int(x['start_time'].split(':')[1])), axis=1)
    cur_data['Full Time'] = cur_data['Full Time'] - cur_data['date'].min()

    import somnia.time_periods as tp

    view = vis.VariableSleepViewer([0, days_past*24*60*60], 24*60*60, start_date=cur_data['date'].min())
    scheds = [ tp.ScheduledPeriod(row['Full Time'].total_seconds(), row['Full Time'].total_seconds() + row['time_spent']*60, tp.SleepState.awake) for idx, row in cur_data.iterrows()]

    view.add_shifts(scheds)
    plt.show()
    #proj_data[dt.date.today() - proj_data['date'] < days_past]


if __name__ == "__main__":
    #monthly_weekly_daily_plots('monthly')
    raster_plot_last_time_period()
