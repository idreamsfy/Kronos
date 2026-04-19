# A股银行股票批量数据下载工具

## 📋 概述

这个Python脚本用于批量下载所有A股银行股票的历史行情数据（过去10年），并保存为符合Kronos训练要求的CSV格式。

### 主要特性

✅ **自动化批量下载** - 一键下载所有34只银行股票  
✅ **Kronos标准格式** - 直接生成可用于训练的CSV文件  
✅ **智能跳过机制** - 自动检测已存在的文件，避免重复下载  
✅ **API限流保护** - 自动延迟避免触发API限制  
✅ **详细进度显示** - 实时显示下载状态和统计信息  
✅ **错误容错处理** - 单只股票失败不影响其他股票  

---

## 🚀 快速开始

### 前置条件

1. **安装依赖**
```bash
pip install gm pandas
```

2. **配置掘金量化Token**
   
   编辑 `tests/batch_download_bank_stocks.py` 文件第13行：
   ```python
   GM_TOKEN = 'your_token_here'
   ```

3. **获取银行股票列表**
```bash
python tests/get_bank_stocks_list.py
```

### 运行脚本

```bash
python tests/batch_download_bank_stocks.py
```

---

## 📊 输出文件格式

### 文件命名规范

```
kronos_{交易所}_{股票代码}_daily_{开始日期}_{结束日期}.csv
```

示例：
```
kronos_SHSE_600000_daily_2016-04-19_2026-04-19.csv
kronos_SHSE_601398_daily_2016-04-19_2026-04-19.csv
kronos_SZSE_000001_daily_2016-04-19_2026-04-19.csv
```

### CSV文件结构

```csv
timestamps,open,close,high,low,volume,amount
2016-04-19,9.85,9.90,9.95,9.82,45000000,445500000.00
2016-04-20,9.90,9.88,9.93,9.85,42000000,415800000.00
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

## 💡 使用场景

### 1. 完整批量下载（默认）

```bash
python tests/batch_download_bank_stocks.py
```

这将：
- 下载所有34只银行股票
- 时间跨度：10年
- 请求间隔：2秒
- 总耗时：约2-3分钟

### 2. 自定义下载参数

编辑脚本中的 `main()` 函数：

```python
if __name__ == '__main__':
    # 下载5年数据，间隔1秒
    batch_download_bank_stocks(years=5, delay=1)
    
    # 或下载15年数据，间隔3秒
    batch_download_bank_stocks(years=15, delay=3)
```

### 3. 下载单只股票

如果需要单独下载某只股票，可以使用现有的 `download_spdb_data.py` 作为模板修改。

---

## 📁 文件位置

### 输入文件
```
data/
└── bank_stocks_list_YYYYMMDD.csv  # 银行股票列表
```

### 输出文件
```
data/
├── kronos_SHSE_600000_daily_2016-04-19_2026-04-19.csv
├── kronos_SHSE_601398_daily_2016-04-19_2026-04-19.csv
├── kronos_SHSE_601939_daily_2016-04-19_2026-04-19.csv
├── kronos_SZSE_000001_daily_2016-04-19_2026-04-19.csv
└── ... (共34个文件)
```

### 预计文件大小
- 单只股票（10年）: ~130 KB
- 34只股票总计: ~4.4 MB

---

## 🔧 配置选项

### 修改下载年数

```python
# 在 batch_download_bank_stocks() 函数中
batch_download_bank_stocks(years=10)  # 改为需要的年数
```

### 调整API请求间隔

```python
# 避免触发API限流
batch_download_bank_stocks(delay=2)  # 增加延迟时间
```

### 更改输出目录

```python
# 在 download_single_stock() 函数中
output_dir = '/path/to/your/directory'
```

---

## 📈 执行流程

```
1. 加载银行股票列表
   └─> 读取 data/bank_stocks_list_*.csv

2. 遍历每只股票
   ├─> 检查文件是否已存在
   │   └─> 存在则跳过
   ├─> 调用掘金API获取数据
   ├─> 转换为Kronos格式
   ├─> 保存为CSV文件
   └─> 延迟等待（避免限流）

3. 生成统计报告
   └─> 显示成功/失败/跳过数量
```

---

## ⚙️ 控制台输出示例

```
================================================================================
批量下载A股银行股票历史数据 (Kronos格式)
================================================================================

配置信息:
  - 下载年数: 10年
  - 请求间隔: 2秒
  - 数据格式: Kronos训练格式
  - Token: cabb19a30fc311ec9772...
================================================================================

📂 读取银行股票列表: D:\workspace\Kronos\data\bank_stocks_list_20260419.csv
✅ 成功加载 34 只银行股票

开始批量下载 (34只股票)...
--------------------------------------------------------------------------------

[1/34] 工商银行 (SHSE.601398)
   ✅ 保存成功: 2435条记录, 128.5KB

[2/34] 建设银行 (SHSE.601939)
   ✅ 保存成功: 2435条记录, 128.3KB

[3/34] 农业银行 (SHSE.601288)
   ✅ 保存成功: 2435条记录, 128.7KB

...

[34/34] 东方财富 (SZSE.300059)
   ✅ 保存成功: 2435条记录, 129.1KB

================================================================================
批量下载完成！
================================================================================

统计信息:
  - 总计: 34 只
  - 成功: 34 只 ✅
  - 失败: 0 只 ❌
  - 跳过: 0 只 ⏭️

成功率: 100.0%

文件保存在: D:\workspace\Kronos\data
================================================================================

已生成的Kronos格式文件 (34个):
  - kronos_SHSE_600000_daily_2016-04-19_2026-04-19.csv       128.5 KB
  - kronos_SHSE_601398_daily_2016-04-19_2026-04-19.csv       128.3 KB
  ...
```

---

## ❓ 常见问题

### Q1: API限流怎么办？

**A**: 增加 `delay` 参数：
```python
batch_download_bank_stocks(years=10, delay=5)  # 增加到5秒
```

### Q2: 如何重新下载某只股票？

**A**: 删除对应的CSV文件后重新运行：
```bash
# Windows
del data\kronos_SHSE_600000_daily_*.csv

# Linux/Mac
rm data/kronos_SHSE_600000_daily_*.csv

# 然后重新运行
python tests/batch_download_bank_stocks.py
```

### Q3: 下载失败如何处理？

**A**: 
1. 检查网络连接
2. 验证Token是否有效
3. 查看错误信息
4. 单独测试失败的股票

### Q4: 可以中断后继续吗？

**A**: 可以！脚本会自动跳过已存在的文件，随时可以中断和恢复。

### Q5: 数据质量如何保证？

**A**: 
- ✅ 自动OHLC逻辑验证
- ✅ 空值检查
- ✅ 时间排序验证
- ✅ Kronos格式兼容性检查

---

## 🎯 与Kronos训练配合

### 1. 直接使用

生成的文件可直接用于Kronos训练：

```yaml
# config.yaml
data:
  data_path: "data/kronos_SHSE_600000_daily_2016-04-19_2026-04-19.csv"
  lookback_window: 60
  predict_window: 10
```

### 2. 批量训练

创建批处理脚本：

```python
import glob
import subprocess

# 获取所有Kronos格式文件
kronos_files = glob.glob('data/kronos_*_daily_*.csv')

for csv_file in kronos_files:
    print(f"\n训练: {csv_file}")
    
    # 创建配置文件
    config = f"""
data:
  data_path: "{csv_file}"
  lookback_window: 60
  predict_window: 10
  
training:
  tokenizer_epochs: 10
  basemodel_epochs: 5
  batch_size: 8
"""
    
    # 写入临时配置文件
    with open('temp_config.yaml', 'w') as f:
        f.write(config)
    
    # 运行训练
    subprocess.run([
        'python', 'finetune_csv/train_sequential.py',
        '--config', 'temp_config.yaml'
    ])
```

### 3. 数据合并

如果需要合并多只股票的数据：

```python
import pandas as pd
import glob

# 读取所有Kronos文件
files = glob.glob('data/kronos_*_daily_*.csv')
all_data = []

for f in files:
    df = pd.read_csv(f)
    # 从文件名提取股票代码
    code = f.split('_')[2]
    df['symbol'] = code
    all_data.append(df)

# 合并
combined_df = pd.concat(all_data, ignore_index=True)
combined_df.to_csv('data/all_banks_combined.csv', index=False)

print(f"合并完成: {len(combined_df)} 条记录")
```

---

## 📊 数据统计

### 当前版本
- **银行数量**: 34只
- **时间跨度**: 10年（2016-2026）
- **预计记录数**: ~2,435条/股票
- **总记录数**: ~82,790条
- **文件大小**: ~4.4 MB

### 覆盖率
- ✅ 大型商业银行（6家）
- ✅ 股份制商业银行（12家）
- ✅ 城市商业银行（10家）
- ✅ 农村商业银行（4家）
- ✅ 其他金融机构（2家）

---

## 🚀 性能优化建议

### 1. 并行下载（高级）

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_download():
    bank_stocks = load_bank_stocks_list()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for _, row in bank_stocks.iterrows():
            future = executor.submit(
                download_single_stock,
                row['full_symbol'],
                row['name'],
                years=10
            )
            futures.append(future)
        
        for future in futures:
            future.result()
```

⚠️ **注意**: 需要确认API是否支持并发请求

### 2. 增量更新

```python
# 只下载最近1年的新数据
batch_download_bank_stocks(years=1)
```

### 3. 缓存机制

```python
# 检查文件修改时间
import os.path
from datetime import datetime, timedelta

file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(filepath))
if file_age < timedelta(days=7):
    print("文件较新，跳过")
```

---

## 📝 注意事项

### ⚠️ API限制
- 掘金量化API可能有调用频率限制
- 建议设置合理的 `delay` 参数
- 监控API使用情况

### ⚠️ 数据质量
- 停牌期间可能无数据
- 新股上市时间较短
- 部分股票可能有数据缺失

### ⚠️ 存储空间
- 34只股票 × 10年 ≈ 4.4 MB
- 定期清理不需要的文件
- 考虑压缩存储

---

## 🔄 维护建议

### 定期更新
```bash
# 每月运行一次，获取最新数据
python tests/get_bank_stocks_list.py  # 更新股票列表
python tests/batch_download_bank_stocks.py  # 下载最新数据
```

### 数据备份
```bash
# 备份到云端或外部存储
cp data/kronos_*.csv backup/
```

### 版本管理
```bash
# 使用日期标记
mv data/kronos_*.csv data/archive/2026-04/
```

---

## 📞 技术支持

如有问题，请检查：
1. 掘金量化Token是否有效
2. 网络连接是否正常
3. Python环境是否正确
4. 参考掘金量化API文档

---

## 📄 相关文档

- [README_BANK_STOCKS_LIST.md](README_BANK_STOCKS_LIST.md) - 银行股票列表获取
- [DOWNLOAD_TOOL_IMPROVEMENT_SUMMARY.md](../DOWNLOAD_TOOL_IMPROVEMENT_SUMMARY.md) - 数据下载工具改进
- [DATA_COMPATIBILITY_REPORT.md](../DATA_COMPATIBILITY_REPORT.md) - 数据兼容性分析

---

**最后更新**: 2026-04-19  
**版本**: v1.0  
**维护者**: Kronos Project Team
