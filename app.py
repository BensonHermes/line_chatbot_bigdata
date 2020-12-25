from io import StringIO
import requests 
# from pyquery import PyQuery as pq
# import matplotlib.pyplot as plt
# import numpy as np
# import pandas as pd
# import pyimgur
# from selenium import webdriver
import mysql.connector
from mysql.connector import Error


from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

from message import *
from BasicInfoSetting import *
from GetWarn import *
from ReturnHome import *
from flex_button import *


app = Flask(__name__)
# Channel Access Token
line_bot_api = LineBotApi('F7fZ4NRk3qz1K4XPu6EKW6pejsgcWA6esSdwme1oVWyy2DzCB1gtZRXNwNC6+NLa+62r8OUl9w7EbHnUDP3EWocuWwCcpK5HpMmQkXQ8+4LIoIGT037RCmzohu84RsigD4o20eXGNJFiA9HkMWjOvQdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('fca3781ffe4aa6bf0cfa89f33a635182')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


BISMList = {}   # the state machine of BasicInfoSetting
BICommands = [   # commands for basic setting    '全部重新設定',
    '全部重新設定',
    '查看目前設定',
    '設定用戶ID',
    '設定住家地址',
    '設定常用地點',
    '設定緊急聯絡人'
]
GWSMList = {}   # the state machine of GetWarn
RHSMList = {}
RHCommands = [
]

def resetAllMachine(user_id):
    BISMList[user_id].reset()
    GWSMList[user_id].reset()
    RHSMList[user_id].reset()

def checkStateMachine(user_id):
    if user_id not in BISMList:
        BISMList[user_id] = BasicInfoStateMachine()
    if user_id not in GWSMList:
        GWSMList[user_id] = GetWarnStateMachine()
    if user_id not in RHSMList:
        RHSMList[user_id] = ReturnHomeMachine()
    
# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = ""
    msg = event.message.text
    user_id = event.source.user_id
    checkStateMachine(user_id)

    if '基本資料設定' in msg:
        resetAllMachine(user_id)
        message = BasicInfoSettingEntrance()
    elif '查詢警示地點' in msg:
        # resetAllMachine(user_id)
        GWSMList[user_id].locate()
        note = '請點選下方的按鈕，選擇要查詢的位置'
        message = TextSendMessage(
            text = note,
            quick_reply = chooseLocationButton()
            )
        # message = FlexSendMessage(
        #     alt_text = ,
        #     contents = chooseLocationFlex('請選擇要查詢的地點')
        # )
    elif '開始回家' in msg:
        resetAllMachine(user_id)
        RHSMList[user_id].set_time()
        message = SetReturnHomeTime()
    elif BISMList[user_id].state != 'default' or msg in BICommands:
        note = BasicInfoSetting(event, BISMList[user_id])
        # print(BISMList[user_id].state)
        if BISMList[user_id].state == 'home' or BISMList[user_id].state == 'all_home':
            # print('here')
            message = TextSendMessage(text=note, quick_reply=chooseLocationButton())
        else:
            message = TextSendMessage(text=note)
    elif RHSMList[user_id].state != 'default' or msg in RHCommands:
        message = ReturnHomeSetting(event, RHSMList[user_id])
    else:   # default
        return
        # message = TextSendMessage(text=msg)

    line_bot_api.reply_message(event.reply_token, message)

@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    user_id = event.source.user_id
    message = ""
    if BISMList[user_id].state != 'default':
        note = BasicInfoSetting(event, BISMList[user_id])
        message = TextSendMessage(text=note)
    elif GWSMList[user_id].state != 'default':
        # message = TextSendMessage(text=GetWarn(event))
        message = GetWarn(event, GWSMList[user_id])
        GWSMList[user_id].reset()
    else:
        return
    line_bot_api.reply_message(event.reply_token, message)

@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    if RHSMList[user_id].state == 'set_time':
        # ReturnHome(event, RHSMList[user_id])
        RHSMList[user_id].time = parsetime(event.postback.params['time'])
        # print(RHSMList[user_id].time)
        # RHSMList[user_id].start_counting()
        # note = RHSMList[user_id].time.strftime('回家時間：%Y/%m/%d %H:%M')
        # message = TextSendMessage(text=note)
        # line_bot_api.reply_message(event.reply_token, message)
        ReturnHome(line_bot_api, event, RHSMList[user_id])
    elif RHSMList[user_id].state != 'default' and 'arrive_home' in event.postback.data:
        RHSMList[user_id].reset()
        message = TextSendMessage(text='請稍候...')
        line_bot_api.reply_message(event.reply_token, message)

# def doSQL(order: int, sqlStatement: str, data: list)
#     try:
#         # 連接 MySQL/MariaDB 資料庫
#         connection = mysql.connector.connect(
#             host='140.119.19.73',          # 主機名稱
#             port='9306',
#             database='TG06', # 資料庫名稱
#             user='TG06',        # 帳號
#             password='i8p3q6')  # 密碼
        
#         if connection.is_connected():
#             print("database version:", connection.get_server_info())

#         # 查詢資料庫
#         cursor = connection.cursor()
#         cursor.execute("SELECT DATABASE();")
#         record = cursor.fetchone()
#         print("current database:", record)
#         # if(order==0):
#         #     cursor.execute(sqlStatement)
#         # 列出查詢的資料'
#             # records = cursor.fetchall()
#             # return records
#             # for (Course_id, Course_name) in cursor:
#             #     print("Course_id: %s, Course_name: %s" % (Course_id, Course_name))
#         # else:
#         #     cursor.execute(sqlStatement,data)
#         #     connection.commit()

#     except Error as e:
#         print("資料庫連接失敗：", e)

#     finally:
#         if (connection.is_connected()):
#             cursor.close()
#             connection.close()
#             print("資料庫連線已關閉")


import os
if __name__ == "__main__":
    print(parsetime('03:00'))
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
