# coding=utf-8
"""
获取所有A股银行板块的股票代码
使用AKShare免费API获取数据
保存为CSV文件供后续使用
"""
import pandas as pd
import datetime
import os


def get_all_bank_stocks():
    """
    获取所有A股银行板块的股票代码和信息
    
    Returns:
        DataFrame: 包含银行股票信息的DataFrame
    """
    print("=" * 80)
    print("获取A股银行板块股票列表")
    print("=" * 80)
    
    try:
        import akshare as ak
    except ImportError:
        print("\n❌ 错误: 未安装akshare库")
        print("请运行: pip install akshare")
        return None
    
    try:
        # 方法1: 获取银行板块成分股
        print("\n正在从东方财富网获取银行板块成分股...")
        print("(如果失败，请检查网络连接或稍后重试)")
        
        # 添加重试机制
        max_retries = 3
        industry_df = None
        
        for attempt in range(max_retries):
            try:
                import time
                if attempt > 0:
                    print(f"   重试 {attempt}/{max_retries}...")
                    time.sleep(3)
                
                # 获取行业板块信息
                industry_df = ak.stock_board_industry_name_em()
                break  # 成功则跳出循环
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"   尝试 {attempt + 1}/{max_retries} 失败: {str(e)[:80]}")
                else:
                    raise  # 最后一次失败，抛出异常
        
        # 查找银行板块
        bank_board = industry_df[industry_df['板块名称'].str.contains('银行', na=False)]
        
        if len(bank_board) == 0:
            print("❌ 未找到银行板块")
            return None
        
        print(f"✅ 找到 {len(bank_board)} 个银行相关板块:")
        for idx, row in bank_board.iterrows():
            print(f"   - {row['板块名称']}")
        
        # 获取第一个银行板块的成分股（通常是"银行"板块）
        bank_board_name = bank_board.iloc[0]['板块名称']
        print(f"\n正在获取 [{bank_board_name}] 的成分股...")
        
        # 获取板块成分股
        bank_stocks_df = ak.stock_board_industry_cons_em(symbol=bank_board_name)
        
        if bank_stocks_df is None or len(bank_stocks_df) == 0:
            print("❌ 未获取到银行板块成分股")
            return None
        
        print(f"✅ 成功获取 {len(bank_stocks_df)} 只银行股票")
        
        # 数据处理
        print("\n正在处理数据...")
        
        # 重命名列
        column_mapping = {
            '代码': 'symbol',
            '名称': 'name',
            '最新价': 'price',
            '涨跌幅': 'change_pct',
            '涨跌额': 'change_amount',
            '成交量': 'volume',
            '成交额': 'amount',
            '振幅': 'amplitude',
            '最高': 'high',
            '最低': 'low',
            '今开': 'open',
            '昨收': 'prev_close',
            '量比': 'volume_ratio',
            '换手率': 'turnover_rate',
            '市盈率-动态': 'pe_ratio',
            '市净率': 'pb_ratio',
        }
        
        # 只保留存在的列
        available_columns = {k: v for k, v in column_mapping.items() if k in bank_stocks_df.columns}
        bank_stocks_df = bank_stocks_df.rename(columns=available_columns)
        
        # 添加板块信息
        bank_stocks_df.insert(0, 'board_name', bank_board_name)
        bank_stocks_df.insert(1, 'industry', '银行')
        
        # 添加交易所前缀
        def add_exchange_prefix(code):
            """根据股票代码添加交易所前缀"""
            code = str(code).zfill(6)
            if code.startswith('6'):
                return f'SHSE.{code}'
            elif code.startswith('0') or code.startswith('3'):
                return f'SZSE.{code}'
            else:
                return f'UNKNOWN.{code}'
        
        bank_stocks_df['full_symbol'] = bank_stocks_df['symbol'].apply(add_exchange_prefix)
        
        # 重新排列列顺序
        priority_columns = ['full_symbol', 'symbol', 'name', 'board_name', 'industry', 'price']
        other_columns = [col for col in bank_stocks_df.columns if col not in priority_columns]
        bank_stocks_df = bank_stocks_df[priority_columns + other_columns]
        
        # 按股票代码排序
        bank_stocks_df = bank_stocks_df.sort_values('symbol').reset_index(drop=True)
        
        print(f"✅ 数据处理完成")
        print(f"\n数据概览:")
        print(f"  - 股票数量: {len(bank_stocks_df)}")
        print(f"  - 板块名称: {bank_board_name}")
        print(f"  - 列名: {', '.join(bank_stocks_df.columns)}")
        print(f"\n前10只银行股票:")
        print(bank_stocks_df[['full_symbol', 'symbol', 'name', 'price']].head(10).to_string(index=False))
        
        return bank_stocks_df
        
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def get_bank_stocks_local():
    """
    本地备用方法：使用已知的银行股票代码列表
    当网络API失败时使用
    """
    print("\n使用本地备用方法：已知银行股票列表")
    
    # A股主要银行股票列表（截至2026年）
    bank_stocks_data = [
        # 大型商业银行
        ('601398', '工商银行', 'SHSE'),
        ('601939', '建设银行', 'SHSE'),
        ('601288', '农业银行', 'SHSE'),
        ('601988', '中国银行', 'SHSE'),
        ('601328', '交通银行', 'SHSE'),
        ('601658', '邮储银行', 'SHSE'),
        
        # 股份制商业银行
        ('600036', '招商银行', 'SHSE'),
        ('601166', '兴业银行', 'SHSE'),
        ('600000', '浦发银行', 'SHSE'),
        ('600016', '民生银行', 'SHSE'),
        ('600015', '华夏银行', 'SHSE'),
        ('601818', '光大银行', 'SHSE'),
        ('601998', '中信银行', 'SHSE'),
        ('601997', '贵阳银行', 'SHSE'),
        ('601169', '北京银行', 'SHSE'),
        ('601009', '南京银行', 'SHSE'),
        ('600926', '杭州银行', 'SHSE'),
        ('601128', '常熟银行', 'SHSE'),
        ('601838', '成都银行', 'SHSE'),
        ('601577', '长沙银行', 'SHSE'),
        ('601528', '瑞丰银行', 'SHSE'),
        ('601187', '厦门银行', 'SHSE'),
        ('601963', '重庆银行', 'SHSE'),
        ('601860', '紫金银行', 'SHSE'),
        ('601162', '天风证券', 'SHSE'),  # 注：有些可能不是纯银行
        
        # 深圳交易所银行
        ('000001', '平安银行', 'SZSE'),
        ('002142', '宁波银行', 'SZSE'),
        ('002807', '江阴银行', 'SZSE'),
        ('002839', '张家港行', 'SZSE'),
        ('002936', '郑州银行', 'SZSE'),
        ('002948', '青岛银行', 'SZSE'),
        ('002958', '青农商行', 'SZSE'),
        ('002966', '苏州银行', 'SZSE'),
        ('300059', '东方财富', 'SZSE'),  # 互联网金融
    ]
    
    # 创建DataFrame
    data = []
    for code, name, exchange in bank_stocks_data:
        full_symbol = f'{exchange}.{code}'
        data.append({
            'full_symbol': full_symbol,
            'symbol': code,
            'name': name,
            'industry': '银行',
            'board_name': '银行板块',
        })
    
    df = pd.DataFrame(data)
    
    print(f"✅ 加载 {len(df)} 只银行股票（本地数据）")
    print(f"\n前10只银行股票:")
    print(df[['full_symbol', 'symbol', 'name']].head(10).to_string(index=False))
    
    return df


def get_bank_stocks_alternative():
    """
    备用方法：通过股票列表筛选银行股
    """
    print("\n尝试备用方法：从全部A股中筛选银行股...")
    
    try:
        import akshare as ak
        
        # 获取所有A股列表
        print("正在获取所有A股列表...")
        all_stocks_df = ak.stock_zh_a_spot_em()
        
        if all_stocks_df is None or len(all_stocks_df) == 0:
            print("❌ 未获取到A股列表")
            return None
        
        print(f"✅ 获取到 {len(all_stocks_df)} 只A股")
        
        # 筛选银行股（通过名称包含"银行"）
        bank_mask = all_stocks_df['名称'].str.contains('银行', na=False)
        bank_stocks_df = all_stocks_df[bank_mask].copy()
        
        print(f"✅ 筛选出 {len(bank_stocks_df)} 只银行股票")
        
        if len(bank_stocks_df) == 0:
            print("❌ 未找到银行股票")
            return None
        
        # 重命名列
        column_mapping = {
            '代码': 'symbol',
            '名称': 'name',
            '最新价': 'price',
        }
        
        available_columns = {k: v for k, v in column_mapping.items() if k in bank_stocks_df.columns}
        bank_stocks_df = bank_stocks_df.rename(columns=available_columns)
        
        # 添加交易所前缀
        def add_exchange_prefix(code):
            code = str(code).zfill(6)
            if code.startswith('6'):
                return f'SHSE.{code}'
            elif code.startswith('0') or code.startswith('3'):
                return f'SZSE.{code}'
            else:
                return f'UNKNOWN.{code}'
        
        bank_stocks_df['full_symbol'] = bank_stocks_df['symbol'].apply(add_exchange_prefix)
        bank_stocks_df.insert(0, 'industry', '银行')
        
        # 选择主要列
        main_columns = ['full_symbol', 'symbol', 'name', 'industry', 'price']
        available_main_cols = [col for col in main_columns if col in bank_stocks_df.columns]
        bank_stocks_df = bank_stocks_df[available_main_cols]
        
        # 排序
        bank_stocks_df = bank_stocks_df.sort_values('symbol').reset_index(drop=True)
        
        print(f"\n前10只银行股票:")
        print(bank_stocks_df.head(10).to_string(index=False))
        
        return bank_stocks_df
        
    except Exception as e:
        print(f"❌ 备用方法失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def save_to_csv(df, filename=None):
    """
    保存银行股票列表到CSV文件
    
    Args:
        df: DataFrame数据
        filename: 文件名，默认自动生成
    
    Returns:
        str: 文件路径
    """
    if df is None or len(df) == 0:
        print("❌ 没有数据可保存")
        return None
    
    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成文件名
    if filename is None:
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        filename = f"bank_stocks_list_{date_str}.csv"
    
    filepath = os.path.join(output_dir, filename)
    
    print(f"\n正在保存到: {filepath}")
    
    # 保存为CSV
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    # 验证文件
    if os.path.exists(filepath):
        file_size = os.path.getsize(filepath) / 1024  # KB
        print(f"✅ 文件保存成功!")
        print(f"   文件大小: {file_size:.2f} KB")
        print(f"   文件路径: {filepath}")
        print(f"   记录数: {len(df)}")
        
        # 读取验证
        verify_df = pd.read_csv(filepath)
        print(f"   验证列名: {', '.join(verify_df.columns)}")
        
        return filepath
    else:
        print(f"❌ 文件保存失败")
        return None


def print_summary(df):
    """打印银行股票统计摘要"""
    if df is None or len(df) == 0:
        return
    
    print("\n" + "=" * 80)
    print("银行股票统计摘要")
    print("=" * 80)
    
    print(f"\n总计: {len(df)} 只银行股票")
    
    # 按交易所统计
    if 'full_symbol' in df.columns:
        sh_count = len(df[df['full_symbol'].str.startswith('SHSE', na=False)])
        sz_count = len(df[df['full_symbol'].str.startswith('SZSE', na=False)])
        print(f"\n交易所分布:")
        print(f"  - 上海证券交易所 (SHSE): {sh_count} 只")
        print(f"  - 深圳证券交易所 (SZSE): {sz_count} 只")
    
    # 价格统计
    if 'price' in df.columns:
        print(f"\n价格统计:")
        print(f"  - 最高价: ¥{df['price'].max():.2f}")
        print(f"  - 最低价: ¥{df['price'].min():.2f}")
        print(f"  - 平均价: ¥{df['price'].mean():.2f}")
        print(f"  - 中位数: ¥{df['price'].median():.2f}")
    
    # 列出所有银行名称
    if 'name' in df.columns:
        print(f"\n银行列表:")
        for idx, row in df.iterrows():
            symbol = row.get('full_symbol', row.get('symbol', 'N/A'))
            name = row.get('name', 'N/A')
            price = row.get('price', 0)
            print(f"  {idx+1:3d}. {symbol:<15} {name:<10} ¥{price:>8.2f}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("A股银行股票代码获取工具")
    print("=" * 80)
    print(f"运行时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 尝试主要方法
    bank_stocks_df = get_all_bank_stocks()
    
    # 如果主要方法失败，尝试备用方法
    if bank_stocks_df is None or len(bank_stocks_df) == 0:
        print("\n主要方法失败，尝试网络备用方法...")
        bank_stocks_df = get_bank_stocks_alternative()
    
    # 如果网络方法都失败，使用本地数据
    if bank_stocks_df is None or len(bank_stocks_df) == 0:
        print("\n网络方法失败，使用本地银行股票列表...")
        bank_stocks_df = get_bank_stocks_local()
    
    if bank_stocks_df is not None and len(bank_stocks_df) > 0:
        # 打印统计摘要
        print_summary(bank_stocks_df)
        
        # 保存到CSV
        filepath = save_to_csv(bank_stocks_df)
        
        if filepath:
            print("\n" + "=" * 80)
            print("✅ 任务完成！")
            print("=" * 80)
            print(f"\n文件已保存至: {filepath}")
            print("\n使用示例:")
            print("  import pandas as pd")
            print(f"  df = pd.read_csv('{filepath}')")
            print("  print(df.head())")
            print("  print(df['symbol'].tolist())  # 获取所有股票代码")
            print("=" * 80)
            
            return True
        else:
            print("\n❌ 保存文件失败")
            return False
    else:
        print("\n" + "=" * 80)
        print("❌ 未能获取银行股票数据")
        print("=" * 80)
        return False


if __name__ == '__main__':
    success = main()
    
    if not success:
        exit(1)
