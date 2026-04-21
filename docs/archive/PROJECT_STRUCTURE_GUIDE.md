# 📁 Kronos 项目结构快速参考

**重构完成**: 2026年4月20日  

---

## 🗺️ 目录导航

### 📝 文档 (docs/)

```bash
# 使用指南
docs/guides/mps_gpu_guide.md          # MPS GPU 训练
docs/guides/quick_start_mps.md        # 快速开始
docs/guides/training_continue.md      # 继续训练
docs/guides/training_summary.md       # 训练总结

# 归档文档（历史）
docs/archive/                         # 临时文档和状态报告
```

### 💾 数据 (data/)

```bash
# 原始数据（CSV）
data/raw/akshare/daily_300033.csv    # 同花顺数据
data/raw/akshare/daily_000001.csv    # 平安银行
...

# 处理后数据（Pickle）
data/processed/train_data.pkl        # 训练集
data/processed/val_data.pkl          # 验证集
data/processed/test_data.pkl         # 测试集
```

### 🔧 脚本 (scripts/)

```bash
# 数据获取
scripts/data/fetch_futu.py           # Futu API 获取
scripts/data/fetch_akshare.py        # AkShare 获取
scripts/data/preprocess.py           # 数据预处理

# 训练管理
scripts/training/start_training.sh   # 启动训练
scripts/training/monitor.sh          # 监控进度
scripts/training/start_tomorrow.sh   # 明日启动

# 工具
scripts/utils/check_environment.py   # 环境检查
scripts/utils/debug_setup.py         # 调试设置
```

### ⚙️ 配置 (config/)

```bash
# 训练配置
config/training/mps_config.yaml      # MPS 训练配置

# 推理配置
config/inference/                    # （待添加）
```

### 🧪 测试 (tests/)

```bash
# 单元测试
tests/unit/                          # （待添加）

# 集成测试
tests/integration/test_step1*.py     # 模型加载测试
tests/integration/test_step2*.py     # 数据准备测试
tests/integration/test_step3*.py     # 训练测试

# 测试数据
tests/data/                          # 测试数据集
```

### 📦 输出 (outputs/)

```bash
# 模型文件
outputs/models/finetune_tokenizer_300033_mps/best_model/

# 预测结果
outputs/predictions/                 # （待使用）

# 训练日志
outputs/logs/training_output.log     # 最新训练日志
```

---

## 🚀 常用命令

### 启动训练

```bash
# 方法 1: 使用脚本
./scripts/training/start_training.sh

# 方法 2: 直接运行
source .venv/bin/activate
python finetune/train_tokenizer_mps.py
```

### 监控训练

```bash
# 实时监控
./scripts/training/monitor.sh

# 查看日志
tail -f outputs/logs/training_output.log
```

### 数据操作

```bash
# 获取新数据
python scripts/data/fetch_futu.py

# 预处理数据
python scripts/data/preprocess.py

# 查看数据
ls -lh data/raw/akshare/
ls -lh data/processed/
```

### 环境检查

```bash
# 检查环境
python scripts/utils/check_environment.py

# 检查 MPS
python -c "import torch; print(torch.backends.mps.is_available())"
```

---

## 📂 核心模块

### model/ - 模型核心

```
model/
├── kronos.py          # Kronos 主模型
├── tokenizer.py       # Tokenizer
├── predictor.py       # Predictor
└── modules.py         # 基础模块
```

### finetune/ - 微调模块

```
finetune/
├── train_tokenizer_mps.py    # MPS 训练脚本
├── dataset.py                # 数据集处理
├── config.py                 # 配置管理
├── utils/                    # 工具函数
└── scripts/                  # 训练脚本
```

### examples/ - 示例代码

```
examples/
├── prediction_example.py
├── prediction_batch_example.py
└── data/                     # 示例数据
```

---

## 🔍 快速查找

### 想找...

**训练相关**:
- 训练脚本 → `finetune/train_tokenizer_mps.py`
- 配置文件 → `config/training/mps_config.yaml`
- 启动脚本 → `scripts/training/start_training.sh`
- 监控脚本 → `scripts/training/monitor.sh`

**数据相关**:
- 原始数据 → `data/raw/akshare/`
- 处理数据 → `data/processed/`
- 获取脚本 → `scripts/data/fetch_*.py`
- 预处理 → `scripts/data/preprocess.py`

**文档相关**:
- 使用指南 → `docs/guides/`
- 快速开始 → `docs/guides/quick_start_mps.md`
- GPU 训练 → `docs/guides/mps_gpu_guide.md`
- 归档文档 → `docs/archive/`

**测试相关**:
- 单元测试 → `tests/unit/`
- 集成测试 → `tests/integration/`
- 测试数据 → `tests/data/`

**输出相关**:
- 模型文件 → `outputs/models/`
- 训练日志 → `outputs/logs/`
- 预测结果 → `outputs/predictions/`

---

## 📋 文件类型索引

### Python 文件

```
核心代码:
- model/*.py              # 模型实现
- finetune/*.py           # 微调实现

脚本:
- scripts/**/*.py         # 实用脚本
- tests/**/*.py           # 测试代码
- examples/*.py           # 示例代码
```

### Shell 脚本

```
- scripts/training/*.sh   # 训练管理
- tools/*.sh             # 开发工具（待添加）
```

### 配置文件

```
- config/**/*.yaml       # YAML 配置
- requirements.txt       # Python 依赖
- .gitignore            # Git 忽略规则
```

### 文档文件

```
- README.md              # 项目说明
- docs/**/*.md          # 详细文档
- data/README.md        # 数据说明
```

---

## 💡 最佳实践

### 1. 添加新数据

```bash
# 1. 放置原始 CSV
cp your_data.csv data/raw/akshare/

# 2. 运行预处理
python scripts/data/preprocess.py

# 3. 验证数据
ls -lh data/processed/
```

### 2. 开始新训练

```bash
# 1. 检查环境
python scripts/utils/check_environment.py

# 2. 启动训练
./scripts/training/start_training.sh

# 3. 监控进度
./scripts/training/monitor.sh
```

### 3. 添加新功能

```bash
# 1. 在适当目录创建
model/new_feature.py     # 新功能模块

# 2. 添加测试
tests/unit/test_new_feature.py

# 3. 更新文档
docs/guides/new_feature.md
```

### 4. 提交代码

```bash
# 1. 检查状态
git status

# 2. 添加变更
git add <files>

# 3. 提交
git commit -m "描述变更"

# 注意: data/ 和 outputs/ 中的大文件会自动忽略
```

---

## ⚠️ 注意事项

### Git 忽略

以下目录/文件**不会**提交到 git：
- `data/raw/` - 原始数据
- `data/processed/*.pkl` - 处理后的数据
- `outputs/` - 所有输出
- `docs/archive/` - 归档文档
- `.venv/` - 虚拟环境

### 路径引用

在代码中使用相对路径时，注意当前工作目录：

```python
# 推荐：使用绝对路径
import os
project_root = os.path.dirname(os.path.dirname(__file__))
data_path = os.path.join(project_root, 'data', 'processed')

# 或者从项目根目录运行
cd /Users/john/Documents/GitHub/Kronos
python finetune/train_tokenizer_mps.py
```

### 备份建议

定期备份重要数据：
```bash
# 备份模型
cp -r outputs/models/ /backup/models_$(date +%Y%m%d)

# 备份数据
cp -r data/processed/ /backup/data_$(date +%Y%m%d)
```

---

## 🔗 相关链接

- [项目主 README](../README.md)
- [数据说明](../data/README.md)
- [文档索引](../docs/README.md)
- [重构方案](../REFACTORING_PLAN.md)
- [重构报告](../REFACTORING_COMPLETE.md)

---

**最后更新**: 2026年4月20日  
**版本**: v1.0
