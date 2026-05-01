"""
数据质量分析脚本
分析 5min_300033_with_features.csv 的数据质量
"""
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def analyze_data_quality(file_path):
    """
    全面分析金融数据文件的质量
    """
    print("=" * 80)
    print("金融数据质量分析报告")
    print("=" * 80)
    print(f"文件路径: {file_path}")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 1. 读取数据
    print("\n【1. 数据加载】")
    try:
        df = pd.read_csv(file_path, parse_dates=['timestamps'])
        print(f"✓ 成功加载数据")
        print(f"  - 总行数: {len(df):,}")
        print(f"  - 总列数: {len(df.columns)}")
    except Exception as e:
        print(f"✗ 数据加载失败: {e}")
        return
    
    # 2. 基本信息
    print("\n【2. 数据结构】")
    print(f"数据类型分布:")
    dtype_counts = df.dtypes.value_counts()
    for dtype, count in dtype_counts.items():
        print(f"  - {dtype}: {count} 列")
    
    print(f"\n列名列表 ({len(df.columns)} 列):")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2d}. {col}")
    
    # 3. 时间范围分析
    print("\n【3. 时间范围分析】")
    if 'timestamps' in df.columns:
        time_min = df['timestamps'].min()
        time_max = df['timestamps'].max()
        time_range = time_max - time_min
        print(f"起始时间: {time_min}")
        print(f"结束时间: {time_max}")
        print(f"时间跨度: {time_range}")
        print(f"交易日数量: {df['timestamps'].dt.date.nunique()}")
        
        # 检查时间间隔
        if len(df) > 1:
            time_diffs = df['timestamps'].diff().dropna()
            most_common_interval = time_diffs.mode()[0]
            print(f"最常见时间间隔: {most_common_interval}")
            
            # 检查是否有缺失的时间点
            expected_intervals = time_range / most_common_interval
            actual_intervals = len(df) - 1
            missing_ratio = (expected_intervals - actual_intervals) / expected_intervals * 100
            print(f"预期数据点数: {expected_intervals:.0f}")
            print(f"实际数据点数: {actual_intervals}")
            print(f"时间连续性: {'良好' if missing_ratio < 5 else '存在缺失'} (缺失率: {missing_ratio:.2f}%)")
    
    # 4. 缺失值分析
    print("\n【4. 缺失值分析】")
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / len(df)) * 100
    missing_df = pd.DataFrame({
        '缺失数量': missing_count,
        '缺失比例(%)': missing_pct
    })
    missing_df = missing_df[missing_df['缺失数量'] > 0].sort_values('缺失数量', ascending=False)
    
    if len(missing_df) == 0:
        print("✓ 无缺失值")
    else:
        print(f"发现 {len(missing_df)} 个列存在缺失值:")
        for col, row in missing_df.iterrows():
            print(f"  - {col:30s}: {row['缺失数量']:6d} ({row['缺失比例(%)']:.2f}%)")
    
    # 5. 重复值分析
    print("\n【5. 重复值分析】")
    duplicate_count = df.duplicated().sum()
    print(f"重复行数: {duplicate_count}")
    if duplicate_count > 0:
        print(f"  ⚠ 警告: 发现 {duplicate_count} 行完全重复的数据")
    else:
        print("✓ 无重复数据")
    
    # 6. 数值特征统计
    print("\n【6. 核心价格数据统计】")
    price_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
    existing_price_cols = [col for col in price_cols if col in df.columns]
    
    if existing_price_cols:
        stats = df[existing_price_cols].describe()
        print(stats.round(2).to_string())
        
        # 检查 OHLC 合理性
        print("\nOHLC 合理性检查:")
        invalid_ohlc = ((df['high'] < df['low']) | 
                       (df['high'] < df['open']) | 
                       (df['high'] < df['close']) |
                       (df['low'] > df['open']) | 
                       (df['low'] > df['close']))
        invalid_count = invalid_ohlc.sum()
        if invalid_count > 0:
            print(f"  ⚠ 警告: 发现 {invalid_count} 行 OHLC 数据不合理")
        else:
            print("  ✓ OHLC 数据合理")
    
    # 7. 技术指标分析
    print("\n【7. 技术指标完整性检查】")
    technical_indicators = [
        'MA5', 'MA10', 'MA20', 'MA30', 'MA60',
        'EMA12', 'EMA26', 'MACD', 'MACD_signal', 'MACD_hist',
        'RSI', 'BB_upper', 'BB_lower', 'BB_width', 'ATR',
        'volume_MA5', 'volume_MA20', 'volume_ratio'
    ]
    
    existing_indicators = [col for col in technical_indicators if col in df.columns]
    print(f"技术指标列数: {len(existing_indicators)}/{len(technical_indicators)}")
    
    for indicator in existing_indicators:
        null_count = df[indicator].isnull().sum()
        if null_count > 0:
            print(f"  ⚠ {indicator:20s}: {null_count:5d} 缺失值 ({null_count/len(df)*100:.2f}%)")
    
    # 8. 收益率和波动率分析
    print("\n【8. 收益率和波动率分析】")
    return_cols = ['return_1', 'return_5', 'return_10', 'return_20']
    volatility_cols = ['volatility_5', 'volatility_20']
    
    existing_return_cols = [col for col in return_cols if col in df.columns]
    existing_volatility_cols = [col for col in volatility_cols if col in df.columns]
    
    if existing_return_cols:
        print("\n收益率统计:")
        for col in existing_return_cols:
            mean_ret = df[col].mean()
            std_ret = df[col].std()
            min_ret = df[col].min()
            max_ret = df[col].max()
            print(f"  {col:15s}: 均值={mean_ret:8.4f}, 标准差={std_ret:8.4f}, "
                  f"范围=[{min_ret:8.4f}, {max_ret:8.4f}]")
    
    if existing_volatility_cols:
        print("\n波动率统计:")
        for col in existing_volatility_cols:
            mean_vol = df[col].mean()
            std_vol = df[col].std()
            print(f"  {col:15s}: 均值={mean_vol:8.4f}, 标准差={std_vol:8.4f}")
    
    # 9. 异常值检测
    print("\n【9. 异常值检测 (基于3σ原则)】")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    outlier_summary = {}
    
    for col in numeric_cols[:10]:  # 只检查前10个数值列
        mean_val = df[col].mean()
        std_val = df[col].std()
        lower_bound = mean_val - 3 * std_val
        upper_bound = mean_val + 3 * std_val
        
        outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
        outlier_pct = outliers / len(df) * 100
        
        if outlier_pct > 1:  # 只显示异常值比例超过1%的列
            outlier_summary[col] = {
                'outliers': outliers,
                'percentage': outlier_pct
            }
    
    if outlier_summary:
        print("发现以下列存在较多异常值:")
        for col, info in outlier_summary.items():
            print(f"  - {col:30s}: {info['outliers']:6d} ({info['percentage']:.2f}%)")
    else:
        print("✓ 未发现显著异常值")
    
    # 10. 标签分布
    print("\n【10. 标签分布分析】")
    if 'label' in df.columns:
        label_dist = df['label'].value_counts()
        print("标签分布:")
        for label, count in label_dist.items():
            pct = count / len(df) * 100
            print(f"  标签 {label}: {count:6d} ({pct:5.2f}%)")
        
        # 检查类别平衡
        if len(label_dist) == 2:
            imbalance_ratio = label_dist.max() / label_dist.min()
            print(f"\n类别不平衡比率: {imbalance_ratio:.2f}")
            if imbalance_ratio > 2:
                print("  ⚠ 警告: 存在类别不平衡问题")
            else:
                print("  ✓ 类别分布相对平衡")
    
    # 11. 数据相关性分析
    print("\n【11. 关键特征相关性】")
    correlation_cols = ['close', 'volume', 'RSI', 'MACD', 'return_1', 'volatility_5']
    existing_corr_cols = [col for col in correlation_cols if col in df.columns]
    
    if len(existing_corr_cols) >= 2:
        corr_matrix = df[existing_corr_cols].corr()
        print("相关系数矩阵 (部分):")
        print(corr_matrix.round(3).to_string())
    
    # 12. 数据质量评分
    print("\n【12. 数据质量综合评分】")
    score = 100
    
    # 缺失值扣分
    total_missing = df.isnull().sum().sum()
    missing_ratio = total_missing / (len(df) * len(df.columns)) * 100
    if missing_ratio > 0:
        score -= min(20, missing_ratio * 10)
        print(f"  - 缺失值比例: {missing_ratio:.2f}% (扣分: {min(20, missing_ratio * 10):.1f})")
    
    # 重复值扣分
    if duplicate_count > 0:
        dup_ratio = duplicate_count / len(df) * 100
        score -= min(10, dup_ratio * 5)
        print(f"  - 重复值比例: {dup_ratio:.2f}% (扣分: {min(10, dup_ratio * 5):.1f})")
    
    # OHLC合理性扣分
    if 'high' in df.columns and 'low' in df.columns:
        if invalid_count > 0:
            ohlc_ratio = invalid_count / len(df) * 100
            score -= min(15, ohlc_ratio * 5)
            print(f"  - OHLC不合理比例: {ohlc_ratio:.2f}% (扣分: {min(15, ohlc_ratio * 5):.1f})")
    
    # 时间连续性扣分
    if 'timestamps' in df.columns and len(df) > 1:
        if missing_ratio > 5:
            score -= min(10, missing_ratio)
            print(f"  - 时间不连续 (扣分: {min(10, missing_ratio):.1f})")
    
    score = max(0, score)
    
    print(f"\n{'='*50}")
    print(f"数据质量总分: {score:.1f}/100")
    if score >= 90:
        print("评级: 优秀 ✓")
    elif score >= 75:
        print("评级: 良好 ✓")
    elif score >= 60:
        print("评级: 合格 ⚠")
    else:
        print("评级: 需要改进 ✗")
    print(f"{'='*50}")
    
    # 13. 建议
    print("\n【13. 改进建议】")
    suggestions = []
    
    if missing_ratio > 0:
        suggestions.append("1. 处理缺失值：考虑使用前向填充、插值或删除含缺失值的行")
    
    if duplicate_count > 0:
        suggestions.append("2. 删除重复数据：确保每条记录的唯一性")
    
    if 'timestamps' in df.columns:
        suggestions.append("3. 时间特征工程：添加小时、星期、月份等时间特征")
    
    if 'label' in df.columns and len(label_dist) == 2:
        if imbalance_ratio > 2:
            suggestions.append("4. 类别平衡：使用过采样(SMOTE)或欠采样技术平衡类别")
    
    suggestions.append("5. 特征标准化：对数值特征进行标准化或归一化处理")
    suggestions.append("6. 异常值处理：考虑使用IQR方法或Z-score方法处理异常值")
    
    for suggestion in suggestions:
        print(f"  {suggestion}")
    
    print("\n" + "=" * 80)
    print("分析完成")
    print("=" * 80)
    
    return df

if __name__ == "__main__":
    file_path = "data/raw/futu/5min_300033_with_features.csv"
    df = analyze_data_quality(file_path)
