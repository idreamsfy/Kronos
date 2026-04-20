# Kronos 重构快速参考

## 🚀 常用命令

### 训练
```bash
# 批量训练银行股（中文输出）
python scripts/train/batch_train_all_banks_cn.py --gpu 0

# 单股票训练
python scripts/train/test_step3_finetune.py
```

### 预测
```bash
# 批量预测银行股
python scripts/predict/kronos_bank_prediction_report.py

# 批量预测（简化版）
python scripts/predict/batch_predict_banks_next_week.py
```

### 数据
```bash
# 下载银行股票数据
python scripts/data/batch_download_bank_stocks.py

# 转换数据格式
python scripts/data/convert_to_kronos_format.py

# 检查数据兼容性
python scripts/data/check_data_compatibility.py
```

### 工具
```bash
# 检查训练状态
python scripts/utils/check_all_training_results.py

# 验证环境
python tools/verify_environment.py

# 测试torchrun
python tools/test_torchrun.py
```

---

## 📁 重要目录

| 目录 | 用途 | 示例 |
|------|------|------|
| `src/kronos/` | 核心模型代码 | 导入模型 |
| `scripts/train/` | 训练脚本 | 运行训练 |
| `scripts/predict/` | 预测脚本 | 生成预测 |
| `data/processed/` | Kronos格式数据 | 训练数据 |
| `models/finetuned/` | 微调模型 | 加载模型 |
| `outputs/predictions/` | 预测结果 | 查看结果 |
| `docs/reports/` | 报告归档 | 查阅报告 |

---

## 🔄 路径变更对照

### 代码导入
```python
# ❌ 旧
from model.kronos import Kronos, KronosTokenizer, KronosPredictor
from finetune.config import Config

# ✅ 新
from src.kronos import Kronos, KronosTokenizer, KronosPredictor
from src.finetuning import Config
```

### 脚本执行
```bash
# ❌ 旧
python tests/batch_train_all_banks_cn.py
python tests/kronos_bank_prediction_report.py

# ✅ 新
python scripts/train/batch_train_all_banks_cn.py
python scripts/predict/kronos_bank_prediction_report.py
```

### 数据文件
```python
# ❌ 旧
"data/kronos_SHSE_601398_daily.csv"
"outputs/finetuned_models/601398_daily_finetune/"

# ✅ 新
"data/processed/kronos_SHSE_601398_daily.csv"
"models/finetuned/bank_stocks/601398_daily_finetune/"
```

---

## 📊 项目统计

- **源代码**: src/ (4个模块)
- **脚本**: scripts/ (19个脚本)
- **数据**: data/processed/ (32个CSV文件)
- **模型**: models/finetuned/ (32个银行股模型)
- **文档**: docs/ (38个报告)
- **配置**: configs/training/ (2个配置文件)

---

## ⚡ 快速导航

### 我想...

**训练模型**
→ `scripts/train/batch_train_all_banks_cn.py`

**生成预测**
→ `scripts/predict/kronos_bank_prediction_report.py`

**下载数据**
→ `scripts/data/batch_download_bank_stocks.py`

**查看训练状态**
→ `scripts/utils/check_all_training_results.py`

**查看预测报告**
→ `docs/reports/prediction_reports/`

**了解项目结构**
→ `PROJECT_STRUCTURE.md`

---

## 🔧 常见问题

### Q: 找不到模块？
A: 确保在根目录运行，或添加项目根目录到Python路径：
```python
import sys
sys.path.insert(0, '/path/to/Kronos')
```

### Q: 数据在哪里？
A: 
- 原始数据: `data/raw/`
- Kronos格式: `data/processed/`
- 元数据: `data/metadata/`

### Q: 模型在哪里？
A:
- 预训练: `models/pretrained/`
- 微调: `models/finetuned/bank_stocks/`

### Q: 预测结果在哪里？
A: `outputs/predictions/json/`

### Q: 如何清理输出？
A: 可以安全删除 `outputs/` 目录所有内容（可重新生成）

---

## 📞 需要帮助？

1. 查看 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 完整结构说明
2. 查看 [REFACTORING_COMPLETE.md](REFACTORING_COMPLETE.md) - 重构详情
3. 查看 `docs/guides/` - 使用指南
4. 提交 Issue - 问题反馈

---

**最后更新**: 2026-04-19  
**版本**: 重构后 v2.0
