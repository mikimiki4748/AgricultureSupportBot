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
    #data = pd.read_csv("work/data.csv")#サンプルデータ
    print(date)
    data = pd.read_csv("tmp/data.csv")
    d = data[data["time"].str.contains(date)]
    d = d[['time', 'air_temperature']]
    d = d.dropna(axis=0)
    d['time'] = pd.to_datetime(d['time'])

    return d    #d = time and air_temperature

def temp(s, e):
    date_format = '%Y-%m-%d'
    start = datetime.datetime.strptime(s, date_format)
    end = datetime.datetime.strptime(e, date_format)

    day = []
    df = []
    temp_s = start
    temp_e = end
    for i in range((end - start).days + 1):
        date_output = start.strftime(date_format)
        day.append(date_output)
        df.append(get_data(day[i]))
        start += datetime.timedelta(days = 1)
    
    plt.rcParams["font.size"] = 8

    for i in range((temp_e - temp_s).days + 1):
        x = np.array(df[i].time)
        y = np.array(df[i].air_temperature)
            
        plt.plot(x, y)

    start_string = temp_s.strftime(date_format)
    end_string = temp_e.strftime(date_format)
    
    plt.title("Air Temperature in " + start_string + "~" + end_string)
    plt.xlabel("Date")
    plt.ylabel("Air Temperature")
    #plt.show()
    file_name  = "tmp/air_temperature.png"
    plt.savefig(file_name)
    print('saved as: '+file_name)
    return file_name
    #確認
    #import os
    #print('file_nameで確認')
    #print(os.path.exists(file_name))

