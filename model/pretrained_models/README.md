# 📦 预训练模型目录

本目录包含 Kronos 的预训练模型，用于微调和推理。

## 📂 目录结构

```
pretrained_models/
├── Kronos-base/                    # Kronos 基础模型（102M 参数）
│   ├── README.md
│   ├── config.json
│   └── model.safetensors          (390 MB)
│
└── Kronos-Tokenizer-base/         # Tokenizer 模型
    ├── README.md
    ├── config.json
    └── model.safetensors          (15 MB)
```

## 🎯 可用模型

### 1. Kronos-base

**规格**:
- **参数量**: 102,310,592 (约 1.02 亿)
- **文件大小**: 390 MB
- **格式**: SafeTensors
- **用途**: 金融时序预测基础模型

**加载方法**:
```python
from model.kronos import Kronos

# 从本地路径加载
model = Kronos.from_pretrained("./model/pretrained_models/Kronos-base")
```

### 2. Kronos-Tokenizer-base

**规格**:
- **文件大小**: 15 MB
- **格式**: SafeTensors
- **用途**: 金融时序数据 Tokenizer

**加载方法**:
```python
from model.kronos import KronosTokenizer

# 从本地路径加载
tokenizer = KronosTokenizer.from_pretrained("./model/pretrained_models/Kronos-Tokenizer-base")
```

## 💾 下载模型

### 方法 1: 使用 Hugging Face（自动下载）

```python
from huggingface_hub import snapshot_download

# 下载 Kronos-base
snapshot_download(
    repo_id="NeoQuasar/Kronos-base",
    local_dir="./model/pretrained_models/Kronos-base"
)

# 下载 Tokenizer
snapshot_download(
    repo_id="NeoQuasar/Kronos-Tokenizer-base",
    local_dir="./model/pretrained_models/Kronos-Tokenizer-base"
)
```

### 方法 2: 使用国内镜像

```bash
export HF_ENDPOINT=https://hf-mirror.com

python << 'EOF'
from huggingface_hub import snapshot_download

# 下载 Kronos-base
snapshot_download(
    repo_id="NeoQuasar/Kronos-base",
    local_dir="./model/pretrained_models/Kronos-base"
)
EOF
```

### 方法 3: 手动下载

从 Hugging Face 下载后放置到对应目录：
- Kronos-base: https://huggingface.co/NeoQuasar/Kronos-base
- Tokenizer: https://huggingface.co/NeoQuasar/Kronos-Tokenizer-base

## 🚀 使用示例

### 完整预测流程

```python
import pandas as pd
from model.kronos import Kronos, KronosTokenizer, KronosPredictor

# 1. 加载模型和 tokenizer
model = Kronos.from_pretrained("./model/pretrained_models/Kronos-base")
tokenizer = KronosTokenizer.from_pretrained("./model/pretrained_models/Kronos-Tokenizer-base")

# 2. 创建预测器
predictor = KronosPredictor(
    model=model,
    tokenizer=tokenizer,
    max_context=512
)

# 3. 加载数据
df = pd.read_csv("./data/raw/akshare/daily_300033.csv")
df['timestamps'] = pd.to_datetime(df['timestamps'])

# 4. 准备输入
lookback = 100
pred_len = 20

x_df = df.loc[:lookback-1, ['open', 'high', 'low', 'close', 'volume', 'amount']]
x_timestamp = df.loc[:lookback-1, 'timestamps']
y_timestamp = df.loc[lookback:lookback+pred_len-1, 'timestamps']

# 5. 预测
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

### 使用 MPS GPU 加速

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

## 🔄 模型更新

### 检查更新

```bash
# 查看 Hugging Face 上的最新版本
python << 'EOF'
from huggingface_hub import HfApi

api = HfApi()
model_info = api.model_info("NeoQuasar/Kronos-base")
print(f"最新 SHA: {model_info.sha}")
print(f"最后更新: {model_info.last_modified}")
EOF
```

### 重新下载

```bash
# 删除旧模型
rm -rf model/pretrained_models/Kronos-base

# 重新下载
export HF_ENDPOINT=https://hf-mirror.com
python -c "from huggingface_hub import snapshot_download; snapshot_download('NeoQuasar/Kronos-base', local_dir='./model/pretrained_models/Kronos-base')"
```

## 📊 存储空间

### 当前占用

| 模型 | 大小 |
|------|------|
| Kronos-base | 390 MB |
| Kronos-Tokenizer-base | 15 MB |
| **总计** | **405 MB** |

### 清理建议

如果不需要本地副本，可以删除并依赖 Hugging Face 缓存：

```bash
# 删除本地副本
rm -rf model/pretrained_models/

# 代码中直接使用模型 ID
model = Kronos.from_pretrained("NeoQuasar/Kronos-base")
```

## 🔗 相关资源

- **Hugging Face**: https://huggingface.co/NeoQuasar
- **Kronos GitHub**: https://github.com/shiyu-coder/Kronos
- **国内镜像**: https://hf-mirror.com

## ⚠️ 注意事项

1. **Git 忽略**: 预训练模型文件较大，已添加到 `.gitignore`
2. **存储空间**: 确保有足够的磁盘空间（建议至少 1GB）
3. **版本管理**: 记录使用的模型版本，确保可复现性
4. **备份**: 定期备份重要的微调模型

---

*最后更新: 2026年4月21日*
