# coding=utf-8
"""
Simple prediction script for SPDB next week K-line chart
Using trained Kronos model with fallback to simple prediction
"""
import pandas as pd
import numpy as np
import torch
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from model import Kronos, KronosTokenizer, KronosPredictor
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt


def load_models():
    """Load trained models"""
    print("=" * 80)
    print("Loading Trained Kronos Models")
    print("=" * 80)
    
    tokenizer_path = "outputs/finetuned_models/spdb_daily_finetune/tokenizer/best_model"
    predictor_path = "outputs/finetuned_models/spdb_daily_finetune/basemodel/best_model"
    
    print(f"\n[1/2] Loading Tokenizer...")
    import json
    from safetensors.torch import load_file
    
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
    
    model_file = Path(tokenizer_path) / "model.safetensors"
    state_dict = load_file(str(model_file))
    tokenizer.load_state_dict(state_dict)
    tokenizer.eval()
    print("[OK] Tokenizer loaded successfully")
    
    print(f"\n[2/2] Loading Predictor...")
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
    
    model_file = Path(predictor_path) / "model.safetensors"
    state_dict = load_file(str(model_file))
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    print("[OK] Predictor loaded successfully")
    
    return tokenizer, model


def predict_and_plot():
    """Main prediction and plotting function"""
    print("\n" + "=" * 80)
    print("SPDB (SHSE.600000) Next Week Prediction")
    print("=" * 80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Load models
    tokenizer, model = load_models()
    
    # Load data
    print("\n" + "=" * 80)
    print("Loading Historical Data")
    print("=" * 80)
    
    data_file = "data/kronos_SHSE_600000_daily_2021-04-19_2026-04-18.csv"
    df = pd.read_csv(data_file)
    print(f"[OK] Loaded {len(df)} records")
    print(f"   Range: {df['timestamps'].iloc[0]} to {df['timestamps'].iloc[-1]}")
    
    # Use recent 60 days
    lookback = 60
    recent_df = df.tail(lookback).copy()
    print(f"\n[INFO] Using last {lookback} days for prediction")
    print(f"   From: {recent_df['timestamps'].iloc[0]}")
    print(f"   To: {recent_df['timestamps'].iloc[-1]}")
    
    # Generate prediction timestamps (next 5 trading days)
    last_date = pd.to_datetime(recent_df['timestamps'].iloc[-1])
    y_timestamps = []
    current_date = last_date
    
    for i in range(5):
        current_date += timedelta(days=1)
        while current_date.weekday() >= 5:
            current_date += timedelta(days=1)
        y_timestamps.append(current_date)
    
    y_timestamps = pd.DatetimeIndex(y_timestamps)
    x_timestamps = pd.to_datetime(recent_df['timestamps'])
    
    print(f"\n" + "=" * 80)
    print("Prediction Period")
    print("=" * 80)
    for i, ts in enumerate(y_timestamps, 1):
        print(f"   Day {i}: {ts.strftime('%Y-%m-%d')}")
    
    # Try Kronos prediction first
    print(f"\n" + "=" * 80)
    print("Running Prediction")
    print("=" * 80)
    
    pred_df = None
    use_kronos = False
    
    try:
        predictor = KronosPredictor(
            model=model,
            tokenizer=tokenizer,
            device=torch.device('cpu'),
            max_context=512
        )
        
        print("[INFO] Attempting Kronos model prediction...")
        pred_df = predictor.predict(
            df=recent_df,
            x_timestamp=x_timestamps,
            y_timestamp=y_timestamps,
            pred_len=5,
            T=1.0,
            top_k=0,
            top_p=0.9,
            sample_count=10,
            verbose=True
        )
        use_kronos = True
        print("[OK] Kronos prediction completed!")
        
    except Exception as e:
        print(f"[WARN] Kronos prediction failed: {e}")
        print("[INFO] Using simplified prediction method...")
        
        # Simplified prediction
        close_prices = recent_df['close'].values
        ma5 = np.mean(close_prices[-5:])
        trend = (close_prices[-1] - close_prices[-5]) / 5
        
        predictions = []
        last_close = close_prices[-1]
        last_volume = recent_df['volume'].iloc[-1]
        
        for i, ts in enumerate(y_timestamps):
            np.random.seed(42 + i)
            noise = np.random.normal(0, last_close * 0.01)
            predicted_close = last_close + trend + noise
            predicted_close = max(predicted_close, last_close * 0.95)
            
            daily_range = predicted_close * 0.02
            predicted_high = predicted_close + daily_range * np.random.uniform(0.5, 1.0)
            predicted_low = predicted_close - daily_range * np.random.uniform(0.5, 1.0)
            predicted_open = predicted_low + (predicted_high - predicted_low) * np.random.uniform(0.3, 0.7)
            predicted_volume = int(last_volume * np.random.uniform(0.8, 1.2))
            
            predictions.append({
                'open': round(predicted_open, 2),
                'high': round(predicted_high, 2),
                'low': round(predicted_low, 2),
                'close': round(predicted_close, 2),
                'volume': predicted_volume
            })
            
            last_close = predicted_close
        
        pred_df = pd.DataFrame(predictions, index=y_timestamps)
        print("[OK] Simplified prediction completed!")
    
    # Print prediction results
    print(f"\n" + "=" * 80)
    print("Prediction Results Summary")
    print("=" * 80)
    
    last_close = df['close'].iloc[-1]
    print(f"\nCurrent Price (Last Trading Day):")
    print(f"   Close: CNY {last_close:.2f}")
    
    print(f"\nNext Week Prediction ({len(pred_df)} trading days):")
    print("-" * 80)
    print(f"{'Date':<12} {'Open':>8} {'High':>8} {'Low':>8} {'Close':>8} {'Change':>10}")
    print("-" * 80)
    
    for idx, row in pred_df.iterrows():
        date = idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx)
        change_pct = (row['close'] - last_close) / last_close * 100
        symbol = "+" if change_pct >= 0 else ""
        print(f"{date:<12} {row['open']:>8.2f} {row['high']:>8.2f} {row['low']:>8.2f} {row['close']:>8.2f} {symbol}{change_pct:>8.2f}%")
    
    print("-" * 80)
    
    # Statistics
    pred_close = pred_df['close'].values
    weekly_change = (pred_close[-1] - last_close) / last_close * 100
    print(f"\nWeekly Statistics:")
    print(f"   Predicted High: CNY {pred_df['high'].max():.2f}")
    print(f"   Predicted Low: CNY {pred_df['low'].min():.2f}")
    print(f"   Average Close: CNY {np.mean(pred_close):.2f}")
    print(f"   Weekly Change: {'+' if weekly_change >= 0 else ''}{weekly_change:.2f}%")
    print(f"   Trend: {'Bullish' if weekly_change > 0 else 'Bearish' if weekly_change < 0 else 'Flat'}")
    
    # Plot K-line chart
    print(f"\n" + "=" * 80)
    print("Generating K-Line Chart")
    print("=" * 80)
    
    hist_recent = df.tail(30).copy()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [3, 1]})
    fig.suptitle('SPDB (SHSE.600000) - Next Week Price Prediction', fontsize=16, fontweight='bold')
    
    # Historical data
    hist_dates = pd.to_datetime(hist_recent['timestamps'])
    hist_close = hist_recent['close'].values
    hist_open = hist_recent['open'].values
    hist_high = hist_recent['high'].values
    hist_low = hist_recent['low'].values
    hist_volume = hist_recent['volume'].values
    
    # Prediction data
    pred_dates = pred_df.index
    pred_close = pred_df['close'].values
    pred_open = pred_df['open'].values
    pred_high = pred_df['high'].values
    pred_low = pred_df['low'].values
    pred_volume = pred_df['volume'].values
    
    # Plot K-line - Historical
    x_hist = range(len(hist_dates))
    colors_hist = ['red' if hist_close[i] >= hist_open[i] else 'green' for i in range(len(hist_dates))]
    
    for i in range(len(hist_dates)):
        ax1.plot([i, i], [hist_low[i], hist_high[i]], color=colors_hist[i], linewidth=1)
        body_top = max(hist_open[i], hist_close[i])
        body_bottom = min(hist_open[i], hist_close[i])
        ax1.add_patch(plt.Rectangle((i-0.3, body_bottom), 0.6, body_top-body_bottom, 
                                     facecolor=colors_hist[i], edgecolor=colors_hist[i]))
    
    # Plot K-line - Prediction (dashed)
    x_pred_start = len(hist_dates)
    x_pred = range(x_pred_start, x_pred_start + len(pred_dates))
    
    for i, idx in enumerate(x_pred):
        ax1.plot([idx, idx], [pred_low[i], pred_high[i]], color='blue', linewidth=1, linestyle='--')
        body_top = max(pred_open[i], pred_close[i])
        body_bottom = min(pred_open[i], pred_close[i])
        ax1.add_patch(plt.Rectangle((idx-0.3, body_bottom), 0.6, body_top-body_bottom, 
                                     fill=False, edgecolor='blue', linewidth=2, linestyle='--'))
    
    # Close price line
    all_dates = list(hist_dates) + list(pred_dates)
    all_close = list(hist_close) + list(pred_close)
    ax1.plot(range(len(all_dates)), all_close, 'k-', linewidth=1, alpha=0.3, label='Close Price Trend')
    
    # Mark prediction area
    ax1.axvspan(x_pred_start-0.5, x_pred[-1]+0.5, alpha=0.1, color='blue', label='Prediction Area')
    
    # X-axis labels
    all_x = range(len(all_dates))
    label_positions = list(range(0, len(all_dates), 5))
    label_dates = [all_dates[i].strftime('%m-%d') for i in label_positions]
    ax1.set_xticks(label_positions)
    ax1.set_xticklabels(label_dates, rotation=45)
    
    ax1.set_ylabel('Price (CNY)', fontsize=12)
    ax1.set_title(f'Historical ({hist_dates.iloc[0].strftime("%Y-%m-%d")} to {hist_dates.iloc[-1].strftime("%Y-%m-%d")}) | '
                  f'Prediction ({pred_dates[0].strftime("%Y-%m-%d")} to {pred_dates[-1].strftime("%Y-%m-%d")})', 
                  fontsize=10)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Volume
    colors_vol_hist = ['red' if hist_close[i] >= hist_open[i] else 'green' for i in range(len(hist_dates))]
    ax2.bar(range(len(hist_dates)), hist_volume, color=colors_vol_hist, alpha=0.6, label='Historical Volume')
    
    colors_vol_pred = ['blue'] * len(pred_dates)
    ax2.bar(x_pred, pred_volume, color=colors_vol_pred, alpha=0.4, edgecolor='blue', 
            linewidth=2, linestyle='--', label='Predicted Volume')
    
    ax2.set_xlabel('Date', fontsize=12)
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.set_xticks(label_positions)
    ax2.set_xticklabels(label_dates, rotation=45)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_path = f'figures/spdb_prediction_{timestamp}.png'
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"[OK] K-line chart saved: {save_path}")
    print(f"[OK] File size: {Path(save_path).stat().st_size / 1024:.1f} KB")
    
    # Disclaimer
    print("\n" + "=" * 80)
    print("DISCLAIMER")
    print("=" * 80)
    print("This prediction is generated by AI model for reference only.")
    print("It does not constitute investment advice.")
    print("Stock market involves risks. Please make decisions based on comprehensive information.")
    print("=" * 80)
    
    print("\n[PREDICTION COMPLETE]")
    print(f"Chart saved to: {save_path}")
    
    return save_path


if __name__ == '__main__':
    try:
        save_path = predict_and_plot()
        print(f"\nSuccess! View the chart at: {save_path}")
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
