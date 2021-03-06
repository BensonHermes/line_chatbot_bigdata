from linebot.models import FlexSendMessage
from transitions import Machine
from flex_button import *
from db import *

# nccu_lat = 24.9861694
# nccu_long = 121.5749262

def GetWarn(event, BISM, GWSM):
    home_lat = 0
    home_long = 0
    if BISM.info.ready:
        home_lat = BISM.info.home_la
        home_long = BISM.info.home_long
    else:
        home_info = getHomeInfo(event.source.user_id)[0]
        home_lat = float(home_info[1])
        home_long = float(home_info[2])

    latitude = event.message.latitude
    longitude = event.message.longitude
    lat1 = min(latitude, home_lat) - 0.002
    lat2 = max(latitude, home_lat) + 0.002
    long1 = min(longitude, home_long) - 0.002
    long2 = max(longitude, home_long) + 0.002

    text = ''
    res = getWarnPlaceInRange(lat1, long1, lat2, long2)
    num = 1
    for (DeptNm, BranchNm, Address, Contact) in res:
        place = DeptNm + BranchNm
        if num > 1:
            text += "\n"
        text += "危險地點%d: %s\n所屬轄區: %s\n轄區聯絡人:  %s" % (num, Address, place, Contact)
        num += 1
    
    if text == '':
        text = "無"

    message = FlexSendMessage(
        alt_text = '警示地點查詢結果',
        contents = getWarnMapFlex(text, latitude, longitude, home_lat, home_long)
    )
    return message

class GetWarnStateMachine(object):

    states = ['default', 'locate']

    def __init__(self):

        self.start_location = {}
        self.machine = Machine(model=self, states=GetWarnStateMachine.states, initial='default')

        # add_transition(trigger, source, dest)
        self.machine.add_transition('reset', '*', 'default')
        self.machine.add_transition('locate', '*', 'locate')

# testing data:
# NCCU: 24.9861694,121.5749262