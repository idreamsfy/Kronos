# coding=utf-8
"""
批量下载A股科创板(STAR Market)所有股票历史行情数据
从star_market_stocks_list_*.csv读取股票代码
使用掘金量化API获取过去5年数据
保存为符合Kronos训练要求的CSV格式

科创板特点:
- 股票代码: 688xxx
- 上市时间: 2019年7月后
- 涨跌幅限制: 20%
- 交易所: 上海证券交易所 (SHSE)
"""
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *
import pandas as pd
import datetime
import os
import time
import glob

# 配置掘金量化Token
GM_TOKEN = 'cabb19a30fc311ec977252560acd7b8ecabb19a4'

# 设置Token
set_token(GM_TOKEN)


def load_star_stocks_list(csv_file=None):
    """
    加载科创板股票列表
    
    Args:
        csv_file: CSV文件路径，默认自动查找最新的文件
    
    Returns:
        DataFrame: 科创板股票列表
    """
    if csv_file is None:
        # 自动查找最新的科创板股票列表文件
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'metadata')
        pattern = os.path.join(data_dir, 'star_market_stocks_list_*.csv')
        files = glob.glob(pattern)
        
        if not files:
            print("❌ 错误: 未找到科创板股票列表文件")
            print(f"   请先运行: python scripts/data/batch_download_star_market.py 生成列表")
            return None
        
        # 选择最新的文件
        csv_file = max(files, key=os.path.getctime)
    
    print(f"📂 读取科创板股票列表: {csv_file}")
    
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ 成功加载 {len(df)} 只科创板股票")
        return df
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return None


def get_star_market_stocks():
    """
    获取所有科创板股票列表（备用方法）
    如果CSV文件不存在，则生成科创板代码列表
    
    Returns:
        DataFrame: 科创板股票列表，包含代码和名称
    """
    print("📊 生成科创板股票列表...")
    
    try:
        # 科创板代码范围: 688000-688999
        # 目前约有570+只科创板股票
        codes = [f"688{i:03d}" for i in range(0, 600)]
        
        star_stocks = pd.DataFrame({
            'code': codes,
            'name': [f"科创板{code}" for code in codes]
        })
        
        print(f"✅ 生成 {len(star_stocks)} 只科创板股票代码")
        print(f"⚠️  注意: 部分代码可能尚未上市或已退市")
        
        return star_stocks
        
    except Exception as e:
        print(f"❌ 生成股票列表失败: {e}")
        return None


def save_stock_list(stocks_df, output_dir=None):
    """
    保存股票列表到CSV文件
    
    Args:
        stocks_df: 股票DataFrame
        output_dir: 输出目录
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'metadata')
    
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d')
    filename = f"star_market_stocks_list_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    stocks_df.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f"💾 股票列表已保存: {filepath}")
    
    return filepath


def download_single_stock(symbol, stock_name, years=5, output_dir=None):
    """
    下载单只科创板股票的历史数据并保存为Kronos格式
    
    Args:
        symbol: 股票代码（如 SHSE.688001）
        stock_name: 股票名称
        years: 下载年数，默认5年
        output_dir: 输出目录
    
    Returns:
        bool: 是否成功
    """
    try:
        # 计算时间范围
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=years*365)
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # 获取历史行情数据（掘金量化API）
        history_data = history(
            symbol=symbol,
            frequency='1d',
            start_time=start_date_str,
            end_time=end_date_str,
            fill_missing='last',
            df=True
        )
        
        if history_data is None or len(history_data) == 0:
            print(f"   ⚠️  未获取到数据")
            return False
        
        # 数据处理 - 转换为Kronos格式
        kronos_columns = {
            'eob': 'timestamps',
            'open': 'open',
            'close': 'close',
            'high': 'high',
            'low': 'low',
            'volume': 'volume',
            'amount': 'amount',
        }
        
        # 只保留Kronos需要的列
        available_columns = {k: v for k, v in kronos_columns.items() if k in history_data.columns}
        df_kronos = history_data.rename(columns=available_columns)
        
        # 确保所有必需列都存在
        required_columns = ['timestamps', 'open', 'close', 'high', 'low', 'volume', 'amount']
        missing_columns = [col for col in required_columns if col not in df_kronos.columns]
        
        if missing_columns:
            print(f"   ⚠️  缺少列: {missing_columns}")
            return False
        
        # 按时间排序
        df_kronos = df_kronos.sort_values('timestamps').reset_index(drop=True)
        
        # 转换时间格式
        df_kronos['timestamps'] = pd.to_datetime(df_kronos['timestamps'])
        
        # 生成文件名
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'processed')
        
        os.makedirs(output_dir, exist_ok=True)
        
        start_str = df_kronos['timestamps'].iloc[0].strftime('%Y-%m-%d')
        end_str = df_kronos['timestamps'].iloc[-1].strftime('%Y-%m-%d')
        
        # 提取股票代码（去掉交易所前缀）
        code = symbol.split('.')[1] if '.' in symbol else symbol
        exchange = symbol.split('.')[0] if '.' in symbol else 'SHSE'
        
        filename = f"kronos_{exchange}_{code}_daily_{start_str}_{end_str}.csv"
        filepath = os.path.join(output_dir, filename)
        
        # 保存为CSV
        df_kronos.to_csv(filepath, index=False, encoding='utf-8')
        
        # 验证文件
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath) / 1024  # KB
            print(f"   ✅ 保存成功: {len(df_kronos)}条记录, {file_size:.1f}KB")
            return True
        else:
            print(f"   ❌ 保存失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 错误: {str(e)[:100]}")
        return False


def batch_download_star_stocks(years=5, delay=2, max_stocks=None):
    """
    批量下载所有科创板股票数据
    
    Args:
        years: 下载年数，默认5年
        delay: 每次请求间隔秒数，避免API限流
        max_stocks: 最大下载数量，None表示全部
    """
    print("=" * 80)
    print("批量下载A股科创板股票历史数据 (Kronos格式)")
    print("=" * 80)
    print(f"\n配置信息:")
    print(f"  - 下载年数: {years}年")
    print(f"  - 请求间隔: {delay}秒")
    print(f"  - 数据格式: Kronos训练格式")
    print(f"  - 数据来源: 掘金量化API")
    print(f"  - Token: {GM_TOKEN[:20]}...")
    if max_stocks:
        print(f"  - 下载数量: 最多{max_stocks}只")
    print("=" * 80)
    
    # 加载科创板股票列表
    star_stocks_df = load_star_stocks_list()
    
    # 如果CSV文件不存在，则生成代码列表
    if star_stocks_df is None:
        print("\n⚠️  未找到股票列表文件，尝试生成...")
        star_stocks_df = get_star_market_stocks()
    
    if star_stocks_df is None or len(star_stocks_df) == 0:
        print("\n❌ 无法继续：未获取到科创板股票列表")
        return
    
    # 限制下载数量（用于测试）
    if max_stocks and max_stocks < len(star_stocks_df):
        print(f"\n⚠️  限制下载数量为 {max_stocks} 只（测试模式）")
        star_stocks_df = star_stocks_df.head(max_stocks)
    
    # 保存股票列表
    list_file = save_stock_list(star_stocks_df)
    
    # 统计信息
    total = len(star_stocks_df)
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    print(f"\n开始批量下载 ({total}只股票)...")
    print("-" * 80)
    
    # 输出目录
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'processed')
    
    for idx, row in star_stocks_df.iterrows():
        code = str(row.get('code', '')).zfill(6)  # 确保是字符串并补齐6位
        name = row.get('name', '未知')
        
        # 添加交易所前缀
        symbol = f'SHSE.{code}'
        
        print(f"\n[{idx+1}/{total}] {name} ({symbol})")
        
        # 检查文件是否已存在
        code_only = symbol.split('.')[1] if '.' in symbol else symbol
        exchange = symbol.split('.')[0] if '.' in symbol else 'SHSE'
        
        existing_files = glob.glob(os.path.join(output_dir, f"kronos_{exchange}_{code_only}_daily_*.csv"))
        if existing_files:
            print(f"   ⏭️  文件已存在，跳过")
            skipped_count += 1
            continue
        
        # 下载数据
        success = download_single_stock(symbol, name, years=years, output_dir=output_dir)
        
        if success:
            success_count += 1
        else:
            failed_count += 1
        
        # 延迟，避免API限流
        if idx < total - 1:  # 最后一个不需要延迟
            time.sleep(delay)
    
    # 打印总结
    print("\n" + "=" * 80)
    print("批量下载完成！")
    print("=" * 80)
    print(f"\n统计信息:")
    print(f"  - 总计: {total} 只")
    print(f"  - 成功: {success_count} 只 ✅")
    print(f"  - 失败: {failed_count} 只 ❌")
    print(f"  - 跳过: {skipped_count} 只 ⏭️")
    
    if total > 0:
        print(f"\n成功率: {success_count/total*100:.1f}%")
    
    print(f"\n文件保存在: {output_dir}")
    print(f"股票列表: {list_file}")
    print("=" * 80)
    
    # 列出已生成的文件
    kronos_files = glob.glob(os.path.join(output_dir, 'kronos_SHSE_688*_daily_*.csv'))
    if kronos_files:
        print(f"\n已生成的Kronos格式文件 ({len(kronos_files)}个):")
        for f in sorted(kronos_files)[:20]:  # 只显示前20个
            filename = os.path.basename(f)
            size_kb = os.path.getsize(f) / 1024
            print(f"  - {filename:<60} {size_kb:>8.1f} KB")
        
        if len(kronos_files) > 20:
            print(f"  ... 还有 {len(kronos_files) - 20} 个文件")
    
    print("\n" + "=" * 80)


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("A股科创板股票批量数据下载工具")
    print("=" * 80)
    print(f"运行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n说明:")
    print("  - 科创板股票代码: 688xxx")
    print("  - 默认下载过去5年数据")
    print("  - 使用掘金量化API (需要Token)")
    print("=" * 80)
    
    try:
        # 批量下载（5年数据，每次请求间隔2秒）
        # 可以通过max_stocks参数限制下载数量进行测试
        batch_download_star_stocks(years=5, delay=2, max_stocks=None)
        
        print("\n✅ 任务完成！")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
