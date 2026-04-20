"""
使用 Tushare 获取股票 300033（东方财富）过去10年数据
并转换为 Kronos 格式保存为 CSV
"""
import tushare as ts
import pandas as pd
import os
from datetime import datetime

print("=" * 70)
print("使用 Tushare 获取股票 300033（东方财富）数据")
print("=" * 70)

# 股票代码
stock_code = "300033"
output_dir = "./akshare_data"
output_file = os.path.join(output_dir, f"daily_{stock_code}.csv")

try:
    print(f"\n正在获取 {stock_code} 的历史数据...")
    
    # ==================== 配置 Tushare Token ====================
    # 请在此处填入您的 Tushare Token
    # 获取 Token: https://tushare.pro/user/token
    TUSHARE_TOKEN = "6dafd0f683c71cd9032943e9029f2bb5a1a871684ed7bac4eef07c93"  # <-- 请替换为您的实际 Token
    # ==========================================================
    
    if TUSHARE_TOKEN == "YOUR_TUSHARE_TOKEN_HERE":
        raise Exception("请先在脚本中设置 TUSHARE_TOKEN")
    
    # 设置 Token
    ts.set_token(TUSHARE_TOKEN)
    pro = ts.pro_api()
    
    print("使用 Tushare Pro API 获取数据...")
    
    # 尝试获取日线数据
    try:
        df = pro.daily(ts_code=f"{stock_code}.SZ", 
                      start_date='20160101', 
                      end_date='20260419')
        
        if df.empty:
            raise Exception("未获取到数据")
            
        print(f"✅ 通过 daily 接口获取成功: {len(df)} 条记录")
        
    except Exception as e:
        print(f"daily 接口失败: {e}")
        print("尝试使用 stock_basic + daily_basic 组合...")
        
        # 尝试其他免费接口
        try:
            # 获取股票基本信息
            stock_info = pro.stock_basic(ts_code=f"{stock_code}.SZ", fields='ts_code,symbol,name,area,industry,list_date')
            print(f"股票信息: {stock_info.iloc[0]['name']} ({stock_info.iloc[0]['symbol']})")
            
            # 尝试使用 adj_factor 和 daily_basic
            df = pro.adj_factor(ts_code=f"{stock_code}.SZ", start_date='20160101', end_date='20260419')
            
            if df.empty:
                raise Exception("adj_factor 也未获取到数据")
            
            print(f"✅ 获取到复权因子: {len(df)} 条记录")
            print("注意: 此接口仅提供复权因子，需要结合其他数据源")
            
        except Exception as e2:
            raise Exception(f"所有接口均失败: {e2}")
    
    # 转换数据格式为 Kronos 要求
    print("\n转换数据格式...")
    
    if 'trade_date' in df.columns:
        # Pro 接口格式
        df.rename(columns={
            'trade_date': 'timestamps',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'vol': 'volume',
            'amount': 'amount'
        }, inplace=True)
    else:
        # 旧版接口格式
        df.reset_index(inplace=True)
        df.rename(columns={
            'date': 'timestamps',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume',
            'price_change': 'amount'  # 旧版没有 amount，用 price_change 替代
        }, inplace=True)
    
    # 选择需要的列
    required_columns = ['timestamps', 'open', 'high', 'low', 'close', 'volume', 'amount']
    
    # 检查是否有 amount 列，如果没有则计算
    if 'amount' not in df.columns or df['amount'].isnull().all():
        print("计算成交额 (amount = close * volume)...")
        df['amount'] = df['close'] * df['volume'] * 100  # volume 是手，需要乘以100
    
    df = df[required_columns]
    
    # 转换时间格式
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    # 按时间排序
    df = df.sort_values('timestamps').reset_index(drop=True)
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存为 CSV
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ 数据已成功保存至: {output_file}")
    print(f"\n数据统计:")
    print(f"  - 记录数: {len(df)}")
    print(f"  - 时间范围: {df['timestamps'].min()} 至 {df['timestamps'].max()}")
    print(f"  - 收盘价范围: ¥{df['close'].min():.2f} - ¥{df['close'].max():.2f}")
    print(f"  - 成交量范围: {df['volume'].min()} - {df['volume'].max()}")
    print(f"\n前5条数据:")
    print(df.head())
    
    print("\n" + "=" * 70)
    print("完成！数据符合 Kronos 训练要求")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ 获取数据失败: {e}")
    print("\n使用说明:")
    print("1. 打开文件: tests/fetch_300033_tushare.py")
    print("2. 找到第 23 行的 TUSHARE_TOKEN 变量")
    print("3. 将 'YOUR_TUSHARE_TOKEN_HERE' 替换为您的实际 Token")
    print("4. 保存文件后重新运行")
    print("\n获取 Token:")
    print("  - 访问: https://tushare.pro/user/token")
    print("  - 登录后复制您的 Token")
