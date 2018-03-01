# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals

import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort, send_from_directory
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    ImageSendMessage
)
#added
import re
from datetime import datetime
from datetime import timedelta
import time
from work.temperature import temp
from work.humidity import humi
from work.visual import test
from get_web_envdata import getEnvData
import image
from io import StringIO

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
host_name = 'https://nameless-gorge-55138.herokuapp.com'
#host_name = 'https://47240bc3.ngrok.io'

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route('/img/<path:filename>')
def image(filename):
    return send_from_directory('img', filename)


@app.route('/tmp/<path:filename>')
def csv(filename):  
    return send_from_directory('tmp', filename)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        
        received_text = event.message.text

        if re.search('温度', received_text):
            getEnvData()#データダウンロード
            #現在から7日前までの時間
            dt_tday = datetime.now()
            dt_week_ago = dt_tday - timedelta(days=6)
            str_tday = dt_tday.strftime('%Y-%m-%d')
            str_week_ago = dt_week_ago.strftime('%Y-%m-%d')
            #画像生成
            file_name = temp(str_week_ago, str_tday)
            #画像送信
            try:
                post_image(event.reply_token, host_name+'/'+file_name)
            except Exception as e:
                print(e)
        elif re.search('湿度', received_text):
            getEnvData()
            dt_tday = datetime.now()
            dt_week_ago = dt_tday - timedelta(days=6)
            str_tday = dt_tday.strftime('%Y-%m-%d')
            str_week_ago = dt_week_ago.strftime('%Y-%m-%d')
            file_name = humi(str_week_ago, str_tday)
            try:
                post_image(event.reply_token, host_name+'/'+file_name)
            except Exception as e:
                print(e)
        elif re.search('csv', received_text):
            try:
                post_text(event.reply_token, host_name+'/tmp/data.csv')
            except Exception as e:
                print(e)
        else:
            post_text(event.reply_token, received_text)
    
    return 'OK'

def post_text(token, text):
    line_bot_api.reply_message(
        token,
        TextSendMessage(text=text)
    )


def post_image(token, image_path):
    image_message = ImageSendMessage(
        original_content_url = image_path,
        preview_image_url = image_path
    )
    line_bot_api.reply_message(
        token,
        image_message
    )


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
