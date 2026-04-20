"""
使用 AkShare 获取 A 股同花顺历史数据并生成符合 Kronos 训练要求的 CSV 文件

Kronos 数据格式要求:
- timestamps: 时间戳 (YYYY-MM-DD HH:MM:SS)
- open: 开盘价
- high: 最高价
- low: 最低价
- close: 收盘价
- volume: 成交量
- amount: 成交额

支持的数据频率:
- daily: 日线数据
- weekly: 周线数据
- monthly: 月线数据
"""

import akshare as ak
import pandas as pd
import os
from datetime import datetime
import time


def get_stock_list():
    """
    获取 A 股股票列表
    
    Returns:
        DataFrame: 包含股票代码和名称的 DataFrame
    """
    print("正在获取 A 股股票列表...")
    try:
        # 获取沪深 A 股列表
        stock_info = ak.stock_info_a_code_name()
        print(f"成功获取 {len(stock_info)} 只股票")
        return stock_info
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return None


def fetch_stock_data_daily(symbol, start_date="20150101", end_date=None, max_retries=3):
    """
    获取单只股票的日线数据
    
    Args:
        symbol: 股票代码 (如: 600977)
        start_date: 开始日期 (格式: YYYYMMDD)
        end_date: 结束日期 (格式: YYYYMMDD)，默认为今天
        max_retries: 最大重试次数
    
    Returns:
        DataFrame: 符合 Kronos 格式的数据
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")
    
    for attempt in range(max_retries):
        try:
            print(f"正在获取 {symbol} 的数据 ({start_date} 至 {end_date})... [尝试 {attempt + 1}/{max_retries}]")
            
            # 使用 AkShare 获取个股历史行情
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"  # 前复权
            )
            
            if df.empty:
                print(f"警告: {symbol} 没有数据")
                return None
            
            # 转换列名以匹配 Kronos 格式
            df.rename(columns={
                '日期': 'timestamps',
                '开盘': 'open',
                '最高': 'high',
                '最低': 'low',
                '收盘': 'close',
                '成交量': 'volume',
                '成交额': 'amount'
            }, inplace=True)
            
            # 选择需要的列
            df = df[['timestamps', 'open', 'high', 'low', 'close', 'volume', 'amount']]
            
            # 转换时间格式
            df['timestamps'] = pd.to_datetime(df['timestamps'])
            
            # 按时间排序
            df = df.sort_values('timestamps').reset_index(drop=True)
            
            print(f"成功获取 {symbol}: {len(df)} 条记录")
            return df
            
        except Exception as e:
            print(f"获取 {symbol} 数据失败 (尝试 {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                print(f"等待 2 秒后重试...")
                time.sleep(2)
            else:
                print(f"达到最大重试次数，放弃获取 {symbol}")
                return None


def fetch_stock_data_weekly(symbol, start_date="20150101", end_date=None):
    """
    获取单只股票的周线数据
    """
    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")
    
    try:
        print(f"正在获取 {symbol} 的周线数据...")
        
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="weekly",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )
        
        if df.empty:
            return None
        
        df.rename(columns={
            '日期': 'timestamps',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume',
            '成交额': 'amount'
        }, inplace=True)
        
        df = df[['timestamps', 'open', 'high', 'low', 'close', 'volume', 'amount']]
        df['timestamps'] = pd.to_datetime(df['timestamps'])
        df = df.sort_values('timestamps').reset_index(drop=True)
        
        print(f"成功获取 {symbol} 周线: {len(df)} 条记录")
        return df
        
    except Exception as e:
        print(f"获取 {symbol} 周线数据失败: {e}")
        return None


def save_to_csv(df, output_path, symbol, frequency="daily"):
    """
    保存数据为 CSV 文件
    
    Args:
        df: DataFrame
        output_path: 输出目录
        symbol: 股票代码
        frequency: 数据频率 (daily/weekly/monthly)
    """
    os.makedirs(output_path, exist_ok=True)
    
    # 生成文件名
    filename = f"{frequency}_{symbol}.csv"
    filepath = os.path.join(output_path, filename)
    
    # 保存 CSV
    df.to_csv(filepath, index=False)
    print(f"✓ 数据已保存至: {filepath}")
    
    return filepath


def batch_fetch_stocks(symbols, output_dir="./akshare_data", frequency="daily", 
                       start_date="20150101", max_stocks=None):
    """
    批量获取多只股票数据
    
    Args:
        symbols: 股票代码列表
        output_dir: 输出目录
        frequency: 数据频率 (daily/weekly/monthly)
        start_date: 开始日期
        max_stocks: 最大处理股票数量 (None 表示全部)
    
    Returns:
        list: 成功处理的文件路径列表
    """
    success_files = []
    failed_stocks = []
    
    if max_stocks:
        symbols = symbols[:max_stocks]
    
    total = len(symbols)
    print(f"\n开始批量获取 {total} 只股票的{frequency}数据...")
    print("=" * 70)
    
    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{total}] 处理股票: {symbol}")
        
        # 根据频率选择获取函数
        if frequency == "daily":
            df = fetch_stock_data_daily(symbol, start_date)
        elif frequency == "weekly":
            df = fetch_stock_data_weekly(symbol, start_date)
        else:
            print(f"不支持的频率: {frequency}")
            continue
        
        if df is not None and not df.empty:
            filepath = save_to_csv(df, output_dir, symbol, frequency)
            success_files.append(filepath)
        else:
            failed_stocks.append(symbol)
        
        # 避免请求过快被封禁
        if i < total:
            time.sleep(0.5)
    
    # 打印总结
    print("\n" + "=" * 70)
    print(f"批量获取完成!")
    print(f"✓ 成功: {len(success_files)} 只股票")
    print(f"✗ 失败: {len(failed_stocks)} 只股票")
    
    if failed_stocks:
        print(f"\n失败的股票: {failed_stocks[:10]}")  # 只显示前10个
    
    return success_files


def main():
    """
    主函数 - 示例用法
    """
    print("=" * 70)
    print("AkShare A 股数据获取工具 - Kronos 数据格式")
    print("=" * 70)
    
    # ==================== 配置参数 ====================
    OUTPUT_DIR = "./akshare_data"  # 输出目录
    FREQUENCY = "daily"  # 数据频率: daily, weekly, monthly
    START_DATE = "20150101"  # 开始日期 (10年前)
    MAX_STOCKS = None  # 最大处理股票数量 (None 表示全部)
    
    # 目标股票：300033 东方财富
    SAMPLE_SYMBOLS = [
        "300033",  # 东方财富
    ]
    
    # ==================== 执行流程 ====================
    
    # 方案 1: 获取指定股票列表
    print("\n【方案 1】获取指定股票列表的数据")
    print("-" * 70)
    success_files = batch_fetch_stocks(
        symbols=SAMPLE_SYMBOLS,
        output_dir=OUTPUT_DIR,
        frequency=FREQUENCY,
        start_date=START_DATE,
        max_stocks=MAX_STOCKS
    )
    
    # 方案 2: 获取所有 A 股 (取消注释以启用)
    # print("\n【方案 2】获取所有 A 股数据 (这可能需要很长时间)")
    # print("-" * 70)
    # stock_list = get_stock_list()
    # if stock_list is not None:
    #     all_symbols = stock_list['code'].tolist()
    #     success_files = batch_fetch_stocks(
    #         symbols=all_symbols,
    #         output_dir=OUTPUT_DIR,
    #         frequency=FREQUENCY,
    #         start_date=START_DATE,
    #         max_stocks=None  # 设置为具体数字限制数量
    #     )
    
    # ==================== 结果展示 ====================
    print("\n" + "=" * 70)
    print("数据获取完成!")
    print(f"输出目录: {os.path.abspath(OUTPUT_DIR)}")
    print(f"成功文件数: {len(success_files)}")
    
    if success_files:
        print("\n生成的文件:")
        for f in success_files[:10]:  # 只显示前10个
            print(f"  - {f}")
        if len(success_files) > 10:
            print(f"  ... 还有 {len(success_files) - 10} 个文件")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
