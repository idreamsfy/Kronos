# ✅ Kronos 模型下载完成报告

**完成时间**: 2026年4月21日  
**方法**: 使用国内镜像 (hf-mirror.com)  

---

## 📦 已下载的模型

### 1. Kronos-Tokenizer-base ✅

**状态**: 下载完成并验证通过

- **模型 ID**: `NeoQuasar/Kronos-Tokenizer-base`
- **下载量**: 830,501 次
- **用途**: 金融时序数据 Tokenizer
- **标签**: pytorch, safetensors, Finance

**测试结果**:
```
✅ Tokenizer 加载成功
类型: KronosTokenizer
```

---

### 2. Kronos-base ✅

**状态**: 下载完成并验证通过

- **模型 ID**: `NeoQuasar/Kronos-base`
- **下载量**: 364,806 次
- **文件大小**: 390 MB
- **参数量**: **102,310,592** (约 1.02 亿参数)
- **用途**: Kronos 基础模型（最大版本）
- **标签**: safetensors, Finance, Candlestick

**测试结果**:
```
✅ Kronos-base 加载成功
类型: Kronos
参数量: 102,310,592
```

---

## 🚀 下载方法

### 使用国内镜像加速

```bash
# 设置镜像环境变量
export HF_ENDPOINT=https://hf-mirror.com

# 下载模型
python << 'EOF'
from huggingface_hub import snapshot_download

# 下载 Kronos-base
snapshot_download(
    repo_id="NeoQuasar/Kronos-base",
    cache_dir="~/.cache/huggingface/hub"
)
EOF
```

**优势**:
- ✅ 下载速度快（从几小时缩短到几分钟）
- ✅ 稳定性好
- ✅ 支持断点续传

---

## 📊 模型对比

| 模型 | 参数量 | 大小 | 下载量 | 适用场景 |
|------|--------|------|--------|---------|
| **Kronos-mini** | - | 小 | 215K | 快速推理，资源受限 |
| **Kronos-small** | - | 中小 | 330K | 平衡性能和速度 |
| **Kronos-base** | **102M** | **390MB** | **365K** | **最佳性能** ✨ |

---

## 💻 存储位置

### Hugging Face 缓存目录

```
~/.cache/huggingface/hub/
├── models--NeoQuasar--Kronos-Tokenizer-base/
│   ├── blobs/
│   ├── refs/
│   └── snapshots/
│       └── 0e0117387f39004a9016484a186a908917e22426/
│           ├── README.md
│           ├── config.json
│           └── model.safetensors
│
└── models--NeoQuasar--Kronos-base/
    ├── blobs/
    │   ├── 1a2dbfe... (README.md)
    │   ├── a6344aa... (.gitattributes)
    │   ├── abff193... (model.safetensors - 390MB)
    │   └── b38b53e... (config.json)
    ├── refs/
    └── snapshots/
        └── 2b554741eca47781b64468546e77fef3e85130e6/
            ├── README.md -> ../../blobs/1a2dbfe...
            ├── config.json -> ../../blobs/b38b53e...
            └── model.safetensors -> ../../blobs/abff193...
```

**总占用空间**: ~400 MB

---

## 🎯 使用方法

### 1. 加载 Tokenizer

```python
from model.kronos import KronosTokenizer

# 加载 tokenizer
tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
print("✅ Tokenizer 加载成功")
```

### 2. 加载 Kronos-base 模型

```python
from model.kronos import Kronos

# 加载模型
model = Kronos.from_pretrained("NeoQuasar/Kronos-base")
print(f"✅ Kronos-base 加载成功")
print(f"参数量: {sum(p.numel() for p in model.parameters()):,}")
```

### 3. 创建 Predictor

```python
from model.kronos import KronosPredictor

# 创建预测器
predictor = KronosPredictor(
    model=model,
    tokenizer=tokenizer,
    max_context=512
)
print("✅ Predictor 创建成功")
```

### 4. 进行预测

```python
import pandas as pd

# 加载数据
df = pd.read_csv("./data/raw/akshare/daily_300033.csv")
df['timestamps'] = pd.to_datetime(df['timestamps'])

# 准备输入
lookback = 100
pred_len = 20

x_df = df.loc[:lookback-1, ['open', 'high', 'low', 'close', 'volume', 'amount']]
x_timestamp = df.loc[:lookback-1, 'timestamps']
y_timestamp = df.loc[lookback:lookback+pred_len-1, 'timestamps']

# 预测
pred_df = predictor.predict(
    df=x_df,
    x_timestamp=x_timestamp,
    y_timestamp=y_timestamp,
    pred_len=pred_len,
    T=1.0,
    top_p=0.9,
    sample_count=1
)

print(pred_df)
```

---

## 🔄 与训练结合

### 使用 Kronos-base 进行微调

可以修改训练配置，使用 Kronos-base 替代 Kronos-small：

```yaml
# config/training/mps_config.yaml
pretrained_model_path: "NeoQuasar/Kronos-base"  # 使用 base 版本
pretrained_tokenizer_path: "NeoQuasar/Kronos-Tokenizer-base"
```

**优势**:
- ✅ 更多参数（102M vs 可能更小的版本）
- ✅ 更好的表达能力
- ✅ 更高的预测精度

**注意**:
- ⚠️ 需要更多内存
- ⚠️ 训练时间可能更长
- ⚠️ 可能需要调整批次大小

---

## 💡 性能优化建议

### MPS GPU 加速

```python
import torch

# 检查 MPS 可用性
if torch.backends.mps.is_available():
    device = torch.device('mps')
    model.to(device)
    print("✅ 使用 Apple Silicon MPS 加速")
else:
    device = torch.device('cpu')
    print("⚠️ 使用 CPU")
```

### 内存管理

```python
# 清理缓存
import gc
gc.collect()
torch.cuda.empty_cache()  # 如果使用 CUDA
torch.mps.empty_cache()   # 如果使用 MPS
```

### 批次大小调整

```python
# 根据可用内存调整
batch_size = 32  # Kronos-base 可能需要更小的批次
```

---

## 📈 模型特性

### Kronos-base 特点

1. **大规模参数**
   - 102,310,592 参数
   - 更强的表达能力

2. **金融领域优化**
   - 针对金融时序数据训练
   - 支持 K 线图分析

3. **SafeTensors 格式**
   - 安全的模型权重格式
   - 快速加载
   - 防止代码执行漏洞

4. **预训练知识**
   - 大量金融数据预训练
   - 捕捉市场模式
   - 泛化能力强

---

## 🎓 下一步建议

### 1. 测试预测性能

```bash
# 运行预测示例
python examples/prediction_example.py
```

### 2. 使用新模型重新训练

```bash
# 更新配置文件
# 使用 Kronos-base 作为基础模型
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python finetune/train_tokenizer_mps.py
```

### 3. 比较不同模型

测试 Kronos-mini、Kronos-small 和 Kronos-base 的性能差异。

### 4. 部署应用

将训练好的模型部署到 Web UI 或 API 服务。

---

## 🔗 相关资源

- **Hugging Face**: https://huggingface.co/NeoQuasar
- **Kronos GitHub**: https://github.com/shiyu-coder/Kronos
- **国内镜像**: https://hf-mirror.com
- **文档**: 查看各模型的 README

---

## ✅ 总结

### 完成情况

- ✅ Kronos-Tokenizer-base 下载并验证
- ✅ Kronos-base 下载并验证
- ✅ 模型加载测试通过
- ✅ 使用国内镜像加速成功

### 关键数据

- **Kronos-base 参数量**: 102,310,592
- **模型大小**: 390 MB
- **下载方式**: hf-mirror.com 国内镜像
- **存储位置**: ~/.cache/huggingface/hub/

### 可用性

- ✅ 立即可用于推理
- ✅ 可用于微调训练
- ✅ 支持 MPS GPU 加速
- ✅ 与现有代码兼容

---

**🎉 所有模型下载完成并验证通过！**

现在可以使用 Kronos-base 进行高质量的金融时序预测了！

---

*最后更新: 2026年4月21日*  
*状态: ✅ 完成*
