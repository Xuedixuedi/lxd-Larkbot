import json
import requests
import config
import receive_mail

url = config.DANCE_WEB_HOOK  # bot的webhook地址
byte_sport_app_url = config.BYTE_SPORT_APP
time = "19:00"
mail_text = receive_mail.mail()

text_message = {
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
                        "content": "请在今天" + time + "前离开工位下班，否则来不及了。",
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

headers = {
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=json.dumps(text_message))
print(response.text)
