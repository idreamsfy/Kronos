# 📊 Kronos MPS 训练状态报告

**检查时间**: 2026年4月19日 22:15  
**目标**: 使用 Apple Silicon MPS GPU 训练同花顺 (300033) 数据  

---

## ✅ 已完成配置

### 1. GPU 支持
- ✅ **MPS 可用**: Apple Silicon GPU 加速已启用
- ✅ **PyTorch 版本**: 2.10.0
- ✅ **设备检测**: `torch.backends.mps.is_available()` = True

### 2. 数据准备
- ✅ **训练数据**: `data/processed_datasets/train_data.pkl` (21 MB)
- ✅ **验证数据**: `data/processed_datasets/val_data.pkl` (202 KB)
- ✅ **测试数据**: `data/processed_datasets/test_data.pkl` (202 KB)
- ✅ **Futu 数据**: `akshare_data/daily_300033.csv` (2,425条记录)

### 3. 配置文件
- ✅ `finetune/config_300033_mps.yaml` - MPS 专用配置
- ✅ `finetune/config.py` - 主配置文件

### 4. 训练脚本
- ✅ `finetune/train_tokenizer_mps.py` - MPS 优化脚本
- ✅ `train_mps.sh` - 一键启动脚本

### 5. 预训练模型
- ✅ **Tokenizer**: `~/.cache/huggingface/hub/models--NeoQuasar--Kronos-Tokenizer-base/` (已缓存)

---

## ⚠️ 当前问题

### 问题描述

训练脚本在启动时似乎卡在模型加载阶段，没有显示任何输出或错误信息。

### 可能原因

1. **模型加载缓慢**
   - 从 HuggingFace 加载模型可能需要时间
   - 首次加载需要初始化 MPS 后端

2. **数据集路径问题**
   - 需要从 Kronos 根目录运行
   - 相对路径 `./data/processed_datasets/` 必须正确

3. **内存不足**
   - MPS 需要足够的统一内存
   - 其他应用可能占用了大量内存

4. **脚本输出缓冲**
   - Python 输出可能被缓冲
   - 使用 `tee` 可能导致延迟显示

---

## 🔍 诊断步骤

### 1. 检查 MPS 状态

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python -c "import torch; print(f'MPS: {torch.backends.mps.is_available()}')"
```

**结果**: ✅ MPS 可用

### 2. 检查数据文件

```bash
ls -lh data/processed_datasets/
```

**结果**: ✅ 所有 pickle 文件存在

### 3. 检查模型缓存

```bash
ls ~/.cache/huggingface/hub/models--NeoQuasar--Kronos-Tokenizer-base/
```

**结果**: ✅ 模型已缓存

### 4. 测试数据加载

```bash
cd /Users/john/Documents/GitHub/Kronos
python -c "from finetune.dataset import QlibDataset; ds = QlibDataset('train'); print(len(ds))"
```

**结果**: ❌ 路径错误（需要从根目录运行）

---

## 💡 解决方案

### 方案 1: 重新运行并耐心等待

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python finetune/train_tokenizer_mps.py
```

**建议**: 等待至少 5-10 分钟，首次运行可能需要下载依赖和初始化 MPS。

### 方案 2: 使用无缓冲输出

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
PYTHONUNBUFFERED=1 python finetune/train_tokenizer_mps.py
```

### 方案 3: 减小批次大小

编辑 `finetune/config_300033_mps.yaml`:

```yaml
batch_size: 32  # 从 50 改为 32
```

### 方案 4: 检查系统资源

```bash
# 检查内存使用
top -o mem

# 检查 GPU 使用情况
sudo powermetrics --samplers gpu_power -i 1000
```

---

## 📋 下一步行动

### 立即尝试

1. **使用无缓冲模式运行**:
   ```bash
   cd /Users/john/Documents/GitHub/Kronos
   source .venv/bin/activate
   PYTHONUNBUFFERED=1 python finetune/train_tokenizer_mps.py
   ```

2. **监控进程**:
   ```bash
   # 在另一个终端窗口
   top | grep python
   ```

3. **查看日志**:
   ```bash
   tail -f training_log.txt
   ```

### 如果仍然卡住

1. **检查是否有错误文件生成**:
   ```bash
   ls -lh outputs/models/finetune_tokenizer_300033_mps/
   ```

2. **尝试简化测试**:
   ```python
   import torch
   from model.kronos import KronosTokenizer
   
   device = torch.device('mps')
   print("加载模型...")
   model = KronosTokenizer.from_pretrained('NeoQuasar/Kronos-Tokenizer-base')
   model.to(device)
   print("✅ 模型加载成功！")
   ```

3. **查看详细错误**:
   ```bash
   python -u finetune/train_tokenizer_mps.py 2>&1 | tee debug.log
   ```

---

## 🎯 预期行为

正常运行时应该看到：

```
======================================================================
Kronos Tokenizer 微调 - Apple Silicon MPS (GPU)
======================================================================
✅ MPS 可用
PyTorch 版本: 2.10.0
设备: Apple Silicon MPS

加载配置文件: /Users/john/Documents/GitHub/Kronos/finetune/config_300033_mps.yaml
使用设备: mps

加载预训练 tokenizer: NeoQuasar/Kronos-Tokenizer-base
✅ 模型加载成功

开始在设备上训练: mps
加载数据集...
[TRAIN] Pre-computing sample indices...
[TRAIN] Found 612379 possible samples. Using 100000 per epoch.
[VAL] Pre-computing sample indices...
[VAL] Found XXXX possible samples. Using XXXX per epoch.
训练集大小: 100000, 验证集大小: XXXX

开始训练，共 30 个 epoch
批次大小: 50
学习率: 0.0002
总步数: XXXX
======================================================================

Epoch [1/30] Step [10/XXXX] Loss: X.XXXXXX LR: 0.000200
...
```

---

## 📞 需要帮助？

如果问题持续存在，请提供：

1. **完整错误信息**（如果有）
2. **系统信息**:
   ```bash
   uname -a
   python --version
   python -c "import torch; print(torch.__version__)"
   ```
3. **内存使用情况**:
   ```bash
   vm_stat
   ```
4. **训练脚本输出**（使用 `PYTHONUNBUFFERED=1`）

---

**最后更新**: 2026年4月19日 22:15  
**状态**: ⏳ 等待进一步诊断
