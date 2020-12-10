import requests
import pandas as pd
import numpy as np
import simplejson
import time
import re


def requests_data(p, TYPE_KEY_WORD):
    try:
        response = requests.get(
            'http://datacenter.eastmoney.com/api/data/get?st=NOTICE_DATE%2CSECURITY_CODE&sr=-1%2C-1&ps=500&p='
            + str(p) + '&type=' + TYPE_KEY_WORD + '&sty=ALL')
    except:
        time.sleep(5)
        response = requests_data(p, TYPE_KEY_WORD)
    return response


def get_data(TYPE_KEY_WORD):
    df = pd.DataFrame()
    response = requests_data(1, TYPE_KEY_WORD)
    pageNum = int(re.sub(r'.*"pages":([0-9]+).*', r'\1', response.text[:200]))
    l_cols = np.array(
        [re.sub(r'.*"(.+)".*', r'\1', s) for s in re.findall(r'"[^:,]*?":', re.finditer(r'{.+?},', re.sub(
            r'.*"data":(\[.+]).*', r'\1', response.text)).__next__()[0])])
    for p in range(1, pageNum + 1):
        if p > 1:
            response = requests_data(p, TYPE_KEY_WORD)
            while response.status_code != 200 or len(re.findall(r'"data":', response.text)) == 0:
                response = requests_data(p, TYPE_KEY_WORD)
        l_str = re.sub(r'"[^:,]*?":', r'',
                       re.sub(r'{', r'[', re.sub(r'}', r']', re.sub(r'.*"data":(\[.*]).*', r'\1', response.text))))
        dataContent = np.array(simplejson.loads(l_str))
        df_temp = pd.DataFrame(dataContent, columns=l_cols)
        df = pd.concat([df, df_temp], axis=0)
        print('已获取' + str(p) + '页')
    return df


def extract_data(df, dirName):
    codes = df['SECURITY_CODE'].drop_duplicates()
    for code in codes:
        df_temp = df[df['SECURITY_CODE'] == code]
        df_temp.to_excel('./' + dirName + '/' + code + '.xlsx', index=False)


d = {'RPT_LICO_FN_CPD': '业绩报表', 'RPT_DMSK_FN_BALANCE': '资产负债表',
     'RPT_DMSK_FN_INCOME': '利润表', 'RPT_DMSK_FN_CASHFLOW': '现金流量表'}
for key, value in d.items():
    df = get_data(key)
    extract_data(df, value)
