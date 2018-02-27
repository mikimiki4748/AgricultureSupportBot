import os
import sys
import redis
import enum
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


class gateway(enum.Enum):
    anan  = "45327972"
    ishii = "45324459"
# def get_db_id(gateway_id= "45327972", node_id="7"):
#     return gateway_id+"_"+node_id

def set_db():
    # キーの登録 飛び飛び
    r.set('key' + str(i * 2), {'val': 'val' + str(i)})

    # キーの参照
    for i in range(10):
        key = 'key' + str(i)
        print(key + ' → ' + str(r.get(key)))

def del_db():
    # キー一覧
    print("キー一覧 --before--", r.keys())
    # 設定したデータベースの削除
    r.flushdb()
    print("キー一覧 --after--", r.keys())


def get_daily_temp(day_ago):
    '''日ごとの平均・最高・最低気温を返す'''
    date_format = '%Y-%m-%d'
    daily_temps = []

    for i in range(day_ago,0,-1):
        dt_date = (datetime.now() - timedelta(days=i)).replace(hour=0,minute=0,second=0,microsecond=0)
        str_date = datetime.strftime(dt_date, date_format)
        #epc_date = int(time.mktime(dt_date.timetuple()))*1000
        #print(str_date, epc_date)
        daily_temp = r.hgetall(str_date)
        #print(dict_data)
        if not daily_temp:
            print("Not found of data at "+str_date)
            daily_list = get_daily_data(i)#{"date":d_date, "avg_temp": avg_temp, "max_temp": max_temp, "min_temp": min_temp}
            for daily_dict in daily_list:
                key = daily_dict.get("date")
                del daily_dict["date"]
                r.hmset(key, daily_dict)
                print(r.hgetall(key))
                daily_temps.append(r.hgetall(key))
            return daily_temps
        else:
            print("Can get from DB:"+str_date,daily_temp)
            
            daily_temps.append(daily_temp)
    return daily_temps


if __name__ == '__main__' :
    get_daily_temp(7)
    print("---\n")
    get_daily_temp(2)
    # 接続エラーがあれば終了
    # try:
    #     print('DB size : ' + str(r.dbsize()))
    # except Exception as e:
    #     print(type(e))
    #     sys.exit()
    # set_db()
    # del_db()


