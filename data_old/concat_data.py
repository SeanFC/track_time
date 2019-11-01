#!/bin/python3

from glob import glob
from os import system, path, makedirs
import settings
import ntpath
import csv
import numpy as np

import pandas as pd

data_files = glob(path.join(settings.base_path+'_bk', '*.csv'))
test_files = ['/home/sean/projects/track_time/data/190808.csv']

df = pd.DataFrame(columns=('start_time', 'time_spent', 'project_name', 'extra', 'date'))

for file_path in data_files:
#for file_path in test_files:

    f = pd.read_csv(file_path, names=('start_time', 'time_spent', 'project_name', 'extra'))
    file_date = path.splitext(path.basename(file_path))[0]

    f['date'] = file_date

    df = df.append(f, ignore_index=True)

# Reposition the columns 
cols = df.columns.to_list()
cols = cols[-1:] + cols[:-1]
df = df[cols]

# Put the values in the right order and sort out the indicies
df.sort_values(['date', 'start_time'], axis=0, inplace=True, ascending=True, kind='quicksort')
#df = df.set_index(pd.Series(np.arange(0, df.shape[0]))) # We no longer bother with index so this isn't needed

# Save the data file
df.to_csv(settings.data_file_path, index=False)
