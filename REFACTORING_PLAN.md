# Kronos 项目重构方案

## 📋 当前问题分析

### 1. 根目录混乱
- ❌ 大量临时文档文件 (30+个.md文件)
- ❌ 测试脚本散落在根目录
- ❌ 配置文件没有统一管理
- ❌ 输出文件分散

### 2. 目录结构不合理
- ❌ `tests/` 包含太多非测试文件（下载脚本、预测脚本等）
- ❌ `outputs/` 和 `prediction_results/` 功能重叠
- ❌ `data/` 混合原始数据和Kronos格式数据
- ❌ `finetune/` 和 `finetune_csv/` 功能重复

### 3. 文件组织问题
- ❌ 批量训练脚本有多个版本
- ❌ 预测报告散落在不同位置
- ❌ 缺少清晰的模块划分

---

## 🎯 重构目标

1. **清晰的目录结构** - 按功能模块化组织
2. **分离关注点** - 代码、数据、配置、文档分离
3. **易于维护** - 相关文件放在一起
4. **便于扩展** - 新功能容易添加
5. **规范化** - 遵循Python项目最佳实践

---

## 📁 新目录结构

```
Kronos/
├── .gitignore
├── README.md
├── requirements.txt
├── LICENSE
│
├── docs/                          # 文档目录
│   ├── guides/                    # 使用指南
│   │   ├── quick_start.md
│   │   ├── training_guide.md
│   │   ├── prediction_guide.md
│   │   └── gpu_setup.md
│   ├── reports/                   # 报告归档
│   │   ├── training_reports/      # 训练报告
│   │   ├── prediction_reports/    # 预测报告
│   │   └── analysis_reports/      # 分析报告
│   └── api/                       # API文档
│       └── model_api.md
│
├── src/                           # 源代码
│   ├── kronos/                    # 核心模型
│   │   ├── __init__.py
│   │   ├── kronos.py
│   │   ├── module.py
│   │   └── utils.py
│   │
│   ├── finetuning/                # 微调相关
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── dataset.py
│   │   ├── train_tokenizer.py
│   │   ├── train_predictor.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── training_utils.py
│   │
│   ├── prediction/                # 预测相关
│   │   ├── __init__.py
│   │   ├── predictor.py
│   │   └── visualizer.py
│   │
│   └── data/                      # 数据处理
│       ├── __init__.py
│       ├── downloader.py          # 数据下载
│       ├── converter.py           # 格式转换
│       └── validator.py           # 数据验证
│
├── configs/                       # 配置文件
│   ├── training/                  # 训练配置
│   │   ├── default.yaml
│   │   ├── bank_stocks.yaml
│   │   └── custom_template.yaml
│   └── prediction/                # 预测配置
│       └── default.yaml
│
├── scripts/                       # 可执行脚本
│   ├── train/                     # 训练脚本
│   │   ├── train_single.py        # 单GPU训练
│   │   ├── train_multi.py         # 多GPU训练
│   │   └── batch_train_banks.py   # 批量训练银行股
│   │
│   ├── predict/                   # 预测脚本
│   │   ├── predict_single.py      # 单股票预测
│   │   └── batch_predict_banks.py # 批量预测银行股
│   │
│   ├── data/                      # 数据处理脚本
│   │   ├── download_stock_data.py # 下载股票数据
│   │   ├── convert_format.py      # 转换数据格式
│   │   └── validate_data.py       # 验证数据
│   │
│   └── utils/                     # 工具脚本
│       ├── check_training_status.py
│       ├── monitor_gpu.py
│       └── cleanup.py
│
├── tests/                         # 测试代码
│   ├── unit/                      # 单元测试
│   │   ├── test_model.py
│   │   ├── test_dataset.py
│   │   └── test_config.py
│   │
│   ├── integration/               # 集成测试
│   │   ├── test_training.py
│   │   └── test_prediction.py
│   │
│   └── fixtures/                  # 测试数据
│       └── sample_data.csv
│
├── data/                          # 数据目录
│   ├── raw/                       # 原始数据
│   │   └── *.csv
│   ├── processed/                 # 处理后数据（Kronos格式）
│   │   └── *.csv
│   ├── metadata/                  # 元数据
│   │   └── bank_stocks_list.csv
│   └── README.md
│
├── models/                        # 模型文件
│   ├── pretrained/                # 预训练模型
│   │   └── Kronos-base/
│   ├── finetuned/                 # 微调模型
│   │   ├── bank_stocks/
│   │   │   ├── 601398_daily/     # 工商银行
│   │   │   ├── 600036_daily/     # 招商银行
│   │   │   └── ...
│   │   └── custom/
│   └── checkpoints/               # 训练检查点
│
├── outputs/                       # 输出目录（临时）
│   ├── predictions/               # 预测结果
│   │   ├── json/
│   │   └── csv/
│   ├── figures/                   # 生成的图表
│   └── logs/                      # 训练日志
│
├── notebooks/                     # Jupyter notebooks
│   ├── exploratory_analysis.ipynb
│   ├── model_evaluation.ipynb
│   └── prediction_demo.ipynb
│
├── tools/                         # 辅助工具
│   ├── setup_gpu_environment.bat
│   ├── monitor_training.bat
│   └── verify_environment.py
│
└── examples/                      # 示例代码
    ├── basic_prediction.py
    ├── batch_prediction.py
    └── custom_training.py
```

---

## 🔄 迁移步骤

### Phase 1: 创建新目录结构
1. 创建所有新目录
2. 添加 `__init__.py` 文件

### Phase 2: 移动源代码
1. `model/` → `src/kronos/`
2. `finetune/` → `src/finetuning/`
3. `finetune_csv/` → 合并到 `src/finetuning/`

### Phase 3: 移动脚本
1. 根目录测试脚本 → `scripts/`
2. `tests/` 中的工具脚本 → `scripts/`
3. 保留真正的测试在 `tests/`

### Phase 4: 整理数据
1. `data/*.csv` → `data/raw/` 或 `data/processed/`
2. `prepared_data/` → `data/processed/`
3. `prediction_results/` → `outputs/predictions/`

### Phase 5: 整理文档
1. 根目录 `.md` 文件 → `docs/reports/`
2. 分类归档（训练、预测、分析）
3. 删除过时文档

### Phase 6: 整理模型
1. `outputs/finetuned_models/` → `models/finetuned/`
2. `outputs/models/` → `models/pretrained/`

### Phase 7: 更新导入路径
1. 更新所有Python文件的import语句
2. 更新配置文件中的路径
3. 测试所有功能

### Phase 8: 清理
1. 删除空目录
2. 删除重复文件
3. 更新 `.gitignore`

---

## ⚠️ 注意事项

1. **备份**: 重构前完整备份
2. **Git历史**: 使用 `git mv` 保持历史
3. **测试**: 每步之后验证功能
4. **文档**: 更新所有路径引用
5. **配置**: 检查所有硬编码路径

---

## 📝 后续优化建议

1. **添加setup.py** - 使项目可安装
2. **添加pyproject.toml** - 现代Python项目配置
3. **添加Makefile** - 简化常用命令
4. **添加Dockerfile** - 容器化部署
5. **添加CI/CD** - 自动化测试和部署
6. **添加logging配置** - 统一日志管理
7. **添加环境变量管理** - 使用 `.env` 文件

---

**预计时间**: 2-3小时  
**风险等级**: 中等（需要仔细测试）  
**回滚方案**: Git恢复
