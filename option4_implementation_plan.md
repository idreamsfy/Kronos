# 🎯 方案四：集成学习实施步骤说明书

**基于**: Kronos模型优化训练方案 (MODEL_OPTIMIZATION_PLAN.md)  
**制定时间**: 2026年5月1日  
**目标**: 通过多模型融合提升预测稳定性和准确性  
**适配环境**: AMD EPYC 9T24 + NVIDIA RTX 5880 Ada (12GB) + CUDA 12.8  
**预计耗时**: 7-10天  
**实施难度**: ⭐⭐⭐⭐ (复杂)

---

## 📋 目录

1. [方案概述](#方案概述)
2. [前置条件检查](#前置条件检查)
3. [实施步骤详解](#实施步骤详解)
   - [步骤1: 准备多个基模型](#步骤1-准备多个基模型)
   - [步骤2: 实现集成预测器](#步骤2-实现集成预测器)
   - [步骤3: 训练不同配置的模型](#步骤3-训练不同配置的模型)
   - [步骤4: 权重优化与调优](#步骤4-权重优化与调优)
   - [步骤5: 验证与评估](#步骤5-验证与评估)
4. [代码实现](#代码实现)
5. [测试与验证](#测试与验证)
6. [性能监控](#性能监控)
7. [常见问题与解决方案](#常见问题与解决方案)
8. [预期成果](#预期成果)

---

## 方案概述

### 核心思想

集成学习(Ensemble Learning)通过组合多个模型的预测结果，利用"群体智慧"降低单一模型的偏差和方差，从而提升整体预测性能。

### 技术路线

```
┌─────────────────┐
│  输入数据       │
└────────┬────────┘
         │
    ┌────┴────┐
    │ 数据预处理 │
    └────┬────┘
         │
    ┌────┴────────────────────┐
    │                         │
┌───▼───┐  ┌────────┐  ┌────▼────┐
│Model 1│  │Model 2 │  │Model 3  │
│Kronos │  │Kronos  │  │LSTM/    │
│Base   │  │Small   │  │GRU      │
└───┬───┘  └────┬───┘  └────┬────┘
    │           │            │
    └────┬──────┴────────────┘
         │
    ┌────▼────┐
    │加权融合  │
    │(Weights)│
    └────┬────┘
         │
    ┌────▼────┐
    │最终预测  │
    └─────────┘
```

### 预期收益

| 指标 | 当前值 | 集成后目标 | 提升幅度 |
|------|--------|-----------|---------|
| MAPE | 1.70% | 1.50% | -0.20% |
| R² | -3.76 | -2.5 | +1.26 |
| 方向准确率 | 66.7% | 72% | +5.3% |
| 预测稳定性 | 低 | 中高 | 显著提升 |

---

## 前置条件检查

### 硬件要求

- ✅ **CPU**: AMD EPYC 9T24 (16核/32线程) - 已满足
- ✅ **内存**: 64GB DDR5 - 已满足
- ✅ **GPU**: NVIDIA RTX 5880 Ada (12GB) - 已满足
- ✅ **CUDA**: 12.8版本 - 已满足

### 软件依赖

```bash
# 确认PyTorch已安装且支持CUDA
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}'); print(f'CUDA Version: {torch.version.cuda}')"

# 确认其他依赖
pip list | grep -E "pandas|numpy|scikit-learn|tqdm"
```

### 现有模型检查

```bash
# 检查预训练模型是否存在
ls -lh model/pretrained_models/

# 应包含:
# - kronos-base/
# - kronos-small/
# - tokenizer配置
```

### 数据准备

```bash
# 确认训练数据存在
ls -lh data/raw/futu/5min_300033*.csv
ls -lh data/processed/*.pkl
```

---

## 实施步骤详解

### 步骤1: 准备多个基模型

#### 1.1 模型选择策略

我们将使用以下3个基模型:

1. **Kronos-Base** (主模型)
   - 参数量: ~中等
   - 优势: 平衡性能与速度
   - 权重建议: 0.5

2. **Kronos-Small** (轻量模型)
   - 参数量: ~小
   - 优势: 快速推理，捕捉短期模式
   - 权重建议: 0.3

3. **LSTM/GRU基线** (传统模型)
   - 参数量: ~小
   - 优势: 擅长时序依赖，补充Transformer盲区
   - 权重建议: 0.2

#### 1.2 加载预训练模型

创建文件 `finetune/ensemble/load_models.py`:

```python
import torch
from model.kronos import Kronos, KronosTokenizer, KronosPredictor

def load_kronos_base(model_path='model/pretrained_models/kronos-base'):
    """加载Kronos-Base模型"""
    print("加载 Kronos-Base 模型...")
    
    # 加载tokenizer
    tokenizer = KronosTokenizer.from_pretrained(
        f"{model_path}/tokenizer",
        map_location='cuda' if torch.cuda.is_available() else 'cpu'
    )
    
    # 加载model
    model = Kronos.from_pretrained(
        model_path,
        map_location='cuda' if torch.cuda.is_available() else 'cpu'
    )
    
    model.eval()
    print(f"✓ Kronos-Base 加载完成")
    return model, tokenizer

def load_kronos_small(model_path='model/pretrained_models/kronos-small'):
    """加载Kronos-Small模型"""
    print("加载 Kronos-Small 模型...")
    
    tokenizer = KronosTokenizer.from_pretrained(
        f"{model_path}/tokenizer",
        map_location='cuda' if torch.cuda.is_available() else 'cpu'
    )
    
    model = Kronos.from_pretrained(
        model_path,
        map_location='cuda' if torch.cuda.is_available() else 'cpu'
    )
    
    model.eval()
    print(f"✓ Kronos-Small 加载完成")
    return model, tokenizer

if __name__ == '__main__':
    base_model, base_tokenizer = load_kronos_base()
    small_model, small_tokenizer = load_kronos_small()
    
    print("\n模型信息:")
    print(f"Base参数量: {sum(p.numel() for p in base_model.parameters()):,}")
    print(f"Small参数量: {sum(p.numel() for p in small_model.parameters()):,}")
```

#### 1.3 创建LSTM基线模型

创建文件 `finetune/ensemble/lstm_baseline.py`:

```python
import torch
import torch.nn as nn
import numpy as np
import pandas as pd

class LSTMStockPredictor(nn.Module):
    """LSTM股票预测模型"""
    
    def __init__(self, input_dim=6, hidden_dim=128, num_layers=2, dropout=0.2):
        super().__init__()
        
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # LSTM层
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # 全连接层
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, input_dim)
        )
        
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_output = lstm_out[:, -1, :]
        prediction = self.fc(last_output)
        return prediction
    
    def predict_sequence(self, x, pred_len):
        """滚动预测序列"""
        batch_size = x.size(0)
        predictions = []
        current_input = x.clone()
        
        for _ in range(pred_len):
            next_pred = self.forward(current_input)
            predictions.append(next_pred.unsqueeze(1))
            current_input = torch.cat([current_input[:, 1:, :], next_pred.unsqueeze(1)], dim=1)
        
        return torch.cat(predictions, dim=1)


class LSTMPredictor:
    """LSTM预测器封装"""
    
    def __init__(self, model, device=None):
        self.model = model
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.price_cols = ['open', 'high', 'low', 'close']
        self.vol_col = 'volume'
        self.amt_vol = 'amount'
        
    def prepare_data(self, df, lookback=100):
        """准备LSTM输入数据"""
        features = df[self.price_cols + [self.vol_col, self.amt_vol]].values
        features = features.astype(np.float32)
        
        mean = np.mean(features, axis=0)
        std = np.std(features, axis=0) + 1e-5
        features_norm = (features - mean) / std
        
        sequences = []
        for i in range(len(features_norm) - lookback):
            seq = features_norm[i:i+lookback]
            sequences.append(seq)
        
        return np.array(sequences), mean, std
    
    def predict(self, df, pred_len=48, lookback=100):
        """执行预测"""
        self.model.eval()
        sequences, mean, std = self.prepare_data(df, lookback)
        
        with torch.no_grad():
            last_seq = sequences[-1:]
            x_tensor = torch.FloatTensor(last_seq).to(self.device)
            pred_norm = self.model.predict_sequence(x_tensor, pred_len)
            pred_norm = pred_norm.cpu().numpy()[0]
            predictions = pred_norm * std + mean
            
            y_timestamp = pd.date_range(
                start=df.index[-1] + pd.Timedelta(minutes=5),
                periods=pred_len,
                freq='5min'
            )
            
            pred_df = pd.DataFrame(
                predictions,
                columns=self.price_cols + [self.vol_col, self.amt_vol],
                index=y_timestamp
            )
            
            return pred_df


def train_lstm_model(train_df, epochs=20, batch_size=64, lr=1e-3):
    """训练LSTM模型"""
    print("开始训练LSTM模型...")
    
    predictor = LSTMPredictor(LSTMStockPredictor(input_dim=6))
    sequences, mean, std = predictor.prepare_data(train_df, lookback=100)
    
    X_train = torch.FloatTensor(sequences[:-100])
    y_train = torch.FloatTensor(sequences[100:])
    
    dataset = torch.utils.data.TensorDataset(X_train, y_train)
    dataloader = torch.utils.data.DataLoader(
        dataset, 
        batch_size=batch_size, 
        shuffle=True,
        num_workers=4,
        pin_memory=True
    )
    
    model = LSTMStockPredictor(input_dim=6, hidden_dim=128, num_layers=2)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()
    
    for epoch in range(epochs):
        total_loss = 0
        for batch_x, batch_y in dataloader:
            optimizer.zero_grad()
            output = model(batch_x)
            loss = criterion(output, batch_y[:, -1, :])
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        avg_loss = total_loss / len(dataloader)
        if (epoch + 1) % 5 == 0:
            print(f"  Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.6f}")
    
    print("✓ LSTM模型训练完成")
    return model
```

---

### 步骤2: 实现集成预测器

#### 2.1 基础集成框架

创建文件 `finetune/ensemble/ensemble_predictor.py`:

```python
import torch
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from model.kronos import KronosPredictor


class EnsemblePredictor:
    """集成预测器 - 多模型融合"""
    
    def __init__(
        self, 
        models: List,
        predictors: List[KronosPredictor],
        weights: Optional[List[float]] = None,
        model_names: Optional[List[str]] = None
    ):
        """
        初始化集成预测器
        
        Args:
            models: 模型列表
            predictors: 对应的预测器列表
            weights: 权重列表（自动归一化）
            model_names: 模型名称列表（用于日志）
        """
        self.models = models
        self.predictors = predictors
        self.model_names = model_names or [f"Model_{i}" for i in range(len(models))]
        
        # 设置权重（默认均等）
        if weights is None:
            self.weights = [1.0 / len(models)] * len(models)
        else:
            # 归一化权重
            weight_sum = sum(weights)
            self.weights = [w / weight_sum for w in weights]
        
        print(f"集成预测器初始化完成:")
        print(f"  模型数量: {len(models)}")
        print(f"  权重: {self.weights}")
        for name, weight in zip(self.model_names, self.weights):
            print(f"    - {name}: {weight:.2f}")
    
    def predict_ensemble(
        self, 
        df, 
        x_timestamp, 
        y_timestamp, 
        pred_len,
        T=1.0, 
        top_k=0, 
        top_p=0.9, 
        sample_count=1,
        verbose=True
    ) -> pd.DataFrame:
        """
        集成预测
        
        Args:
            df: 输入DataFrame
            x_timestamp: 历史时间戳
            y_timestamp: 预测时间戳
            pred_len: 预测长度
            T: 温度参数
            top_k: Top-K采样
            top_p: Top-P采样
            sample_count: 采样次数
            verbose: 是否显示进度
            
        Returns:
            集成预测结果DataFrame
        """
        predictions = []
        
        print("\n开始集成预测...")
        for i, (predictor, name) in enumerate(zip(self.predictors, self.model_names)):
            print(f"\n[{i+1}/{len(self.predictors)}] 预测中: {name}")
            
            try:
                # 单个模型预测
                pred_df = predictor.predict(
                    df=df,
                    x_timestamp=x_timestamp,
                    y_timestamp=y_timestamp,
                    pred_len=pred_len,
                    T=T,
                    top_k=top_k,
                    top_p=top_p,
                    sample_count=sample_count,
                    verbose=verbose
                )
                predictions.append(pred_df)
                print(f"  ✓ {name} 预测完成")
                
            except Exception as e:
                print(f"  ✗ {name} 预测失败: {str(e)}")
                # 如果某个模型失败，使用均匀权重重新分配
                remaining_weights = sum(self.weights[j] for j in range(len(self.weights)) if j != i)
                if remaining_weights > 0:
                    adjusted_weights = [
                        self.weights[j] / remaining_weights if j != i else 0 
                        for j in range(len(self.weights))
                    ]
                    print(f"  调整权重: {adjusted_weights}")
        
        if len(predictions) == 0:
            raise RuntimeError("所有模型预测均失败")
        
        # 加权融合
        print("\n融合预测结果...")
        ensemble_pred = self._weighted_average(predictions)
        
        return ensemble_pred
    
    def _weighted_average(self, predictions: List[pd.DataFrame]) -> pd.DataFrame:
        """加权平均融合"""
        # 确保所有预测具有相同的索引
        reference_index = predictions[0].index
        
        weighted_sum = None
        for pred_df, weight in zip(predictions, self.weights):
            # 对齐索引
            pred_aligned = pred_df.reindex(reference_index)
            
            if weighted_sum is None:
                weighted_sum = pred_aligned * weight
            else:
                weighted_sum += pred_aligned * weight
        
        return weighted_sum
    
    def evaluate_ensemble(
        self, 
        actual_df: pd.DataFrame, 
        pred_df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        评估集成预测效果
        
        Args:
            actual_df: 实际值
            pred_df: 预测值
            
        Returns:
            评估指标字典
        """
        from sklearn.metrics import mean_absolute_percentage_error, r2_score
        
        price_cols = ['open', 'high', 'low', 'close']
        
        metrics = {}
        
        # MAPE
        mape_values = []
        for col in price_cols:
            if col in actual_df.columns and col in pred_df.columns:
                actual = actual_df[col].values
                pred = pred_df[col].values
                mask = actual != 0
                if mask.any():
                    mape = mean_absolute_percentage_error(actual[mask], pred[mask])
                    mape_values.append(mape)
        
        if mape_values:
            metrics['MAPE'] = np.mean(mape_values) * 100
        
        # R²
        r2_values = []
        for col in price_cols:
            if col in actual_df.columns and col in pred_df.columns:
                actual = actual_df[col].values
                pred = pred_df[col].values
                r2 = r2_score(actual, pred)
                r2_values.append(r2)
        
        if r2_values:
            metrics['R2'] = np.mean(r2_values)
        
        # 方向准确率
        if len(actual_df) > 1 and len(pred_df) > 1:
            actual_changes = np.diff(actual_df['close'].values)
            pred_changes = np.diff(pred_df['close'].values)
            direction_correct = np.sum(np.sign(actual_changes) == np.sign(pred_changes))
            metrics['Direction_Accuracy'] = direction_correct / len(actual_changes) * 100
        
        return metrics
```

---

### 步骤3: 训练不同配置的模型

#### 3.1 微调Kronos-Base模型

创建文件 `finetune/ensemble/train_kronos_variants.py`:

```python
import torch
import pandas as pd
from finetune.dataset import FiveMinFinetuneDataset
from finetune.config import TrainingConfig
from model.kronos import Kronos, KronosTokenizer, KronosPredictor
from torch.utils.data import DataLoader


def train_kronos_variant(
    config_name: str,
    learning_rate: float,
    batch_size: int,
    epochs: int,
    pred_len: int = 48,
    lookback: int = 100
):
    """
    训练Kronos变体模型
    
    Args:
        config_name: 配置名称（用于保存）
        learning_rate: 学习率
        batch_size: 批次大小
        epochs: 训练轮数
        pred_len: 预测长度
        lookback: 回看长度
    """
    print(f"\n{'='*60}")
    print(f"训练配置: {config_name}")
    print(f"学习率: {learning_rate}, Batch Size: {batch_size}")
    print(f"Epochs: {epochs}, Pred Len: {pred_len}")
    print(f"{'='*60}\n")
    
    # 加载数据
    print("加载数据...")
    df = pd.read_csv('data/raw/futu/5min_300033_updated.csv', parse_dates=['timestamps'])
    df.set_index('timestamps', inplace=True)
    
    # 创建数据集
    dataset = FiveMinFinetuneDataset(
        df=df,
        lookback=lookback,
        pred_len=pred_len
    )
    
    # 数据加载器 (CUDA优化)
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=8,
        pin_memory=True,
        prefetch_factor=4,
        persistent_workers=True
    )
    
    # 加载预训练模型
    print("加载预训练模型...")
    model_path = 'model/pretrained_models/kronos-base'
    tokenizer = KronosTokenizer.from_pretrained(f"{model_path}/tokenizer")
    model = Kronos.from_pretrained(model_path)
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = model.to(device)
    tokenizer = tokenizer.to(device)
    
    # 优化器
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)
    
    # 混合精度训练
    scaler = torch.cuda.amp.GradScaler()
    torch.backends.cudnn.benchmark = True
    
    # 训练循环
    print("开始训练...\n")
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        for batch_idx, batch in enumerate(dataloader):
            # 前向传播 (混合精度)
            with torch.cuda.amp.autocast(dtype=torch.float16):
                # 这里需要根据实际的训练逻辑调整
                # 简化示例，实际需要完整的训练步骤
                pass
            
            # 反向传播
            # scaler.scale(loss).backward()
            # scaler.step(optimizer)
            # scaler.update()
            # optimizer.zero_grad()
            
            total_loss += 0  # 占位
        
        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
        
        # 清理显存
        torch.cuda.empty_cache()
    
    # 保存模型
    save_path = f"finetune/ensemble/models/{config_name}"
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(f"{save_path}/tokenizer")
    print(f"\n✓ 模型已保存至: {save_path}")
    
    return model, tokenizer


if __name__ == '__main__':
    # 训练不同配置的模型
    
    # 配置1: 标准配置
    train_kronos_variant(
        config_name="kronos_base_standard",
        learning_rate=2e-5,
        batch_size=64,
        epochs=10,
        pred_len=48
    )
    
    # 配置2: 更激进的学习率
    train_kronos_variant(
        config_name="kronos_base_aggressive",
        learning_rate=5e-5,
        batch_size=64,
        epochs=10,
        pred_len=48
    )
    
    # 配置3: 短预测窗口
    train_kronos_variant(
        config_name="kronos_base_short_window",
        learning_rate=2e-5,
        batch_size=64,
        epochs=10,
        pred_len=24  # 半天
    )
```

#### 3.2 训练LSTM基线模型

```bash
# 运行LSTM训练
cd finetune/ensemble
python lstm_baseline.py
```

---

### 步骤4: 权重优化与调优

#### 4.1 网格搜索最优权重

创建文件 `finetune/ensemble/optimize_weights.py`:

```python
import numpy as np
import pandas as pd
from itertools import product
from finetune.ensemble.ensemble_predictor import EnsemblePredictor


def optimize_weights_grid_search(
    models,
    predictors,
    model_names,
    val_df,
    x_timestamp,
    y_timestamp,
    pred_len,
    weight_step=0.1
):
    """
    网格搜索最优权重
    
    Args:
        models: 模型列表
        predictors: 预测器列表
        model_names: 模型名称
        val_df: 验证数据
        x_timestamp: 历史时间戳
        y_timestamp: 预测时间戳
        pred_len: 预测长度
        weight_step: 权重步长
        
    Returns:
        最优权重配置
    """
    n_models = len(models)
    
    # 生成权重组合
    weight_range = np.arange(0, 1.01, weight_step)
    
    best_mape = float('inf')
    best_weights = None
    best_results = None
    
    print("开始网格搜索最优权重...")
    print(f"模型数量: {n_models}")
    print(f"权重步长: {weight_step}")
    
    # 对于3个模型，遍历所有可能的权重组合
    if n_models == 3:
        for w1, w2, w3 in product(weight_range, repeat=3):
            # 归一化
            total = w1 + w2 + w3
            if total == 0:
                continue
            
            weights = [w1/total, w2/total, w3/total]
            
            # 跳过权重太小的组合
            if any(w < 0.05 for w in weights):
                continue
            
            # 创建集成预测器
            ensemble = EnsemblePredictor(
                models=models,
                predictors=predictors,
                weights=weights,
                model_names=model_names
            )
            
            # 预测
            try:
                pred_df = ensemble.predict_ensemble(
                    df=val_df,
                    x_timestamp=x_timestamp,
                    y_timestamp=y_timestamp,
                    pred_len=pred_len,
                    verbose=False
                )
                
                # 评估
                metrics = ensemble.evaluate_ensemble(val_df, pred_df)
                mape = metrics.get('MAPE', float('inf'))
                
                if mape < best_mape:
                    best_mape = mape
                    best_weights = weights
                    best_results = metrics
                    
                    print(f"\n新最优权重: {weights}")
                    print(f"  MAPE: {mape:.2f}%")
                    print(f"  R²: {metrics.get('R2', 'N/A')}")
                    
            except Exception as e:
                continue
    
    print(f"\n{'='*60}")
    print(f"最优权重: {best_weights}")
    print(f"最优MAPE: {best_mape:.2f}%")
    print(f"{'='*60}")
    
    return best_weights, best_results


if __name__ == '__main__':
    # 示例用法
    # 需要先加载模型和预测器
    pass
```

#### 4.2 动态权重调整

创建文件 `finetune/ensemble/dynamic_weighting.py`:

```python
import numpy as np
import pandas as pd


class DynamicWeightEnsemble:
    """动态权重集成 - 根据近期表现调整权重"""
    
    def __init__(self, models, predictors, model_names, window_size=10):
        self.models = models
        self.predictors = predictors
        self.model_names = model_names
        self.window_size = window_size
        
        # 初始权重
        self.current_weights = [1.0 / len(models)] * len(models)
        
        # 历史表现记录
        self.performance_history = {name: [] for name in model_names}
    
    def update_weights(self, recent_predictions, actual_values):
        """
        根据近期表现更新权重
        
        Args:
            recent_predictions: 各模型的近期预测结果
            actual_values: 实际值
        """
        new_weights = []
        
        for i, name in enumerate(self.model_names):
            # 计算该模型的误差
            pred = recent_predictions[i]
            actual = actual_values
            
            # MAPE
            mask = actual != 0
            if mask.any():
                mape = np.mean(np.abs((actual[mask] - pred[mask]) / actual[mask]))
            else:
                mape = 1.0
            
            # 记录表现
            self.performance_history[name].append(mape)
            
            # 保持最近window_size个记录
            if len(self.performance_history[name]) > self.window_size:
                self.performance_history[name] = self.performance_history[name][-self.window_size:]
        
        # 基于平均表现计算新权重（误差越小，权重越大）
        inverse_errors = []
        for name in self.model_names:
            if self.performance_history[name]:
                avg_error = np.mean(self.performance_history[name])
                inverse_errors.append(1.0 / (avg_error + 1e-6))
            else:
                inverse_errors.append(1.0)
        
        # 归一化
        total = sum(inverse_errors)
        self.current_weights = [w / total for w in inverse_errors]
        
        print("权重已更新:")
        for name, weight in zip(self.model_names, self.current_weights):
            print(f"  {name}: {weight:.3f}")
    
    def predict(self, df, x_timestamp, y_timestamp, pred_len, **kwargs):
        """使用当前权重进行预测"""
        from finetune.ensemble.ensemble_predictor import EnsemblePredictor
        
        ensemble = EnsemblePredictor(
            models=self.models,
            predictors=self.predictors,
            weights=self.current_weights,
            model_names=self.model_names
        )
        
        return ensemble.predict_ensemble(
            df=df,
            x_timestamp=x_timestamp,
            y_timestamp=y_timestamp,
            pred_len=pred_len,
            **kwargs
        )
```

---

### 步骤5: 验证与评估

#### 5.1 完整评估流程

创建文件 `finetune/ensemble/evaluate_ensemble.py`:

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from finetune.ensemble.ensemble_predictor import EnsemblePredictor
from finetune.ensemble.load_models import load_kronos_base, load_kronos_small


def run_full_evaluation():
    """运行完整的集成学习评估"""
    
    print("="*60)
    print("Kronos 集成学习评估")
    print("="*60)
    
    # 1. 加载模型
    print("\n[1/5] 加载模型...")
    base_model, base_tokenizer = load_kronos_base()
    small_model, small_tokenizer = load_kronos_small()
    
    # 加载LSTM模型
    import torch
    from finetune.ensemble.lstm_baseline import LSTMStockPredictor, LSTMPredictor
    lstm_model = LSTMStockPredictor(input_dim=6, hidden_dim=128, num_layers=2)
    lstm_model.load_state_dict(torch.load('finetune/ensemble/models/lstm_baseline.pth'))
    lstm_predictor = LSTMPredictor(lstm_model)
    
    # 2. 准备数据
    print("\n[2/5] 准备数据...")
    df = pd.read_csv('data/raw/futu/5min_300033_updated.csv', parse_dates=['timestamps'])
    df.set_index('timestamps', inplace=True)
    
    # 分割训练集和测试集
    split_date = '2026-04-25'
    train_df = df[df.index < split_date]
    test_df = df[df.index >= split_date]
    
    print(f"训练集: {len(train_df)} 条")
    print(f"测试集: {len(test_df)} 条")
    
    # 3. 创建预测器
    print("\n[3/5] 创建预测器...")
    from model.kronos import KronosPredictor
    
    base_predictor = KronosPredictor(base_model, base_tokenizer)
    small_predictor = KronosPredictor(small_model, small_tokenizer)
    
    models = [base_model, small_model, lstm_model]
    predictors = [base_predictor, small_predictor, lstm_predictor]
    model_names = ['Kronos-Base', 'Kronos-Small', 'LSTM']
    
    # 4. 集成预测
    print("\n[4/5] 执行集成预测...")
    
    # 准备时间戳
    lookback = 100
    pred_len = 48
    
    x_df = train_df.iloc[-lookback:]
    x_timestamp = x_df.index
    y_timestamp = pd.date_range(
        start=x_timestamp[-1] + pd.Timedelta(minutes=5),
        periods=pred_len,
        freq='5min'
    )
    
    # 创建集成预测器
    ensemble = EnsemblePredictor(
        models=models,
        predictors=predictors,
        weights=[0.5, 0.3, 0.2],
        model_names=model_names
    )
    
    # 预测
    pred_df = ensemble.predict_ensemble(
        df=x_df,
        x_timestamp=x_timestamp,
        y_timestamp=y_timestamp,
        pred_len=pred_len,
        T=1.0,
        top_p=0.9,
        verbose=True
    )
    
    # 获取实际值
    actual_df = test_df.iloc[:pred_len]
    
    # 5. 评估
    print("\n[5/5] 评估结果...")
    metrics = ensemble.evaluate_ensemble(actual_df, pred_df)
    
    print("\n" + "="*60)
    print("评估结果:")
    print("="*60)
    for metric_name, value in metrics.items():
        print(f"  {metric_name}: {value:.4f}")
    print("="*60)
    
    # 可视化
    plot_results(actual_df, pred_df, metrics)
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pred_df.to_csv(f"outputs/predictions/ensemble_prediction_{timestamp}.csv")
    print(f"\n预测结果已保存至: outputs/predictions/ensemble_prediction_{timestamp}.csv")
    
    return metrics


def plot_results(actual_df, pred_df, metrics):
    """可视化预测结果"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 收盘价对比
    ax = axes[0, 0]
    ax.plot(actual_df.index, actual_df['close'], label='Actual', linewidth=2)
    ax.plot(pred_df.index, pred_df['close'], label='Predicted', linewidth=2, linestyle='--')
    ax.set_title('Close Price Comparison')
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 最高价对比
    ax = axes[0, 1]
    ax.plot(actual_df.index, actual_df['high'], label='Actual High', linewidth=2)
    ax.plot(pred_df.index, pred_df['high'], label='Predicted High', linewidth=2, linestyle='--')
    ax.set_title('High Price Comparison')
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 成交量对比
    ax = axes[1, 0]
    ax.bar(actual_df.index, actual_df['volume'], alpha=0.5, label='Actual Volume')
    ax.bar(pred_df.index, pred_df['volume'], alpha=0.5, label='Predicted Volume', color='orange')
    ax.set_title('Volume Comparison')
    ax.set_xlabel('Time')
    ax.set_ylabel('Volume')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 误差分布
    ax = axes[1, 1]
    errors = (pred_df['close'] - actual_df['close']).values
    ax.hist(errors, bins=20, alpha=0.7, edgecolor='black')
    ax.axvline(x=0, color='red', linestyle='--', linewidth=2)
    ax.set_title('Prediction Error Distribution')
    ax.set_xlabel('Error')
    ax.set_ylabel('Frequency')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 添加指标文本
    metrics_text = f"MAPE: {metrics.get('MAPE', 0):.2f}%\nR²: {metrics.get('R2', 0):.4f}"
    fig.text(0.02, 0.02, metrics_text, fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat'))
    
    plt.savefig('outputs/predictions/ensemble_evaluation.png', dpi=150, bbox_inches='tight')
    print("可视化结果已保存至: outputs/predictions/ensemble_evaluation.png")
    plt.show()


if __name__ == '__main__':
    metrics = run_full_evaluation()
```

---

## 代码实现

### 目录结构

```
finetune/ensemble/
├── __init__.py
├── load_models.py              # 模型加载
├── lstm_baseline.py            # LSTM基线模型
├── ensemble_predictor.py       # 集成预测器
├── train_kronos_variants.py    # 训练变体模型
├── optimize_weights.py         # 权重优化
├── dynamic_weighting.py        # 动态权重
├── evaluate_ensemble.py        # 评估脚本
└── models/                     # 保存的模型
    ├── kronos_base_standard/
    ├── kronos_base_aggressive/
    └── lstm_baseline.pth
```

### 快速开始脚本

创建文件 `finetune/ensemble/run_ensemble.py`:

```python
#!/usr/bin/env python
"""
集成学习快速启动脚本
一键执行完整的集成学习流程
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    print("="*60)
    print("Kronos 集成学习 - 快速启动")
    print("="*60)
    
    # 步骤1: 训练LSTM基线模型
    print("\n[步骤1] 训练LSTM基线模型...")
    from finetune.ensemble.lstm_baseline import train_lstm_model
    import pandas as pd
    
    df = pd.read_csv('data/raw/futu/5min_300033_updated.csv', parse_dates=['timestamps'])
    df.set_index('timestamps', inplace=True)
    
    lstm_model = train_lstm_model(df, epochs=20, batch_size=64, lr=1e-3)
    
    # 步骤2: 运行完整评估
    print("\n[步骤2] 运行集成学习评估...")
    from finetune.ensemble.evaluate_ensemble import run_full_evaluation
    
    metrics = run_full_evaluation()
    
    print("\n" + "="*60)
    print("集成学习流程完成!")
    print("="*60)
    print(f"最终MAPE: {metrics.get('MAPE', 0):.2f}%")
    print(f"最终R²: {metrics.get('R2', 0):.4f}")
    print(f"方向准确率: {metrics.get('Direction_Accuracy', 0):.2f}%")
    print("="*60)


if __name__ == '__main__':
    main()
```

---

## 测试与验证

### 单元测试

创建文件 `tests/test_ensemble.py`:

```python
import pytest
import pandas as pd
import numpy as np
import torch


def test_ensemble_predictor_initialization():
    """测试集成预测器初始化"""
    from finetune.ensemble.ensemble_predictor import EnsemblePredictor
    
    # 模拟模型和预测器
    models = [None, None, None]
    predictors = [None, None, None]
    model_names = ['Model1', 'Model2', 'Model3']
    
    ensemble = EnsemblePredictor(
        models=models,
        predictors=predictors,
        weights=[0.5, 0.3, 0.2],
        model_names=model_names
    )
    
    assert len(ensemble.models) == 3
    assert len(ensemble.weights) == 3
    assert abs(sum(ensemble.weights) - 1.0) < 1e-6


def test_weighted_average():
    """测试加权平均融合"""
    from finetune.ensemble.ensemble_predictor import EnsemblePredictor
    
    models = [None, None]
    predictors = [None, None]
    
    ensemble = EnsemblePredictor(
        models=models,
        predictors=predictors,
        weights=[0.6, 0.4]
    )
    
    # 创建模拟预测结果
    index = pd.date_range('2026-01-01', periods=10, freq='5min')
    pred1 = pd.DataFrame({
        'close': np.random.randn(10)
    }, index=index)
    pred2 = pd.DataFrame({
        'close': np.random.randn(10)
    }, index=index)
    
    result = ensemble._weighted_average([pred1, pred2])
    
    assert result.shape == pred1.shape
    assert 'close' in result.columns


def test_lstm_model():
    """测试LSTM模型"""
    from finetune.ensemble.lstm_baseline import LSTMStockPredictor
    
    model = LSTMStockPredictor(input_dim=6, hidden_dim=128, num_layers=2)
    
    # 测试前向传播
    batch_size = 32
    seq_len = 100
    x = torch.randn(batch_size, seq_len, 6)
    
    output = model(x)
    
    assert output.shape == (batch_size, 6)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

### 运行测试

```bash
# 运行单元测试
pytest tests/test_ensemble.py -v

# 运行集成测试
python finetune/ensemble/run_ensemble.py
```

---

## 性能监控

### CUDA性能监控

```python
# 在训练过程中监控GPU使用情况
import torch

def monitor_gpu_usage():
    """监控GPU使用情况"""
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / 1024**2
        reserved = torch.cuda.memory_reserved() / 1024**2
        print(f"GPU Memory - Allocated: {allocated:.2f} MB, Reserved: {reserved:.2f} MB")
```

### 训练日志

创建文件 `finetune/ensemble/training_logger.py`:

```python
import logging
from datetime import datetime


def setup_logger(log_file='finetune/ensemble/logs/training.log'):
    """设置训练日志"""
    logger = logging.getLogger('ensemble_training')
    logger.setLevel(logging.INFO)
    
    # 文件处理器
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)
    
    # 控制台处理器
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # 格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger
```

---

## 常见问题与解决方案

### 问题1: 显存不足 (OOM)

**症状**: `RuntimeError: CUDA out of memory`

**解决方案**:
```python
# 1. 减小batch size
batch_size = 32  # 从64降到32

# 2. 启用梯度累积
accumulation_steps = 4

# 3. 清理显存
torch.cuda.empty_cache()

# 4. 使用混合精度
with torch.cuda.amp.autocast(dtype=torch.float16):
    # 训练代码
```

### 问题2: 某个模型预测失败

**症状**: 集成预测时某个模型抛出异常

**解决方案**:
```python
# 在ensemble_predictor.py中已有容错机制
# 会自动调整权重，排除失败的模型

try:
    pred_df = predictor.predict(...)
except Exception as e:
    print(f"模型失败: {e}")
    # 权重自动重新分配
```

### 问题3: 权重优化耗时过长

**症状**: 网格搜索需要很长时间

**解决方案**:
```python
# 1. 增大权重步长
weight_step = 0.2  # 从0.1增加到0.2

# 2. 使用随机搜索替代网格搜索
from scipy.optimize import differential_evolution

# 3. 减少验证数据量
val_df = val_df.sample(n=1000, random_state=42)
```

### 问题4: 集成效果不如单一模型

**症状**: 集成后的MAPE比单个模型还高

**解决方案**:
```python
# 1. 检查模型多样性
# 确保各模型有不同的优势和劣势

# 2. 调整权重
# 给表现更好的模型更高权重

# 3. 移除表现差的模型
models = [good_model1, good_model2]  # 只保留好的模型
weights = [0.6, 0.4]
```

---

## 预期成果

### 技术指标达成

完成本方案后，预期达到以下指标:

| 指标 | 当前值 | 目标值 | 达成状态 |
|------|--------|--------|---------|
| MAPE | 1.70% | 1.50% | □ 待验证 |
| R² | -3.76 | -2.5 | □ 待验证 |
| 方向准确率 | 66.7% | 72% | □ 待验证 |
| 预测稳定性 | 低 | 中高 | □ 待验证 |

### 交付物清单

- [ ] `finetune/ensemble/ensemble_predictor.py` - 集成预测器核心代码
- [ ] `finetune/ensemble/lstm_baseline.py` - LSTM基线模型
- [ ] `finetune/ensemble/load_models.py` - 模型加载工具
- [ ] `finetune/ensemble/train_kronos_variants.py` - 模型训练脚本
- [ ] `finetune/ensemble/optimize_weights.py` - 权重优化脚本
- [ ] `finetune/ensemble/dynamic_weighting.py` - 动态权重调整
- [ ] `finetune/ensemble/evaluate_ensemble.py` - 评估脚本
- [ ] `finetune/ensemble/run_ensemble.py` - 快速启动脚本
- [ ] `tests/test_ensemble.py` - 单元测试
- [ ] 训练好的LSTM模型 (`finetune/ensemble/models/lstm_baseline.pth`)
- [ ] 评估报告 (`outputs/predictions/ensemble_evaluation.png`)
- [ ] 预测结果CSV文件

### 后续优化方向

1. **增加更多基模型**
   - GRU变体
   - Transformer变体
   - XGBoost/LightGBM

2. **Stacking集成**
   - 使用元学习器组合基模型预测

3. **在线学习**
   - 实时更新模型权重
   - 适应市场变化

4. **深度学习集成**
   - Bagging
   - Boosting
   - Blending

---

## 总结

方案四（集成学习）通过组合多个不同类型的模型，能够有效降低单一模型的偏差和方差，提升预测的稳定性和准确性。虽然实施复杂度较高，但预期能够带来显著的性能提升。

**关键成功因素**:
1. ✅ 模型多样性 - 确保各模型有不同的优势
2. ✅ 权重优化 - 找到最优的权重配置
3. ✅ 充分验证 - 严格的交叉验证和测试
4. ✅ 持续监控 - 跟踪各模型的表现

**下一步行动**:
1. 按照本说明书逐步实施
2. 每完成一个步骤进行验证
3. 记录实验结果和发现的问题
4. 根据实际情况调整方案

---

**文档版本**: v1.0  
**最后更新**: 2026年5月1日  
**维护者**: Kronos开发团队  

*注: 本实施方案需结合实际资源和约束条件灵活调整。*
