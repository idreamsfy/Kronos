# Kronos 微调指南 - 单 GPU/CPU 版本

本目录包含用于在单 GPU 或 CPU 上微调 Kronos 模型的简化脚本，无需使用 `torchrun` 或分布式训练。

## 📋 前提条件

1. 已安装所有依赖项（参见根目录的 `requirements.txt`）
2. 已完成数据预处理，生成了处理好的数据集：
   - `data/processed_datasets/train_data.pkl`
   - `data/processed_datasets/val_data.pkl`
   - `data/processed_datasets/test_data.pkl`

## 🚀 Step 3: 微调训练

### Step 3.1: 微调 Tokenizer

**运行命令：**

```bash
cd /Users/john/Documents/GitHub/Kronos

# 使用 GPU 训练（如果有）
python finetune/train_tokenizer_single.py

# 或者强制使用 CPU
# CUDA_VISIBLE_DEVICES="" python finetune/train_tokenizer_single.py
```

**说明：**
- 加载预训练的 Kronos Tokenizer (`NeoQuasar/Kronos-Tokenizer-base`)
- 使用 `train_data.pkl` 和 `val_data.pkl` 进行训练
- 最佳模型将保存到：`outputs/models/finetune_tokenizer_demo/checkpoints/best_model`
- 训练过程中会实时显示损失值和进度

**预期输出示例：**
```
Using device: cuda
GPU: Apple M1 Pro
Models will be saved to: outputs/models/finetune_tokenizer_demo

Loading pretrained tokenizer from: NeoQuasar/Kronos-Tokenizer-base
Model loaded successfully!

Starting training...

======================================================================
Training started with 30 epochs
Batch size: 50, Learning rate: 0.0002
======================================================================

[Epoch 1/30, Step 100/400] LR 0.000195, Loss: 0.5234
[Epoch 1/30, Step 200/400] LR 0.000190, Loss: 0.4876
...

----------------------------------------------------------------------
--- Epoch 1/30 Summary ---
Average Training Loss: 0.5123
Validation Loss: 0.4987
Time This Epoch: 0:05:32
Total Time Elapsed: 0:05:32
----------------------------------------------------------------------

✓ Best model saved to outputs/models/finetune_tokenizer_demo/checkpoints/best_model (Val Loss: 0.4987)
```

---

### Step 3.2: 微调 Predictor

**在 Tokenizer 微调完成后运行：**

```bash
cd /Users/john/Documents/GitHub/Kronos

# 使用 GPU 训练（如果有）
python finetune/train_predictor_single.py

# 或者强制使用 CPU
# CUDA_VISIBLE_DEVICES="" python finetune/train_predictor_single.py
```

**说明：**
- 使用微调后的 Tokenizer 和预训练的 Kronos Predictor
- 最佳模型将保存到：`outputs/models/finetune_predictor_demo/checkpoints/best_model`

**注意：** 如果 Step 3.1 还未完成，此脚本会自动回退到使用预训练的 Tokenizer。

---

## ⏱️ 预计训练时间

根据硬件配置不同，训练时间会有所差异：

| 硬件配置 | Tokenizer 训练时间 | Predictor 训练时间 |
|---------|------------------|------------------|
| GPU (RTX 3090) | ~30 分钟 | ~1 小时 |
| GPU (M1/M2) | ~1-2 小时 | ~2-3 小时 |
| CPU (8 核) | ~4-6 小时 | ~8-10 小时 |

**提示：** 
- 训练时间取决于数据集大小和 GPU 性能
- 可以在 `config.py` 中减少 `epochs` 来加快训练
- 第一批次的处理速度最慢，后续会加快

---

## 📊 监控训练进度

训练过程中会显示以下信息：
- ✅ 每个 batch 的损失值和学习率
- ✅ 每个 epoch 的平均训练损失和验证损失
- ✅ 当前 epoch 用时和总用时
- ✅ 最佳模型保存通知

---

## 🛠️ 常见问题

### Q1: 训练速度太慢怎么办？
**A:** 
- 确保使用了 GPU（检查是否显示 "Using device: cuda"）
- 减少 `config.py` 中的 `batch_size` 可以降低显存占用
- 减少 `epochs` 数量可以缩短训练时间

### Q2: 显存不足怎么办？
**A:**
- 在 `config.py` 中减小 `batch_size`（例如从 50 改为 20）
- 启用梯度累积：增加 `accumulation_steps`

### Q3: 如何在后台运行训练？
**A:**
```bash
# Linux/macOS
nohup python finetune/train_tokenizer_single.py > train_tokenizer.log 2>&1 &

# 查看日志
tail -f train_tokenizer.log
```

### Q4: 如何恢复中断的训练？
**A:**
- 目前脚本不支持自动恢复
- 可以从保存的最佳检查点手动加载继续训练
- 建议修改 `config.py` 中的学习率继续
