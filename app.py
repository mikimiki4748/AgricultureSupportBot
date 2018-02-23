# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import time
import re
import image
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

@app.route("/")
def chart():
    dt_tday = datetime.now()
    labels = [(dt_tday - timedelta(days=i)).strftime('%Y-%m-%d')
        for i in range(6,-1,-1)]
    #values = get_weekly_temp()
    values = [10,9,8,7,6,4,7,8]
    return render_template('chart.html', values=values, labels=labels)

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
