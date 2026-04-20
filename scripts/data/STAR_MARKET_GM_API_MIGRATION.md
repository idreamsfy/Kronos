# 科创板数据下载工具 - 掘金量化版

## ✅ 修改完成

已将科创板股票数据下载工具从AKShare改为使用**掘金量化API**。

---

## 🔄 主要变更

### 1. API接口更换
- ❌ **之前**: AKShare (免费，但稳定性较差)
- ✅ **现在**: 掘金量化API (稳定，与银行股下载一致)

### 2. 数据获取方式
- ❌ **之前**: 动态获取股票列表
- ✅ **现在**: 从CSV文件读取股票列表（更可靠）

### 3. Token配置
```python
GM_TOKEN = 'cabb19a30fc311ec977252560acd7b8ecabb19a4'
set_token(GM_TOKEN)
```

---

## 📝 修改的文件

### 1. [batch_download_star_market.py](file://d:\workspace\Kronos\scripts\data\batch_download_star_market.py)
**主要变更**:
- ✅ 导入 `from gm.api import *`
- ✅ 添加Token配置
- ✅ 新增 `load_star_stocks_list()` 函数
- ✅ 简化 `get_star_market_stocks()` 为备用方法
- ✅ 修改 `download_single_stock()` 使用掘金API
- ✅ 更新 `batch_download_star_stocks()` 逻辑
- ✅ 调整delay为2秒（与银行股一致）

### 2. [test_star_market_download.py](file://d:\workspace\Kronos\scripts\data\test_star_market_download.py)
**主要变更**:
- ✅ 更新注释说明使用掘金API
- ✅ 调整delay为2秒

### 3. [README_STAR_MARKET.md](file://d:\workspace\Kronos\scripts\data\README_STAR_MARKET.md)
**主要变更**:
- ✅ 更新特性说明
- ✅ 移除AKShare安装说明
- ✅ 更新预计时间（20-30分钟）
- ✅ 添加Token配置说明
- ✅ 版本号更新为2.0

---

## 🎯 核心功能对比

| 功能 | AKShare版 | 掘金量化版 |
|------|-----------|-----------|
| **数据来源** | AKShare免费API | 掘金量化API |
| **股票列表** | 动态获取 | CSV文件读取 |
| **稳定性** | 一般 | 高 |
| **速度** | 快（1秒间隔） | 中（2秒间隔） |
| **Token** | 不需要 | 需要配置 |
| **一致性** | 与银行股不同 | 与银行股相同 |
| **维护性** | 依赖外部API | 项目内统一管理 |

---

## 🚀 使用方法

### 测试模式
```bash
cd scripts/data
python test_star_market_download.py
```

### 全量下载
```bash
python batch_download_star_market.py
```

### 配置参数
在 `main()` 函数中修改：
```python
batch_download_star_stocks(
    years=5,        # 下载年数
    delay=2,        # 请求间隔（秒）
    max_stocks=None # None=全部
)
```

---

## 📊 技术细节

### 数据获取流程
1. **加载股票列表**: 从 `data/metadata/star_market_stocks_list_*.csv` 读取
2. **如果不存在**: 生成688000-688599代码列表
3. **保存列表**: 自动生成CSV文件
4. **逐个下载**: 使用掘金API获取历史数据
5. **格式转换**: 转换为Kronos训练格式
6. **保存文件**: 保存到 `data/processed/`

### 掘金API调用
```python
history_data = history(
    symbol=symbol,           # SHSE.688001
    frequency='1d',          # 日线
    start_time='2021-04-19', # 开始日期
    end_time='2026-04-19',   # 结束日期
    fill_missing='last',     # 填充缺失值
    df=True                  # 返回DataFrame
)
```

### 数据列映射
```python
kronos_columns = {
    'eob': 'timestamps',
    'open': 'open',
    'close': 'close',
    'high': 'high',
    'low': 'low',
    'volume': 'volume',
    'amount': 'amount',
}
```

---

## ⚙️ 配置文件

### Token配置
位置: `batch_download_star_market.py` 第17行
```python
GM_TOKEN = 'cabb19a30fc311ec977252560acd7b8ecabb19a4'
```

### 股票列表
位置: `data/metadata/star_market_stocks_list_YYYYMMDD.csv`

格式:
```csv
code,name
688001,华兴源创
688002,睿创微纳
...
```

---

## 💡 优势

### 相比AKShare版本
1. ✅ **更稳定**: 掘金API稳定性更高
2. ✅ **更统一**: 与银行股下载使用相同API
3. ✅ **更易维护**: 项目内统一管理
4. ✅ **更可靠**: 不受外部API变化影响
5. ✅ **断点续传**: 自动跳过已下载文件

### 性能
- **下载速度**: ~2秒/只股票
- **总时间**: 600只 × 2秒 = 约20-30分钟
- **成功率**: 预计 >95%

---

## 🔧 注意事项

1. **Token有效性**: 确保Token未过期
2. **网络连接**: 保持稳定网络连接
3. **磁盘空间**: 预留至少100MB
4. **中断恢复**: 可以安全中断后继续
5. **文件覆盖**: 已存在的文件会被跳过

---

## 📈 预期输出

### 成功示例
```
[1/600] 科创板688001 (SHSE.688001)
   ✅ 保存成功: 1200条记录, 85.3KB

[2/600] 科创板688002 (SHSE.688002)
   ✅ 保存成功: 1180条记录, 83.7KB
...
```

### 统计信息
```
批量下载完成！
================================================================================

统计信息:
  - 总计: 600 只
  - 成功: 580 只 ✅
  - 失败: 10 只 ❌
  - 跳过: 10 只 ⏭️

成功率: 96.7%
```

---

## 📖 相关文档

- [快速参考](file://d:\workspace\Kronos\scripts\data\README_STAR_MARKET.md)
- [详细指南](file://d:\workspace\Kronos\docs\guides\STAR_MARKET_DOWNLOAD_GUIDE.md)
- [银行股下载](file://d:\workspace\Kronos\scripts\data\batch_download_bank_stocks.py)

---

## 🎉 总结

✅ **已完成**: 科创板数据下载工具已成功迁移到掘金量化API  
✅ **一致性**: 与银行股下载工具保持一致  
✅ **可靠性**: 更高的稳定性和可维护性  
✅ **易用性**: 使用方式简单，支持断点续传  

现在可以使用统一的掘金量化API下载所有A股数据！🚀
