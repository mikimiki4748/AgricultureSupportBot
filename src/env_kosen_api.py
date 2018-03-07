# -*- coding: utf-8 -*-
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
import urllib.request
import json
import requests
import time

from datetime import datetime
from datetime import timedelta
from urllib.parse import urlencode
from urllib.parse import quote
 
 
attr_list = ["nodeID","time","air_temperature",
    "relative_humidity","illuminance","ATPR",
    "soil_temperature","soil_moisture_content",
    "amount_of_solar_radiation","wind_speed",
    "wind_direction","rainfall","precipitation"]

api_format = '%Y-%m-%dT%H:%M:%S.000000Z'
time_format = '%Y-%m-%d %H:%M:%S'
date_format = '%Y-%m-%d'
response_format = '%Y-%m-%d %H:%M:%S.%f'
token_response = {}

def get_token():
    global token_response
    if is_token_valid(token_response):
        return token_response['Token']

    url = 'http://www17337uj.sakura.ne.jp:3100/getToken'
    with urllib.request.urlopen(url) as res:
        html = res.read().decode("utf-8")
    # print(html)
    token_response = json.loads(html)
    print('有効期限:',token_response['Expire'])
    print('結果:',token_response['Response'])
    print('トークン:',token_response['Token'])

    return token_response['Token']

def is_token_valid(token_response):
    # KeyError にならないようにget()を使う.
    if token_response.get('Response') == 'Success' and \
        datetime.strptime(token_response.get('Expire'), response_format) > datetime.now():
        return True
    return False
    
def get_util_now(day_ago):
    reference_token = get_token()

    url = 'http://www17337uj.sakura.ne.jp/v1/json/collection/item/'
    gw_id   = '45327972'
    gw_name = 'sensorData_v2_'+gw_id
    node_id = '7'#7 15
    #TODO: 気温以外の対応
    keys = '[\"nodeID\",\"time\",\"air_temperature\"]'

    end_time = datetime.now()
    start_time = (end_time - timedelta(days=day_ago)).replace(hour=0,minute=0,second=0,microsecond=0)
    print(datetime.strftime(start_time, api_format)+" - "+datetime.strftime(end_time, api_format))

    start_epoch = int(time.mktime(start_time.timetuple()))*1000
    end_epoch = int(time.mktime(end_time.timetuple()))*1000
    query = '{\"$where\":\"this.time >= new Date('+str(start_epoch)+') && this.time <= new Date('+str(end_epoch)+')\",\"nodeID\":'+node_id+'}'
    #query = quote(query)
    
    payload = {
        'Name' :gw_name,
        'Keys' :keys,
        'Query':query
    }
    par_params = urllib.parse.urlencode(payload)
    par_params = par_params.encode('ascii')
    headers ={
        'Authorization':reference_token,
    }

    res = requests.get(url,params=payload,headers=headers)
    json_res = res.json()

    if json_res['Response'] != 'Success':
        print('Failed download environmental data.')
        return False
    return json_res['List']

def get_the_day(sensor_id, node_id, env_kind, dt_day):
    reference_token = get_token()

    url = 'http://www17337uj.sakura.ne.jp/v1/json/collection/item/'
    gw_name = 'sensorData_v2_'+sensor_id
    
    #TODO: 気温以外の対応
    keys = '[\"nodeID\",\"time\",\"air_temperature\"]'

    start_time = dt_day.replace(hour=0,minute=0,second=0,microsecond=0)
    end_time = dt_day.replace(hour=23,minute=59,second=59,microsecond=999)
    print(datetime.strftime(start_time, api_format)+" - "+datetime.strftime(end_time, api_format))

    start_epoch = int(time.mktime(start_time.timetuple()))*1000
    end_epoch = int(time.mktime(end_time.timetuple()))*1000
    query = '{\"$where\":\"this.time >= new Date('+str(start_epoch)+') && this.time <= new Date('+str(end_epoch)+')\",\"nodeID\":'+node_id+'}'
    #query = quote(query)
    
    payload = {
        'Name' :gw_name,
        'Keys' :keys,
        'Query':query
    }
    par_params = urllib.parse.urlencode(payload)
    par_params = par_params.encode('ascii')
    headers ={
        'Authorization':reference_token,
    }

    res = requests.get(url,params=payload,headers=headers)
    json_res = res.json()

    if json_res['Response'] != 'Success':
        print('Failed download environmental data.')
        return False
    return json_res['List']

def get_daily_data(sensor_id, node_id, env_kind, dt_target):
    env_list = get_the_day(sensor_id, node_id, env_kind, dt_target)

    daily_data = list()
    avg_temp = 0 
    max_temp = -100
    min_temp = 100
    temp_num = 0
    pre_date = datetime.strftime(datetime.strptime(dict(env_list[0]).get('time', None), api_format) + timedelta(hours = 9), date_format)
    
    for data_json in env_list:
        data_dict = dict(data_json)
        str_time = data_dict.get('time', None)
        if(str_time is None):
            continue
        api_time = datetime.strptime(str_time, api_format) + timedelta(hours = 9)#9時間プラス
    #    d_time = datetime.strftime(api_time, time_format)
        d_date = datetime.strftime(api_time, date_format)
        
        #TODO:other element
        air_temperature = data_dict.get('air_temperature', None)
        if air_temperature is None:
            continue
        
        if d_date == pre_date:
            temp_num += 1
            avg_temp += air_temperature
            #print(air_temperature)
            if max_temp < air_temperature:
                max_temp = air_temperature
            if min_temp > air_temperature:
                min_temp = air_temperature
        else:
            #TODO:同じ処理を書いている.関数化orクラス化.
            avg_temp = round(avg_temp / float(temp_num), 2)
            daily_data.append({"date":pre_date, "avg_temp": avg_temp, "max_temp": max_temp, "min_temp": min_temp})            
            print("日にち:", pre_date)
            print("平均値:", avg_temp)
            print("最高値:", max_temp)
            print("最低値:", min_temp)
            
            temp_num = 1
            avg_temp = air_temperature
            max_temp = air_temperature
            min_temp = air_temperature
            #print(air_temperature)
            pre_date = d_date
    else:
        avg_temp = round(avg_temp / float(temp_num), 2)
        daily_data.append({"date":d_date, "avg_temp": avg_temp, "max_temp": max_temp, "min_temp": min_temp})            
        print("日にち:", d_date)
        print("平均値:", avg_temp)
        print("最高値:", max_temp)
        print("最低値:", min_temp)
    
    return daily_data


if __name__ == '__main__' :
    daily_data = get_daily_data(1)
    for i in range(len(daily_data)):
        print(daily_data[i])
    #getToken()

