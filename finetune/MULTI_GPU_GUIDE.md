# Kronos 多 GPU/CPU 并行训练指南

## 📊 当前系统状态

**您的系统配置：**
- CPU: Apple M1 (集成 GPU)
- CUDA: 不可用
- MPS: 不可用（当前环境）
- 可用 CPU 核心数：8 核

## 🚀 多进程训练方案

由于 Apple M1 是单芯片设计，没有多个独立的 GPU，我们采用 **CPU 多进程并行训练** 方案。

### ✅ 已创建的训练脚本

1. **`train_tokenizer_single.py`** - 单进程版本（适合调试和小规模训练）
2. **`train_tokenizer_multiprocess.py`** - 多进程版本（推荐使用，4 个 CPU 进程并行）
3. **`train_predictor_single.py`** - Predictor 单进程训练脚本

---

## 🎯 使用方法

### 方案 1：多进程训练（推荐 ⭐）

**优势：**
- ✅ 使用 4 个 CPU 进程并行处理数据
- ✅ 有效批次大小提升 4 倍（50 → 200）
- ✅ 训练速度更快

**运行命令：**
```bash
cd /Users/john/Documents/GitHub/Kronos
python finetune/train_tokenizer_multiprocess.py
```

**预期输出：**
```
No CUDA available. Using 4 CPU processes for parallel training
Models will be saved to: ./outputs/models/finetune_tokenizer_demo
Starting distributed training with 4 processes...
[Rank 0] Using device: cpu
[Rank 1] Using device: cpu
[Rank 2] Using device: cpu
[Rank 3] Using device: cpu

======================================================================
Training started with 30 epochs
Batch size per GPU: 50, Effective batch size: 200
Learning rate: 0.0002
Number of GPUs: 4
======================================================================
```

---

### 方案 2：单进程训练

**适用场景：**
- 调试代码
- 测试小数据集
- 内存有限的情况

**运行命令：**
```bash
cd /Users/john/Documents/GitHub/Kronos
python finetune/train_tokenizer_single.py
```

---

## ⏱️ 预计训练时间对比

| 训练模式 | 进程数 | 有效批次大小 | 预计每 epoch 时间 | 总时间（30 epochs） |
|---------|-------|------------|----------------|------------------|
| 单进程 CPU | 1 | 50 | ~20-30 分钟 | 10-15 小时 |
| 多进程 CPU | 4 | 200 | ~8-15 分钟 | 4-7.5 小时 |
| 单 GPU (RTX 3090) | 1 | 50 | ~1-2 分钟 | 30-60 分钟 |
| 多 GPU (4x RTX 3090) | 4 | 200 | ~30-60 秒 | 15-30 分钟 |

**注意：** 实际时间取决于 CPU 性能、内存速度和数据集大小。

---

## 🔍 监控训练进度

### 查看进程状态
```bash
# 查看所有相关进程
ps aux | grep train_tokenizer

# 查看 CPU 使用情况
top | grep python
```

### 关键指标
训练过程中会显示：
- ✅ 当前 epoch 和 step
- ✅ 学习率变化
- ✅ 损失值（Loss）
- ✅ 验证损失（Validation Loss）
- ✅ 最佳模型保存通知

---

## 💡 优化建议

### 1. 调整批次大小
如果内存不足，在 `config.py` 中减小批次大小：
```python
self.batch_size = 20  # 从 50 改为 20
```

### 2. 减少训练轮数
对于快速测试，可以减少 epochs：
```python
self.epochs = 5  # 从 30 改为 5
```

### 3. 后台运行训练
```bash
# macOS/Linux
nohup python finetune/train_tokenizer_multiprocess.py > train.log 2>&1 &

# 查看日志
tail -f train.log
```

---

## 🛠️ 常见问题

### Q1: 为什么多进程比单进程快？
**A:** 
- 每个进程独立处理数据，提高数据加载效率
- 梯度累积和同步在 CPU 之间进行
- 有效批次大小增加，加速收敛

### Q2: 可以使用更多进程吗？
**A:**
- 可以修改 `train_tokenizer_multiprocess.py` 中的进程数
- 但进程数过多会导致上下文切换开销
- 建议设置为 CPU 核心数的 50-75%

### Q3: 如何在有 NVIDIA GPU 的机器上运行？
**A:**
- 脚本会自动检测并使用 CUDA GPU
- 使用原始的 `torchrun` 脚本效果更好：
```bash
torchrun --standalone --nproc_per_node=2 finetune/train_tokenizer.py
```

### Q4: 训练中断后如何恢复？
**A:**
- 当前版本不支持自动恢复
- 可以从保存的检查点手动加载
- 建议在新脚本中添加 checkpoint 功能

---

## 📈 训练完成后

Tokenizer 训练完成后：
1. 检查最佳模型是否保存在 `outputs/models/finetune_tokenizer_demo/checkpoints/best_model`
2. 运行 Step 3.2 - Predictor 微调：
   ```bash
   python finetune/train_predictor_single.py
   ```

---

## 🎓 技术细节

### 分布式训练原理
- 使用 PyTorch 的 `DistributedDataParallel` (DDP)
- 每个进程维护模型副本
- 梯度在所有进程间同步（All-Reduce）
- 数据被分割到不同进程

### 为什么使用 Gloo 后端？
- NCCL 仅支持 NVIDIA GPU
- macOS 上的 CPU 训练使用 Gloo 后端
- Gloo 支持 CPU 间的梯度同步

---

**祝训练顺利！** 🚀

如有问题，请查看日志或联系支持。
