# -*- coding: utf-8 -*-
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
import urllib.request
import json

from datetime import datetime
from datetime import timedelta
import time
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
   

def getEnvData():
    reference_token = ''
    reference_token = getToken()
    #石井のIDは 45324459
    #阿南高専のIDは 45327972
    url = 'http://www17337uj.sakura.ne.jp/v1/json/collection/item/'
    gw_id   = '45327972'
    gw_name = 'sensorData_v2_'+gw_id
    node_id = '7'#7 15
    keys = '['
    for index,attr in enumerate( attr_list):
        keys += '\"'+attr+'\"'
        if index != len(attr_list)-1:
            keys += ','
    keys += ']'
    #print(keys)
    #keys = '[\"nodeID\",\"time\",\"air_temperature\"]'
    #現在から6日前までの時間
    tday = datetime.now()
    week_ago = tday - timedelta(days=6)
    epc_y = int(time.mktime(week_ago.timetuple()))*1000
    epc_t = int(time.mktime(tday.timetuple()))*1000
    #print('yesterday epoch:'+str(epc_y))
    #print('     oday epoch:'+str(epc_t))
    #辞書のパターン
    #query_dict = {'\"$where\"':'\"this.time >= new Date('+str(epc_y)+')&&this.time <= new Date('+str(epc_t)+')\"',
    #              '\"nodeID\"':node_id}
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

    try:
        import requests
        res = requests.get(url,params=payload,headers=headers)
      
        json_res = res.json()
        if json_res['Response'] != 'Success':
            print('Failed download environmental data.')
        
        env_list = json_res['List']
        #csv形式で書き出す
        f=open('tmp/data.csv','w')
        #f.write('_id,air_temperature,,relative_humidity,ATPR,amount_of_solar_radiation,nodeID,precipitation,time,wind_direction,wind_speed\n')
        f.write(',')
        for attr in attr_list:
            f.write(attr+',')
        f.write('\n')
        
        data_id = 0
        dt = ''
        date_format = '%Y-%m-%dT%H:%M:%S.000000Z'
        for datum in env_list:
            f.write(str(data_id)+',')
            dec = dict(datum)
            for attr in attr_list:
                if attr == 'time':
                    #9時間プラス
                    str_dt = dec.get('time','')
                    if str_dt != '':
                        dt = datetime.strptime(str_dt, date_format)
                        dt += timedelta(hours = 9)
                        f.write(datetime.strftime(dt, date_format))
                        f.write(',')
                else:
                    f.write(str(dec.get(attr,''))+',')
            f.write('\n')
            data_id += 1
        f.close()

    except URLError as e:
        print(e)
        return None
    except HTTPError as e:
        print(e)#couldnt be found
        return None
    
    return None


if __name__ == '__main__' :
    #getEnvData()
    getToken()

