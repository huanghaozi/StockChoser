import requests
import pandas as pd
import numpy as np
import simplejson
import time
import datetime
import re

date = (datetime.datetime.now() + datetime.timedelta(days=-7)).strftime('%Y-%m-%d')


def requests_data(p, TYPE_KEY_WORD):
    global date
    try:
        response = requests.get(
            'http://datacenter.eastmoney.com/api/data/get?st=NOTICE_DATE%2CSECURITY_CODE&sr=-1%2C-1&ps=500&p='
            + str(p) + '&type=' + TYPE_KEY_WORD + '&sty=ALL&filter=(NOTICE_DATE>=%27' + date + '%27)')
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
    for index, row in df.iterrows():
        try:
            df_target = pd.read_excel('./' + dirName + '/' + row['SECUCODE'] + '.xlsx', dtype='object', index_col=0)
        except FileNotFoundError:
            df_target = df.iloc[[index]]
            df_target.to_excel('./' + dirName + '/' + row['SECURITY_CODE'] + '.xlsx', index=False)
            continue
        df_target = df_target.append(row)
        df_target.drop_duplicates()
        df_target.to_excel('./' + dirName + '/' + row['SECURITY_CODE'] + '.xlsx', index=False)


d = {'RPT_LICO_FN_CPD': '业绩报表', 'RPT_DMSK_FN_BALANCE': '资产负债表',
     'RPT_DMSK_FN_INCOME': '利润表', 'RPT_DMSK_FN_CASHFLOW': '现金流量表'}
df_calc = pd.DataFrame()
for key, value in d.items():
    df = get_data(key)
    if value == '业绩报表' or value == '资产负债表':
        if df_calc.empty:
            df_calc = df
        else:
            df_calc = pd.merge(left=df_calc, right=df, left_on=['SECURITY_CODE', 'REPORTDATE'],
                               right_on=['SECURITY_CODE', 'REPORT_DATE']).reset_index(drop=True)
    extract_data(df, value)

df_NO_ADV = df_calc.drop(columns=['ADVANCE_RECEIVABLES']).dropna()
df_NO_ADV = df_NO_ADV.drop(index=df_NO_ADV[df_NO_ADV['TOTAL_OPERATE_INCOME'] == 0].index)
df_NO_ADV = df_NO_ADV.drop(index=df_NO_ADV[df_NO_ADV['BASIC_EPS'] == 0].index)
df_NO_ADV = df_NO_ADV.drop(index=df_NO_ADV[df_NO_ADV['TOTAL_ASSETS'] == 0].index)
new_df_NO_ADV = pd.DataFrame()
new_df_NO_ADV['公告日'] = df_NO_ADV['NOTICE_DATE_x']
new_df_NO_ADV['报告期'] = df_NO_ADV['REPORTDATE']
new_df_NO_ADV['证券名称'] = df_NO_ADV['SECURITY_NAME_ABBR_x']
new_df_NO_ADV['证券代码'] = df_NO_ADV['SECURITY_CODE']
new_df_NO_ADV['净利率'] = df_NO_ADV['PARENT_NETPROFIT'] * 100 / df_NO_ADV['TOTAL_OPERATE_INCOME']
new_df_NO_ADV['毛利率'] = df_NO_ADV['XSMLL']
new_df_NO_ADV['应收账款占营收'] = df_NO_ADV['ACCOUNTS_RECE'] * 100 / df_NO_ADV['TOTAL_OPERATE_INCOME']
new_df_NO_ADV['经营净额比净利润'] = df_NO_ADV['MGJYXJJE'] * 100 / df_NO_ADV['BASIC_EPS'].where(df_NO_ADV['BASIC_EPS'] != 0.0,
                                                                                       0.00000001)
new_df_NO_ADV['净资产收益率ROE'] = df_NO_ADV['WEIGHTAVG_ROE']
new_df_NO_ADV['资产负债比'] = df_NO_ADV['TOTAL_LIABILITIES'] * 100 / df_NO_ADV['TOTAL_ASSETS']
new_df_NO_ADV['投入资本回报率ROIC'] = df_NO_ADV['WEIGHTAVG_ROE'] * 100 / (100 + new_df_NO_ADV['资产负债比'])

df = new_df_NO_ADV
df = df[df['净利率'] >= 10]
df = df[df['毛利率'] >= 40]
df = df[df['应收账款占营收'] <= 20]
df = df[df['经营净额比净利润'] >= 120]
df = df[df['净资产收益率ROE'] >= 15]
df = df[df['投入资本回报率ROIC'] >= 3]

newly = df[['证券代码', '证券名称', '公告日', '报告期']].apply(lambda y: y.apply(lambda x: x.split(' 00:00:00')[0]))
output = '# 近七日新增\r\n'
s = newly.to_markdown(index=False)
output += s
output += '\r\n\r\n'

df_origin = pd.read_excel('筛选结果.xlsx', dtype='object')
df = pd.concat([df_origin, df], axis=0)
df.to_excel('筛选结果.xlsx', index=False)

date = datetime.datetime.now()
month = (date.month - 1) - (date.month - 1) % 3 + 1
newdate = datetime.datetime(date.year, month, 1)
newdate = newdate + datetime.timedelta(days=-1)
near = df[pd.to_datetime(df['报告期']) >= newdate][['证券代码', '证券名称', '公告日', '报告期']].apply(
    lambda y: y.apply(lambda x: x.split(' 00:00:00')[0]))
output += '# 最近季度\r\n'
s = near.to_markdown(index=False)
output += s
output += '\r\n\r\n'

date = newdate
month = (date.month - 1) - (date.month - 1) % 3 + 1
newdate = datetime.datetime(date.year, month, 1)
newdate = newdate + datetime.timedelta(days=-1)
nearlast = df[pd.to_datetime(df['报告期']) == newdate][['证券代码', '证券名称', '公告日', '报告期']].apply(
    lambda y: y.apply(lambda x: x.split(' 00:00:00')[0]))
output += '# 上一季度\r\n'
s = nearlast.to_markdown(index=False)
output += s
output += '\r\n\r\n'

date = newdate
month = (date.month - 1) - (date.month - 1) % 3 + 1
newdate = datetime.datetime(date.year, month, 1)
newdate = newdate + datetime.timedelta(days=-1)
nearnearlast = df[pd.to_datetime(df['报告期']) == newdate][['证券代码', '证券名称', '公告日', '报告期']].apply(
    lambda y: y.apply(lambda x: x.split(' 00:00:00')[0]))
output += '# 上上季度\r\n'
s = nearnearlast.to_markdown(index=False)
output += s
output += '\r\n\r\n'

jnji1 = pd.merge(near, nearlast, on=['证券代码', '证券名称'])[['证券代码', '证券名称']]
jnji2 = pd.merge(near, nearnearlast, on=['证券代码', '证券名称'])[['证券代码', '证券名称']]
jnji = pd.concat([jnji1, jnji2], axis=0).drop_duplicates()
output += '# 交集\r\n'
s = jnji.to_markdown(index=False)
output += s
output += '\r\n\r\n'

f = open('推送.md', 'w', encoding='utf-8')
f.write(output)
f.close()
