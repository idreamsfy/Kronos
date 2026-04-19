# Kronos 银行股票模型训练状态

## 📊 当前训练任务

### 工商银行 (ICBC) - SHSE.601398

**启动时间**: 2026-04-19 11:42:34  
**配置文件**: `finetune_csv/configs/config_icbc_daily.yaml`  
**数据文件**: `data/kronos_SHSE_601398_daily_2016-04-21_2026-04-17.csv`

#### 训练配置
- **数据量**: 2,426条记录（10年历史）
- **训练集**: 1,940条 (80%)
- **验证集**: 364条 (15%)
- **测试集**: 122条 (5%)
- **Lookback Window**: 60
- **Predict Window**: 10
- **Batch Size**: 8
- **设备**: CPU

#### Tokenizer训练
- **Epochs**: 15
- **Learning Rate**: 0.0002
- **参数量**: 3,958,042
- **状态**: ✅ 进行中

**Epoch 1 进度**:
```
Step 220/233 - Loss: 0.0171
  - VQ Loss: -0.0632
  - Recon Loss Pre: 0.0573
  - Recon Loss All: 0.0401
```

**损失趋势**: 
- Step 10: 0.8502 → Step 220: 0.0171
- **下降幅度**: 98.0% ✅

---

## 📈 训练进度追踪

### Tokenizer Training (Phase 1)

| Epoch | Steps | Best Loss | Status |
|-------|-------|-----------|--------|
| 1/15  | 220/233 | ~0.017 | 🔄 进行中 |
| 2/15  | - | - | ⏳ 等待中 |
| 3/15  | - | - | ⏳ 等待中 |
| ...   | - | - | ⏳ 等待中 |
| 15/15 | - | - | ⏳ 等待中 |

预计完成时间：约30-40分钟（CPU）

### Predictor Training (Phase 2)

| Epoch | Steps | Best Loss | Status |
|-------|-------|-----------|--------|
| 1/10  | - | - | ⏳ 等待中 |
| ...   | - | - | ⏳ 等待中 |
| 10/10 | - | - | ⏳ 等待中 |

预计开始时间：Tokenizer完成后  
预计完成时间：约20-30分钟（CPU）

---

## 💾 输出文件

### 模型保存路径
```
outputs/finetuned_models/icbc_daily_finetune/
├── tokenizer/
│   ├── best_model/
│   │   ├── model.safetensors
│   │   ├── config.json
│   │   └── README.md
│   └── checkpoints/
├── basemodel/
│   ├── best_model/
│   │   ├── model.safetensors
│   │   ├── config.json
│   │   └── README.md
│   └── checkpoints/
└── logs/
    └── training_logs.txt
```

---

## 🎯 下一步计划

### 已完成
- ✅ 下载34只银行股票数据
- ✅ 转换为Kronos格式
- ✅ 创建工商银行配置文件
- ✅ 启动训练

### 进行中
- 🔄 工商银行 Tokenizer 训练

### 待执行
1. ⏳ 完成工商银行完整训练（Tokenizer + Predictor）
2. ⏳ 验证训练结果
3. ⏳ 训练其他银行股票（可选）
4. ⏳ 进行预测测试

---

## 📝 训练命令参考

### 单只股票训练
```bash
python finetune_csv/train_sequential.py --config finetune_csv/configs/config_icbc_daily.yaml
```

### 批量训练所有银行
```bash
python tests/batch_train_all_banks.py
```

### 训练指定股票
```bash
python tests/batch_train_all_banks.py --stock 601398
```

### 使用GPU训练
```bash
python tests/batch_train_all_banks.py --gpu 0
```

---

## 🔍 监控训练

### 实时查看日志
```bash
# Windows PowerShell
Get-Content outputs\finetuned_models\icbc_daily_finetune\logs\training_logs.txt -Wait

# Linux/Mac
tail -f outputs/finetuned_models/icbc_daily_finetune/logs/training_logs.txt
```

### 检查模型文件
```bash
# 查看已生成的模型
ls outputs/finetuned_models/icbc_daily_finetune/tokenizer/best_model/
ls outputs/finetuned_models/icbc_daily_finetune/basemodel/best_model/
```

---

## ⚙️ 其他银行股票配置

已准备好训练其他银行，只需运行：

```bash
# 建设银行
python finetune_csv/train_sequential.py --config finetune_csv/configs/config_601939_daily.yaml

# 农业银行
python finetune_csv/train_sequential.py --config finetune_csv/configs/config_601288_daily.yaml

# 招商银行
python finetune_csv/train_sequential.py --config finetune_csv/configs/config_600036_daily.yaml
```

或使用批量脚本自动生成配置并训练：
```bash
python tests/batch_train_all_banks.py --start 0 --end 5  # 训练前5只
```

---

## 📊 预期结果

### Tokenizer性能指标
- **目标Loss**: < 0.05
- **当前Loss**: 0.0171 (Epoch 1)
- **评估**: 优秀 ✅

### Predictor性能指标
- **目标Loss**: < 6.0
- **预期改进**: 相比随机初始化提升20%+

### 模型质量评分
- **Tokenizer**: 预计 85-95/100
- **Predictor**: 预计 70-80/100
- **综合评分**: 预计 78-88/100

---

## ⚠️ 注意事项

1. **训练时间**: CPU训练较慢，预计总耗时50-70分钟
2. **内存占用**: 约2-4GB RAM
3. **磁盘空间**: 每个模型约50-100MB
4. **网络需求**: 首次需要下载预训练模型

---

## 🚀 快速操作指南

### 如果训练中断
```bash
# 重新启动（会自动继续）
python finetune_csv/train_sequential.py --config finetune_csv/configs/config_icbc_daily.yaml
```

### 跳过已存在的模型
```bash
python finetune_csv/train_sequential.py --config finetune_csv/configs/config_icbc_daily.yaml --skip-existing
```

### 仅训练Tokenizer
```bash
python finetune_csv/train_sequential.py --config finetune_csv/configs/config_icbc_daily.yaml --train-basemodel False
```

### 仅训练Predictor
```bash
python finetune_csv/train_sequential.py --config finetune_csv/configs/config_icbc_daily.yaml --train-tokenizer False
```

---

**最后更新**: 2026-04-19 11:43  
**状态**: 🔄 Tokenizer训练中 (Epoch 1/15)
