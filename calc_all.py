import pandas as pd
import os


def get_union_codes(keys):
    filenames = []
    for key in keys:
        filename_temp = []
        for root, dirs, files in os.walk('./' + key):
            for filename in files:
                filename_temp.append(filename)
        filenames.append(filename_temp)
    result = []
    for l in filenames:
        if len(result) == 0:
            result = l
        else:
            result = [j for j in result if j in l]
    return result


def extract_data(dirName, colNames, codes):
    df = pd.DataFrame()
    for root, dirs, files in os.walk('./' + dirName):
        for filename in files:
            if filename in codes:
                filepath = os.path.join(root, filename)
                df_temp = pd.read_excel(filepath, dtype='object')[colNames]
                df = pd.concat([df, df_temp], axis=0)
    return df


d = {'业绩报表': ['SECURITY_CODE', 'SECURITY_NAME_ABBR', 'NOTICE_DATE', 'REPORTDATE',
              'TOTAL_OPERATE_INCOME', 'PARENT_NETPROFIT', 'WEIGHTAVG_ROE', 'MGJYXJJE', 'BASIC_EPS', 'XSMLL'],
     '资产负债表': ['SECURITY_CODE', 'SECURITY_NAME_ABBR', 'NOTICE_DATE', 'REPORT_DATE',
               'ACCOUNTS_RECE', 'ADVANCE_RECEIVABLES', 'TOTAL_ASSETS', 'TOTAL_LIABILITIES']}

codes = get_union_codes(d.keys())
df = pd.DataFrame()
for key, value in d.items():
    if df.empty:
        df = extract_data(key, value, codes)
    else:
        df_temp = extract_data(key, value, codes)
        df = pd.merge(left=df, right=df_temp, left_on=['SECURITY_CODE', 'REPORTDATE'],
                      right_on=['SECURITY_CODE', 'REPORT_DATE']).reset_index(drop=True)

df_NO_ADV = df.drop(columns=['ADVANCE_RECEIVABLES']).dropna()
df_NO_ADV = df_NO_ADV.drop(index=df_NO_ADV[df_NO_ADV['TOTAL_OPERATE_INCOME'] == 0].index)
df_NO_ADV = df_NO_ADV.drop(index=df_NO_ADV[df_NO_ADV['BASIC_EPS'] == 0].index)
df_NO_ADV = df_NO_ADV.drop(index=df_NO_ADV[df_NO_ADV['TOTAL_ASSETS'] == 0].index)
new_df_NO_ADV = pd.DataFrame()
new_df_NO_ADV['公告日'] = df_NO_ADV['NOTICE_DATE_x']
new_df_NO_ADV['报告期'] = df_NO_ADV['REPORTDATE']
new_df_NO_ADV['证券名称'] = df_NO_ADV['SECURITY_NAME_ABBR_x']
new_df_NO_ADV['证券代码'] = df_NO_ADV['SECURITY_CODE']
new_df_NO_ADV['净利率'] = df_NO_ADV['PARENT_NETPROFIT']*100/df_NO_ADV['TOTAL_OPERATE_INCOME']
new_df_NO_ADV['毛利率'] = df_NO_ADV['XSMLL']
new_df_NO_ADV['应收账款占营收'] = df_NO_ADV['ACCOUNTS_RECE']*100/df_NO_ADV['TOTAL_OPERATE_INCOME']
new_df_NO_ADV['经营净额比净利润'] = df_NO_ADV['MGJYXJJE']*100/df_NO_ADV['BASIC_EPS'].where(df_NO_ADV['BASIC_EPS'] != 0.0, 0.00000001)
new_df_NO_ADV['净资产收益率ROE'] = df_NO_ADV['WEIGHTAVG_ROE']
new_df_NO_ADV['资产负债比'] = df_NO_ADV['TOTAL_LIABILITIES']*100/df_NO_ADV['TOTAL_ASSETS']
new_df_NO_ADV['投入资本回报率ROIC'] = df_NO_ADV['WEIGHTAVG_ROE']*100/(100+new_df_NO_ADV['资产负债比'])
new_df_NO_ADV.to_excel('计算指标.xlsx', index=False)

