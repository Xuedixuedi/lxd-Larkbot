import time

import schedule

import dance
import receive_mail

# mail_text = receive_mail.mail()

headers = {
    'Content-Type': 'application/json'
}

if __name__ == '__main__':
    dance.dance_bot_repeat(headers)  # 跳舞提醒机器人
    receive_mail.mail_bot_repeat(headers)  # 邮箱机器人

    while True:
        schedule.run_pending()
        time.sleep(1)
