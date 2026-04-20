# PyTorch GPU版本安装指南

## ⚠️ 问题诊断

### 发现的问题
当前安装的PyTorch是**CPU版本**，不支持GPU加速：

```bash
$ python -c "import torch; print(torch.__version__)"
2.11.0+cpu  # ← CPU版本

$ python -c "import torch; print(torch.cuda.is_available())"
False  # ← CUDA不可用
```

### 影响
- ❌ 训练速度极慢（比GPU慢5-10倍）
- ❌ 无法利用RTX 2080 Ti的强大性能
- ❌ 训练时间从10分钟增加到65分钟

---

## ✅ 解决方案

### 步骤1: 卸载CPU版本
```bash
pip uninstall torch torchvision torchaudio -y
```

### 步骤2: 安装CUDA版本
```bash
# CUDA 11.8版本（推荐，兼容性好）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 步骤3: 验证安装
```bash
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('Version:', torch.__version__)"
```

预期输出：
```
CUDA: True
Version: 2.7.1+cu118
```

---

## 📊 版本选择

### CUDA版本对应关系

| CUDA Toolkit | PyTorch Index URL | 推荐度 |
|-------------|-------------------|--------|
| CUDA 11.8 | `https://download.pytorch.org/whl/cu118` | ⭐⭐⭐⭐⭐ 推荐 |
| CUDA 12.1 | `https://download.pytorch.org/whl/cu121` | ⭐⭐⭐⭐ |
| CPU Only | `https://download.pytorch.org/whl/cpu` | ❌ 不推荐 |

### 您的系统
- **GPU**: NVIDIA RTX 2080 Ti
- **CUDA Driver**: 13.2
- **推荐**: CUDA 11.8（向后兼容，稳定性好）

---

## 🔍 验证步骤

### 1. 检查CUDA可用性
```python
import torch

print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("CUDA version:", torch.version.cuda)
    print("GPU name:", torch.cuda.get_device_name(0))
    print("GPU memory:", torch.cuda.get_device_properties(0).total_memory / 1024**3, "GB")
```

### 2. 简单GPU测试
```python
import torch

# 创建tensor并移到GPU
x = torch.randn(1000, 1000).cuda()
y = torch.randn(1000, 1000).cuda()

# GPU计算
z = torch.mm(x, y)

print("GPU computation successful!")
print("Result shape:", z.shape)
```

### 3. 检查nvidia-smi
```bash
nvidia-smi
```

运行训练时应该看到Python进程占用GPU显存。

---

## 💡 常见问题

### Q1: 下载速度慢怎么办？

**使用国内镜像源**:
```bash
# 清华大学镜像
pip install torch torchvision torchaudio \
  --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
  --extra-index-url https://download.pytorch.org/whl/cu118
```

### Q2: 安装失败怎么办？

**清理缓存后重试**:
```bash
pip cache purge
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --no-cache-dir
```

### Q3: 如何确认使用了正确的版本？

```bash
# 查看已安装的包
pip list | findstr torch

# 应该看到类似：
# torch                    2.7.1+cu118
# torchaudio               2.7.1+cu118
# torchvision              0.22.1+cu118
```

### Q4: CUDA版本不匹配怎么办？

PyTorch的CUDA版本与系统CUDA驱动是**向后兼容**的：
- PyTorch cu118 可以在 CUDA 13.2驱动上运行 ✅
- 不需要降级系统CUDA驱动

---

## 🚀 安装完成后

### 重新运行训练
```bash
python finetune_csv/train_sequential.py --config finetune_csv/configs/config_icbc_daily.yaml
```

### 预期输出
```
Using device: cuda:0 (rank=0, world_size=1, local_rank=0)

✅ CUDA Available: Yes
   GPU: NVIDIA GeForce RTX 2080 Ti
   Memory Allocated: XXX MB
```

### 性能提升
- **Tokenizer训练**: 53秒 → 8-10秒 (**5-6x加速**)
- **Predictor训练**: 517秒 → 60-80秒 (**6-8x加速**)
- **总训练时间**: 65分钟 → 10-12分钟 (**~6x加速**)

---

## 📝 注意事项

### 1. 磁盘空间
- PyTorch CUDA版本约 **2.8 GB**
- 确保有足够的磁盘空间

### 2. 下载时间
- 取决于网络速度
- 通常需要5-15分钟

### 3. 虚拟环境
- 确保在正确的虚拟环境中安装
- 激活环境: `.venv\Scripts\activate`

### 4. 兼容性
- Python 3.11 ✅
- Windows ✅
- RTX 2080 Ti ✅

---

## 🔄 回滚方案

如果CUDA版本有问题，可以回滚到CPU版本：

```bash
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio
```

但**强烈建议使用GPU版本**以获得更好的性能。

---

## 📞 技术支持

如果遇到问题：
1. 检查Python版本: `python --version`
2. 检查CUDA驱动: `nvidia-smi`
3. 查看PyTorch官方文档: https://pytorch.org/get-started/locally/
4. 检查GitHub issues: https://github.com/pytorch/pytorch/issues

---

**最后更新**: 2026-04-19 12:51  
**状态**: 🔄 正在安装PyTorch CUDA版本  
**预计完成**: 5-15分钟（取决于网速）
