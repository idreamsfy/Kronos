# 🚀 Kronos 模型优化训练方案报告

**基于**: 预测准确性对比分析 (PREDICTION_ACCURACY_ANALYSIS.md)  
**制定时间**: 2026年4月30日  
**目标**: 解决当前模型存在的系统性问题，提升预测准确性  

---

## 📋 问题诊断总结

### 当前模型表现

| 指标 | 当前值 | 目标值 | 差距 |
|------|--------|--------|------|
| **MAPE** | 1.70% | <1.0% | -0.70% |
| **R²** | -3.76 | >0.5 | +4.26 |
| **方向准确率** | 66.7% | >75% | +8.3% |
| **最高价误差** | ¥6.67 | <¥3.0 | -¥3.67 |
| **成交量误差** | -14.24% | <±5% | +9.24% |

### 核心问题

1. ❌ **R²为负值** (-3.76) - 最严重问题
2. ❌ **系统性看空偏差** - 持续低估价格
3. ❌ **最高价严重低估** - 平均差¥6.67
4. ❌ **中长期预测失效** - 第3天完全误判
5. ❌ **成交量预测不准** - 平均误差-14%

---

## 🎯 优化目标

### 短期目标 (1-2周)

- [ ] MAPE 降至 1.2% 以下
- [ ] R² 提升至正值 (>0)
- [ ] 方向准确率提升至 70%+
- [ ] 消除系统性看空偏差

### 中期目标 (1-2月)

- [ ] MAPE 降至 1.0% 以下
- [ ] R² 提升至 0.3+
- [ ] 方向准确率提升至 75%+
- [ ] 最高价误差降至 ¥4.0 以内

### 长期目标 (3-6月)

- [ ] MAPE 降至 0.8% 以下
- [ ] R² 提升至 0.5+
- [ ] 方向准确率提升至 80%+
- [ ] 达到生产级应用标准

---

## 🔧 优化方案

### 方案一：数据层面优化 ⭐⭐⭐⭐⭐

#### 1.1 扩充训练数据集

**问题分析**:
- 当前训练数据: 34,800条 (3年历史)
- 缺少最新市场模式
- 可能存在数据分布偏差

**实施方案**:

```python
# 步骤1: 合并新旧数据
import pandas as pd

historical_df = pd.read_csv('./data/raw/futu/5min_300033.csv')
new_df = pd.read_csv('./data/raw/futu/5min_300033_2026-04-27_2026-04-30.csv')

combined_df = pd.concat([historical_df, new_df], ignore_index=True)
combined_df = combined_df.sort_values('timestamps').reset_index(drop=True)

# 步骤2: 保存更新后的数据
combined_df.to_csv('./data/raw/futu/5min_300033_updated.csv', index=False)

print(f"原始数据: {len(historical_df):,} 条")
print(f"新增数据: {len(new_df):,} 条")
print(f"合并后: {len(combined_df):,} 条")
```

**预期效果**:
- 增加最新市场模式
- 改善数据分布
- 提升模型适应性

**优先级**: ⭐⭐⭐⭐⭐ (最高)  
**实施难度**: ⭐ (简单)  
**预计耗时**: 1天

---

#### 1.2 数据增强策略

**问题分析**:
- 训练数据中上涨行情样本不足
- 导致模型学习到悲观模式
- 需要平衡数据分布

**实施方案**:

```python
# 方法1: 过采样上涨行情
up_trend_mask = combined_df['close'] > combined_df['open']
down_trend_mask = combined_df['close'] <= combined_df['open']

up_samples = combined_df[up_trend_mask]
down_samples = combined_df[down_trend_mask]

print(f"上涨样本: {len(up_samples)} ({len(up_samples)/len(combined_df)*100:.1f}%)")
print(f"下跌样本: {len(down_samples)} ({len(down_samples)/len(combined_df)*100:.1f}%)")

# 如果下跌样本过多，进行过采样
if len(down_samples) > len(up_samples) * 1.5:
    # 重复采样上涨样本
    up_sampled = up_samples.sample(
        n=len(down_samples), 
        replace=True, 
        random_state=42
    )
    balanced_df = pd.concat([up_sampled, down_samples])
    print(f"平衡后数据: {len(balanced_df)} 条")
```

**方法2: 添加噪声增强**
```python
import numpy as np

def add_noise(df, noise_level=0.01):
    """添加小幅噪声进行数据增强"""
    df_augmented = df.copy()
    
    # 对价格添加噪声
    for col in ['open', 'high', 'low', 'close']:
        noise = np.random.normal(0, noise_level, len(df))
        df_augmented[col] = df_augmented[col] * (1 + noise)
    
    # 确保OHLC逻辑正确
    df_augmented['high'] = df_augmented[['open', 'high', 'low', 'close']].max(axis=1)
    df_augmented['low'] = df_augmented[['open', 'high', 'low', 'close']].min(axis=1)
    
    return df_augmented

# 生成增强数据
augmented_df = add_noise(combined_df, noise_level=0.005)
final_df = pd.concat([combined_df, augmented_df], ignore_index=True)
```

**预期效果**:
- 平衡涨跌样本比例
- 增加模型鲁棒性
- 减少过拟合风险

**优先级**: ⭐⭐⭐⭐  
**实施难度**: ⭐⭐ (中等)  
**预计耗时**: 2天

---

#### 1.3 特征工程增强

**问题分析**:
- 当前仅使用基础OHLCV数据
- 缺少技术指标和市场情绪因子
- 信息量不足

**实施方案**:

```python
def add_technical_indicators(df):
    """添加技术指标"""
    df = df.copy()
    
    # 1. 移动平均线
    df['ma5'] = df['close'].rolling(5).mean()
    df['ma10'] = df['close'].rolling(10).mean()
    df['ma20'] = df['close'].rolling(20).mean()
    
    # 2. MACD
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    
    # 3. RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # 4. 布林带
    df['bb_middle'] = df['close'].rolling(20).mean()
    bb_std = df['close'].rolling(20).std()
    df['bb_upper'] = df['bb_middle'] + 2 * bb_std
    df['bb_lower'] = df['bb_middle'] - 2 * bb_std
    
    # 5. 成交量指标
    df['volume_ma'] = df['volume'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / df['volume_ma']
    
    # 6. 价格变化率
    df['price_change'] = df['close'].pct_change()
    df['price_range'] = (df['high'] - df['low']) / df['close']
    
    # 7. 时间特征
    df['hour'] = df['timestamps'].dt.hour
    df['minute'] = df['timestamps'].dt.minute
    df['weekday'] = df['timestamps'].dt.dayofweek
    df['is_morning'] = (df['hour'] < 12).astype(int)
    
    return df

# 应用特征工程
enhanced_df = add_technical_indicators(combined_df)
print(f"原始特征数: 6")
print(f"增强后特征数: {len(enhanced_df.columns) - 1}")  # 减去timestamps
```

**新增特征列表**:
- 移动平均线 (MA5, MA10, MA20)
- MACD及信号线
- RSI (相对强弱指标)
- 布林带 (上轨、中轨、下轨)
- 成交量比率
- 价格变化率和波动范围
- 时间特征 (小时、分钟、星期、时段)

**预期效果**:
- 提供更丰富的市场信息
- 帮助模型捕捉复杂模式
- 提升预测准确性

**优先级**: ⭐⭐⭐⭐⭐  
**实施难度**: ⭐⭐⭐ (较复杂)  
**预计耗时**: 3-5天

---

### 方案二：模型架构优化 ⭐⭐⭐⭐

#### 2.1 缩短预测窗口

**问题分析**:
- 当前预测窗口: 144个5分钟 (3天)
- 误差随时间累积严重
- 第3天完全误判

**实施方案**:

```python
# 修改训练配置
LOOKBACK = 100      # 保持不变
PRED_LEN = 48       # 从144改为48 (1天)

# 重新创建数据集
dataset = FiveMinFinetuneDataset(
    df=enhanced_df,
    lookback=LOOKBACK,
    pred_len=PRED_LEN
)

print(f"预测窗口: {PRED_LEN}个5分钟 = {PRED_LEN/48:.1f}天")
```

**多步预测策略**:
```python
# 如果需要预测3天，采用滚动预测
def multi_step_prediction(model, tokenizer, initial_data, days=3):
    """滚动预测多天"""
    predictions = []
    current_data = initial_data.copy()
    
    for day in range(days):
        # 预测下一天
        pred = predict_one_day(model, tokenizer, current_data)
        predictions.append(pred)
        
        # 将预测结果加入上下文
        current_data = pd.concat([current_data.iloc[-50:], pred])
    
    return pd.concat(predictions)
```

**预期效果**:
- 大幅降低单步预测误差
- 提高短期预测可靠性
- R²有望转正

**优先级**: ⭐⭐⭐⭐⭐  
**实施难度**: ⭐⭐ (中等)  
**预计耗时**: 2天

---

#### 2.2 调整模型超参数

**问题分析**:
- Temperature=1.0 可能不够灵活
- Top-p=0.9 限制了多样性
- 学习率可能需要调整

**实施方案**:

```python
# 实验不同的参数组合
param_configs = [
    {'T': 0.8, 'top_p': 0.9, 'name': '保守型'},
    {'T': 1.0, 'top_p': 0.95, 'name': '均衡型'},
    {'T': 1.2, 'top_p': 0.95, 'name': '激进型'},
    {'T': 1.0, 'top_p': 1.0, 'name': '全采样'},
]

for config in param_configs:
    print(f"\n测试配置: {config['name']}")
    print(f"  T={config['T']}, top_p={config['top_p']}")
    
    pred_df = predictor.predict(
        df=x_df,
        x_timestamp=x_ts,
        y_timestamp=y_ts,
        pred_len=PRED_LEN,
        T=config['T'],
        top_p=config['top_p']
    )
    
    # 计算误差
    mape = calculate_mape(actual, pred_df)
    print(f"  MAPE: {mape:.2f}%")
```

**学习率调整**:
```python
# 尝试不同的学习率
learning_rates = [5e-6, 1e-5, 2e-5, 5e-5]

for lr in learning_rates:
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=lr,
        weight_decay=0.01
    )
    
    # 训练并验证
    train_and_evaluate(model, optimizer, epochs=5)
```

**预期效果**:
- 找到最优参数组合
- 平衡稳定性和灵活性
- 提升预测质量

**优先级**: ⭐⭐⭐⭐  
**实施难度**: ⭐ (简单)  
**预计耗时**: 2-3天

---

#### 2.3 损失函数优化

**问题分析**:
- 当前使用简单的CrossEntropyLoss
- 未考虑价格预测的特殊性
- 可能对极端值惩罚不足

**实施方案**:

```python
class CustomLoss(nn.Module):
    """自定义损失函数"""
    
    def __init__(self, alpha=1.0, beta=0.5):
        super().__init__()
        self.alpha = alpha  # CE损失权重
        self.beta = beta    # 回归损失权重
        self.ce_loss = nn.CrossEntropyLoss()
        self.mse_loss = nn.MSELoss()
    
    def forward(self, s1_logits, s2_logits, target_s1, target_s2, 
                pred_prices, actual_prices):
        # Token预测损失
        ce_loss = self.ce_loss(s1_logits.reshape(-1, s1_logits.size(-1)), 
                               target_s1.reshape(-1))
        ce_loss += self.ce_loss(s2_logits.reshape(-1, s2_logits.size(-1)), 
                                target_s2.reshape(-1))
        
        # 价格回归损失 (额外监督)
        reg_loss = self.mse_loss(pred_prices, actual_prices)
        
        return self.alpha * ce_loss + self.beta * reg_loss

# 使用自定义损失
criterion = CustomLoss(alpha=1.0, beta=0.3)
```

**预期效果**:
- 直接优化价格预测
- 减少量化误差影响
- 提升数值准确性

**优先级**: ⭐⭐⭐  
**实施难度**: ⭐⭐⭐⭐ (复杂)  
**预计耗时**: 5-7天

---

### 方案三：训练策略优化 ⭐⭐⭐⭐⭐

#### 3.1 课程学习 (Curriculum Learning)

**问题分析**:
- 直接从困难样本开始训练
- 模型难以收敛
- 需要循序渐进

**实施方案**:

```python
def curriculum_training(model, dataset, epochs=10):
    """课程学习训练"""
    
    # 阶段1: 简单样本 (短序列)
    print("阶段1: 训练短序列 (lookback=50)")
    simple_dataset = FiveMinFinetuneDataset(df, lookback=50, pred_len=20)
    train_epoch(model, simple_dataset, epochs=3)
    
    # 阶段2: 中等样本
    print("阶段2: 训练中等序列 (lookback=75)")
    medium_dataset = FiveMinFinetuneDataset(df, lookback=75, pred_len=30)
    train_epoch(model, medium_dataset, epochs=3)
    
    # 阶段3: 完整样本
    print("阶段3: 训练完整序列 (lookback=100)")
    full_dataset = FiveMinFinetuneDataset(df, lookback=100, pred_len=48)
    train_epoch(model, full_dataset, epochs=4)

def train_epoch(model, dataset, epochs):
    """训练一个阶段"""
    dataloader = DataLoader(dataset, batch_size=8, shuffle=True)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)
    
    for epoch in range(epochs):
        total_loss = 0
        for batch in dataloader:
            # 训练步骤
            loss = train_step(model, batch, optimizer)
            total_loss += loss
        
        avg_loss = total_loss / len(dataloader)
        print(f"  Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
```

**预期效果**:
- 更稳定的训练过程
- 更好的收敛性
- 提升最终性能

**优先级**: ⭐⭐⭐⭐  
**实施难度**: ⭐⭐⭐ (较复杂)  
**预计耗时**: 3-4天

---

#### 3.2 早停和模型选择

**问题分析**:
- 当前固定训练5个epoch
- 可能欠拟合或过拟合
- 需要智能停止机制

**实施方案**:

```python
class EarlyStopping:
    """早停机制"""
    
    def __init__(self, patience=3, min_delta=0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = float('inf')
        self.early_stop = False
    
    def __call__(self, val_loss):
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
            # 保存最佳模型
            save_best_model()
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True

# 使用早停
early_stopping = EarlyStopping(patience=3, min_delta=0.001)

for epoch in range(max_epochs):
    train_loss = train_one_epoch()
    val_loss = validate()
    
    early_stopping(val_loss)
    
    if early_stopping.early_stop:
        print(f"早停触发！最佳验证损失: {early_stopping.best_loss:.4f}")
        break
```

**预期效果**:
- 自动找到最佳训练轮数
- 避免过拟合
- 节省训练时间

**优先级**: ⭐⭐⭐⭐⭐  
**实施难度**: ⭐⭐ (中等)  
**预计耗时**: 1天

---

#### 3.3 交叉验证

**问题分析**:
- 当前仅使用单一训练/测试分割
- 评估结果可能有偏差
- 需要更可靠的评估

**实施方案**:

```python
from sklearn.model_selection import TimeSeriesSplit

def time_series_cross_validation(model_class, df, n_splits=5):
    """时间序列交叉验证"""
    
    tscv = TimeSeriesSplit(n_splits=n_splits)
    scores = []
    
    for fold, (train_idx, val_idx) in enumerate(tscv.split(df)):
        print(f"\nFold {fold+1}/{n_splits}")
        
        train_df = df.iloc[train_idx]
        val_df = df.iloc[val_idx]
        
        # 训练模型
        model = model_class()
        train_model(model, train_df)
        
        # 验证
        val_score = evaluate(model, val_df)
        scores.append(val_score)
        
        print(f"  Validation Score: {val_score:.4f}")
    
    print(f"\n平均得分: {np.mean(scores):.4f} ± {np.std(scores):.4f}")
    return scores

# 执行交叉验证
scores = time_series_cross_validation(KronosModel, enhanced_df, n_splits=5)
```

**预期效果**:
- 更可靠的性能评估
- 发现模型稳定性问题
- 指导超参数调优

**优先级**: ⭐⭐⭐  
**实施难度**: ⭐⭐⭐ (较复杂)  
**预计耗时**: 3-5天

---

### 方案四：集成学习 ⭐⭐⭐

#### 4.1 多模型融合

**问题分析**:
- 单一模型存在局限性
- 不同模型擅长不同场景
- 融合可提升稳定性

**实施方案**:

```python
class EnsemblePredictor:
    """集成预测器"""
    
    def __init__(self, models, weights=None):
        self.models = models
        self.weights = weights or [1/len(models)] * len(models)
    
    def predict(self, data):
        """加权平均预测"""
        predictions = []
        
        for model in self.models:
            pred = model.predict(data)
            predictions.append(pred)
        
        # 加权平均
        ensemble_pred = np.average(predictions, axis=0, weights=self.weights)
        return ensemble_pred

# 创建集成模型
models = [
    kronos_base_model,      # Kronos-base
    kronos_small_model,     # Kronos-small
    lstm_model,             # LSTM基线
]

ensemble = EnsemblePredictor(models, weights=[0.5, 0.3, 0.2])
```

**预期效果**:
- 降低单模型风险
- 提升预测稳定性
- 综合各模型优势

**优先级**: ⭐⭐⭐  
**实施难度**: ⭐⭐⭐⭐ (复杂)  
**预计耗时**: 7-10天

---

## 📅 实施计划

### 第1周：快速改进

**Day 1-2**: 数据扩充
- [ ] 合并新旧数据
- [ ] 验证数据质量
- [ ] 重新微调模型

**Day 3-4**: 缩短预测窗口
- [ ] 修改pred_len为48
- [ ] 重新训练
- [ ] 验证效果

**Day 5-7**: 超参数调优
- [ ] 测试不同T和top_p组合
- [ ] 调整学习率
- [ ] 选择最优配置

**预期成果**:
- MAPE: 1.70% → 1.3%
- R²: -3.76 → -1.0
- 方向准确率: 66.7% → 70%

---

### 第2周：中级优化

**Day 8-10**: 特征工程
- [ ] 添加技术指标
- [ ] 添加时间特征
- [ ] 重新训练模型

**Day 11-12**: 早停机制
- [ ] 实现EarlyStopping
- [ ] 自动选择最佳模型
- [ ] 验证效果

**Day 13-14**: 数据增强
- [ ] 平衡涨跌样本
- [ ] 添加噪声增强
- [ ] 重新训练

**预期成果**:
- MAPE: 1.3% → 1.1%
- R²: -1.0 → 0.2
- 方向准确率: 70% → 73%

---

### 第3-4周：深度优化

**Day 15-20**: 课程学习
- [ ] 实现三阶段训练
- [ ] 逐步增加难度
- [ ] 验证收敛性

**Day 21-25**: 损失函数优化
- [ ] 实现CustomLoss
- [ ] 联合优化CE和MSE
- [ ] 调整权重参数

**Day 26-28**: 交叉验证
- [ ] 实现TimeSeriesSplit
- [ ] 执行5折交叉验证
- [ ] 评估稳定性

**预期成果**:
- MAPE: 1.1% → 0.9%
- R²: 0.2 → 0.4
- 方向准确率: 73% → 76%

---

### 第5-8周：高级优化

**Month 2**: 集成学习
- [ ] 训练多个基模型
- [ ] 实现加权融合
- [ ] 优化权重分配

**Month 2-3**: 模型架构升级
- [ ] 尝试Kronos-large
- [ ] 优化注意力机制
- [ ] 引入外部数据

**Month 3**: 生产化
- [ ] 建立自动化训练pipeline
- [ ] 实现在线学习机制
- [ ] 部署监控系统

**预期成果**:
- MAPE: 0.9% → 0.7%
- R²: 0.4 → 0.6
- 方向准确率: 76% → 80%+

---

## 📊 预期收益评估

### 投入产出比

| 方案 | 实施难度 | 预计耗时 | 预期提升 | ROI |
|------|---------|---------|---------|-----|
| 数据扩充 | ⭐ | 1天 | MAPE -0.2% | ⭐⭐⭐⭐⭐ |
| 缩短窗口 | ⭐⭐ | 2天 | R² +2.0 | ⭐⭐⭐⭐⭐ |
| 超参数调优 | ⭐ | 2天 | MAPE -0.1% | ⭐⭐⭐⭐ |
| 特征工程 | ⭐⭐⭐ | 5天 | MAPE -0.2% | ⭐⭐⭐⭐ |
| 早停机制 | ⭐⭐ | 1天 | 防过拟合 | ⭐⭐⭐⭐ |
| 课程学习 | ⭐⭐⭐ | 4天 | R² +0.2 | ⭐⭐⭐ |
| 损失优化 | ⭐⭐⭐⭐ | 7天 | MAPE -0.1% | ⭐⭐⭐ |
| 集成学习 | ⭐⭐⭐⭐ | 10天 | MAPE -0.2% | ⭐⭐ |

**推荐优先实施**:
1. ✅ 数据扩充 (高ROI，低难度)
2. ✅ 缩短预测窗口 (高ROI，解决核心问题)
3. ✅ 超参数调优 (低成本，快速见效)
4. ✅ 特征工程 (中等成本，显著提升)

---

## 🎯 成功标准

### 技术指标

- [ ] MAPE < 1.0%
- [ ] R² > 0.5
- [ ] 方向准确率 > 75%
- [ ] 最高价误差 < ¥4.0
- [ ] 成交量误差 < ±8%

### 业务指标

- [ ] 可用于辅助交易决策
- [ ] 预测稳定性提升
- [ ] 用户满意度提高
- [ ] 实盘测试通过

### 工程指标

- [ ] 训练自动化
- [ ] 模型版本管理
- [ ] 性能监控完善
- [ ] 文档齐全

---

## ⚠️ 风险与应对

### 技术风险

1. **过拟合风险**
   - 应对: 早停、正则化、交叉验证

2. **训练不稳定**
   - 应对: 课程学习、梯度裁剪

3. **性能不达预期**
   - 应对: 多方案并行、及时调整

### 资源风险

1. **计算资源不足**
   - 应对: 优化batch size、使用混合精度

2. **时间预算超限**
   - 应对: 优先级排序、分阶段实施

### 数据风险

1. **数据质量问题**
   - 应对: 严格的数据验证流程

2. **市场 regime change**
   - 应对: 在线学习、定期重训练

---

## 📝 总结与建议

### 核心建议

1. **立即执行** (本周):
   - ✅ 数据扩充 + 新数据加入
   - ✅ 缩短预测窗口至1天
   - ✅ 超参数调优

2. **近期执行** (2周内):
   - ✅ 特征工程增强
   - ✅ 早停机制
   - ✅ 数据平衡

3. **中期规划** (1-2月):
   - ✅ 课程学习
   - ✅ 损失函数优化
   - ✅ 交叉验证

4. **长期愿景** (3-6月):
   - ✅ 集成学习
   - ✅ 模型架构升级
   - ✅ 生产化部署

### 关键成功因素

1. **数据质量** - 高质量、多样化的训练数据
2. **合理预期** - 设定可达成的阶段性目标
3. **持续迭代** - 小步快跑，快速验证
4. **科学评估** - 严格的交叉验证和测试

### 预期最终效果

通过全面实施本优化方案，预期可将Kronos模型从当前的**中等水平**提升至**良好甚至优秀水平**：

```
当前: MAPE 1.70%, R² -3.76, 方向准确率 66.7%
目标: MAPE 0.70%, R² 0.60+, 方向准确率 80%+
```

这将使模型达到**生产级应用标准**，可作为可靠的辅助决策工具。

---

**报告制定时间**: 2026年4月30日  
**基于分析**: PREDICTION_ACCURACY_ANALYSIS.md  
**下一步**: 开始实施第1周快速改进方案  

---

*本报告为技术优化方案，具体实施需结合实际资源和约束条件调整。*
