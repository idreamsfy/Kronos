# 🚀 300033 五分钟K线 Kronos-base 微调指南

**开始时间**: 2026年4月25日  
**数据类型**: 5分钟K线 (Futu API)  
**模型**: Kronos-base (102M参数)  

---

## 📋 微调配置

### 数据配置

| 参数 | 值 | 说明 |
|------|-----|------|
| **数据源** | Futu API | 富途牛牛5分钟K线 |
| **股票代码** | SZ.300033 | 同花顺 |
| **时间范围** | 2023-04-26 至 2026-04-24 | 3年数据 |
| **总记录数** | 34,800 条 | 5分钟K线 |
| **样本数** | 34,680 个 | 训练样本 |

### 模型配置

| 参数 | 值 | 说明 |
|------|-----|------|
| **基础模型** | Kronos-base | 102.3M 参数 |
| **Tokenizer** | Kronos-Tokenizer-base | BSQuantizer |
| **Lookback** | 100 | 100个5分钟 ≈ 8小时 |
| **Pred_len** | 20 | 20个5分钟 ≈ 1.5小时 |

### 训练配置

| 参数 | 值 | 说明 |
|------|-----|------|
| **Batch size** | 8 | 每批次样本数 |
| **Epochs** | 5 | 训练轮数 |
| **Learning rate** | 1e-5 | 初始学习率 |
| **Weight decay** | 0.01 | 权重衰减 |
| **Optimizer** | AdamW | 优化器 |
| **Scheduler** | CosineAnnealingLR | 学习率调度 |
| **Device** | MPS | Apple Silicon GPU |

---

## 🎯 微调目标

### 主要目标

1. **适配5分钟数据特征**
   - 学习高频交易模式
   - 捕捉短期价格波动
   - 理解日内交易规律

2. **提升预测精度**
   - 短期价格预测 (1.5小时)
   - 成交量预测
   - 波动率预测

3. **保持泛化能力**
   - 避免过拟合
   - 保留预训练知识
   - 适应不同市场环境

---

## 📊 预期结果

### 训练时间估算

```
预编码阶段: ~5分钟 (34,680 样本 @ 120 it/s)
训练阶段: 
  - 每个 epoch: ~4,335 batches
  - 每 batch: ~0.5秒 (MPS)
  - 每个 epoch: ~36分钟
  - 5个 epochs: ~3小时

总耗时: 约 3-3.5 小时
```

### 预期性能提升

- **Loss 下降**: 从 ~3.5 降至 ~1.5-2.0
- **预测精度**: 提升 10-20%
- **收敛速度**: 较快 (小学习率微调)

---

## 🔧 使用方法

### 启动微调

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python finetune/finetune_300033_5min.py
```

### 监控进度

```bash
# 查看实时日志
tail -f outputs/logs/finetune_5min_300033.log

# 查看训练进度
grep "Epoch" outputs/logs/finetune_5min_300033.log
```

### 检查输出

```bash
# 查看模型文件
ls -lh outputs/models/finetune_300033_5min_base/

# 查看最佳模型
ls -lh outputs/models/finetune_300033_5min_base/best_model/
```

---

## 📁 输出文件

### 目录结构

```
outputs/models/finetune_300033_5min_base/
├── best_model/              # 最佳模型 (最低 loss)
│   ├── config.json
│   ├── model.safetensors
│   └── README.md
├── checkpoint_epoch_2/      # 第2轮检查点
├── checkpoint_epoch_4/      # 第4轮检查点
└── ...

outputs/logs/
└── finetune_5min_300033.log # 训练日志
```

### 文件大小

- **模型权重**: ~400 MB (safetensors 格式)
- **配置文件**: ~1 KB
- **训练日志**: ~10-50 KB

---

## 🎓 技术细节

### 自回归训练策略

```python
# 拼接输入和目标
xy_raw = torch.cat([x_raw, y_raw], dim=1)

# Tokenizer 编码
tokens = tokenizer.encode(xy_raw, half=True)  # [s1_ids, s2_ids]

# 创建 shifted sequence (next token prediction)
input_s1 = tokens[0][:, :-1]   # 去掉最后一个
target_s1 = tokens[0][:, 1:]   # 去掉第一个

# 模型前向传播
s1_logits, s2_logits = model(s1_ids=input_s1, s2_ids=input_s2)

# 计算交叉熵损失
loss = CE(s1_logits, target_s1) + CE(s2_logits, target_s2)
```

### 预编码优化

**问题**: 每个 batch 都调用 tokenizer.encode() 非常慢

**解决**: 训练前一次性编码所有数据

```python
# 预编码 (只需做一次)
for sample in dataset:
    tokens = tokenizer.encode(sample)
    encoded_data.append(tokens)

# 训练时直接使用
for batch in encoded_dataloader:
    loss = train_step(batch)  # 快速！
```

**效果**: 训练速度提升 10倍+

---

## ⚠️ 注意事项

### 内存管理

```python
# macOS MPS 特殊配置
DataLoader(
    dataset,
    batch_size=8,
    num_workers=0,      # 必须为 0
    pin_memory=False    # 必须为 False
)
```

### 设备一致性

```python
# 确保所有组件在同一设备上
tokenizer.to(DEVICE)
model.to(DEVICE)
data.to(DEVICE)
```

### 梯度裁剪

```python
# 防止梯度爆炸
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

---

## 📈 训练监控

### 关键指标

1. **Training Loss**
   - 应该持续下降
   - 最终稳定在 1.5-2.0

2. **S1 vs S2 Loss**
   - S1 (粗粒度): 通常较高
   - S2 (细粒度): 通常较低
   - 两者应同步下降

3. **Learning Rate**
   - 从 1e-5 逐渐降低
   - 最终约 1e-7

### 正常现象

✅ Loss 波动: 小幅度波动是正常的  
✅ 训练速度慢: MPS 比 CUDA 慢  
✅ 内存占用高: 预编码需要大量内存  

### 异常情况

❌ Loss 不下降: 检查学习率是否太小  
❌ Loss NaN: 检查数据是否有异常值  
❌ OOM 错误: 减小 batch_size  

---

## 🔄 后续步骤

### 1. 验证模型

```python
from model import Kronos, KronosTokenizer, KronosPredictor
import pandas as pd

# 加载微调后的模型
model_path = "./outputs/models/finetune_300033_5min_base/best_model"
tokenizer = KronosTokenizer.from_pretrained(model_path)
model = Kronos.from_pretrained(model_path)

# 创建预测器
predictor = KronosPredictor(model, tokenizer, device='mps')

# 加载测试数据
df = pd.read_csv('./data/raw/futu/5min_300033.csv')
df['timestamps'] = pd.to_datetime(df['timestamps'])

# 进行预测
lookback = 100
pred_len = 20

x_df = df.iloc[-lookback:][['open', 'high', 'low', 'close', 'volume', 'amount']]
x_ts = df.iloc[-lookback:]['timestamps']
y_ts = pd.date_range(start=x_ts.iloc[-1] + pd.Timedelta(minutes=5), 
                     periods=pred_len, freq='5min')

pred_df = predictor.predict(
    df=x_df,
    x_timestamp=x_ts,
    y_timestamp=y_ts,
    pred_len=pred_len,
    T=1.0,
    top_p=0.9
)

print(pred_df)
```

### 2. 对比分析

```python
# 对比原始模型和微调模型
# 使用相同的测试数据
# 计算 MAE, RMSE, MAPE 等指标

from sklearn.metrics import mean_absolute_error, mean_squared_error

mae_original = mean_absolute_error(y_true, y_pred_original)
mae_finetuned = mean_absolute_error(y_true, y_pred_finetuned)

print(f"原始模型 MAE: {mae_original:.4f}")
print(f"微调模型 MAE: {mae_finetuned:.4f}")
print(f"改进: {(mae_original - mae_finetuned) / mae_original * 100:.2f}%")
```

### 3. 回测策略

```python
# 基于微调模型的预测开发交易策略
# 例如: 预测价格上涨则买入，下跌则卖出

def trading_strategy(predictions, threshold=0.01):
    """
    简单的交易策略
    predictions: 预测的未来价格
    threshold: 触发交易的阈值
    """
    current_price = predictions['close'].iloc[0]
    future_price = predictions['close'].iloc[-1]
    
    change_pct = (future_price - current_price) / current_price
    
    if change_pct > threshold:
        return 'BUY'
    elif change_pct < -threshold:
        return 'SELL'
    else:
        return 'HOLD'
```

---

## 📝 故障排除

### 问题 1: 预编码很慢

**原因**: MPS 加速有限

**解决**: 
- 耐心等待 (约5分钟)
- 或减少数据集大小进行测试

### 问题 2: 内存不足

**错误**: `RuntimeError: MPS out of memory`

**解决**:
```python
# 减小 batch size
BATCH_SIZE = 4  # 从 8 降到 4

# 或减小 lookback
LOOKBACK = 50   # 从 100 降到 50
```

### 问题 3: Loss 不收敛

**可能原因**:
- 学习率太小
- 数据质量问题
- 模型配置不当

**解决**:
```python
# 增加学习率
LEARNING_RATE = 5e-5  # 从 1e-5 增加到 5e-5

# 检查数据
print(df.isnull().sum())
print(df.describe())
```

---

## 🎯 成功标准

### 训练阶段

- ✅ Loss 从 ~3.5 降至 ~1.5-2.0
- ✅ S1 和 S2 loss 同步下降
- ✅ 无 NaN 或 Inf
- ✅ 训练平稳，无剧烈波动

### 验证阶段

- ✅ 预测结果合理
- ✅ 相比原始模型有提升
- ✅ 在不同时间段表现稳定

### 应用阶段

- ✅ 可用于实盘预测
- ✅ 响应速度快 (< 1秒)
- ✅ 内存占用合理 (< 2GB)

---

## 📊 性能基准

### 与日线数据对比

| 指标 | 日线数据 | 5分钟数据 | 说明 |
|------|---------|----------|------|
| **样本数** | ~2,300 | ~34,680 | 5分钟多15倍 |
| **训练时间** | ~30分钟 | ~3小时 | 5分钟长6倍 |
| **预测粒度** | 天 | 5分钟 | 更精细 |
| **应用场景** | 中长期 | 短期/日内 | 不同策略 |

### 与其他模型对比

| 模型 | 参数量 | 训练时间 | 预测精度 | 适用场景 |
|------|--------|---------|---------|---------|
| **Kronos-mini** | 4.1M | ~10分钟 | 中等 | 快速实验 |
| **Kronos-small** | 24.7M | ~1小时 | 良好 | 一般应用 |
| **Kronos-base** | 102.3M | ~3小时 | 优秀 | 生产环境 |
| **Kronos-large** | 499.2M | ~10小时 | 最佳 | 研究用途 |

---

## 🔗 相关资源

- **原始微调脚本**: `finetune/finetune_ths_real.py`
- **5分钟数据获取**: `scripts/data/fetch_300033_futu.py`
- **数据指南**: `docs/guides/FUTU_5MIN_DATA_GUIDE.md`
- **Kronos 文档**: `README.md`

---

## 📝 版本历史

### v1.0 (2026-04-25)
- ✅ 首次实现5分钟数据微调
- ✅ 支持 MPS 加速
- ✅ 预编码优化
- ✅ 自动保存检查点

---

**祝微调顺利！** 🎉

---

*创建时间: 2026年4月25日*  
*作者: Kronos Team*
