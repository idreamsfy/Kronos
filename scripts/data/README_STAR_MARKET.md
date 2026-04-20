# 科创板股票数据下载工具

## 📋 简介

批量下载A股科创板（STAR Market）所有股票的历史行情数据，保存为Kronos训练格式。

**特点**:
- ✅ 使用掘金量化API
- ✅ 从CSV文件读取股票列表
- ✅ 生成Kronos训练格式CSV
- ✅ 支持断点续传
- ✅ 可配置下载参数

---

## 🚀 快速开始

### 1. 确保依赖已安装

掘金量化API应该已经在项目中配置好。

### 2. 测试运行（推荐先测试）

```bash
cd scripts/data
python test_star_market_download.py
```

这会下载前3只股票作为测试。

### 3. 全量下载

```bash
python batch_download_star_market.py
```

这将下载所有科创板股票（约600只）的过去5年数据。

---

## ⚙️ 配置说明

编辑 `batch_download_star_market.py` 的 `main()` 函数：

```python
batch_download_star_stocks(
    years=5,        # 下载年数（默认5年）
    delay=1,        # 请求间隔秒数（避免API限流）
    max_stocks=None # 最大下载数量（None=全部）
)
```

**测试模式示例**:
```python
max_stocks=10  # 只下载前10只
```

---

## 📁 输出文件

### 股票列表
- **位置**: `data/metadata/star_market_stocks_list_YYYYMMDD.csv`
- **格式**: CSV (code, name)

### 历史数据
- **位置**: `data/processed/kronos_SHSE_688xxx_daily_*.csv`
- **格式**: Kronos训练格式
- **列**: timestamps, open, close, high, low, volume, amount

---

## 💡 使用建议

1. **首次使用**: 先用测试模式验证
2. **网络稳定**: 确保网络连接稳定
3. **耐心等待**: 全量下载约需20-30分钟（600只股票 × 2秒间隔）
4. **断点续传**: 可以安全中断后重新运行
5. **定期更新**: 每月运行一次更新数据

---

## 🔧 常见问题

### Q: 下载失败怎么办？
A: 检查网络连接，确认掘金量化Token配置正确，重新运行即可（会跳过已下载的文件）

### Q: 如何加快下载速度？
A: 减小delay参数（如1秒），但要注意API限流风险

### Q: 数据保存在哪里？
A: `data/processed/` 目录

### Q: 如何验证数据？
A: 查看生成的CSV文件，确认有7列且数据完整

### Q: Token在哪里配置？
A: 在脚本开头的 `GM_TOKEN` 变量中配置

---

## 📖 详细文档

查看完整指南: [STAR_MARKET_DOWNLOAD_GUIDE.md](../../docs/guides/STAR_MARKET_DOWNLOAD_GUIDE.md)

---

## 🔗 相关工具

- [银行股下载](batch_download_bank_stocks.py) - 下载银行股票数据
- [数据兼容性检查](check_data_compatibility.py) - 验证数据格式

---

**创建时间**: 2026-04-19  
**版本**: 2.0 (掘金量化版)  
**依赖**: 掘金量化API (gm.api)
