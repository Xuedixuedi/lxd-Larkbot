import json
import time

import schedule
import requests

import config

dance_url = config.DANCE_WEB_HOOK  # bot的webhook地址
byte_sport_app_url = config.BYTE_SPORT_APP
dance_time = "18:45"

dance_text_message = {
    "msg_type": "interactive",
    "card": {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "template": "turquoise",
            "title": {
                "content": " 💃 运动提醒",
                "tag": "plain_text"
            }
        },
        "i18n_elements": {
            "zh_cn": [
                {
                    "tag": "div",
                    "text": {
                        "content": "请马上离开工位下班，否则来不及了。",
                        "tag": "lark_md"
                    }
                },
                {
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "content": "查看课程",
                                "tag": "plain_text"
                            },
                            "type": "primary",
                            "url": byte_sport_app_url
                        }, {
                            "tag": "button",
                            "text": {
                                "content": "现在下班",
                                "tag": "plain_text"
                            },
                            "type": "default",
                            "url": ""
                        }
                    ],
                    "tag": "action"
                }
            ]
        }
    }
}


def dance_bot_push(headers):
    response = requests.request("POST", dance_url, headers=headers, data=json.dumps(dance_text_message))
    print(response.text)


# 每天18：45重复
def dance_bot_repeat(headers):
    schedule.every().monday.at("18:45").do(dance_bot_push, headers)
    schedule.every().tuesday.at("18:45").do(dance_bot_push, headers)
    schedule.every().wednesday.at("18:45").do(dance_bot_push, headers)
    # schedule.every(10).seconds.do(dance_bot_push, headers)
