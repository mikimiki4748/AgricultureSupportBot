import os
import redis
import time
from datetime import datetime
from datetime import timedelta

REDIS_URL = os.environ.get('REDIS_URL') if os.environ.get(
    'REDIS_URL') != None else 'redis://localhost:6379'
DATABASE_INDEX = 1
pool = redis.ConnectionPool.from_url(REDIS_URL, db=DATABASE_INDEX)
r = redis.StrictRedis(connection_pool=pool)

db_date_format = "%Y/%m/%d"

def del_db():
    print("DB削除するキー", r.keys())
    r.flushdb()

def gen_key(str_sensor_id, str_node_id, dt_date, int_attr_id):
    return "row_"+str_sensor_id +"_"+ str_node_id +"_"+ dt_date.strftime(db_date_format) +"_"+ str(int_attr_id)

# def extract_data(str_sensor_id, str_node_id, dt_date, int_attr_id):
#     key = gen_key(str_sensor_id, str_node_id, dt_date, int_attr_id)
#     return r.hgetall(key)

def put_row_temp(str_sensor_id, str_node_id, dt_date, flt_temp):
    key = gen_key(str_sensor_id, str_node_id, dt_date, 0)    
    r.set(key, flt_temp)
    return True

if __name__ == '__main__' :
    del_db()
