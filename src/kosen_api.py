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
 

attr_list = ["air_temperature","amount_of_solar_radiation",
    "illuminance","ATPR",
    "soil_temperature","soil_moisture_content",
    "relative_humidity","wind_speed",
    "wind_direction","rainfall","precipitation"]#"nodeID","time" もキーとしてある.

api_format = '%Y-%m-%dT%H:%M:%S.000000Z'
token_expire_format = '%Y-%m-%d %H:%M:%S.%f'

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
        datetime.strptime(token_response.get('Expire'), token_expire_format) > datetime.now():
        return True
    return False

def download_day_data(sensor_id, node_id, dt_day, env_id):
    reference_token = get_token()

    url = 'http://www17337uj.sakura.ne.jp/v1/json/collection/item/'
    gw_name = 'sensorData_v2_'+sensor_id
    
    keys = "[\"nodeID\",\"time\",\"{0}\"]".format(attr_list[env_id])

    start_time = dt_day.replace(hour=0,minute=0,second=0,microsecond=0)
    end_time = dt_day.replace(hour=23,minute=59,second=59,microsecond=999)
    print('取得範囲', datetime.strftime(start_time, api_format)+" - "+datetime.strftime(end_time, api_format))

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
    res = requests.get(url,params=payload,headers=headers)# 1分くらいかかる.
    json_res = res.json()

    if json_res['Response'] != 'Success':
        return False
    return json_res['List']

if __name__ == '__main__' :
    # anan  = {'sensor': '45327972', 'nodes': ['7', '15']}
    # ishii  = {'sensor': '45324459', 'nodes': ['7', '15']}
    response = download_day_data('45324459', '7', datetime.now() - timedelta(days=3), 1)
    print(response)