# 📁 Kronos 项目目录重构方案

**重构日期**: 2026年4月21日  
**目标**: 清理冗余文件，优化目录结构，提高可维护性  

---

## 🎯 重构目标

1. ✅ 清理临时文档和测试文件
2. ✅ 整理配置文件到统一位置
3. ✅ 归档历史训练记录
4. ✅ 简化根目录结构
5. ✅ 保留核心功能文件

---

## 📂 重构后的目录结构

```
Kronos/
├── README.md                          # 主文档
├── requirements.txt                   # 依赖
├── LICENSE                            # 许可证
├── .gitignore                         # Git 忽略
│
├── model/                             # 模型核心代码
│   ├── __init__.py
│   ├── kronos.py                      # Kronos 主模型
│   ├── module.py                      # 模型模块
│   └── pretrained_models/             # 预训练模型
│       ├── README.md
│       ├── Kronos-base/
│       └── Kronos-Tokenizer-base/
│
├── finetune/                          # 微调相关
│   ├── predict_ths_300033.py         # ✨ 预测脚本
│   ├── compare_predictions.py        # ✨ 对比分析
│   ├── finetune_ths_real.py          # ✨ 真正微调
│   ├── finetune_ths_simple.py        # 简单预测
│   ├── preprocess_ths_data.py        # 数据预处理
│   ├── config_loader.py              # 配置加载器
│   ├── train_predictor.py            # 预测器训练
│   ├── train_tokenizer.py            # Tokenizer 训练
│   ├── qlib_data_preprocess.py       # Qlib 数据处理
│   ├── qlib_test.py                  # Qlib 测试
│   ├── utils/
│   │   ├── __init__.py
│   │   └── training_utils.py
│   └── configs/                       # 微调配置
│       └── ths_300033_config.py      # 同花顺配置
│
├── finetune_csv/                      # CSV 微调（独立模块）
│   ├── README.md
│   ├── README_CN.md
│   ├── config_loader.py
│   ├── finetune_base_model.py
│   ├── finetune_tokenizer.py
│   ├── train_sequential.py
│   ├── check_training_status.py
│   ├── configs/
│   └── examples/
│
├── scripts/                           # 工具脚本
│   ├── data/                          # 数据获取脚本
│   │   ├── fetch_akshare_data.py
│   │   ├── fetch_300033_*.py         # 各种数据源
│   │   └── validate_akshare_data.py
│   ├── training/                      # 训练脚本
│   │   ├── start_training.sh
│   │   ├── start_finetune_ths.sh
│   │   ├── start_finetune_ths_real.sh
│   │   ├── monitor.sh
│   │   └── monitor_finetune.sh
│   └── utils/                         # 工具脚本
│       ├── check_environment.py
│       └── debug_setup.py
│
├── webui/                             # Web 界面
│   ├── app.py
│   ├── run.py
│   ├── start.sh
│   ├── requirements.txt
│   ├── README.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── PORT_CONFIGURATION.md
│   └── templates/
│       └── index.html
│
├── tests/                             # 测试文件
│   ├── test_kronos_regression.py     # 回归测试
│   ├── test_finutned_tokenizer.py    # Tokenizer 测试
│   ├── testaka.py                    # AkShare 测试
│   ├── tusharetest.py                # Tushare 测试
│   ├── test_mootdx.py                # Mootdx 测试
│   ├── data/                         # 测试数据
│   │   ├── generate_regression_output.py
│   │   ├── regression_input.csv
│   │   └── regression_output_*.csv
│   └── integration/                  # 集成测试
│       ├── test_step1_load_model.py
│       ├── test_step2_prepare_data.py
│       ├── test_step3_finetune.py
│       └── test_step3_predict.py
│
├── examples/                          # 示例代码
│   ├── prediction_example.py
│   ├── prediction_batch_example.py
│   ├── prediction_cn_markets_day.py
│   ├── prediction_wo_vol_example.py
│   └── use_local_model.py
│
├── config/                            # 全局配置
│   └── training/
│       └── mps_config.yaml
│
├── docs/                              # 文档
│   ├── guides/                        # 使用指南
│   │   ├── mps_gpu_guide.md
│   │   └── ...
│   ├── api/                           # API 文档
│   ├── archive/                       # 归档文档
│   │   └── *.md                      # 所有历史文档
│   └── README.md
│
├── outputs/                           # 输出文件
│   ├── models/                        # 训练模型
│   │   ├── finetune_300033_base_real/
│   │   ├── finetune_tokenizer_300033_mps/
│   │   └── finetune_tokenizer_demo/
│   ├── predictions/                   # 预测结果
│   │   ├── ths_300033_*.csv
│   │   └── comparison_*.csv
│   └── logs/                          # 训练日志
│       └── *.log
│
├── data/                              # 数据文件
│   ├── raw/                           # 原始数据
│   │   └── akshare/
│   │       └── daily_300033.csv
│   ├── processed/                     # 处理后数据
│   │   ├── train_data.pkl
│   │   ├── val_data.pkl
│   │   └── test_data.pkl
│   └── README.md
│
└── figures/                           # 图表图片
    ├── logo.png
    ├── overview.png
    ├── prediction_example.png
    └── backtest_result_example.png
```

---

## 🗑️ 需要清理的文件

### 1. 根目录临时文档 (移动到 docs/archive/)

```
FINETUNE_CHALLENGES_AND_SOLUTIONS.md
FINETUNE_FINAL_COMPLETE_REPORT.md
FINETUNE_SUCCESS_REPORT.md
FINETUNE_SUCCESS_SUMMARY.md
FINETUNE_SUMMARY_AND_RECOMMENDATION.md
FINETUNE_THS_300033_COMPLETE.md
GIT_PUSH_SUCCESS.md
MODEL_DOWNLOAD_COMPLETE.md
MODEL_DOWNLOAD_STATUS.md
PREDICTION_COMPARISON_REPORT.md
PREDICTION_THS_300033_10DAYS.md
PRETRAINED_MODELS_LOCAL_SETUP.md
PROJECT_STRUCTURE_GUIDE.md
QUICK_START.md
REFACTORING_COMPLETE.md
REFACTORING_PLAN.md
TOMORROW_TRAINING_GUIDE_DAY3.md
TRAINING_PAUSED_DAY2.md
WEBUI_DEPLOYMENT_COMPLETE.md
torchrun_LIMITATIONS.md
training_results_analysis.md
start_training_now.sh
```

### 2. 重复的测试文档 (移动到 docs/archive/)

```
tests/AKSHARE_DATA_README.md
tests/AKSHARE_DATA_SUMMARY.md
tests/AKSHARE_STATUS_REPORT.md
tests/DATA_SOURCES_TEST_REPORT.md
tests/FETCH_300033_ISSUE.md
tests/FINAL_DATA_SOURCES_SUMMARY.md
tests/FUTU_API_GUIDE.md
tests/TUSHARE_SETUP_GUIDE.md
```

### 3. Futu API 技能文档 (可选归档)

```
tests/skills/LEGAL_Futu_api_cn.md
tests/skills/LEGAL_Futu_api_en.md
tests/skills/futuapi/           # 整个目录可以归档
tests/skills/install-futu-opend/ # 整个目录可以归档
```

### 4. 冗余的 README 文件

```
outputs/models/*/README.md       # 模型目录中的 README
finetune_csv/outputs/*/README.md # 示例输出中的 README
```

---

## 📝 重构步骤

### Step 1: 创建归档目录

```bash
mkdir -p docs/archive
```

### Step 2: 移动临时文档

```bash
# 移动根目录临时文档
mv FINETUNE_*.md docs/archive/
mv PREDICTION_*.md docs/archive/
mv *_COMPLETE.md docs/archive/
mv *_STATUS.md docs/archive/
mv *_GUIDE.md docs/archive/
mv *_REPORT.md docs/archive/
mv TRAINING_*.md docs/archive/
mv WEBUI_*.md docs/archive/
mv PRETRAINED_*.md docs/archive/
mv PROJECT_*.md docs/archive/
mv QUICK_START.md docs/archive/
mv REFACTORING_*.md docs/archive/
mv TOMORROW_*.md docs/archive/
mv torchrun_LIMITATIONS.md docs/archive/
mv training_results_analysis.md docs/archive/
mv start_training_now.sh docs/archive/
```

### Step 3: 移动测试文档

```bash
mv tests/*.md docs/archive/
```

### Step 4: 整理配置文件

```bash
# 将配置移到 config 目录
mkdir -p config/training
mv finetune/configs/ths_300033_config.py config/
mv config/training/mps_config.yaml config/training/
```

### Step 5: 更新引用路径

需要更新以下文件中的路径引用：
- `finetune/predict_ths_300033.py`
- `finetune/compare_predictions.py`
- `finetune/finetune_ths_real.py`
- `webui/app.py`

### Step 6: 更新 .gitignore

确保忽略以下内容：
```
docs/archive/
outputs/
data/raw/
*.log
__pycache__/
```

---

## ✅ 重构检查清单

- [ ] 创建 docs/archive/ 目录
- [ ] 移动所有临时文档到 archive
- [ ] 移动测试文档到 archive
- [ ] 整理配置文件到 config/
- [ ] 更新代码中的路径引用
- [ ] 更新 .gitignore
- [ ] 验证核心功能正常
- [ ] 提交重构更改
- [ ] 更新 README.md

---

## 🎯 重构收益

### 优点

1. ✅ **清晰的目录结构**
   - 核心代码、脚本、文档分离
   - 易于导航和维护

2. ✅ **减少混乱**
   - 根目录只保留关键文件
   - 临时文档归档管理

3. ✅ **更好的组织**
   - 配置文件集中管理
   - 输出文件分类存储

4. ✅ **易于扩展**
   - 模块化结构
   - 新功能容易添加

### 注意事项

⚠️ **备份重要文件**
- 重构前备份所有文件
- 确认归档后可恢复

⚠️ **更新路径引用**
- 检查所有硬编码路径
- 使用相对路径或配置

⚠️ **测试功能**
- 重构后验证所有功能
- 确保没有破坏现有代码

---

## 📊 重构前后对比

### 重构前

```
根目录: ~50 个文件 (包括大量 .md 文档)
结构: 扁平化，难以导航
文档: 分散在各处
```

### 重构后

```
根目录: ~8 个核心文件
结构: 清晰的层级结构
文档: 集中在 docs/
```

---

**准备开始重构？** 

执行以下步骤：
1. 备份当前项目
2. 运行重构脚本
3. 验证功能
4. 提交更改

---

*最后更新: 2026年4月21日*
