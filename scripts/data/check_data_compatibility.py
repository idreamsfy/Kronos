# coding=utf-8
"""
检查浦发银行数据是否符合Kronos训练要求
"""
import pandas as pd
import numpy as np
from pathlib import Path

def check_kronos_data_compatibility(csv_path):
    """
    检查CSV数据是否符合Kronos训练要求
    
    Kronos要求的数据格式:
    - 必需列: timestamps, open, close, high, low, volume, amount
    - 时间格式: YYYY/MM/DD HH:MM (5分钟数据) 或 YYYY-MM-DD (日线数据)
    - 数据类型: OHLCV为数值型
    """
    
    print("=" * 80)
    print("Kronos 数据兼容性检查")
    print("=" * 80)
    
    # 读取数据
    print(f"\n📂 正在读取数据: {csv_path}")
    df = pd.read_csv(csv_path)
    
    print(f"✅ 数据加载成功")
    print(f"   - 记录数: {len(df):,}")
    print(f"   - 列数: {len(df.columns)}")
    
    # 检查必需列
    print("\n" + "=" * 80)
    print("1. 列名检查")
    print("=" * 80)
    
    kronos_required_cols = ['timestamps', 'open', 'close', 'high', 'low', 'volume', 'amount']
    current_cols = df.columns.tolist()
    
    print(f"\nKronos要求的列: {kronos_required_cols}")
    print(f"当前数据的列: {current_cols}")
    
    missing_cols = [col for col in kronos_required_cols if col not in current_cols]
    
    if missing_cols:
        print(f"\n❌ 缺少的列: {missing_cols}")
        print("\n需要转换的列映射:")
        col_mapping = {
            'date': 'timestamps',
            'trade_date': 'timestamps',
            'datetime': 'timestamps',
            'symbol': '可删除或不使用',
            'name': '可删除或不使用',
            'pre_close': '可选列',
            'amplitude': '可选列',
            'change_pct': '可选列',
            'change_amount': '可选列',
            'turnover_rate': '可选列'
        }
        
        for curr_col, kronos_col in col_mapping.items():
            if curr_col in current_cols and kronos_col in missing_cols:
                print(f"   ✓ '{curr_col}' → '{kronos_col}'")
    else:
        print(f"\n✅ 所有必需列都存在")
    
    # 检查数据类型
    print("\n" + "=" * 80)
    print("2. 数据类型检查")
    print("=" * 80)
    
    numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
    available_numeric_cols = [col for col in numeric_cols if col in current_cols]
    
    print(f"\n数值型列检查:")
    for col in available_numeric_cols:
        dtype = df[col].dtype
        has_null = df[col].isnull().any()
        null_count = df[col].isnull().sum()
        
        status = "✅" if pd.api.types.is_numeric_dtype(df[col]) else "❌"
        null_status = f"(空值: {null_count})" if has_null else ""
        print(f"   {status} {col:10s}: {dtype} {null_status}")
    
    # 检查时间列
    print("\n" + "=" * 80)
    print("3. 时间列检查")
    print("=" * 80)
    
    time_cols = ['timestamps', 'date', 'trade_date', 'datetime']
    available_time_cols = [col for col in time_cols if col in current_cols]
    
    if available_time_cols:
        time_col = available_time_cols[0]
        print(f"\n使用时间列: '{time_col}'")
        print(f"示例值: {df[time_col].iloc[0]}")
        print(f"数据类型: {df[time_col].dtype}")
        
        # 尝试解析日期
        try:
            parsed_dates = pd.to_datetime(df[time_col])
            print(f"✅ 日期格式可解析")
            print(f"   - 最早日期: {parsed_dates.min()}")
            print(f"   - 最晚日期: {parsed_dates.max()}")
            print(f"   - 时间跨度: {(parsed_dates.max() - parsed_dates.min()).days} 天")
        except Exception as e:
            print(f"❌ 日期解析失败: {e}")
    else:
        print(f"\n❌ 未找到时间列")
    
    # 数据质量检查
    print("\n" + "=" * 80)
    print("4. 数据质量检查")
    print("=" * 80)
    
    issues = []
    
    # 检查空值
    null_counts = df[available_numeric_cols].isnull().sum()
    total_nulls = null_counts.sum()
    if total_nulls > 0:
        issues.append(f"发现 {total_nulls} 个空值")
        print(f"\n⚠️  空值统计:")
        for col, count in null_counts.items():
            if count > 0:
                print(f"   - {col}: {count} 个空值")
    else:
        print(f"\n✅ 无空值")
    
    # 检查异常值（负数）
    for col in ['open', 'high', 'low', 'close']:
        if col in df.columns:
            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                issues.append(f"{col} 存在 {negative_count} 个负值")
    
    if not any("负值" in issue for issue in issues):
        print(f"✅ 价格数据无负值")
    
    # 检查OHLC逻辑
    if all(col in df.columns for col in ['open', 'high', 'low', 'close']):
        invalid_high = (df['high'] < df['low']).sum()
        invalid_oh = ((df['open'] > df['high']) | (df['open'] < df['low'])).sum()
        invalid_cl = ((df['close'] > df['high']) | (df['close'] < df['low'])).sum()
        
        if invalid_high > 0:
            issues.append(f"{invalid_high} 条记录的 high < low")
        if invalid_oh > 0:
            issues.append(f"{invalid_oh} 条记录的 open 超出 [low, high] 范围")
        if invalid_cl > 0:
            issues.append(f"{invalid_cl} 条记录的 close 超出 [low, high] 范围")
        
        if invalid_high == 0 and invalid_oh == 0 and invalid_cl == 0:
            print(f"✅ OHLC数据逻辑正确")
    
    # 检查数据量
    print("\n" + "=" * 80)
    print("5. 数据量评估")
    print("=" * 80)
    
    record_count = len(df)
    print(f"\n总记录数: {record_count:,}")
    
    # Kronos建议的最小数据量
    min_recommended = 10000  # 至少1万条
    good_amount = 50000      # 5万条以上较好
    
    if record_count < min_recommended:
        print(f"⚠️  数据量较少 (建议至少 {min_recommended:,} 条)")
        print(f"   当前数据量可能不足以充分训练模型")
        issues.append(f"数据量不足: {record_count} < {min_recommended}")
    elif record_count < good_amount:
        print(f"✅ 数据量适中 ({record_count:,} 条)")
        print(f"   可以进行训练，但更多数据会更好")
    else:
        print(f"✅ 数据量充足 ({record_count:,} 条)")
    
    # 频率检查
    if available_time_cols:
        try:
            parsed_dates = pd.to_datetime(df[available_time_cols[0]])
            if len(parsed_dates) > 1:
                time_diffs = parsed_dates.diff().dropna()
                median_diff = time_diffs.median()
                
                print(f"\n数据频率分析:")
                print(f"   - 中位数时间间隔: {median_diff}")
                
                if median_diff.days >= 1:
                    print(f"   - 类型: 日线数据")
                    print(f"   ⚠️  Kronos主要针对5分钟K线优化，日线数据可能需要调整参数")
                elif median_diff.hours >= 1:
                    print(f"   - 类型: 小时级数据")
                elif median_diff.minutes >= 5:
                    print(f"   - 类型: 分钟级数据")
                    if median_diff.minutes == 5:
                        print(f"   ✅ 5分钟数据，完美匹配Kronos")
                else:
                    print(f"   - 类型: 高频数据")
        except:
            pass
    
    # 总结和建议
    print("\n" + "=" * 80)
    print("6. 总结与建议")
    print("=" * 80)
    
    if not issues:
        print("\n✅ 数据基本符合Kronos训练要求！")
    else:
        print(f"\n⚠️  发现 {len(issues)} 个问题:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    
    print("\n" + "-" * 80)
    print("建议操作:")
    print("-" * 80)
    
    # 生成转换建议
    if missing_cols:
        print("\n📝 需要数据转换:")
        print("   运行以下命令创建符合Kronos格式的数据:")
        print("   python tests/convert_to_kronos_format.py")
    
    if 'symbol' in df.columns or 'name' in df.columns:
        print("\n💡 提示: 可以删除不必要的列以减小文件大小")
    
    print("\n📚 参考配置:")
    print("   - lookback_window: 512 (默认)")
    print("   - predict_window: 48 (默认)")
    print("   - batch_size: 16 (可根据内存调整)")
    
    # 返回兼容性评分
    score = 100
    if missing_cols:
        score -= 30
    if total_nulls > 0:
        score -= 20
    if record_count < min_recommended:
        score -= 20
    if issues:
        score -= len(issues) * 5
    
    score = max(0, score)
    
    print(f"\n{'=' * 80}")
    print(f"兼容性评分: {score}/100")
    print(f"{'=' * 80}")
    
    if score >= 80:
        print("✅ 数据质量良好，可以直接用于训练")
    elif score >= 60:
        print("⚠️  数据需要进行一些转换后才能使用")
    else:
        print("❌ 数据需要大量处理才能用于训练")
    
    return score >= 60


if __name__ == '__main__':
    import sys
    
    # 默认检查浦发银行数据
    csv_file = 'data/SHSE_600000_daily_2021-04-19_2026-04-18.csv'
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    
    # 检查文件是否存在
    if not Path(csv_file).exists():
        print(f"❌ 文件不存在: {csv_file}")
        sys.exit(1)
    
    # 执行检查
    is_compatible = check_kronos_data_compatibility(csv_file)
    
    sys.exit(0 if is_compatible else 1)
