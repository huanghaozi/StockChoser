import requests
import pandas as pd
import numpy as np
import demjson
import time
import re

TYPE_KEY_WORD = 'RPT_DMSK_FN_BALANCE'

df = pd.DataFrame()
notLoaded = []
response = requests.get(
    'http://datacenter.eastmoney.com/api/data/get?st=NOTICE_DATE%2CSECURITY_CODE&sr=-1%2C-1&ps=500&p=1&type=' + TYPE_KEY_WORD + '&sty=ALL')
if response.status_code == 200:
    pageNum = int(re.sub(r'.*"pages":([0-9]+).*', r'\1', response.text[:200]))
    l_cols = np.array([re.sub(r'.*"(.+)".*', r'\1', s) for s in re.findall(r'"[^:,]*?":', re.finditer(r'{.+?},', re.sub(
        r'.*"data":(\[.+]).*', r'\1', response.text)).__next__()[0])])

for p in range(1, pageNum + 1):
    try:
        if p > 1:
            response = requests.get(
                'http://datacenter.eastmoney.com/api/data/get?st=NOTICE_DATE%2CSECURITY_CODE&sr=-1%2C-1&ps=500&p='
                + str(p) + '&type=' + TYPE_KEY_WORD + '&sty=ALL')
            while response.status_code != 200:
                time.sleep(5)
                response = requests.get(
                    'http://datacenter.eastmoney.com/api/data/get?st=NOTICE_DATE%2CSECURITY_CODE&sr=-1%2C-1&ps=500&p='
                    + str(p) + '&type=' + TYPE_KEY_WORD + '&sty=ALL')
        l_str = re.sub(r'"[^:,]*?":', r'',
                       re.sub(r'{', r'[', re.sub(r'}', r']', re.sub(r'.*"data":(\[.*]).*', r'\1', response.text))))
        dataContent = np.array(demjson.decode(l_str))
        df_temp = pd.DataFrame(dataContent, columns=l_cols)
        df = pd.concat([df, df_temp], axis=0)
        print('已获取' + str(p) + '页')
    except:
        notLoaded.append(p)
        continue

codes = df['SECUCODE'].drop_duplicates()
for code in codes:
    df_temp = df[df['SECUCODE'] == code]
    df_temp.to_excel('./资产负债表/' + code + '.xlsx')
