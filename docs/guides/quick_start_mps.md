# 🚀 Kronos GPU 训练 - 快速开始

## ✅ 配置完成

您的 Kronos 已配置为使用 **Apple Silicon MPS (GPU)** 进行训练！

---

## 📊 当前状态

- ✅ **MPS 可用**: Apple Silicon GPU 加速已启用
- ✅ **数据就绪**: 同花顺 (300033) 10年历史数据 (2,425条)
- ✅ **配置文件**: `finetune/config_300033_mps.yaml`
- ✅ **训练脚本**: `finetune/train_tokenizer_mps.py`

---

## 🎯 开始训练

### 方法 1: 使用启动脚本（最简单）

```bash
cd /Users/john/Documents/GitHub/Kronos
./train_mps.sh
```

### 方法 2: 直接运行 Python

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python finetune/train_tokenizer_mps.py
```

---

## ⏱️ 预计时间

- **每个 epoch**: ~2-3 分钟
- **总训练时间** (30 epochs): ~1-1.5 小时
- **设备**: Apple M1/M2/M3 MPS

---

## 📁 输出位置

训练完成后，模型将保存在：

```
outputs/models/finetune_tokenizer_300033_mps/
├── best_model/              # 最佳模型
│   ├── config.json
│   └── model.safetensors
└── checkpoint_epoch_X/      # 定期检查点
```

---

## 🔍 监控训练

训练过程中会显示：

```
Epoch [1/30] Step [10/40] Loss: 0.123456 LR: 0.000200
...
Epoch [1/30] 完成!
  训练损失: 0.087654
  验证损失: 0.076543
  耗时: 0:02:15
✅ 保存最佳模型
```

---

## 💡 提示

### 性能优化

1. **连接电源**: 确保 MacBook 接通电源
2. **关闭其他应用**: 释放更多内存给训练
3. **保持散热**: 避免过热降频

### 随时停止

按 `Ctrl+C` 可以随时停止训练，已保存的检查点不会丢失。

### 继续训练

如果中断，可以重新运行脚本，会从新的 epoch 开始。

---

## 📈 训练后

### 1. 验证模型

```bash
python tests/test_finutned_tokenizer.py
```

### 2. 进行预测

使用微调后的模型进行股票价格预测。

---

## ❓ 常见问题

### Q: 如何确认使用了 GPU？

查看输出中是否显示：
```
✅ MPS 可用
使用设备: mps
```

### Q: 训练太慢怎么办？

- 检查是否真的使用了 MPS（而非 CPU）
- 增加 batch_size（如果内存允许）
- 关闭其他占用资源的应用

### Q: 内存不足怎么办？

减小 `finetune/config_300033_mps.yaml` 中的 `batch_size`：
```yaml
batch_size: 32  # 从 50 改为 32
```

---

## 📚 详细文档

完整的使用指南请查看：
- `GPU_TRAINING_MPS_GUIDE.md` - 完整的 MPS 训练指南

---

**准备好了吗？开始训练吧！** 🎉

```bash
./train_mps.sh
```
