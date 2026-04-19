# 浦发银行历史行情数据

## 📊 数据说明

本目录包含浦发银行（SHSE.600000）的历史行情数据，使用AKShare免费API下载。

## 📁 文件列表

### 日线数据
- **文件名**: `SHSE_600000_浦发电行_daily_20210419_20260418.csv`
- **时间范围**: 2021-04-19 至 2026-04-17（约5年）
- **记录数**: 1,211 条
- **文件大小**: 123 KB
- **数据来源**: 东方财富网（通过AKShare）
- **复权方式**: 前复权（qfq）

## 📋 数据字段

| 字段名 | 说明 | 示例 |
|--------|------|------|
| symbol | 股票代码（含交易所） | SHSE.600000 |
| name | 股票名称 | 浦发银行 |
| date | 交易日期 | 2021-04-19 |
| 股票代码 | 纯数字代码 | 600000 |
| open | 开盘价 | 8.61 |
| close | 收盘价 | 8.64 |
| high | 最高价 | 8.70 |
| low | 最低价 | 8.51 |
| volume | 成交量（手） | 502039 |
| amount | 成交额（元） | 529864992.0 |
| amplitude | 振幅（%） | 2.21 |
| change_pct | 涨跌幅（%） | 0.47 |
| change_amount | 涨跌额 | 0.04 |
| turnover_rate | 换手率（%） | 0.17 |

## 📈 数据统计摘要

### 价格统计（5年）
- **最高价**: ¥14.39
- **最低价**: ¥5.58
- **平均收盘价**: ¥8.13
- **最新收盘价**: ¥9.86（2026-04-17）

### 成交量统计
- **总成交量**: 554,919,990 手
- **日均成交量**: 458,233 手
- **最大日成交量**: 2,095,882 手

## 💻 使用方法

### Python 读取示例

```python
import pandas as pd

# 读取CSV文件
df = pd.read_csv('data/SHSE_600000_浦发电行_daily_20210419_20260418.csv')

# 查看基本信息
print(f"数据形状: {df.shape}")
print(f"日期范围: {df['date'].min()} 至 {df['date'].max()}")
print(f"\n前5行数据:")
print(df.head())

# 基本统计分析
print(f"\n价格统计:")
print(df[['open', 'high', 'low', 'close']].describe())

# 计算移动平均线
df['MA5'] = df['close'].rolling(window=5).mean()
df['MA20'] = df['close'].rolling(window=20).mean()
df['MA60'] = df['close'].rolling(window=60).mean()

# 保存处理后的数据
df.to_csv('data/SHSE_600000_processed.csv', index=False, encoding='utf-8-sig')
```

### 可视化示例

```python
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 转换日期格式
df['date'] = pd.to_datetime(df['date'])

# 创建图表
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

# 绘制价格和均线
ax1.plot(df['date'], df['close'], label='收盘价', linewidth=1)
ax1.plot(df['date'], df['MA5'], label='MA5', linewidth=0.8, alpha=0.7)
ax1.plot(df['date'], df['MA20'], label='MA20', linewidth=0.8, alpha=0.7)
ax1.plot(df['date'], df['MA60'], label='MA60', linewidth=0.8, alpha=0.7)
ax1.set_ylabel('价格 (元)')
ax1.set_title('浦发银行 (SHSE.600000) 5年股价走势')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 绘制成交量
ax2.bar(df['date'], df['volume'], alpha=0.6, color='gray', label='成交量')
ax2.set_ylabel('成交量 (手)')
ax2.set_xlabel('日期')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 格式化x轴日期
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('figures/spdb_5year_chart.png', dpi=150, bbox_inches='tight')
plt.show()
```

## 🔄 更新数据

如需更新数据到最新日期，运行以下命令：

```bash
python tests/download_spdb_data_akshare.py
```

## 📝 注意事项

1. **数据复权**: 使用前复权数据，已考虑分红配股等因素
2. **交易日**: 仅包含实际交易日，不包含周末和节假日
3. **数据质量**: 数据来自公开API，建议在使用前进行验证
4. **更新频率**: 每个交易日收盘后可更新最新数据

## 🔗 相关资源

- **AKShare官网**: https://akshare.akfamily.xyz/
- **数据来源**: 东方财富网、新浪财经
- **Kronos项目**: 可使用此数据进行模型训练和回测

## 📞 问题反馈

如遇到数据下载或格式问题，请检查：
1. 网络连接是否正常
2. AKShare库是否安装: `pip install akshare`
3. 数据源网站是否可访问

---

**最后更新**: 2026-04-18  
**数据版本**: v1.0
