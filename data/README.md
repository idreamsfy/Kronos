# 数据目录说明

## 📂 目录结构

```
data/
├── raw/                    # 原始数据文件（不提交到 git）
│   └── akshare/           # 从 AkShare/Futu 获取的 CSV 文件
│       ├── daily_300033.csv
│       ├── daily_000001.csv
│       └── ...
├── processed/             # 处理后的数据文件（不提交到 git）
│   ├── train_data.pkl    # 训练数据
│   ├── val_data.pkl      # 验证数据
│   └── test_data.pkl     # 测试数据
└── README.md             # 本文档
```

## 📥 数据获取

### 方法 1: 使用 Futu API（推荐）

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python scripts/data/fetch_futu.py
```

**要求**: 
- 已安装并启动 FutuOpenD
- 配置好 Futu API

### 方法 2: 使用 AkShare

```bash
python scripts/data/fetch_akshare.py
```

**注意**: AkShare 可能受网络限制影响

## 🔄 数据预处理

将原始 CSV 数据转换为 Kronos 训练所需的 pickle 格式：

```bash
python scripts/data/preprocess.py
```

这将生成：
- `data/processed/train_data.pkl`
- `data/processed/val_data.pkl`
- `data/processed/test_data.pkl`

## 📊 数据格式

### 原始数据 (CSV)

```csv
timestamps,open,high,low,close,volume,amount
2016-04-21,38.82,39.62,37.48,37.62,13942230,728270344.6
...
```

### 处理后数据 (Pickle)

Python dict 格式，键为股票代码，值为 DataFrame。

## ⚠️ 注意事项

1. **大文件不提交**: `data/raw/` 和 `data/processed/` 中的所有文件都在 `.gitignore` 中
2. **数据备份**: 建议定期备份重要的数据文件
3. **存储空间**: 确保有足够的磁盘空间（建议至少 10GB）

## 🔗 相关文档

- [MPS GPU 训练指南](../docs/guides/mps_gpu_guide.md)
- [快速开始](../docs/guides/quick_start_mps.md)
