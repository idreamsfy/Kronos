import tushare as ts
ts.set_token('6dafd0f683c71cd9032943e9029f2bb5a1a871684ed7bac4eef07c93')
pro = ts.pro_api()
#df = pro.daily(ts_code='600000.SH', start_date='20200101', end_date='20201231')
df = pro.trade_cal(exchange='', start_date='20250901', end_date='20251001', fields='exchange,cal_date,is_open,pretrade_date', is_open='0')

print(df.head())