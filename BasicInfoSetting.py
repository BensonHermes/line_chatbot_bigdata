from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
from transitions import Machine
from db import *
from flex_button import *

def BasicInfoSettingEntrance():
    message = TemplateSendMessage(
        alt_text='基本資料設定',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    text='初始資料設定',
                    actions=[
                        MessageTemplateAction(
                            label='點我設定',
                            text='初始資料設定'
                        )
                    ]
                ),
                CarouselColumn(
                    text='查看目前設定',
                    actions=[
                        MessageTemplateAction(
                            label='點我查看',
                            text='查看目前設定'
                        )
                    ]
                ),
                CarouselColumn(
                    text='設定用戶名稱',
                    actions=[
                        MessageTemplateAction(
                            label='點我設定',
                            text='設定用戶名稱'
                        )
                    ]
                ),
                CarouselColumn(
                    # thumbnail_image_url='',
                    # title='',
                    text='設定住家地址',
                    actions=[
                        # PostbackTemplateAction(
                        #     label='回傳一個訊息',
                        #     data='將這個訊息偷偷回傳給機器人'
                        # ),
                        MessageTemplateAction(
                            label='點我設定',
                            text='設定住家地址'
                        )
                        # URITemplateAction(
                        #     label='進入1的網頁',
                        #     uri='https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Number_1_in_green_rounded_square.svg/200px-Number_1_in_green_rounded_square.svg.png'
                        # )
                    ]
                ),
                # CarouselColumn(
                #     text='設定常用地點',
                #     actions=[
                #         MessageTemplateAction(
                #             label='點我設定',
                #             text='設定常用地點'
                #         )
                #     ]
                # ),
                CarouselColumn(
                    text='設定緊急聯絡人',
                    actions=[
                        MessageTemplateAction(
                            label='點我設定',
                            text='設定緊急聯絡人'
                        )
                    ]
                )
            ]
        )
    )
    return message

def setId(id, user_id):
    return

def BasicInfoSetting(line_bot_api, event, BISM):
    # print("user id", event.source.user_id)
    # print("message type", event.message.type)
    user_id = event.source.user_id
    if event.message.type == 'text':
        msg = event.message.text
        if BISM.state == 'default':
            if '初始資料設定' in msg:
                BISM.all_setting_id()
                return "用戶名稱設置：請輸入用戶名稱"
            elif '查看目前設定' in msg:
                return getCurrentSetting(event.source.user_id, BISM)
            elif '設定用戶名稱' in msg:
                BISM.setting_id()
                return "請輸入用戶名稱"
            elif '設定住家地址' in msg:
                BISM.setting_home()
                return "請點選下方的按鈕，輸入住家位置"
            # elif '設定常用地點' in msg:
            #     BISM.setting_often()
            #     return "請利用左下方的選單，輸入常用地點位置"
            elif '設定緊急聯絡人' in msg:
                BISM.setting_contact()
                return "請輸入緊急連絡人名稱"
        elif BISM.state == 'id':
            message = TextSendMessage(text="檢查名稱中...")
            line_bot_api.push_message(user_id, message)

            success = setUserName(user_id, msg)
            if success:
                BISM.info.name = msg
                BISM.reset()
                return "設定完成"
            else:
                return "此名稱已被使用過，請輸入另外的名稱"
        elif BISM.state == 'contact': 
            message = TextSendMessage(text="搜尋中...")
            line_bot_api.push_message(user_id, message)

            success, token = setContact(user_id, msg)
            BISM.reset()
            if success:
                BISM.info.contact_name = msg
                BISM.info.contact_token = token
                return "設定完成"
            else: 
                return "找不到此人。請確認對方已加入機器人好友，並已設定名稱"
        elif BISM.state == 'all_contact': 
            BISM.info.need_update = True
            message = TextSendMessage(text="搜尋中...")
            line_bot_api.push_message(user_id, message)

            success, token = checkContact(user_id, msg)
            BISM.reset()
            if success:
                BISM.info.contact_name = msg
                BISM.info.contact_token = token
                return "設定完成"
            else: 
                return "找不到此人。請確認對方已加入機器人好友，並已設定名稱"

        elif BISM.state == 'all_id':
            message = TextSendMessage(text="檢查名稱中...")
            line_bot_api.push_message(user_id, message)

            success = checkUserName(user_id, msg)
            if success:
                BISM.info.name = msg
                BISM.all_setting_home()
                return "住家設置：請點選下方的按鈕，輸入住家位置"
            else:
                return "此名稱已被使用過，請輸入另外的名稱"
    elif event.message.type == 'location':
        if BISM.state == 'home' or BISM.state == 'all_home':
            BISM.info.home_address = event.message.address
            BISM.info.home_la = event.message.latitude
            BISM.info.home_long = event.message.longitude

            if BISM.state == 'all_home':
                BISM.all_setting_contact()
                return "緊急聯絡人設置：請輸入緊急聯絡人名稱"
            else:
                setHome(
                    user_id,
                    event.message.address,
                    event.message.latitude,
                    event.message.longitude
                    )
                BISM.reset()
                return "設定完成"
    BISM.reset()
    return "無法辨識"

def getCurrentSetting(user_id, BISM):
    info = []
    if BISM.info.ready:
        info = [
            BISM.info.name, 
            BISM.info.home_address, 
            BISM.info.contact_name
            ]
    else:
        info = getUserInfo(user_id)
        info = info[0]

    result = '用戶名稱：' + info[0]
    result += '\n住家位置：' + info[1]
    result += '\n緊急聯絡人：' + info[2]

    return result

class Info:
    def __init__(self):
        self.ready = False
        self.need_update = False
        self.name = ''
        self.home_la = 0
        self.home_long = 0
        self.home_address = ''
        self.contact_name = ''
        self.contact_token = ''
    
    def set(self, name, home_la, home_long, home_address, contact_name, contact_token):
        self.ready = True
        self.name = name
        self.home_la = home_la
        self.home_long = home_long
        self.home_address = home_address
        self.contact_name = contact_name
        self.contact_token = contact_token


class BasicInfoStateMachine(object):

    states = ['default', 'id', 'home', 'contact', 'all_id', 'all_home', 'all_contact']

    def __init__(self):
        self.machine = Machine(model=self, states=BasicInfoStateMachine.states, initial='default')
        self.info = Info()

        # add_transition(trigger, source, dest)
        self.machine.add_transition('reset', '*', 'default')
        self.machine.add_transition('setting_id', '*', 'id')
        self.machine.add_transition('setting_home', '*', 'home')
        # self.machine.add_transition('setting_often', '*', 'often')
        self.machine.add_transition('setting_contact', '*', 'contact')
        self.machine.add_transition('all_setting_id', '*', 'all_id')
        self.machine.add_transition('all_setting_home', 'all_id', 'all_home')
        self.machine.add_transition('all_setting_contact', 'all_home', 'all_contact')
        # self.machine.add_transition('all_setting_often', 'all_home', 'all_often')
