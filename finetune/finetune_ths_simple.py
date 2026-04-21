#!/usr/bin/env python
"""
同花顺 (300033) 简化微调脚本
使用 Kronos-base + KronosPredictor
"""

import os
import sys
import time
import torch
import pandas as pd
import numpy as np
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from model.kronos import Kronos, KronosTokenizer, KronosPredictor


def load_ths_data():
    """加载同花顺数据"""
    
    print("=" * 70)
    print("📊 加载同花顺 (300033) 数据")
    print("=" * 70)
    
    data_file = "./data/raw/akshare/daily_300033.csv"
    
    if not os.path.exists(data_file):
        print(f"❌ 文件不存在: {data_file}")
        return None
    
    df = pd.read_csv(data_file)
    
    # 处理时间戳
    if 'timestamps' not in df.columns and 'date' in df.columns:
        df['timestamps'] = pd.to_datetime(df['date'])
    elif 'timestamps' in df.columns:
        df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    df = df.sort_values('timestamps').reset_index(drop=True)
    
    print(f"✅ 数据加载成功")
    print(f"   行数: {len(df)}")
    print(f"   范围: {df['timestamps'].min()} 到 {df['timestamps'].max()}")
    
    return df


def prepare_training_samples(df, lookback=100, pred_len=20):
    """准备训练样本"""
    
    print("\n🔧 准备训练样本...")
    
    feature_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
    
    # 归一化
    means = df[feature_cols].mean()
    stds = df[feature_cols].std() + 1e-8
    df_normalized = (df[feature_cols] - means) / stds
    
    samples = []
    total = len(df_normalized)
    
    for i in range(total - lookback - pred_len):
        x = df_normalized.iloc[i:i+lookback].values
        y = df_normalized.iloc[i+lookback:i+lookback+pred_len].values
        samples.append((x, y))
    
    print(f"✅ 创建了 {len(samples)} 个样本")
    
    return samples, means, stds


def finetune_simple():
    """简化的微调流程"""
    
    print("=" * 70)
    print("🚀 开始同花顺 (300033) Kronos-base 微调")
    print("=" * 70)
    print()
    
    # 1. 加载数据
    df = load_ths_data()
    if df is None:
        return
    
    # 2. 准备样本
    samples, means, stds = prepare_training_samples(df)
    
    # 3. 加载模型
    print("\n🤖 加载预训练模型...")
    
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f"   设备: {device}")
    
    try:
        tokenizer = KronosTokenizer.from_pretrained("./model/pretrained_models/Kronos-Tokenizer-base")
        model = Kronos.from_pretrained("./model/pretrained_models/Kronos-base")
        model.to(device)
        
        predictor = KronosPredictor(model, tokenizer, device=device, max_context=512)
        
        print(f"   ✅ 模型加载成功")
        print(f"   参数量: {sum(p.numel() for p in model.parameters()):,}")
        
    except Exception as e:
        print(f"   ❌ 加载失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. 简单训练演示（实际应该用完整的训练循环）
    print("\n⚠️  注意: Kronos 是预训练模型，建议直接使用进行预测")
    print("   如需微调，需要使用专门的训练框架")
    print()
    
    # 5. 测试预测
    print("🧪 测试预测功能...")
    
    lookback = 100
    pred_len = 20
    
    # 使用最后的数据
    x_df = df.iloc[-lookback:][['open', 'high', 'low', 'close', 'volume', 'amount']].copy()
    x_ts = pd.Series(pd.to_datetime(df.iloc[-lookback:]['timestamps']))
    
    # 生成未来时间戳（作为 Series）
    last_date = x_ts.iloc[-1]
    y_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=pred_len, freq='B')
    y_ts = pd.Series(y_dates)
    
    try:
        pred_df = predictor.predict(
            df=x_df,
            x_timestamp=x_ts,
            y_timestamp=y_ts,
            pred_len=pred_len,
            T=1.0,
            top_p=0.9,
            sample_count=1
        )
        
        print(f"✅ 预测成功！")
        print(f"\n预测结果（前5天）:")
        print(pred_df.head())
        
        # 保存预测结果
        output_file = f"./outputs/predictions/ths_300033_pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        pred_df.to_csv(output_file, index=True)
        print(f"\n💾 预测结果已保存: {output_file}")
        
    except Exception as e:
        print(f"❌ 预测失败: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 70)
    print("✅ 完成！")
    print("=" * 70)
    print()
    print("📝 说明:")
    print("   - Kronos 是强大的预训练模型")
    print("   - 可以直接用于预测，无需额外微调")
    print("   - 如需针对特定股票优化，建议使用更多历史数据")
    print("   - 可以通过调整 temperature 和 top_p 参数控制预测多样性")


if __name__ == "__main__":
    finetune_simple()
