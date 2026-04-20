# coding=utf-8
"""
将浦发银行数据转换为Kronos训练格式
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

def convert_to_kronos_format(input_csv, output_csv=None):
    """
    将股票数据转换为Kronos训练所需格式
    
    Kronos要求的格式:
    - 列名: timestamps, open, close, high, low, volume, amount
    - 时间格式: YYYY/MM/DD HH:MM (5分钟) 或 YYYY-MM-DD (日线)
    """
    
    print("=" * 80)
    print("数据转换: 标准格式 → Kronos格式")
    print("=" * 80)
    
    # 读取数据
    print(f"\n📂 读取源数据: {input_csv}")
    df = pd.read_csv(input_csv)
    print(f"✅ 成功加载 {len(df)} 条记录")
    
    # 列映射
    col_mapping = {
        'date': 'timestamps',
        'trade_date': 'timestamps',
        'datetime': 'timestamps',
        'open': 'open',
        'close': 'close',
        'high': 'high',
        'low': 'low',
        'volume': 'volume',
        'amount': 'amount'
    }
    
    # 重命名列
    print("\n🔄 转换列名...")
    
    # 首先确定使用哪个时间列
    time_col_candidates = ['date', 'trade_date', 'datetime']
    time_col_used = None
    for col in time_col_candidates:
        if col in df.columns:
            time_col_used = col
            break
    
    if time_col_used is None:
        print("❌ 未找到时间列 (date/trade_date/datetime)")
        return False
    
    print(f"   使用时间列: '{time_col_used}'")
    
    # 创建新的DataFrame，只包含需要的列
    df_kronos = pd.DataFrame()
    df_kronos['timestamps'] = df[time_col_used]
    
    # 复制其他必需列
    for col in ['open', 'close', 'high', 'low', 'volume', 'amount']:
        if col in df.columns:
            df_kronos[col] = df[col]
        else:
            print(f"❌ 缺少列: {col}")
            return False
    
    print(f"✅ 列名转换完成")
    
    # 选择需要的列（已经在上一步完成）
    # df_kronos 已经包含正确的列
    
    # 处理时间格式
    print("\n🔄 处理时间格式...")
    try:
        # 尝试解析日期
        df_kronos['timestamps'] = pd.to_datetime(df_kronos['timestamps'])
        
        # 检查是日线还是分钟线
        time_diffs = df_kronos['timestamps'].diff().dropna()
        median_diff = time_diffs.median()
        
        if median_diff.days >= 1:
            # 日线数据: 保持 YYYY-MM-DD 格式
            df_kronos['timestamps'] = df_kronos['timestamps'].dt.strftime('%Y-%m-%d')
            print(f"   检测到日线数据，使用格式: YYYY-MM-DD")
        else:
            # 分钟线数据: 转换为 YYYY/MM/DD HH:MM 格式
            df_kronos['timestamps'] = df_kronos['timestamps'].dt.strftime('%Y/%m/%d %H:%M')
            print(f"   检测到分钟线数据，使用格式: YYYY/MM/DD HH:MM")
        
        print(f"✅ 时间格式转换完成")
    except Exception as e:
        print(f"⚠️  时间格式转换警告: {e}")
        print(f"   保持原始时间格式")
    
    # 数据验证
    print("\n🔍 数据验证...")
    
    # 检查空值
    null_counts = df_kronos.isnull().sum()
    if null_counts.sum() > 0:
        print(f"⚠️  发现空值:")
        for col, count in null_counts.items():
            if count > 0:
                print(f"   - {col}: {count} 个")
        print(f"   正在删除含空值的行...")
        df_kronos = df_kronos.dropna()
        print(f"   ✅ 删除后剩余 {len(df_kronos)} 条记录")
    else:
        print(f"✅ 无空值")
    
    # 检查数值范围
    price_cols = ['open', 'high', 'low', 'close']
    for col in price_cols:
        if (df_kronos[col] <= 0).any():
            negative_count = (df_kronos[col] <= 0).sum()
            print(f"⚠️  {col} 存在 {negative_count} 个非正值，正在过滤...")
            df_kronos = df_kronos[df_kronos[col] > 0]
    
    # OHLC逻辑验证
    invalid_count = 0
    if all(col in df_kronos.columns for col in ['open', 'high', 'low', 'close']):
        invalid_high_low = (df_kronos['high'] < df_kronos['low']).sum()
        invalid_open = ((df_kronos['open'] > df_kronos['high']) | (df_kronos['open'] < df_kronos['low'])).sum()
        invalid_close = ((df_kronos['close'] > df_kronos['high']) | (df_kronos['close'] < df_kronos['low'])).sum()
        
        invalid_count = invalid_high_low + invalid_open + invalid_close
        
        if invalid_count > 0:
            print(f"⚠️  发现 {invalid_count} 条OHLC逻辑异常的记录，正在过滤...")
            mask = (
                (df_kronos['high'] >= df_kronos['low']) &
                (df_kronos['open'] >= df_kronos['low']) & (df_kronos['open'] <= df_kronos['high']) &
                (df_kronos['close'] >= df_kronos['low']) & (df_kronos['close'] <= df_kronos['high'])
            )
            df_kronos = df_kronos[mask]
            print(f"   ✅ 过滤后剩余 {len(df_kronos)} 条记录")
        else:
            print(f"✅ OHLC数据逻辑正确")
    
    # 确定输出文件路径
    if output_csv is None:
        input_path = Path(input_csv)
        output_csv = str(input_path.parent / f"kronos_{input_path.stem}.csv")
    
    # 保存数据
    print(f"\n💾 保存数据到: {output_csv}")
    df_kronos.to_csv(output_csv, index=False, encoding='utf-8-sig')
    
    # 验证输出文件
    if Path(output_csv).exists():
        file_size = Path(output_csv).stat().st_size / 1024
        print(f"✅ 文件保存成功!")
        print(f"   文件大小: {file_size:.2f} KB")
        print(f"   记录数: {len(df_kronos)}")
        
        # 显示示例数据
        print(f"\n📋 转换后的数据示例 (前5行):")
        print(df_kronos.head().to_string(index=False))
        
        print(f"\n📊 数据统计:")
        print(f"   - 总记录数: {len(df_kronos):,}")
        print(f"   - 时间范围: {df_kronos['timestamps'].iloc[0]} 至 {df_kronos['timestamps'].iloc[-1]}")
        print(f"   - 价格范围: ¥{df_kronos['low'].min():.2f} - ¥{df_kronos['high'].max():.2f}")
        print(f"   - 平均成交量: {df_kronos['volume'].mean():,.0f}")
        
        return True
    else:
        print(f"❌ 文件保存失败")
        return False


def create_training_config(data_path, config_path=None):
    """
    为转换后的数据创建训练配置文件
    """
    print("\n" + "=" * 80)
    print("创建训练配置文件")
    print("=" * 80)
    
    if config_path is None:
        config_path = "finetune_csv/configs/config_spdb_daily.yaml"
    
    # 读取数据获取信息
    df = pd.read_csv(data_path)
    record_count = len(df)
    
    # 根据数据量调整配置
    if record_count < 5000:
        tokenizer_epochs = 10
        basemodel_epochs = 5
        batch_size = 8
        print(f"⚠️  数据量较少 ({record_count} 条)，使用保守配置")
    elif record_count < 20000:
        tokenizer_epochs = 15
        basemodel_epochs = 10
        batch_size = 16
        print(f"✅ 数据量适中 ({record_count} 条)")
    else:
        tokenizer_epochs = 20
        basemodel_epochs = 15
        batch_size = 32
        print(f"✅ 数据量充足 ({record_count} 条)")
    
    config_content = f"""# Configuration for Kronos Fine-tuning on SPDB Daily Data
# Generated by convert_to_kronos_format.py

data:
  # Path to the converted data
  data_path: "{data_path}"
  lookback_window: 512
  predict_window: 48
  max_context: 512
  clip: 5.0
  # Dataset split ratio
  train_ratio: 0.8
  val_ratio: 0.15
  test_ratio: 0.05

training:
  # Adjusted epochs based on data size
  tokenizer_epochs: {tokenizer_epochs}
  basemodel_epochs: {basemodel_epochs}
  batch_size: {batch_size}
  log_interval: 10
  num_workers: 0  # Set to 0 for Windows compatibility
  seed: 42
  
  tokenizer_learning_rate: 0.0002
  predictor_learning_rate: 0.000001
  
  adam_beta1: 0.9
  adam_beta2: 0.95
  adam_weight_decay: 0.1
  
  # Gradient accumulation steps
  accumulation_steps: 1

# Model path configuration
model_paths:
  # Use pre-trained models from Hugging Face
  pretrained_tokenizer: "NeoQuasar/Kronos-Tokenizer-base"
  pretrained_predictor: "NeoQuasar/Kronos-base"
  
  # Experiment name and save paths
  exp_name: "spdb_daily_finetune"
  base_path: "outputs/finetuned_models"
  
  # Auto-generated paths (leave empty for auto-generation)
  base_save_path: ""
  finetuned_tokenizer: ""
  
  tokenizer_save_name: "tokenizer"
  basemodel_save_name: "basemodel"

experiment:
  name: "spdb_daily_prediction"
  description: "Fine-tuning on SPDB daily data"
  use_comet: false
"""
    
    # 保存配置文件
    config_path_obj = Path(config_path)
    config_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✅ 配置文件已保存: {config_path}")
    print(f"\n📝 配置要点:")
    print(f"   - Tokenizer Epochs: {tokenizer_epochs}")
    print(f"   - Predictor Epochs: {basemodel_epochs}")
    print(f"   - Batch Size: {batch_size}")
    print(f"   - Lookback Window: 512")
    print(f"   - Predict Window: 48")
    
    return config_path


if __name__ == '__main__':
    # 默认输入文件
    input_file = 'data/SHSE_600000_daily_2021-04-19_2026-04-18.csv'
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    
    # 检查文件是否存在
    if not Path(input_file).exists():
        print(f"❌ 文件不存在: {input_file}")
        sys.exit(1)
    
    # 执行转换
    success = convert_to_kronos_format(input_file)
    
    if success:
        # 生成输出文件名
        input_path = Path(input_file)
        output_file = str(input_path.parent / f"kronos_{input_path.stem}.csv")
        
        # 创建训练配置
        create_training_config(output_file)
        
        print("\n" + "=" * 80)
        print("✅ 转换完成！")
        print("=" * 80)
        print(f"\n下一步:")
        print(f"1. 检查转换后的数据: {output_file}")
        print(f"2. 使用配置文件开始训练:")
        print(f"   python finetune_csv/train_sequential.py --config finetune_csv/configs/config_spdb_daily.yaml")
        print("=" * 80)
    else:
        print("\n❌ 转换失败")
        sys.exit(1)
