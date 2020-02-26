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

def stacked_bar_chart(in_data, bar_labels):
    stack_data = np.cumsum(in_data, axis=0)
    n_proj, n_group = stack_data.shape

    stack_data = np.vstack((np.zeros((1, n_group)), stack_data))

    for proj_idx in range(n_proj):
        plt.bar(np.arange(n_group), in_data[proj_idx, :], bottom=stack_data[proj_idx, :], label=bar_labels[proj_idx])

if __name__ == "__main__":
    #plot_type = "monthly" 
    plot_type = "all_week" 
    #plot_type = "daily"

    # Pull in project data
    parser = lambda date: pd.datetime.strptime(date, '%y%m%d')
    proj_data = pd.read_csv(settings.data_file_path, parse_dates=['date'], date_parser=parser)
    proj_data['project_name'] = proj_data['project_name'].str.lower()

    if plot_type == "monthly":
        base_time = dt.datetime(year = proj_data['date'][0].year, month = proj_data['date'][0].month, day=1)
        date_list = [
                dt.datetime(
                    year = base_time.year + ((base_time.month +x)//12 if (base_time.month +x)//12 != (base_time.month +x)/12 else (base_time.month +x-1)//12), 
                    month = (base_time.month + x)%12 if (base_time.month + x)%12 != 0 else 12, 
                    day=1) 
                for x in range(8)
                ]
    elif plot_type == "all_week" or plot_type == "daily":
        base_time = proj_data['date'][0]
        date_list = [ base_time + dt.timedelta(days=x) for x in range(223) ]
    else:
        print("Please event valid plot type")
        exit()

    proj_names = proj_data['project_name'].unique()
    proj_time_by_group = np.zeros((len(proj_names), len(date_list)))

    proj_data['Grouping'] = proj_data['date'].apply(lambda x, bins: map_bin(x,bins,base_time), bins=[(x-base_time).total_seconds() for x in date_list])
    grouped_data = proj_data.groupby('Grouping')
    for group_idx, g in enumerate(grouped_data):
        cur_group = g[1]
        time_per_proj = {}
        for proj_idx, proj_name in enumerate(proj_names):
            proj_time_by_group[proj_idx, g[0]-1] = np.sum(cur_group[cur_group['project_name'] == proj_name]['time_spent'].to_numpy(dtype='int'))

    if plot_type == "monthly" :
        stacked_bar_chart(proj_time_by_group, proj_names)
        plt.gca().set_xticklabels(list(map(lambda x: x.strftime("%B"), [base_time, *date_list] )))
    elif plot_type == "daily":
        stacked_bar_chart(proj_time_by_group, proj_names)
    elif plot_type == "all_week":
        weekly_proj_times = np.zeros((5, 7))
        for i in np.arange(7):
            weekly_proj_times[:, i] = np.sum(proj_time_by_group[:, i::7], axis=1)
        stacked_bar_chart(weekly_proj_times[:, [-1, *(np.arange(6))]], proj_names)

    plt.legend()
    plt.show()
