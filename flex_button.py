def getWarnMapFlex(text, latitude1, longitude1, latitude2, longitude2):
   pos = "?"
   if latitude1 > 0:
      pos += "latitude1=" + "{:.6f}".format(latitude1) + "&longitude1=" + "{:.6f}".format(longitude1)
   if latitude2 > 0:
      if pos != "?":
         pos += "&"
      pos += "latitude2=" + "{:.6f}".format(latitude2) + "&longitude2=" + "{:.6f}".format(longitude2)
   if pos == "?":
      pos = ""
      
   
   return {
      "type": "bubble",
      "body": {
         "type": "box",
         "layout": "vertical",
         "contents": [
            {
               "type": "text",
               "text": "在回家的路上會經過的危險地點如下：",
               "wrap": True,
               "size": "lg"
            },
            {
               "type": "box",
               "layout": "vertical",
               "margin": "lg",
               "contents": [
                  {
                     "type": "box",
                     "layout": "baseline",
                     "spacing": "sm",
                     "contents": [
                        {
                           "type": "text",
                           "text": text,
                           "wrap": True,
                           "color": "#666666",
                           "flex": 5
                        }
                     ]
                  }
               ]
            }
         ]
      },
      "footer": {
         "type": "box",
         "layout": "vertical",
         "spacing": "sm",
         "contents": [
            {
               "type": "button",
               "style": "link",
               "height": "sm",
               "action": {
                  "type": "uri",
                  "label": "打開地圖",
                  "uri": "https://TeresaChou.github.io/WarnMap/index.html" + pos
               }
            }
            # {
            #    "type": "spacer",
            #    "size": "sm"
            # }
         ],
         "flex": 0
      }
   }

def getDemoWarnFlex(name):
   # text = "危險地點：指南路一段道南橋下涵洞附近\n\
   #    所屬轄區：台北市政府警察局文山地基分局\n\
   #    轄區聯絡人：陳警務員、02-27592016、02-27269541"
   return {
      "type": "bubble",
      "body": {
         "type": "box",
         "layout": "vertical",
         "contents": [
            {
               "type": "text",
               "text": name + "在危險地方已經超過五分鐘了，請快確認他的人身安全吧！",
               "wrap": True,
               "size": "lg"
            }
         ]
      },
      "footer": {
         "type": "box",
         "layout": "vertical",
         "spacing": "sm",
         "contents": [
            {
               "type": "button",
               "style": "link",
               "height": "sm",
               "action": {
                  "type": "uri",
                  "label": "打開地圖",
                  "uri": "https://TeresaChou.github.io/WarnMap/index.html?demo=1"
               }
            }
            # {
            #    "type": "spacer",
            #    "size": "sm"
            # }
         ],
         "flex": 0
      }
   }


def chooseLocationButton():
   return {
      'items': [
         {
            'type': 'action',
            'action': {
               'type':'location',
               'label': '按我選擇地點'
            }
         }
      ]
   }

def arriveHomeButton():
   return {
      'items': [
         {
            'type': 'action',
            'action': {
               'type':'postback',
               'label': '到家了',
               'data': 'arrive_home'
               # 'text': '到家了/行程取消'
            }
         },
         {
            'type': 'action',
            'action': {
               'type':'postback',
               'label': '行程取消',
               'data': 'cancel_schedule'
               # 'text': '到家了/行程取消'
            }
         }
      ]
   }

def noted_button():
   return {
      'items': [
         {
            'type': 'action',
            'action': {
               'type':'postback',
               'label': '知道了',
               'data': 'demo_noted'
            }
         }
      ]
   }