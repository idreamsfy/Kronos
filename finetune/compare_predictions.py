#!/usr/bin/env python
"""
对比原始模型和微调模型的预测效果
"""

import os
import sys
import torch
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from model.kronos import Kronos, KronosTokenizer, KronosPredictor


def load_data():
    """加载同花顺数据"""
    data_file = "./data/raw/akshare/daily_300033.csv"
    
    if not os.path.exists(data_file):
        print(f"❌ 文件不存在: {data_file}")
        return None
    
    df = pd.read_csv(data_file)
    if 'timestamps' not in df.columns and 'date' in df.columns:
        df['timestamps'] = pd.to_datetime(df['date'])
    elif 'timestamps' in df.columns:
        df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    df = df.sort_values('timestamps').reset_index(drop=True)
    print(f"✅ 数据加载: {len(df)} 行")
    print(f"   范围: {df['timestamps'].min()} 到 {df['timestamps'].max()}")
    
    return df


def compare_predictions():
    """对比预测效果"""
    
    print("=" * 70)
    print("🔍 对比原始模型 vs 微调模型预测效果")
    print("=" * 70)
    print()
    
    # 检查微调模型是否存在
    finetuned_model_path = "./outputs/models/finetune_300033_base_real/best_model"
    
    if not os.path.exists(finetuned_model_path):
        print("⚠️  微调模型尚未完成训练")
        print(f"   路径: {finetuned_model_path}")
        print()
        print("💡 建议:")
        print("   1. 等待训练完成")
        print("   2. 或手动停止当前训练并保存检查点")
        print()
        
        # 检查是否有检查点
        checkpoint_dir = "./outputs/models/finetune_300033_base_real"
        if os.path.exists(checkpoint_dir):
            checkpoints = [d for d in os.listdir(checkpoint_dir) if d.startswith('checkpoint_epoch_')]
            if checkpoints:
                print(f"📁 找到 {len(checkpoints)} 个检查点:")
                for cp in sorted(checkpoints):
                    print(f"   - {cp}")
                print()
                print("您可以使用最新的检查点进行对比测试")
        return
    
    # 加载数据
    print("1. 加载数据...")
    df = load_data()
    if df is None:
        return
    print()
    
    # 设备选择
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f"2. 使用设备: {device}")
    print()
    
    # 加载 Tokenizer
    print("3. 加载 Tokenizer...")
    tokenizer_path = "./model/pretrained_models/Kronos-Tokenizer-base"
    tokenizer = KronosTokenizer.from_pretrained(tokenizer_path)
    print(f"   ✅ Tokenizer 加载成功")
    print()
    
    # 加载原始模型
    print("4. 加载原始模型...")
    original_model_path = "./model/pretrained_models/Kronos-base"
    model_orig = Kronos.from_pretrained(original_model_path)
    model_orig.to(device)
    predictor_orig = KronosPredictor(model_orig, tokenizer, device=device, max_context=512)
    print(f"   ✅ 原始模型加载成功")
    print()
    
    # 加载微调模型
    print("5. 加载微调模型...")
    try:
        # 从原始模型复制架构，然后加载微调权重
        model_fine = Kronos.from_pretrained(original_model_path)
        
        # 加载微调后的权重
        import safetensors.torch
        state_dict = safetensors.torch.load_file(f"{finetuned_model_path}/model.safetensors")
        model_fine.load_state_dict(state_dict, strict=False)
        
        model_fine.to(device)
        predictor_fine = KronosPredictor(model_fine, tokenizer, device=device, max_context=512)
        print(f"   ✅ 微调模型加载成功")
    except Exception as e:
        print(f"   ❌ 微调模型加载失败: {e}")
        print(f"   💡 尝试使用最新检查点...")
        
        # 查找最新检查点
        checkpoint_dir = "./outputs/models/finetune_300033_base_real"
        if os.path.exists(checkpoint_dir):
            checkpoints = [d for d in os.listdir(checkpoint_dir) if d.startswith('checkpoint_epoch_')]
            if checkpoints:
                latest_checkpoint = sorted(checkpoints)[-1]
                checkpoint_path = os.path.join(checkpoint_dir, latest_checkpoint)
                print(f"   使用检查点: {latest_checkpoint}")
                
                try:
                    model_fine = Kronos.from_pretrained(original_model_path)
                    state_dict = safetensors.torch.load_file(f"{checkpoint_path}/model.safetensors")
                    model_fine.load_state_dict(state_dict, strict=False)
                    model_fine.to(device)
                    predictor_fine = KronosPredictor(model_fine, tokenizer, device=device, max_context=512)
                    print(f"   ✅ 检查点模型加载成功")
                except Exception as e2:
                    print(f"   ❌ 检查点加载也失败: {e2}")
                    return
            else:
                return
        else:
            return
    print()
    
    # 准备预测数据（使用最后 100 天）
    print("6. 准备预测数据...")
    lookback = 100
    pred_len = 20
    
    x_df = df.iloc[-lookback:][['open', 'high', 'low', 'close', 'volume', 'amount']].copy()
    x_ts = pd.Series(pd.to_datetime(df.iloc[-lookback:]['timestamps']))
    
    # 生成未来时间戳
    last_date = x_ts.iloc[-1]
    y_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=pred_len, freq='B')
    y_ts = pd.Series(y_dates)
    
    print(f"   输入数据: {lookback} 天")
    print(f"   预测长度: {pred_len} 天")
    print(f"   起始日期: {y_dates[0].strftime('%Y-%m-%d')}")
    print(f"   结束日期: {y_dates[-1].strftime('%Y-%m-%d')}")
    print()
    
    # 执行预测
    print("7. 执行预测...")
    print("-" * 70)
    
    # 原始模型预测
    print("   📊 原始模型预测中...")
    try:
        pred_orig = predictor_orig.predict(
            df=x_df,
            x_timestamp=x_ts,
            y_timestamp=y_ts,
            pred_len=pred_len,
            T=1.0,
            top_p=0.9,
            sample_count=1,
            verbose=False
        )
        print(f"   ✅ 原始模型预测完成")
    except Exception as e:
        print(f"   ❌ 原始模型预测失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    
    # 微调模型预测
    print("   📊 微调模型预测中...")
    try:
        pred_fine = predictor_fine.predict(
            df=x_df,
            x_timestamp=x_ts,
            y_timestamp=y_ts,
            pred_len=pred_len,
            T=1.0,
            top_p=0.9,
            sample_count=1,
            verbose=False
        )
        print(f"   ✅ 微调模型预测完成")
    except Exception as e:
        print(f"   ❌ 微调模型预测失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    print("-" * 70)
    print()
    
    # 对比结果
    print("8. 对比分析...")
    print("=" * 70)
    print()
    
    # 显示前 5 天预测
    print("📈 预测结果对比（前 5 天）:")
    print("-" * 70)
    print(f"{'日期':<12} {'原始-开盘':>10} {'微调-开盘':>10} {'原始-收盘':>10} {'微调-收盘':>10}")
    print("-" * 70)
    
    for i in range(min(5, len(pred_orig))):
        date_str = pred_orig.index[i].strftime('%Y-%m-%d')
        orig_open = pred_orig.iloc[i]['open']
        fine_open = pred_fine.iloc[i]['open']
        orig_close = pred_orig.iloc[i]['close']
        fine_close = pred_fine.iloc[i]['close']
        
        print(f"{date_str:<12} {orig_open:>10.2f} {fine_open:>10.2f} {orig_close:>10.2f} {fine_close:>10.2f}")
    
    print("-" * 70)
    print()
    
    # 统计差异
    print("📊 统计分析:")
    print("-" * 70)
    
    open_diff = (pred_fine['open'] - pred_orig['open']).abs().mean()
    close_diff = (pred_fine['close'] - pred_orig['close']).abs().mean()
    high_diff = (pred_fine['high'] - pred_orig['high']).abs().mean()
    low_diff = (pred_fine['low'] - pred_orig['low']).abs().mean()
    volume_diff = (pred_fine['volume'] - pred_orig['volume']).abs().mean()
    
    print(f"平均差异:")
    print(f"  开盘价: {open_diff:.2f} ({open_diff/pred_orig['open'].mean()*100:.2f}%)")
    print(f"  收盘价: {close_diff:.2f} ({close_diff/pred_orig['close'].mean()*100:.2f}%)")
    print(f"  最高价: {high_diff:.2f} ({high_diff/pred_orig['high'].mean()*100:.2f}%)")
    print(f"  最低价: {low_diff:.2f} ({low_diff/pred_orig['low'].mean()*100:.2f}%)")
    print(f"  成交量: {volume_diff:.0f} ({volume_diff/pred_orig['volume'].mean()*100:.2f}%)")
    print("-" * 70)
    print()
    
    # 价格范围对比
    print("💰 价格范围对比:")
    print("-" * 70)
    print(f"{'指标':<10} {'原始模型':>12} {'微调模型':>12} {'差异':>12}")
    print("-" * 70)
    
    orig_price_range = pred_orig['close'].max() - pred_orig['close'].min()
    fine_price_range = pred_fine['close'].max() - pred_fine['close'].min()
    price_range_diff = fine_price_range - orig_price_range
    
    print(f"{'收盘价范围':<10} {orig_price_range:>12.2f} {fine_price_range:>12.2f} {price_range_diff:>+12.2f}")
    
    orig_vol_mean = pred_orig['volume'].mean()
    fine_vol_mean = pred_fine['volume'].mean()
    vol_diff = fine_vol_mean - orig_vol_mean
    
    print(f"{'平均成交量':<10} {orig_vol_mean:>12.0f} {fine_vol_mean:>12.0f} {vol_diff:>+12.0f}")
    print("-" * 70)
    print()
    
    # 保存结果
    print("9. 保存对比结果...")
    output_dir = "./outputs/predictions"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 保存完整预测
    pred_orig.to_csv(f"{output_dir}/comparison_original_{timestamp}.csv")
    pred_fine.to_csv(f"{output_dir}/comparison_finetuned_{timestamp}.csv")
    
    # 保存对比摘要
    comparison_summary = pd.DataFrame({
        'date': pred_orig.index,
        'original_open': pred_orig['open'],
        'finetuned_open': pred_fine['open'],
        'original_close': pred_orig['close'],
        'finetuned_close': pred_fine['close'],
        'original_high': pred_orig['high'],
        'finetuned_high': pred_fine['high'],
        'original_low': pred_orig['low'],
        'finetuned_low': pred_fine['low'],
        'original_volume': pred_orig['volume'],
        'finetuned_volume': pred_fine['volume'],
    })
    comparison_summary.to_csv(f"{output_dir}/comparison_summary_{timestamp}.csv", index=False)
    
    print(f"   ✅ 结果已保存:")
    print(f"      - {output_dir}/comparison_original_{timestamp}.csv")
    print(f"      - {output_dir}/comparison_finetuned_{timestamp}.csv")
    print(f"      - {output_dir}/comparison_summary_{timestamp}.csv")
    print()
    
    # 可视化
    print("10. 生成可视化图表...")
    try:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 收盘价对比
        ax1 = axes[0, 0]
        ax1.plot(pred_orig.index, pred_orig['close'], 'b-o', label='Original', markersize=4)
        ax1.plot(pred_fine.index, pred_fine['close'], 'r-s', label='Finetuned', markersize=4)
        ax1.set_title('Close Price Comparison', fontsize=12)
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # 开盘价对比
        ax2 = axes[0, 1]
        ax2.plot(pred_orig.index, pred_orig['open'], 'b-o', label='Original', markersize=4)
        ax2.plot(pred_fine.index, pred_fine['open'], 'r-s', label='Finetuned', markersize=4)
        ax2.set_title('Open Price Comparison', fontsize=12)
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Price')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        # 成交量对比
        ax3 = axes[1, 0]
        ax3.bar(range(len(pred_orig)), pred_orig['volume'], alpha=0.5, label='Original', color='blue')
        ax3.bar(range(len(pred_fine)), pred_fine['volume'], alpha=0.5, label='Finetuned', color='red')
        ax3.set_title('Volume Comparison', fontsize=12)
        ax3.set_xlabel('Day')
        ax3.set_ylabel('Volume')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 差异图
        ax4 = axes[1, 1]
        close_diff_series = pred_fine['close'] - pred_orig['close']
        colors = ['green' if x >= 0 else 'red' for x in close_diff_series]
        ax4.bar(range(len(close_diff_series)), close_diff_series, color=colors, alpha=0.7)
        ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax4.set_title('Close Price Difference (Finetuned - Original)', fontsize=12)
        ax4.set_xlabel('Day')
        ax4.set_ylabel('Difference')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/comparison_plot_{timestamp}.png", dpi=150, bbox_inches='tight')
        print(f"   ✅ 图表已保存: {output_dir}/comparison_plot_{timestamp}.png")
    except Exception as e:
        print(f"   ⚠️  图表生成失败: {e}")
    
    print()
    print("=" * 70)
    print("🎉 对比分析完成！")
    print("=" * 70)
    print()
    print("💡 下一步:")
    print("   1. 查看保存的 CSV 文件了解详细数据")
    print("   2. 查看生成的对比图表")
    print("   3. 根据结果调整模型参数")
    print()


if __name__ == "__main__":
    compare_predictions()
