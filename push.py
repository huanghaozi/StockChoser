import requests
import json
import os

token = os.getenv('token')
title = '选股器今日数据'
topic = 'StockChoser'
f = open('推送.html', 'r', encoding='utf-8')
content = f.read()
url = 'http://pushplus.hxtrip.com/send'
data = {
    "token": token,
    "title": title,
    "content": content,
    "topic": topic
}
body = json.dumps(data).encode(encoding='utf-8')
headers = {'Content-Type': 'application/json'}
requests.post(url, data=body, headers=headers)
