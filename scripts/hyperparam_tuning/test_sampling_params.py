#!/usr/bin/env python
"""
测试不同采样参数组合对预测性能的影响
无需重新训练模型，仅进行推理测试

测试配置:
1. 保守型: T=0.8, top_p=0.9
2. 当前默认: T=1.0, top_p=0.9
3. 均衡型: T=1.0, top_p=0.95
4. 激进型: T=1.2, top_p=0.95
5. 全采样: T=1.0, top_p=1.0
"""

import os
import sys
import torch
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from model.kronos import Kronos, KronosTokenizer, KronosPredictor


def calculate_mape(actual, predicted):
    """计算MAPE"""
    mask = actual != 0
    return np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100


def calculate_r2(actual, predicted):
    """计算R²"""
    ss_res = np.sum((actual - predicted) ** 2)
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)
    return 1 - (ss_res / ss_tot)


def calculate_direction_accuracy(actual_changes, predicted_changes):
    """计算方向准确率"""
    actual_direction = np.sign(actual_changes)
    predicted_direction = np.sign(predicted_changes)
    return np.mean(actual_direction == predicted_direction) * 100


def test_sampling_params():
    """测试不同采样参数组合"""
    
    print("=" * 80)
    print("🔬 测试不同采样参数组合")
    print("=" * 80)
    print()
    
    # 模型路径
    tokenizer_path = "outputs/models/tokenizer/best_model"
    predictor_path = "outputs/models/predictor/best_model"
    data_path = "data/raw/futu/5min_300033_with_features.csv"
    
    # 检查文件是否存在
    if not os.path.exists(tokenizer_path):
        print(f"❌ Tokenizer模型不存在: {tokenizer_path}")
        return
    
    if not os.path.exists(predictor_path):
        print(f"❌ Predictor模型不存在: {predictor_path}")
        return
    
    if not os.path.exists(data_path):
        print(f"❌ 数据文件不存在: {data_path}")
        return
    
    print("1. 加载模型...")
    print(f"   Tokenizer: {tokenizer_path}")
    print(f"   Predictor: {predictor_path}")
    
    # 加载模型
    tokenizer = KronosTokenizer.from_pretrained(tokenizer_path)
    model = Kronos.from_pretrained(predictor_path)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    
    # 创建预测器
    predictor = KronosPredictor(model, tokenizer, device=device, max_context=512)
    
    print(f"   设备: {device}")
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print()
    
    print("2. 加载测试数据...")
    df = pd.read_csv(data_path)
    
    # 确保timestamps是datetime类型
    if not pd.api.types.is_datetime64_any_dtype(df['timestamps']):
        df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    print(f"   数据行数: {len(df):,}")
    print(f"   特征列数: {len(df.columns)}")
    print()
    
    # 准备测试数据（使用最后100条作为输入，预测接下来48条）
    lookback = 100
    pred_len = 48
    
    # 分割数据
    test_input = df.iloc[-lookback:].copy()
    test_actual = df.iloc[-lookback:-lookback+pred_len].copy()
    
    print(f"3. 准备测试数据...")
    print(f"   Lookback: {lookback} 条")
    print(f"   Predict: {pred_len} 条")
    print()
    
    # 定义测试配置
    param_configs = [
        {'T': 0.8, 'top_p': 0.9, 'name': '保守型'},
        {'T': 1.0, 'top_p': 0.9, 'name': '当前默认'},
        {'T': 1.0, 'top_p': 0.95, 'name': '均衡型'},
        {'T': 1.2, 'top_p': 0.95, 'name': '激进型'},
        {'T': 1.0, 'top_p': 1.0, 'name': '全采样'},
    ]
    
    results = []
    
    print("4. 开始测试不同采样参数组合...")
    print("=" * 80)
    
    for config in param_configs:
        print(f"\n测试配置: {config['name']}")
        print(f"  Temperature: {config['T']}")
        print(f"  Top-p: {config['top_p']}")
        
        try:
            # 进行预测
            start_time = datetime.now()
            
            pred_df = predictor.predict(
                df=test_input,
                x_timestamp=test_input['timestamps'].iloc[-lookback:],
                y_timestamp=test_actual['timestamps'],
                pred_len=pred_len,
                T=config['T'],
                top_p=config['top_p']
            )
            
            end_time = datetime.now()
            inference_time = (end_time - start_time).total_seconds()
            
            # 计算指标
            actual_close = test_actual['close'].values
            pred_close = pred_df['close'].values
            
            mape = calculate_mape(actual_close, pred_close)
            r2 = calculate_r2(actual_close, pred_close)
            
            # 计算方向准确率
            actual_changes = np.diff(actual_close)
            pred_changes = np.diff(pred_close)
            direction_acc = calculate_direction_accuracy(actual_changes, pred_changes)
            
            # 计算最高价误差
            actual_high = test_actual['high'].values
            pred_high = pred_df['high'].values
            high_error = np.mean(np.abs(actual_high - pred_high))
            
            result = {
                'name': config['name'],
                'T': config['T'],
                'top_p': config['top_p'],
                'MAPE': mape,
                'R2': r2,
                'Direction_Accuracy': direction_acc,
                'High_Error': high_error,
                'Inference_Time': inference_time
            }
            
            results.append(result)
            
            print(f"  ✅ MAPE: {mape:.2f}%")
            print(f"  ✅ R²: {r2:.4f}")
            print(f"  ✅ 方向准确率: {direction_acc:.1f}%")
            print(f"  ✅ 最高价误差: ¥{high_error:.2f}")
            print(f"  ⏱️  推理时间: {inference_time:.2f}秒")
            
        except Exception as e:
            print(f"  ❌ 错误: {str(e)}")
            continue
    
    print("\n" + "=" * 80)
    print("📊 测试结果汇总")
    print("=" * 80)
    
    if not results:
        print("\n❌ 没有成功的测试结果，请检查错误信息")
        return None
    
    # 创建结果DataFrame
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('MAPE')
    
    print("\n按MAPE排序:")
    print(results_df[['name', 'T', 'top_p', 'MAPE', 'R2', 'Direction_Accuracy']].to_string(index=False))
    
    # 找出最佳配置
    best_mape_idx = results_df['MAPE'].idxmin()
    best_r2_idx = results_df['R2'].idxmax()
    best_dir_idx = results_df['Direction_Accuracy'].idxmax()
    
    print("\n🏆 最佳配置:")
    print(f"  最低MAPE: {results_df.loc[best_mape_idx]['name']} "
          f"(T={results_df.loc[best_mape_idx]['T']}, "
          f"top_p={results_df.loc[best_mape_idx]['top_p']}, "
          f"MAPE={results_df.loc[best_mape_idx]['MAPE']:.2f}%)")
    
    print(f"  最高R²: {results_df.loc[best_r2_idx]['name']} "
          f"(T={results_df.loc[best_r2_idx]['T']}, "
          f"top_p={results_df.loc[best_r2_idx]['top_p']}, "
          f"R²={results_df.loc[best_r2_idx]['R2']:.4f})")
    
    print(f"  最高方向准确率: {results_df.loc[best_dir_idx]['name']} "
          f"(T={results_df.loc[best_dir_idx]['T']}, "
          f"top_p={results_df.loc[best_dir_idx]['top_p']}, "
          f"准确率={results_df.loc[best_dir_idx]['Direction_Accuracy']:.1f}%)")
    
    # 保存结果
    output_dir = "outputs/hyperparam_tuning"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{output_dir}/sampling_params_test_{timestamp}.csv"
    results_df.to_csv(output_file, index=False)
    
    print(f"\n💾 结果已保存到: {output_file}")
    
    # 绘制对比图
    plot_comparison(results_df, output_dir, timestamp)
    
    print("\n✅ 测试完成！")
    
    return results_df


def plot_comparison(results_df, output_dir, timestamp):
    """绘制对比图"""
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. MAPE对比
    ax1 = axes[0, 0]
    bars1 = ax1.bar(range(len(results_df)), results_df['MAPE'], 
                    color=['#2ecc71', '#3498db', '#9b59b6', '#e74c3c', '#f39c12'])
    ax1.set_xticks(range(len(results_df)))
    ax1.set_xticklabels(results_df['name'], rotation=45, ha='right')
    ax1.set_ylabel('MAPE (%)')
    ax1.set_title('MAPE对比')
    ax1.grid(axis='y', alpha=0.3)
    
    # 在柱状图上标注数值
    for bar, val in zip(bars1, results_df['MAPE']):
        ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                f'{val:.2f}%', ha='center', va='bottom', fontsize=9)
    
    # 2. R²对比
    ax2 = axes[0, 1]
    colors2 = ['#2ecc71' if x > 0 else '#e74c3c' for x in results_df['R2']]
    bars2 = ax2.bar(range(len(results_df)), results_df['R2'], color=colors2)
    ax2.set_xticks(range(len(results_df)))
    ax2.set_xticklabels(results_df['name'], rotation=45, ha='right')
    ax2.set_ylabel('R²')
    ax2.set_title('R²对比')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.grid(axis='y', alpha=0.3)
    
    for bar, val in zip(bars2, results_df['R2']):
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + (0.1 if val > 0 else -0.1),
                f'{val:.4f}', ha='center', va='bottom' if val > 0 else 'top', fontsize=9)
    
    # 3. 方向准确率对比
    ax3 = axes[1, 0]
    bars3 = ax3.bar(range(len(results_df)), results_df['Direction_Accuracy'],
                    color='#3498db')
    ax3.set_xticks(range(len(results_df)))
    ax3.set_xticklabels(results_df['name'], rotation=45, ha='right')
    ax3.set_ylabel('方向准确率 (%)')
    ax3.set_title('方向准确率对比')
    ax3.grid(axis='y', alpha=0.3)
    
    for bar, val in zip(bars3, results_df['Direction_Accuracy']):
        ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=9)
    
    # 4. 综合雷达图
    ax4 = axes[1, 1]
    categories = ['MAPE\n(越低越好)', 'R²\n(越高越好)', '方向准确率\n(越高越好)']
    
    # 归一化指标（转换为0-1范围，越高越好）
    normalized = pd.DataFrame()
    normalized['MAPE_norm'] = 1 - (results_df['MAPE'] - results_df['MAPE'].min()) / (results_df['MAPE'].max() - results_df['MAPE'].min())
    normalized['R2_norm'] = (results_df['R2'] - results_df['R2'].min()) / (results_df['R2'].max() - results_df['R2'].min())
    normalized['Dir_norm'] = (results_df['Direction_Accuracy'] - results_df['Direction_Accuracy'].min()) / (results_df['Direction_Accuracy'].max() - results_df['Direction_Accuracy'].min())
    
    x = np.arange(len(categories))
    width = 0.15
    
    for i, name in enumerate(results_df['name']):
        values = [normalized.iloc[i]['MAPE_norm'], 
                 normalized.iloc[i]['R2_norm'],
                 normalized.iloc[i]['Dir_norm']]
        ax4.bar(x + i*width, values, width, label=name, alpha=0.7)
    
    ax4.set_xticks(x + width * 2)
    ax4.set_xticklabels(categories)
    ax4.set_ylabel('归一化得分')
    ax4.set_title('综合性能对比')
    ax4.legend(loc='upper right', fontsize=8)
    ax4.set_ylim(0, 1.1)
    ax4.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    plot_file = f"{output_dir}/sampling_params_comparison_{timestamp}.png"
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    print(f"📊 对比图已保存到: {plot_file}")
    plt.close()


if __name__ == "__main__":
    test_sampling_params()
