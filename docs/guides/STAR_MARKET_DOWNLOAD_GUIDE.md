# 科创板股票数据下载指南

## 📋 概述

本工具用于批量下载A股科创板（STAR Market）所有股票的历史行情数据，并保存为符合Kronos训练要求的CSV格式。

### 科创板特点
- **股票代码**: 688xxx
- **上市时间**: 2019年7月后
- **交易所**: 上海证券交易所 (SHSE)
- **涨跌幅限制**: 20%
- **数据来源**: AKShare (免费API)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install akshare pandas
```

### 2. 运行脚本

```bash
# 下载所有科创板股票（过去5年数据）
python scripts/data/batch_download_star_market.py

# 测试模式：只下载前10只股票
python scripts/data/batch_download_star_market.py
# 在代码中修改 max_stocks=10
```

---

## ⚙️ 配置说明

### 主要参数

在 `batch_download_star_market.py` 的 `main()` 函数中修改：

```python
# 批量下载（5年数据，每次请求间隔1秒）
batch_download_star_stocks(
    years=5,        # 下载年数，默认5年
    delay=1,        # 请求间隔秒数，避免API限流
    max_stocks=None # 最大下载数量，None表示全部
)
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `years` | int | 5 | 下载历史数据的年数 |
| `delay` | float | 1 | 每次API请求间隔（秒） |
| `max_stocks` | int/None | None | 最大下载数量，用于测试 |

---

## 📁 输出文件

### 1. 股票列表
**位置**: `data/metadata/star_market_stocks_list_YYYYMMDD.csv`

**内容**:
```csv
code,name
688001,华兴源创
688002,睿创微纳
688003,天准科技
...
```

### 2. Kronos格式数据
**位置**: `data/processed/kronos_SHSE_688xxx_daily_YYYY-MM-DD_YYYY-MM-DD.csv`

**格式**:
```csv
timestamps,open,close,high,low,volume,amount
2019-07-22,30.0,30.0,30.0,30.0,1000000,30000000
2019-07-23,31.5,31.2,32.0,30.8,1200000,37440000
...
```

**列说明**:
- `timestamps`: 日期
- `open`: 开盘价
- `close`: 收盘价
- `high`: 最高价
- `low`: 最低价
- `volume`: 成交量（手）
- `amount`: 成交额（元）

---

## 📊 使用示例

### 示例1: 下载全部科创板股票

```python
# 修改 main() 函数
batch_download_star_stocks(years=5, delay=1, max_stocks=None)
```

**预计时间**: 
- 科创板约500+只股票
- 每只1秒间隔
- 总计约10-15分钟

### 示例2: 测试模式（下载前10只）

```python
# 修改 main() 函数
batch_download_star_stocks(years=5, delay=1, max_stocks=10)
```

**用途**: 测试脚本是否正常工作

### 示例3: 下载更长时间数据

```python
# 下载10年数据（如果上市时间允许）
batch_download_star_stocks(years=10, delay=1, max_stocks=None)
```

### 示例4: 加快下载速度

```python
# 减少延迟（注意API限流风险）
batch_download_star_stocks(years=5, delay=0.5, max_stocks=None)
```

---

## 🔧 常见问题

### Q1: 提示找不到akshare模块？

**解决**:
```bash
pip install akshare
```

### Q2: 下载速度慢？

**解决**:
- 减小 `delay` 参数（如0.5秒）
- 但要注意API限流风险
- 建议保持1秒间隔

### Q3: 某些股票下载失败？

**原因**:
- 新股上市时间短，数据不足
- API临时故障
- 网络问题

**解决**:
- 查看错误信息
- 重新运行脚本（会跳过已下载的文件）

### Q4: 如何断点续传？

**说明**:
- 脚本会自动检测已存在的文件
- 已下载的股票会被跳过
- 可以安全中断后重新运行

### Q5: 数据量有多大？

**估算**:
- 每只股票约1000-1500条记录（5年）
- 每个CSV文件约50-100KB
- 500只股票总计约25-50MB

---

## 📈 数据质量检查

下载完成后，建议检查数据质量：

```python
import pandas as pd
import glob

# 读取一个样本文件
files = glob.glob('data/processed/kronos_SHSE_688*_daily_*.csv')
if files:
    df = pd.read_csv(files[0])
    print(f"记录数: {len(df)}")
    print(f"列名: {df.columns.tolist()}")
    print(f"时间范围: {df['timestamps'].min()} 到 {df['timestamps'].max()}")
    print(f"缺失值:\n{df.isnull().sum()}")
```

---

## 🔄 后续步骤

### 1. 验证数据格式

```bash
python scripts/data/check_data_compatibility.py
```

### 2. 转换数据（如果需要）

数据已经是Kronos格式，可以直接使用。

### 3. 开始训练

```bash
# 单股票训练
python scripts/train/test_step3_finetune.py

# 批量训练
python scripts/train/batch_train_all_banks_cn.py --gpu 0
```

---

## 💡 最佳实践

### 1. 首次运行
- 先用 `max_stocks=10` 测试
- 确认数据格式正确
- 再运行全量下载

### 2. 定期更新
- 每月运行一次更新最新数据
- 脚本会自动跳过已下载的股票

### 3. 备份数据
- 下载完成后备份 `data/processed/` 目录
- 避免重复下载

### 4. 监控进度
- 观察控制台输出
- 检查成功率
- 查看生成的文件数量

---

## 📝 注意事项

1. **API限流**: AKShare是免费API，请遵守使用规范
2. **网络稳定**: 确保网络连接稳定
3. **磁盘空间**: 预留至少100MB空间
4. **Python版本**: 建议使用Python 3.8+
5. **时区**: 数据为中国时区（UTC+8）

---

## 🔗 相关资源

- [AKShare文档](https://akshare.akfamily.xyz/)
- [Kronos项目README](../../README.md)
- [项目结构说明](../../PROJECT_STRUCTURE.md)
- [银行股下载脚本](batch_download_bank_stocks.py)

---

## 📞 问题反馈

如遇到问题，请提供：
1. 错误信息
2. Python版本
3. AKShare版本
4. 操作步骤

---

**最后更新**: 2026-04-19  
**版本**: 1.0  
**作者**: Kronos Team
