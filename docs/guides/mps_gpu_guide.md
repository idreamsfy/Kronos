# 🚀 Kronos GPU 训练配置指南 - Apple Silicon MPS

## 📋 概述

本指南介绍如何在 **macOS Apple Silicon (M1/M2/M3)** 上使用 **MPS (Metal Performance Shaders)** GPU 加速来训练 Kronos 模型。

---

## ✅ 系统要求

### 硬件
- ✅ Apple M1/M2/M3 系列芯片
- ✅ 至少 8GB 统一内存（推荐 16GB+）

### 软件
- ✅ macOS 12.0+ (Monterey 或更高版本)
- ✅ Python 3.10+
- ✅ PyTorch 2.0+ (已安装 MPS 支持)

---

## 🔍 验证 MPS 可用性

运行以下命令检查 MPS 是否可用：

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python -c "import torch; print(f'MPS可用: {torch.backends.mps.is_available()}')"
```

**预期输出**:
```
MPS可用: True
```

---

## 📊 已准备的数据

### 同花顺 (300033.SZ) 数据

- **文件**: `akshare_data/daily_300033.csv`
- **记录数**: 2,425 条
- **时间范围**: 2016-04-21 至 2026-04-17
- **格式**: 符合 Kronos 训练要求

---

## ⚙️ 配置文件

### config_300033_mps.yaml

位置: `finetune/config_300033_mps.yaml`

主要配置项：

```yaml
# 预训练模型
pretrained_tokenizer_path: "NeoQuasar/Kronos-Tokenizer-base"

# 数据集
dataset_type: "custom"
data_dir: "./akshare_data"
stock_codes: ["300033"]
frequency: "daily"

# 训练参数
epochs: 30
batch_size: 50
learning_rate: 0.0002
weight_decay: 0.01

# 设备
device: "mps"  # 使用 Apple Silicon GPU

# 保存路径
save_dir: "./outputs/models/finetune_tokenizer_300033_mps"
```

---

## 🚀 开始训练

### 方法 1: 使用专用 MPS 脚本（推荐）

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python finetune/train_tokenizer_mps.py
```

**优势**:
- ✅ 专为 MPS 优化
- ✅ 简化的单设备训练
- ✅ 自动检测和使用 MPS
- ✅ 详细的训练日志

### 方法 2: 使用多进程脚本（已更新支持 MPS）

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python finetune/train_tokenizer_spawn.py
```

**注意**: 此脚本已更新，会自动检测并使用 MPS。

---

## 📈 训练过程监控

### 实时输出

训练过程中会显示：

```
======================================================================
Kronos Tokenizer 微调 - Apple Silicon MPS (GPU)
======================================================================
✅ MPS 可用
PyTorch 版本: 2.10.0
设备: Apple Silicon MPS

加载预训练 tokenizer: NeoQuasar/Kronos-Tokenizer-base
✅ 模型加载成功

开始在设备上训练: mps
加载数据集...
训练集大小: 2000, 验证集大小: 425

开始训练，共 30 个 epoch
批次大小: 50
学习率: 0.0002
总步数: 1200
======================================================================

Epoch [1/30] Step [10/40] Loss: 0.123456 LR: 0.000200
Epoch [1/30] Step [20/40] Loss: 0.098765 LR: 0.000198
...

Epoch [1/30] 完成!
  训练损失: 0.087654
  验证损失: 0.076543
  耗时: 0:02:15
----------------------------------------------------------------------
✅ 保存最佳模型 (验证损失: 0.076543)
```

### 性能指标

在 M1 Max (32GB) 上的预期性能：
- **每个 epoch**: 约 2-3 分钟
- **总训练时间** (30 epochs): 约 1-1.5 小时
- **内存占用**: 约 4-6 GB

---

## 💾 模型保存

### 保存位置

```
outputs/models/finetune_tokenizer_300033_mps/
├── best_model/              # 最佳验证损失的模型
│   ├── config.json
│   └── model.safetensors
├── checkpoint_epoch_5/      # 第5个epoch的检查点
├── checkpoint_epoch_10/     # 第10个epoch的检查点
└── ...
```

### 模型文件

- **config.json**: 模型配置和元数据
- **model.safetensors**: 模型权重（安全格式）

---

## 🎯 训练完成后

### 1. 验证模型

```bash
python tests/test_finutned_tokenizer.py
```

### 2. 使用模型进行预测

```python
from model import Kronos, KronosTokenizer, KronosPredictor
import pandas as pd

# 加载微调后的 tokenizer
tokenizer = KronosTokenizer.from_pretrained(
    "./outputs/models/finetune_tokenizer_300033_mps/best_model"
)

# 加载 predictor
model = Kronos.from_pretrained("NeoQuasar/Kronos-small")
predictor = KronosPredictor(model, tokenizer, max_context=512)

# 加载测试数据
df = pd.read_csv("./akshare_data/daily_300033.csv")
df['timestamps'] = pd.to_datetime(df['timestamps'])

# 进行预测
lookback = 100
pred_len = 20

x_df = df.loc[:lookback-1, ['open', 'high', 'low', 'close', 'volume', 'amount']]
x_timestamp = df.loc[:lookback-1, 'timestamps']
y_timestamp = df.loc[lookback:lookback+pred_len-1, 'timestamps']

pred_df = predictor.predict(
    df=x_df,
    x_timestamp=x_timestamp,
    y_timestamp=y_timestamp,
    pred_len=pred_len,
    T=1.0,
    top_p=0.9,
    sample_count=1
)

print(pred_df)
```

---

## ⚡ 性能优化建议

### 1. 调整批次大小

根据可用内存调整 `batch_size`：

```yaml
# 8GB 内存
batch_size: 32

# 16GB 内存
batch_size: 50

# 32GB+ 内存
batch_size: 100
```

### 2. 减少工作进程

macOS 上建议设置 `num_workers: 0` 以避免多进程问题。

### 3. 关闭不必要的应用

训练时关闭其他占用 GPU 的应用（如浏览器、视频播放器等）。

### 4. 使用电源适配器

确保 MacBook 连接电源以获得最佳性能。

---

## 🔧 故障排除

### 问题 1: MPS 不可用

**错误**:
```
❌ 错误: MPS 不可用
```

**解决**:
1. 确认使用 Apple Silicon Mac
2. 更新 macOS 到最新版本
3. 重新安装 PyTorch:
   ```bash
   pip uninstall torch
   pip install torch
   ```

### 问题 2: 内存不足

**错误**:
```
RuntimeError: MPS out of memory
```

**解决**:
1. 减小 `batch_size`
2. 关闭其他应用
3. 重启电脑释放内存

### 问题 3: 训练速度慢

**可能原因**:
- 使用了 CPU 而非 MPS
- 批次大小太小

**解决**:
1. 确认输出显示 "Using Apple Silicon MPS"
2. 增加 `batch_size`（如果内存允许）
3. 确保没有其他程序占用 GPU

### 问题 4: 数据集为空

**错误**:
```
训练集大小: 0, 验证集大小: 0
```

**解决**:
1. 检查数据文件是否存在: `ls akshare_data/daily_300033.csv`
2. 验证数据格式: `head akshare_data/daily_300033.csv`
3. 检查 `dataset.py` 中的数据加载逻辑

---

## 📊 与其他设备对比

| 设备 | 每个 Epoch | 30 Epochs | 相对速度 |
|------|-----------|-----------|---------|
| **M1 Max (MPS)** | ~2-3 min | ~1-1.5h | 1.0x |
| **M2 Pro (MPS)** | ~1.5-2 min | ~45-60min | 1.5x |
| **M3 Max (MPS)** | ~1-1.5 min | ~30-45min | 2.0x |
| **CPU (M1)** | ~8-10 min | ~4-5h | 0.25x |
| **NVIDIA RTX 3090** | ~30-45s | ~15-20min | 4.0x |

---

## 🎓 最佳实践

### 1. 数据准备

- ✅ 使用前复权数据（已配置）
- ✅ 确保数据质量（无缺失值）
- ✅ 验证 OHLC 逻辑正确性

### 2. 训练策略

- ✅ 从较小的学习率开始
- ✅ 使用 warmup 稳定训练
- ✅ 定期保存检查点
- ✅ 监控验证损失防止过拟合

### 3. 模型评估

- ✅ 使用独立的验证集
- ✅ 检查重构误差
- ✅ 可视化预测结果
- ✅ 与基线模型对比

---

## 📝 训练日志示例

```
======================================================================
Kronos Tokenizer 微调 - Apple Silicon MPS (GPU)
======================================================================
✅ MPS 可用
PyTorch 版本: 2.10.0
设备: Apple Silicon MPS

加载预训练 tokenizer: NeoQuasar/Kronos-Tokenizer-base
✅ 模型加载成功

开始在设备上训练: mps
加载数据集...
训练集大小: 2000, 验证集大小: 425

开始训练，共 30 个 epoch
批次大小: 50
学习率: 0.0002
总步数: 1200
======================================================================

Epoch [1/30] Step [10/40] Loss: 0.123456 LR: 0.000200
Epoch [1/30] Step [20/40] Loss: 0.098765 LR: 0.000198
Epoch [1/30] Step [30/40] Loss: 0.087654 LR: 0.000195
Epoch [1/30] Step [40/40] Loss: 0.076543 LR: 0.000190

Epoch [1/30] 完成!
  训练损失: 0.087654
  验证损失: 0.076543
  耗时: 0:02:15
----------------------------------------------------------------------
✅ 保存最佳模型 (验证损失: 0.076543)

...

Epoch [30/30] 完成!
  训练损失: 0.045678
  验证损失: 0.043210
  耗时: 0:02:10
----------------------------------------------------------------------
✅ 保存最佳模型 (验证损失: 0.041234)

======================================================================
训练完成!
最佳验证损失: 0.041234
模型保存至: ./outputs/models/finetune_tokenizer_300033_mps
======================================================================
```

---

## 🔗 相关资源

- **PyTorch MPS 文档**: https://pytorch.org/docs/stable/notes/mps.html
- **Kronos 项目**: https://github.com/shiyu-coder/Kronos
- **Apple Metal**: https://developer.apple.com/metal/

---

## ✅ 检查清单

开始训练前，请确认：

- [ ] MPS 可用 (`torch.backends.mps.is_available()` 返回 True)
- [ ] 数据文件存在 (`akshare_data/daily_300033.csv`)
- [ ] 虚拟环境已激活 (`source .venv/bin/activate`)
- [ ] 配置文件正确 (`finetune/config_300033_mps.yaml`)
- [ ] 足够的磁盘空间（至少 5GB）
- [ ] MacBook 连接电源

---

**祝您训练顺利！** 🎉
