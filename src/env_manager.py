import os
import sys
import redis
import enum
import json
import requests
import time

from datetime import datetime
from datetime import timedelta

from src.env_redis import get_daily_temp


def get_avg_temp(day_ago):
    daily_list = get_daily_temp(day_ago)
    result = []
    for daily_dict in daily_list:
        if daily_dict.get(b"avg_temp") is not None:
            result.append(float(daily_dict.get(b"avg_temp")))
        elif daily_dict.get("avg_temp") is not None:
            result.append(float(daily_dict.get("avg_temp")))
        else:
            print("Cant get data at get_avg_temp()")
    return result

def get_max_temp(day_ago):
    daily_list = get_daily_temp(day_ago)
    result = []
    for daily_dict in daily_list:
        if daily_dict.get(b"max_temp") is not None:
            result.append(float(daily_dict.get(b"max_temp")))
        elif daily_dict.get("max_temp") is not None:
            result.append(float(daily_dict.get("max_temp")))
        else:
            print("Cant get data at get_max_temp()")
    return result

def get_min_temp(day_ago):
    daily_list = get_daily_temp(day_ago)
    result = []
    for daily_dict in daily_list:
        if daily_dict.get(b"min_temp") is not None:
            result.append(float(daily_dict.get(b"min_temp")))
        elif daily_dict.get("min_temp") is not None:
            result.append(float(daily_dict.get("min_temp")))
        else:
            print("Cant get data at get_min_temp()")
    return result

if __name__ == '__main__' :
    pass
    # print(get_avg_temp(7))
    # print(get_max_temp(7))
    # print(get_min_temp(7))
