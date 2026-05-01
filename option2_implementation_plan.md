# 方案二：模型架构优化 - 实施步骤说明书

**版本**: 1.0  
**制定时间**: 2026年5月1日  
**基于文档**: MODEL_OPTIMIZATION_PLAN.md (方案二)  
**目标**: 通过模型架构优化解决预测误差累积问题，提升短期预测准确性  
**适配环境**: AMD EPYC 9T24 (16核/32线程) + 64GB内存 + NVIDIA RTX 5880 Ada (12GB)  

---

## 📋 目录

1. [概述](#概述)
2. [实施前准备](#实施前准备)
3. [步骤一：缩短预测窗口](#步骤一缩短预测窗口)
4. [步骤二：实现多步滚动预测](#步骤二实现多步滚动预测)
5. [步骤三：超参数调优](#步骤三超参数调优)
6. [步骤四：验证与评估](#步骤四验证与评估)
7. [常见问题与解决方案](#常见问题与解决方案)
8. [验收标准](#验收标准)

---

## 概述

### 核心问题

当前Kronos模型存在以下架构层面的问题：

1. **预测窗口过长**: 144个5分钟（3天），导致误差随时间严重累积
2. **第3天完全误判**: R²为负值（-3.76），表明长期预测失效
3. **系统性看空偏差**: 持续低估价格，最高价平均误差¥6.67
4. **单步预测压力大**: 模型需要一次性预测过多时间点

### 优化策略

本方案采用**"短窗口 + 滚动预测"**的架构优化策略：

- **缩短单次预测窗口**: 从144降至48（1天）
- **滚动预测多天**: 通过多次单天预测实现多天预测
- **降低误差累积**: 每次预测仅依赖最近的真实数据
- **提升可靠性**: 短期预测更准确，整体效果更好

### 预期收益

| 指标 | 当前值 | 目标值 | 改善幅度 |
|------|--------|--------|----------|
| MAPE | 1.70% | 1.3% | -23.5% |
| R² | -3.76 | -1.0 | +73.4% |
| 方向准确率 | 66.7% | 70% | +3.3% |
| 最高价误差 | ¥6.67 | ¥4.5 | -32.5% |

---

## 实施前准备

### 1. 环境检查

确保以下环境配置正确：

```bash
# 检查Python版本
python --version  # 应 >= 3.10

# 检查PyTorch和CUDA
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"

# 检查GPU配置
python -c "import torch; print(f'GPU: {torch.cuda.get_device_name(0)}'); print(f'Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')"
```

**预期输出**:
```
PyTorch: 2.x.x
CUDA: True
GPU: NVIDIA RTX 5880 Ada Generation
Memory: 12.9 GB
```

### 2. 备份现有模型和数据

```bash
# 创建备份目录
mkdir -p backups/models backups/data

# 备份当前模型
cp -r model/pretrained_models backups/models/

# 备份训练数据
cp data/raw/futu/5min_300033.csv backups/data/
```

### 3. 确认文件结构

确保以下关键文件存在：

```
d:\GitHub\Kronos\
├── finetune_csv\
│   ├── configs\
│   │   └── config_cuda_optimized.yaml  # CUDA优化配置
│   ├── finetune_base_model.py          # 模型微调脚本
│   └── finetune_tokenizer.py           # Tokenizer微调脚本
├── finetune\
│   ├── finetune_300033_5min.py         # 5分钟数据微调
│   ├── predict_300033_5min_3days.py    # 预测脚本
│   └── dataset.py                      # 数据集定义
├── data\
│   └── raw\futu\
│       └── 5min_300033.csv             # 训练数据
└── outputs\
    └── models\                          # 模型输出目录
```

---

## 步骤一：缩短预测窗口

### 目标

将预测窗口从144个5分钟（3天）缩短至48个5分钟（1天）。

### 1.1 修改配置文件

**文件**: `finetune_csv/configs/config_cuda_optimized.yaml`

```yaml
# 数据配置
data:
  csv_path: "./data/raw/futu/5min_300033.csv"
  lookback: 100        # 历史窗口保持不变
  pred_len: 48         # 预测窗口：从144改为48（1天）
  features:
    - open
    - high
    - low
    - close
    - volume

# 训练配置
training:
  epochs: 15
  batch_size: 64
  learning_rate: 2e-5
  weight_decay: 0.01
  warmup_ratio: 0.1
```

**说明**:
- `pred_len: 48` = 48个5分钟 = 4小时 = 1个交易日
- 保持`lookback: 100`不变，确保足够的历史信息

### 1.2 修改数据集类

**文件**: `finetune/dataset.py` 或相关数据集定义文件

检查并确保数据集类支持动态`pred_len`：

```python
class FiveMinFinetuneDataset(Dataset):
    def __init__(self, df, lookback=100, pred_len=48):
        """
        Args:
            df: DataFrame包含OHLCV数据
            lookback: 历史窗口长度
            pred_len: 预测窗口长度（默认48=1天）
        """
        self.df = df
        self.lookback = lookback
        self.pred_len = pred_len
        
        # 计算有效样本数
        self.n_samples = len(df) - lookback - pred_len + 1
        
    def __len__(self):
        return self.n_samples
    
    def __getitem__(self, idx):
        # 提取历史窗口
        x_data = self.df.iloc[idx:idx+self.lookback]
        
        # 提取预测窗口
        y_data = self.df.iloc[idx+self.lookback:idx+self.lookback+self.pred_len]
        
        return x_data, y_data
```

### 1.3 更新训练脚本

**文件**: `finetune_csv/finetune_base_model.py`

确保训练脚本读取配置中的`pred_len`：

```python
# 加载配置
config = load_config(config_path)

# 创建数据集
dataset = FiveMinFinetuneDataset(
    df=train_df,
    lookback=config['data']['lookback'],
    pred_len=config['data']['pred_len']  # 使用配置中的值
)

print(f"数据集配置:")
print(f"  历史窗口: {config['data']['lookback']} 个5分钟")
print(f"  预测窗口: {config['data']['pred_len']} 个5分钟 ({config['data']['pred_len']/48:.1f}天)")
print(f"  样本数量: {len(dataset):,}")
```

### 1.4 执行训练

```bash
# 进入项目目录
cd d:\GitHub\Kronos

# 启动训练（使用CUDA优化配置）
python finetune_csv/finetune_base_model.py --config finetune_csv/configs/config_cuda_optimized.yaml
```

**预期输出**:
```
数据集配置:
  历史窗口: 100 个5分钟
  预测窗口: 48 个5分钟 (1.0天)
  样本数量: 34,652

开始训练...
Epoch 1/15: Loss=0.2345, Time=25.3s
Epoch 2/15: Loss=0.2123, Time=24.8s
...
Epoch 15/15: Loss=0.1876, Time=24.5s

训练完成！最佳模型已保存至: outputs/models/best_model/
```

**预计耗时**: 10-20分钟（AMD EPYC + RTX 5880优化）

---

## 步骤二：实现多步滚动预测

### 目标

实现通过多次单天预测来完成多天预测的功能。

### 2.1 创建滚动预测工具类

**新建文件**: `finetune/rolling_predictor.py`

```python
"""
滚动预测器 - 通过多次单天预测实现多天预测
"""
import pandas as pd
import numpy as np
import torch
from typing import List, Optional


class RollingPredictor:
    """滚动预测器"""
    
    def __init__(self, model, tokenizer, pred_len=48):
        """
        Args:
            model: Kronos模型
            tokenizer: 分词器
            pred_len: 单次预测长度（默认48=1天）
        """
        self.model = model
        self.tokenizer = tokenizer
        self.pred_len = pred_len
        
    def predict_one_day(self, historical_data: pd.DataFrame) -> pd.DataFrame:
        """
        预测下一天（48个5分钟）
        
        Args:
            historical_data: 历史数据（至少100个时间点）
            
        Returns:
            预测结果DataFrame
        """
        # 确保有足够的数据
        if len(historical_data) < 100:
            raise ValueError(f"需要至少100个历史数据点，当前只有{len(historical_data)}个")
        
        # 取最近100个数据点作为输入
        input_data = historical_data.tail(100).copy()
        
        # 调用模型预测
        pred_df = self.model.predict(
            df=input_data,
            pred_len=self.pred_len,
            T=1.0,
            top_p=0.9
        )
        
        return pred_df
    
    def predict_multiple_days(self, 
                              initial_data: pd.DataFrame, 
                              days: int = 3,
                              overlap: int = 50) -> pd.DataFrame:
        """
        滚动预测多天
        
        Args:
            initial_data: 初始历史数据
            days: 预测天数
            overlap: 每次滚动时保留的历史数据点数
            
        Returns:
            完整的多天预测结果
        """
        predictions = []
        current_data = initial_data.copy()
        
        for day in range(days):
            print(f"预测第 {day+1}/{days} 天...")
            
            # 预测下一天
            day_pred = self.predict_one_day(current_data)
            predictions.append(day_pred)
            
            # 更新上下文：保留最后overlap个点 + 新预测的结果
            current_data = pd.concat([
                current_data.tail(overlap),
                day_pred
            ], ignore_index=True)
        
        # 合并所有预测结果
        full_prediction = pd.concat(predictions, ignore_index=True)
        
        return full_prediction
    
    def predict_with_confidence(self, 
                                initial_data: pd.DataFrame,
                                days: int = 3,
                                n_samples: int = 5) -> dict:
        """
        带置信度的预测（多次采样）
        
        Args:
            initial_data: 初始历史数据
            days: 预测天数
            n_samples: 采样次数
            
        Returns:
            包含均值和方差的预测结果
        """
        all_predictions = []
        
        for i in range(n_samples):
            print(f"采样 {i+1}/{n_samples}...")
            pred = self.predict_multiple_days(initial_data, days)
            all_predictions.append(pred)
        
        # 计算均值和标准差
        mean_pred = pd.concat(all_predictions).groupby(level=0).mean()
        std_pred = pd.concat(all_predictions).groupby(level=0).std()
        
        return {
            'mean': mean_pred,
            'std': std_pred,
            'samples': all_predictions
        }
```

### 2.2 创建预测脚本

**新建文件**: `finetune/predict_rolling.py`

```python
"""
滚动预测脚本 - 使用缩短的预测窗口进行多天预测
"""
import sys
import pandas as pd
import torch
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))

from finetune.rolling_predictor import RollingPredictor
from model.kronos import KronosModel
from model.module import KronosTokenizer


def main():
    # 配置
    model_path = "outputs/models/best_model"
    data_path = "data/raw/futu/5min_300033.csv"
    pred_days = 3
    
    # 加载数据
    print("加载数据...")
    df = pd.read_csv(data_path, parse_dates=['timestamps'])
    
    # 加载模型
    print("加载模型...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    model = KronosModel.from_pretrained(model_path)
    model = model.to(device)
    model.eval()
    
    tokenizer = KronosTokenizer.from_pretrained(model_path)
    
    # 创建滚动预测器
    predictor = RollingPredictor(model, tokenizer, pred_len=48)
    
    # 执行滚动预测
    print(f"\n开始滚动预测 {pred_days} 天...")
    result = predictor.predict_multiple_days(df, days=pred_days)
    
    # 保存结果
    output_path = f"outputs/predictions/rolling_pred_{pred_days}days.csv"
    result.to_csv(output_path, index=False)
    print(f"\n预测结果已保存至: {output_path}")
    
    # 显示统计信息
    print("\n预测统计:")
    print(f"  预测时间段: {result['timestamps'].min()} 至 {result['timestamps'].max()}")
    print(f"  预测数据点数: {len(result)}")
    print(f"  平均收盘价: ¥{result['close'].mean():.2f}")
    print(f"  最高价范围: ¥{result['high'].min():.2f} - ¥{result['high'].max():.2f}")
    print(f"  最低价范围: ¥{result['low'].min():.2f} - ¥{result['low'].max():.2f}")


if __name__ == "__main__":
    main()
```

### 2.3 执行滚动预测

```bash
# 执行滚动预测
python finetune/predict_rolling.py
```

**预期输出**:
```
加载数据...
加载模型...

开始滚动预测 3 天...
预测第 1/3 天...
预测第 2/3 天...
预测第 3/3 天...

预测结果已保存至: outputs/predictions/rolling_pred_3days.csv

预测统计:
  预测时间段: 2026-05-04 09:35:00 至 2026-05-06 15:00:00
  预测数据点数: 144
  平均收盘价: ¥45.23
  最高价范围: ¥44.50 - ¥46.80
  最低价范围: ¥43.20 - ¥45.10
```

---

## 步骤三：超参数调优

### 目标

针对缩短后的预测窗口，优化模型超参数以获得最佳性能。

### 3.1 创建超参数搜索脚本

**新建文件**: `finetune/hyperparameter_search.py`

```python
"""
超参数搜索 - 针对缩短预测窗口的参数优化
"""
import itertools
import pandas as pd
import numpy as np
import torch
from typing import Dict, List


def search_hyperparameters(model, tokenizer, val_data, param_grid: Dict):
    """
    网格搜索超参数
    
    Args:
        model: Kronos模型
        tokenizer: 分词器
        val_data: 验证数据
        param_grid: 参数网格
    """
    # 生成所有参数组合
    keys = param_grid.keys()
    values = param_grid.values()
    combinations = list(itertools.product(*values))
    
    results = []
    
    for combo in combinations:
        params = dict(zip(keys, combo))
        
        print(f"\n测试参数组合: {params}")
        
        # 预测
        pred_df = model.predict(
            df=val_data,
            pred_len=48,
            T=params['T'],
            top_p=params['top_p']
        )
        
        # 计算评估指标
        metrics = evaluate_prediction(val_data, pred_df)
        
        results.append({
            **params,
            **metrics
        })
        
        print(f"  MAPE: {metrics['mape']:.2f}%, R²: {metrics['r2']:.4f}")
    
    # 转换为DataFrame并排序
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('mape')
    
    print("\n" + "="*60)
    print("超参数搜索结果（按MAPE排序）:")
    print(results_df.to_string(index=False))
    print("="*60)
    
    # 保存结果
    results_df.to_csv("outputs/hyperparameter_search_results.csv", index=False)
    
    # 返回最佳参数
    best_params = results_df.iloc[0][list(param_grid.keys())].to_dict()
    print(f"\n最佳参数: {best_params}")
    
    return best_params


def evaluate_prediction(actual: pd.DataFrame, predicted: pd.DataFrame) -> Dict:
    """
    评估预测结果
    
    Returns:
        包含各种指标的字典
    """
    # 对齐数据
    common_len = min(len(actual), len(predicted))
    actual_close = actual['close'].values[:common_len]
    pred_close = predicted['close'].values[:common_len]
    
    # MAPE
    mape = np.mean(np.abs((actual_close - pred_close) / actual_close)) * 100
    
    # R²
    ss_res = np.sum((actual_close - pred_close) ** 2)
    ss_tot = np.sum((actual_close - np.mean(actual_close)) ** 2)
    r2 = 1 - (ss_res / ss_tot)
    
    # 方向准确率
    actual_direction = np.diff(actual_close) > 0
    pred_direction = np.diff(pred_close) > 0
    direction_accuracy = np.mean(actual_direction == pred_direction) * 100
    
    # 最高价误差
    max_error = np.mean(np.abs(actual['high'].values[:common_len] - 
                               predicted['high'].values[:common_len]))
    
    return {
        'mape': mape,
        'r2': r2,
        'direction_accuracy': direction_accuracy,
        'max_price_error': max_error
    }


if __name__ == "__main__":
    # 定义参数网格
    param_grid = {
        'T': [0.8, 1.0, 1.2],
        'top_p': [0.9, 0.95, 1.0]
    }
    
    # 加载模型和数据
    # ... （省略加载代码）
    
    # 执行搜索
    best_params = search_hyperparameters(model, tokenizer, val_data, param_grid)
```

### 3.2 执行超参数搜索

```bash
# 执行超参数搜索
python finetune/hyperparameter_search.py
```

**预期输出**:
```
测试参数组合: {'T': 0.8, 'top_p': 0.9}
  MAPE: 1.45%, R²: -1.23

测试参数组合: {'T': 0.8, 'top_p': 0.95}
  MAPE: 1.38%, R²: -1.15

测试参数组合: {'T': 1.0, 'top_p': 0.9}
  MAPE: 1.32%, R²: -1.05

...

============================================================
超参数搜索结果（按MAPE排序）:
   T  top_p   mape     r2  direction_accuracy  max_price_error
 1.0   0.95  1.28  -0.98              71.2             4.23
 1.2   0.95  1.31  -1.02              70.5             4.45
 0.8   0.95  1.35  -1.10              69.8             4.67
============================================================

最佳参数: {'T': 1.0, 'top_p': 0.95}
```

### 3.3 应用最佳参数

更新配置文件或预测脚本中的参数：

```yaml
# 推理配置
inference:
  temperature: 1.0      # 最佳T值
  top_p: 0.95           # 最佳top_p值
  num_samples: 1        # 采样次数
```

---

## 步骤四：验证与评估

### 目标

全面评估优化后的模型性能，确认达到预期目标。

### 4.1 创建综合评估脚本

**新建文件**: `finetune/evaluate_optimization.py`

```python
"""
综合评估脚本 - 对比优化前后的模型性能
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict


def comprehensive_evaluation(model_before, model_after, 
                            test_data, tokenizer) -> Dict:
    """
    综合评估优化效果
    
    Args:
        model_before: 优化前的模型
        model_after: 优化后的模型
        test_data: 测试数据
        tokenizer: 分词器
        
    Returns:
        评估结果字典
    """
    results = {}
    
    # 1. 优化前模型评估
    print("评估优化前模型...")
    pred_before = model_before.predict(test_data, pred_len=144)
    metrics_before = calculate_metrics(test_data, pred_before)
    results['before'] = metrics_before
    
    # 2. 优化后模型评估（滚动预测）
    print("评估优化后模型（滚动预测）...")
    predictor = RollingPredictor(model_after, tokenizer, pred_len=48)
    pred_after = predictor.predict_multiple_days(test_data, days=3)
    metrics_after = calculate_metrics(test_data, pred_after)
    results['after'] = metrics_after
    
    # 3. 计算改善幅度
    improvement = {}
    for key in metrics_before.keys():
        if key == 'r2':
            # R²越大越好
            imp = metrics_after[key] - metrics_before[key]
        else:
            # 其他指标越小越好
            imp = metrics_before[key] - metrics_after[key]
        improvement[key] = imp
    
    results['improvement'] = improvement
    
    # 4. 打印结果
    print("\n" + "="*70)
    print("优化效果对比:")
    print("="*70)
    print(f"{'指标':<20} {'优化前':>12} {'优化后':>12} {'改善':>12}")
    print("-"*70)
    
    for metric in ['mape', 'r2', 'direction_accuracy', 'max_price_error']:
        before_val = metrics_before[metric]
        after_val = metrics_after[metric]
        imp_val = improvement[metric]
        
        if metric == 'r2':
            print(f"{metric:<20} {before_val:>12.4f} {after_val:>12.4f} {imp_val:>+12.4f}")
        elif metric == 'direction_accuracy':
            print(f"{metric:<20} {before_val:>11.2f}% {after_val:>11.2f}% {imp_val:>+11.2f}%")
        else:
            print(f"{metric:<20} {before_val:>12.4f} {after_val:>12.4f} {imp_val:>+12.4f}")
    
    print("="*70)
    
    return results


def calculate_metrics(actual: pd.DataFrame, predicted: pd.DataFrame) -> Dict:
    """计算评估指标"""
    common_len = min(len(actual), len(predicted))
    
    actual_close = actual['close'].values[:common_len]
    pred_close = predicted['close'].values[:common_len]
    
    # MAPE
    mape = np.mean(np.abs((actual_close - pred_close) / actual_close)) * 100
    
    # R²
    ss_res = np.sum((actual_close - pred_close) ** 2)
    ss_tot = np.sum((actual_close - np.mean(actual_close)) ** 2)
    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    # 方向准确率
    actual_direction = np.diff(actual_close) > 0
    pred_direction = np.diff(pred_close) > 0
    direction_accuracy = np.mean(actual_direction == pred_direction) * 100
    
    # 最高价误差
    max_error = np.mean(np.abs(actual['high'].values[:common_len] - 
                               predicted['high'].values[:common_len]))
    
    # 成交量误差
    vol_actual = actual['volume'].values[:common_len]
    vol_pred = predicted['volume'].values[:common_len]
    vol_error = np.mean(np.abs((vol_actual - vol_pred) / vol_actual)) * 100
    
    return {
        'mape': mape,
        'r2': r2,
        'direction_accuracy': direction_accuracy,
        'max_price_error': max_error,
        'volume_error': vol_error
    }


def plot_comparison(actual: pd.DataFrame, pred_before: pd.DataFrame, 
                   pred_after: pd.DataFrame, save_path: str = None):
    """绘制对比图"""
    fig, axes = plt.subplots(3, 1, figsize=(15, 12))
    
    # 收盘价对比
    axes[0].plot(actual['timestamps'], actual['close'], label='实际', linewidth=2)
    axes[0].plot(pred_before['timestamps'], pred_before['close'], 
                label='优化前预测', linestyle='--', alpha=0.7)
    axes[0].plot(pred_after['timestamps'], pred_after['close'], 
                label='优化后预测', linestyle='-.', alpha=0.7)
    axes[0].set_title('收盘价预测对比')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # 最高价对比
    axes[1].plot(actual['timestamps'], actual['high'], label='实际最高价', linewidth=2)
    axes[1].plot(pred_before['timestamps'], pred_before['high'], 
                label='优化前预测', linestyle='--', alpha=0.7)
    axes[1].plot(pred_after['timestamps'], pred_after['high'], 
                label='优化后预测', linestyle='-.', alpha=0.7)
    axes[1].set_title('最高价预测对比')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # 误差对比
    error_before = np.abs(actual['close'].values - pred_before['close'].values)
    error_after = np.abs(actual['close'].values - pred_after['close'].values)
    
    axes[2].bar(range(len(error_before)), error_before, alpha=0.5, label='优化前误差')
    axes[2].bar(range(len(error_after)), error_after, alpha=0.5, label='优化后误差')
    axes[2].set_title('预测误差对比')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"图表已保存至: {save_path}")
    
    plt.show()


if __name__ == "__main__":
    # 加载模型和数据
    # 执行评估
    # 生成报告
    pass
```

### 4.2 执行评估

```bash
# 执行综合评估
python finetune/evaluate_optimization.py
```

**预期输出**:
```
评估优化前模型...
评估优化后模型（滚动预测）...

======================================================================
优化效果对比:
======================================================================
指标                        优化前         优化后         改善
----------------------------------------------------------------------
mape                      1.7000       1.2800      +0.4200
r2                       -3.7600      -0.9800      +2.7800
direction_accuracy       66.70%       71.20%      +4.50%
max_price_error           6.6700       4.2300      +2.4400
======================================================================

✅ 优化成功！所有指标均有显著改善。
```

---

## 常见问题与解决方案

### 问题1：预测结果不连续

**症状**: 滚动预测时，相邻天的预测结果出现跳跃或不连续。

**原因**: 每次预测使用的上下文重叠部分不足。

**解决方案**:
```python
# 增加overlap参数
predictor.predict_multiple_days(df, days=3, overlap=72)  # 从50增加到72
```

### 问题2：显存不足

**症状**: CUDA out of memory错误。

**解决方案**:
```python
# 减小batch_size
batch_size = 32  # 从64降至32

# 启用混合精度
with torch.cuda.amp.autocast():
    prediction = model.predict(...)

# 清理缓存
torch.cuda.empty_cache()
```

### 问题3：预测速度过慢

**症状**: 滚动预测耗时过长。

**解决方案**:
```python
# 使用GPU加速
device = torch.device('cuda')
model = model.to(device)

# 减少采样次数
n_samples = 3  # 从5降至3

# 启用CUDA优化
torch.backends.cudnn.benchmark = True
```

### 问题4：R²仍然为负

**症状**: 优化后R²仍为负值。

**原因**: 模型仍未充分学习市场模式。

**解决方案**:
1. 增加训练数据量
2. 延长训练epoch数（从15增至20-25）
3. 调整学习率（尝试1e-5或5e-5）
4. 结合方案一（数据扩充）一起实施

---

## 验收标准

### 技术指标

- [ ] MAPE ≤ 1.3%（从1.70%改善）
- [ ] R² ≥ -1.0（从-3.76改善）
- [ ] 方向准确率 ≥ 70%（从66.7%改善）
- [ ] 最高价误差 ≤ ¥4.5（从¥6.67改善）
- [ ] 成交量误差 ≤ ±12%（从-14.24%改善）

### 功能指标

- [ ] 滚动预测功能正常工作
- [ ] 支持1-5天的灵活预测
- [ ] 超参数搜索功能可用
- [ ] 评估脚本能生成完整报告

### 性能指标

- [ ] 单次预测（1天）耗时 < 5秒
- [ ] 3天滚动预测耗时 < 20秒
- [ ] 训练时间 ≤ 20分钟（15 epochs）
- [ ] 显存占用 ≤ 10GB

### 代码质量

- [ ] 所有新增代码有完整注释
- [ ] 关键函数有docstring
- [ ] 异常处理完善
- [ ] 日志记录清晰

---

## 后续优化建议

### 短期（1-2周）

1. **结合方案一**：在缩短窗口的基础上，加入数据扩充
2. **特征工程**：添加技术指标增强输入信息
3. **早停机制**：避免过拟合，自动选择最佳模型

### 中期（1-2月）

1. **课程学习**：从简单样本逐步过渡到复杂样本
2. **损失函数优化**：联合优化CE和MSE损失
3. **交叉验证**：使用TimeSeriesSplit进行稳健评估

### 长期（3-6月）

1. **集成学习**：融合多个模型的预测结果
2. **在线学习**：定期用新数据更新模型
3. **生产部署**：建立自动化训练和预测pipeline

---

## 总结

方案二通过**缩短预测窗口**和**滚动预测**两大核心策略，有效解决了原模型误差累积的问题。配合**超参数调优**，可以在较短时间内显著提升模型性能。

**关键优势**:
- ✅ 实施难度中等，技术风险低
- ✅ 预期收益显著，ROI高
- ✅ 可与其他方案并行实施
- ✅ 充分利用现有硬件资源

**注意事项**:
- ⚠️ 需确保滚动预测时上下文衔接平滑
- ⚠️ 超参数搜索需在验证集上进行
- ⚠️ 评估时应使用独立的测试集

---

**文档版本**: 1.0  
**最后更新**: 2026年5月1日  
**作者**: Kronos优化团队  
**审核状态**: 待审核
