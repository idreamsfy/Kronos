"""
使用 yfinance 获取股票 300033（东方财富）过去10年数据
并转换为 Kronos 格式保存为 CSV

注意: 300033.SZ 是东方财富在深圳证券交易所的代码
"""
import yfinance as yf
import pandas as pd
import os
from datetime import datetime

print("=" * 70)
print("使用 yfinance 获取股票 300033（东方财富）数据")
print("=" * 70)

# 股票代码 (深圳证券交易所)
stock_code = "300033.SZ"
output_dir = "./akshare_data"
output_file = os.path.join(output_dir, f"daily_300033.csv")

try:
    print(f"\n正在获取 {stock_code} 的历史数据...")
    print("时间范围: 2016-01-01 至 2026-04-19")
    
    # 下载历史数据
    df = yf.download(
        stock_code,
        start="2016-01-01",
        end="2026-04-19",
        interval="1d",
        progress=False
    )
    
    if df.empty:
        raise Exception("未获取到数据，可能是网络连接问题或股票代码错误")
    
    print(f"✅ 成功获取 {len(df)} 条记录")
    print(f"\n原始数据列: {list(df.columns)}")
    print(f"\n前5条数据:")
    print(df.head())
    
    # 转换数据格式为 Kronos 要求
    print("\n转换数据格式...")
    
    # 重置索引，将 Date 变为列
    df.reset_index(inplace=True)
    
    # 重命名列以匹配 Kronos 格式
    # yfinance 的列名: Date, Open, High, Low, Close, Volume, Adj Close
    df.rename(columns={
        'Date': 'timestamps',
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume'
    }, inplace=True)
    
    # 计算成交额 (amount = close * volume)
    # 注意: A股 volume 单位是股，不是手
    df['amount'] = df['close'] * df['volume']
    
    # 选择需要的列
    required_columns = ['timestamps', 'open', 'high', 'low', 'close', 'volume', 'amount']
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
    print(f"  - 成交量范围: {int(df['volume'].min()):,} - {int(df['volume'].max()):,}")
    print(f"  - 成交额范围: ¥{df['amount'].min():,.0f} - ¥{df['amount'].max():,.0f}")
    
    print(f"\n前5条数据:")
    print(df.head())
    
    print(f"\n后5条数据:")
    print(df.tail())
    
    print("\n" + "=" * 70)
    print("✅ 完成！数据符合 Kronos 训练要求")
    print("=" * 70)
    
    # 验证数据质量
    print("\n数据质量检查:")
    print(f"  - 缺失值: {df.isnull().sum().sum()}")
    print(f"  - OHLC 逻辑检查: ", end="")
    invalid = ((df['high'] < df['low']) | 
               (df['high'] < df['open']) | 
               (df['high'] < df['close']) |
               (df['low'] > df['open']) | 
               (df['low'] > df['close'])).sum()
    if invalid == 0:
        print("✅ 通过")
    else:
        print(f"⚠️  {invalid} 条异常")

except Exception as e:
    print(f"\n❌ 获取数据失败: {e}")
    print("\n可能的原因:")
    print("1. 网络连接问题")
    print("2. Yahoo Finance 暂时不可用")
    print("3. 股票代码格式错误")
    print("\n建议:")
    print("1. 检查网络连接")
    print("2. 稍后重试")
    print("3. 使用已有的 akshare_data 中的数据")
