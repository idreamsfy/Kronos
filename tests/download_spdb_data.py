# coding=utf-8
"""
下载浦发银行(SHSE.600000)历史行情数据并保存为CSV文件
使用掘金量化API获取数据
"""
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
import pandas as pd
import datetime
import os

# 配置掘金量化Token
GM_TOKEN = 'cabb19a30fc311ec977252560acd7b8ecabb19a4'

# 设置Token
set_token(GM_TOKEN)

def download_stock_data():
    """
    下载浦发银行5年历史行情数据
    """
    print("=" * 80)
    print("开始下载浦发银行(SHSE.600000)历史行情数据")
    print("=" * 80)
    
    # 设置股票代码
    symbol = 'SHSE.600000'
    
    # 计算时间范围：5年前到今天
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=5*365)
    
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    print(f"\n股票标的: {symbol}")
    print(f"时间范围: {start_date_str} 至 {end_date_str}")
    print(f"数据频率: 日线数据 (1d)")
    
    try:
        # 获取历史行情数据
        print("\n正在从掘金平台下载数据...")
        history_data = history(
            symbol=symbol,
            frequency='1d',
            start_time=start_date_str,
            end_time=end_date_str,
            fill_missing='last',
            df=True  # 返回DataFrame格式
        )
        
        if history_data is None or len(history_data) == 0:
            print("\n❌ 错误: 未获取到数据，请检查网络连接或token配置")
            return False
        
        print(f"✅ 成功获取 {len(history_data)} 条记录")
        
        # 数据处理
        print("\n正在处理数据...")
        
        # 重命名列名为更友好的名称
        column_mapping = {
            'eob': 'date',           # 结束时间
            'bob': 'trade_date',     # 开始时间
            'open': 'open',          # 开盘价
            'high': 'high',          # 最高价
            'low': 'low',            # 最低价
            'close': 'close',        # 收盘价
            'volume': 'volume',      # 成交量
            'amount': 'amount',      # 成交额
            'pre_close': 'pre_close', # 前收盘价
        }
        
        # 只保留需要的列
        available_columns = [col for col in column_mapping.keys() if col in history_data.columns]
        df = history_data[available_columns].copy()
        df.rename(columns=column_mapping, inplace=True)
        
        # 格式化日期
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        if 'trade_date' in df.columns:
            df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y-%m-%d')
        
        # 添加股票代码列
        df.insert(0, 'symbol', symbol)
        
        # 按日期排序
        df = df.sort_values('date').reset_index(drop=True)
        
        print(f"✅ 数据处理完成")
        print(f"\n数据概览:")
        print(f"  - 总记录数: {len(df)}")
        print(f"  - 日期范围: {df['date'].iloc[0]} 至 {df['date'].iloc[-1]}")
        print(f"  - 列名: {', '.join(df.columns)}")
        print(f"\n前5条数据:")
        print(df.head())
        print(f"\n后5条数据:")
        print(df.tail())
        
        # 保存为CSV文件
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{symbol.replace('.', '_')}_daily_{start_date_str}_{end_date_str}.csv"
        filepath = os.path.join(output_dir, filename)
        
        print(f"\n正在保存数据到: {filepath}")
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        # 验证文件
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
            print(f"✅ 文件保存成功!")
            print(f"   文件大小: {file_size:.2f} MB")
            print(f"   文件路径: {filepath}")
            
            # 读取验证
            verify_df = pd.read_csv(filepath)
            print(f"   验证记录数: {len(verify_df)}")
            
            return True
        else:
            print(f"❌ 文件保存失败")
            return False
            
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def download_5min_data():
    """
    下载浦发银行5分钟K线数据（最近1个月）
    """
    print("\n" + "=" * 80)
    print("开始下载浦发银行(SHSE.600000) 5分钟K线数据")
    print("=" * 80)
    
    symbol = 'SHSE.600000'
    
    # 5分钟数据量大，只下载最近1个月
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=30)
    
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"\n股票标的: {symbol}")
    print(f"时间范围: {start_date_str} 至 {end_date_str}")
    print(f"数据频率: 5分钟 (5min)")
    
    try:
        print("\n正在从掘金平台下载数据...")
        history_data = history(
            symbol=symbol,
            frequency='5min',
            start_time=start_date_str,
            end_time=end_date_str,
            fill_missing='last',
            df=True
        )
        
        if history_data is None or len(history_data) == 0:
            print("\n❌ 错误: 未获取到5分钟数据")
            return False
        
        print(f"✅ 成功获取 {len(history_data)} 条记录")
        
        # 数据处理
        column_mapping = {
            'eob': 'datetime',
            'bob': 'trade_time',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume',
            'amount': 'amount',
        }
        
        available_columns = [col for col in column_mapping.keys() if col in history_data.columns]
        df = history_data[available_columns].copy()
        df.rename(columns=column_mapping, inplace=True)
        
        # 格式化时间
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d %H:%M:%S')
        if 'trade_time' in df.columns:
            df['trade_time'] = pd.to_datetime(df['trade_time']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        df.insert(0, 'symbol', symbol)
        df = df.sort_values('datetime').reset_index(drop=True)
        
        print(f"✅ 数据处理完成")
        print(f"\n数据概览:")
        print(f"  - 总记录数: {len(df)}")
        print(f"  - 时间范围: {df['datetime'].iloc[0]} 至 {df['datetime'].iloc[-1]}")
        
        # 保存为CSV
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{symbol.replace('.', '_')}_5min_recent.csv"
        filepath = os.path.join(output_dir, filename)
        
        print(f"\n正在保存数据到: {filepath}")
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath) / (1024 * 1024)
            print(f"✅ 5分钟数据保存成功!")
            print(f"   文件大小: {file_size:.2f} MB")
            print(f"   文件路径: {filepath}")
            return True
        else:
            print(f"❌ 5分钟数据保存失败")
            return False
            
    except Exception as e:
        print(f"\n❌ 下载5分钟数据时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("浦发银行历史行情数据下载工具")
    print("=" * 80)
    
    # 下载日线数据（5年）
    daily_success = download_stock_data()
    
    # 询问是否下载5分钟数据
    if daily_success:
        print("\n" + "-" * 80)
        choice = input("\n是否同时下载最近1个月的5分钟K线数据？(y/n，默认n): ").strip().lower()
        if choice == 'y':
            download_5min_data()
    
    print("\n" + "=" * 80)
    print("数据下载完成！")
    print("=" * 80)
    print("\n提示:")
    print("1. 数据已保存到 data/ 目录")
    print("2. 可以使用 pandas 读取CSV文件进行分析")
    print("3. 示例代码:")
    print("   import pandas as pd")
    print("   df = pd.read_csv('data/SHSE_600000_daily_*.csv')")
    print("   print(df.head())")
    print("=" * 80)
