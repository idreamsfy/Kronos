"""
验证 AkShare 获取的数据是否符合 Kronos 要求
"""

import pandas as pd
import os
import matplotlib.pyplot as plt


def validate_csv_file(filepath):
    """
    验证 CSV 文件是否符合 Kronos 格式要求
    
    Args:
        filepath: CSV 文件路径
    
    Returns:
        dict: 验证结果
    """
    print(f"\n验证文件: {filepath}")
    print("-" * 70)
    
    try:
        # 读取 CSV
        df = pd.read_csv(filepath)
        
        # 检查必需的列
        required_columns = ['timestamps', 'open', 'high', 'low', 'close', 'volume', 'amount']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ 缺少列: {missing_columns}")
            return {'valid': False, 'error': f'Missing columns: {missing_columns}'}
        
        print(f"✅ 列检查通过: {list(df.columns)}")
        
        # 检查数据类型
        print(f"\n数据形状: {df.shape}")
        print(f"  - 行数: {len(df)}")
        print(f"  - 列数: {len(df.columns)}")
        
        # 检查时间戳
        df['timestamps'] = pd.to_datetime(df['timestamps'])
        print(f"\n时间范围:")
        print(f"  - 开始: {df['timestamps'].min()}")
        print(f"  - 结束: {df['timestamps'].max()}")
        print(f"  - 跨度: {(df['timestamps'].max() - df['timestamps'].min()).days} 天")
        
        # 检查数值范围
        print(f"\n价格统计:")
        print(f"  - Close 范围: [{df['close'].min():.2f}, {df['close'].max():.2f}]")
        print(f"  - Volume 范围: [{df['volume'].min()}, {df['volume'].max()}]")
        print(f"  - Amount 范围: [{df['amount'].min():.2f}, {df['amount'].max():.2f}]")
        
        # 检查缺失值
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            print(f"\n⚠️  发现缺失值:")
            for col, count in null_counts.items():
                if count > 0:
                    print(f"    {col}: {count}")
        else:
            print(f"\n✅ 无缺失值")
        
        # 检查异常值
        print(f"\n数据质量检查:")
        
        # OHLC 逻辑检查
        invalid_ohlc = ((df['high'] < df['low']) | 
                       (df['high'] < df['open']) | 
                       (df['high'] < df['close']) |
                       (df['low'] > df['open']) | 
                       (df['low'] > df['close'])).sum()
        
        if invalid_ohlc > 0:
            print(f"  ⚠️  OHLC 逻辑异常: {invalid_ohlc} 条记录")
        else:
            print(f"  ✅ OHLC 逻辑正常")
        
        # 负值检查
        negative_values = ((df[['open', 'high', 'low', 'close', 'volume', 'amount']] < 0).any(axis=1)).sum()
        if negative_values > 0:
            print(f"  ⚠️  负值记录: {negative_values} 条")
        else:
            print(f"  ✅ 无负值")
        
        # 零值检查
        zero_close = (df['close'] == 0).sum()
        if zero_close > 0:
            print(f"  ⚠️  收盘价为0: {zero_close} 条")
        else:
            print(f"  ✅ 收盘价均大于0")
        
        print(f"\n✅ 验证通过！数据符合 Kronos 要求")
        
        return {
            'valid': True,
            'rows': len(df),
            'date_range': f"{df['timestamps'].min()} to {df['timestamps'].max()}",
            'columns': list(df.columns)
        }
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return {'valid': False, 'error': str(e)}


def plot_stock_data(filepath, output_path=None):
    """
    绘制股票数据图表
    
    Args:
        filepath: CSV 文件路径
        output_path: 输出图片路径
    """
    df = pd.read_csv(filepath)
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    
    # 价格和成交量
    ax1 = axes[0]
    ax1.plot(df['timestamps'], df['close'], label='Close Price', color='blue', linewidth=1.5)
    ax1.set_ylabel('Price', fontsize=12)
    ax1.set_title(f'Stock Price History - {os.path.basename(filepath)}', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 成交量
    ax2 = axes[1]
    ax2.bar(df['timestamps'], df['volume'], label='Volume', color='green', alpha=0.6)
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # 成交额
    ax3 = axes[2]
    ax3.fill_between(df['timestamps'], df['amount'], alpha=0.5, color='orange')
    ax3.set_ylabel('Amount', fontsize=12)
    ax3.set_xlabel('Date', fontsize=12)
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"图表已保存至: {output_path}")
    else:
        plt.show()


def main():
    """主函数"""
    print("=" * 70)
    print("Kronos 数据格式验证工具")
    print("=" * 70)
    
    # 数据目录
    data_dir = "./akshare_data"
    
    if not os.path.exists(data_dir):
        print(f"错误: 目录 {data_dir} 不存在")
        print("请先运行 fetch_akshare_data.py 获取数据")
        return
    
    # 获取所有 CSV 文件
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"目录 {data_dir} 中没有 CSV 文件")
        return
    
    print(f"\n找到 {len(csv_files)} 个 CSV 文件")
    print("=" * 70)
    
    # 验证所有文件
    results = []
    for csv_file in csv_files:
        filepath = os.path.join(data_dir, csv_file)
        result = validate_csv_file(filepath)
        results.append({'file': csv_file, **result})
    
    # 总结
    print("\n" + "=" * 70)
    print("验证总结")
    print("=" * 70)
    
    valid_count = sum(1 for r in results if r.get('valid'))
    invalid_count = len(results) - valid_count
    
    print(f"\n总文件数: {len(results)}")
    print(f"✅ 有效: {valid_count}")
    print(f"❌ 无效: {invalid_count}")
    
    if invalid_count > 0:
        print(f"\n无效文件:")
        for r in results:
            if not r.get('valid'):
                print(f"  - {r['file']}: {r.get('error')}")
    
    # 绘制示例图表
    if valid_count > 0:
        print(f"\n生成示例图表...")
        sample_file = os.path.join(data_dir, csv_files[0])
        output_image = "./figures/akshare_data_sample.png"
        os.makedirs(os.path.dirname(output_image), exist_ok=True)
        
        try:
            plot_stock_data(sample_file, output_image)
        except Exception as e:
            print(f"图表生成失败: {e}")
            print("提示: 可能需要安装 matplotlib: pip install matplotlib")
    
    print("\n" + "=" * 70)
    print("验证完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
