import pandas as pd

df = pd.read_excel('计算指标.xlsx', dtype={'证券代码': 'object'})


df = df[df['净利率'] >= 10]
df = df[df['应收账款占营收'] < 20]
df = df[df['经营净额比净利润'] > 120]
df = df[df['净资产收益率ROE'] > 15]
df = df[df['投入资本回报率ROIC'] > 3]
df = df[df['毛利率'] >= 40]
df.to_excel('筛选结果.xlsx', index=False)
