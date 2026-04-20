# 🚀 明天继续训练指南

**创建时间**: 2026年4月19日 23:05  
**最后进度**: 2 epochs 完成，模型已保存  

---

## 📋 当前状态总结

### ✅ 已完成
- MPS GPU 配置成功
- 训练脚本运行正常
- 2 个 epochs 已完成
- 最佳模型已保存至 `outputs/models/finetune_tokenizer_300033_mps/best_model/`

### 📊 训练数据
- **损失值**: -0.023282 (持续下降)
- **学习率**: 0.000076
- **完成度**: ~4.8% (2,290/60,000 steps)

---

## 🎯 明天开始训练

### 方法 1: 从头开始（推荐）

由于只完成了 2 个 epochs，建议重新开始以获得更好的效果：

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python finetune/train_tokenizer_mps.py
```

或使用启动脚本：
```bash
./train_mps.sh
```

### 方法 2: 后台运行（推荐长时间训练）

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
nohup python -u finetune/train_tokenizer_mps.py > training_output.log 2>&1 &
```

查看进程 ID：
```bash
pgrep -f "train_tokenizer_mps.py"
```

---

## 🔍 监控训练进度

### 实时监控

```bash
./monitor_training.sh
```

或实时查看日志：
```bash
tail -f training_output.log
```

### 快速检查

```bash
# 查看最后 20 行
tail -20 training_output.log

# 检查进程是否运行
pgrep -f "train_tokenizer_mps.py" && echo "运行中" || echo "未运行"

# 查看模型文件
ls -lh outputs/models/finetune_tokenizer_300033_mps/
```

---

## ⏱️ 预计时间

- **每个 epoch**: ~20-30 分钟
- **总训练时间** (30 epochs): ~10-15 小时
- **剩余时间** (28 epochs): ~9-14 小时

**建议**: 早上启动，晚上检查进度

---

## 💾 模型保存位置

```
outputs/models/finetune_tokenizer_300033_mps/
├── best_model/              # 最佳验证损失的模型
│   ├── config.json
│   └── model.safetensors    (15 MB)
└── checkpoint_epoch_X/      # 定期检查点（如果配置了）
```

---

## 🛑 暂停/停止训练

### 优雅停止

```bash
pkill -f "train_tokenizer_mps.py"
```

训练会在当前 step 完成后停止，已保存的模型不会丢失。

### 强制停止

```bash
pkill -9 -f "train_tokenizer_mps.py"
```

---

## 📝 训练后测试

训练完成后，可以测试模型：

```python
from model.kronos import KronosTokenizer
import pandas as pd

# 加载微调后的 tokenizer
tokenizer = KronosTokenizer.from_pretrained(
    "./outputs/models/finetune_tokenizer_300033_mps/best_model"
)

print("✅ 模型加载成功")

# 加载测试数据
df = pd.read_csv("./akshare_data/daily_300033.csv")
df['timestamps'] = pd.to_datetime(df['timestamps'])

# 进行预测测试
# ... (添加预测代码)
```

---

## ⚠️ 注意事项

### 1. 验证集问题

训练日志显示验证集为空：
```
[VAL] Found 0 possible samples. Using 0 per epoch.
```

**影响**: 
- 无法有效选择最佳模型
- 验证损失为 0 可能不准确

**建议**: 
- 可以先继续训练
- 后续可以调查并修复验证集问题

### 2. 内存管理

确保有足够的可用内存：
```bash
# 检查内存使用
top -o mem

# 关闭不必要的应用
```

### 3. 电源连接

确保 MacBook 连接电源适配器以获得最佳性能。

---

## 📁 重要文件清单

### 训练相关
- ✅ `finetune/train_tokenizer_mps.py` - 训练脚本
- ✅ `finetune/config_300033_mps.yaml` - 配置文件
- ✅ `train_mps.sh` - 启动脚本
- ✅ `monitor_training.sh` - 监控脚本

### 数据文件
- ✅ `data/processed_datasets/train_data.pkl` - 训练数据
- ✅ `data/processed_datasets/val_data.pkl` - 验证数据
- ✅ `akshare_data/daily_300033.csv` - 同花顺原始数据

### 输出文件
- ✅ `outputs/models/finetune_tokenizer_300033_mps/best_model/` - 已保存的模型
- ✅ `training_output.log` - 训练日志

### 文档
- ✅ `TRAINING_PAUSED_REPORT.md` - 暂停报告
- ✅ `GPU_TRAINING_MPS_GUIDE.md` - 完整指南
- ✅ `QUICK_START_MPS.md` - 快速开始

---

## 🎓 快速命令参考

```bash
# 激活环境
source .venv/bin/activate

# 启动训练
python finetune/train_tokenizer_mps.py

# 后台运行
nohup python -u finetune/train_tokenizer_mps.py > training_output.log 2>&1 &

# 监控进度
./monitor_training.sh

# 实时日志
tail -f training_output.log

# 停止训练
pkill -f "train_tokenizer_mps.py"

# 检查进程
pgrep -f "train_tokenizer_mps.py"

# 查看模型
ls -lh outputs/models/finetune_tokenizer_300033_mps/
```

---

## 💡 优化建议

如果明天重新训练时想优化：

### 1. 调整批次大小

编辑 `finetune/config_300033_mps.yaml`:
```yaml
batch_size: 100  # 从 50 增加到 100（如果内存允许）
```

### 2. 调整学习率

```yaml
learning_rate: 0.0001  # 从 0.0002 降低
```

### 3. 减少 epochs（快速测试）

```yaml
epochs: 10  # 从 30 减少
```

### 4. 增加日志频率

```yaml
logging_steps: 5  # 从 10 减少到 5
```

---

## 🌟 祝您明天训练顺利！

###  checklist

明天开始前确认：
- [ ] MacBook 连接电源
- [ ] 关闭不必要的应用
- [ ] 足够的磁盘空间（至少 5GB）
- [ ] 虚拟环境可用
- [ ] 数据文件完整

---

**晚安！明天见！** 😴🌙
