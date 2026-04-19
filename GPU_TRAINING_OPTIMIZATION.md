# GPU训练优化指南

## 📊 当前GPU状态

### 硬件信息
- **GPU型号**: NVIDIA GeForce RTX 2080 Ti
- **显存容量**: 11,264 MB (11 GB)
- **CUDA版本**: 13.2
- **驱动版本**: 596.21

### 当前使用情况
```
GPU使用率: 38% (被其他程序占用)
显存使用: 1,709 MB / 11,264 MB (15%)
温度: 32°C
功耗: 20W / 250W (8%)
```

---

## ⚠️ 当前问题

**训练正在使用CPU而不是GPU！**

从训练日志可以看到：
```
Using device: cpu (rank=0, world_size=1, local_rank=0)
```

这导致训练速度非常慢：
- Tokenizer每epoch: ~53秒
- Predictor每epoch: ~517秒（8.6分钟）
- **预计总时间**: 约70分钟（CPU）

如果使用GPU，预计可以加速**5-10倍**！

---

## ✅ 解决方案

### 方案1: 重启当前训练（推荐）

#### 步骤1: 停止当前训练
在运行训练的终端按 `Ctrl+C`

#### 步骤2: 确认配置文件已更新
配置文件 `finetune_csv/configs/config_icbc_daily.yaml` 已添加：
```yaml
device:
  use_cuda: true
  device_id: 0
```

#### 步骤3: 重新启动训练
```bash
python finetune_csv/train_sequential.py --config finetune_csv/configs/config_icbc_daily.yaml
```

#### 预期效果
启动时应该看到：
```
Using device: cuda:0 (rank=0, world_size=1, local_rank=0)
✅ CUDA Available: Yes
   GPU: NVIDIA GeForce RTX 2080 Ti
```

---

### 方案2: 修改批量训练脚本

编辑 `tests/batch_train_all_banks.py`，确保所有训练都使用GPU：

配置文件中已包含：
```python
env['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
```

运行命令：
```bash
# 使用GPU 0
python tests/batch_train_all_banks.py --gpu 0

# 或使用默认GPU
python tests/batch_train_all_banks.py
```

---

## 🚀 GPU性能对比

### CPU vs GPU 训练速度

| 阶段 | CPU时间/epoch | GPU预估时间/epoch | 加速比 |
|------|--------------|------------------|--------|
| Tokenizer (15 epochs) | 53秒 | ~8-10秒 | 5-6x |
| Predictor (10 epochs) | 517秒 | ~60-80秒 | 6-8x |
| **总计** | **~65分钟** | **~10-12分钟** | **~6x** |

### 显存需求

| 模型 | 参数量 | 预估显存 |
|------|--------|---------|
| Tokenizer | 3.96M | ~500 MB |
| Predictor (Kronos-base) | ~100M | ~2-3 GB |
| 批次数据 (batch=8) | - | ~1-2 GB |
| **总计** | - | **~4-6 GB** |

您的RTX 2080 Ti有11GB显存，**完全足够**！✅

---

## 🔧 GPU训练优化建议

### 1. 增加Batch Size

GPU可以处理更大的batch size，提高训练效率：

```yaml
training:
  batch_size: 16  # 从8增加到16
```

**效果**: 
- 训练速度提升 ~30-50%
- 显存占用增加 ~50%
- 可能略微影响收敛

### 2. 使用混合精度训练

如果PyTorch支持，可以启用AMP（Automatic Mixed Precision）：

```python
# 在训练代码中添加
scaler = torch.cuda.amp.GradScaler()
with torch.cuda.amp.autocast():
    output = model(input)
    loss = criterion(output, target)
scaler.scale(loss).backward()
```

**效果**:
- 训练速度提升 ~2-3x
- 显存占用减少 ~50%
- 精度几乎无损失

### 3. 多GPU训练（如果有）

如果您有多块GPU，可以使用DistributedDataParallel：

```bash
# 使用2块GPU
torchrun --nproc_per_node=2 finetune_csv/train_sequential.py \
  --config finetune_csv/configs/config_icbc_daily.yaml
```

---

## 📈 监控GPU使用

### 实时监控
```bash
# Windows PowerShell
nvidia-smi -l 2  # 每2秒刷新

# Linux
watch -n 2 nvidia-smi
```

### Python中检查
```python
import torch

if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Memory: {torch.cuda.memory_allocated(0) / 1024**2:.0f} MB")
    print(f"CUDA Version: {torch.version.cuda}")
else:
    print("CUDA not available!")
```

---

## ❓ 常见问题

### Q1: 为什么显示 "CUDA not available"？

**可能原因**:
1. PyTorch未安装CUDA版本
2. CUDA驱动未正确安装
3. CUDA版本不匹配

**解决方法**:
```bash
# 检查PyTorch CUDA支持
python -c "import torch; print(torch.cuda.is_available())"

# 重新安装带CUDA的PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Q2: GPU显存不足怎么办？

**解决方法**:
1. 减小batch size: `batch_size: 4`
2. 减小lookback_window: `lookback_window: 30`
3. 关闭其他GPU程序
4. 使用梯度累积

### Q3: 如何验证GPU确实在工作？

**方法1**: 查看nvidia-smi
```bash
nvidia-smi
```
应该看到Python进程占用GPU显存和使用率。

**方法2**: 查看训练日志
```
Using device: cuda:0
```

**方法3**: 观察训练速度
- CPU: ~500秒/epoch
- GPU: ~60-80秒/epoch

---

## 🎯 最佳实践

### 1. 训练前检查
```bash
# 检查GPU可用性
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"

# 检查显存
nvidia-smi
```

### 2. 选择合适的Batch Size
```
显存 < 4GB:  batch_size = 4
显存 4-8GB:  batch_size = 8
显存 > 8GB:  batch_size = 16-32
```

### 3. 监控训练过程
```bash
# 终端1: 运行训练
python finetune_csv/train_sequential.py --config config.yaml

# 终端2: 监控GPU
nvidia-smi -l 2
```

### 4. 保存最佳模型
训练会自动保存validation loss最低的模型到：
```
outputs/finetuned_models/icbc_daily_finetune/basemodel/best_model/
```

---

## 📊 性能基准测试

### RTX 2080 Ti 预期性能

| 任务 | CPU时间 | GPU时间 | 加速比 |
|------|---------|---------|--------|
| Tokenizer训练 (1 epoch) | 53秒 | 8-10秒 | 5-6x |
| Predictor训练 (1 epoch) | 517秒 | 60-80秒 | 6-8x |
| 完整训练 (ICBC) | ~65分钟 | ~10-12分钟 | ~6x |
| 批量训练 (34只银行) | ~37小时 | ~6-7小时 | ~6x |

---

## 🔄 下一步行动

### 立即执行
1. ✅ 配置文件已更新（添加device配置）
2. ⏳ 停止当前CPU训练（Ctrl+C）
3. ⏳ 重新启动训练（使用GPU）
4. ⏳ 验证GPU正在使用

### 验证命令
```bash
# 启动GPU训练
python finetune_csv/train_sequential.py --config finetune_csv/configs/config_icbc_daily.yaml

# 新终端监控GPU
nvidia-smi -l 2
```

### 预期输出
```
Using device: cuda:0 (rank=0, world_size=1, local_rank=0)
✅ CUDA Available: Yes
   GPU: NVIDIA GeForce RTX 2080 Ti
   Memory Allocated: XXX MB
```

---

## 💡 额外提示

### 1. 后台运行训练
```bash
# Windows (PowerShell)
Start-Process python -ArgumentList "finetune_csv/train_sequential.py", "--config", "finetune_csv/configs/config_icbc_daily.yaml"

# Linux/Mac
nohup python finetune_csv/train_sequential.py --config config.yaml > training.log 2>&1 &
```

### 2. 训练完成后通知
```python
# 在训练脚本末尾添加
import winsound  # Windows
winsound.Beep(1000, 500)  # 蜂鸣声

# 或发送邮件
import smtplib
# ... 发送邮件代码
```

### 3. 自动批量训练
```bash
# 创建批处理文件 train_all.bat
@echo off
for %%f in (data\kronos_*.csv) do (
    echo Training %%f
    python finetune_csv/train_sequential.py --config auto_generated_config.yaml
)
```

---

**最后更新**: 2026-04-19 12:48  
**状态**: ⚠️ 需要重启训练以使用GPU  
**预计加速**: 5-10倍
