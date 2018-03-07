import os
import sys
import redis
import json
import requests
import time
from datetime import datetime
from datetime import timedelta
from src.env_kosen_api import get_daily_data

# 接続パス、環境変数にあればそれ優先
REDIS_URL = os.environ.get('REDIS_URL') if os.environ.get(
    'REDIS_URL') != None else 'redis://localhost:6379'
# データベースの指定
DATABASE_INDEX = 1  # 0じゃなくあえて1

# コネクションプールから１つ取得
pool = redis.ConnectionPool.from_url(REDIS_URL, db=DATABASE_INDEX)
# コネクションを利用
r = redis.StrictRedis(connection_pool=pool)


def del_db():
    print("DB削除　キー", r.keys())
    r.flushdb()

def get_today_temp(sensor_id, node_id):
    '''
    DBから今日の分取得
    足りない分をとってくる
    DBセット
    返す
    r.hmset(key, daily_dict)'''


def get_daily_temp(sensor_id, node_id, dt_bgn, dt_end):
    '''日ごとの平均・最高・最低気温を返す
    昨日より未来の日付は指定できない
    今日のデータは別の関数で取得する'''
    date_format = '%Y-%m-%d'
    daystamp_format = '%Y%m%d'
    daily_temps = []
    
    dt_bgn.replace(hour=0,minute=0,second=0,microsecond=0)
    dt_end.replace(hour=0,minute=0,second=0,microsecond=0)
    dt_yday = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0) - timedelta(days=1)
    if dt_end >= dt_yday:
        dt_end = dt_yday
    
    dt_target = dt_bgn
    while dt_target <= dt_end:
        str_target_date = datetime.strftime(dt_target, daystamp_format)

        key = sensor_id + node_id + str_target_date + "0"#TODO:env id
        # print(key)
        daily_temp = r.hgetall(key)
        # print(daily_temp)
        
        if not daily_temp:
            print("Not found of data at "+ datetime.strftime(dt_target, date_format))
            #{"date":d_date, "avg_temp": avg_temp, "max_temp": max_temp, "min_temp": min_temp}
            daily_list = get_daily_data(sensor_id, node_id, 0, dt_target)

            for daily_dict in daily_list:
                print(daily_dict)
                daily_dict['valid'] = True
                r.hmset(key, daily_dict)
                print('redis save check:', r.hgetall(key))
                daily_temps.append(r.hgetall(key))
        else:
            print("Can get from DB:"+ datetime.strftime(dt_target, date_format), daily_temp)
            daily_temps.append(daily_temp)
        
        dt_target += timedelta(days=1)

    return daily_temps

if __name__ == '__main__' :
    del_db()
