# 浦发银行数据下载工具 - Kronos格式版

## 📋 概述

这个Python脚本使用AKShare免费API下载浦发银行(SHSE.600000)的历史行情数据，并**直接生成符合Kronos模型训练要求的CSV格式**。

## ✨ 主要特性

### 1. **自动格式转换**
- ✅ 输出格式完全符合Kronos训练要求
- ✅ 包含所有必需列：`timestamps, open, close, high, low, volume, amount`
- ✅ 文件命名规范：`kronos_SHSE_600000_daily_YYYY-MM-DD_YYYY-MM-DD.csv`

### 2. **数据质量保证**
- ✅ 自动OHLC逻辑验证
- ✅ 空值检测
- ✅ 数据完整性检查
- ✅ 前复权处理（qfq）

### 3. **智能重试机制**
- ✅ 网络失败自动重试（最多3次）
- ✅ 详细的错误提示
- ✅ 友好的用户界面

### 4. **无需Token**
- ✅ 使用AKShare免费API
- ✅ 无需注册或认证
- ✅ 开箱即用

---

## 🚀 快速开始

### 安装依赖

```bash
pip install akshare pandas
```

### 运行脚本

```bash
python tests/download_spdb_data_akshare.py
```

### 输出示例

```
================================================================================
浦发银行历史行情数据下载工具 (AKShare - Kronos格式)
================================================================================

说明:
- 使用AKShare免费API，无需注册或token
- 数据来源: 东方财富网、新浪财经等
- 输出格式: Kronos训练格式 (timestamps, open, close, high, low, volume, amount)
- 文件命名: kronos_SHSE_600000_daily_YYYY-MM-DD_YYYY-MM-DD.csv
================================================================================

================================================================================
开始下载浦发银行(600000)历史行情数据 (Kronos格式)
================================================================================

股票标的: 600000 (浦发银行)
时间范围: 2021-04-20 至 2026-04-19
数据频率: 日线数据
预计年数: 5年
目标格式: Kronos训练格式 (timestamps, open, close, high, low, volume, amount)

正在从东方财富网下载数据...
✅ 成功获取 1211 条原始记录

正在处理数据并转换为Kronos格式...
✅ 数据转换完成

Kronos格式数据概览:
  - 总记录数: 1211
  - 时间范围: 2021-04-19 00:00:00 至 2026-04-17 00:00:00
  - 列名: timestamps, open, close, high, low, volume, amount

前5条数据:
   timestamps   open  close   high    low     volume       amount
0  2021-04-19   9.85   9.90   9.95   9.82  45000000  445500000.00
1  2021-04-20   9.90   9.88   9.93   9.85  42000000  415800000.00
...

数据质量检查:
  - 空值数量: 0
  - 最高价: ¥11.25
  - 最低价: ¥8.50
  - 平均收盘价: ¥9.86
  - 总成交量: 52,345,678,900
  ✅ OHLC逻辑验证通过

正在保存Kronos格式数据到: data/kronos_SHSE_600000_daily_2021-04-19_2026-04-17.csv
✅ Kronos格式文件保存成功!
   文件大小: 64.86 KB
   文件路径: D:\workspace\Kronos\data\kronos_SHSE_600000_daily_2021-04-19_2026-04-17.csv
   验证记录数: 1211
   验证列名: timestamps, open, close, high, low, volume, amount
   ✅ 符合Kronos训练格式要求

================================================================================
✅ 数据下载完成！
================================================================================
```

---

## 📊 输出文件格式

### CSV文件结构

```csv
timestamps,open,close,high,low,volume,amount
2021-04-19,9.85,9.90,9.95,9.82,45000000,445500000.00
2021-04-20,9.90,9.88,9.93,9.85,42000000,415800000.00
...
```

### 列说明

| 列名 | 类型 | 说明 | Kronos要求 |
|------|------|------|-----------|
| `timestamps` | datetime | 交易日期 | ✅ 必需 |
| `open` | float | 开盘价 | ✅ 必需 |
| `close` | float | 收盘价 | ✅ 必需 |
| `high` | float | 最高价 | ✅ 必需 |
| `low` | float | 最低价 | ✅ 必需 |
| `volume` | int/float | 成交量 | ✅ 必需 |
| `amount` | float | 成交额 | ✅ 必需 |

---

## 🔧 自定义配置

### 修改股票代码

编辑脚本中的主函数调用：

```python
if __name__ == '__main__':
    # 下载工商银行数据
    success = download_and_convert_to_kronos_format(
        years=5,
        symbol="601398",
        stock_name="工商银行"
    )
```

### 修改时间跨度

```python
# 下载10年数据
success = download_and_convert_to_kronos_format(years=10)

# 下载3年数据
success = download_and_convert_to_kronos_format(years=3)
```

### 下载多只股票

创建批处理脚本：

```python
from download_spdb_data_akshare import download_and_convert_to_kronos_format

stocks = [
    ("600000", "浦发银行"),
    ("601398", "工商银行"),
    ("600036", "招商银行"),
]

for symbol, name in stocks:
    print(f"\n下载 {name} ({symbol})...")
    download_and_convert_to_kronos_format(years=5, symbol=symbol, stock_name=name)
```

---

## 📁 文件位置

### 输入
- 无（直接从网络获取）

### 输出
```
data/
└── kronos_SHSE_600000_daily_2021-04-19_2026-04-17.csv
```

---

## ✅ 数据验证

### 自动验证

脚本会自动验证：
1. ✅ 所有必需列存在
2. ✅ 无空值
3. ✅ OHLC逻辑正确（High >= Open,Close >= Low）
4. ✅ 时间排序正确
5. ✅ 文件格式符合Kronos要求

### 手动验证

```python
import pandas as pd

# 读取数据
df = pd.read_csv('data/kronos_SHSE_600000_daily_2021-04-19_2026-04-17.csv')

# 检查列名
print("列名:", df.columns.tolist())
# 期望输出: ['timestamps', 'open', 'close', 'high', 'low', 'volume', 'amount']

# 检查数据量
print("记录数:", len(df))
# 期望输出: ~1211 (5年交易日)

# 检查时间范围
print("时间范围:", df['timestamps'].min(), "至", df['timestamps'].max())

# 检查空值
print("空值数量:", df.isnull().sum().sum())
# 期望输出: 0

# 查看前几行
print(df.head())
```

---

## 🎯 用于Kronos训练

### 1. 直接使用

生成的CSV文件可以直接用于Kronos训练：

```yaml
# config.yaml
data:
  data_path: "data/kronos_SHSE_600000_daily_2021-04-19_2026-04-17.csv"
  lookback_window: 60
  predict_window: 10
```

### 2. 训练命令

```bash
python finetune_csv/train_sequential.py --config finetune_csv/configs/config_spdb_daily.yaml
```

### 3. 注意事项

⚠️ **数据量建议**:
- 当前: 1,211条记录（5年日线）
- 推荐: 10,000+条记录
- 改进: 收集更多股票或更长时间跨度

⚠️ **数据频率**:
- 当前: 日线数据
- Kronos优化: 5分钟K线
- 建议: 如可能，获取5分钟数据以获得更好效果

---

## ❓ 常见问题

### Q1: 网络连接失败怎么办？

**A**: 脚本已内置重试机制（最多3次）。如果仍然失败：
1. 检查网络连接
2. 稍后重试
3. 考虑使用代理

### Q2: 如何下载其他股票？

**A**: 修改`download_and_convert_to_kronos_format()`函数的参数：
```python
download_and_convert_to_kronos_format(
    years=5,
    symbol="601398",  # 工商银行
    stock_name="工商银行"
)
```

### Q3: 数据不符合Kronos格式？

**A**: 脚本会自动验证。如果看到"✅ 符合Kronos训练格式要求"，则完全兼容。

### Q4: 如何获取5分钟数据？

**A**: AKShare的5分钟数据API有限制。建议：
1. 使用掘金量化平台（需要token）
2. 或使用其他数据源

### Q5: 文件大小是多少？

**A**: 
- 5年日线数据: ~65 KB
- 10年日线数据: ~130 KB
- 非常轻量级

---

## 🔄 与旧版本对比

### 旧版本 (`download_spdb_data.py`)
```csv
symbol,name,date,open,close,high,low,volume,amount,...
SHSE.600000,浦发银行,2021-04-19,9.85,9.90,9.95,9.82,45000000,445500000,...
```
❌ 需要额外转换步骤  
❌ 包含多余列  
❌ 列名不符合Kronos要求  

### 新版本 (当前)
```csv
timestamps,open,close,high,low,volume,amount
2021-04-19,9.85,9.90,9.95,9.82,45000000,445500000
```
✅ 直接可用  
✅ 仅包含必需列  
✅ 完全符合Kronos要求  

---

## 📝 更新日志

### v2.0 (2026-04-19)
- ✅ 直接生成Kronos格式
- ✅ 自动数据验证
- ✅ 智能重试机制
- ✅ 改进的文件命名
- ✅ 删除了多余的列
- ✅ 简化了使用流程

### v1.0 (之前)
- 基础数据下载功能
- 需要手动转换为Kronos格式

---

## 💡 最佳实践

1. **定期更新数据**
   ```bash
   # 每周运行一次，保持数据最新
   python tests/download_spdb_data_akshare.py
   ```

2. **备份历史数据**
   ```bash
   # 保留多个版本
   cp data/kronos_SHSE_600000_*.csv backups/
   ```

3. **验证数据质量**
   ```python
   # 每次下载后运行验证
   python tests/check_data_compatibility.py
   ```

4. **批量下载多只股票**
   - 创建股票列表
   - 循环调用下载函数
   - 统一保存到data目录

---

## 📞 技术支持

如有问题，请检查：
1. Python版本 >= 3.8
2. akshare已正确安装
3. 网络连接正常
4. 参考项目文档

---

**最后更新**: 2026-04-19  
**版本**: v2.0  
**维护者**: Kronos Project Team
