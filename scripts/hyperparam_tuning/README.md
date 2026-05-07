# 🔬 超参数调优工具集

本目录包含用于优化Kronos模型超参数的工具和脚本。

---

## 📋 目录结构

```
scripts/hyperparam_tuning/
├── README.md                          # 本文件
├── test_sampling_params.py           # Phase 1: 采样参数测试
├── search_learning_rate.py           # Phase 2: 学习率搜索
└── tune_regularization.py            # Phase 3: 正则化调优 (待创建)
```

---

## 🎯 调优目标

### 当前模型性能
- **MAPE**: 1.70%
- **R²**: -3.76
- **方向准确率**: 66.7%
- **验证Loss**: 3.70

### 预期目标
- **MAPE**: < 1.4% (-0.3%)
- **R²**: > -1.0 (+2.8)
- **方向准确率**: > 70% (+3%)
- **验证Loss**: < 2.8 (-0.9)

---

## 🚀 使用指南

### Phase 1: 采样参数测试（推荐首先执行）

**目的**: 找到最优的Temperature和Top-p组合  
**耗时**: ~5分钟（仅推理，无需训练）  
**风险**: 无

```bash
# 运行采样参数测试
python scripts/hyperparam_tuning/test_sampling_params.py
```

**测试的配置**:
1. 保守型: T=0.8, top_p=0.9
2. 当前默认: T=1.0, top_p=0.9
3. 均衡型: T=1.0, top_p=0.95
4. 激进型: T=1.2, top_p=0.95
5. 全采样: T=1.0, top_p=1.0

**输出**:
- `outputs/hyperparam_tuning/sampling_params_test_*.csv`
- `outputs/hyperparam_tuning/sampling_params_comparison_*.png`

---

### Phase 2: 学习率搜索

**目的**: 找到最优学习率  
**耗时**: ~9小时（4个实验 × 140分钟/实验）  
**风险**: 低

```bash
# 运行学习率搜索
python scripts/hyperparam_tuning/search_learning_rate.py
```

**测试的学习率**:
- 1e-5 (保守)
- 2e-5 (当前使用)
- 5e-5 (中等)
- 1e-4 (激进)

**注意**: 
- 每个实验会生成独立的模型
- 模型保存在 `outputs/models/lr_search_*/`
- 建议先运行Phase 1，确定最佳采样参数后再进行Phase 2

---

### Phase 3: 正则化调优（待实施）

**目的**: 减少过拟合  
**耗时**: ~4小时  
**风险**: 中

```bash
# 运行正则化调优（待创建）
python scripts/hyperparam_tuning/tune_regularization.py
```

**测试的参数**:
- weight_decay: 0.01, 0.05, 0.1
- dropout: 0.1, 0.2, 0.3 (如果模型支持)

---

## 📊 结果分析

### 查看实验结果

所有实验结果保存在 `outputs/hyperparam_tuning/` 目录：

```bash
# 查看采样参数测试结果
ls outputs/hyperparam_tuning/sampling_params_test_*.csv

# 查看学习率搜索记录
cat outputs/hyperparam_tuning/lr_search_experiments.csv
```

### 比较不同配置

使用以下指标评估：
1. **验证Loss** - 越低越好
2. **MAPE** - 越低越好
3. **R²** - 越高越好（正值最佳）
4. **方向准确率** - 越高越好

---

## 💡 最佳实践

### 1. 按顺序执行

```
Phase 1 (采样参数) → Phase 2 (学习率) → Phase 3 (正则化)
```

**理由**: 
- Phase 1成本低，快速见效
- Phase 2需要大量计算资源
- Phase 3在前两步基础上进一步优化

### 2. 保留基线模型

永远不要覆盖原始模型：
```
outputs/models/predictor/best_model/  # 原始模型（保留）
outputs/models/lr_search_*/           # 新实验模型
```

### 3. 详细记录

每次实验都会自动生成记录：
- 配置文件
- 训练日志
- 性能指标

### 4. A/B测试

在部署前，对比新旧模型：
```python
# 使用两个模型进行预测，比较结果
model_old = load_model("outputs/models/predictor/best_model")
model_new = load_model("outputs/models/lr_search_1e-4_xxx")

pred_old = model_old.predict(...)
pred_new = model_new.predict(...)

# 比较MAPE、R²等指标
```

---

## ⚠️ 注意事项

### GPU资源

- 每个学习率实验需要约140分钟GPU时间
- 确保GPU可用且显存充足（≥12GB）
- 可以并行运行多个实验（如果有多块GPU）

### 磁盘空间

- 每个模型约400MB
- 4个学习率实验需要约1.6GB空间
- 定期清理失败的实验

### 中断恢复

如果训练中断：
1. 检查日志文件：`outputs/models/logs/`
2. 查看已完成的epoch
3. 决定是否继续或重新开始

---

## 📈 预期时间线

| 阶段 | 任务 | 预计耗时 | 累计耗时 |
|------|------|---------|---------|
| Day 1 | Phase 1: 采样参数测试 | 5分钟 | 5分钟 |
| Day 2-4 | Phase 2: 学习率搜索 | 9小时 | 9小时 |
| Day 5-6 | Phase 3: 正则化调优 | 4小时 | 13小时 |
| Day 7 | 结果分析与模型选择 | 2小时 | 15小时 |

**总计**: 约7天完成全部调优

---

## 🎯 成功标准

调优成功的标志：

✅ **短期目标**（必须达到）:
- MAPE < 1.5%
- R² > -1.0
- 验证Loss < 3.0

✅ **中期目标**（期望达到）:
- MAPE < 1.3%
- R² > 0.0
- 验证Loss < 2.5

✅ **长期目标**（理想状态）:
- MAPE < 1.0%
- R² > 0.3
- 方向准确率 > 75%

---

## 🔧 故障排除

### 问题1: CUDA Out of Memory

**解决方案**:
```yaml
# 修改配置文件
training:
  batch_size: 16  # 从32降低到16
  use_amp: true   # 确保启用混合精度
```

### 问题2: 训练不收敛

**可能原因**:
- 学习率过高
- 数据质量问题

**解决方案**:
- 尝试更小的学习率（1e-5）
- 检查数据预处理

### 问题3: 验证Loss持续上升

**可能原因**:
- 过拟合
- 学习率过高

**解决方案**:
- 增加weight_decay
- 降低学习率
- 启用早停机制

---

## 📞 支持

如有问题，请查看：
- [OPTION2_FEASIBILITY_ANALYSIS.md](../../OPTION2_FEASIBILITY_ANALYSIS.md)
- [OPTION2_EXECUTIVE_SUMMARY.md](../../OPTION2_EXECUTIVE_SUMMARY.md)
- [MODEL_OPTIMIZATION_PLAN.md](../../MODEL_OPTIMIZATION_PLAN.md)

---

**最后更新**: 2026年5月7日  
**维护者**: AI Assistant
