# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import time
import re
import image
import redis
from argparse import ArgumentParser
from datetime import datetime
from datetime import timedelta
from io import StringIO
from flask import Flask
from flask import Markup
from flask import request
from flask import abort
from flask import render_template
from flask import send_from_directory

from work.temperature import temp
from work.humidity import humi
from work.visual import test
from get_web_envdata import getEnvData
from src.db_handler import get_weekly_temp
from src.db_handler import update_env_data


app = Flask(__name__)

# # 接続パス、環境変数にあればそれ優先
# REDIS_URL = os.environ.get('REDIS_URL') if os.environ.get(
#     'REDIS_URL') != None else 'redis://localhost:6379'
# # データベースの指定
# DATABASE_INDEX = 1  # 0じゃなくあえて1
# # コネクションプールから１つ取得
# pool = redis.ConnectionPool.from_url(REDIS_URL, db=DATABASE_INDEX)
# # コネクションを利用
# r = redis.StrictRedis(connection_pool=pool)


@app.route("/")
def chart():
    days_ago = 6
    data_dict = getEnvData(days_ago)
    
    dt_tday = datetime.now()
    labels = [(dt_tday - timedelta(days=i)).strftime('%Y-%m-%d')
        for i in range(days_ago,-1,-1)]
    #values = get_weekly_temp()
    dataset_ave = data_dict.get("average")
    dataset_max = data_dict.get("max")
    dataset_min = data_dict.get("min")
    return render_template('chart.html', dataset_ave=dataset_ave,
    dataset_max=dataset_max, dataset_min=dataset_min, labels=labels)

@app.route("/update")
def update_db():
    update_env_data()

@app.route('/img/<path:filename>')
def image(filename):
    return send_from_directory('img', filename)

@app.route('/tmp/<path:filename>')
def csv(filename):  
    return send_from_directory('tmp', filename)

@app.route("/callback", methods=['POST'])
def callback():
    getEnvData()#データダウンロード
    #現在から7日前までの時間
    dt_tday = datetime.now()
    dt_week_ago = dt_tday - timedelta(days=6)
    str_tday = dt_tday.strftime('%Y-%m-%d')
    str_week_ago = dt_week_ago.strftime('%Y-%m-%d')
    #画像生成
    file_name = temp(str_week_ago, str_tday)
    
    #湿度
    getEnvData()
    dt_tday = datetime.now()
    dt_week_ago = dt_tday - timedelta(days=6)
    str_tday = dt_tday.strftime('%Y-%m-%d')
    str_week_ago = dt_week_ago.strftime('%Y-%m-%d')
    file_name = humi(str_week_ago, str_tday)


if __name__ == "__main__":
    app.run(host='192.168.33.10', port=8000)
    '''
    arg_parser = ArgumentParser(
      usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
    '''
