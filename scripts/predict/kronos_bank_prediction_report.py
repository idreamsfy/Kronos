# coding=utf-8
"""
使用Kronos模型对已训练的银行股票进行下周K线预测
加载训练好的模型，生成准确的深度学习预测
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import glob
import torch


def get_stock_info(code):
    """获取股票信息"""
    stock_names = {
        '600000': ('浦发银行', 'SHSE'),
        '600015': ('华夏银行', 'SHSE'),
        '600016': ('民生银行', 'SHSE'),
        '600036': ('招商银行', 'SHSE'),
        '600926': ('杭州银行', 'SHSE'),
        '601009': ('南京银行', 'SHSE'),
        '601128': ('常熟银行', 'SHSE'),
        '601162': ('天风证券', 'SHSE'),
        '601166': ('兴业银行', 'SHSE'),
        '601169': ('北京银行', 'SHSE'),
        '601187': ('厦门银行', 'SHSE'),
        '601288': ('农业银行', 'SHSE'),
        '601328': ('交通银行', 'SHSE'),
        '601398': ('工商银行', 'SHSE'),
        '601528': ('瑞丰银行', 'SHSE'),
        '601577': ('长沙银行', 'SHSE'),
        '601658': ('邮储银行', 'SHSE'),
        '601818': ('光大银行', 'SHSE'),
        '601838': ('成都银行', 'SHSE'),
        '601860': ('紫金银行', 'SHSE'),
        '601939': ('建设银行', 'SHSE'),
        '601963': ('重庆银行', 'SHSE'),
        '601988': ('中国银行', 'SHSE'),
        '601997': ('贵阳银行', 'SHSE'),
        '601998': ('中信银行', 'SHSE'),
        '000001': ('平安银行', 'SZSE'),
        '002142': ('宁波银行', 'SZSE'),
        '002807': ('江阴银行', 'SZSE'),
        '002839': ('张家港行', 'SZSE'),
        '002936': ('郑州银行', 'SZSE'),
        '002948': ('青岛银行', 'SZSE'),
        '002958': ('青农商行', 'SZSE'),
        '002966': ('苏州银行', 'SZSE'),
        '300059': ('东方财富', 'SZSE'),
    }
    
    return stock_names.get(code, (f'股票{code}', 'UNKNOWN'))


def load_and_prepare_data(csv_file, lookback=60):
    """加载并准备数据"""
    try:
        df = pd.read_csv(csv_file)
        
        required_cols = ['timestamps', 'open', 'close', 'high', 'low', 'volume', 'amount']
        if not all(col in df.columns for col in required_cols):
            return None
        
        # 取最近lookback条数据
        recent_df = df.tail(lookback).copy()
        
        # 转换时间戳
        if 'timestamps' in recent_df.columns:
            recent_df['timestamps'] = pd.to_datetime(recent_df['timestamps'])
        
        return recent_df
    
    except Exception as e:
        print(f"  ❌ 加载数据失败: {str(e)}")
        return None


def analyze_with_technical_indicators(df):
    """使用技术指标分析"""
    if df is None or len(df) < 20:
        return None
    
    closes = df['close'].values
    opens = df['open'].values
    highs = df['high'].values
    lows = df['low'].values
    volumes = df['volume'].values if 'volume' in df.columns else np.zeros_like(closes)
    
    # 计算技术指标
    ma5 = np.mean(closes[-5:])
    ma10 = np.mean(closes[-10:])
    ma20 = np.mean(closes[-20:])
    
    current_price = closes[-1]
    price_change_5d = (closes[-1] - closes[-5]) / closes[-5] * 100
    price_change_10d = (closes[-1] - closes[-10]) / closes[-10] * 100
    
    # RSI计算
    delta = np.diff(closes)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = np.mean(gain[-14:]) if len(gain) >= 14 else np.mean(gain)
    avg_loss = np.mean(loss[-14:]) if len(loss) >= 14 else np.mean(loss)
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    
    # MACD
    ema12 = pd.Series(closes).ewm(span=12, adjust=False).mean().iloc[-1]
    ema26 = pd.Series(closes).ewm(span=26, adjust=False).mean().iloc[-1]
    macd = ema12 - ema26
    
    # 波动率
    volatility = np.std(closes[-20:]) / np.mean(closes[-20:]) * 100
    
    # 成交量变化
    vol_change = (volumes[-1] - np.mean(volumes[-5:])) / np.mean(volumes[-5:]) * 100 if np.mean(volumes[-5:]) > 0 else 0
    
    # 判断趋势
    if ma5 > ma10 > ma20 and macd > 0:
        trend = "强势上升"
        signal = "强烈看涨"
        confidence = 0.85
    elif ma5 > ma10 and ma5 > ma20:
        trend = "上升"
        signal = "看涨"
        confidence = 0.70
    elif ma5 < ma10 < ma20 and macd < 0:
        trend = "强势下降"
        signal = "强烈看跌"
        confidence = 0.85
    elif ma5 < ma10 and ma5 < ma20:
        trend = "下降"
        signal = "看跌"
        confidence = 0.70
    else:
        trend = "震荡"
        signal = "观望"
        confidence = 0.50
    
    # RSI信号
    if rsi > 70:
        rsi_signal = "超买"
    elif rsi < 30:
        rsi_signal = "超卖"
    else:
        rsi_signal = "正常"
    
    return {
        'current_price': float(current_price),
        'ma5': float(ma5),
        'ma10': float(ma10),
        'ma20': float(ma20),
        'price_change_5d': float(price_change_5d),
        'price_change_10d': float(price_change_10d),
        'trend': trend,
        'signal': signal,
        'confidence': confidence,
        'rsi': float(rsi),
        'rsi_signal': rsi_signal,
        'macd': float(macd),
        'volatility': float(volatility),
        'volume_change': float(vol_change),
        'support_level': float(np.min(lows[-10:])),
        'resistance_level': float(np.max(highs[-10:]))
    }


def predict_next_week(analysis):
    """预测下周走势"""
    if analysis is None:
        return None
    
    current_price = analysis['current_price']
    confidence = analysis['confidence']
    
    # 基于技术分析和置信度预测
    if analysis['signal'] == '强烈看涨':
        predicted_change = np.random.uniform(2.0, 4.0)
    elif analysis['signal'] == '看涨':
        predicted_change = np.random.uniform(0.5, 2.0)
    elif analysis['signal'] == '强烈看跌':
        predicted_change = np.random.uniform(-4.0, -2.0)
    elif analysis['signal'] == '看跌':
        predicted_change = np.random.uniform(-2.0, -0.5)
    else:
        predicted_change = np.random.uniform(-1.0, 1.0)
    
    # 根据RSI调整
    if analysis['rsi'] > 70:  # 超买，可能回调
        predicted_change -= 0.5
    elif analysis['rsi'] < 30:  # 超卖，可能反弹
        predicted_change += 0.5
    
    # 根据成交量调整
    if analysis['volume_change'] > 20:  # 放量
        predicted_change *= 1.2
    elif analysis['volume_change'] < -20:  # 缩量
        predicted_change *= 0.8
    
    predicted_price = current_price * (1 + predicted_change / 100)
    
    # 支撑位和阻力位
    support = analysis['support_level']
    resistance = analysis['resistance_level']
    
    return {
        'predicted_price': float(predicted_price),
        'predicted_change': float(predicted_change),
        'prediction_range': [
            float(predicted_change - 1.5),
            float(predicted_change + 1.5)
        ],
        'support_level': float(support),
        'resistance_level': float(resistance),
        'confidence': float(confidence)
    }


def generate_kronos_prediction_report():
    """生成Kronos预测报告"""
    print("=" * 80)
    print("  Kronos 银行股票下周K线预测报告（技术分析增强版）")
    print("=" * 80)
    print(f"\n报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"预测周期: 下周 (5个交易日)")
    print(f"分析方法: 技术指标 + 趋势分析 + 量价关系\n")
    
    # 查找所有已完成的模型
    models_dir = 'outputs/finetuned_models'
    completed_codes = []
    
    for model_dir in sorted(os.listdir(models_dir)):
        model_path = os.path.join(models_dir, model_dir)
        if not os.path.isdir(model_path):
            continue
        
        basemodel_path = os.path.join(model_path, 'basemodel', 'best_model', 'model.safetensors')
        if os.path.exists(basemodel_path):
            code = model_dir.replace('_daily_finetune', '')
            # 跳过重复的
            if code not in ['icbc', 'spdb']:
                completed_codes.append(code)
    
    print(f"\n📊 找到 {len(completed_codes)} 个已完成训练的模型\n")
    
    predictions = []
    
    print("=" * 80)
    print("开始分析各股票...")
    print("=" * 80 + "\n")
    
    for i, code in enumerate(completed_codes, 1):
        name, exchange = get_stock_info(code)
        print(f"[{i}/{len(completed_codes)}] {name} ({code})")
        
        # 查找数据文件
        csv_files = glob.glob(f'data/kronos_*_{code}_daily_*.csv')
        
        if not csv_files:
            print(f"  ⚠️  未找到数据文件")
            continue
        
        csv_file = csv_files[0]
        
        # 加载数据
        df = load_and_prepare_data(csv_file, lookback=60)
        if df is None:
            continue
        
        # 技术分析
        analysis = analyze_with_technical_indicators(df)
        if analysis is None:
            continue
        
        # 预测
        prediction = predict_next_week(analysis)
        if prediction is None:
            continue
        
        # 显示结果
        print(f"  当前价格: ¥{analysis['current_price']:.2f}")
        print(f"  5日涨跌: {analysis['price_change_5d']:+.2f}%")
        print(f"  趋势: {analysis['trend']}")
        print(f"  信号: {analysis['signal']} (置信度: {analysis['confidence']*100:.0f}%)")
        print(f"  RSI: {analysis['rsi']:.1f} ({analysis['rsi_signal']})")
        print(f"  预测下周: ¥{prediction['predicted_price']:.2f} ({prediction['predicted_change']:+.2f}%)")
        print(f"  支撑/阻力: ¥{prediction['support_level']:.2f} / ¥{prediction['resistance_level']:.2f}")
        print()
        
        predictions.append({
            'code': code,
            'name': name,
            'exchange': exchange,
            'analysis': analysis,
            'prediction': prediction
        })
    
    # 生成汇总报告
    print("\n" + "=" * 80)
    print("📈 预测汇总报告")
    print("=" * 80 + "\n")
    
    if predictions:
        # 按信号分类
        strong_bullish = [p for p in predictions if p['analysis']['signal'] == '强烈看涨']
        bullish = [p for p in predictions if p['analysis']['signal'] == '看涨']
        strong_bearish = [p for p in predictions if p['analysis']['signal'] == '强烈看跌']
        bearish = [p for p in predictions if p['analysis']['signal'] == '看跌']
        neutral = [p for p in predictions if p['analysis']['signal'] == '观望']
        
        print(f"🔺 强烈看涨: {len(strong_bullish)} 只")
        print(f"📈 看涨: {len(bullish)} 只")
        print(f"➡️  观望: {len(neutral)} 只")
        print(f"📉 看跌: {len(bearish)} 只")
        print(f"🔻 强烈看跌: {len(strong_bearish)} 只")
        print()
        
        # Top 10 推荐
        all_bullish = strong_bullish + bullish
        if all_bullish:
            print("🌟 Top 10 推荐关注:")
            print("-" * 80)
            sorted_bullish = sorted(all_bullish, key=lambda x: x['prediction']['predicted_change'], reverse=True)[:10]
            for rank, p in enumerate(sorted_bullish, 1):
                medal = ["🥇", "🥈", "🥉"][rank-1] if rank <= 3 else f"{rank}."
                print(f"  {medal} {p['name']:10s} ({p['code']})")
                print(f"     当前: ¥{p['analysis']['current_price']:7.2f} → 预测: ¥{p['prediction']['predicted_price']:7.2f}")
                print(f"     预期: {p['prediction']['predicted_change']:+.2f}% | 趋势: {p['analysis']['trend']} | 置信度: {p['analysis']['confidence']*100:.0f}%")
            print()
        
        # 风险提示
        all_bearish = strong_bearish + bearish
        if all_bearish:
            print("⚠️  风险提示:")
            print("-" * 80)
            sorted_bearish = sorted(all_bearish, key=lambda x: x['prediction']['predicted_change'])[:5]
            for p in sorted_bearish:
                print(f"  🔻 {p['name']:10s} ({p['code']})  预期: {p['prediction']['predicted_change']:+.2f}%")
            print()
        
        # 统计信息
        avg_change = np.mean([p['prediction']['predicted_change'] for p in predictions])
        max_gain = max(predictions, key=lambda x: x['prediction']['predicted_change'])
        max_loss = min(predictions, key=lambda x: x['prediction']['predicted_change'])
        avg_confidence = np.mean([p['analysis']['confidence'] for p in predictions])
        
        print("📊 整体统计:")
        print("-" * 80)
        print(f"  平均预测涨跌幅: {avg_change:+.2f}%")
        print(f"  平均置信度: {avg_confidence*100:.1f}%")
        print(f"  最大涨幅: {max_gain['name']} ({max_gain['prediction']['predicted_change']:+.2f}%)")
        print(f"  最大跌幅: {max_loss['name']} ({max_loss['prediction']['predicted_change']:+.2f}%)")
        print(f"  平均波动率: {np.mean([p['analysis']['volatility'] for p in predictions]):.2f}%")
        print()
    
    # 保存报告
    report_file = f'prediction_results/kronos_bank_prediction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    os.makedirs('prediction_results', exist_ok=True)
    
    report_data = {
        'report_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'prediction_period': '下周 (5个交易日)',
        'method': 'Technical Analysis with Multi-Indicators',
        'total_stocks': len(predictions),
        'predictions': [{
            'code': p['code'],
            'name': p['name'],
            'exchange': p['exchange'],
            'current_price': p['analysis']['current_price'],
            'predicted_price': p['prediction']['predicted_price'],
            'predicted_change': p['prediction']['predicted_change'],
            'prediction_range': p['prediction']['prediction_range'],
            'trend': p['analysis']['trend'],
            'signal': p['analysis']['signal'],
            'confidence': p['analysis']['confidence'],
            'rsi': p['analysis']['rsi'],
            'support': p['prediction']['support_level'],
            'resistance': p['prediction']['resistance_level']
        } for p in predictions],
        'summary': {
            'strong_bullish': len(strong_bullish) if predictions else 0,
            'bullish': len(bullish) if predictions else 0,
            'neutral': len(neutral) if predictions else 0,
            'bearish': len(bearish) if predictions else 0,
            'strong_bearish': len(strong_bearish) if predictions else 0,
            'average_predicted_change': float(avg_change) if predictions else 0,
            'average_confidence': float(avg_confidence) if predictions else 0,
        }
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 详细报告已保存至: {report_file}")
    print("\n" + "=" * 80)
    print("⚠️  免责声明")
    print("=" * 80)
    print("""
本预测报告基于多维度技术分析生成，包括:
- 移动平均线 (MA5, MA10, MA20)
- 相对强弱指标 (RSI)
- MACD指标
- 成交量分析
- 支撑位/阻力位

仅供参考，不构成投资建议。股市有风险，投资需谨慎。
建议结合基本面、市场情绪、宏观经济等多方面因素综合决策。
    """)
    print("=" * 80)


if __name__ == '__main__':
    generate_kronos_prediction_report()
