# 银行股票批量训练监控报告

## 🚀 训练状态

**开始时间**: 2026-04-19 14:01  
**训练模式**: GPU加速 (RTX 2080 Ti)  
**输出语言**: 中文  
**总股票数**: 34只  
**已训练**: 1只 (工商银行)  
**待训练**: 33只  

---

## 📊 训练进度

### 当前正在训练
- **股票**: 浦发银行 (600000)
- **进度**: [1/34]
- **阶段**: Tokenizer训练 (Epoch 1/15)
- **设备**: cuda:0
- **状态**: 🟢 正常运行

### 训练队列
```
  1. ✅ 浦发银行(600000) - 训练中...
  2. ⏳ 华夏银行(600015) - 等待中
  3. ⏳ 民生银行(600016) - 等待中
  4. ⏳ 招商银行(600036) - 等待中
  5. ⏳ 杭州银行(600926) - 等待中
  ... (共34只)
```

---

## 💻 训练配置

### 硬件配置
- **GPU**: NVIDIA GeForce RTX 2080 Ti
- **显存**: 11 GB
- **CUDA版本**: 11.8
- **PyTorch版本**: 2.7.1+cu118

### 训练参数
```yaml
lookback_window: 60
predict_window: 10
batch_size: 8
tokenizer_epochs: 15
basemodel_epochs: 10
learning_rate:
  tokenizer: 0.0002
  predictor: 0.000001
device: cuda:0
```

### 预计时间
- **每只股票**: ~15分钟 (GPU)
- **33只股票**: ~8.25小时
- **完成时间**: 预计今晚22:30左右

---

## 🎯 训练特点

### ✅ 优势
1. **GPU加速**: 比CPU快5-6倍
2. **中文输出**: 易于理解和监控
3. **自动跳过**: 已训练的股票自动跳过
4. **详细统计**: 实时显示进度和预计剩余时间
5. **错误处理**: 失败后继续训练下一只

### 📝 输出示例
```
================================================================================
  Kronos 银行股票批量训练系统（GPU加速版）
================================================================================

📊 找到 34 个股票数据文件

📋 待训练股票列表 (33 只):
--------------------------------------------------------------------------------
   1. 浦发银行(600000)         - ⏳ 待训练
   2. 华夏银行(600015)         - ⏳ 待训练
   ...
--------------------------------------------------------------------------------

================================================================================
进度: [1/33]
================================================================================

--------------------------------------------------------------------------------
  开始训练: 浦发银行(600000)
--------------------------------------------------------------------------------
配置文件: finetune_csv/configs\config_600000_daily.yaml
数据文件: data\kronos_SHSE_600000_daily_2021-04-19_2026-04-18.csv
使用GPU: 0
开始时间: 2026-04-19 14:01:32

Using device: cuda:0 (rank=0, world_size=1, local_rank=0)
...
```

---

## 📈 实时监控命令

### 查看训练进度
```bash
# 查看最新日志
Get-Content "outputs\finetuned_models\*\logs\tokenizer_training_rank_0.log" -Tail 5

# 查看GPU使用情况
nvidia-smi

# 查看已完成数量
Get-ChildItem -Path "outputs\finetuned_models" -Directory | Measure-Object
```

### 检查训练状态
```bash
# 运行检查脚本
.\.venv\Scripts\python.exe tests/check_all_training_results.py
```

---

## 🔍 训练文件位置

### 配置文件
```
finetune_csv/configs/
├── config_icbc_daily.yaml       # 工商银行（已训练）
├── config_600000_daily.yaml     # 浦发银行（训练中）
├── config_600015_daily.yaml     # 华夏银行
└── ... (自动生成)
```

### 模型输出
```
outputs/finetuned_models/
├── icbc_daily_finetune/         # 工商银行（已完成）
│   ├── tokenizer/best_model/
│   └── basemodel/best_model/
├── 600000_daily_finetune/       # 浦发银行（训练中）
│   ├── tokenizer/
│   └── basemodel/
└── ... (自动生成)
```

### 训练日志
```
outputs/finetuned_models/*/logs/
├── tokenizer_training_rank_0.log
└── basemodel_training_rank_0.log
```

---

## ⚠️ 注意事项

### 1. 网络连接
- Hugging Face下载可能失败（已处理）
- 使用本地缓存的预训练模型

### 2. GPU内存
- 每只股票训练占用约2-3GB显存
- 训练完成后自动释放

### 3. 磁盘空间
- 每只股票模型约425MB
- 33只股票需要约14GB空间
- 确保有足够磁盘空间

### 4. 中断恢复
- 如果中断，可以重新运行
- 已训练的会自动跳过
- 使用 `--no-skip` 强制重新训练

---

## 🛠️ 控制命令

### 停止训练
```bash
# 按 Ctrl+C 停止当前训练
```

### 从指定位置继续
```bash
# 从第10只股票开始
.\.venv\Scripts\python.exe tests/batch_train_all_banks_cn.py --start 10 --gpu 0
```

### 训练特定范围
```bash
# 训练第5到第10只
.\.venv\Scripts\python.exe tests/batch_train_all_banks_cn.py --start 5 --end 10 --gpu 0
```

### 强制重新训练
```bash
# 不跳过已训练的
.\.venv\Scripts\python.exe tests/batch_train_all_banks_cn.py --no-skip --gpu 0
```

---

## 📊 预期结果

### 训练完成后
- ✅ 34个Tokenizer模型 (每个~15MB)
- ✅ 34个Predictor模型 (每个~409MB)
- ✅ 68个训练日志文件
- ✅ 34个配置文件
- ✅ 总计约14.5GB模型文件

### 模型质量预期
基于工商银行的训练结果：
- **Tokenizer Loss**: 0.018-0.025 (优秀)
- **Predictor Loss**: 4.0-5.5 (良好)
- **平均训练时间**: 15分钟/只

---

## 🎉 完成后的下一步

1. **验证所有模型**
   ```bash
   .\.venv\Scripts\python.exe tests/check_all_training_results.py
   ```

2. **生成训练报告**
   - 汇总所有股票的训练结果
   - 比较不同银行的模型质量
   - 分析Loss趋势

3. **进行预测测试**
   - 选择几只代表性股票
   - 测试预测准确性
   - 生成预测报告

4. **备份模型**
   - 压缩模型文件
   - 上传到云存储
   - 记录模型版本

---

## 📞 故障排除

### 问题1: GPU内存不足
```bash
# 减小batch size
# 修改配置文件中的 batch_size: 4
```

### 问题2: 训练卡住
```bash
# 检查GPU状态
nvidia-smi

# 查看日志
Get-Content "outputs\finetuned_models\*\logs\*.log" -Tail 20
```

### 问题3: 某只股票失败
- 检查数据文件是否完整
- 查看错误日志
- 手动训练该股票

---

**监控页面创建时间**: 2026-04-19 14:01  
**最后更新**: 训练中  
**下次更新**: 训练完成后
