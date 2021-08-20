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


def monthly_weekly_daily_plots(plot_type, figax=None):
    # Pull in project data
    parser = lambda date: dt.datetime.strptime(date, '%y%m%d')
    proj_data = pd.read_csv(settings.data_file_path, parse_dates=['date'], date_parser=parser)
    proj_data['group_name'] = proj_data['group_name'].str.lower()

    if plot_type == "monthly":
        base_time = dt.datetime(year = proj_data['date'][0].year, month = proj_data['date'][0].month, day=1)

        amount_of_months = int((proj_data['date'].iloc[-1] - base_time).days/31 + 2) #TODO: Unsure why +2 needed here
        date_list = [
                dt.datetime(
                    year = base_time.year + ((base_time.month +x)//12 if (base_time.month +x)//12 != (base_time.month +x)/12 else (base_time.month +x-1)//12), 
                    month = (base_time.month + x)%12 if (base_time.month + x)%12 != 0 else 12, 
                    day=1) 
                for x in range(amount_of_months)
                ]
    elif plot_type == "all_week" or plot_type == "daily":
        # Where to start from 
        #TODO: Make this an input option
        base_time = proj_data['date'][0]
        base_time = pd.Timestamp(dt.date.today() - dt.timedelta(days=31))

        amount_of_days = (proj_data['date'].iloc[-1] - base_time).days + 1
        date_list = [ base_time + dt.timedelta(days=x) for x in range(amount_of_days) ]
    else:
        print("Please enter valid plot type")
        exit()

    if not figax:
        fig, ax = plt.subplots(1,1)
    else:
        fig, ax = figax

    proj_names = proj_data['group_name'].unique()
    proj_time_by_group = np.zeros((len(proj_names), len(date_list)))

    proj_data['Grouping'] = proj_data['date'].apply(lambda x, bins: map_bin(x,bins,base_time), bins=[(x-base_time).total_seconds() for x in date_list])
    grouped_data = proj_data.groupby('Grouping')
    for group_idx, g in enumerate(grouped_data):
        cur_group = g[1]
        time_per_proj = {}
        for proj_idx, proj_name in enumerate(proj_names):
            proj_time_by_group[proj_idx, g[0]-1] = np.sum(cur_group[cur_group['group_name'] == proj_name]['time_spent'].to_numpy(dtype='int'))

    if plot_type == "monthly":
        stacked_bar_chart(ax, proj_time_by_group, proj_names)
        ax.set_xticklabels(list(map(lambda x: x.strftime("%b"), date_list)))
        ax.set_xticks(range(len(date_list)))
        ax.set_ylabel("Logged Time (m)")
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
    
    ax.legend(loc='upper left')
    return ax

def raster_plot_last_time_period(days_past=7):
    group = 'somnus'

    parser = lambda date: dt.datetime.strptime(date, '%y%m%d')
    proj_data = pd.read_csv(settings.data_file_path, parse_dates=['date'], date_parser=parser)
    import somnia.visualise as vis

    # By today we want the end of day so days past needs an extra 1 to reflect this
    min_date = dt.date.today() - dt.timedelta(days=days_past - 1)
    min_date_pd = pd.to_datetime(min_date)
    
    cur_data = proj_data[
        (dt.date.today() >= proj_data['date'].dt.date) &
        (min_date_pd <= proj_data['date'].dt.date) &
        (proj_data['group_name'] == group)
        ].copy()

    cur_data['Full Time'] = cur_data.apply(lambda x: dt.datetime(year=x['date'].year, month=x['date'].month, day=x['date'].day, hour=int(x['start_time'].split(':')[0]), minute=int(x['start_time'].split(':')[1])), axis=1)

    cur_data['Full Time'] = cur_data['Full Time'] - min_date_pd 

    import somnia.time_periods as tp

    view = vis.VariableSleepViewer([0, (days_past+1)*24*60*60], 24*60*60, start_date=min_date) # The days_part+1 here is so we can include today
    scheds = [ tp.ScheduledPeriod(row['Full Time'].total_seconds(), row['Full Time'].total_seconds() + row['time_spent']*60, tp.SleepState.awake) for idx, row in cur_data.iterrows()]

    view.add_shifts(scheds)

    def plot_marker(axes, time_h, **kwargs):
        for idx, ax in enumerate(axes):
            time = (time_h + idx*24)*60*60
            ax.plot([time, time], [0,1], linestyle='dashed', color='red')

    _ = [plot_marker(view.axes, x) for x in [9, 12, 14, 17, 18]]

    plt.show()

def graph_month_in_group_split(cur_group, figax, project_name=None):
    if not figax:
        fig, ax = plt.subplots(1,1)
    else:
        fig, ax = figax

    parser = lambda date: dt.datetime.strptime(date, '%y%m%d')
    proj_data = pd.read_csv(settings.data_file_path, parse_dates=['date'], date_parser=parser)
    proj_data = proj_data[proj_data['group_name'] == cur_group]

    min_date = dt.datetime.today() - dt.timedelta(days=31) #TOOD: 31 should change based on month
    proj_data = proj_data[proj_data['date'] >= min_date]

    # If we're given a project name then display the graph for the extra column, otherwise we show all the projects 
    column_name = 'project_name'
    if project_name is not None:
        proj_data = proj_data[proj_data['project_name'] == project_name]
        column_name='extra'

    task_names = proj_data[column_name].unique()
    task_times = [ proj_data[proj_data[column_name] == tn]['time_spent'].sum() for tn in task_names]

    ax.pie(task_times, labels=task_names)
    print(task_names)

    ax.text(0.05, 0.95, cur_group, transform=ax.transAxes, bbox={'boxstyle':'square', 'facecolor':'white'})

def create_daily_timesheet():
    cur_group = 'zentum'

    parser = lambda date: dt.datetime.strptime(date, '%y%m%d')
    proj_data = pd.read_csv(settings.data_file_path, parse_dates=['date'], date_parser=parser)
    proj_data = proj_data[proj_data['group_name'] == cur_group]

    days_to_run = 60
    min_date = dt.date.today() - dt.timedelta(days=days_to_run) 

    for days_since_start in range(days_to_run):
        cur_day = min_date + dt.timedelta(days=days_since_start) 
        cur_data = proj_data[cur_day == proj_data['date'].apply(lambda x:x.date())]

        seer_time = cur_data[cur_data['project_name'] == 'seer']['time_spent'].sum()
        safeflight_time = cur_data[cur_data['project_name'] == 'safeflight']['time_spent'].sum()
        all_time = cur_data['time_spent'].sum()

        def print_hour(time_s):
            if np.isnan(time_s):
                return "00:00"
            return str(int(time_s/60))+ ':' + str(int(np.mod(time_s, 60))) 
        print(
                cur_day, 
                print_hour(all_time), 
                print_hour(seer_time), 
                print_hour(safeflight_time),
                print_hour(8*60 * (seer_time/(safeflight_time + seer_time))),
                print_hour(8*60 * (safeflight_time/(safeflight_time + seer_time)))
                )


if __name__ == "__main__":
    create_daily_timesheet()
    exit()

    fig, axes = plt.subplots(2, 2)
    monthly_weekly_daily_plots('all_week', (fig, axes[0, 0]))
    monthly_weekly_daily_plots('monthly', (fig, axes[0, 1]))
    #monthly_weekly_daily_plots('monthly')
    #raster_plot_last_time_period(7)

    #TODO: What about the projects for these
    #TODO: These should be able on the biggest groups worked on
    #graph_month_in_group_split('sudorn', (fig, axes[1,0]))
    graph_month_in_group_split('zentum', (fig, axes[1,0]))
    graph_month_in_group_split('zentum', (fig, axes[1,1]), project_name='seer')
    plt.show()
