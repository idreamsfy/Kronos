# 🛠️ Kronos 调试环境配置指南

本指南将帮助您完整配置 Kronos 金融基础模型的调试环境。

## 📋 前提条件

- **Python 版本**: Python 3.10 或更高版本
- **GPU** (可选但推荐): CUDA 兼容的 GPU，用于更快的训练/推理
- **网络连接**: 需要从 Hugging Face Hub 下载模型
- **磁盘空间**: 约 2-5 GB，用于存储依赖和模型

## ✅ 已完成配置

### 1. 依赖安装 ✓

所有必需的依赖已安装：
- ✅ numpy
- ✅ pandas
- ✅ torch >= 2.0.0
- ✅ einops
- ✅ huggingface_hub
- ✅ matplotlib
- ✅ tqdm
- ✅ safetensors

### 2. VS Code 调试配置 ✓

已创建 `.vscode/launch.json`，包含以下调试配置：

| 配置名称 | 用途 |
|---------|------|
| 🐛 Debug Setup Script | 调试环境测试脚本 |
| 📈 Run Prediction Example | 运行预测示例代码 |
| 📊 Run Batch Prediction | 运行批量预测示例 |
| 🔍 Debug Model Loading | 调试模型加载过程 |
| 🌐 WebUI App (Flask) | 运行 Web 界面应用 |
| 🔧 Finetune Tokenizer | 微调 Tokenizer 模型 |
| 🎯 Finetune Predictor | 微调 Predictor 模型 |
| 🧪 Run Tests | 运行回归测试 |

### 3. Python 设置配置 ✓

已创建 `.vscode/settings.json`，包含：
- Python 路径自动检测
- 代码格式化设置
- Linting 配置
- 测试框架配置

## 🚀 快速开始

### 步骤 1: 验证环境配置

运行调试设置脚本验证所有组件是否正常工作：

```powershell
# 在项目根目录执行
python debug_setup.py
```

该脚本将：
1. ✅ 检查所有包的安装情况
2. ✅ 测试从 Hugging Face 加载模型
3. ✅ 运行简单的预测测试
4. ✅ 提供详细的错误信息（如果有问题）

### 步骤 2: 使用 VS Code 调试

#### 方法 1: 使用预配置的启动配置

1. 在 VS Code 中打开项目
2. 按 `F5` 或进入 "运行和调试"
3. 选择要运行的配置（例如："🐛 Debug Setup Script"）
4. 点击绿色运行按钮

#### 方法 2: 手动设置断点调试

1. 打开任意 Python 文件（如 `examples/prediction_example.py`）
2. 在代码行号左侧单击，设置断点（红色圆点）
3. 按 `F5` 开始调试
4. 使用调试控制：
   - `F10`: 单步跳过（不进入函数）
   - `F11`: 单步进入（进入函数内部）
   - `Shift+F11`: 单步跳出
   - `Shift+F5`: 停止调试

### 步骤 3: 运行示例代码

#### 示例 1: 单次预测

```powershell
# 在 VS Code 中选择 "📈 Run Prediction Example" 配置
# 或直接运行
python examples/prediction_example.py
```

#### 示例 2: 批量预测

```powershell
python examples/prediction_batch_example.py
```

#### 示例 3: Web 界面

```powershell
# 选择 "🌐 WebUI App (Flask)" 配置
python webui/app.py
```

然后在浏览器中访问显示的 URL（通常是 http://127.0.0.1:7860）

## 🔍 调试技巧

### 技巧 1: 检查模型加载

创建测试脚本 `test_model.py`：

```python
from model import Kronos, KronosTokenizer
import torch

# 加载模型
tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
model = Kronos.from_pretrained("NeoQuasar/Kronos-small")

# 设置断点检查模型结构
print(model)
print(f"Device: {next(model.parameters()).device}")
```

### 技巧 2: 检查数据预处理

在 `debug_setup.py` 的 `test_prediction()` 函数中设置断点，观察：
- DataFrame 结构
- 时间戳格式
- OHLCV 数据归一化过程

### 技巧 3: 调试微调流程

1. 首先安装 Qlib: `pip install pyqlib`
2. 配置 `finetune/config.py` 中的路径
3. 使用调试配置：
   - "🔧 Finetune Tokenizer"
   - "🎯 Finetune Predictor"

## 🐛 常见问题解决

### 问题 1: Hugging Face 认证错误

**症状**: 无法下载模型，出现 401 错误

**解决方案**:
```bash
# 登录 Hugging Face
huggingface-cli login
```

或使用环境变量：
```powershell
$env:HUGGING_FACE_HUB_TOKEN="your_token_here"
```

### 问题 2: CUDA/GPU 问题

**症状**: 运行时提示 CUDA 不可用

**检查 GPU 状态**:
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"GPU count: {torch.cuda.device_count()}")
```

**强制使用 CPU**:
```python
predictor = KronosPredictor(model, tokenizer, max_context=512, device='cpu')
```

### 问题 3: 内存不足

**解决方案**:
1. 减小 `lookback` 参数
2. 减小 `pred_len` 参数
3. 使用较小的模型（Kronos-small 而非 Kronos-base）
4. 减小 `sample_count`

### 问题 4: 导入错误

**症状**: `ModuleNotFoundError: No module named 'model'`

**解决方案**:
确保在项目根目录运行，或设置 PYTHONPATH：
```powershell
$env:PYTHONPATH="d:\GitHub\Kronos"
```

## 📝 下一步建议

1. **熟悉 API**: 运行 `examples/prediction_example.py` 查看基本用法
2. **实验不同参数**: 调整 temperature (T), top_p, sample_count
3. **尝试批量预测**: 使用 `prediction_batch_example.py` 处理多个时间序列
4. **微调模型**: 参考 `finetune/` 目录下的脚本进行迁移学习
5. **Web 界面**: 启动 `webui/app.py` 体验图形界面

## 📖 代码结构说明

```
Kronos/
├── model/                  # 核心模型代码
│   ├── kronos.py          # 主要模型实现
│   ├── module.py          # 模型模块
│   └── __init__.py        # 导出接口
├── examples/              # 示例脚本
│   ├── prediction_example.py
│   └── prediction_batch_example.py
├── finetune/              # 微调脚本
│   ├── train_tokenizer.py
│   ├── train_predictor.py
│   └── config.py
├── webui/                 # Web 界面
│   ├── app.py
│   └── templates/
├── tests/                 # 测试用例
├── debug_setup.py         # 环境测试脚本 ⭐
└── .vscode/               # VS Code 配置 ⭐
    ├── launch.json        # 调试配置
    └── settings.json      # 编辑器设置
```

## 🎯 调试配置文件说明

### launch.json 配置项

每个配置包含：
- `name`: 显示名称
- `type`: 调试器类型 (debugpy)
- `request`: 启动方式 (launch)
- `program/module`: 要运行的脚本
- `cwd`: 工作目录
- `env`: 环境变量
- `justMyCode`: 是否只调试用户代码（false 可以调试库代码）

### 使用建议

- **初学者**: 从 "🐛 Debug Setup Script" 开始
- **开发功能**: 使用 "📈 Run Prediction Example"
- **性能调优**: 使用 "🎯 Finetune Predictor"
- **测试验证**: 使用 "🧪 Run Tests"

## ✨ 成功标志

当您看到以下输出时，说明环境配置成功：

```
✅ Debug environment setup complete!

💡 Next steps:
   1. Run examples/prediction_example.py for full demo
   2. Run examples/prediction_batch_example.py for batch prediction
   3. Check finetune/ directory for fine-tuning scripts
   4. Run webui/app.py for web interface
```

## 📞 需要帮助？

如果遇到问题：
1. 检查 `debug_setup.py` 的错误输出
2. 查看 VS Code 终端输出
3. 确认所有依赖已正确安装
4. 检查网络连接（需要访问 Hugging Face）

---

**祝您使用愉快！** 🚀
