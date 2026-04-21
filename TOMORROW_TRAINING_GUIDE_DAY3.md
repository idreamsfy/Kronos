# 🚀 明天继续训练指南 - Day 3

**创建时间**: 2026年4月20日 14:50  
**当前进度**: 21/30 epochs (70%)  
**剩余工作**: 9 epochs  

---

## 📊 当前状态

### ✅ 已完成
- 21 个 epochs 训练完成
- 最佳模型已保存 (15 MB)
- 损失值: -0.024770 (持续下降)
- MPS GPU 工作正常

### ⏳ 待完成
- Epoch 22-30 (9 个 epochs)
- 预计时间: 3-4 小时

---

## 🎯 明天启动训练

### 方法 1: 使用启动脚本（推荐）

```bash
cd /Users/john/Documents/GitHub/Kronos
./start_training_now.sh
```

**优势**:
- ✅ 自动检查环境
- ✅ 自动清理日志
- ✅ 后台运行
- ✅ 自动验证启动状态

### 方法 2: 手动启动

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python finetune/train_tokenizer_mps.py
```

### 方法 3: 后台运行

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
nohup python -u finetune/train_tokenizer_mps.py > outputs/logs/training_output.log 2>&1 &
```

---

## 🔍 监控训练

### 实时监控

```bash
tail -f outputs/logs/training_output.log
```

按 `Ctrl+C` 退出监控（不会停止训练）。

### 查看进度

```bash
# 查看最后 20 行
tail -20 outputs/logs/training_output.log

# 或使用监控脚本
./scripts/training/monitor.sh
```

### 检查进程

```bash
# 检查是否运行
pgrep -f "train_tokenizer_mps.py" && echo "运行中" || echo "未运行"

# 查看进程详情
ps aux | grep train_tokenizer_mps
```

---

## ⏱️ 时间估算

### 预计时间表

假设早上 9:00 开始：

| 时间 | 进度 | 说明 |
|------|------|------|
| 09:00 | Epoch 22 开始 | 启动训练 |
| 09:30 | Epoch 23 开始 | - |
| 10:00 | Epoch 24 开始 | - |
| 10:30 | Epoch 25 开始 | - |
| 11:00 | Epoch 26 开始 | - |
| 11:30 | Epoch 27 开始 | - |
| 12:00 | Epoch 28 开始 | - |
| 12:30 | Epoch 29 开始 | - |
| 13:00 | Epoch 30 开始 | 最后一个 epoch |
| 13:30 | **训练完成** | 🎉 |

**总时长**: 约 3.5-4.5 小时

---

## 💾 模型保存

### 保存位置

```
outputs/models/finetune_tokenizer_300033_mps/best_model/
├── model.safetensors    (15 MB)
├── config.json
└── README.md
```

### 保存机制

- 每个 epoch 结束后评估验证损失
- 如果验证损失更低，自动保存为最佳模型
- 由于验证集为空，会定期保存检查点

---

## 🛑 暂停/停止训练

### 优雅停止

```bash
pkill -f "train_tokenizer_mps.py"
```

训练会在当前 step 完成后停止。

### 强制停止

```bash
pkill -9 -f "train_tokenizer_mps.py"
```

仅在紧急情况下使用。

---

## 📈 预期输出

### 训练日志示例

```
Epoch [22/30] Step [10/2000] Loss: -0.024771 LR: 0.000050
Epoch [22/30] Step [20/2000] Loss: -0.024772 LR: 0.000050
...
Epoch [22/30] 完成!
  训练损失: -0.024775
  验证损失: 0.000000
  耗时: 0:25:30
✅ 保存最佳模型

...

Epoch [30/30] 完成!
  训练损失: -0.024800
  验证损失: 0.000000
  耗时: 0:24:50
✅ 保存最佳模型

======================================================================
训练完成!
最佳验证损失: 0.000000
模型保存至: ./outputs/models/finetune_tokenizer_300033_mps
======================================================================
```

---

## 🎓 训练完成后

### 1. 验证模型

```python
from model.kronos import KronosTokenizer

# 加载训练好的模型
tokenizer = KronosTokenizer.from_pretrained(
    "./outputs/models/finetune_tokenizer_300033_mps/best_model"
)

print("✅ 模型加载成功")
print(f"模型类型: {type(tokenizer)}")
```

### 2. 测试预测

```python
import pandas as pd
from model import Kronos, KronosPredictor

# 加载模型
model = Kronos.from_pretrained("NeoQuasar/Kronos-small")
predictor = KronosPredictor(model, tokenizer, max_context=512)

# 加载测试数据
df = pd.read_csv("./data/raw/akshare/daily_300033.csv")
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

### 3. 提交代码

```bash
# 添加新文件
git add outputs/models/finetune_tokenizer_300033_mps/
git add TRAINING_PAUSED_DAY2.md

# 提交
git commit -m "feat: 完成 30 epochs 训练，获得最终优化模型"

# 推送
git push origin trainning_use_MPS_20260419
```

---

## 💡 优化建议

### 如果想加快训练

1. **增加批次大小** (如果内存允许)
   ```python
   # 修改 finetune/train_tokenizer_mps.py
   batch_size=100  # 从 50 增加到 100
   ```

2. **减少 epochs** (如果效果已足够好)
   ```python
   # 修改配置文件或脚本
   epochs=25  # 从 30 减少到 25
   ```

### 如果想提高质量

1. **降低学习率**
   ```python
   learning_rate=0.0001  # 从 0.0002 降低
   ```

2. **增加 epochs**
   ```python
   epochs=50  # 从 30 增加到 50
   ```

---

## ⚠️ 注意事项

### 1. 电源连接

确保 MacBook 连接电源适配器：
- 避免电池耗尽
- 获得最佳性能
- 防止过热降频

### 2. 内存管理

关闭不必要的应用：
```bash
# 检查内存使用
top -o mem

# 关闭浏览器、视频播放器等
```

### 3. 散热

保持良好的散热：
- 使用散热垫
- 避免堵塞通风口
- 室温适宜

### 4. 磁盘空间

确保有足够的空间：
```bash
df -h /
# 至少需要 5GB 可用空间
```

---

## 📝 快速命令参考

```bash
# 激活环境
source .venv/bin/activate

# 启动训练
python finetune/train_tokenizer_mps.py

# 后台运行
nohup python -u finetune/train_tokenizer_mps.py > outputs/logs/training_output.log 2>&1 &

# 监控进度
tail -f outputs/logs/training_output.log

# 停止训练
pkill -f "train_tokenizer_mps.py"

# 检查进程
pgrep -f "train_tokenizer_mps.py"

# 查看模型
ls -lh outputs/models/finetune_tokenizer_300033_mps/best_model/
```

---

## 🎯 明日目标

### 主要任务
1. ✅ 完成剩余 9 个 epochs
2. ✅ 获得最终的优化模型
3. ✅ 验证模型质量
4. ✅ 准备预测测试

### 次要任务
1. 📝 更新文档
2. 🔧 优化配置
3. 🧪 编写测试
4. 📊 分析结果

---

## 🌟 预期成果

### 训练完成后的收获

1. **优化模型**
   - 30 epochs 微调的 tokenizer
   - 针对同花顺 (300033) 优化
   - 15 MB SafeTensors 格式

2. **性能提升**
   - 更好的重构能力
   - 更准确的预测
   - 更快的推理速度

3. **完整流程**
   - 数据获取 → 预处理 → 训练 → 验证
   - 完整的 MLOps 实践
   - 可复现的训练流程

---

## 📞 问题排查

### 如果训练无法启动

1. **检查环境**
   ```bash
   python scripts/utils/check_environment.py
   ```

2. **检查 MPS**
   ```python
   import torch
   print(torch.backends.mps.is_available())
   ```

3. **检查数据**
   ```bash
   ls -lh data/processed/
   ```

### 如果训练中途停止

1. **查看日志**
   ```bash
   tail -100 outputs/logs/training_output.log
   ```

2. **检查错误**
   ```bash
   grep -i "error\|exception" outputs/logs/training_output.log
   ```

3. **重新启动**
   ```bash
   ./start_training_now.sh
   ```

---

## 🎉 准备好了吗？

### 启动前检查清单

- [ ] MacBook 连接电源
- [ ] 关闭不必要的应用
- [ ] 足够的磁盘空间 (5GB+)
- [ ] 虚拟环境可用
- [ ] 数据文件完整
- [ ] 网络连接正常

### 启动命令

```bash
cd /Users/john/Documents/GitHub/Kronos
./start_training_now.sh
```

---

**祝您明天训练顺利！期待完成最后的 9 个 epochs！** 🚀

---

*最后更新: 2026年4月20日 14:50*  
*下次训练: 2026年4月21日*  
*剩余工作: 9 epochs (30%)*
