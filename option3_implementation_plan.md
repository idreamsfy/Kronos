# 方案三：训练策略优化 - 实施步骤说明书

**文档版本**: v1.0  
**制定时间**: 2026年5月1日  
**基于**: MODEL_OPTIMIZATION_PLAN.md - 方案三  
**目标**: 通过课程学习、早停机制和交叉验证提升模型训练效果  
**适配环境**: AMD EPYC 9T24 (16核/32线程) + 64GB内存 + NVIDIA RTX 5880 Ada (12GB)

---

## 📋 目录

1. [概述](#概述)
2. [实施前准备](#实施前准备)
3. [模块一：课程学习 (Curriculum Learning)](#模块一课程学习-curriculum-learning)
4. [模块二：早停和模型选择 (Early Stopping)](#模块二早停和模型选择-early-stopping)
5. [模块三：交叉验证 (Cross Validation)](#模块三交叉验证-cross-validation)
6. [集成测试与验证](#集成测试与验证)
7. [预期成果](#预期成果)
8. [风险与应对](#风险与应对)
9. [附录](#附录)

---

## 概述

### 方案三核心内容

方案三聚焦于**训练策略优化**，包含三个关键模块：

1. **课程学习 (Curriculum Learning)**: 从简单到复杂逐步训练，提升收敛稳定性
2. **早停和模型选择 (Early Stopping)**: 自动找到最佳训练轮数，避免过拟合
3. **交叉验证 (Cross Validation)**: 时间序列交叉验证，评估模型稳定性

### 预期收益

| 指标 | 当前值 | 目标值 | 提升幅度 |
|------|--------|--------|---------|
| MAPE | 1.70% | 0.9% | -47% |
| R² | -3.76 | 0.4 | +4.16 |
| 方向准确率 | 66.7% | 76% | +9.3% |
| 训练稳定性 | 低 | 高 | 显著提升 |

### 实施周期

- **总周期**: 3-4周（Day 15-28）
- **预计耗时**: 
  - 课程学习: 3-4天
  - 早停机制: 1天
  - 交叉验证: 3-5天

---

## 实施前准备

### 1. 环境检查

执行以下命令验证系统配置：

```bash
cd d:\GitHub\Kronos
python check_gpu_config.py
```

**预期输出**:
- GPU: NVIDIA RTX 5880 Ada (12GB)
- CUDA: 12.8
- 可用显存: ≥10GB
- Python: 3.10+

### 2. 备份现有代码

```bash
# 创建备份目录
mkdir backups\training_strategy_optimization

# 备份关键文件
copy finetune_csv\train_sequential.py backups\training_strategy_optimization\
copy finetune_csv\finetune_base_model.py backups\training_strategy_optimization\
copy finetune_csv\config_loader.py backups\training_strategy_optimization\
```

### 3. 确认数据路径

检查配置文件中的数据路径是否正确：

```yaml
# finetune_csv/configs/config_cuda_optimized.yaml
data:
  data_path: "./finetune_csv/data/HK_ali_09988_kline_5min_all.csv"
  lookback_window: 100
  predict_window: 48  # 已从144缩短为48
```

### 4. 安装依赖

确保已安装所需库：

```bash
pip install scikit-learn pandas numpy torch pyyaml
```

---

## 模块一：课程学习 (Curriculum Learning)

### 1.1 理论基础

**课程学习**模仿人类学习过程，从简单样本开始，逐步增加难度：

```
阶段1: 短序列 (lookback=50, pred_len=20) → 基础模式学习
阶段2: 中等序列 (lookback=75, pred_len=30) → 中期依赖学习
阶段3: 完整序列 (lookback=100, pred_len=48) → 长期依赖学习
```

**优势**:
- ✅ 更稳定的梯度下降
- ✅ 避免局部最优
- ✅ 提升最终性能

### 1.2 实施步骤

#### Step 1: 创建课程学习数据集类

**文件**: `finetune_csv/dataset_curriculum.py` (新建)

创建支持动态调整窗口大小的数据集类，允许在训练过程中改变序列长度。

**关键功能**:
- `update_windows()`: 动态更新lookback和predict窗口
- 保持与原有CustomKlineDataset兼容的数据预处理逻辑
- 支持时间序列分割（train/val/test）

#### Step 2: 实现课程学习训练器

**文件**: `finetune_csv/train_curriculum.py` (新建)

创建专门的课程学习训练器，包含三个阶段：

**阶段配置**:
```python
curriculum_stages = [
    {
        'name': 'Stage 1: Short Sequences',
        'lookback': 50,
        'pred_len': 20,
        'epochs': 3,
        'lr': 5e-5,
        'batch_size': 128
    },
    {
        'name': 'Stage 2: Medium Sequences',
        'lookback': 75,
        'pred_len': 30,
        'epochs': 3,
        'lr': 3e-5,
        'batch_size': 96
    },
    {
        'name': 'Stage 3: Full Sequences',
        'lookback': 100,
        'pred_len': 48,
        'epochs': 4,
        'lr': 2e-5,
        'batch_size': 64
    }
]
```

**训练流程**:
1. 加载预训练模型和tokenizer
2. 按顺序执行三个阶段
3. 每个阶段结束后保存中间模型
4. 记录每个阶段的训练/验证损失

**CUDA优化**:
- 启用混合精度训练 (AMP)
- 使用梯度累积 (accumulation_steps=2)
- num_workers=8 (充分利用32线程CPU)
- pin_memory=True

#### Step 3: 运行课程学习训练

```bash
cd finetune_csv
python train_curriculum.py --config configs/config_cuda_optimized.yaml
```

**监控要点**:
- 观察每个阶段的损失曲线
- 验证损失应稳步下降
- 如某阶段损失不降，考虑降低学习率或增加epochs

**预期耗时**: 
- Stage 1: ~2-3分钟 (3 epochs)
- Stage 2: ~3-4分钟 (3 epochs)
- Stage 3: ~5-6分钟 (4 epochs)
- **总计**: ~10-13分钟

### 1.3 验证课程学习效果

训练完成后，检查日志文件：

```bash
type outputs\models\{exp_name}\logs_curriculum\curriculum_training.log
```

**成功标志**:
- ✅ 三个阶段均顺利完成
- ✅ 验证损失持续下降
- ✅ 最终验证损失 < 初始损失的50%

---

## 模块二：早停和模型选择 (Early Stopping)

### 2.1 理论基础

**早停机制**监控验证集性能，当性能不再提升时自动停止训练：

```
Epoch 1: val_loss = 0.85  ← 保存
Epoch 2: val_loss = 0.72  ← 保存（最佳）
Epoch 3: val_loss = 0.75  ← counter=1
Epoch 4: val_loss = 0.78  ← counter=2
Epoch 5: val_loss = 0.80  ← counter=3 → 触发早停
```

**优势**:
- ✅ 自动找到最佳训练轮数
- ✅ 避免过拟合
- ✅ 节省训练时间和计算资源

### 2.2 实施步骤

#### Step 1: 实现EarlyStopping类

**文件**: `finetune_csv/early_stopping.py` (新建)

```python
import os
import torch

class EarlyStopping:
    """早停机制 - 监控验证损失"""
    
    def __init__(self, patience=3, min_delta=0.001, save_path=None):
        """
        Args:
            patience: 容忍多少个epoch没有改善
            min_delta: 最小改善阈值
            save_path: 最佳模型保存路径
        """
        self.patience = patience
        self.min_delta = min_delta
        self.save_path = save_path
        self.counter = 0
        self.best_loss = float('inf')
        self.early_stop = False
        self.best_epoch = 0
    
    def __call__(self, val_loss, model, epoch):
        """
        检查是否需要早停
        
        Args:
            val_loss: 当前验证损失
            model: 模型对象
            epoch: 当前epoch
        """
        if val_loss < self.best_loss - self.min_delta:
            # 有显著改善
            self.best_loss = val_loss
            self.counter = 0
            self.best_epoch = epoch
            
            # 保存最佳模型
            if self.save_path:
                os.makedirs(self.save_path, exist_ok=True)
                model.save_pretrained(self.save_path)
                print(f"  ✓ 最佳模型已保存 (Epoch {epoch}, Loss: {val_loss:.4f})")
        else:
            # 无改善
            self.counter += 1
            print(f"  ⚠ 无改善 ({self.counter}/{self.patience})")
            
            if self.counter >= self.patience:
                self.early_stop = True
                print(f"  ✗ 早停触发！最佳Epoch: {self.best_epoch}, 最佳Loss: {self.best_loss:.4f}")
    
    def reset(self):
        """重置早停状态（用于新课程阶段）"""
        self.counter = 0
        self.best_loss = float('inf')
        self.early_stop = False
        self.best_epoch = 0
```

#### Step 2: 集成到训练循环

修改 `finetune_csv/finetune_base_model.py` 中的 `train_model()` 函数：

**添加早停逻辑**:

```python
from early_stopping import EarlyStopping

def train_model(model, tokenizer, device, config, save_dir, logger):
    # ... 现有代码 ...
    
    # 初始化早停
    early_stopping = EarlyStopping(
        patience=config.early_stopping_patience,  # 从配置读取，默认3
        min_delta=config.early_stopping_min_delta,  # 默认0.001
        save_path=os.path.join(save_dir, "best_model_early_stop")
    )
    
    for epoch in range(config.basemodel_epochs):
        # ... 训练代码 ...
        
        # 验证
        avg_val_loss = validate(model, val_loader, device, tokenizer)
        
        # 检查早停
        early_stopping(avg_val_loss, model, epoch)
        
        if early_stopping.early_stop:
            logger.info(f"Early stopping triggered at epoch {epoch+1}")
            break
    
    return early_stopping.best_loss
```

#### Step 3: 更新配置文件

在 `finetune_csv/configs/config_cuda_optimized.yaml` 中添加早停参数：

```yaml
training:
  # ... 现有配置 ...
  early_stopping_patience: 3      # 容忍3个epoch无改善
  early_stopping_min_delta: 0.001 # 最小改善阈值
```

#### Step 4: 运行带早停的训练

```bash
cd finetune_csv
python finetune_base_model.py --config configs/config_cuda_optimized.yaml
```

**监控要点**:
- 观察验证损失变化
- 注意早停触发的epoch
- 比较早停模型与固定epoch模型的性能

**预期效果**:
- 原计划30 epochs → 实际可能在15-20 epochs停止
- 节省约30-50%训练时间
- 验证损失更低（避免过拟合）

### 2.3 验证早停效果

对比实验：

| 配置 | Epochs | Val Loss | 训练时间 | 是否过拟合 |
|------|--------|----------|---------|-----------|
| 固定30 epochs | 30 | 0.75 | 10分钟 | 是（后期上升） |
| 早停(patience=3) | 18 | 0.68 | 6分钟 | 否 |

**成功标志**:
- ✅ 早停在合适时机触发
- ✅ 早停模型的验证损失更低
- ✅ 训练时间显著减少

---

## 模块三：交叉验证 (Cross Validation)

### 3.1 理论基础

**时间序列交叉验证**将数据分为多个连续的时间段，轮流作为验证集：

```
Fold 1: [Train: 2023-2024] [Val: 2025 Q1]
Fold 2: [Train: 2023-2025 Q1] [Val: 2025 Q2]
Fold 3: [Train: 2023-2025 Q2] [Val: 2025 Q3]
Fold 4: [Train: 2023-2025 Q3] [Val: 2025 Q4]
Fold 5: [Train: 2023-2025 Q4] [Val: 2026 Q1]
```

**优势**:
- ✅ 更可靠的性能评估
- ✅ 发现模型在不同时期的稳定性
- ✅ 指导超参数调优

### 3.2 实施步骤

#### Step 1: 实现时间序列交叉验证器

**文件**: `finetune_csv/cross_validation.py` (新建)

```python
import os
import sys
import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import TimeSeriesSplit

sys.path.append('../')
from model import Kronos, KronosTokenizer
from finetune_base_model import train_model
from config_loader import CustomFinetuneConfig

class TimeSeriesCrossValidator:
    """时间序列交叉验证器"""
    
    def __init__(self, config_path='configs/config_cuda_optimized.yaml', n_splits=5):
        self.config = CustomFinetuneConfig(config_path)
        self.n_splits = n_splits
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 加载数据
        self.df = self._load_data()
        
        print(f"Total data points: {len(self.df)}")
        print(f"Time range: {self.df['timestamps'].min()} to {self.df['timestamps'].max()}")
    
    def _load_data(self):
        """加载并预处理数据"""
        df = pd.read_csv(self.config.data_path)
        df['timestamps'] = pd.to_datetime(df['timestamps'])
        df = df.sort_values('timestamps').reset_index(drop=True)
        return df
    
    def run_cross_validation(self):
        """执行时间序列交叉验证"""
        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        
        scores = []
        
        for fold, (train_idx, val_idx) in enumerate(tscv.split(self.df)):
            print(f"\n{'='*60}")
            print(f"Fold {fold+1}/{self.n_splits}")
            print(f"{'='*60}")
            
            # 分割数据
            train_df = self.df.iloc[train_idx]
            val_df = self.df.iloc[val_idx]
            
            print(f"Train size: {len(train_df)}, Val size: {len(val_df)}")
            print(f"Train period: {train_df['timestamps'].min()} to {train_df['timestamps'].max()}")
            print(f"Val period: {val_df['timestamps'].min()} to {val_df['timestamps'].max()}")
            
            # 保存临时数据文件
            train_path = f"temp_train_fold{fold+1}.csv"
            val_path = f"temp_val_fold{fold+1}.csv"
            
            train_df.to_csv(train_path, index=False)
            val_df.to_csv(val_path, index=False)
            
            try:
                # 训练模型
                score = self._train_and_evaluate_fold(
                    train_path, val_path, fold+1
                )
                scores.append(score)
                
                print(f"Fold {fold+1} Score (Val Loss): {score:.4f}")
                
            except Exception as e:
                print(f"Fold {fold+1} failed: {str(e)}")
                scores.append(float('inf'))
            
            finally:
                # 清理临时文件
                if os.path.exists(train_path):
                    os.remove(train_path)
                if os.path.exists(val_path):
                    os.remove(val_path)
        
        # 汇总结果
        valid_scores = [s for s in scores if s != float('inf')]
        if valid_scores:
            mean_score = np.mean(valid_scores)
            std_score = np.std(valid_scores)
            
            print(f"\n{'='*60}")
            print(f"Cross-Validation Results")
            print(f"{'='*60}")
            print(f"Mean Validation Loss: {mean_score:.4f} ± {std_score:.4f}")
            print(f"Number of successful folds: {len(valid_scores)}/{self.n_splits}")
            print(f"{'='*60}")
            
            return valid_scores
        else:
            print("All folds failed!")
            return []
    
    def _train_and_evaluate_fold(self, train_path, val_path, fold):
        """训练并评估单个fold"""
        # 加载模型和tokenizer
        tokenizer = KronosTokenizer.from_pretrained(self.config.finetuned_tokenizer_path)
        model = Kronos.from_pretrained(self.config.pretrained_predictor_path)
        
        tokenizer = tokenizer.to(self.device)
        model = model.to(self.device)
        
        # 创建临时配置
        temp_config = self._create_temp_config(train_path, fold)
        
        # 训练模型（使用早停）
        best_val_loss = train_model(
            model, tokenizer, self.device, temp_config,
            save_dir=f"outputs/models/cv_fold{fold}",
            logger=None  # 简化日志
        )
        
        # 清理
        del model, tokenizer
        torch.cuda.empty_cache()
        
        return best_val_loss
    
    def _create_temp_config(self, train_path, fold):
        """创建临时配置对象"""
        # 这里需要创建一个简化的配置对象
        # 实际实现时可能需要修改config_loader以支持动态数据路径
        pass
```

#### Step 2: 创建交叉验证配置文件

**文件**: `finetune_csv/configs/config_cv.yaml` (新建)

```yaml
experiment:
  name: "cross_validation_test"
  description: "5-fold time series cross-validation"
  train_tokenizer: false  # 使用已训练的tokenizer
  train_basemodel: true
  pre_trained_tokenizer: true
  pre_trained_predictor: true

data:
  data_path: "./finetune_csv/data/HK_ali_09988_kline_5min_all.csv"
  lookback_window: 100
  predict_window: 48
  clip: 5.0
  train_ratio: 0.7
  val_ratio: 0.15
  test_ratio: 0.15

training:
  basemodel_epochs: 20  # 减少epochs以加速CV
  batch_size: 64
  predictor_learning_rate: 2e-5
  num_workers: 8
  seed: 100
  early_stopping_patience: 3
  early_stopping_min_delta: 0.001

model_paths:
  exp_name: "cv_experiment"
  base_path: "./outputs/models"
  pretrained_tokenizer: "./model/pretrained_models/kronos-base/tokenizer"
  pretrained_predictor: "./model/pretrained_models/kronos-base/predictor"
  finetuned_tokenizer: "./outputs/models/{exp_name}/tokenizer/best_model"

device:
  use_cuda: true
  device_id: 0
```

#### Step 3: 运行交叉验证

```bash
cd finetune_csv
python cross_validation.py --config configs/config_cv.yaml --n_splits 5
```

**预期输出**:
```
============================================================
Fold 1/5
============================================================
Train size: 24360, Val size: 5220
Train period: 2023-01-01 to 2024-12-31
Val period: 2025-01-01 to 2025-03-31
Fold 1 Score (Val Loss): 0.7234

...

============================================================
Cross-Validation Results
============================================================
Mean Validation Loss: 0.7156 ± 0.0423
Number of successful folds: 5/5
============================================================
```

#### Step 4: 分析交叉验证结果

**关键指标**:
1. **平均验证损失**: 越低越好
2. **标准差**: 越小表示模型越稳定
3. **各fold一致性**: 检查是否有异常fold

**决策指南**:
- 如果标准差 > 0.1: 模型不稳定，需要更多数据或正则化
- 如果某fold损失显著高于其他: 检查该时期是否有特殊市场事件
- 如果所有fold损失都高: 模型容量不足或特征不够

### 3.3 验证交叉验证效果

**成功标志**:
- ✅ 所有fold顺利完成
- ✅ 平均验证损失 < 单折验证损失
- ✅ 标准差 < 0.05（表示稳定性好）

**后续行动**:
- 使用平均性能最好的超参数配置
- 在全量数据上重新训练最终模型
- 记录CV结果作为模型性能的可靠估计

---

## 集成测试与验证

### 4.1 完整训练流程测试

将三个模块集成到统一训练流程：

**文件**: `finetune_csv/train_with_all_strategies.py` (新建)

```python
"""
集成训练脚本 - 结合课程学习、早停和交叉验证
"""

import argparse
from curriculum_trainer import CurriculumTrainer
from early_stopping import EarlyStopping
from cross_validation import TimeSeriesCrossValidator

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, default='curriculum',
                       choices=['curriculum', 'early_stopping', 'cv', 'full'],
                       help='Training mode')
    parser.add_argument('--config', type=str, default='configs/config_cuda_optimized.yaml')
    args = parser.parse_args()
    
    if args.mode == 'curriculum':
        trainer = CurriculumTrainer(args.config)
        trainer.run_full_curriculum()
    
    elif args.mode == 'early_stopping':
        # 使用带早停的标准训练
        from finetune_base_model import main as train_main
        train_main()
    
    elif args.mode == 'cv':
        cv = TimeSeriesCrossValidator(args.config, n_splits=5)
        cv.run_cross_validation()
    
    elif args.mode == 'full':
        # 完整流程：CV → 课程学习 + 早停
        print("Step 1: Cross-Validation for hyperparameter tuning")
        cv = TimeSeriesCrossValidator(args.config, n_splits=3)
        scores = cv.run_cross_validation()
        
        print("\nStep 2: Curriculum Learning with Early Stopping on full data")
        trainer = CurriculumTrainer(args.config)
        trainer.run_full_curriculum()

if __name__ == '__main__':
    main()
```

### 4.2 性能对比实验

运行以下实验对比不同策略的效果：

| 实验ID | 策略组合 | 预期MAPE | 预期R² | 训练时间 |
|--------|---------|---------|--------|---------|
| Exp1 | Baseline（当前） | 1.70% | -3.76 | 10分钟 |
| Exp2 | +课程学习 | 1.30% | -1.50 | 13分钟 |
| Exp3 | +早停 | 1.25% | -1.20 | 6分钟 |
| Exp4 | 课程学习+早停 | 1.10% | 0.00 | 8分钟 |
| Exp5 | 全部策略 | 0.90% | 0.40 | 15分钟 |

**执行命令**:
```bash
# Exp2: 课程学习
python train_curriculum.py --config configs/config_cuda_optimized.yaml

# Exp3: 早停
python finetune_base_model.py --config configs/config_cuda_optimized.yaml

# Exp5: 全部策略
python train_with_all_strategies.py --mode full --config configs/config_cuda_optimized.yaml
```

### 4.3 结果记录与分析

创建结果记录表：

**文件**: `outputs/predictions/training_strategy_comparison.csv`

```csv
Experiment,Strategy,MAPE,R2,Direction_Accuracy,Max_Price_Error,Training_Time,Best_Epoch
Exp1,Baseline,1.70,-3.76,66.7,6.67,10min,5
Exp2,Curriculum,,,,,,
Exp3,Early_Stopping,,,,,,
Exp4,Curriculum+ES,,,,,,
Exp5,All_Strategies,,,,,,
```

每次实验后更新此表格。

---

## 预期成果

### 技术指标达成

| 指标 | 当前值 | 短期目标 | 中期目标 | 最终目标 |
|------|--------|---------|---------|---------|
| MAPE | 1.70% | 1.30% | 1.10% | 0.90% |
| R² | -3.76 | -1.50 | 0.00 | 0.40 |
| 方向准确率 | 66.7% | 70% | 73% | 76% |
| 最高价误差 | ¥6.67 | ¥5.0 | ¥4.5 | ¥4.0 |
| 训练稳定性 | 低 | 中 | 中高 | 高 |

### 工程成果

- ✅ 课程学习训练器 (`train_curriculum.py`)
- ✅ 早停机制 (`early_stopping.py`)
- ✅ 交叉验证器 (`cross_validation.py`)
- ✅ 集成训练脚本 (`train_with_all_strategies.py`)
- ✅ 完整的实验对比报告

### 知识积累

- ✅ 理解不同训练策略对模型性能的影响
- ✅ 掌握时间序列交叉验证方法
- ✅ 建立自动化训练pipeline的基础
- ✅ 积累超参数调优经验

---

## 风险与应对

### 技术风险

#### 1. 课程学习收敛困难

**症状**: 某个阶段损失不下降或震荡

**应对**:
- 降低该阶段学习率（减半）
- 增加该阶段epochs
- 检查数据质量（是否有异常值）
- 减小batch_size以增加梯度更新频率

#### 2. 早停过早触发

**症状**: 训练在5-10 epochs就停止，但损失仍在下降趋势

**应对**:
- 增加patience参数（3 → 5）
- 减小min_delta（0.001 → 0.0005）
- 使用平滑后的验证损失（移动平均）

#### 3. 交叉验证耗时过长

**症状**: 5折CV需要超过2小时

**应对**:
- 减少n_splits（5 → 3）
- 减少每折的epochs（20 → 10）
- 使用更大的batch_size
- 启用混合精度训练

### 资源风险

#### 1. 显存不足

**症状**: CUDA Out Of Memory错误

**应对**:
```python
# 减小batch_size
batch_size: 64 → 32

# 启用梯度累积
accumulation_steps: 2

# 启用混合精度
with torch.cuda.amp.autocast(dtype=torch.float16):
    loss = model(input)

# 定期清理
torch.cuda.empty_cache()
```

#### 2. 训练时间超出预期

**应对**:
- 优先实施早停（节省最多时间）
- 减少课程学习的阶段数（3 → 2）
- 使用更少的CV folds（5 → 3）

### 数据风险

#### 1. 数据分布偏移

**症状**: 不同fold之间性能差异大（std > 0.1）

**应对**:
- 检查各时期的市场特征
- 增加数据增强
- 使用更长的历史数据
- 考虑引入外部特征（宏观经济指标）

#### 2. 数据质量问题

**症状**: 训练损失突然飙升

**应对**:
- 检查数据是否有缺失值或异常值
- 验证OHLC逻辑正确性（high >= low等）
- 重新运行数据预处理脚本

---

## 附录

### A. 文件清单

实施过程中创建/修改的文件：

| 文件路径 | 类型 | 说明 |
|---------|------|------|
| `finetune_csv/dataset_curriculum.py` | 新建 | 课程学习数据集类 |
| `finetune_csv/train_curriculum.py` | 新建 | 课程学习训练器 |
| `finetune_csv/early_stopping.py` | 新建 | 早停机制实现 |
| `finetune_csv/cross_validation.py` | 新建 | 时间序列交叉验证器 |
| `finetune_csv/train_with_all_strategies.py` | 新建 | 集成训练脚本 |
| `finetune_csv/configs/config_cv.yaml` | 新建 | CV专用配置 |
| `finetune_csv/finetune_base_model.py` | 修改 | 集成早停逻辑 |
| `finetune_csv/configs/config_cuda_optimized.yaml` | 修改 | 添加早停参数 |

### B. 关键命令速查

```bash
# 1. 课程学习训练
cd finetune_csv
python train_curriculum.py --config configs/config_cuda_optimized.yaml

# 2. 带早停的训练
python finetune_base_model.py --config configs/config_cuda_optimized.yaml

# 3. 交叉验证
python cross_validation.py --config configs/config_cv.yaml --n_splits 5

# 4. 完整策略训练
python train_with_all_strategies.py --mode full --config configs/config_cuda_optimized.yaml

# 5. 查看训练日志
type outputs\models\{exp_name}\logs_curriculum\curriculum_training.log

# 6. 监控GPU使用
nvidia-smi -l 1
```

### C. 常见问题解答

**Q1: 课程学习一定要三个阶段吗？**

A: 不一定。可以根据实际情况调整：
- 如果数据量少，可以只用2个阶段
- 如果时间紧张，可以减少每个阶段的epochs
- 关键是保证从简单到复杂的渐进过程

**Q2: 早停的patience应该设多少？**

A: 建议从3开始，根据实验调整：
- patience=3: 适合快速实验
- patience=5: 更保守，适合最终训练
- patience=7: 非常保守，适合重要模型

**Q3: 交叉验证需要每次都从头训练吗？**

A: 是的，每个fold都需要独立训练以确保公平比较。但可以：
- 使用相同的随机种子保证可复现性
- 共享预训练模型作为起点
- 并行运行多个fold（如果有多个GPU）

**Q4: 如何判断策略是否有效？**

A: 通过对比实验：
1. 保持其他条件不变
2. 只改变一个策略
3. 比较验证集性能
4. 统计显著性检验（如t-test）

### D. 参考资料

1. **课程学习**: Bengio et al., "Curriculum Learning", ICML 2009
2. **早停**: Prechelt, "Early Stopping - But When?", LNCS 1524, 1998
3. **时间序列CV**: Bergmeir et al., "A note on the validity of cross-validation for evaluating autoregressive time series prediction", 2018
4. **PyTorch AMP**: https://pytorch.org/docs/stable/notes/amp_examples.html

### E. 下一步行动

完成方案三后，建议继续：

1. **方案四：集成学习** (Month 2)
   - 训练多个基模型
   - 实现加权融合
   - 优化权重分配

2. **模型架构升级** (Month 2-3)
   - 尝试Kronos-large
   - 优化注意力机制
   - 引入外部数据

3. **生产化部署** (Month 3)
   - 建立自动化训练pipeline
   - 实现在线学习机制
   - 部署监控系统

---

**文档结束**

*本实施计划为技术指导文档，具体实施需结合实际资源和约束条件调整。建议在实施过程中详细记录实验结果，以便后续分析和优化。*
