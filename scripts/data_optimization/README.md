# 📊 数据优化脚本使用说明

**基于**: 方案一 - 数据层面优化  
**适配环境**: AMD EPYC 9T24 + 64GB内存 + NVIDIA RTX 5880 Ada (12GB)  
**CUDA版本**: 12.8  

---

## 📁 脚本目录结构

```
scripts/data_optimization/
├── merge_data.py              # 步骤1: 数据合并
├── validate_data.py           # 步骤2: 数据验证
├── balance_data.py            # 步骤3: 数据平衡
├── augment_data.py            # 步骤4: 数据增强
├── feature_engineering.py     # 步骤5: 特征工程
├── train_model.py             # 步骤6: 模型训练
├── run_all_steps.py           # 一键执行所有步骤
└── README.md                  # 本说明文档
```

---

## 🚀 快速开始

### 方法1: 一键执行（推荐）

```bash
# 执行所有优化步骤
python scripts/data_optimization/run_all_steps.py
```

这将自动依次执行：
1. ✅ 数据合并
2. ✅ 数据验证
3. ✅ 数据平衡
4. ✅ 数据增强
5. ✅ 特征工程
6. ✅ 模型训练

### 方法2: 分步执行

如果需要单独执行某个步骤：

```bash
# 步骤1: 合并历史数据和新数据
python scripts/data_optimization/merge_data.py

# 步骤2: 验证数据质量
python scripts/data_optimization/validate_data.py

# 步骤3: 平衡涨跌样本
python scripts/data_optimization/balance_data.py

# 步骤4: 数据增强（添加噪声）
python scripts/data_optimization/augment_data.py

# 步骤5: 特征工程（添加技术指标）
python scripts/data_optimization/feature_engineering.py

# 步骤6: 使用优化后的数据训练模型
python scripts/data_optimization/train_model.py
```

---

## 📋 详细步骤说明

### 步骤1: 数据合并 (`merge_data.py`)

**功能**: 合并历史数据和新数据，创建完整的时间序列数据集

**输入**:
- `data/raw/futu/5min_300033.csv` (历史数据)
- `data/raw/futu/5min_300033_2026-04-27_2026-04-30.csv` (新数据)

**输出**:
- `data/raw/futu/5min_300033_updated.csv` (合并后的数据)

**日志**: `logs/data_merge.log`

---

### 步骤2: 数据验证 (`validate_data.py`)

**功能**: 全面验证数据质量，包括缺失值、重复值、数值范围等

**检查项目**:
- ✅ 缺失值检测
- ✅ 重复值检测
- ✅ 数据类型验证
- ✅ 数值范围合理性
- ✅ 时间序列连续性
- ✅ 价格合理性 (high >= low, etc.)
- ✅ 收益率分布

**输出**:
- `data/validation_report.txt` (验证报告)

**日志**: `logs/data_validation.log`

---

### 步骤3: 数据平衡 (`balance_data.py`)

**功能**: 平衡涨跌样本比例，解决数据不平衡问题

**策略**:
- 如果上涨样本不足：过采样上涨样本
- 如果下跌样本过多：欠采样下跌样本
- 目标比例：50% 上涨 / 50% 下跌

**输入**:
- `data/raw/futu/5min_300033_updated.csv`

**输出**:
- `data/raw/futu/5min_300033_balanced.csv`

**日志**: `logs/data_balance.log`

---

### 步骤4: 数据增强 (`augment_data.py`)

**功能**: 通过添加高斯噪声进行数据增强，增加样本多样性

**增强方法**:
- 对价格列 (open, high, low, close) 添加高斯噪声
- 噪声水平：1% 标准差
- 自动修正价格合理性 (high >= low, etc.)

**可选增强** (代码中已注释):
- 滑动窗口增强：创建重叠样本

**输入**:
- `data/raw/futu/5min_300033_balanced.csv`

**输出**:
- `data/raw/futu/5min_300033_augmented.csv`

**日志**: `logs/data_augmentation.log`

---

### 步骤5: 特征工程 (`feature_engineering.py`)

**功能**: 添加技术指标和时间特征，丰富模型输入

**新增特征**:

#### 技术指标 (20+个)
- **移动平均线**: MA5, MA10, MA20, MA30, MA60
- **指数移动平均**: EMA12, EMA26
- **MACD**: MACD, MACD_signal, MACD_hist
- **RSI**: 相对强弱指标 (14期)
- **布林带**: BB_upper, BB_lower, BB_width
- **ATR**: 平均真实波幅 (14期)
- **成交量指标**: volume_MA5, volume_MA20, volume_ratio
- **收益率**: return_1, return_5, return_10, return_20
- **波动率**: volatility_5, volatility_20

#### 时间特征 (8个)
- hour, minute, day_of_week, day_of_month
- month, quarter, is_trading_day, time_period

**输入**:
- `data/raw/futu/5min_300033_augmented.csv`

**输出**:
- `data/raw/futu/5min_300033_with_features.csv` (包含30+个特征)

**日志**: `logs/feature_engineering.log`

---

### 步骤6: 模型训练 (`train_model.py`)

**功能**: 使用优化后的数据和CUDA配置训练模型

**配置**:
- 数据文件: `data/raw/futu/5min_300033_with_features.csv`
- 配置文件: `finetune_csv/configs/config_cuda_optimized.yaml`
- 训练脚本: `finetune_csv/train_sequential.py`

**训练参数** (来自config_cuda_optimized.yaml):
- Batch Size: 64
- Num Workers: 8 (AMD EPYC优化)
- Mixed Precision: FP16 (AMP)
- Gradient Accumulation: 2步
- Learning Rate: 2e-5

**预期性能**:
- 每epoch: ~20-40秒
- 15 epochs: ~5-10分钟
- 30 epochs: ~10-20分钟

**输出**:
- 模型保存在: `outputs/models/`
- 训练日志: `logs/training.log`

---

## 🔧 自定义配置

### 修改数据路径

在所有脚本中，可以修改以下参数：

```python
# 输入数据路径
input_path='data/raw/futu/5min_300033_updated.csv'

# 输出数据路径
output_path='data/raw/futu/5min_300033_balanced.csv'
```

### 调整噪声水平

在 `augment_data.py` 中：

```python
add_noise_to_data(
    noise_level=0.01  # 调整为 0.005 (更小) 或 0.02 (更大)
)
```

### 修改平衡比例

在 `balance_data.py` 中：

```python
balance_data(
    target_ratio=0.5  # 调整为 0.6 (60%上涨) 或其他值
)
```

### 选择不同的技术指标

在 `feature_engineering.py` 的 `calculate_technical_indicators()` 函数中添加或删除指标。

---

## 📊 数据处理流程

```
原始数据
  ↓
[步骤1] 数据合并 → 5min_300033_updated.csv
  ↓
[步骤2] 数据验证 → validation_report.txt
  ↓
[步骤3] 数据平衡 → 5min_300033_balanced.csv
  ↓
[步骤4] 数据增强 → 5min_300033_augmented.csv
  ↓
[步骤5] 特征工程 → 5min_300033_with_features.csv (30+特征)
  ↓
[步骤6] 模型训练 → outputs/models/
```

---

## ⚠️ 注意事项

### 1. 磁盘空间

确保有足够的磁盘空间：
- 原始数据: ~10 MB
- 中间文件: ~50 MB
- 总需求: ~100 MB

### 2. 内存使用

脚本针对64GB内存优化：
- 数据加载时使用pandas，高效处理
- 特征工程时会临时占用较多内存
- 如有内存压力，可减小batch size

### 3. 训练时间

基于RTX 5880 Ada的预期时间：
- 数据预处理 (步骤1-5): ~5-10分钟
- 模型训练 (步骤6): ~10-20分钟 (30 epochs)
- 总计: ~15-30分钟

### 4. 日志查看

所有步骤都会生成日志文件：
```bash
# 查看最新日志
type logs\data_merge.log
type logs\data_validation.log
type logs\data_balance.log
type logs\data_augmentation.log
type logs\feature_engineering.log
type logs\training.log
```

---

## 🐛 常见问题

### Q1: 找不到数据文件

**错误**: `文件不存在: data/raw/futu/5min_300033.csv`

**解决**:
```bash
# 检查文件是否存在
dir data\raw\futu\

# 如果文件在其他位置，修改脚本中的路径
```

### Q2: CUDA不可用

**错误**: `CUDA not available`

**解决**:
```python
# 检查CUDA状态
python -c "import torch; print(torch.cuda.is_available())"

# 确保安装了正确的PyTorch版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### Q3: 内存不足

**错误**: `MemoryError`

**解决**:
- 关闭其他应用程序
- 减小batch size (在config文件中)
- 使用更小的数据集进行测试

### Q4: 训练速度慢

**检查**:
```python
# 确认使用了GPU
python -c "import torch; print(torch.cuda.get_device_name(0))"

# 确认启用了混合精度
# 检查 config_cuda_optimized.yaml 中 use_amp: true
```

---

## 📈 预期成果

完成所有步骤后，预期获得：

1. **数据质量提升**
   - ✅ 合并了最新市场数据
   - ✅ 平衡了涨跌样本
   - ✅ 添加了噪声增强
   - ✅ 丰富了特征工程

2. **模型性能提升**
   - ✅ R² 从负值提升到正值
   - ✅ 减少系统性看空偏差
   - ✅ 提高预测准确性
   - ✅ 更好的泛化能力

3. **训练效率**
   - ✅ 充分利用AMD EPYC多核CPU
   - ✅ 充分利用RTX 5880 Ada GPU
   - ✅ 启用混合精度训练
   - ✅ 快速迭代实验

---

## 📞 技术支持

如遇到问题，请检查：
1. 日志文件 (`logs/` 目录)
2. 验证报告 (`data/validation_report.txt`)
3. 系统配置 (`SYSTEM_CONFIG.md`)
4. 实施计划 (`option1_implementation_plan.md`)

---

**最后更新**: 2026年5月1日  
**适配环境**: AMD EPYC 9T24 + 64GB + RTX 5880 Ada + CUDA 12.8
