import os
import sys
import redis
import json
import requests
import time
from datetime import datetime
from datetime import timedelta
from src.env_kosen_api import get_daily_data


REDIS_URL = os.environ.get('REDIS_URL') if os.environ.get(
    'REDIS_URL') != None else 'redis://localhost:6379'
DATABASE_INDEX = 2

pool = redis.ConnectionPool.from_url(REDIS_URL, db=DATABASE_INDEX)
r = redis.StrictRedis(connection_pool=pool)


def del_db():
    r.flushdb()

def set_row_data(sensor_id, node_id, data_list):
    pass

if __name__ == '__main__' :
    del_db()


