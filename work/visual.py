# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import subprocess
import sys
import datetime

def get_data(date):
    data = pd.read_csv("data.csv")
    d = data[data["time"].str.contains(date)]
    d = d[['time', 'air_temperature']]
    d = d.dropna(axis=0)
    d['time'] = pd.to_datetime(d['time'])

    return d    #d = time and air_temperature

def ave_temp(temp):
    return np.mean(temp.air_temperature)

def sekisan(temp, ave, dc):
    time = []
    change = []
    day_temp = []
    sum_temp = []

    for g in range(dc):
        for h in temp[g].time.items():
            time.append(h[1])
    
    for i in range(dc):
        for j in temp[i].air_temperature.items():
            day_temp.append(j[1])

    result = 0
    for k in range(len(day_temp)):
        if day_temp[k] > ave:
            change.append(time[k])
            result += day_temp[k] - ave
            sum_temp.append(result)
    
    return (change, sum_temp)   

def test(s, e):
    date_format = '%Y-%m-%d'
    start = datetime.datetime.strptime(s, date_format)
    end = datetime.datetime.strptime(e, date_format)

    day = []
    time_temp = []
    ave = []
    temp_s = start
    temp_e = end

    for i in range((end - start).days + 1):
        date_output = start.strftime(date_format)
        day.append(date_output)
        time_temp.append(get_data(day[i]))
        ave.append(ave_temp(time_temp[i]))
        start += datetime.timedelta(days = 1)
        
    threshold = np.sum(ave) / len(ave)
    day_count = (temp_e - temp_s).days + 1
    change_time, res = sekisan(time_temp, threshold, day_count)
        
    a = np.array(change_time)
    b = np.array(res)
    
    plt.rcParams["font.size"] = 8

    plt.plot(a, b)
    start_string = temp_s.strftime(date_format)
    end_string = temp_e.strftime(date_format)
    plt.title("Accumulated Temperature in " + start_string + "~" + end_string)
    plt.xlabel("Date")
    plt.ylabel("Accumulated Temperature")

    #plt.show()

    plt.savefig("/tmp/accumulated_temperature.png")

    #subprocess.call('rm -rf ' + filename, shell=True)

