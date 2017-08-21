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
    data = pd.read_csv("tmp/data.csv")
    d = data[data["time"].str.contains(date)]
    d = d[['time', 'air_temperature']]
    d = d.dropna(axis=0)
    d['time'] = pd.to_datetime(d['time'])

    return d    #d = time and air_temperature

def temp(s, e):
    plt.figure()#reset graph  
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
    dt = datetime.datetime.now()
    date_format = '%Y%m%d%H%M%S'
    file_name  = "img/"+datetime.datetime.strftime(dt,date_format)+"air_temperature.png"
    plt.savefig(file_name)
    return file_name
