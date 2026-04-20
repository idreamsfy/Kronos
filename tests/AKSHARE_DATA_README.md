# AkShare A 股数据获取工具

## 📊 功能说明

本脚本使用 AkShare 库从同花顺获取 A 股历史数据，并生成符合 **Kronos** 训练要求的 CSV 文件。

### 数据格式

生成的 CSV 文件包含以下列：
- `timestamps`: 时间戳 (YYYY-MM-DD)
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量
- `amount`: 成交额

### 支持的数据频率

- ✅ **daily** - 日线数据（默认）
- ✅ **weekly** - 周线数据
- ✅ **monthly** - 月线数据

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python -m pip install akshare -i https://mirrors.aliyun.com/pypi/simple/ -U
```

### 2. 运行脚本

```bash
python tests/fetch_akshare_data.py
```

### 3. 查看结果

生成的文件保存在 `./akshare_data/` 目录：

```bash
ls -lh akshare_data/
```

---

## ⚙️ 配置说明

编辑 `tests/fetch_akshare_data.py` 中的 `main()` 函数来自定义参数：

```python
# ==================== 配置参数 ====================
OUTPUT_DIR = "./akshare_data"      # 输出目录
FREQUENCY = "daily"                # 数据频率: daily, weekly, monthly
START_DATE = "20150101"           # 开始日期 (10年前)
MAX_STOCKS = 5                    # 最大处理股票数量 (None=全部)

# 示例股票列表
SAMPLE_SYMBOLS = [
    "600977",  # 中国电影
    "600000",  # 浦发银行
    "000001",  # 平安银行
    "600519",  # 贵州茅台
    "000858",  # 五粮液
]
```

---

## 📋 使用示例

### 示例 1: 获取指定股票的日线数据（过去10年）

```python
SAMPLE_SYMBOLS = ["600519", "000001", "600000"]
FREQUENCY = "daily"
START_DATE = "20150101"
MAX_STOCKS = None  # 获取所有指定股票
```

### 示例 2: 获取所有 A 股的周线数据

```python
# 取消注释 main() 函数中的方案 2
stock_list = get_stock_list()
all_symbols = stock_list['code'].tolist()
success_files = batch_fetch_stocks(
    symbols=all_symbols,
    output_dir="./akshare_weekly",
    frequency="weekly",
    start_date="20150101",
    max_stocks=None
)
```

### 示例 3: 只获取最近3年的数据

```python
START_DATE = "20220101"  # 从2022年开始
```

### 示例 4: 测试少量股票

```python
MAX_STOCKS = 3  # 只处理前3只股票
```

---

## 📁 输出文件示例

生成的 CSV 文件格式：

```csv
timestamps,open,high,low,close,volume,amount
2016-08-09,9.41,11.55,9.41,11.55,1803,2308726.0
2016-08-10,12.83,12.83,12.83,12.83,705,994952.0
2016-08-11,14.24,14.24,14.24,14.24,675,1048353.0
...
```

**文件命名规则**: `{frequency}_{symbol}.csv`

例如：
- `daily_600519.csv` - 贵州茅台日线数据
- `weekly_000001.csv` - 平安银行周线数据

---

## 🔧 高级用法

### 批量获取大量股票

```python
# 获取沪深300成分股
import akshare as ak

# 获取沪深300成分股列表
hs300 = ak.stock_hs300_constituent()
symbols = hs300['代码'].tolist()

# 批量获取
batch_fetch_stocks(
    symbols=symbols,
    output_dir="./hs300_data",
    frequency="daily",
    start_date="20150101",
    max_stocks=50  # 限制数量避免时间过长
)
```

### 自定义时间范围

```python
# 获取特定时间段的数据
START_DATE = "20200101"  # 2020年1月1日
END_DATE = "20231231"    # 2023年12月31日

# 修改 fetch_stock_data_daily 函数调用
df = fetch_stock_data_daily(symbol, START_DATE, END_DATE)
```

### 添加错误重试机制

```python
def fetch_with_retry(symbol, max_retries=3):
    for attempt in range(max_retries):
        try:
            df = fetch_stock_data_daily(symbol)
            if df is not None:
                return df
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)
    return None
```

---

## ⚠️ 注意事项

### 1. 请求频率限制

AkShare 基于网络爬虫，频繁请求可能被封禁 IP。建议：

```python
# 在 batch_fetch_stocks 中已添加延迟
time.sleep(0.5)  # 每只股票间隔0.5秒

# 如需更保守的设置
time.sleep(1.0)  # 间隔1秒
```

### 2. 数据完整性

- 新股可能没有10年数据
- 停牌期间无交易数据
- 建议使用前复权 (`adjust="qfq"`) 保证价格连续性

### 3. 存储空间

全量 A 股（约5000只）的10年日线数据：
- 每只股票约 100-200 KB
- 总计约 500 MB - 1 GB

### 4. 执行时间

- 单只股票：~1-2 秒
- 100 只股票：~2-3 分钟
- 全量 A 股：~2-3 小时

---

## 🐛 常见问题

### Q1: 提示 "No module named 'akshare'"

**解决**:
```bash
pip install akshare
```

### Q2: 某些股票获取失败

**原因**: 
- 股票代码不存在
- 网络问题
- 数据源暂时不可用

**解决**:
```python
# 检查失败的股票列表
if failed_stocks:
    print(f"失败的股票: {failed_stocks}")
    # 可以重新运行获取失败的股票
    batch_fetch_stocks(failed_stocks, ...)
```

### Q3: 数据量太少

**原因**: 
- 新股上市时间短
- 开始日期设置太晚

**解决**:
```python
# 调整开始日期
START_DATE = "20100101"  # 更早的日期
```

### Q4: 如何获取实时数据？

AkShare 主要提供历史数据，实时数据需要使用其他接口：

```python
# 获取实时行情
realtime = ak.stock_zh_a_spot_em()
print(realtime.head())
```

---

## 📊 数据验证

获取数据后，建议验证数据质量：

```python
import pandas as pd

# 读取数据
df = pd.read_csv("./akshare_data/daily_600519.csv")

# 基本统计
print(df.describe())

# 检查缺失值
print(df.isnull().sum())

# 检查时间范围
print(f"数据范围: {df['timestamps'].min()} 至 {df['timestamps'].max()}")
print(f"总记录数: {len(df)}")

# 可视化
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 6))
plt.plot(pd.to_datetime(df['timestamps']), df['close'])
plt.title('Stock Price History')
plt.xlabel('Date')
plt.ylabel('Price')
plt.savefig('price_chart.png')
plt.show()
```

---

## 🎯 与 Kronos 集成

生成的数据可以直接用于 Kronos 模型：

```python
from model import Kronos, KronosTokenizer, KronosPredictor
import pandas as pd

# 加载数据
df = pd.read_csv("./akshare_data/daily_600519.csv")
df['timestamps'] = pd.to_datetime(df['timestamps'])

# 准备预测输入
lookback = 100
pred_len = 20

x_df = df.loc[:lookback-1, ['open', 'high', 'low', 'close', 'volume', 'amount']]
x_timestamp = df.loc[:lookback-1, 'timestamps']
y_timestamp = df.loc[lookback:lookback+pred_len-1, 'timestamps']

# 使用 Kronos 进行预测
tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
model = Kronos.from_pretrained("NeoQuasar/Kronos-small")
predictor = KronosPredictor(model, tokenizer, max_context=512)

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

## 📝 更新日志

- **2026-04-19**: 初始版本
  - ✅ 支持日线、周线、月线数据
  - ✅ 批量获取多只股票
  - ✅ 自动创建输出目录
  - ✅ 详细的进度显示和错误处理

---

## 🤝 贡献

如有问题或建议，请提交 Issue 或 Pull Request。

---

## 📄 许可证

本项目遵循 Kronos 项目的许可证。

---

**祝使用愉快！** 🎉
