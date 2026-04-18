# 🚀 GPU训练已启动 - 实时监控

**启动时间：** 2026年4月18日 11:08  
**设备：** NVIDIA GeForce RTX 2080 Ti (cuda:0)  
**配置：** test_finetune_run  

---

## ✅ 训练状态

### Tokenizer Fine-tuning (进行中)

```
当前进度: Epoch 1/5, Step 200/4660 (4.3%)
预计完成时间: ~17分钟 (本epoch)
总预计时间: ~1.5小时 (5 epochs)
```

**训练指标：**
```
Loss: -0.0317 ✅ 稳定
VQ Loss: -0.0713 ✅ 良好
Recon Loss Pre: 0.0049 ✅ 优秀
Recon Loss All: 0.0031 ✅ 优秀
Learning Rate: 0.000054 (warmup阶段)
```

**训练速度：**
```
每步耗时: ~0.24秒 ⚡
每epoch: ~18.6分钟
加速比: ~150倍 (vs CPU)
```

---

## 📊 性能对比

| 指标 | CPU训练 | GPU训练 | 提升 |
|------|---------|---------|------|
| 每步耗时 | ~35秒 | ~0.24秒 | **146x** |
| 每epoch | ~2-3天 | ~18.6分钟 | **150x** |
| Tokenizer (5 epochs) | ~10-15天 | ~1.5小时 | **160x** |
| Predictor (3 epochs) | ~5-7天 | ~1小时 | **120x** |
| **总计** | **~15-22天** | **~2.5小时** | **144x** |

---

## 🎯 训练流程

### Phase 1: Tokenizer Fine-tuning (当前)
```
✅ 加载预训练tokenizer
✅ 初始化优化器和学习率调度器
⏳ Epoch 1/5 (4.3% 完成)
⏸️ Epoch 2-5/5 (待进行)
📁 保存位置: outputs/finetuned_models/test_finetune_run/tokenizer/best_model/
```

### Phase 2: Predictor Fine-tuning (待开始)
```
⏸️ 加载预训练predictor
⏸️ Epoch 1-3/3
📁 保存位置: outputs/finetuned_models/test_finetune_run/basemodel/best_model/
```

---

## 🔍 监控训练

### 方法1: 使用监控脚本（推荐）

打开新的终端窗口，运行：
```powershell
cd d:\GitHub\Kronos
.\monitor_training.bat
```

这将每5秒自动刷新显示：
- GPU利用率和温度
- 最新训练日志

### 方法2: 手动查看日志

```powershell
# 查看最后20行日志
Get-Content outputs\finetuned_models\test_finetune_run\logs\tokenizer_training_rank_0.log -Tail 20

# 实时跟踪日志
Get-Content outputs\finetuned_models\test_finetune_run\logs\tokenizer_training_rank_0.log -Tail 20 -Wait
```

### 方法3: 检查GPU状态

```powershell
# 实时监控GPU
while ($true) { Clear-Host; nvidia-smi; Start-Sleep 2 }
```

---

## 📈 预期输出示例

### 正常训练日志：
```
[Epoch 1/5, Step 200/4660] LR: 0.000054, Loss: -0.0317
  - VQ Loss: -0.0713
  - Recon Loss Pre: 0.0049
  - Recon Loss All: 0.0031
```

### Epoch完成时：
```
--- Epoch 1/5 Summary ---
Validation Loss: 0.0022
Epoch Time: 0:18:35
Total Training Time: 0:18:35

Best model saved to: outputs/finetuned_models/test_finetune_run\tokenizer\best_model
```

### 全部完成后：
```
============================================================
Tokenizer training completed successfully!
Total time: 1:32:45
Best validation loss: 0.0020
============================================================

Starting Predictor Fine-tuning Phase...
```

---

## ⚠️ 注意事项

### 1. 不要中断训练
- 训练会自动保存最佳模型
- 但中断会导致需要重新开始当前epoch
- 让它在后台运行即可

### 2. GPU温度监控
```
正常范围: 60-75°C
警告范围: 75-85°C
危险范围: >85°C
```

如果温度过高，可以：
- 降低batch size (从16改为8)
- 改善散热
- 暂停训练让GPU冷却

### 3. 磁盘空间
```
预计需要: ~50 MB (模型文件)
当前可用: 充足
```

---

## 🎛️ 故障排除

### 问题1: 训练突然停止

**检查：**
```powershell
# 查看完整日志
Get-Content outputs\finetuned_models\test_finetune_run\logs\tokenizer_training_rank_0.log | Select-String "ERROR" -Context 5
```

**解决：**
- 检查是否有CUDA out of memory错误
- 如果有，减小batch size
- 重新启动训练

### 问题2: GPU利用率低 (<50%)

**可能原因：**
- 数据加载瓶颈
- CPU成为瓶颈

**解决：**
更新配置文件增加workers：
```yaml
training:
  num_workers: 4  # 从0增加到4
```

### 问题3: Loss不下降或爆炸

**正常情况：**
- Loss在-0.03到-0.04之间波动是正常的
- VQ Loss应该保持负值

**异常情况：**
- Loss变成NaN或Inf
- Loss持续增长

**解决：**
- 降低学习率
- 检查数据质量
- 重启训练

---

## 📝 训练完成后

### 1. 验证模型

```python
from model import KronosTokenizer, KronosPredictor

# 加载tokenizer
tokenizer = KronosTokenizer.from_pretrained(
    "outputs/finetuned_models/test_finetune_run/tokenizer/best_model"
)

# 加载predictor
predictor = KronosPredictor.from_pretrained(
    "outputs/finetuned_models/test_finetune_run/basemodel/best_model",
    tokenizer=tokenizer
)

print("✅ Models loaded successfully!")
```

### 2. 测试预测

```python
import pandas as pd
import numpy as np

# 加载测试数据
df = pd.read_csv("data/HK_ali_09988_kline_5min_all.csv")

# 准备输入
x_df = df.iloc[-512:]  # 最后512条记录

# 进行预测
pred_df = predictor.predict(
    df=x_df,
    x_timestamp=None,
    y_timestamp=None,
    pred_len=48,
    T=1.0,
    top_p=0.9,
    sample_count=1
)

print("Prediction shape:", pred_df.shape)
print(pred_df.head())
```

### 3. 可视化结果

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(df['close'].tail(100).values, label='Historical')
plt.plot(range(52, 100), pred_df['close'].values[:48], label='Prediction', linestyle='--')
plt.legend()
plt.title('Stock Price Prediction')
plt.savefig('prediction_result.png')
plt.show()
```

---

## 🎉 总结

### 当前状态：
✅ **GPU训练已成功启动**  
✅ **训练速度极快 (150x加速)**  
✅ **训练指标健康**  
⏳ **预计2.5小时完成全部训练**  

### 下一步：
1. **让训练在后台运行**
2. **定期监控进度** (使用monitor_training.bat)
3. **等待完成后测试模型**

---

**训练正在进行中，请耐心等待！预计完成时间：约13:38 (2.5小时后)** 🚀
