import os
import redis
import time
from datetime import datetime
from datetime import timedelta

from src.kosen_api import api_format

REDIS_URL = os.environ.get('REDIS_URL') if os.environ.get(
    'REDIS_URL') != None else 'redis://localhost:6379'

DATABASE_INDEX = 1
pool = redis.ConnectionPool.from_url(REDIS_URL, db=DATABASE_INDEX)
r = redis.StrictRedis(connection_pool=pool)


def del_db():
    print("DB削除するキー", r.keys())
    r.flushdb()

def gen_key(str_sensor_id, str_node_id, dt_date, int_attr_id):
    return "row_"+str_sensor_id +"_"+ str_node_id +"_"+ dt_date.strftime(api_format) +"_"+ str(int_attr_id)

def extract_data(str_sensor_id, str_node_id, dt_date, env_id):
    key = gen_key(str_sensor_id, str_node_id, dt_date, env_id)
    return r.hgetall(key)

def put_row_data(str_sensor_id, str_node_id, dt_date, env_id, flt_env_data):
    key = gen_key(str_sensor_id, str_node_id, dt_date, env_id)    
    r.set(key, flt_env_data)
    return True

if __name__ == '__main__' :
    del_db()
