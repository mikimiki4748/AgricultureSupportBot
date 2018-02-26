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

def getToken():
   # url = "http://agridatabase.mybluemix.net/v1/json/token/"
   url = 'http://www17337uj.sakura.ne.jp:3100/getToken'
   with urllib.request.urlopen(url) as res:
      html = res.read().decode("utf-8")
#   print(html)
   dict_response = json.loads(html)
   print('有効期限: ',dict_response['Expire'])
   print('結果: ',dict_response['Response'])
   print('Token: ',dict_response['Token'])
   return dict_response['Token'] #トークン
   

def getEnvData(data_days=6):
    reference_token = getToken()
    #石井のIDは 45324459
    #阿南高専のIDは 45327972
    url = 'http://www17337uj.sakura.ne.jp/v1/json/collection/item/'
    gw_id   = '45327972'
    gw_name = 'sensorData_v2_'+gw_id
    node_id = '7'#7 15
    '''
    keys = '['
    for index,attr in enumerate( attr_list):
        keys += '\"'+attr+'\"'
        if index != len(attr_list)-1:
            keys += ','
    keys += ']'
    #print(keys)
    '''
    keys = '[\"nodeID\",\"time\",\"air_temperature\"]'
    #現在から6日前までの時間
    tday = datetime.now()
    week_ago = tday - timedelta(days=data_days)
    epc_y = int(time.mktime(week_ago.timetuple()))*1000
    epc_t = int(time.mktime(tday.timetuple()))*1000
    #print('yesterday epoch:'+str(epc_y))
    #print('    today epoch:'+str(epc_t))
    query = '{\"$where\":\"this.time >= new Date('+str(epc_y)+') && this.time <= new Date('+str(epc_t)+')\",\"nodeID\":'+node_id+'}'
    #query = quote(query)
    
    #リクエスト送信
    payload = {'Name' :gw_name,
              'Keys' :keys,
              'Query':query}
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
    env_list = json_res['List']
    #print(env_list)

    api_format = '%Y-%m-%dT%H:%M:%S.000000Z'
    time_format = '%Y-%m-%d %H:%M:%S'
    date_format = '%Y-%m-%d'

    ave_temp  = [0 for i in range(data_days+2)]
    high_temp = [-100 for i in range(data_days+2)]
    low_temp  = [ 100 for i in range(data_days+2)]
    temp_num = 0
    temp_index = 0
    pre_date = datetime.strftime(datetime.strptime(dict(env_list[0]).get('time', None), api_format) + timedelta(hours = 9), date_format)
    for data_json in env_list:
        data_dict = dict(data_json)
        str_time = data_dict.get('time', None)
    #    if(str_time is None):
    #        continue

        api_time = datetime.strptime(str_time, api_format) + timedelta(hours = 9)#9時間プラス
    #    d_time = datetime.strftime(api_time, time_format)
        d_date = datetime.strftime(api_time, date_format)
        
        air_temperature = data_dict.get('air_temperature', None)
        if air_temperature is None:
            continue
        
        if pre_date == d_date:
            temp_num += 1
            ave_temp[temp_index] += air_temperature
            print(air_temperature)
            if high_temp[temp_index] < air_temperature:
                high_temp[temp_index] = air_temperature
            if low_temp[temp_index] > air_temperature:
                low_temp[temp_index] = air_temperature
        else:
            #TODO:同じ処理を書いている.関数化orクラス化.
            #print("合計値:", ave_temp[temp_index])
            #print("データ数:", temp_num)
            ave_temp[temp_index] = round(ave_temp[temp_index] / float(temp_num), 2)
            print("平均値:", ave_temp[temp_index])
            #print("日にち:", d_date)
            print("最高値:", high_temp[temp_index])
            print("最低値:", low_temp[temp_index])
            
            temp_index += 1
            temp_num = 1
            ave_temp[temp_index] = air_temperature
            high_temp[temp_index] = air_temperature
            low_temp[temp_index] = air_temperature          
            print(air_temperature)
            pre_date = d_date
    else:
        #print("--ループ終了--")
        ave_temp[temp_index] = round(ave_temp[temp_index] / float(temp_num), 2)
        print("平均値:", ave_temp[temp_index])
        #print("データ数:", temp_num)
        #print("日にち:", d_date)
        print("最高値:", high_temp[temp_index])
        print("最低値:", low_temp[temp_index])
    
    result = {"average": ave_temp, "max": high_temp, "min": low_temp}
    return result

if __name__ == '__main__' :
    getEnvData()
    #getToken()

