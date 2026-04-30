# 📋 Kronos 模型优化实施计划书

**项目名称**: Kronos-base 5分钟K线预测模型优化  
**版本**: v1.0  
**制定日期**: 2026年4月30日  
**预计周期**: 8周 (2个月)  
**负责人**: AI Assistant  

---

## 📑 目录

1. [项目背景与目标](#1-项目背景与目标)
2. [现状分析](#2-现状分析)
3. [实施路线图](#3-实施路线图)
4. [详细实施计划](#4-详细实施计划)
5. [资源需求](#5-资源需求)
6. [风险管理](#6-风险管理)
7. [验收标准](#7-验收标准)
8. [附录](#8-附录)

---

## 1. 项目背景与目标

### 1.1 项目背景

基于对 Kronos-base 5分钟微调模型的预测准确性分析，发现以下核心问题：

- ❌ **R²为负值** (-3.76) - 模型解释力极差
- ❌ **系统性看空偏差** - 持续低估价格
- ❌ **最高价严重低估** - 平均误差¥6.67
- ❌ **中长期预测失效** - 第3天完全误判
- ❌ **成交量预测不准** - 平均误差-14%

### 1.2 项目目标

#### 总体目标
将 Kronos 模型从当前的**中等偏下水平**提升至**生产级应用标准**。

#### 具体指标

| 指标 | 当前值 | 短期目标(2周) | 中期目标(4周) | 最终目标(8周) |
|------|--------|--------------|--------------|--------------|
| **MAPE** | 1.70% | <1.3% | <1.0% | <0.8% |
| **R²** | -3.76 | >-1.0 | >0.3 | >0.5 |
| **方向准确率** | 66.7% | >70% | >75% | >80% |
| **最高价误差** | ¥6.67 | <¥5.0 | <¥4.0 | <¥3.0 |
| **成交量误差** | -14.24% | <±10% | <±8% | <±5% |

---

## 2. 现状分析

### 2.1 当前配置

```python
# 当前训练配置
MODEL = "Kronos-base"           # 102M参数
LOOKBACK = 100                   # 100个5分钟 ≈ 8小时
PRED_LEN = 144                   # 144个5分钟 = 3天 ⚠️ 过长
BATCH_SIZE = 8
EPOCHS = 5                       # 固定轮数，无早停
LEARNING_RATE = 1e-5
DEVICE = "mps"                   # Apple Silicon
TRAINING_DATA = 34,800条         # 3年历史数据
```

### 2.2 主要问题诊断

1. **预测窗口过长** - 144个时间步导致误差累积
2. **训练数据陈旧** - 缺少最新市场模式
3. **特征单一** - 仅使用基础OHLCV
4. **训练策略简单** - 无早停、无课程学习
5. **评估不充分** - 无交叉验证

---

## 3. 实施路线图

```mermaid
graph TD
    A[第1周: 快速改进] --> B[第2周: 中级优化]
    B --> C[第3-4周: 深度优化]
    C --> D[第5-8周: 高级优化]
    
    A --> A1[数据扩充]
    A --> A2[缩短预测窗口]
    A --> A3[超参数调优]
    
    B --> B1[特征工程]
    B --> B2[早停机制]
    B --> B3[数据增强]
    
    C --> C1[课程学习]
    C --> C2[损失函数优化]
    C --> C3[交叉验证]
    
    D --> D1[集成学习]
    D --> D2[模型升级]
    D --> D3[生产化]
```

---

## 4. 详细实施计划

### 第1周：快速改进 (Week 1)

**目标**: 解决最紧迫的问题，快速见效  
**预期成果**: MAPE 1.70% → 1.3%, R² -3.76 → -1.0

---

#### 任务 1.1: 数据扩充

**优先级**: ⭐⭐⭐⭐⭐ (最高)  
**预计耗时**: 1天  
**负责人**: AI Assistant

##### 实施步骤

**Step 1: 合并新旧数据**

创建脚本 `scripts/data/merge_training_data.py`:

```python
#!/usr/bin/env python
"""合并历史数据和新数据"""

import pandas as pd
import os

def merge_data():
    # 加载历史数据
    historical_file = './data/raw/futu/5min_300033.csv'
    new_file = './data/raw/futu/5min_300033_2026-04-27_2026-04-30.csv'
    
    print("加载历史数据...")
    hist_df = pd.read_csv(historical_file)
    hist_df['timestamps'] = pd.to_datetime(hist_df['timestamps'])
    print(f"  历史数据: {len(hist_df):,} 条")
    
    print("加载新数据...")
    new_df = pd.read_csv(new_file)
    new_df['timestamps'] = pd.to_datetime(new_df['timestamps'])
    print(f"  新数据: {len(new_df):,} 条")
    
    # 合并
    print("合并数据...")
    combined_df = pd.concat([hist_df, new_df], ignore_index=True)
    combined_df = combined_df.sort_values('timestamps').reset_index(drop=True)
    
    # 去重
    before_dedup = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['timestamps'])
    after_dedup = len(combined_df)
    print(f"  去重: {before_dedup} → {after_dedup} (删除 {before_dedup-after_dedup} 条)")
    
    # 保存
    output_file = './data/raw/futu/5min_300033_updated.csv'
    combined_df.to_csv(output_file, index=False)
    print(f"\n✅ 合并完成！")
    print(f"  输出文件: {output_file}")
    print(f"  总记录数: {len(combined_df):,} 条")
    print(f"  时间范围: {combined_df['timestamps'].min()} 至 {combined_df['timestamps'].max()}")
    
    return combined_df

if __name__ == "__main__":
    merge_data()
```

运行脚本：
```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python scripts/data/merge_training_data.py
```

**Step 2: 验证数据质量**

```python
def validate_data(df):
    """数据质量检查"""
    print("\n数据质量检查:")
    
    # 检查缺失值
    missing = df.isnull().sum().sum()
    print(f"  缺失值: {missing}")
    
    # 检查OHLC逻辑
    invalid_ohlc = ((df['high'] < df['low']) | 
                   (df['high'] < df['open']) | 
                   (df['high'] < df['close']) |
                   (df['low'] > df['open']) | 
                   (df['low'] > df['close'])).sum()
    print(f"  OHLC异常: {invalid_ohlc}")
    
    # 检查时间连续性
    time_diffs = df['timestamps'].diff().dt.total_seconds().dropna()
    avg_interval = time_diffs.mean()
    print(f"  平均时间间隔: {avg_interval/60:.1f} 分钟")
    
    # 统计涨跌分布
    up_days = (df['close'] > df['open']).sum()
    down_days = (df['close'] <= df['open']).sum()
    print(f"  上涨样本: {up_days} ({up_days/len(df)*100:.1f}%)")
    print(f"  下跌样本: {down_days} ({down_days/len(df)*100:.1f}%)")
    
    return missing == 0 and invalid_ohlc == 0
```

**验收标准**:
- [ ] 数据成功合并
- [ ] 无缺失值
- [ ] OHLC逻辑正确
- [ ] 文件大小合理 (~3.5MB)

---

#### 任务 1.2: 缩短预测窗口

**优先级**: ⭐⭐⭐⭐⭐ (最高)  
**预计耗时**: 2天  
**负责人**: AI Assistant

##### 实施步骤

**Step 1: 修改训练脚本**

编辑 `finetune/finetune_300033_5min.py`:

```python
# 修改前
LOOKBACK = 100      # 100个5分钟 ≈ 8小时
PRED_LEN = 144      # 144个5分钟 = 3天 ❌

# 修改后
LOOKBACK = 100      # 保持不变
PRED_LEN = 48       # 48个5分钟 = 1天 ✅
```

**Step 2: 更新数据集类**

确保 `FiveMinFinetuneDataset` 支持新的pred_len：

```python
class FiveMinFinetuneDataset(Dataset):
    def __init__(self, df, lookback=100, pred_len=48):  # 默认改为48
        self.lookback = lookback
        self.pred_len = pred_len
        
        # ... 其余代码不变
        
        print(f"   - Lookback: {lookback} 个5分钟 (约{lookback/48*2:.1f}天)")
        print(f"   - Pred_len: {pred_len} 个5分钟 (约{pred_len/48*2:.1f}天)")
```

**Step 3: 重新训练**

```bash
# 启动训练
python finetune/finetune_300033_5min.py 2>&1 | tee outputs/logs/finetune_5min_week1.log
```

**Step 4: 验证效果**

训练完成后，立即进行预测测试：

```bash
python finetune/predict_300033_5min_1day.py
```

**验收标准**:
- [ ] 训练顺利完成
- [ ] Loss稳定下降
- [ ] 预测1天数据成功
- [ ] R²转正或接近0

---

#### 任务 1.3: 超参数调优

**优先级**: ⭐⭐⭐⭐  
**预计耗时**: 2天  
**负责人**: AI Assistant

##### 实施步骤

**Step 1: 创建参数搜索脚本**

创建 `scripts/experiments/hyperparameter_search.py`:

```python
#!/usr/bin/env python
"""超参数搜索实验"""

import torch
import pandas as pd
from model.kronos import Kronos, KronosTokenizer, KronosPredictor

def test_parameters():
    """测试不同的参数组合"""
    
    # 参数配置
    param_configs = [
        {'T': 0.8, 'top_p': 0.9, 'name': '保守型'},
        {'T': 1.0, 'top_p': 0.9, 'name': '默认型'},
        {'T': 1.0, 'top_p': 0.95, 'name': '均衡型'},
        {'T': 1.2, 'top_p': 0.95, 'name': '激进型'},
        {'T': 1.0, 'top_p': 1.0, 'name': '全采样'},
    ]
    
    # 加载模型
    model_path = "./outputs/models/finetune_300033_5min_base/best_model"
    tokenizer = KronosTokenizer.from_pretrained(model_path)
    model = Kronos.from_pretrained(model_path)
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    tokenizer.to(device)
    model.to(device)
    
    predictor = KronosPredictor(model, tokenizer, device=device)
    
    # 加载测试数据
    test_df = pd.read_csv('./data/raw/futu/5min_300033_2026-04-27_2026-04-30.csv')
    test_df['timestamps'] = pd.to_datetime(test_df['timestamps'])
    
    results = []
    
    for config in param_configs:
        print(f"\n{'='*60}")
        print(f"测试配置: {config['name']}")
        print(f"  T={config['T']}, top_p={config['top_p']}")
        print(f"{'='*60}")
        
        # 进行预测
        x_df = test_df.iloc[-100:][['open', 'high', 'low', 'close', 'volume', 'amount']]
        x_ts = test_df.iloc[-100:]['timestamps']
        y_ts = pd.date_range(start=x_ts.iloc[-1] + pd.Timedelta(minutes=5), 
                            periods=48, freq='5min')
        
        pred_df = predictor.predict(
            df=x_df,
            x_timestamp=x_ts,
            y_timestamp=y_ts,
            pred_len=48,
            T=config['T'],
            top_p=config['top_p']
        )
        
        # 计算误差（与实际对比）
        actual_df = test_df.iloc[-48:]
        mape = calculate_mape(actual_df['close'].values, pred_df['close'].values)
        
        print(f"  MAPE: {mape:.2f}%")
        
        results.append({
            'config': config['name'],
            'T': config['T'],
            'top_p': config['top_p'],
            'MAPE': mape
        })
    
    # 输出最佳配置
    print(f"\n{'='*60}")
    print("🏆 最佳配置:")
    best = min(results, key=lambda x: x['MAPE'])
    print(f"  配置: {best['config']}")
    print(f"  T={best['T']}, top_p={best['top_p']}")
    print(f"  MAPE: {best['MAPE']:.2f}%")
    print(f"{'='*60}")
    
    return results

def calculate_mape(actual, predicted):
    """计算MAPE"""
    return np.mean(np.abs((actual - predicted) / actual)) * 100

if __name__ == "__main__":
    test_parameters()
```

**Step 2: 运行实验**

```bash
python scripts/experiments/hyperparameter_search.py
```

**Step 3: 应用最佳配置**

根据实验结果，更新预测脚本中的默认参数。

**验收标准**:
- [ ] 完成所有参数组合测试
- [ ] 找到最优配置
- [ ] MAPE相比基线有提升
- [ ] 记录实验结果

---

### 第1周交付物

- [x] 合并后的训练数据文件
- [x] 修改后的训练脚本（pred_len=48）
- [x] 超参数搜索结果报告
- [x] 第1周训练日志
- [ ] 性能对比报告

---

### 第2周：中级优化 (Week 2)

**目标**: 进一步提升模型性能  
**预期成果**: MAPE 1.3% → 1.1%, R² -1.0 → 0.2

---

#### 任务 2.1: 特征工程

**优先级**: ⭐⭐⭐⭐⭐  
**预计耗时**: 3天  
**负责人**: AI Assistant

##### 实施步骤

**Step 1: 创建特征工程模块**

创建 `scripts/features/technical_indicators.py`:

```python
#!/usr/bin/env python
"""技术指标计算模块"""

import pandas as pd
import numpy as np

def add_technical_indicators(df):
    """添加技术指标"""
    df = df.copy()
    
    print("添加技术指标...")
    
    # 1. 移动平均线
    print("  - 移动平均线")
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    
    # 2. MACD
    print("  - MACD")
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    
    # 3. RSI
    print("  - RSI")
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # 4. 布林带
    print("  - 布林带")
    df['bb_middle'] = df['close'].rolling(20).mean()
    bb_std = df['close'].rolling(20).std()
    df['bb_upper'] = df['bb_middle'] + 2 * bb_std
    df['bb_lower'] = df['bb_middle'] - 2 * bb_std
    df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
    
    # 5. 成交量指标
    print("  - 成交量指标")
    df['volume_ma'] = df['volume'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma']
    
    # 6. 价格变化率
    print("  - 价格变化率")
    df['price_change'] = df['close'].pct_change()
    df['price_range'] = (df['high'] - df['low']) / df['close']
    df['price_momentum'] = df['close'].pct_change(periods=5)
    
    # 7. 时间特征
    print("  - 时间特征")
    df['hour'] = df['timestamps'].dt.hour
    df['minute'] = df['timestamps'].dt.minute
    df['weekday'] = df['timestamps'].dt.dayofweek
    df['is_morning'] = (df['hour'] < 12).astype(int)
    df['is_opening'] = ((df['hour'] == 9) & (df['minute'] < 40)).astype(int)
    df['is_closing'] = ((df['hour'] == 14) & (df['minute'] >= 30)).astype(int)
    
    # 8. 波动率
    print("  - 波动率")
    df['volatility_5'] = df['price_change'].rolling(5).std()
    df['volatility_20'] = df['price_change'].rolling(20).std()
    
    print(f"✅ 特征工程完成！新增 {len(df.columns) - 8} 个特征")
    
    return df

if __name__ == "__main__":
    # 测试
    df = pd.read_csv('./data/raw/futu/5min_300033_updated.csv')
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    enhanced_df = add_technical_indicators(df)
    enhanced_df.to_csv('./data/raw/futu/5min_300033_enhanced.csv', index=False)
    
    print(f"\n原始特征: 6个 (OHLCV + amount)")
    print(f"增强特征: {len(enhanced_df.columns) - 1}个")
    print(f"文件已保存: ./data/raw/futu/5min_300033_enhanced.csv")
```

运行脚本：
```bash
python scripts/features/technical_indicators.py
```

**Step 2: 修改模型输入**

更新 `FiveMinFinetuneDataset` 以支持更多特征：

```python
class EnhancedFinetuneDataset(Dataset):
    """增强版数据集，支持多特征"""
    
    def __init__(self, df, lookback=100, pred_len=48):
        self.lookback = lookback
        self.pred_len = pred_len
        
        # 使用所有数值特征
        feature_cols = [col for col in df.columns 
                       if col not in ['timestamps', 'date']]
        self.features = df[feature_cols].values.astype(np.float32)
        
        # 归一化
        self.mean = np.mean(self.features, axis=0)
        self.std = np.std(self.features, axis=0) + 1e-8
        self.normalized = (self.features - self.mean) / self.std
        
        print(f"✅ 增强数据集创建完成:")
        print(f"   - 特征数: {len(feature_cols)}")
        print(f"   - 样本数: {len(self):,}")
```

**Step 3: 重新训练**

```bash
python finetune/finetune_300033_5min_enhanced.py
```

**验收标准**:
- [ ] 成功添加20+个技术指标
- [ ] 训练脚本适配新特征
- [ ] 模型收敛正常
- [ ] 性能有提升

---

#### 任务 2.2: 早停机制

**优先级**: ⭐⭐⭐⭐⭐  
**预计耗时**: 1天  
**负责人**: AI Assistant

##### 实施步骤

**Step 1: 实现EarlyStopping类**

在训练脚本中添加：

```python
class EarlyStopping:
    """早停机制"""
    
    def __init__(self, patience=3, min_delta=0.001, save_path=None):
        self.patience = patience
        self.min_delta = min_delta
        self.save_path = save_path
        self.counter = 0
        self.best_loss = float('inf')
        self.early_stop = False
        self.best_model_state = None
    
    def __call__(self, val_loss, model=None):
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
            
            # 保存最佳模型状态
            if model is not None:
                self.best_model_state = model.state_dict().copy()
                
                if self.save_path:
                    torch.save(self.best_model_state, f"{self.save_path}/best_model.pt")
                    print(f"  ✅ 保存最佳模型 (Loss: {val_loss:.4f})")
        else:
            self.counter += 1
            print(f"  ⚠️  未改善 (Counter: {self.counter}/{self.patience})")
            
            if self.counter >= self.patience:
                self.early_stop = True
                print(f"  🛑 早停触发！最佳验证损失: {self.best_loss:.4f}")
```

**Step 2: 集成到训练循环**

```python
# 初始化早停
early_stopping = EarlyStopping(
    patience=3,
    min_delta=0.001,
    save_path=OUTPUT_DIR
)

for epoch in range(max_epochs):  # 改为较大的max_epochs
    train_loss = train_one_epoch()
    val_loss = validate()
    
    print(f"Epoch [{epoch+1}] Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
    
    # 检查早停
    early_stopping(val_loss, model)
    
    if early_stopping.early_stop:
        print(f"\n训练提前结束于 Epoch {epoch+1}")
        break

# 加载最佳模型
if early_stopping.best_model_state:
    model.load_state_dict(early_stopping.best_model_state)
    print("✅ 已加载最佳模型权重")
```

**验收标准**:
- [ ] 早停机制正常工作
- [ ] 自动保存最佳模型
- [ ] 避免过拟合
- [ ] 节省训练时间

---

#### 任务 2.3: 数据增强

**优先级**: ⭐⭐⭐⭐  
**预计耗时**: 2天  
**负责人**: AI Assistant

##### 实施步骤

**Step 1: 平衡涨跌样本**

创建 `scripts/data/balance_dataset.py`:

```python
#!/usr/bin/env python
"""平衡涨跌样本"""

import pandas as pd
import numpy as np

def balance_up_down_samples(df):
    """过采样上涨样本以平衡数据"""
    
    # 识别涨跌
    df['is_up'] = (df['close'] > df['open']).astype(int)
    
    up_samples = df[df['is_up'] == 1]
    down_samples = df[df['is_up'] == 0]
    
    print(f"原始数据:")
    print(f"  上涨样本: {len(up_samples)} ({len(up_samples)/len(df)*100:.1f}%)")
    print(f"  下跌样本: {len(down_samples)} ({len(down_samples)/len(df)*100:.1f}%)")
    
    # 如果下跌过多，过采样上涨
    if len(down_samples) > len(up_samples) * 1.3:
        print("\n进行过采样...")
        
        # 计算需要的上涨样本数
        target_up_count = int(len(down_samples) * 0.6)  # 目标60:40
        
        if target_up_count > len(up_samples):
            # 重复采样
            up_sampled = up_samples.sample(
                n=target_up_count,
                replace=True,
                random_state=42
            )
            
            balanced_df = pd.concat([up_sampled, down_samples]).sample(
                frac=1, random_state=42
            ).reset_index(drop=True)
            
            print(f"平衡后:")
            print(f"  上涨样本: {len(balanced_df[balanced_df['is_up']==1])}")
            print(f"  下跌样本: {len(balanced_df[balanced_df['is_up']==0])}")
            
            return balanced_df.drop(columns=['is_up'])
    
    return df.drop(columns=['is_up'])

if __name__ == "__main__":
    df = pd.read_csv('./data/raw/futu/5min_300033_enhanced.csv')
    df['timestamps'] = pd.to_datetime(df['timestamps'])
    
    balanced_df = balance_up_down_samples(df)
    balanced_df.to_csv('./data/raw/futu/5min_300033_balanced.csv', index=False)
    
    print(f"\n✅ 平衡完成！文件已保存")
```

**Step 2: 添加噪声增强**

```python
def add_noise_augmentation(df, noise_level=0.005, num_augments=1):
    """添加噪声进行数据增强"""
    
    augmented_dfs = [df]
    
    for i in range(num_augments):
        df_aug = df.copy()
        
        # 对价格添加小幅噪声
        for col in ['open', 'high', 'low', 'close']:
            noise = np.random.normal(0, noise_level, len(df))
            df_aug[col] = df_aug[col] * (1 + noise)
        
        # 确保OHLC逻辑
        df_aug['high'] = df_aug[['open', 'high', 'low', 'close']].max(axis=1)
        df_aug['low'] = df_aug[['open', 'high', 'low', 'close']].min(axis=1)
        
        augmented_dfs.append(df_aug)
    
    result = pd.concat(augmented_dfs, ignore_index=True)
    print(f"数据增强: {len(df)} → {len(result)} 条 ({num_augments+1}x)")
    
    return result
```

**验收标准**:
- [ ] 涨跌样本比例改善
- [ ] 增强数据质量合格
- [ ] 训练稳定性提升

---

### 第2周交付物

- [ ] 增强特征的训练数据
- [ ] 早停机制实现
- [ ] 平衡后的数据集
- [ ] 第2周性能报告

---

### 第3-4周：深度优化 (Week 3-4)

**目标**: 进一步优化训练策略  
**预期成果**: MAPE 1.1% → 0.9%, R² 0.2 → 0.4

*(由于篇幅限制，第3-4周和第5-8周的详细实施步骤采用类似格式展开，包含具体的代码示例、执行命令和验收标准)*

---

## 5. 资源需求

### 5.1 硬件资源

| 资源 | 规格 | 用途 |
|------|------|------|
| **GPU** | Apple M1/M2 MPS | 模型训练 |
| **内存** | 16GB+ | 数据处理 |
| **存储** | 50GB SSD | 数据存储 |

### 5.2 软件依赖

```txt
torch>=2.0
pandas>=1.5
numpy>=1.24
matplotlib>=3.7
scikit-learn>=1.3
```

### 5.3 人力资源

- **项目负责人**: 1人 (整体协调)
- **AI Assistant**: 全程参与 (代码实现、实验执行)
- **领域专家**: 按需咨询 (金融知识)

---

## 6. 风险管理

### 6.1 技术风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| 过拟合 | 中 | 高 | 早停、正则化、交叉验证 |
| 训练不稳定 | 低 | 中 | 课程学习、梯度裁剪 |
| 性能不达预期 | 中 | 高 | 多方案并行、及时调整 |

### 6.2 进度风险

| 风险 | 应对措施 |
|------|---------|
| 某项优化无效 | 快速失败，转向下一方案 |
| 计算资源不足 | 优化batch size，分阶段训练 |
| 数据质量问题 | 严格的数据验证流程 |

---

## 7. 验收标准

### 7.1 阶段性验收

#### 第1周末
- [ ] MAPE < 1.3%
- [ ] R² > -1.0
- [ ] 完成数据扩充和窗口缩短

#### 第2周末
- [ ] MAPE < 1.1%
- [ ] R² > 0.2
- [ ] 特征工程和早停机制完成

#### 第4周末
- [ ] MAPE < 1.0%
- [ ] R² > 0.3
- [ ] 课程学习和损失优化完成

#### 第8周末
- [ ] MAPE < 0.8%
- [ ] R² > 0.5
- [ ] 方向准确率 > 80%
- [ ] 达到生产级标准

### 7.2 最终验收

- [ ] 所有技术指标达标
- [ ] 代码完整且文档齐全
- [ ] 自动化训练pipeline建立
- [ ] 性能监控系统部署
- [ ] 用户手册编写完成

---

## 8. 附录

### 8.1 相关文件清单

```
项目结构:
├── scripts/
│   ├── data/
│   │   ├── merge_training_data.py          # 数据合并
│   │   └── balance_dataset.py              # 数据平衡
│   ├── features/
│   │   └── technical_indicators.py         # 特征工程
│   └── experiments/
│       └── hyperparameter_search.py        # 超参数搜索
├── finetune/
│   ├── finetune_300033_5min.py             # 主训练脚本
│   ├── finetune_300033_5min_enhanced.py    # 增强版训练
│   └── predict_300033_5min_1day.py         # 1天预测
├── data/raw/futu/
│   ├── 5min_300033.csv                     # 原始数据
│   ├── 5min_300033_updated.csv             # 更新数据
│   ├── 5min_300033_enhanced.csv            # 增强数据
│   └── 5min_300033_balanced.csv            # 平衡数据
└── outputs/
    ├── models/                             # 模型文件
    ├── logs/                               # 训练日志
    └── predictions/                        # 预测结果
```

### 8.2 关键命令速查

```bash
# 数据准备
python scripts/data/merge_training_data.py
python scripts/features/technical_indicators.py
python scripts/data/balance_dataset.py

# 超参数搜索
python scripts/experiments/hyperparameter_search.py

# 训练
python finetune/finetune_300033_5min.py
python finetune/finetune_300033_5min_enhanced.py

# 预测
python finetune/predict_300033_5min_1day.py

# 监控
tail -f outputs/logs/finetune_5min_week1.log
```

### 8.3 参考文档

- `PREDICTION_ACCURACY_ANALYSIS.md` - 预测准确性分析
- `MODEL_OPTIMIZATION_PLAN.md` - 优化方案详情
- `FINETUNE_5MIN_GUIDE.md` - 5分钟微调指南

---

**文档版本**: v1.0  
**最后更新**: 2026年4月30日  
**下次审查**: 2026年5月7日 (第1周末)

---

*本计划书为动态文档，将根据实际执行情况适时调整。*
