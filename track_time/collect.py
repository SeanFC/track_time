"""Add data to the data base"""
from os import system, path, makedirs
from datetime import datetime, timedelta
from time import sleep
import csv
import sys
import argparse
from glob import glob
from math import ceil

import pandas as pd
from .settings import base_path, data_file_path

#TODO: Give better name
def get_as_nearest_time_string(time, nearest_time_interval=5):
    cur_start_hour = time.hour
    cur_start_minute = round(time.minute/nearest_time_interval)*nearest_time_interval

    #TODO:Near midnight problem, try and have python lib handle this time stuff
    if cur_start_minute > 60 - nearest_time_interval:
        cur_start_hour += 1
        cur_start_minute = 0

    time_indicator = str(cur_start_hour) + ":" + str(cur_start_minute) 

    if cur_start_minute < 10: time_indicator = str(cur_start_hour) + ":0" + str(cur_start_minute)
    if cur_start_hour < 10: time_indicator = '0' + time_indicator

    return time_indicator

def get_timedelta_minute_string(td):
    return str(ceil(td.total_seconds()/60))

def save_timed_project(file_path, date_string, start_time_string, minutes_to_wait, name_string):
    split_name = name_string.split(',')

    group_name = split_name[0].strip()
    project_name = split_name[1].strip() if len(split_name) > 1 else None
    extra = split_name[2].strip() if len(split_name) > 2 else None

    dat = {
            'date': [date_string], 
            'start_time': [start_time_string], 
            'time_spend':[minutes_to_wait], 
            'group_name':[group_name],
            'project_name': [project_name],
            'extra': [extra]
            }
    new_data = pd.DataFrame(data=dat)

    with open(file_path, 'a') as csv_file_handler:
        new_data.to_csv(csv_file_handler, mode='a', header=False, index=False)

def main_start():
    # Set up the possible arguments to the command line
    parser = argparse.ArgumentParser(description="Set and save task related timers")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-n", "--project_name", help="The project this task is associated to", default="Other")
    group.add_argument("-p", "--list_projects", help="List previous projects", action="store_true" )
    group.add_argument("-u", "--count_up", help="Time up for 0 till asked to stop", action="store_true")
    group.add_argument("-o", "--open", help="Open today\'s time tracking file", action="store_true")
    parser.add_argument("-s", "--subscribe", help="Count down the current timer", action="store_true" )
    parser.add_argument("-l", "--length", type=int, help="The length of the task in minutes", default=20)

    args = parser.parse_args()

    # Set parameters 
    app_name = "Tasking Time"
    minutes_to_wait = args.length
    round_to_time_interval = 5

    # Find conditional parameters
    start_time = datetime.now()
    date_string = start_time.strftime("%y%m%d")

    if not path.exists(base_path):
        makedirs(base_path)

    file_name = date_string + '.csv'
    file_path = path.join(base_path, file_name)
    #file_path = 'test.csv'

    # List all the projects that have been selected so far
    if args.list_projects:
        data_files = glob(path.join(base_path, '*.csv'))
        project_names = set()
        
        # Go through all the csv files and find the unique project names
        for data_file_handler in data_files:     
            with open(data_file_handler, 'r') as csv_file_handler:
                csv_read_handler = csv.reader(csv_file_handler)
                
                project_names.update( set([ row[2] for row in csv_read_handler]) )
        
        # Print the unique names
        for name in project_names:
            print(name)

    elif args.count_up:
        project_name = input("Enter project name: ")
        time_spent_delta = datetime.now() - start_time
        time_spent = get_timedelta_minute_string(time_spent_delta)
        time_spent = 0 if time_spent_delta.seconds < 60 else time_spent

        if not project_name and not time_spent:
            print("ERROR: For event at {} no time or project name has been given and the event was less that 1 minute".format(get_as_nearest_time_string(start_time, 1)))
            exit()
        elif not project_name:
            print("ERROR: {},{} event not saved since no project name given".format(get_as_nearest_time_string(start_time, 1), time_spent))
            exit()
        elif not time_spent: 
            print("ERROR: Event {},0,{} not saved since less than a minute long".format(get_as_nearest_time_string(start_time, 1), project_name))
            exit()
        
        save_timed_project(data_file_path, date_string, get_as_nearest_time_string(start_time, 1), time_spent, project_name)
        # Save the completed time track
        #with open(file_path, 'a') as csv_file_handler:
        #    csv_write_handler = csv.writer(csv_file_handler, lineterminator='\n')
        #    csv_write_handler.writerow([get_as_nearest_time_string(start_time, 1), time_spent, project_name])

    elif args.open:
       #TODO:This should be replaced with the editor variable
       system("vim + {}".format(data_file_path)) # Open the vim file of the database, the + here means we go to the end of the file, 

    # Start a new task
    else:
        chosen_project = args.project_name.strip()
        start_time_string = get_as_nearest_time_string(start_time, round_to_time_interval)
        end_time_string = get_as_nearest_time_string(start_time + timedelta(minutes=minutes_to_wait), round_to_time_interval)

        if args.subscribe:
            end_time = start_time + timedelta(minutes=minutes_to_wait);
            secs_past = 0;
            while datetime.now() < end_time or secs_past > 1000000: #TODO:Poor maximum subscribe time
                cur_time = datetime.now()
                sleep(1)
                system("echo AT"+str(chosen_project)+":"+str(get_timedelta_minute_string(end_time - cur_time)))
            system("echo AF"+str(chosen_project)+":"+str(0))
        else:
            sleep(minutes_to_wait*60)

        message = chosen_project + "\n " + start_time_string + " -> " + end_time_string

        system("notify-send --icon=task-past -a \"" + app_name + "\" \"" + message + "\"")

        #max_freq = 450
        #for i in np.arange(440, max_freq, 10):
        #    system("play -nq -t alsa synth 0.4 sine {}".format(str(i)))
        #    print(i)
            #system("play -nq -t alsa synth 0.1 sine {}".format(str(i)))

        #system("play -nq -t alsa synth 0.5 square {}".format(str(max_freq)))
        #system("cvlc wow.mpeg")
        #system("cvlc to-the-point.mp3")

        # Save the completed timer
        with open(file_path, 'a') as csv_file_handler:
            csv_write_handler = csv.writer(csv_file_handler)
            csv_write_handler.writerow([start_time_string, minutes_to_wait, chosen_project])
