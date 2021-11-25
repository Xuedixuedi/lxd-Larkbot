import json
import os
import poplib
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr

import requests
import schedule

import config

mail_url = config.MAIL_URL
mail_text = ""
mail_bot_url = config.MAIL_WEB_HOOK


# 获取邮件的信息
# param: 为解码的原始文本，text是为了存放递归调用的文本
# indent用于缩进显示:
def get_mail_info(msg, mail_text, indent=0):
    if indent == 0:
        for header in ['From', 'To', 'Subject']:
            value = msg.get(header, '')
            if value:
                if header == 'Subject':
                    value = decode_str(value)
                else:
                    hdr, addr = parseaddr(value)
                    name = decode_str(hdr)
                    value = u'%s <%s>' % (name, addr)
            # print('%s%s: %s' % ('  ' * indent, header, value))
            mail_text += '%s%s: %s' % ('  ' * indent, header, value) + "\n"

    if msg.is_multipart():
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            # mail_text += '%spart %s' % ('  ' * indent, n) + "\n"
            mail_text += '%s--------------------' % ('  ' * indent) + '\n'
            # print('%spart %s' % ('  ' * indent, n))
            # print('%s--------------------' % ('  ' * indent))
            mail_text = get_mail_info(part, mail_text, indent + 1)
            if n == 0:
                break
    else:
        content_type = msg.get_content_type()
        if content_type == 'text/plain' or content_type == 'text/html':
            content = msg.get_payload(decode=True)
            charset = guess_charset(msg)

            if charset:
                content = content.decode(charset)

            mail_text += '%sText: %s' % ('  ' * indent, content + '...') + '\n'
            # print('%sText: %s' % ('  ' * indent, content + '...'))
        else:
            print('%sAttachment: %s' % ('  ' * indent, content_type))

    return mail_text


# 对返回的文本解码成可读
def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


# 获取文本的编码格式
# 这个只能猜测是utf-8的才可以，如果不是就寄了，但是寄了也问题不大
def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


# 所有和邮箱有关的操作整合在一个函数中
def mail():
    # 输入邮件地址, 口令和POP3服务器地址:
    email = config.EMAIL_ADDRESS
    password = config.EMAIL_PASSWORD
    pop3_server = config.POP3_SERVER

    # 连接到POP3服务器:
    server = poplib.POP3(pop3_server)

    # 可选:打印POP3服务器的欢迎文字:
    print(server.getwelcome().decode('utf-8'))

    # 身份认证:
    server.user(email)
    server.pass_(password)

    # stat()返回邮件数量和占用空间:
    print('Messages: %s. Size: %s' % server.stat())
    # list()返回所有邮件的编号:
    resp, mails, octets = server.list()
    # 可以查看返回的列表类似[b'1 82923', b'2 2184', ...]
    # print(mails)

    # 获取最新一封邮件, 注意索引号从1开始:
    index = len(mails)
    resp, lines, octets = server.retr(index)

    # lines存储了邮件的原始文本的每一行,
    # 可以获得整个邮件的原始文本:
    msg_content = b'\r\n'.join(lines).decode('utf-8')
    # 稍后解析出邮件:
    msg = Parser().parsestr(msg_content)

    # 解析后的文本
    mail_text = ""
    mail_text = get_mail_info(msg, mail_text)
    print(mail_text)

    # 关闭连接:
    server.quit()

    return mail_text


def mail_bot_push(headers):
    mail_text = "**邮箱中最新的一封邮件为：**\n" + mail()
    mail_text = os.linesep.join([s for s in mail_text.splitlines() if s])  # 删除多余空行

    mail_text_message = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "template": "orange",
                "title": {
                    "content": " 📧 邮件提醒",
                    "tag": "plain_text"
                }
            },
            "i18n_elements": {
                "zh_cn": [
                    {
                        "tag": "div",
                        "text": {
                            "content": mail_text,
                            "tag": "lark_md"
                        }
                    },
                    {
                        "actions": [
                            {
                                "tag": "button",
                                "text": {
                                    "content": "进入邮箱",
                                    "tag": "plain_text"
                                },
                                "type": "primary",
                                "url": mail_url
                            }, {
                                "tag": "button",
                                "text": {
                                    "content": "好的",
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

    response = requests.request("POST", mail_bot_url, headers=headers, data=json.dumps(mail_text_message))
    print(response.text)


def mail_bot_repeat(headers):
    schedule.every().day.at("17:30").do(mail_bot_push, headers)
