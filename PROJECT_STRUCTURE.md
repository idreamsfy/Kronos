# Kronos 项目结构说明

## 📁 目录结构

```
Kronos/
├── src/                    # 源代码
│   ├── kronos/            # 核心模型代码
│   ├── finetuning/        # 微调训练代码
│   ├── prediction/        # 预测相关代码
│   └── data/              # 数据处理代码
│
├── scripts/               # 可执行脚本
│   ├── train/             # 训练脚本
│   ├── predict/           # 预测脚本
│   ├── data/              # 数据处理脚本
│   └── utils/             # 工具脚本
│
├── configs/               # 配置文件
│   ├── training/          # 训练配置
│   └── prediction/        # 预测配置
│
├── tests/                 # 测试代码
│   ├── unit/              # 单元测试
│   ├── integration/       # 集成测试
│   └── fixtures/          # 测试数据
│
├── data/                  # 数据目录
│   ├── raw/               # 原始数据
│   ├── processed/         # 处理后数据（Kronos格式）
│   └── metadata/          # 元数据
│
├── models/                # 模型文件
│   ├── pretrained/        # 预训练模型
│   ├── finetuned/         # 微调模型
│   └── checkpoints/       # 训练检查点
│
├── outputs/               # 输出目录（临时）
│   ├── predictions/       # 预测结果
│   ├── figures/           # 生成的图表
│   └── logs/              # 训练日志
│
├── docs/                  # 文档
│   ├── guides/            # 使用指南
│   ├── reports/           # 报告归档
│   └── api/               # API文档
│
├── notebooks/             # Jupyter notebooks
├── tools/                 # 辅助工具
├── examples/              # 示例代码
└── figures/               # 项目图片
```

## 🚀 快速开始

### 训练模型
```bash
# 单股票训练
python scripts/train/test_step3_finetune.py

# 批量训练银行股
python scripts/train/batch_train_all_banks_cn.py --gpu 0
```

### 预测
```bash
# 批量预测银行股
python scripts/predict/kronos_bank_prediction_report.py
```

### 数据下载
```bash
# 下载银行股票数据
python scripts/data/batch_download_bank_stocks.py
```

## 📝 重要说明

1. **src/** - 所有核心代码都在这里，可以导入使用
2. **scripts/** - 可直接运行的脚本
3. **configs/** - 所有配置文件
4. **data/** - 数据按原始和处理后分开存储
5. **models/** - 所有模型文件统一管理
6. **outputs/** - 临时输出，可以安全删除

## 🔄 迁移说明

如果你之前使用了旧的路径，请参考以下映射：

| 旧路径 | 新路径 |
|--------|--------|
| `model/` | `src/kronos/` |
| `finetune/` | `src/finetuning/` |
| `tests/batch_*.py` | `scripts/train/` 或 `scripts/predict/` |
| `outputs/finetuned_models/` | `models/finetuned/bank_stocks/` |
| `prediction_results/` | `outputs/predictions/json/` |
| `data/kronos_*.csv` | `data/processed/` |

## ⚙️ 环境变量

建议设置以下环境变量：
```bash
KRONOS_DATA_DIR=data/
KRONOS_MODEL_DIR=models/
KRONOS_OUTPUT_DIR=outputs/
```

## 📦 依赖安装

```bash
pip install -r requirements.txt
```

## 🧪 运行测试

```bash
# 单元测试
python -m pytest tests/unit/

# 集成测试
python -m pytest tests/integration/
```

## 📖 文档

- [快速开始](docs/guides/QUICK_START.md)
- [训练指南](docs/guides/)
- [预测报告](docs/reports/prediction_reports/)
- [训练报告](docs/reports/training_reports/)

## 🔧 开发

添加新功能时：
1. 核心代码放在 `src/` 对应模块
2. 可执行脚本放在 `scripts/` 对应类别
3. 配置放在 `configs/`
4. 测试放在 `tests/`
5. 文档放在 `docs/`

## 📋 清理

可以安全删除的目录：
- `outputs/` - 所有输出都可以重新生成
- `gmcache/` - 缓存文件

不要删除：
- `data/` - 需要重新下载
- `models/` - 需要重新训练
- `src/` - 源代码
