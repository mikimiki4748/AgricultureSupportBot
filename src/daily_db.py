import os
import redis
import time
from datetime import datetime
from datetime import timedelta

from src.row_db import put_row_data
from src.kosen_api import attr_list
from src.kosen_api import api_format


# 接続パス、環境変数にあればそれ優先
REDIS_URL = os.environ.get('REDIS_URL') if os.environ.get(
    'REDIS_URL') != None else 'redis://localhost:6379'
DATABASE_INDEX = 1  # 0じゃなくあえて1
pool = redis.ConnectionPool.from_url(REDIS_URL, db=DATABASE_INDEX)
r = redis.StrictRedis(connection_pool=pool)

db_date_format = "%Y-%m-%d"#DBのキーに使う
date_format = "%Y/%m/%d"#DB保存するvalueの形式,グラフ表示するときの形式


def del_db():
    print("DB削除するキー", r.keys())
    r.flushdb()

def gen_key(str_sensor_id, str_node_id, dt_date, int_attr_id):
    return "day_"+str_sensor_id +"_"+ str_node_id +"_"+ dt_date.strftime(db_date_format) +"_"+ str(int_attr_id)

def extract_data(str_sensor_id, str_node_id, dt_date, int_attr_id):
    key = gen_key(str_sensor_id, str_node_id, dt_date, int_attr_id)
    return r.hgetall(key)

def put_data(str_sensor_id, str_node_id, dt_date, int_attr_id, dict_content):
    key = gen_key(str_sensor_id, str_node_id, dt_date, int_attr_id)    
    r.hmset(key, dict_content)
    return True

def save_daily_data(sensor_id, node_id, dt_target, env_id, env_list):
    '''kosen_api.pyで取得したデータをDB保存する
    '''
    if env_id == 0:#TODO: env id をenumで定義
        daily_dict = save_daily_temp(sensor_id, node_id, dt_target, env_id, env_list)
    elif env_id == 1:
        daily_dict = save_daily_illum(sensor_id, node_id, dt_target, env_id, env_list)

    return True


def save_daily_temp(sensor_id, node_id, dt_target, env_id, env_list):
    avg_temp = 0 
    max_temp = -100
    min_temp = 100
    temp_num = 0
    str_date = datetime.strftime(dt_target, date_format)

    daily_dict = dict()
    for env in env_list:
        env_dict = dict(env)
        str_time = env_dict.get('time', None)
        if(str_time is None):#ないときはないと思うが念のため.
            continue
        env_data = env_dict.get(attr_list[env_id], None)
        if env_data is None:#ないときがある.
            continue
        #サーバの時刻はUTCのため+9h
        dt_api = datetime.strptime(str_time, api_format) + timedelta(hours = 9)#9時間プラス
        
        #そのままのデータを保存
        put_row_data(sensor_id, node_id, dt_api, env_id, env_data)# DB save

        temp_num += 1
        avg_temp += env_data
        if max_temp < env_data:
            max_temp = env_data
        if min_temp > env_data:
            min_temp = env_data
    else:
        if avg_temp != 0 or temp_num != 0:
            avg_temp = round(avg_temp / float(temp_num), 2)#REVIEW:round()は偶数への丸めのため一般的な四捨五入ではない.
        if max_temp == -100 or min_temp == 100:
            daily_dict = {"date":str_date, "valid": False, "avg_temp": None, "max_temp": None, "min_temp": None}          
        else:
            daily_dict = {"date":str_date, "valid": True, "avg_temp": avg_temp, "max_temp": max_temp, "min_temp": min_temp}
        # print("download_one_day_data return -> :", daily_dict)

    print("save_daily_temp().daily_dict", daily_dict)
    put_data(sensor_id, node_id, dt_target, env_id, daily_dict)

    return daily_dict

def save_daily_illum(sensor_id, node_id, dt_target, env_id, env_list):
    '''
    1日あたりの日射量を積算し保存.
    日射量ｘΔｔ(s)（単位時間）の積分を計算し[kwh]で保存
    750w/m2が10分単位で取得されている場合
    0.75×10/60を1日分積算していって求めてください。
    #  {'time': '2018-04-01T03:41:34.000000Z', '_id': '5ac054f1cb54b4001062c45f', 'nodeID': 7.0, 'amount_of_solar_radiation': 709.0},
    #  {'time': '2018-04-01T03:41:59.000000Z', '_id': '5ac0550acb54b4001062c46f', 'nodeID': 7.0, 'amount_of_solar_radiation': 709.0}]
    '''
    accumu_illum = 0
    pre_illum = 0
    dt_past = None #datetime

    str_date = datetime.strftime(dt_target, date_format)#FIXME:api time, dt_target 違う場合.

    daily_dict = dict()
    for env in env_list:
        env_dict = dict(env)
        str_time = env_dict.get('time', None)
        if(str_time is None):#ないときはないと思うが念のため.
            continue
        env_data = env_dict.get(attr_list[env_id], None)
        if env_data is None:#ないときがある.
            continue
        #サーバの時刻はUTCのため+9h
        dt_api = datetime.strptime(str_time, api_format) + timedelta(hours = 9)#9時間プラス
        
        #そのままのデータを保存
        put_row_data(sensor_id, node_id, dt_api, env_id, env_data)# DB save


        if dt_past is None:
            dt_past = dt_api
            pre_illum = env_data
            continue
        else:
            #accumu_illum[kWs] += 発電量[w] / 1000 * 経過時間[s]
            accumu_illum += float(env_data) / 1000 * (dt_api - dt_past).total_seconds()
            dt_past = dt_api
            pre_illum = env_data
        print(dt_api.strftime(api_format), '\taccumu_illum:', accumu_illum)
    else:
        if accumu_illum == 0:
            #"valid": False はセンサ値が一日分有効でないことを示す.
            daily_dict = {"date":dt_target.strftime(db_date_format), "valid": False, "accumu_illum": None}          
        else:
            #accumu_illum[kWs] -> [kWh]
            accumu_illum = round(accumu_illum / 3600, 2)#REVIEW:round()は偶数への丸めのため一般的な四捨五入ではない.
            daily_dict = {"date":dt_target.strftime(db_date_format), "valid": True, "accumu_illum": accumu_illum}
        # print("download_one_day_data return -> :", daily_dict)

    print("save_daily_illum().daily_dict", daily_dict)
    put_data(sensor_id, node_id, dt_target, env_id, daily_dict)

    return daily_dict

if __name__ == '__main__' :
    del_db()
