#!/usr/bin/env python
"""
使用微调后的5分钟K线模型预测同花顺 (300033) 未来3天走势
基于5分钟粒度进行高频预测
"""

import os
import sys
import torch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib

# 设置中文字体支持
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from model.kronos import Kronos, KronosTokenizer, KronosPredictor


def predict_3days_5min():
    """使用5分钟模型预测未来3天"""
    
    print("=" * 70)
    print("🔮 使用5分钟微调模型预测同花顺 (300033) 未来3天走势")
    print("=" * 70)
    print()
    
    # ==================== 1. 加载最新数据 ====================
    print("1. 加载最新5分钟K线数据...")
    data_file = "./data/raw/futu/5min_300033.csv"
    
    if not os.path.exists(data_file):
        print(f"❌ 数据文件不存在: {data_file}")
        return
    
    df = pd.read_csv(data_file)
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    df = df.sort_values('timestamps').reset_index(drop=True)
    
    print(f"   ✅ 数据加载: {len(df):,} 条记录")
    print(f"   最新时间: {df['timestamps'].max()}")
    print(f"   最新收盘价: ¥{df['close'].iloc[-1]:.2f}")
    print()
    
    # ==================== 2. 设备选择 ====================
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f"2. 使用设备: {device}")
    print()
    
    # ==================== 3. 加载微调模型 ====================
    print("3. 加载微调后的5分钟模型...")
    model_path = "./outputs/models/finetune_300033_5min_base/best_model"
    
    try:
        # 从原始模型加载架构，然后加载微调权重
        original_model_path = "./model/pretrained_models/Kronos-base"
        original_tokenizer_path = "./model/pretrained_models/Kronos-Tokenizer-base"
        
        tokenizer = KronosTokenizer.from_pretrained(original_tokenizer_path)
        model = Kronos.from_pretrained(original_model_path)
        
        # 加载微调后的权重
        import safetensors.torch
        finetuned_weights = f"{model_path}/model.safetensors"
        if os.path.exists(finetuned_weights):
            state_dict = safetensors.torch.load_file(finetuned_weights)
            model.load_state_dict(state_dict, strict=False)
            print(f"   ✅ 微调权重加载成功")
        else:
            print(f"   ⚠️  未找到微调权重，使用原始模型")
        
        tokenizer.to(device)
        model.to(device)
        
        predictor = KronosPredictor(model, tokenizer, device=device, max_context=512)
        print(f"   ✅ 模型准备完成")
        print(f"   参数量: {sum(p.numel() for p in model.parameters()):,}")
    except Exception as e:
        print(f"   ❌ 模型加载失败: {e}")
        print("   提示: 请确保已完成微调训练")
        return
    
    print()
    
    # ==================== 4. 准备预测数据 ====================
    print("4. 准备预测数据...")
    
    # 5分钟预测配置
    lookback = 100  # 使用最近100个5分钟K线 (约8小时)
    pred_len_5min = 144  # 预测144个5分钟 = 3天 (每天48个5分钟)
    
    # 提取最近的看窗数据
    recent_data = df.iloc[-lookback:].copy()
    
    x_df = recent_data[['open', 'high', 'low', 'close', 'volume', 'amount']]
    x_timestamp = recent_data['timestamps']
    
    # 生成未来3天的5分钟时间戳
    last_time = x_timestamp.iloc[-1]
    
    # 生成交易时间的5分钟时间戳
    future_timestamps = []
    current_date = last_time.date() + timedelta(days=1)
    
    days_generated = 0
    while days_generated < 3:
        # 跳过周末
        if current_date.weekday() < 5:  # 周一到周五
            # 上午交易时间: 9:30-11:30
            for hour in range(9, 12):
                for minute in range(0, 60, 5):
                    if hour == 9 and minute < 35:
                        continue
                    if hour == 11 and minute > 30:
                        break
                    ts = pd.Timestamp(current_date).replace(hour=hour, minute=minute)
                    future_timestamps.append(ts)
            
            # 下午交易时间: 13:00-15:00
            for hour in range(13, 15):
                for minute in range(0, 60, 5):
                    if hour == 15 and minute > 0:
                        break
                    ts = pd.Timestamp(current_date).replace(hour=hour, minute=minute)
                    future_timestamps.append(ts)
            
            days_generated += 1
        
        current_date += timedelta(days=1)
    
    y_timestamp = pd.Series(future_timestamps[:pred_len_5min])
    
    print(f"   历史数据: {lookback} 个5分钟K线 ({df.iloc[-lookback]['timestamps']} 至 {last_time})")
    print(f"   预测长度: {pred_len_5min} 个5分钟K线 (3天)")
    print(f"   预测区间: {y_timestamp.iloc[0]} 至 {y_timestamp.iloc[-1]}")
    print()
    
    # ==================== 5. 执行预测 ====================
    print("5. 执行5分钟粒度预测...")
    print("   提示: 这需要一些时间，请耐心等待...")
    print("-" * 70)
    
    try:
        pred_df = predictor.predict(
            df=x_df,
            x_timestamp=x_timestamp,
            y_timestamp=y_timestamp,
            pred_len=pred_len_5min,
            T=1.0,
            top_p=0.9,
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
    
    # ==================== 6. 显示预测结果 ====================
    print("6. 预测结果详情:")
    print("=" * 70)
    print()
    
    # 按天分组显示
    pred_df['date'] = pred_df.index.date
    pred_df['time'] = pred_df.index.time
    
    for date, day_data in pred_df.groupby('date'):
        print(f"📅 {date} (星期{['一','二','三','四','五','六','日'][date.weekday()]})")
        print(f"   开盘: ¥{day_data['open'].iloc[0]:.2f}")
        print(f"   最高: ¥{day_data['high'].max():.2f}")
        print(f"   最低: ¥{day_data['low'].min():.2f}")
        print(f"   收盘: ¥{day_data['close'].iloc[-1]:.2f}")
        print(f"   成交量: {int(day_data['volume'].sum()):,}")
        print(f"   成交额: ¥{day_data['amount'].sum():,.0f}")
        
        # 计算涨跌幅
        day_change = (day_data['close'].iloc[-1] - day_data['open'].iloc[0]) / day_data['open'].iloc[0] * 100
        print(f"   涨跌幅: {day_change:+.2f}%")
        print()
    
    print("-" * 70)
    print()
    
    # ==================== 7. 统计分析 ====================
    print("7. 整体统计分析:")
    print("=" * 70)
    print()
    
    # 价格统计
    avg_close = pred_df['close'].mean()
    max_close = pred_df['close'].max()
    min_close = pred_df['close'].min()
    price_range = max_close - min_close
    
    last_close = df['close'].iloc[-1]
    total_change = pred_df['close'].iloc[-1] - last_close
    total_change_pct = (total_change / last_close) * 100
    
    print(f"📊 价格统计:")
    print(f"   当前收盘价: ¥{last_close:.2f}")
    print(f"   预测平均价: ¥{avg_close:.2f}")
    print(f"   预测最高价: ¥{max_close:.2f}")
    print(f"   预测最低价: ¥{min_close:.2f}")
    print(f"   价格波动范围: ¥{price_range:.2f} ({price_range/avg_close*100:.2f}%)")
    print()
    
    print(f"📈 趋势分析:")
    print(f"   3天总变化: ¥{total_change:+.2f} ({total_change_pct:+.2f}%)")
    
    if total_change > 0:
        trend = "📈 看涨"
    elif total_change < 0:
        trend = "📉 看跌"
    else:
        trend = "➡️ 平稳"
    
    print(f"   整体趋势: {trend}")
    print()
    
    # 成交量统计
    total_volume = pred_df['volume'].sum()
    avg_daily_volume = total_volume / 3
    
    print(f"💰 成交量统计:")
    print(f"   3天总成交量: {int(total_volume):,}")
    print(f"   日均成交量: {int(avg_daily_volume):,}")
    print()
    
    # 波动性分析
    daily_returns = pred_df['close'].pct_change().dropna()
    volatility = daily_returns.std() * 100
    
    print(f"📊 波动性分析:")
    print(f"   平均收益率: {daily_returns.mean()*100:+.4f}%")
    print(f"   波动率: {volatility:.2f}%")
    print()
    
    print("=" * 70)
    print()
    
    # ==================== 8. 可视化 ====================
    print("8. 生成可视化图表...")
    
    fig, axes = plt.subplots(3, 1, figsize=(16, 12))
    
    # 图1: 收盘价走势
    ax1 = axes[0]
    ax1.plot(pred_df.index, pred_df['close'], linewidth=1.5, color='#2E86AB', label='Predicted Close')
    ax1.axhline(y=last_close, color='red', linestyle='--', alpha=0.5, label=f'Current Price ¥{last_close:.2f}')
    ax1.fill_between(pred_df.index, pred_df['low'], pred_df['high'], alpha=0.2, color='#2E86AB', label='Price Range')
    ax1.set_ylabel('Price (¥)', fontsize=12)
    ax1.set_title('THS 300033 - 3-Day 5-Min Prediction', fontsize=14, fontweight='bold')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=12))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    
    # 图2: 成交量
    ax2 = axes[1]
    colors = ['#2E86AB' if pred_df['close'].iloc[i] >= pred_df['open'].iloc[i] else '#A23B72' 
              for i in range(len(pred_df))]
    ax2.bar(pred_df.index, pred_df['volume'], width=0.003, color=colors, alpha=0.7, label='Volume')
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=12))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
    
    # 图3: 累计收益率
    ax3 = axes[2]
    cumulative_returns = (pred_df['close'] / last_close - 1) * 100
    ax3.plot(pred_df.index, cumulative_returns, linewidth=2, color='#F18F01')
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax3.fill_between(pred_df.index, cumulative_returns, 0, alpha=0.3, color='#F18F01')
    ax3.set_ylabel('Cumulative Return (%)', fontsize=12)
    ax3.set_xlabel('Time', fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax3.xaxis.set_major_locator(mdates.HourLocator(interval=12))
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    
    # 保存图表
    output_dir = "./outputs/predictions"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plot_file = f"{output_dir}/ths_300033_5min_3days_pred_{timestamp}.png"
    plt.savefig(plot_file, dpi=150, bbox_inches='tight')
    print(f"   ✅ 图表已保存: {plot_file}")
    print()
    
    # ==================== 9. 保存预测结果 ====================
    print("9. 保存预测结果...")
    
    csv_file = f"{output_dir}/ths_300033_5min_3days_pred_{timestamp}.csv"
    pred_df.to_csv(csv_file)
    print(f"   ✅ 预测数据已保存: {csv_file}")
    print()
    
    # ==================== 10. 风险提示 ====================
    print("=" * 70)
    print("⚠️  重要提示:")
    print("=" * 70)
    print()
    print("1. 本预测基于5分钟K线微调模型，适合短期交易参考")
    print("2. 5分钟粒度预测波动较大，请谨慎使用")
    print("3. 股市有风险，投资需谨慎")
    print("4. 预测结果不构成投资建议")
    print("5. 建议结合日线级别预测综合判断")
    print()
    print("=" * 70)
    print()
    print("🎉 预测完成！")
    print()


if __name__ == "__main__":
    predict_3days_5min()
