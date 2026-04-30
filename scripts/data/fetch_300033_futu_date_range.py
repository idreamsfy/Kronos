#!/usr/bin/env python
"""
获取指定日期范围的同花顺 (300033) 5分钟K线数据
并保存到独立的CSV文件
"""

from futu import *
import pandas as pd
import os
from datetime import datetime, timedelta

print("=" * 70)
print("使用 Futu API 获取指定日期范围的 5分钟K线数据")
print("=" * 70)

# ==================== 配置参数 ====================
stock_code = "SZ.300033"  # 股票代码

# 指定日期范围
start_date = "2026-04-27"
end_date = "2026-04-30"

# 输出配置
output_dir = "./data/raw/futu"
output_file = os.path.join(output_dir, f"5min_300033_{start_date}_{end_date}.csv")

# K线类型
kline_type = KLType.K_5M  # 5分钟K线
kline_name = "5分钟"

print(f"\n配置信息:")
print(f"  - 股票代码: {stock_code}")
print(f"  - K线类型: {kline_name}")
print(f"  - 时间范围: {start_date} 至 {end_date}")
print(f"  - 输出文件: {output_file}")

try:
    print("\n初始化 Futu API 客户端...")
    
    # 创建行情上下文对象
    quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    
    print("✅ 客户端初始化成功")
    print(f"\n正在获取 {start_date} 至 {end_date} 的{kline_name}K线数据...")
    print("⚠️  提示: 请耐心等待...\n")
    
    # 获取历史K线
    ret, data, page_req_key = quote_ctx.request_history_kline(
        code=stock_code,
        start=start_date,
        end=end_date,
        ktype=kline_type,        # 5分钟K线
        autype=AuType.QFQ,       # 前复权
        max_count=1000           # 单次最大返回1000条
    )
    
    if ret != RET_OK:
        raise Exception(f"API 请求失败: {data}")
    
    if data is None or data.empty:
        raise Exception("未获取到数据")
    
    print(f"✅ 首次获取 {len(data)} 条记录")
    
    # 检查是否需要分页获取更多数据
    all_data = [data]
    total_count = len(data)
    
    # 4天约 4*48 = 192条5分钟K线，设置合理上限
    max_records = 500
    
    while page_req_key is not None and total_count < max_records:
        print(f"已获取 {total_count} 条，继续获取更多...")
        ret, data, page_req_key = quote_ctx.request_history_kline(
            code=stock_code,
            start=start_date,
            end=end_date,
            ktype=kline_type,
            autype=AuType.QFQ,
            max_count=1000,
            page_req_key=page_req_key
        )
        
        if ret == RET_OK and data is not None and not data.empty:
            all_data.append(data)
            total_count += len(data)
        else:
            break
    
    # 合并所有数据
    if len(all_data) > 1:
        df = pd.concat(all_data, ignore_index=True)
    else:
        df = all_data[0]
    
    print(f"\n总共获取 {len(df)} 条{kline_name}K线记录")
    
    # 转换数据格式为 Kronos 要求
    print("\n转换数据格式...")
    print(f"原始列名: {list(df.columns)}")
    
    # Futu API 返回的列名映射
    column_mapping = {
        'time_key': 'timestamps',
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'volume': 'volume',
        'turnover': 'amount'  # Futu 使用 turnover 表示成交额
    }
    
    # 重命名列
    df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns}, inplace=True)
    
    # 确保有必需的列
    required_columns = ['timestamps', 'open', 'high', 'low', 'close', 'volume', 'amount']
    missing_cols = [col for col in required_columns if col not in df.columns]
    
    if missing_cols:
        raise Exception(f"缺少必需的列: {missing_cols}")
    
    # 选择需要的列
    df = df[required_columns]
    
    # 转换时间格式
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    # 按时间排序
    df = df.sort_values('timestamps').reset_index(drop=True)
    
    # 过滤到指定日期范围（确保精确）
    df = df[(df['timestamps'] >= start_date) & (df['timestamps'] <= end_date + ' 23:59:59')]
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存为 CSV
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ 数据已成功保存至: {output_file}")
    print(f"\n数据统计:")
    print(f"  - 记录数: {len(df)} 条")
    print(f"  - 时间范围: {df['timestamps'].min()} 至 {df['timestamps'].max()}")
    
    # 按天统计
    df['date'] = df['timestamps'].dt.date
    daily_stats = df.groupby('date').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
        'amount': 'sum'
    }).round(2)
    
    print(f"\n📅 每日统计:")
    print("-" * 70)
    for date, row in daily_stats.iterrows():
        weekday = ['一','二','三','四','五','六','日'][pd.Timestamp(date).weekday()]
        change_pct = ((row['close'] - row['open']) / row['open'] * 100) if row['open'] != 0 else 0
        print(f"{date} (星期{weekday}):")
        print(f"  开盘: ¥{row['open']:.2f} | 最高: ¥{row['high']:.2f} | 最低: ¥{row['low']:.2f} | 收盘: ¥{row['close']:.2f}")
        print(f"  涨跌: {change_pct:+.2f}% | 成交量: {int(row['volume']):,} | 成交额: ¥{row['amount']:,.0f}")
        print()
    
    print(f"  - 收盘价范围: ¥{df['close'].min():.2f} - ¥{df['close'].max():.2f}")
    print(f"  - 总成交量: {int(df['volume'].sum()):,}")
    print(f"  - 总成交额: ¥{df['amount'].sum():,.0f}")
    
    print(f"\n前5条数据:")
    print(df[['timestamps', 'open', 'high', 'low', 'close', 'volume']].head())
    
    print(f"\n后5条数据:")
    print(df[['timestamps', 'open', 'high', 'low', 'close', 'volume']].tail())
    
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
    
    # 检查时间间隔
    if len(df) > 1:
        time_diffs = df['timestamps'].diff().dt.total_seconds().dropna()
        avg_interval = time_diffs.mean()
        print(f"  - 平均时间间隔: {avg_interval/60:.1f} 分钟")
        if 270 <= avg_interval <= 330:  # 5分钟 = 300秒，允许±30秒误差
            print(f"  - 时间间隔: ✅ 正常 (5分钟)")
        else:
            print(f"  - 时间间隔: ⚠️  异常 (期望5分钟)")
    
    # 关闭连接
    quote_ctx.close()
    
    print("\n" + "=" * 70)
    print("✅ 完成！数据已保存到独立文件")
    print(f"✅ 文件位置: {output_file}")
    print("=" * 70)

except ConnectionRefusedError:
    print("\n❌ 连接失败: 无法连接到 FutuOpenD")
    print("\n可能的原因:")
    print("1. FutuOpenD 未启动")
    print("2. FutuOpenD 端口不是默认的 11111")
    print("3. 防火墙阻止了连接")
    
    print("\n解决步骤:")
    print("1. 下载并安装 FutuOpenD:")
    print("   https://www.futunn.com/download/openAPI")
    print("2. 启动 FutuOpenD 并登录")
    print("3. 确保监听端口为 11111")
    print("4. 重新运行此脚本")

except Exception as e:
    print(f"\n❌ 获取数据失败: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n建议:")
    print("1. 确保 FutuOpenD 正在运行")
    print("2. 检查股票代码格式是否正确 (SZ.300033)")
    print("3. 检查网络连接")
    print("4. 查看 FutuOpenD 日志获取详细错误信息")
