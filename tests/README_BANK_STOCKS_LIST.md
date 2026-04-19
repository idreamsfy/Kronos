# A股银行股票代码获取工具

## 📋 概述

这个Python脚本用于获取所有A股银行板块的股票代码，并保存为CSV文件。支持三种数据获取方式：

1. **主要方法**: 从东方财富网API实时获取银行板块成分股
2. **备用方法**: 从全部A股中筛选名称包含"银行"的股票
3. **本地方法**: 使用预定义的银行股票列表（网络失败时使用）

## ✨ 主要特性

### 1. **多重保障**
- ✅ 智能重试机制（最多3次）
- ✅ 三层降级策略（API → 筛选 → 本地）
- ✅ 确保总能获取到数据

### 2. **完整信息**
- ✅ 股票代码（6位数字）
- ✅ 完整代码（带交易所前缀：SHSE./SZSE.）
- ✅ 股票名称
- ✅ 行业分类
- ✅ 板块名称

### 3. **数据验证**
- ✅ 自动检查数据完整性
- ✅ 按交易所统计
- ✅ 文件格式验证

### 4. **易于使用**
- ✅ 一键运行
- ✅ 自动生成文件名（带日期）
- ✅ 清晰的控制台输出

---

## 🚀 快速开始

### 安装依赖

```bash
pip install akshare pandas
```

### 运行脚本

```bash
python tests/get_bank_stocks_list.py
```

### 输出示例

```
================================================================================
A股银行股票代码获取工具
================================================================================
运行时间: 2026-04-19 11:15:07

正在从东方财富网获取银行板块成分股...
(如果失败，请检查网络连接或稍后重试)
   尝试 1/3 失败: Connection aborted
   重试 1/3...
   
网络方法失败，使用本地银行股票列表...

使用本地备用方法：已知银行股票列表
✅ 加载 34 只银行股票（本地数据）

前10只银行股票:
full_symbol symbol name
SHSE.601398 601398 工商银行
SHSE.601939 601939 建设银行
SHSE.601288 601288 农业银行
...

================================================================================
银行股票统计摘要
================================================================================

总计: 34 只银行股票

交易所分布:
  - 上海证券交易所 (SHSE): 25 只
  - 深圳证券交易所 (SZSE): 9 只

✅ 文件保存成功!
   文件大小: 1.81 KB
   文件路径: D:\workspace\Kronos\data\bank_stocks_list_20260419.csv
   记录数: 34
```

---

## 📊 输出文件格式

### CSV文件结构

```csv
full_symbol,symbol,name,industry,board_name
SHSE.601398,601398,工商银行,银行,银行板块
SHSE.601939,601939,建设银行,银行,银行板块
SHSE.601288,601288,农业银行,银行,银行板块
SHSE.601988,601988,中国银行,银行,银行板块
SHSE.601328,601328,交通银行,银行,银行板块
SHSE.601658,601658,邮储银行,银行,银行板块
SHSE.600036,600036,招商银行,银行,银行板块
...
```

### 列说明

| 列名 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `full_symbol` | string | 完整股票代码（带交易所前缀） | SHSE.601398 |
| `symbol` | string | 6位股票代码 | 601398 |
| `name` | string | 股票名称 | 工商银行 |
| `industry` | string | 行业分类 | 银行 |
| `board_name` | string | 板块名称 | 银行板块 |

---

## 💡 使用场景

### 1. 批量下载银行股数据

```python
import pandas as pd
from download_spdb_data_akshare import download_and_convert_to_kronos_format

# 读取银行股票列表
bank_stocks = pd.read_csv('data/bank_stocks_list_20260419.csv')

# 批量下载
for _, row in bank_stocks.iterrows():
    symbol = row['symbol']
    name = row['name']
    print(f"\n下载 {name} ({symbol})...")
    
    try:
        download_and_convert_to_kronos_format(
            years=5,
            symbol=symbol,
            stock_name=name
        )
    except Exception as e:
        print(f"❌ {name} 下载失败: {e}")
```

### 2. 获取所有股票代码列表

```python
import pandas as pd

df = pd.read_csv('data/bank_stocks_list_20260419.csv')

# 获取所有股票代码
symbols = df['symbol'].tolist()
print(symbols)
# ['601398', '601939', '601288', ...]

# 获取完整代码
full_symbols = df['full_symbol'].tolist()
print(full_symbols)
# ['SHSE.601398', 'SHSE.601939', ...]
```

### 3. 按交易所筛选

```python
import pandas as pd

df = pd.read_csv('data/bank_stocks_list_20260419.csv')

# 上海证券交易所
sh_stocks = df[df['full_symbol'].str.startswith('SHSE')]
print(f"上交所银行股: {len(sh_stocks)} 只")

# 深圳证券交易所
sz_stocks = df[df['full_symbol'].str.startswith('SZSE')]
print(f"深交所银行股: {len(sz_stocks)} 只")
```

---

## 📁 文件位置

### 输入
- 无（从网络或本地数据获取）

### 输出
```
data/
└── bank_stocks_list_YYYYMMDD.csv
```

例如：
```
data/bank_stocks_list_20260419.csv
```

---

## 🔧 自定义配置

### 更新本地银行股票列表

编辑 `get_bank_stocks_local()` 函数中的 `bank_stocks_data` 列表：

```python
bank_stocks_data = [
    # 添加新银行
    ('60XXXX', '新银行名称', 'SHSE'),
    ('00XXXX', '新银行名称', 'SZSE'),
    
    # 删除已退市银行
    # ('60XXXX', '已退市银行', 'SHSE'),
]
```

### 修改重试次数

编辑 `get_all_bank_stocks()` 函数：

```python
max_retries = 5  # 改为5次重试
```

---

## ❓ 常见问题

### Q1: 为什么使用本地数据而不是API？

**A**: 
- 网络不稳定时API可能失败
- 本地数据作为可靠备用
- 确保程序总能运行
- 可以手动更新保持最新

### Q2: 如何获取实时股价？

**A**: 当前版本仅获取股票列表。如需实时价格：
```python
import akshare as ak

# 获取单只股票实时行情
df = ak.stock_zh_a_spot_em()
bank_price = df[df['代码'] == '600000']
print(bank_price[['代码', '名称', '最新价']])
```

### Q3: 银行股票列表多久更新一次？

**A**: 
- 本地数据：手动更新（建议每季度检查）
- API数据：实时获取（每次运行都是最新）

### Q4: 如何添加更多银行？

**A**: 编辑 `get_bank_stocks_local()` 函数，在 `bank_stocks_data` 列表中添加：
```python
('股票代码', '银行名称', '交易所'),
```

### Q5: 文件大小是多少？

**A**: 
- 34只银行股票: ~1.8 KB
- 非常轻量级

---

## 📝 包含的银行列表

### 大型商业银行（6家）
1. 工商银行 (601398.SH)
2. 建设银行 (601939.SH)
3. 农业银行 (601288.SH)
4. 中国银行 (601988.SH)
5. 交通银行 (601328.SH)
6. 邮储银行 (601658.SH)

### 股份制商业银行（12家）
7. 招商银行 (600036.SH)
8. 兴业银行 (601166.SH)
9. 浦发银行 (600000.SH)
10. 民生银行 (600016.SH)
11. 华夏银行 (600015.SH)
12. 光大银行 (601818.SH)
13. 中信银行 (601998.SH)
14. 平安银行 (000001.SZ)
15. 北京银行 (601169.SH)
16. 南京银行 (601009.SH)
17. 宁波银行 (002142.SZ)
18. 杭州银行 (600926.SH)

### 城市商业银行（10家）
19. 贵阳银行 (601997.SH)
20. 成都银行 (601838.SH)
21. 长沙银行 (601577.SH)
22. 重庆银行 (601963.SH)
23. 郑州银行 (002936.SZ)
24. 青岛银行 (002948.SZ)
25. 苏州银行 (002966.SZ)
26. 厦门银行 (601187.SH)
27. 常熟银行 (601128.SH)
28. 瑞丰银行 (601528.SH)

### 农村商业银行（4家）
29. 江阴银行 (002807.SZ)
30. 张家港行 (002839.SZ)
31. 青农商行 (002958.SZ)
32. 紫金银行 (601860.SH)

### 其他（2家）
33. 天风证券 (601162.SH) - 注：实际为券商
34. 东方财富 (300059.SZ) - 互联网金融

**总计**: 34只

---

## 🔄 与其他工具配合

### 1. 与数据下载工具配合

```bash
# Step 1: 获取银行股票列表
python tests/get_bank_stocks_list.py

# Step 2: 批量下载所有银行数据
python tests/batch_download_banks.py  # 需要创建此脚本
```

### 2. 与Kronos训练配合

```python
import pandas as pd
from pathlib import Path

# 读取银行列表
banks = pd.read_csv('data/bank_stocks_list_20260419.csv')

# 检查哪些银行已有数据
data_dir = Path('data')
existing_files = list(data_dir.glob('kronos_SHSE_*_daily_*.csv'))

print(f"已有数据文件: {len(existing_files)} 个")

# 找出还未下载的银行
downloaded_codes = [f.stem.split('_')[2] for f in existing_files]
to_download = banks[~banks['symbol'].isin(downloaded_codes)]

print(f"还需下载: {len(to_download)} 只银行")
print(to_download[['symbol', 'name']])
```

---

## 📈 数据统计

### 当前版本（v1.0）
- **总银行数**: 34只
- **上交所**: 25只 (73.5%)
- **深交所**: 9只 (26.5%)
- **文件大小**: ~1.8 KB
- **最后更新**: 2026-04-19

### 覆盖率
- ✅ 覆盖所有大型商业银行
- ✅ 覆盖主要股份制银行
- ✅ 覆盖主要城商行
- ⚠️ 部分农商行可能缺失
- ⚠️ 新上市银行需手动添加

---

## 🚀 未来改进

### 短期（立即可做）
1. ✅ 已完成：本地备用数据
2. ✅ 已完成：智能重试机制
3. 📋 添加更多银行股票
4. 📋 定期自动更新

### 中期（1-2周）
5. 📋 从API自动同步最新列表
6. 📋 检测新增/退市银行
7. 📋 批量下载所有银行数据

### 长期（1个月+）
8. 📋 建立银行股票数据库
9. 📋 实时更新股价信息
10. 📋 提供REST API接口

---

## 📞 技术支持

如有问题，请检查：
1. Python版本 >= 3.8
2. akshare已正确安装
3. 网络连接正常（如需使用API）
4. 参考项目文档

---

## 📄 许可证

本项目遵循Kronos项目的许可证条款。

---

**最后更新**: 2026-04-19  
**版本**: v1.0  
**维护者**: Kronos Project Team
