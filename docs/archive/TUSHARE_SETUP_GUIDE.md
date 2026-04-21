# 📊 使用 Tushare 获取股票 300033 数据指南

## 🎯 目标

获取股票 **300033（东方财富）** 过去10年的历史数据，并保存为符合 Kronos 训练要求的 CSV 格式。

---

## 📋 前置准备

### 1. 获取 Tushare Token

1. 访问 Tushare Pro: https://tushare.pro/
2. 注册账号并登录
3. 进入"个人中心" -> "接口TOKEN"
4. 复制您的 Token（类似：`xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）

### 2. 安装依赖

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python -m pip install tushare -i https://mirrors.aliyun.com/pypi/simple/ -U
```

---

## ⚙️ 配置步骤

### 步骤 1: 编辑脚本

打开文件 `tests/fetch_300033_tushare.py`

### 步骤 2: 设置 Token

找到第 **23** 行：

```python
TUSHARE_TOKEN = "YOUR_TUSHARE_TOKEN_HERE"  # <-- 请替换为您的实际 Token
```

将 `"YOUR_TUSHARE_TOKEN_HERE"` 替换为您的实际 Token，例如：

```python
TUSHARE_TOKEN = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"  # 示例 Token
```

### 步骤 3: 保存文件

保存修改后的文件。

---

## 🚀 运行脚本

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python tests/fetch_300033_tushare.py
```

---

## 📁 输出结果

成功执行后，会在 `./akshare_data/` 目录生成：

```
akshare_data/daily_300033.csv
```

### 文件格式

```csv
timestamps,open,high,low,close,volume,amount
2016-01-04,15.23,15.89,15.12,15.67,1234567,19345678.90
2016-01-05,15.70,16.12,15.55,15.98,1345678,21456789.01
...
```

### 数据说明

| 列名 | 说明 | 示例 |
|------|------|------|
| timestamps | 交易日期 | 2016-01-04 |
| open | 开盘价 | 15.23 |
| high | 最高价 | 15.89 |
| low | 最低价 | 15.12 |
| close | 收盘价 | 15.67 |
| volume | 成交量（手） | 1234567 |
| amount | 成交额（元） | 19345678.90 |

---

## ✅ 验证数据

运行验证脚本：

```bash
python tests/validate_akshare_data.py
```

或直接查看文件：

```bash
head -10 akshare_data/daily_300033.csv
wc -l akshare_data/daily_300033.csv
```

---

## 🔧 常见问题

### Q1: 提示 "请先在脚本中设置 TUSHARE_TOKEN"

**解决**: 
- 确保已将 `YOUR_TUSHARE_TOKEN_HERE` 替换为实际 Token
- 检查是否有空格或引号错误

### Q2: 提示 "未获取到数据，请检查 Token 是否正确"

**可能原因**:
- Token 无效或已过期
- 积分不足（某些接口需要积分）
- 网络连接问题

**解决**:
1. 重新登录 Tushare 获取新 Token
2. 检查账户积分是否足够
3. 检查网络连接

### Q3: 获取的数据不完整

**原因**: 
- Tushare 免费版有调用次数限制
- 某些历史数据可能缺失

**解决**:
- 升级 Tushare 会员获取更多权限
- 分多次获取不同时间段的数据

### Q4: 网络连接超时

**解决**:
```bash
# 检查网络
ping api.tushare.pro

# 稍后重试
sleep 60
python tests/fetch_300033_tushare.py
```

---

## 📊 数据使用

### 在 Kronos 中使用

```python
from model import Kronos, KronosTokenizer, KronosPredictor
import pandas as pd

# 加载数据
df = pd.read_csv("./akshare_data/daily_300033.csv")
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

## 💡 高级用法

### 获取其他股票

修改脚本中的 `stock_code` 变量：

```python
stock_code = "600519"  # 贵州茅台
stock_code = "000001"  # 平安银行
stock_code = "600000"  # 浦发银行
```

### 获取不同时间范围

修改 `start_date` 和 `end_date`：

```python
df = pro.daily(
    ts_code=f"{stock_code}.SZ", 
    start_date='20200101',  # 从2020年开始
    end_date='20241231'     # 到2024年结束
)
```

### 批量获取多只股票

创建循环：

```python
stocks = ["300033", "600519", "000001"]

for code in stocks:
    df = pro.daily(ts_code=f"{code}.SZ", start_date='20160101', end_date='20260419')
    # 保存逻辑...
    time.sleep(1)  # 避免频繁调用
```

---

## 📞 技术支持

- **Tushare 官方文档**: https://tushare.pro/document/2
- **Tushare 社区**: https://tushare.pro/community
- **GitHub Issues**: https://github.com/waditu/tushare/issues

---

## 📝 更新日志

- **2026-04-19**: 初始版本
  - ✅ 支持 Tushare Pro API
  - ✅ 自动转换为 Kronos 格式
  - ✅ 完整的数据验证
  - ✅ 详细的错误提示

---

**祝您使用愉快！** 🎉
