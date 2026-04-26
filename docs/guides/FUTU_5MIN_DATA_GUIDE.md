# 📊 Futu API 获取5分钟K线数据使用指南

**更新日期**: 2026年4月21日  
**适用**: 同花顺 (300033) 5分钟高频数据获取  

---

## 🎯 功能说明

本脚本使用 Futu API（富途牛牛）获取同花顺 (300033) 最近3年的5分钟K线数据，并转换为 Kronos 训练格式。

### 主要特性

- ✅ 获取最近3年5分钟K线数据
- ✅ 自动分页下载大量数据
- ✅ 前复权处理
- ✅ 数据质量检查
- ✅ 符合 Kronos 训练格式要求
- ✅ 详细的进度提示和统计信息

---

## 📋 前置要求

### 1. 安装 FutuOpenD

**下载地址**: https://www.futunn.com/download/openAPI

**安装步骤**:
1. 下载对应操作系统的 FutuOpenD
2. 安装并启动程序
3. 使用富途牛牛账号登录
4. 确保监听端口为 `11111`（默认）

### 2. 安装 Python 依赖

```bash
pip install futu-api pandas
```

### 3. 验证连接

```python
from futu import *

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
print("连接成功！")
quote_ctx.close()
```

---

## 🚀 使用方法

### 基本用法

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python scripts/data/fetch_300033_futu.py
```

### 输出示例

```
======================================================================
使用 Futu API（富途牛牛）获取股票 300033（同花顺）5分钟K线数据
======================================================================

配置信息:
  - 股票代码: SZ.300033
  - K线类型: 5分钟
  - 时间范围: 2023-04-21 至 2026-04-21
  - 输出文件: ./data/raw/futu/5min_300033.csv

初始化 Futu API 客户端...
✅ 客户端初始化成功

正在获取5分钟K线数据...
⚠️  提示: 5分钟数据量较大，请耐心等待...

已获取 1,000 条，继续获取更多...
已获取 2,000 条，继续获取更多...
...
已获取 36,000 条，继续获取更多...

总共获取 36,245 条5分钟K线记录

转换数据格式...

✅ 数据已成功保存至: ./data/raw/futu/5min_5min_300033.csv

数据统计:
  - 记录数: 36,245 条
  - 时间范围: 2023-04-21 09:35:00 至 2026-04-21 15:00:00
  - 交易日数: 约 755 天
  - 收盘价范围: ¥45.23 - ¥285.67
  - 成交量范围: 12,345 - 8,901,234
  - 成交额范围: ¥567,890 - ¥234,567,890

数据质量检查:
  - 缺失值: 0
  - OHLC 逻辑: ✅ 通过
  - 平均时间间隔: 5.0 分钟
  - 时间间隔: ✅ 正常 (5分钟)

======================================================================
✅ 完成！数据符合 Kronos 训练要求
✅ 已获取 36,245 条5分钟K线数据，可用于高频交易模型训练
======================================================================
```

---

## 📁 输出文件

### 文件位置

```
./data/raw/futu/5min_300033.csv
```

### 文件格式

```csv
timestamps,open,high,low,close,volume,amount
2023-04-21 09:35:00,52.30,52.50,52.20,52.40,123456,6456789.00
2023-04-21 09:40:00,52.40,52.60,52.35,52.55,234567,12345678.00
...
```

### 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| **timestamps** | 时间戳 | 2023-04-21 09:35:00 |
| **open** | 开盘价 | 52.30 |
| **high** | 最高价 | 52.50 |
| **low** | 最低价 | 52.20 |
| **close** | 收盘价 | 52.40 |
| **volume** | 成交量 | 123456 |
| **amount** | 成交额 | 6456789.00 |

---

## ⚙️ 配置参数

### 修改时间范围

编辑脚本中的以下行：

```python
# 最近3年
start_date = (datetime.now() - timedelta(days=365*3)).strftime("%Y-%m-%d")

# 改为最近1年
start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

# 改为最近5年
start_date = (datetime.now() - timedelta(days=365*5)).strftime("%Y-%m-%d")
```

### 修改K线类型

```python
# 5分钟K线（默认）
kline_type = KLType.K_5M

# 其他可选类型
kline_type = KLType.K_1M   # 1分钟
kline_type = KLType.K_15M  # 15分钟
kline_type = KLType.K_30M  # 30分钟
kline_type = KLType.K_60M  # 60分钟
kline_type = KLType.K_DAY  # 日线
```

### 修改数据上限

```python
# 默认50,000条
max_records = 50000

# 增加上限
max_records = 100000

# 减少上限
max_records = 20000
```

---

## 📊 数据量估算

### 不同时间跨度的数据量

| 时间跨度 | 交易日 | 5分钟K线数 | 文件大小 |
|---------|--------|-----------|---------|
| **1个月** | ~22天 | ~1,056条 | ~100KB |
| **3个月** | ~65天 | ~3,120条 | ~300KB |
| **6个月** | ~130天 | ~6,240条 | ~600KB |
| **1年** | ~250天 | ~12,000条 | ~1.2MB |
| **3年** | ~750天 | ~36,000条 | ~3.5MB |
| **5年** | ~1,250天 | ~60,000条 | ~6MB |

> 注: 每天约48个5分钟K线（交易时间4小时）

---

## 🔧 常见问题

### Q1: 连接失败怎么办？

**错误**: `ConnectionRefusedError: 无法连接到 FutuOpenD`

**解决**:
1. 确认 FutuOpenD 已启动
2. 检查端口是否为 11111
3. 确认防火墙未阻止连接
4. 重启 FutuOpenD

```bash
# 检查 FutuOpenD 是否运行
ps aux | grep FutuOpenD

# 检查端口监听
lsof -i :11111
```

---

### Q2: 数据获取很慢？

**原因**: 5分钟数据量大，需要多次分页请求

**优化**:
1. 减少时间范围（如改为1年）
2. 使用更快的网络
3. 耐心等待（3年数据约需5-10分钟）

---

### Q3: 数据不完整？

**可能原因**:
1. 停牌期间无数据（正常）
2. 非交易时间段无数据（正常）
3. API 限制导致中断

**检查**:
```python
# 查看数据时间范围
df['timestamps'].min()
df['timestamps'].max()

# 检查缺失日期
import pandas as pd
all_dates = pd.date_range(start=df['timestamps'].min(), 
                          end=df['timestamps'].max(), 
                          freq='B')  # 工作日
missing_dates = all_dates[~all_dates.isin(df['timestamps'].dt.date)]
print(f"缺失日期: {len(missing_dates)} 天")
```

---

### Q4: 如何获取其他股票？

**修改股票代码**:

```python
# 同花顺
stock_code = "SZ.300033"

# 贵州茅台
stock_code = "SH.600519"

# 腾讯控股
stock_code = "HK.00700"

# 苹果
stock_code = "US.AAPL"
```

---

### Q5: 数据格式不符合 Kronos 要求？

**检查清单**:
- ✅ 包含所有必需列: timestamps, open, high, low, close, volume, amount
- ✅ 时间格式正确: YYYY-MM-DD HH:MM:SS
- ✅ 无缺失值
- ✅ OHLC 逻辑正确 (high >= low, high >= open/close, low <= open/close)

**修复脚本**:

```python
import pandas as pd

df = pd.read_csv('./data/raw/futu/5min_300033.csv')
df['timestamps'] = pd.to_datetime(df['timestamps'])
df = df.sort_values('timestamps').reset_index(drop=True)
df.to_csv('./data/raw/futu/5min_300033_fixed.csv', index=False)
```

---

## 📈 数据应用场景

### 1. 高频交易模型训练

5分钟K线适合训练：
- 短期价格预测模型
- 日内交易策略
- 波动率预测
- 量价关系分析

### 2. Kronos 模型微调

```python
from model import Kronos, KronosTokenizer, KronosPredictor
import pandas as pd

# 加载5分钟数据
df = pd.read_csv('./data/raw/futu/5min_300033.csv')
df['timestamps'] = pd.to_datetime(df['timestamps'])

# 准备训练数据
lookback = 100  # 使用100个5分钟（约8小时）
pred_len = 20   # 预测20个5分钟（约1.5小时）

x_df = df.loc[:lookback-1, ['open', 'high', 'low', 'close', 'volume', 'amount']]
x_timestamp = df.loc[:lookback-1, 'timestamps']
y_timestamp = df.loc[lookback:lookback+pred_len-1, 'timestamps']

# 进行预测
predictor = KronosPredictor(model, tokenizer, device='mps')
pred_df = predictor.predict(
    df=x_df,
    x_timestamp=x_timestamp,
    y_timestamp=y_timestamp,
    pred_len=pred_len,
    T=1.0,
    top_p=0.9
)
```

### 3. 技术分析

```python
import matplotlib.pyplot as plt

# 绘制K线图
df['timestamps'] = pd.to_datetime(df['timestamps'])
recent = df.tail(100)  # 最近100个5分钟

plt.figure(figsize=(14, 7))
plt.plot(recent['timestamps'], recent['close'], label='Close')
plt.fill_between(recent['timestamps'], recent['low'], recent['high'], alpha=0.3)
plt.title('300033 5-Minute K-Line Chart')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.show()
```

---

## 🎯 最佳实践

### 1. 定期更新数据

```bash
# 创建定时任务（每天收盘后更新）
crontab -e

# 添加以下内容（每个交易日15:30执行）
30 15 * * 1-5 cd /path/to/Kronos && python scripts/data/fetch_300033_futu.py
```

### 2. 数据备份

```bash
# 备份到云存储
cp ./data/raw/futu/5min_300033.csv ~/Backup/StockData/

# 或使用 Git LFS
git lfs track "*.csv"
git add data/raw/futu/5min_300033.csv
git commit -m "Update 5min data"
```

### 3. 数据验证

```python
# 验证数据完整性
def validate_data(filepath):
    df = pd.read_csv(filepath)
    
    checks = {
        '记录数': len(df),
        '缺失值': df.isnull().sum().sum(),
        '时间范围': f"{df['timestamps'].min()} to {df['timestamps'].max()}",
        '价格异常': ((df['high'] < df['low']).sum()),
    }
    
    for key, value in checks.items():
        print(f"{key}: {value}")
    
    return len(df) > 1000 and df.isnull().sum().sum() == 0

validate_data('./data/raw/futu/5min_300033.csv')
```

---

## 🔗 相关资源

- **Futu API 文档**: https://openapi.futunn.com/futu-api-doc/
- **Kronos 项目**: https://github.com/shiyu-coder/Kronos
- **富途牛牛官网**: https://www.futunn.com/

---

## 📝 版本历史

### v2.0 (2026-04-21)
- ✅ 支持5分钟K线数据获取
- ✅ 优化分页下载逻辑
- ✅ 增加数据质量检查
- ✅ 改进输出信息显示
- ✅ 调整数据存储路径

### v1.0 (之前)
- 仅支持日线数据
- 10年时间范围
- 基础功能

---

**祝您使用愉快！** 🎉

---

*最后更新: 2026年4月21日*  
*作者: Kronos Team*
