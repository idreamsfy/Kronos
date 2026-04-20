# coding=utf-8
"""
下载浦发银行(SHSE.600000)历史行情数据并保存为Kronos训练格式的CSV文件
使用AKShare免费API获取数据（无需token）
生成的数据格式完全符合Kronos模型训练要求
"""
import pandas as pd
import datetime
import os
import sys

def download_and_convert_to_kronos_format(years=5, symbol="600000", stock_name="浦发银行"):
    """
    下载股票数据并转换为Kronos训练格式
    
    Args:
        years: 下载年数，默认5年
        symbol: 股票代码，默认600000
        stock_name: 股票名称，默认浦发银行
    
    Returns:
        bool: 是否成功
    """
    print("=" * 80)
    print(f"开始下载{stock_name}({symbol})历史行情数据 (Kronos格式)")
    print("=" * 80)
    
    try:
        import akshare as ak
    except ImportError:
        print("\n❌ 错误: 未安装akshare库")
        print("请运行: pip install akshare")
        return False
    
    # 计算时间范围
    end_date = datetime.datetime.now().strftime('%Y%m%d')
    start_date = (datetime.datetime.now() - datetime.timedelta(days=years*365)).strftime('%Y%m%d')
    
    print(f"\n股票标的: {symbol} ({stock_name})")
    print(f"时间范围: {start_date[:4]}-{start_date[4:6]}-{start_date[6:]} 至 {end_date[:4]}-{end_date[4:6]}-{end_date[6:]}")
    print(f"数据频率: 日线数据")
    print(f"预计年数: {years}年")
    print(f"目标格式: Kronos训练格式 (timestamps, open, close, high, low, volume, amount)")
    
    try:
        # 使用AKShare获取A股历史行情数据
        print("\n正在从东方财富网下载数据...")
        print("(如果失败，请检查网络连接或稍后重试)")
        
        # 添加重试机制
        max_retries = 3
        df_raw = None
        
        for attempt in range(max_retries):
            try:
                df_raw = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"  # 前复权
                )
                break  # 成功则跳出循环
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"   尝试 {attempt + 1}/{max_retries} 失败: {str(e)[:80]}")
                    print(f"   等待5秒后重试...")
                    import time
                    time.sleep(5)
                else:
                    raise  # 最后一次失败，抛出异常
        
        if df_raw is None or len(df_raw) == 0:
            print("\n❌ 错误: 未获取到数据")
            return False
        
        print(f"✅ 成功获取 {len(df_raw)} 条原始记录")
        
        # 数据处理 - 转换为Kronos格式
        print("\n正在处理数据并转换为Kronos格式...")
        
        # Kronos需要的列映射
        kronos_columns = {
            '日期': 'timestamps',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount',
        }
        
        # 只保留Kronos需要的列并重命名
        available_columns = {k: v for k, v in kronos_columns.items() if k in df_raw.columns}
        df_kronos = df_raw.rename(columns=available_columns)
        
        # 确保所有必需的列都存在
        required_columns = ['timestamps', 'open', 'close', 'high', 'low', 'volume', 'amount']
        missing_columns = [col for col in required_columns if col not in df_kronos.columns]
        
        if missing_columns:
            print(f"\n❌ 错误: 缺少必需的列: {missing_columns}")
            return False
        
        # 按时间排序
        df_kronos = df_kronos.sort_values('timestamps').reset_index(drop=True)
        
        # 转换时间格式为Kronos期望的格式 (YYYY/MM/DD 或 YYYY-MM-DD)
        # Kronos示例使用的是 "2019/11/26 9:35" 格式，但日线数据没有时间部分
        df_kronos['timestamps'] = pd.to_datetime(df_kronos['timestamps'])
        # 保持为datetime对象，pandas会自动处理
        
        print(f"✅ 数据转换完成")
        print(f"\nKronos格式数据概览:")
        print(f"  - 总记录数: {len(df_kronos)}")
        print(f"  - 时间范围: {df_kronos['timestamps'].iloc[0]} 至 {df_kronos['timestamps'].iloc[-1]}")
        print(f"  - 列名: {', '.join(df_kronos.columns)}")
        print(f"\n前5条数据:")
        print(df_kronos.head())
        print(f"\n后5条数据:")
        print(df_kronos.tail())
        
        # 数据质量检查
        print(f"\n数据质量检查:")
        print(f"  - 空值数量: {df_kronos.isnull().sum().sum()}")
        print(f"  - 最高价: ¥{df_kronos['high'].max():.2f}")
        print(f"  - 最低价: ¥{df_kronos['low'].min():.2f}")
        print(f"  - 平均收盘价: ¥{df_kronos['close'].mean():.2f}")
        print(f"  - 总成交量: {df_kronos['volume'].sum():,.0f}")
        
        # OHLC逻辑验证
        invalid_ohlc = ((df_kronos['high'] < df_kronos['low']) | 
                       (df_kronos['high'] < df_kronos['open']) |
                       (df_kronos['high'] < df_kronos['close']) |
                       (df_kronos['low'] > df_kronos['open']) |
                       (df_kronos['low'] > df_kronos['close'])).sum()
        
        if invalid_ohlc > 0:
            print(f"  ⚠️  警告: 发现 {invalid_ohlc} 条OHLC逻辑异常记录")
        else:
            print(f"  ✅ OHLC逻辑验证通过")
        
        # 保存为CSV文件
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成符合Kronos命名规范的文件名
        start_str = df_kronos['timestamps'].iloc[0].strftime('%Y-%m-%d')
        end_str = df_kronos['timestamps'].iloc[-1].strftime('%Y-%m-%d')
        filename = f"kronos_SHSE_{symbol}_daily_{start_str}_{end_str}.csv"
        filepath = os.path.join(output_dir, filename)
        
        print(f"\n正在保存Kronos格式数据到: {filepath}")
        
        # 保存时不包含索引，使用UTF-8编码
        df_kronos.to_csv(filepath, index=False, encoding='utf-8')
        
        # 验证文件
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath) / 1024  # KB
            print(f"✅ Kronos格式文件保存成功!")
            print(f"   文件大小: {file_size:.2f} KB")
            print(f"   文件路径: {filepath}")
            
            # 读取验证
            verify_df = pd.read_csv(filepath)
            print(f"   验证记录数: {len(verify_df)}")
            print(f"   验证列名: {', '.join(verify_df.columns)}")
            
            # 确认符合Kronos要求
            kronos_required = ['timestamps', 'open', 'close', 'high', 'low', 'volume', 'amount']
            has_all = all(col in verify_df.columns for col in kronos_required)
            
            if has_all:
                print(f"   ✅ 符合Kronos训练格式要求")
            else:
                missing = [col for col in kronos_required if col not in verify_df.columns]
                print(f"   ❌ 缺少Kronos必需列: {missing}")
            
            return True
        else:
            print(f"❌ 文件保存失败")
            return False
            
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def download_spdb_5min_data():
    """
    下载浦发银行5分钟K线数据（最近1个月）
    """
    print("\n" + "=" * 80)
    print("开始下载浦发银行(SHSE.600000) 5分钟K线数据")
    print("=" * 80)
    
    try:
        import akshare as ak
    except ImportError:
        print("\n❌ 错误: 未安装akshare库")
        return False
    
    symbol = "600000"
    
    print(f"\n股票标的: {symbol} (浦发银行)")
    print(f"数据频率: 5分钟K线")
    print(f"注意: 5分钟数据量较大，可能需要较长时间")
    
    try:
        # 获取5分钟K线数据
        print("\n正在从新浪财经下载5分钟数据...")
        df = ak.stock_zh_a_minute(
            symbol=symbol,
            period='5',
            adjust='qfq'
        )
        
        if df is None or len(df) == 0:
            print("\n❌ 错误: 未获取到5分钟数据")
            return False
        
        print(f"✅ 成功获取 {len(df)} 条记录")
        
        # 数据处理
        column_mapping = {
            'day': 'datetime',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume',
        }
        
        available_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df.rename(columns=available_columns)
        
        df.insert(0, 'symbol', f'SHSE.{symbol}')
        df.insert(1, 'name', '浦发银行')
        
        df = df.sort_values('datetime').reset_index(drop=True)
        
        print(f"✅ 数据处理完成")
        print(f"\n数据概览:")
        print(f"  - 总记录数: {len(df)}")
        if 'datetime' in df.columns:
            print(f"  - 时间范围: {df['datetime'].iloc[0]} 至 {df['datetime'].iloc[-1]}")
        
        # 保存为CSV
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"SHSE_{symbol}_浦发电行_5min.csv"
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
    print("浦发银行历史行情数据下载工具 (AKShare - Kronos格式)")
    print("=" * 80)
    print("\n说明:")
    print("- 使用AKShare免费API，无需注册或token")
    print("- 数据来源: 东方财富网、新浪财经等")
    print("- 输出格式: Kronos训练格式 (timestamps, open, close, high, low, volume, amount)")
    print("- 文件命名: kronos_SHSE_600000_daily_YYYY-MM-DD_YYYY-MM-DD.csv")
    print("=" * 80)
    
    # 下载日线数据并转换为Kronos格式（5年）
    success = download_and_convert_to_kronos_format(years=5)
    
    if success:
        print("\n" + "=" * 80)
        print("✅ 数据下载完成！")
        print("=" * 80)
        print("\n提示:")
        print("1. 数据已保存到 data/ 目录")
        print("2. 文件格式符合Kronos训练要求")
        print("3. 可直接用于Kronos模型训练")
        print("4. 示例代码:")
        print("   import pandas as pd")
        print("   df = pd.read_csv('data/kronos_SHSE_600000_daily_*.csv')")
        print("   print(df.head())")
        print("   print(df.columns)")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ 数据下载失败")
        print("=" * 80)
