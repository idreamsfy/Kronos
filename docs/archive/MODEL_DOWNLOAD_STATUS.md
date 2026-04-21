# 📦 Kronos 模型下载状态报告

**时间**: 2026年4月21日  
**目标**: 下载 Kronos-Tokenizer-base 和 Kronos-base 模型  

---

## ✅ 已完成的下载

### 1. Kronos-Tokenizer-base

**状态**: ✅ **下载完成**

- **模型 ID**: `NeoQuasar/Kronos-Tokenizer-base`
- **下载量**: 830,501 次
- **路径**: `/Users/john/.cache/huggingface/hub/models--NeoQuasar--Kronos-Tokenizer-base/snapshots/0e0117387f39004a9016484a186a908917e22426`
- **文件大小**: ~10 KB（配置文件）+ 模型权重
- **标签**: pytorch, safetensors, Finance

**用途**: 
- Tokenizer 用于将金融时序数据转换为模型可理解的表示
- 已在之前的训练中使用

---

## ⏳ 正在下载

### 2. Kronos-base

**状态**: 🔄 **下载中**

- **模型 ID**: `NeoQuasar/Kronos-base`
- **下载量**: 364,806 次
- **预计大小**: ~409 MB
- **标签**: safetensors, Finance, Candlestick

**当前进度**: 
- 文件 3/4 已下载
- 主模型文件 (~409MB) 正在下载
- 速度较慢，需要耐心等待

**用途**:
- Kronos 基础模型（可能是最大版本）
- 可用于金融时序预测
- 支持 K 线图分析

---

## ❌ 不存在的模型

### Kronos-large

**状态**: ❌ **不存在**

在 Hugging Face 上没有找到 `NeoQuasar/Kronos-large`。

**可用的 Kronos 模型**:
1. ✅ `NeoQuasar/Kronos-mini` (215,592 次下载)
2. ✅ `NeoQuasar/Kronos-small` (330,218 次下载)
3. ✅ `NeoQuasar/Kronos-base` (364,806 次下载) - **最大版本**
4. ✅ `NeoQuasar/Kronos-Tokenizer-base` (830,501 次下载)
5. ✅ `NeoQuasar/Kronos-Tokenizer-2k` (103,474 次下载)

---

## 📊 可用模型对比

| 模型 | 大小 | 下载量 | 用途 |
|------|------|--------|------|
| **Kronos-mini** | 小 | 215K | 快速推理，资源受限场景 |
| **Kronos-small** | 中小 | 330K | 平衡性能和速度 |
| **Kronos-base** | 大 | 365K | 最佳性能（当前下载中）|
| **Kronos-Tokenizer-base** | - | 831K | Tokenizer（已下载）|
| **Kronos-Tokenizer-2k** | - | 103K | 支持更长序列的 Tokenizer |

---

## 💡 加速下载建议

### 方法 1: 使用镜像源

```bash
# 设置 Hugging Face 镜像
export HF_ENDPOINT=https://hf-mirror.com

# 重新下载
python -c "from huggingface_hub import snapshot_download; snapshot_download('NeoQuasar/Kronos-base')"
```

### 方法 2: 使用 aria2 多线程下载

```bash
# 安装 aria2
brew install aria2

# 手动下载模型文件
# 从 https://huggingface.co/NeoQuasar/Kronos-base/tree/main 获取文件链接
```

### 方法 3: 等待后台下载完成

当前下载已在后台进行，可以：
1. 继续其他工作
2. 定期检查进度
3. 下载会自动完成

---

## 🔍 检查下载进度

### 查看缓存目录

```bash
# 查看 Kronos-base 下载进度
ls -lh ~/.cache/huggingface/hub/models--NeoQuasar--Kronos-base/

# 查看临时文件
du -sh ~/.cache/huggingface/hub/models--NeoQuasar--Kronos-base/blobs/
```

### Python 检查

```python
from huggingface_hub import snapshot_download
import os

# 检查是否已缓存
cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
model_path = os.path.join(cache_dir, "models--NeoQuasar--Kronos-base")

if os.path.exists(model_path):
    print("✅ 模型已缓存")
    # 计算大小
    import subprocess
    result = subprocess.run(['du', '-sh', model_path], capture_output=True, text=True)
    print(f"大小: {result.stdout.strip()}")
else:
    print("❌ 模型未下载")
```

---

## 📝 使用已下载的模型

### Kronos-Tokenizer-base（已就绪）

```python
from model.kronos import KronosTokenizer

# 加载 tokenizer
tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
print("✅ Tokenizer 加载成功")
```

### Kronos-base（下载完成后）

```python
from model.kronos import Kronos

# 加载模型
model = Kronos.from_pretrained("NeoQuasar/Kronos-base")
print("✅ Kronos-base 加载成功")

# 进行预测
# ... 添加预测代码
```

---

## 🎯 下一步行动

### 立即可做

1. **等待 Kronos-base 下载完成**
   - 当前在后台运行
   - 可能需要较长时间（取决于网络速度）

2. **检查下载状态**
   ```bash
   ls -lh ~/.cache/huggingface/hub/models--NeoQuasar--Kronos-base/
   ```

### 下载完成后

3. **测试模型加载**
   ```python
   from model.kronos import Kronos
   model = Kronos.from_pretrained("NeoQuasar/Kronos-base")
   ```

4. **更新训练配置**
   - 可以使用 Kronos-base 替代 Kronos-small
   - 可能获得更好的预测性能

---

## 💾 存储空间

### 当前占用

- **Kronos-Tokenizer-base**: ~100 MB（估计）
- **Kronos-base**: ~500 MB（下载中）
- **总计**: ~600 MB

### 建议

确保有足够的磁盘空间：
```bash
df -h /
# 建议至少 2GB 可用空间
```

---

## 🔗 相关资源

- **Hugging Face**: https://huggingface.co/NeoQuasar
- **Kronos GitHub**: https://github.com/shiyu-coder/Kronos
- **模型文档**: 查看各模型的 README

---

**状态**: ⏳ Kronos-base 下载中，请耐心等待...

*最后更新: 2026年4月21日*
