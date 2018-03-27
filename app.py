# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import time
import re
import enum
import threading
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
from flask import make_response

from src.daily_env import get_daily_temp
from src.daily_env import update_one_year


app = Flask(__name__)
timepicker_format = '%Y-%m-%d'

class gateway(enum.Enum):
    anan  = {'sensor': '45327972', 'nodes': ['7', '15']}
    ishii  = {'sensor': '45324459', 'nodes': ['7', '15']}

@app.route("/del")
def db_reset():
    from src.daily_db import del_db
    del_db()
    return 'delete DB'

@app.route("/update")
def db_update():
    sens = gateway.anan.value
    update_one_year(sens['sensor'], sens['nodes'][0])
    return 'update DB'

@app.route("/cookie", methods=['POST'])
def set_cookie():
    sens_id = request.form['sens_id']
    node_id = request.form['node_id']

    content = "センサID({0})とノードID({1})を保存しました".format(sens_id, node_id)
    response = make_response(content)
    # max_age = 60 * 60 * 24 * 120 # 120 days
    # expires = int(datetime.now().timestamp()) + max_age
    response.set_cookie('sens_id', value=sens_id, max_age=None,
        expires=None, path='/', domain=None, secure=None, httponly=False)
    response.set_cookie('node_id', value=node_id, max_age=None,
        expires=None, path='/', domain=None, secure=None, httponly=False)
    return response

@app.route("/", methods=['GET', 'POST'])
def index():
    sens_id = request.cookies.get('sens_id', 45327972)
    node_id = request.cookies.get('node_id', 7)

    str_start = str()
    str_end = str()
    dt_start = datetime.now()
    dt_end   = datetime.now()
    
    if request.method == 'POST':
        str_start = request.form['date_from']
        str_end = request.form['date_to']

        try:
            dt_start = datetime.strptime(str_start, timepicker_format)
            dt_end   = datetime.strptime(str_end,   timepicker_format)
            if dt_start > dt_end:
                dt_tmp = dt_start
                dt_start = dt_end
                dt_end = dt_tmp
                
        except ValueError:
            dt_end = datetime.now() - timedelta(days=1)
            dt_start = dt_end - timedelta(days=6)
            str_start = datetime.strftime(dt_start, timepicker_format)
            str_end   = datetime.strftime(dt_end, timepicker_format)
    else:
        dt_end = datetime.now() - timedelta(days=1)
        dt_start = dt_end - timedelta(days=6)
        str_start = datetime.strftime(dt_start, timepicker_format)
        str_end   = datetime.strftime(dt_end, timepicker_format)
    
    print("表示範囲", str_start, '~', str_end)

    sens = gateway.anan.value
    daily_temp = get_daily_temp(sens['sensor'], sens['nodes'][0], dt_start, dt_end)

    for row in daily_temp:
        print("contents: ", row)
    asc_date = [row[b'date'].decode('utf-8') for row in daily_temp if row[b'valid'] == b"True"]
    asc_avg = [float(row[b'avg_temp']) for row in daily_temp if row[b'valid'] == b"True"]
    asc_max = [float(row[b'max_temp']) for row in daily_temp if row[b'valid'] == b"True"]
    asc_min = [float(row[b'min_temp']) for row in daily_temp if row[b'valid'] == b"True"]

    return render_template('chart.html', dataset_ave=asc_avg,
        dataset_max=asc_max, dataset_min=asc_min, labels=asc_date,
        str_start=str_start, str_end=str_end,
        sens_id = sens_id, node_id = node_id )


@app.route('/tmp/<path:filename>')
def csv(filename):  
    return send_from_directory('tmp', filename)

# @app.route("/callback", methods=['POST'])


if __name__ == "__main__":
    app.run(host='localhost', port=8000)
    '''
    arg_parser = ArgumentParser(
      usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
    '''
