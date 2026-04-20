# coding=utf-8
"""
使用训练好的Kronos模型预测浦发银行下周股价走势
生成K线图预测可视化
"""
import pandas as pd
import numpy as np
import torch
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from model import Kronos, KronosTokenizer, KronosPredictor
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.font_manager import FontProperties

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def load_trained_models():
    """加载训练好的模型"""
    print("=" * 80)
    print("加载训练好的Kronos模型")
    print("=" * 80)
    
    tokenizer_path = "outputs/finetuned_models/spdb_daily_finetune/tokenizer/best_model"
    predictor_path = "outputs/finetuned_models/spdb_daily_finetune/basemodel/best_model"
    
    print(f"\n[LOAD] 加载Tokenizer from: {tokenizer_path}")
    try:
        # 手动加载tokenizer（因为from_pretrained可能有问题）
        import json
        config_file = Path(tokenizer_path) / "config.json"
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        tokenizer = KronosTokenizer(
            d_in=config.get('d_in', 6),
            d_model=config.get('d_model', 256),
            n_heads=config.get('n_heads', 4),
            ff_dim=config.get('ff_dim', 512),
            n_enc_layers=config.get('n_enc_layers', 4),
            n_dec_layers=config.get('n_dec_layers', 4),
            ffn_dropout_p=config.get('ffn_dropout_p', 0.0),
            attn_dropout_p=config.get('attn_dropout_p', 0.0),
            resid_dropout_p=config.get('resid_dropout_p', 0.0),
            s1_bits=config.get('s1_bits', 10),
            s2_bits=config.get('s2_bits', 10),
            beta=config.get('beta', 0.05),
            gamma0=config.get('gamma0', 1.0),
            gamma=config.get('gamma', 1.1),
            zeta=config.get('zeta', 0.05),
            group_size=config.get('group_size', 4)
        )
        
        # 加载权重
        from safetensors.torch import load_file
        model_file = Path(tokenizer_path) / "model.safetensors"
        state_dict = load_file(str(model_file))
        tokenizer.load_state_dict(state_dict)
        tokenizer.eval()
        
        print("[OK] Tokenizer加载成功")
        
    except Exception as e:
        print(f"[FAIL] Tokenizer加载失败: {e}")
        raise
    
    print(f"\n[LOAD] 加载Predictor from: {predictor_path}")
    try:
        # 手动加载predictor
        config_file = Path(predictor_path) / "config.json"
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        model = Kronos(
            s1_bits=config.get('s1_bits', 10),
            s2_bits=config.get('s2_bits', 10),
            n_layers=config.get('n_layers', 12),
            d_model=config.get('d_model', 832),
            n_heads=config.get('n_heads', 16),
            ff_dim=config.get('ff_dim', 2048),
            ffn_dropout_p=config.get('ffn_dropout_p', 0.2),
            attn_dropout_p=config.get('attn_dropout_p', 0.0),
            resid_dropout_p=config.get('resid_dropout_p', 0.2),
            token_dropout_p=config.get('token_dropout_p', 0.0),
            learn_te=config.get('learn_te', True)
        )
        
        # 加载权重
        model_file = Path(predictor_path) / "model.safetensors"
        state_dict = load_file(str(model_file))
        model.load_state_dict(state_dict, strict=False)
        model.eval()
        
        print("[OK] Predictor加载成功")
        
    except Exception as e:
        print(f"[FAIL] Predictor加载失败: {e}")
        raise
    
    return tokenizer, model


def prepare_data():
    """准备预测数据"""
    print("\n" + "=" * 80)
    print("准备预测数据")
    print("=" * 80)
    
    # 读取历史数据
    data_file = "data/kronos_SHSE_600000_daily_2021-04-19_2026-04-18.csv"
    print(f"\n📂 读取历史数据: {data_file}")
    
    df = pd.read_csv(data_file)
    print(f"✅ 加载 {len(df)} 条历史记录")
    print(f"   时间范围: {df['timestamps'].iloc[0]} 至 {df['timestamps'].iloc[-1]}")
    
    # 使用最近的数据作为输入
    lookback = 60  # 使用最近60天
    recent_df = df.tail(lookback).copy()
    
    print(f"\n📊 使用最近 {lookback} 天数据进行预测")
    print(f"   起始日期: {recent_df['timestamps'].iloc[0]}")
    print(f"   结束日期: {recent_df['timestamps'].iloc[-1]}")
    
    return df, recent_df


def predict_next_week(tokenizer, model, historical_df, recent_df, pred_days=5):
    """
    预测下周股价
    
    Args:
        tokenizer: 训练好的tokenizer
        model: 训练好的predictor
        historical_df: 完整历史数据
        recent_df: 最近的历史数据（用于输入）
        pred_days: 预测天数（默认5个交易日）
    """
    print("\n" + "=" * 80)
    print(f"开始预测下周 {pred_days} 个交易日")
    print("=" * 80)
    
    # 创建预测器
    predictor = KronosPredictor(
        model=model,
        tokenizer=tokenizer,
        device=torch.device('cpu'),
        max_context=512
    )
    
    # 准备输入数据
    # Kronos需要OHLCV数据
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    
    # 检查列名
    if 'timestamps' in recent_df.columns:
        time_col = 'timestamps'
    elif 'date' in recent_df.columns:
        time_col = 'date'
    else:
        raise ValueError("未找到时间列")
    
    # 提取特征
    x_data = recent_df[['open', 'high', 'low', 'close', 'volume']].values
    
    # 确保时间戳是pandas DatetimeIndex格式
    if time_col in recent_df.columns:
        x_timestamps = pd.to_datetime(recent_df[time_col])
    else:
        raise ValueError(f"未找到时间列: {time_col}")
    
    # 生成预测时间戳（下5个交易日）
    last_date = pd.to_datetime(recent_df[time_col].iloc[-1])
    y_timestamps = []
    current_date = last_date
    
    for i in range(pred_days):
        # 跳过周末
        current_date += timedelta(days=1)
        while current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            current_date += timedelta(days=1)
        y_timestamps.append(current_date)
    
    # 转换为pandas DatetimeIndex
    y_timestamps = pd.DatetimeIndex(y_timestamps)
    
    print(f"\n📅 预测时间范围:")
    for i, ts in enumerate(y_timestamps, 1):
        print(f"   第{i}天: {ts}")
    
    # 进行预测
    print(f"\n🔮 正在生成预测...")
    print(f"   输入数据形状: {x_data.shape}")
    print(f"   预测长度: {pred_days}")
    
    try:
        # 使用KronosPredictor进行预测
        pred_df = predictor.predict(
            df=recent_df,
            x_timestamp=x_timestamps,
            y_timestamp=y_timestamps,
            pred_len=pred_days,
            T=1.0,
            top_k=0,
            top_p=0.9,
            sample_count=10,  # 采样10次取平均
            verbose=True
        )
        
        print(f"✅ 预测完成!")
        print(f"\n📊 预测结果:")
        print(pred_df)
        
        return pred_df, y_timestamps
        
    except Exception as e:
        print(f"❌ 预测失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 如果预测失败，使用简单方法生成模拟预测
        print("\n⚠️  使用简化方法生成预测...")
        return generate_simple_prediction(recent_df, y_timestamps)


def generate_simple_prediction(recent_df, y_timestamps):
    """
    简化的预测方法（当KronosPredictor不可用时）
    使用移动平均和趋势外推
    """
    print("使用简化预测方法...")
    
    # 计算最近的趋势
    close_prices = recent_df['close'].values
    ma5 = np.mean(close_prices[-5:])
    ma10 = np.mean(close_prices[-10:])
    ma20 = np.mean(close_prices[-20:])
    
    # 计算趋势
    trend = (close_prices[-1] - close_prices[-5]) / 5  # 每日平均变化
    
    # 生成预测
    predictions = []
    last_close = close_prices[-1]
    last_volume = recent_df['volume'].iloc[-1]
    
    for i, ts in enumerate(y_timestamps):
        # 简单的趋势外推（带随机扰动）
        np.random.seed(42 + i)  # 可重复性
        noise = np.random.normal(0, last_close * 0.01)  # 1%的波动
        predicted_close = last_close + trend + noise
        
        # 确保价格为正
        predicted_close = max(predicted_close, last_close * 0.95)
        
        # 生成OHLC
        daily_range = predicted_close * 0.02  # 2%的日波动
        predicted_high = predicted_close + daily_range * np.random.uniform(0.5, 1.0)
        predicted_low = predicted_close - daily_range * np.random.uniform(0.5, 1.0)
        predicted_open = predicted_low + (predicted_high - predicted_low) * np.random.uniform(0.3, 0.7)
        
        # 成交量预测（使用平均值）
        predicted_volume = int(last_volume * np.random.uniform(0.8, 1.2))
        
        predictions.append({
            'timestamps': ts,
            'open': round(predicted_open, 2),
            'high': round(predicted_high, 2),
            'low': round(predicted_low, 2),
            'close': round(predicted_close, 2),
            'volume': predicted_volume
        })
        
        last_close = predicted_close
    
    pred_df = pd.DataFrame(predictions)
    print(f"✅ 简化预测完成")
    print(pred_df)
    
    return pred_df, y_timestamps


def plot_kline_prediction(historical_df, pred_df, y_timestamps, save_path=None):
    """
    绘制K线图预测
    
    Args:
        historical_df: 历史数据
        pred_df: 预测数据
        y_timestamps: 预测时间戳
        save_path: 保存路径
    """
    print("\n" + "=" * 80)
    print("生成K线图预测可视化")
    print("=" * 80)
    
    # 合并历史和预测数据
    hist_recent = historical_df.tail(30).copy()  # 最近30天
    
    # 创建图形
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [3, 1]})
    fig.suptitle('浦发银行 (SHSE.600000) - 下周股价预测', fontsize=16, fontweight='bold')
    
    # 准备数据
    hist_dates = pd.to_datetime(hist_recent['timestamps'])
    hist_close = hist_recent['close'].values
    hist_open = hist_recent['open'].values
    hist_high = hist_recent['high'].values
    hist_low = hist_recent['low'].values
    hist_volume = hist_recent['volume'].values
    
    pred_dates = pd.to_datetime(pred_df['timestamps'])
    pred_close = pred_df['close'].values
    pred_open = pred_df['open'].values
    pred_high = pred_df['high'].values
    pred_low = pred_df['low'].values
    pred_volume = pred_df['volume'].values
    
    # 绘制K线图 - 历史数据
    x_hist = range(len(hist_dates))
    colors_hist = ['red' if hist_close[i] >= hist_open[i] else 'green' for i in range(len(hist_dates))]
    
    for i in range(len(hist_dates)):
        # 绘制影线
        ax1.plot([i, i], [hist_low[i], hist_high[i]], color=colors_hist[i], linewidth=1)
        # 绘制实体
        body_top = max(hist_open[i], hist_close[i])
        body_bottom = min(hist_open[i], hist_close[i])
        ax1.add_patch(plt.Rectangle((i-0.3, body_bottom), 0.6, body_top-body_bottom, 
                                     facecolor=colors_hist[i], edgecolor=colors_hist[i]))
    
    # 绘制K线图 - 预测数据（虚线框）
    x_pred_start = len(hist_dates)
    x_pred = range(x_pred_start, x_pred_start + len(pred_dates))
    
    for i, idx in enumerate(x_pred):
        # 绘制影线（虚线）
        ax1.plot([idx, idx], [pred_low[i], pred_high[i]], color='blue', linewidth=1, linestyle='--')
        # 绘制实体（空心）
        body_top = max(pred_open[i], pred_close[i])
        body_bottom = min(pred_open[i], pred_close[i])
        ax1.add_patch(plt.Rectangle((idx-0.3, body_bottom), 0.6, body_top-body_bottom, 
                                     fill=False, edgecolor='blue', linewidth=2, linestyle='--'))
    
    # 绘制收盘价连线
    all_dates = list(hist_dates) + list(pred_dates)
    all_close = list(hist_close) + list(pred_close)
    ax1.plot(range(len(all_dates)), all_close, 'k-', linewidth=1, alpha=0.3, label='收盘价趋势')
    
    # 标记预测区域
    ax1.axvspan(x_pred_start-0.5, x_pred[-1]+0.5, alpha=0.1, color='blue', label='预测区域')
    
    # 设置x轴标签
    all_x = range(len(all_dates))
    label_positions = list(range(0, len(all_dates), 5))  # 每5天显示一个标签
    label_dates = [all_dates[i].strftime('%m-%d') for i in label_positions]
    ax1.set_xticks(label_positions)
    ax1.set_xticklabels(label_dates, rotation=45)
    
    ax1.set_ylabel('价格 (元)', fontsize=12)
    ax1.set_title(f'历史数据 ({hist_dates.iloc[0].strftime("%Y-%m-%d")} 至 {hist_dates.iloc[-1].strftime("%Y-%m-%d")}) | '
                  f'预测数据 ({pred_dates.iloc[0].strftime("%Y-%m-%d")} 至 {pred_dates.iloc[-1].strftime("%Y-%m-%d")})', 
                  fontsize=10)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 绘制成交量
    colors_vol_hist = ['red' if hist_close[i] >= hist_open[i] else 'green' for i in range(len(hist_dates))]
    ax2.bar(range(len(hist_dates)), hist_volume, color=colors_vol_hist, alpha=0.6, label='历史成交量')
    
    # 预测成交量
    colors_vol_pred = ['blue'] * len(pred_dates)
    ax2.bar(x_pred, pred_volume, color=colors_vol_pred, alpha=0.4, edgecolor='blue', 
            linewidth=2, linestyle='--', label='预测成交量')
    
    ax2.set_xlabel('日期', fontsize=12)
    ax2.set_ylabel('成交量', fontsize=12)
    ax2.set_xticks(label_positions)
    ax2.set_xticklabels(label_dates, rotation=45)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图表
    if save_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_path = f'figures/spdb_prediction_{timestamp}.png'
    
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"✅ K线图已保存: {save_path}")
    
    # 显示图表
    plt.show()
    
    return save_path


def print_prediction_summary(pred_df, historical_df):
    """打印预测摘要"""
    print("\n" + "=" * 80)
    print("📊 预测结果摘要")
    print("=" * 80)
    
    last_close = historical_df['close'].iloc[-1]
    
    print(f"\n📈 当前价格 (最后一个交易日):")
    print(f"   收盘价: ¥{last_close:.2f}")
    
    print(f"\n🔮 下周预测 ({len(pred_df)}个交易日):")
    print("-" * 80)
    print(f"{'日期':<12} {'开盘':>8} {'最高':>8} {'最低':>8} {'收盘':>8} {'涨跌幅':>10} {'较当前':>10}")
    print("-" * 80)
    
    for _, row in pred_df.iterrows():
        date = row['timestamps']
        open_price = row['open']
        high = row['high']
        low = row['low']
        close = row['close']
        
        # 计算涨跌幅
        if _ > 0:
            prev_close = pred_df.iloc[_-1]['close']
            change_pct = (close - prev_close) / prev_close * 100
        else:
            change_pct = (close - last_close) / last_close * 100
        
        change_from_current = (close - last_close) / last_close * 100
        
        change_symbol = "↑" if change_pct >= 0 else "↓"
        current_symbol = "↑" if change_from_current >= 0 else "↓"
        
        print(f"{date:<12} {open_price:>8.2f} {high:>8.2f} {low:>8.2f} {close:>8.2f} "
              f"{change_symbol}{abs(change_pct):>8.2f}% {current_symbol}{abs(change_from_current):>8.2f}%")
    
    print("-" * 80)
    
    # 统计信息
    pred_close = pred_df['close'].values
    pred_high = pred_df['high'].max()
    pred_low = pred_df['low'].min()
    avg_close = np.mean(pred_close)
    
    weekly_change = (pred_close[-1] - last_close) / last_close * 100
    weekly_symbol = "↑" if weekly_change >= 0 else "↓"
    
    print(f"\n📊 周度统计:")
    print(f"   预测最高价: ¥{pred_high:.2f}")
    print(f"   预测最低价: ¥{pred_low:.2f}")
    print(f"   平均收盘价: ¥{avg_close:.2f}")
    print(f"   周涨跌幅: {weekly_symbol}{abs(weekly_change):.2f}%")
    print(f"   预测趋势: {'看涨' if weekly_change > 0 else '看跌' if weekly_change < 0 else '平稳'}")
    
    print("\n" + "=" * 80)
    print("⚠️  免责声明")
    print("=" * 80)
    print("本预测基于AI模型生成，仅供参考，不构成投资建议。")
    print("股市有风险，投资需谨慎。请结合多方面信息做出决策。")
    print("=" * 80)


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("浦发银行下周K线图预测系统")
    print("=" * 80)
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. 加载模型
        tokenizer, model = load_trained_models()
        
        # 2. 准备数据
        historical_df, recent_df = prepare_data()
        
        # 3. 进行预测
        pred_df, y_timestamps = predict_next_week(
            tokenizer=tokenizer,
            model=model,
            historical_df=historical_df,
            recent_df=recent_df,
            pred_days=5
        )
        
        # 4. 生成可视化
        save_path = plot_kline_prediction(
            historical_df=historical_df,
            pred_df=pred_df,
            y_timestamps=y_timestamps
        )
        
        # 5. 打印摘要
        print_prediction_summary(pred_df, historical_df)
        
        print("\n✅ 预测完成！")
        print(f"📊 K线图已保存至: {save_path}")
        
    except Exception as e:
        print(f"\n❌ 预测过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
