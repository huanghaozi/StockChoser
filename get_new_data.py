import requests
import pandas as pd
import numpy as np
import demjson
import time
import datetime
import re

date = (datetime.datetime.now() + datetime.timedelta(days=-7)).strftime('%Y-%m-%d')
url = 'http://datacenter.eastmoney.com/api/data/get?st=NOTICE_DATE%2CSECURITY_CODE&sr=-1%2C-1&ps=500&p=1&type' \
      '=RPT_DMSK_FN_INCOME&sty=ALL&filter=(NOTICE_DATE>=%27' + date + '%27)'
response = requests.get(url)
while response.status_code != 200:
    time.sleep(5)
    response = requests.get(url)
pageNum = int(re.sub(r'.*"pages":([0-9]+).*', r'\1', response.text[:200]))
l_cols = np.array([re.sub(r'.*"(.+)".*', r'\1', s) for s in re.findall(r'"[^:,]*?":', re.finditer(r'{.+?},', re.sub(
        r'.*"data":(\[.+]).*', r'\1', response.text)).__next__()[0])])
df = pd.DataFrame()
for p in range(1, pageNum + 1):
    try:
        if p > 1:
            response = requests.get(
                'http://datacenter.eastmoney.com/api/data/get?st=NOTICE_DATE%2CSECURITY_CODE&sr=-1%2C-1&ps=500&p='
                + str(p) + '&type=RPT_DMSK_FN_INCOME&sty=ALL')
            while response.status_code != 200:
                time.sleep(5)
                response = requests.get(
                    'http://datacenter.eastmoney.com/api/data/get?st=NOTICE_DATE%2CSECURITY_CODE&sr=-1%2C-1&ps=500&p='
                    + str(p) + '&type=RPT_DMSK_FN_INCOME&sty=ALL')
        l_str = re.sub(r'"[^:,]*?":', r'',
                       re.sub(r'{', r'[', re.sub(r'}', r']', re.sub(r'.*"data":(\[.*]).*', r'\1', response.text))))
        dataContent = np.array(demjson.decode(l_str))
        df_temp = pd.DataFrame(dataContent, columns=l_cols)
        df = pd.concat([df, df_temp], axis=0)
        print('已获取' + str(p) + '页')
    except Exception:
        continue

for index, row in df.iterrows():
    try:
        df_target = pd.read_excel('./利润表/' + row['SECUCODE'] + '.xlsx', dtype='object', index_col=0)
    except FileNotFoundError:
        df_target = df.iloc[[index]]
        df_target.to_excel('./利润表/' + row['SECUCODE'] + '.xlsx')
        continue
    df_target = df_target.append(row)
    df_target.drop_duplicates()
    df_target.to_excel('./利润表/' + row['SECUCODE'] + '.xlsx')

