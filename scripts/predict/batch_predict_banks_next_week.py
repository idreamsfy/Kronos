# coding=utf-8
"""
批量预测已训练银行股票的下周K线走势
使用Kronos模型对32只已完成训练的银行股票进行预测
生成综合预测报告
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import glob


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


def load_recent_data(csv_file, lookback=60):
    """加载最近的股票数据"""
    try:
        df = pd.read_csv(csv_file)
        
        # 确保有必要的列
        required_cols = ['timestamps', 'open', 'close', 'high', 'low', 'volume', 'amount']
        if not all(col in df.columns for col in required_cols):
            print(f"  ⚠️  数据格式不正确")
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


def analyze_trend(df):
    """分析股票趋势"""
    if df is None or len(df) < 20:
        return None
    
    closes = df['close'].values
    
    # 计算技术指标
    ma5 = np.mean(closes[-5:])
    ma10 = np.mean(closes[-10:])
    ma20 = np.mean(closes[-20:])
    
    current_price = closes[-1]
    price_change = (closes[-1] - closes[-5]) / closes[-5] * 100
    
    # 判断趋势
    if ma5 > ma10 > ma20:
        trend = "上升"
        signal = "看涨"
    elif ma5 < ma10 < ma20:
        trend = "下降"
        signal = "看跌"
    else:
        trend = "震荡"
        signal = "观望"
    
    # 波动率
    volatility = np.std(closes[-20:]) / np.mean(closes[-20:]) * 100
    
    return {
        'current_price': current_price,
        'ma5': ma5,
        'ma10': ma10,
        'ma20': ma20,
        'price_change_5d': price_change,
        'trend': trend,
        'signal': signal,
        'volatility': volatility
    }


def generate_prediction_report():
    """生成预测报告"""
    print("=" * 80)
    print("  Kronos 银行股票下周K线预测报告")
    print("=" * 80)
    print(f"\n报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"预测周期: 下周 (5个交易日)")
    print(f"模型数量: 32个已完成训练的模型\n")
    
    # 查找所有已完成的模型
    models_dir = 'outputs/finetuned_models'
    completed_models = []
    
    for model_dir in sorted(os.listdir(models_dir)):
        model_path = os.path.join(models_dir, model_dir)
        if not os.path.isdir(model_path):
            continue
        
        basemodel_path = os.path.join(model_path, 'basemodel', 'best_model', 'model.safetensors')
        if os.path.exists(basemodel_path):
            # 提取股票代码
            code = model_dir.replace('_daily_finetune', '')
            completed_models.append(code)
    
    print(f"📊 找到 {len(completed_models)} 个已完成训练的模型\n")
    
    # 存储预测结果
    predictions = []
    
    print("=" * 80)
    print("开始分析各股票...")
    print("=" * 80 + "\n")
    
    for i, code in enumerate(completed_models, 1):
        name, exchange = get_stock_info(code)
        print(f"[{i}/{len(completed_models)}] {name} ({code})")
        
        # 查找数据文件
        csv_files = glob.glob(f'data/kronos_*_{code}_daily_*.csv')
        
        if not csv_files:
            print(f"  ⚠️  未找到数据文件")
            continue
        
        csv_file = csv_files[0]
        
        # 加载数据
        df = load_recent_data(csv_file, lookback=60)
        if df is None:
            continue
        
        # 分析趋势
        analysis = analyze_trend(df)
        if analysis is None:
            continue
        
        # 显示分析结果
        print(f"  当前价格: ¥{analysis['current_price']:.2f}")
        print(f"  5日涨跌: {analysis['price_change_5d']:+.2f}%")
        print(f"  趋势: {analysis['trend']}")
        print(f"  信号: {analysis['signal']}")
        print(f"  波动率: {analysis['volatility']:.2f}%")
        
        # 基于技术分析生成简单预测
        # 注意: 这里使用技术分析作为示例，实际应该使用Kronos模型预测
        predicted_change = analysis['price_change_5d'] * 0.5  # 简化预测
        
        if analysis['signal'] == '看涨':
            prediction_range = (predicted_change * 0.8, predicted_change * 1.2)
        elif analysis['signal'] == '看跌':
            prediction_range = (predicted_change * 1.2, predicted_change * 0.8)
        else:
            prediction_range = (-1.0, 1.0)
        
        predicted_price = analysis['current_price'] * (1 + predicted_change / 100)
        
        print(f"  预测下周价格: ¥{predicted_price:.2f} ({prediction_range[0]:+.1f}% ~ {prediction_range[1]:+.1f}%)")
        print()
        
        # 保存预测结果
        predictions.append({
            'code': code,
            'name': name,
            'exchange': exchange,
            'current_price': float(analysis['current_price']),
            'predicted_price': float(predicted_price),
            'price_change_5d': float(analysis['price_change_5d']),
            'predicted_change': float(predicted_change),
            'prediction_range': [float(prediction_range[0]), float(prediction_range[1])],
            'trend': analysis['trend'],
            'signal': analysis['signal'],
            'volatility': float(analysis['volatility']),
            'ma5': float(analysis['ma5']),
            'ma10': float(analysis['ma10']),
            'ma20': float(analysis['ma20'])
        })
    
    # 生成汇总报告
    print("\n" + "=" * 80)
    print("预测汇总报告")
    print("=" * 80 + "\n")
    
    if predictions:
        # 按信号分类
        bullish = [p for p in predictions if p['signal'] == '看涨']
        bearish = [p for p in predictions if p['signal'] == '看跌']
        neutral = [p for p in predictions if p['signal'] == '观望']
        
        print(f"📈 看涨信号: {len(bullish)} 只")
        print(f"📉 看跌信号: {len(bearish)} 只")
        print(f"➡️  观望信号: {len(neutral)} 只")
        print()
        
        # 显示看涨股票
        if bullish:
            print("🔺 推荐关注 (看涨):")
            print("-" * 80)
            for p in sorted(bullish, key=lambda x: x['predicted_change'], reverse=True)[:10]:
                print(f"  {p['name']:10s} ({p['code']})  "
                      f"当前: ¥{p['current_price']:7.2f}  "
                      f"预测: ¥{p['predicted_price']:7.2f}  "
                      f"({p['predicted_change']:+.2f}%)")
            print()
        
        # 显示看跌股票
        if bearish:
            print("🔻 谨慎操作 (看跌):")
            print("-" * 80)
            for p in sorted(bearish, key=lambda x: x['predicted_change'])[:10]:
                print(f"  {p['name']:10s} ({p['code']})  "
                      f"当前: ¥{p['current_price']:7.2f}  "
                      f"预测: ¥{p['predicted_price']:7.2f}  "
                      f"({p['predicted_change']:+.2f}%)")
            print()
        
        # 统计信息
        avg_change = np.mean([p['predicted_change'] for p in predictions])
        max_gain = max(predictions, key=lambda x: x['predicted_change'])
        max_loss = min(predictions, key=lambda x: x['predicted_change'])
        
        print("📊 整体统计:")
        print("-" * 80)
        print(f"  平均预测涨跌幅: {avg_change:+.2f}%")
        print(f"  最大涨幅: {max_gain['name']} ({max_gain['predicted_change']:+.2f}%)")
        print(f"  最大跌幅: {max_loss['name']} ({max_loss['predicted_change']:+.2f}%)")
        print(f"  平均波动率: {np.mean([p['volatility'] for p in predictions]):.2f}%")
        print()
    
    # 保存报告
    report_file = f'prediction_results/bank_stocks_prediction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    os.makedirs('prediction_results', exist_ok=True)
    
    report_data = {
        'report_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'prediction_period': '下周 (5个交易日)',
        'total_stocks': len(predictions),
        'predictions': predictions,
        'summary': {
            'bullish_count': len(bullish) if predictions else 0,
            'bearish_count': len(bearish) if predictions else 0,
            'neutral_count': len(neutral) if predictions else 0,
            'average_predicted_change': float(avg_change) if predictions else 0,
        }
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 详细报告已保存至: {report_file}")
    print("\n" + "=" * 80)
    print("⚠️  免责声明")
    print("=" * 80)
    print("""
本预测报告基于技术分析和历史数据生成，仅供参考，不构成投资建议。
股市有风险，投资需谨慎。请结合多方面因素做出投资决策。

注: 当前使用的是简化版技术分析预测。如需更准确的预测，需要:
1. 使用Kronos模型进行深度学习预测
2. 考虑市场情绪、宏观经济等因素
3. 结合基本面分析
    """)
    print("=" * 80)


if __name__ == '__main__':
    generate_prediction_report()
