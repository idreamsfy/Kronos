#!/usr/bin/env python
"""
使用微调后的 Kronos-base 模型预测同花顺 (300033) 未来10天行情
"""

import os
import sys
import torch
import pandas as pd
import numpy as np
from datetime import datetime
import safetensors.torch

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from model.kronos import Kronos, KronosTokenizer, KronosPredictor


def predict_with_finetuned_model():
    """使用微调模型进行预测"""
    
    print("=" * 70)
    print("🔮 使用微调模型预测同花顺 (300033) 未来10天行情")
    print("=" * 70)
    print()
    
    # ==================== 1. 加载数据 ====================
    print("1. 加载最新数据...")
    data_file = "./data/raw/akshare/daily_300033.csv"
    
    if not os.path.exists(data_file):
        print(f"❌ 文件不存在: {data_file}")
        return
    
    df = pd.read_csv(data_file)
    if 'timestamps' not in df.columns and 'date' in df.columns:
        df['timestamps'] = pd.to_datetime(df['date'])
    elif 'timestamps' in df.columns:
        df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    df = df.sort_values('timestamps').reset_index(drop=True)
    
    print(f"   ✅ 数据加载: {len(df)} 行")
    print(f"   最新日期: {df['timestamps'].max().strftime('%Y-%m-%d')}")
    print(f"   最新收盘价: {df['close'].iloc[-1]:.2f}")
    print()
    
    # ==================== 2. 设备选择 ====================
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f"2. 使用设备: {device}")
    print()
    
    # ==================== 3. 加载 Tokenizer ====================
    print("3. 加载 Tokenizer...")
    tokenizer_path = "./model/pretrained_models/Kronos-Tokenizer-base"
    tokenizer = KronosTokenizer.from_pretrained(tokenizer_path)
    print(f"   ✅ Tokenizer 加载成功")
    print()
    
    # ==================== 4. 加载微调模型 ====================
    print("4. 加载微调模型...")
    
    # 从原始模型加载架构
    original_model_path = "./model/pretrained_models/Kronos-base"
    model = Kronos.from_pretrained(original_model_path)
    
    # 加载微调权重
    finetuned_model_path = "./outputs/models/finetune_300033_base_real/best_model/model.safetensors"
    
    if os.path.exists(finetuned_model_path):
        state_dict = safetensors.torch.load_file(finetuned_model_path)
        model.load_state_dict(state_dict, strict=False)
        print(f"   ✅ 微调权重加载成功")
    else:
        print(f"   ⚠️  微调权重文件不存在，使用原始模型")
    
    model.to(device)
    predictor = KronosPredictor(model, tokenizer, device=device, max_context=512)
    print(f"   ✅ 模型准备完成")
    print()
    
    # ==================== 5. 准备预测数据 ====================
    print("5. 准备预测数据...")
    
    lookback = 100  # 使用最近100天数据
    pred_len = 10   # 预测未来10天
    
    # 提取特征
    x_df = df.iloc[-lookback:][['open', 'high', 'low', 'close', 'volume', 'amount']].copy()
    x_ts = pd.Series(pd.to_datetime(df.iloc[-lookback:]['timestamps']))
    
    # 生成未来时间戳（工作日）
    last_date = x_ts.iloc[-1]
    y_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=pred_len, freq='B')
    y_ts = pd.Series(y_dates)
    
    print(f"   历史数据: {lookback} 天 ({df.iloc[-lookback]['timestamps'].strftime('%Y-%m-%d')} 至 {last_date.strftime('%Y-%m-%d')})")
    print(f"   预测长度: {pred_len} 天")
    print(f"   预测区间: {y_dates[0].strftime('%Y-%m-%d')} 至 {y_dates[-1].strftime('%Y-%m-%d')}")
    print()
    
    # ==================== 6. 执行预测 ====================
    print("6. 执行预测...")
    print("-" * 70)
    
    try:
        pred_df = predictor.predict(
            df=x_df,
            x_timestamp=x_ts,
            y_timestamp=y_ts,
            pred_len=pred_len,
            T=1.0,        # Temperature
            top_p=0.9,    # Top-p sampling
            sample_count=1,
            verbose=True
        )
        
        print(f"\n   ✅ 预测完成！")
        
    except Exception as e:
        print(f"\n   ❌ 预测失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    print("-" * 70)
    print()
    
    # ==================== 7. 显示预测结果 ====================
    print("7. 预测结果详情:")
    print("=" * 70)
    print()
    
    # 格式化输出
    print(f"{'日期':<12} {'开盘价':>10} {'最高价':>10} {'最低价':>10} {'收盘价':>10} {'成交量':>12} {'成交额':>14}")
    print("-" * 70)
    
    for idx, row in pred_df.iterrows():
        date_str = idx.strftime('%Y-%m-%d')
        open_price = row['open']
        high_price = row['high']
        low_price = row['low']
        close_price = row['close']
        volume = row['volume']
        amount = row['amount']
        
        print(f"{date_str:<12} {open_price:>10.2f} {high_price:>10.2f} {low_price:>10.2f} {close_price:>10.2f} {volume:>12.0f} {amount:>14.0f}")
    
    print("-" * 70)
    print()
    
    # ==================== 8. 统计分析 ====================
    print("8. 统计分析:")
    print("=" * 70)
    print()
    
    # 价格统计
    avg_close = pred_df['close'].mean()
    max_close = pred_df['close'].max()
    min_close = pred_df['close'].min()
    price_range = max_close - min_close
    
    last_close = df['close'].iloc[-1]
    price_change = avg_close - last_close
    price_change_pct = (price_change / last_close) * 100
    
    print(f"📊 价格统计:")
    print(f"   平均收盘价: {avg_close:.2f}")
    print(f"   最高收盘价: {max_close:.2f}")
    print(f"   最低收盘价: {min_close:.2f}")
    print(f"   价格波动范围: {price_range:.2f} ({price_range/avg_close*100:.2f}%)")
    print()
    
    print(f"📈 趋势分析:")
    print(f"   当前收盘价: {last_close:.2f}")
    print(f"   预测均价: {avg_close:.2f}")
    print(f"   预期变化: {price_change:+.2f} ({price_change_pct:+.2f}%)")
    
    if price_change > 0:
        trend = "📈 看涨"
    elif price_change < 0:
        trend = "📉 看跌"
    else:
        trend = "➡️ 平稳"
    
    print(f"   整体趋势: {trend}")
    print()
    
    # 成交量统计
    avg_volume = pred_df['volume'].mean()
    max_volume = pred_df['volume'].max()
    min_volume = pred_df['volume'].min()
    
    last_volume = df['volume'].iloc[-1]
    volume_change_pct = ((avg_volume - last_volume) / last_volume) * 100
    
    print(f"💰 成交量统计:")
    print(f"   平均成交量: {avg_volume:,.0f}")
    print(f"   最高成交量: {max_volume:,.0f}")
    print(f"   最低成交量: {min_volume:,.0f}")
    print(f"   较近期变化: {volume_change_pct:+.2f}%")
    print()
    
    # 波动性分析
    daily_returns = pred_df['close'].pct_change().dropna()
    volatility = daily_returns.std() * 100
    
    print(f"📊 波动性分析:")
    print(f"   日均收益率: {daily_returns.mean()*100:+.2f}%")
    print(f"   波动率: {volatility:.2f}%")
    print()
    
    print("=" * 70)
    print()
    
    # ==================== 9. 保存结果 ====================
    print("9. 保存预测结果...")
    
    output_dir = "./outputs/predictions"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 保存完整预测
    pred_file = f"{output_dir}/ths_300033_finetuned_pred_{timestamp}.csv"
    pred_df.to_csv(pred_file)
    
    # 保存摘要
    summary = {
        'prediction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'model': 'Kronos-base-finetuned',
        'stock_code': '300033',
        'current_close': float(last_close),
        'predicted_avg_close': float(avg_close),
        'price_change': float(price_change),
        'price_change_pct': float(price_change_pct),
        'trend': 'bullish' if price_change > 0 else 'bearish' if price_change < 0 else 'neutral',
        'volatility': float(volatility),
        'avg_volume': float(avg_volume),
    }
    
    import json
    summary_file = f"{output_dir}/ths_300033_finetuned_summary_{timestamp}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ 预测数据: {pred_file}")
    print(f"   ✅ 摘要信息: {summary_file}")
    print()
    
    # ==================== 10. 风险提示 ====================
    print("=" * 70)
    print("⚠️  重要提示:")
    print("=" * 70)
    print()
    print("1. 本预测基于 AI 模型，仅供参考和学习")
    print("2. 股市有风险，投资需谨慎")
    print("3. 预测结果不构成投资建议")
    print("4. 请结合基本面、技术面等多方面因素综合判断")
    print("5. 市场受多种因素影响，存在不确定性")
    print()
    print("=" * 70)
    print()
    print("🎉 预测完成！")
    print()


if __name__ == "__main__":
    predict_with_finetuned_model()
