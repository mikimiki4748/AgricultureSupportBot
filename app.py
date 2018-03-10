# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import time
import re
import enum
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

from src.daily_env import get_daily_temp


app = Flask(__name__)


class gateway(enum.Enum):
    anan  = {'sensor': '45327972', 'nodes': ['7', '15']}
    ishii  = {'sensor': '45324459', 'nodes': ['7', '15']}

@app.route("/del")
def db_reset():
    from src.daily_db import del_db
    del_db()
    return 'delete DB'
    
@app.route("/", methods=['GET', 'POST'])
def index():
    timepicker_format = '%Y-%m-%d'

    dt_end = datetime.now() - timedelta(days=1)
    dt_start = dt_end - timedelta(days=6)

    str_start  = datetime.strftime(dt_start, timepicker_format)
    str_end    = datetime.strftime(dt_end, timepicker_format)

    if request.method == 'POST':
        str_start = request.form['date_from']
        str_end = request.form['date_to']
        #TODO:injection

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

        str_start  = datetime.strftime(dt_start, timepicker_format)
        str_end    = datetime.strftime(dt_end, timepicker_format)
    print("str_start",str_start)
    print("str_end",str_end)
    sens = gateway.anan.value
    daily_temp = get_daily_temp(sens['sensor'], sens['nodes'][0], dt_start, dt_end)

    for row in daily_temp:
        print("contents: ", row)
    asc_date = [row[b'date'].decode('utf-8') for row in daily_temp if row[b'valid'] == b"True"]
    asc_avg = [float(row[b'avg_temp']) for row in daily_temp if row[b'valid'] == b"True"]
    asc_max = [float(row[b'max_temp']) for row in daily_temp if row[b'valid'] == b"True"]
    asc_min = [float(row[b'min_temp']) for row in daily_temp if row[b'valid'] == b"True"]

    print(str_start, str_end)

    return render_template('chart.html', dataset_ave=asc_avg,
        dataset_max=asc_max, dataset_min=asc_min, labels=asc_date,
        str_start=str_start, str_end=str_end )

@app.route("/update")
def update_db():
    api_format = '%Y-%m-%dT%H:%M:%S.000000Z'
    # time_format = '%Y-%m-%d %H:%M:%S'
    # date_format = '%Y-%m-%d'
    days_ago = 1
    while True:
        end_day = datetime.now()
        start_day = (end_day - timedelta(weeks=days_ago)).replace(hour=0,minute=0,second=0,microsecond=0)
        print(datetime.strftime(start_day, api_format)+" - "+datetime.strftime(end_day, api_format))

        # start_epoch = int(time.mktime(start_day.timetuple()))*1000
        # end_epoch = int(time.mktime(end_day.timetuple()))*1000
    
        days_ago += 1
        if days_ago > 5:
            break

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
