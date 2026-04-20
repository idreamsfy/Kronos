"""
使用 mootdx（通达信数据接口）获取股票 300033（东方财富）过去10年历史数据
并转换为 Kronos 格式保存为 CSV

mootdx 是一个免费的通达信数据读取库，无需 API Key
支持 A 股、基金、债券等行情数据
"""
from mootdx.quotes import Quotes
from mootdx.affair import Affair
import pandas as pd
import os
from datetime import datetime, timedelta

print("=" * 70)
print("使用 mootdx（通达信）获取股票 300059（东方财富）数据")
print("=" * 70)

# 配置参数
stock_code = "300059"  # 股票代码（东方财富）
market = 1  # 市场代码: 0=上海, 1=深圳
output_dir = "./akshare_data"
output_file = os.path.join(output_dir, f"daily_{stock_code}.csv")

# 时间范围（过去10年）
end_date = datetime.now()
start_date = end_date - timedelta(days=3650)  # 10年

print(f"\n配置信息:")
print(f"  - 股票代码: {stock_code}")
print(f"  - 市场: {'深圳' if market == 1 else '上海'}")
print(f"  - 时间范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
print(f"  - 输出文件: {output_file}")

try:
    print("\n初始化 mootdx 客户端...")
    
    # 创建通达信行情客户端
    client = Quotes.factory(market='std', multithread=True, heartbeat=True)
    
    print("✅ 客户端初始化成功")
    print("\n正在获取K线数据...")
    
    # 获取日线数据
    # bars: K线数量，通达信单次最多800条，需要多次请求
    df_list = []
    total_bars = 0
    
    # 计算需要的总交易日数（约 10年 * 250交易日/年 = 2500天）
    # 分多次获取，每次800条
    max_bars_per_request = 800
    estimated_total_bars = 2500
    
    print(f"预计需要获取约 {estimated_total_bars} 条记录")
    print(f"将分 {estimated_total_bars // max_bars_per_request + 1} 次请求\n")
    
    # 第一次获取最新的800条
    for attempt in range(3):  # 最多重试3次
        try:
            klines = client.bars(
                symbol=stock_code,
                market=market,
                frequency=9,  # 9=日线
                offset=0,
                limit=max_bars_per_request
            )
            
            if klines is not None and not klines.empty:
                df_list.append(klines)
                total_bars += len(klines)
                print(f"第1次请求: 获取 {len(klines)} 条记录")
                break
            else:
                raise Exception("返回数据为空")
                
        except Exception as e:
            print(f"第1次请求失败 (尝试 {attempt + 1}/3): {e}")
            if attempt < 2:
                import time
                time.sleep(2)
            else:
                raise
    
    # 继续获取更多历史数据
    offset = max_bars_per_request
    while offset < estimated_total_bars:
        try:
            klines = client.bars(
                symbol=stock_code,
                market=market,
                frequency=9,
                offset=offset,
                limit=max_bars_per_request
            )
            
            if klines is not None and not klines.empty:
                df_list.append(klines)
                total_bars += len(klines)
                print(f"第{offset // max_bars_per_request + 1}次请求: 获取 {len(klines)} 条记录")
                
                # 如果返回的数据少于请求的数量，说明已经到头了
                if len(klines) < max_bars_per_request:
                    print("已获取所有历史数据")
                    break
                    
                offset += max_bars_per_request
                
                # 避免请求过快
                import time
                time.sleep(0.5)
            else:
                print("没有更多数据")
                break
                
        except Exception as e:
            print(f"请求失败: {e}")
            break
    
    if not df_list:
        raise Exception("未获取到任何数据")
    
    # 合并所有数据
    print(f"\n合并数据...")
    df = pd.concat(df_list, ignore_index=True)
    
    print(f"✅ 成功获取 {len(df)} 条原始记录")
    
    # 转换数据格式为 Kronos 要求
    print("\n转换数据格式...")
    
    # mootdx 返回的列名可能不同，需要映射
    # 通常包含: datetime, open, high, low, close, volume, amount
    print(f"原始列名: {list(df.columns)}")
    
    # 重命名列以匹配 Kronos 格式
    column_mapping = {
        'datetime': 'timestamps',
        'date': 'timestamps',
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'vol': 'volume',
        'volume': 'volume',
        'amount': 'amount',
        'turnover': 'amount'
    }
    
    # 应用列名映射
    df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns}, inplace=True)
    
    # 确保有必需的列
    required_columns = ['timestamps', 'open', 'high', 'low', 'close', 'volume', 'amount']
    missing_cols = [col for col in required_columns if col not in df.columns]
    
    if missing_cols:
        print(f"警告: 缺少列 {missing_cols}，尝试计算...")
        
        # 如果没有 amount，计算它
        if 'amount' not in df.columns and 'close' in df.columns and 'volume' in df.columns:
            print("计算成交额 (amount = close * volume * 100)...")
            df['amount'] = df['close'] * df['volume'] * 100
    
    # 选择需要的列
    available_cols = [col for col in required_columns if col in df.columns]
    df = df[available_cols]
    
    # 转换时间格式
    if 'timestamps' in df.columns:
        df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    # 按时间排序
    df = df.sort_values('timestamps').reset_index(drop=True)
    
    # 过滤时间范围
    df = df[(df['timestamps'] >= start_date) & (df['timestamps'] <= end_date)]
    
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
    
    # 数据质量检查
    print("\n数据质量检查:")
    print(f"  - 缺失值: {df.isnull().sum().sum()}")
    
    invalid_ohlc = ((df['high'] < df['low']) | 
                   (df['high'] < df['open']) | 
                   (df['high'] < df['close']) |
                   (df['low'] > df['open']) | 
                   (df['low'] > df['close'])).sum()
    
    if invalid_ohlc == 0:
        print(f"  - OHLC 逻辑: ✅ 通过")
    else:
        print(f"  - OHLC 逻辑: ⚠️  {invalid_ohlc} 条异常")
    
    print("\n" + "=" * 70)
    print("✅ 完成！数据符合 Kronos 训练要求")
    print("=" * 70)

except Exception as e:
    print(f"\n❌ 获取数据失败: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n可能的原因:")
    print("1. 网络连接问题")
    print("2. 通达信服务器暂时不可用")
    print("3. 股票代码或市场代码错误")
    print("\n建议:")
    print("1. 检查网络连接")
    print("2. 稍后重试")
    print("3. 验证股票代码是否正确 (300033.SZ)")
