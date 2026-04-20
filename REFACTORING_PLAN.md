# 📁 Kronos 项目结构重构方案

**创建时间**: 2026年4月20日  
**目标**: 优化项目结构，提高可维护性和开发效率  

---

## 🎯 重构目标

1. **清晰分离**：代码、数据、文档、配置
2. **便于管理**：减少根目录混乱
3. **开发友好**：清晰的模块划分
4. **版本控制**：合理的 .gitignore 配置

---

## 📂 建议的新结构

```
Kronos/
├── .github/                    # GitHub 相关配置
│   ├── workflows/             # CI/CD 工作流
│   └── ISSUE_TEMPLATE/        # Issue 模板
│
├── config/                     # 配置文件集中管理
│   ├── training/              # 训练配置
│   │   ├── default.yaml
│   │   ├── mps_config.yaml
│   │   └── multi_gpu_config.yaml
│   └── inference/             # 推理配置
│       └── prediction.yaml
│
├── data/                       # 数据目录
│   ├── raw/                   # 原始数据
│   │   └── akshare/          # AkShare/Futu 获取的原始 CSV
│   ├── processed/            # 处理后的数据 (pickle)
│   │   ├── train_data.pkl
│   │   ├── val_data.pkl
│   │   └── test_data.pkl
│   └── README.md             # 数据说明文档
│
├── docs/                       # 文档目录
│   ├── guides/               # 使用指南
│   │   ├── installation.md
│   │   ├── training.md
│   │   ├── inference.md
│   │   └── mps_gpu_guide.md
│   ├── api/                  # API 文档
│   ├── tutorials/            # 教程
│   └── README.md
│
├── examples/                   # 示例代码
│   ├── basic_prediction.py
│   ├── batch_prediction.py
│   ├── custom_data_example.py
│   └── data/                 # 示例数据
│       └── XSHG_5min_600977.csv
│
├── finetune/                   # 微调模块
│   ├── __init__.py
│   ├── config.py             # 配置类
│   ├── dataset.py            # 数据集处理
│   ├── train_tokenizer.py    # Tokenizer 训练
│   ├── train_tokenizer_mps.py # MPS 专用训练
│   ├── train_predictor.py    # Predictor 训练
│   ├── utils/                # 工具函数
│   │   ├── __init__.py
│   │   └── training_utils.py
│   └── scripts/              # 训练脚本
│       ├── train.sh
│       └── monitor.sh
│
├── model/                      # 模型核心代码
│   ├── __init__.py
│   ├── kronos.py             # Kronos 主模型
│   ├── tokenizer.py          # Tokenizer
│   ├── predictor.py          # Predictor
│   └── modules.py            # 基础模块
│
├── scripts/                    # 实用脚本
│   ├── data/                 # 数据处理脚本
│   │   ├── fetch_akshare.py
│   │   ├── fetch_futu.py
│   │   └── preprocess.py
│   ├── training/             # 训练相关脚本
│   │   ├── start_training.sh
│   │   ├── monitor_training.sh
│   │   └── stop_training.sh
│   └── utils/                # 通用工具
│       ├── check_environment.py
│       └── validate_data.py
│
├── tests/                      # 测试代码
│   ├── __init__.py
│   ├── unit/                 # 单元测试
│   │   ├── test_model.py
│   │   ├── test_tokenizer.py
│   │   └── test_dataset.py
│   ├── integration/          # 集成测试
│   │   └── test_pipeline.py
│   ├── data/                 # 测试数据
│   └── conftest.py           # pytest 配置
│
├── webui/                      # Web 界面
│   ├── app.py
│   ├── templates/
│   ├── static/
│   └── requirements.txt
│
├── outputs/                    # 输出目录 (不提交到 git)
│   ├── models/               # 训练的模型
│   │   ├── finetuned_tokenizer/
│   │   └── finetuned_predictor/
│   ├── predictions/          # 预测结果
│   └── logs/                 # 训练日志
│
├── tools/                      # 开发工具
│   ├── lint.sh
│   ├── format.sh
│   └── check_types.sh
│
├── .gitignore                  # Git 忽略配置
├── .env.example               # 环境变量示例
├── pyproject.toml             # 项目配置 (替代 setup.py)
├── requirements.txt           # 依赖包
├── requirements-dev.txt       # 开发依赖
├── README.md                  # 项目说明
├── LICENSE                    # 许可证
└── CHANGELOG.md              # 变更日志
```

---

## 🔄 重构步骤

### 阶段 1: 创建新目录结构

```bash
# 创建主要目录
mkdir -p config/{training,inference}
mkdir -p data/{raw/akshare,processed}
mkdir -p docs/{guides,api,tutorials}
mkdir -p finetune/{utils,scripts}
mkdir -p scripts/{data,training,utils}
mkdir -p tests/{unit,integration,data}
mkdir -p outputs/{models,predictions,logs}
mkdir -p tools
mkdir -p .github/workflows
```

### 阶段 2: 移动文件

#### 2.1 移动文档

```bash
# 将所有 MD 文档移动到 docs/guides/
mv GPU_TRAINING_MPS_GUIDE.md docs/guides/mps_gpu_guide.md
mv QUICK_START_MPS.md docs/guides/quick_start_mps.md
mv TOMORROW_CONTINUE_GUIDE.md docs/guides/training_continue.md
mv TRAINING_SUMMARY_DAY1.md docs/guides/training_summary.md

# 保留根目录的重要文档
# README.md, LICENSE 保持在根目录

# 删除或归档临时文档
mkdir -p docs/archive
mv COMPLETE_SUMMARY.md docs/archive/
mv DEBUG_SETUP_GUIDE.md docs/archive/
mv FINAL_PUSH_STATUS.md docs/archive/
mv FINETUNING_IN_PROGRESS.md docs/archive/
mv GIT_COMMIT_SUMMARY.md docs/archive/
mv GPU_TRAINING_SETUP.md docs/archive/
mv GPU_TRAINING_STARTED.md docs/archive/
mv GPU_TRAINING_STATUS.md docs/archive/
mv MULTIGPU_TRAINING_GUIDE.md docs/archive/
mv PUSH_STATUS.md docs/archive/
mv PYTHON_ENV_SETUP_COMPLETE.md docs/archive/
mv SETUP_STATUS_REPORT.md docs/archive/
mv STEP*.md docs/archive/
mv TORCHRUN_*.md docs/archive/
mv TRAINING_*.md docs/archive/
```

#### 2.2 移动数据文件

```bash
# 移动 AkShare 数据
mv akshare_data/* data/raw/akshare/
rmdir akshare_data

# 移动处理后的数据
mv data/processed_datasets/* data/processed/
rmdir data/processed_datasets

# 移动 prepared_data (如果存在)
mv prepared_data/* data/processed/ 2>/dev/null || true
```

#### 2.3 移动脚本

```bash
# 移动数据获取脚本
mv tests/fetch_*.py scripts/data/
mv tests/testaka.py scripts/data/ 2>/dev/null || true
mv tests/tusharetest.py scripts/data/ 2>/dev/null || true

# 移动监控和管理脚本
mv monitor_training.sh scripts/training/
mv train_mps.sh scripts/training/start_training.sh
mv start_training_tomorrow.sh scripts/training/

# 移动测试脚本
mv test_step*.py tests/integration/
mv verify_environment.py scripts/utils/check_environment.py
mv debug_setup.py scripts/utils/
```

#### 2.4 移动配置文件

```bash
# 移动训练配置
mv finetune/config_300033_mps.yaml config/training/mps_config.yaml

# 如果有其他配置文件，也移动到 config/
```

#### 2.5 整理 finetune 目录

```bash
# 确保 finetune 有正确的结构
mv finetune/utils/ finetune/utils/  # 已存在
mkdir -p finetune/scripts
mv finetune/train_tokenizer_spawn.py finetune/
```

#### 2.6 整理 outputs

```bash
# 移动现有模型
mv outputs/models/* outputs/models/  # 已在正确位置

# 移动训练日志
mv training_output.log outputs/logs/
mv training_log.txt outputs/logs/ 2>/dev/null || true
```

#### 2.7 清理 tests 目录

```bash
# 移动测试相关文件
mv tests/data/ tests/data/  # 已存在
mv tests/*.py tests/unit/ 2>/dev/null || true

# 保留必要的测试文件在 tests/
# 移动其他到适当位置
```

### 阶段 3: 更新导入路径

需要更新以下文件中的导入路径：

1. **finetune/*.py** - 更新相对导入
2. **examples/*.py** - 更新数据路径
3. **scripts/**/*.py** - 更新项目根路径引用
4. **tests/**/*.py** - 更新测试数据路径

### 阶段 4: 更新 .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Jupyter Notebook
.ipynb_checkpoints

# Data (large files)
data/raw/
outputs/
*.pkl
*.csv

# Logs
*.log
outputs/logs/

# OS
.DS_Store
Thumbs.db

# Environment variables
.env

# Temporary files
tmp/
temp/
*.tmp
```

### 阶段 5: 创建必要的文档

```bash
# 在 data/ 目录创建 README
cat > data/README.md << 'EOF'
# 数据目录说明

## 目录结构

- `raw/`: 原始数据文件（不提交到 git）
  - `akshare/`: 从 AkShare/Futu 获取的 CSV 文件
- `processed/`: 处理后的数据文件（不提交到 git）
  - `train_data.pkl`: 训练数据
  - `val_data.pkl`: 验证数据
  - `test_data.pkl`: 测试数据

## 数据获取

运行以下脚本获取数据：

```bash
python scripts/data/fetch_akshare.py
python scripts/data/fetch_futu.py
```

## 数据预处理

```bash
python scripts/data/preprocess.py
```
EOF

# 在 docs/ 创建 README
cat > docs/README.md << 'EOF'
# Kronos 文档

## 目录

- [安装指南](guides/installation.md)
- [MPS GPU 训练](guides/mps_gpu_guide.md)
- [快速开始](guides/quick_start_mps.md)
- [训练指南](guides/training.md)
- [推理指南](guides/inference.md)

## API 文档

查看 [API 参考](api/)

## 教程

查看 [教程目录](tutorials/)
EOF
```

### 阶段 6: 创建 pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "kronos"
version = "0.1.0"
description = "Financial Time Series Foundation Model"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
dependencies = [
    "torch>=2.0.0",
    "transformers>=4.30.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "safetensors>=0.3.0",
    "huggingface-hub>=0.16.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]
data = [
    "akshare>=1.10.0",
    "futu-api>=10.0.0",
    "tushare>=1.2.0",
]
webui = [
    "flask>=2.3.0",
    "gradio>=3.0.0",
]

[tool.setuptools.packages.find]
include = ["model*", "finetune*"]

[tool.black]
line-length = 88
target-version = ['py310']

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
```

---

## ✅ 重构检查清单

### 目录结构
- [ ] 创建所有新目录
- [ ] 移动文档到 docs/
- [ ] 移动数据到 data/
- [ ] 移动脚本到 scripts/
- [ ] 整理 finetune/
- [ ] 整理 tests/
- [ ] 整理 outputs/

### 文件更新
- [ ] 更新所有导入路径
- [ ] 更新配置文件中的路径
- [ ] 更新示例代码中的数据路径
- [ ] 更新 .gitignore
- [ ] 创建必要的 README 文件

### 测试
- [ ] 测试模型加载
- [ ] 测试数据加载
- [ ] 测试训练脚本
- [ ] 测试推理脚本
- [ ] 运行单元测试

### 文档
- [ ] 更新主 README.md
- [ ] 创建 CHANGELOG.md
- [ ] 更新所有内部链接

---

## 🎯 预期收益

1. **清晰度提升**: 文件分类明确，易于查找
2. **开发效率**: 模块化结构，便于协作
3. **版本控制**: 合理的 .gitignore，避免提交大文件
4. **可维护性**: 清晰的职责划分
5. **扩展性**: 易于添加新功能模块

---

## ⚠️ 注意事项

1. **备份**: 重构前务必备份整个项目
2. **测试**: 重构后全面测试所有功能
3. **文档**: 更新所有相关文档和示例
4. **Git**: 建议在单独的分支上进行重构
5. **沟通**: 如果有团队成员，提前沟通重构计划

---

**是否开始执行重构？** 

建议先在测试环境中验证，确认无误后再应用到主项目。
