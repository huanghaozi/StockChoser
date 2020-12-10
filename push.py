import requests
import json
import os

token = os.getenv('INPUT_TOKEN')
title = '选股器今日数据'  # 改成你要的标题内容
f = open('推送.html', 'r', encoding='utf-8')
content = f.read()
url = 'http://pushplus.hxtrip.com/send'
data = {
    "token": token,
    "title": title,
    "content": content
}
body = json.dumps(data).encode(encoding='utf-8')
headers = {'Content-Type': 'application/json'}
requests.post(url, data=body, headers=headers)
