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

from src.daily_env import get_daily_data
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

@app.route("/", methods=['GET'])
def index():
    dt_start = datetime.now() - timedelta(days=6)
    dt_end   = datetime.now()
    return render_template('chart.html',
        str_start=dt_start.strftime(timepicker_format),
        str_end=dt_end.strftime(timepicker_format))

@app.route("/", methods=['POST'])
def draw_graph():
    str_start = str()
    str_end = str()
    dt_start = datetime.now()
    dt_end   = datetime.now()
    
    print(request.form)
    sens_id = request.form['sens_node_select'].split('-')[1]
    node_id = request.form['sens_node_select'].split('-')[2]

    str_start = request.form['date_from']
    str_end = request.form['date_to']
    
    env_id = float(request.form['env_select'])
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

    print("表示範囲", str_start, '~', str_end)
    print("sens_id:{0} ,node_id:{1}".format(sens_id, node_id))
    
    if env_id == 0:#FIXME:env_id をenumなどで定義
        daily_temp = get_daily_data(sens_id, node_id, dt_start, dt_end, env_id)

        # for row in daily_temp:
        #     print("contents: ", row)
        asc_date = [item[b'date'].decode('utf-8') for item in daily_temp if item[b'valid'] == b"True"]
        asc_avg = [float(item[b'avg_temp']) for item in daily_temp if item[b'valid'] == b"True"]
        asc_max = [float(item[b'max_temp']) for item in daily_temp if item[b'valid'] == b"True"]
        asc_min = [float(item[b'min_temp']) for item in daily_temp if item[b'valid'] == b"True"]

        return render_template('chart.html', env_id=env_id, dataset_avg=asc_avg,
            dataset_max=asc_max, dataset_min=asc_min, labels=asc_date,
            str_start=str_start, str_end=str_end,
            sens_id = sens_id, node_id = node_id )

    elif env_id >= 1 or env_id < 2:
        daily_illum = get_daily_data(sens_id, node_id, dt_start, dt_end, env_id)
        asc_date = [item[b'date'].decode('utf-8') for item in daily_illum if item[b'valid'] == b"True"]
        asc_illum = [float(item[b'accumu_illum']) for item in daily_illum if item[b'valid'] == b"True"]
        
        if env_id == 1.1:
            #REVIEW: 描画する範囲で積算する.
            #今後実装で播種からの積算にすべき?
            for (i,illum) in enumerate(asc_illum):
                if i == 0:
                    continue
                asc_illum[i] += asc_illum[i-1]

        return render_template('chart.html',env_id=int(env_id),
            labels = asc_date, dataset_illum = asc_illum,
            str_start = str_start, str_end = str_end)

    return render_template('chart.html' )


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
