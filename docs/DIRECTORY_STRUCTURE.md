# 📁 项目目录结构说明

**更新日期**: 2026年4月21日  
**版本**: v2.0 (重构后)  

---

## 🎯 快速导航

### 核心模块

| 目录 | 说明 | 主要文件 |
|------|------|---------|
| **model/** | 模型核心代码 | kronos.py, module.py |
| **finetune/** | 微调与预测 | predict_ths_300033.py |
| **webui/** | Web 界面 | app.py, start.sh |
| **scripts/** | 工具脚本 | training/, data/ |
| **examples/** | 示例代码 | prediction_example.py |

### 数据与输出

| 目录 | 说明 | 内容 |
|------|------|------|
| **data/** | 数据文件 | raw/, processed/ |
| **outputs/** | 输出结果 | models/, predictions/, logs/ |
| **config/** | 配置文件 | ths_300033_config.py |

### 文档

| 目录 | 说明 | 内容 |
|------|------|------|
| **docs/** | 项目文档 | guides/, api/ |
| **docs/archive/** | 归档文档 | 历史报告、指南 |
| **figures/** | 图表图片 | logo, examples |

---

## 📂 详细结构

```
Kronos/
│
├── 📄 核心文件
│   ├── README.md                  # 项目说明
│   ├── requirements.txt           # Python 依赖
│   └── LICENSE                    # 开源许可证
│
├── 🤖 模型模块 (model/)
│   ├── kronos.py                  # Kronos 主模型
│   ├── module.py                  # 模型组件
│   └── pretrained_models/         # 预训练模型
│       ├── Kronos-base/           # 基础模型 (102M)
│       └── Kronos-Tokenizer-base/ # Tokenizer
│
├── 🔧 微调模块 (finetune/)
│   ├── predict_ths_300033.py     # ⭐ 预测脚本
│   ├── compare_predictions.py    # ⭐ 对比分析
│   ├── finetune_ths_real.py      # ⭐ 真正微调
│   ├── finetune_ths_simple.py    # 简单预测
│   ├── preprocess_ths_data.py    # 数据预处理
│   ├── train_predictor.py        # 预测器训练
│   ├── train_tokenizer.py        # Tokenizer 训练
│   └── utils/                    # 工具函数
│
├── 🌐 Web 界面 (webui/)
│   ├── app.py                     # Flask 应用
│   ├── start.sh                   # 启动脚本
│   ├── templates/index.html       # 前端页面
│   └── DEPLOYMENT_GUIDE.md        # 部署指南
│
├── 🛠️ 工具脚本 (scripts/)
│   ├── data/                      # 数据获取
│   │   ├── fetch_akshare_data.py
│   │   └── fetch_300033_*.py
│   ├── training/                  # 训练管理
│   │   ├── start_training.sh
│   │   ├── start_finetune_*.sh
│   │   └── monitor*.sh
│   └── utils/                     # 实用工具
│       ├── check_environment.py
│       └── debug_setup.py
│
├── 📊 数据管理 (data/)
│   ├── raw/                       # 原始数据
│   │   └── akshare/daily_300033.csv
│   ├── processed/                 # 处理后数据
│   │   ├── train_data.pkl
│   │   ├── val_data.pkl
│   │   └── test_data.pkl
│   └── README.md                  # 数据说明
│
├── 📤 输出文件 (outputs/)
│   ├── models/                    # 训练模型
│   │   ├── finetune_300033_base_real/
│   │   └── finetune_tokenizer_*/
│   ├── predictions/               # 预测结果
│   │   ├── ths_300033_*.csv
│   │   └── comparison_*.csv
│   └── logs/                      # 训练日志
│       └── *.log
│
├── ⚙️ 配置管理 (config/)
│   ├── ths_300033_config.py      # 同花顺配置
│   └── training/
│       └── mps_config.yaml        # MPS 训练配置
│
├── 📚 文档中心 (docs/)
│   ├── guides/                    # 使用指南
│   │   └── mps_gpu_guide.md
│   ├── api/                       # API 文档
│   ├── archive/                   # 归档文档 (57个)
│   └── REFACTORING_COMPLETE_REPORT.md
│
├── 💡 示例代码 (examples/)
│   ├── prediction_example.py
│   ├── prediction_batch_example.py
│   ├── use_local_model.py
│   └── data/                      # 示例数据
│
├── 🧪 测试套件 (tests/)
│   ├── test_kronos_regression.py
│   ├── test_finutned_tokenizer.py
│   ├── integration/               # 集成测试
│   └── data/                      # 测试数据
│
└── 🖼️ 图表资源 (figures/)
    ├── logo.png
    ├── overview.png
    └── prediction_example.png
```

---

## 🚀 常用操作

### 1. 预测股票行情

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python finetune/predict_ths_300033.py
```

### 2. 启动 Web UI

```bash
./webui/start.sh
# 访问 http://localhost:8080
```

### 3. 开始微调训练

```bash
./scripts/training/start_finetune_ths_real.sh
```

### 4. 查看训练进度

```bash
./scripts/training/monitor_finetune.sh
```

### 5. 获取最新数据

```bash
python scripts/data/fetch_akshare_data.py
```

---

## 📋 文件分类

### 应该提交到 Git

- ✅ 源代码 (.py)
- ✅ 配置文件 (.yaml, .py)
- ✅ 文档 (.md)
- ✅ 脚本 (.sh)
- ✅ 示例代码

### 不应提交到 Git

- ❌ 大型模型文件 (*.safetensors, *.bin)
- ❌ 训练输出 (outputs/models/*)
- ❌ 预测结果 (outputs/predictions/*)
- ❌ 原始数据 (data/raw/*)
- ❌ 日志文件 (*.log)
- ❌ 归档文档 (docs/archive/*)
- ❌ Python 缓存 (__pycache__/)
- ❌ 虚拟环境 (.venv/)

---

## 🔍 查找文件

### 想找模型代码？
→ `model/kronos.py`

### 想找预测脚本？
→ `finetune/predict_ths_300033.py`

### 想找训练脚本？
→ `scripts/training/`

### 想找历史文档？
→ `docs/archive/`

### 想找配置信息？
→ `config/`

### 想找预测结果？
→ `outputs/predictions/`

---

## 📝 维护建议

### 定期清理

1. **清理旧预测**
   ```bash
   # 保留最近 10 个预测文件
   ls -t outputs/predictions/*.csv | tail -n +11 | xargs rm
   ```

2. **清理日志**
   ```bash
   # 删除超过 30 天的日志
   find outputs/logs/ -name "*.log" -mtime +30 -delete
   ```

3. **归档文档**
   ```bash
   # 将临时文档移到 archive
   mv *_TEMP.md docs/archive/
   ```

### 添加新功能

1. **新脚本** → 放到 `scripts/` 对应子目录
2. **新模型** → 放到 `model/` 
3. **新示例** → 放到 `examples/`
4. **新文档** → 放到 `docs/guides/`

---

## ⚠️ 注意事项

### 路径引用

在代码中使用相对路径或配置：

```python
# ✅ 推荐
import os
project_root = os.path.dirname(os.path.dirname(__file__))
model_path = os.path.join(project_root, "model", "pretrained_models")

# ❌ 避免
model_path = "./model/pretrained_models"
```

### 大文件处理

- 模型文件 (>100MB) 不提交到 Git
- 使用 HuggingFace Hub 或本地路径
- 数据文件使用 .gitignore 忽略

### 文档管理

- 核心文档放在根目录或 docs/
- 临时文档直接放到 docs/archive/
- 定期清理归档文档

---

## 🎯 下一步

1. **阅读主文档**: [README.md](../README.md)
2. **查看指南**: [docs/guides/](guides/)
3. **运行示例**: [examples/](../examples/)
4. **开始微调**: [finetune/](../finetune/)

---

*最后更新: 2026年4月21日*  
*版本: v2.0 (重构后)*
