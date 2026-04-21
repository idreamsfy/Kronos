# 📊 Futu API（富途牛牛）数据获取指南

## 🎯 概述

Futu API 是富途牛牛提供的量化交易接口，可以获取高质量的 A 股、港股、美股行情数据。

---

## ⚙️ 前置要求

### 1. 安装 FutuOpenD

**下载地址**: https://www.futunn.com/download/openAPI

**支持平台**:
- ✅ Windows
- ✅ macOS
- ✅ Linux

### 2. 注册富途牛牛账号

1. 访问: https://www.futunn.com/
2. 注册账号并完成实名认证
3. 下载并安装富途牛牛客户端

### 3. 配置 FutuOpenD

**macOS 配置步骤**:

```bash
# 1. 解压下载的 FutuOpenD
unzip FutuOpenD_macOS.zip

# 2. 启动 FutuOpenD
./FutuOpenD

# 3. 使用富途牛牛 APP 扫码登录

# 4. 确认监听端口（默认 11111）
```

**Windows 配置步骤**:

1. 运行 `FutuOpenD.exe`
2. 使用富途牛牛 APP 扫码登录
3. 确认端口设置为 11111

---

## 🚀 使用脚本获取数据

### 运行脚本

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python tests/fetch_300033_futu.py
```

### 预期输出

如果 FutuOpenD 正常运行，将看到：

```
======================================================================
使用 Futu API（富途牛牛）获取股票 300033（同花顺）数据
======================================================================

配置信息:
  - 股票代码: SZ.300033
  - 时间范围: 2016-04-21 至 2026-04-19
  - 输出文件: ./akshare_data/daily_300033.csv

初始化 Futu API 客户端...
✅ 客户端初始化成功

正在获取K线数据...
✅ 成功获取 1000 条记录
已获取 1000 条，继续获取更多...
✅ 成功获取 1000 条记录
...

总共获取 2500 条记录

转换数据格式...

✅ 数据已成功保存至: ./akshare_data/daily_300033.csv

数据统计:
  - 记录数: 2500
  - 时间范围: 2016-08-09 至 2026-04-19
  - 收盘价范围: ¥XX.XX - ¥XX.XX
  ...

✅ 完成！数据符合 Kronos 训练要求
```

---

## ❌ 当前问题

### 连接失败

```
Connect fail: conn=0(1); msg=ECONNREFUSED
```

**原因**: FutuOpenD 未启动或未正确配置

**解决步骤**:

1. **下载 FutuOpenD**
   ```
   https://www.futunn.com/download/openAPI
   ```

2. **安装并启动**
   ```bash
   # macOS
   chmod +x FutuOpenD
   ./FutuOpenD
   
   # Windows
   # 双击 FutuOpenD.exe
   ```

3. **登录**
   - 打开富途牛牛 APP
   - 扫描 FutuOpenD 显示的二维码
   - 完成登录

4. **验证端口**
   ```bash
   # 检查 11111 端口是否监听
   lsof -i :11111  # macOS/Linux
   netstat -an | findstr 11111  # Windows
   ```

5. **重新运行脚本**
   ```bash
   python tests/fetch_300033_futu.py
   ```

---

## 💡 Futu API 优势

### 优点

1. **数据质量高**
   - 官方数据源
   - 实时性强
   - 历史数据完整

2. **功能丰富**
   - 支持 A 股、港股、美股
   - 提供 Level2 行情
   - 支持交易接口

3. **免费使用**
   - 基础功能免费
   - 无需积分或付费

4. **稳定性好**
   - 官方维护
   - 文档完善
   - 社区活跃

### 缺点

1. **需要安装额外软件**
   - 必须运行 FutuOpenD
   - 占用系统资源

2. **需要账号**
   - 需要注册富途牛牛
   - 需要实名认证

3. **依赖本地服务**
   - FutuOpenD 必须保持运行
   - 网络中断会影响使用

---

## 🔧 高级配置

### 修改端口

如果默认端口 11111 被占用，可以修改：

**编辑 FutuOpenD 配置文件**:
```json
{
  "listen_port": 11111,
  "api_key": "",
  "rsa_private_key": ""
}
```

**修改脚本中的端口**:
```python
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11112)  # 改为新端口
```

### 远程连接

如果 FutuOpenD 运行在其他机器上：

```python
quote_ctx = OpenQuoteContext(host='192.168.1.100', port=11111)
```

---

## 📊 数据格式

### Futu API 返回字段

| 字段名 | 说明 | 示例 |
|--------|------|------|
| time_key | 时间戳 | 2024-01-01 09:30:00 |
| open | 开盘价 | 15.23 |
| high | 最高价 | 15.89 |
| low | 最低价 | 15.12 |
| close | 收盘价 | 15.67 |
| volume | 成交量 | 1234567 |
| turnover | 成交额 | 19345678.90 |
| pe_ratio | 市盈率 | 25.6 |
| turnover_rate | 换手率 | 0.05 |

### 转换为 Kronos 格式

脚本会自动转换为：
```csv
timestamps,open,high,low,close,volume,amount
2024-01-01,15.23,15.89,15.12,15.67,1234567,19345678.90
```

---

## 🎯 获取其他股票

修改脚本中的 `stock_code`：

```python
# A 股
stock_code = "SZ.000001"  # 平安银行
stock_code = "SH.600519"  # 贵州茅台

# 港股
stock_code = "HK.00700"   # 腾讯控股

# 美股
stock_code = "US.AAPL"    # 苹果
stock_code = "US.TSLA"    # 特斯拉
```

---

## 📝 常见问题

### Q1: FutuOpenD 启动失败

**解决**:
- 检查是否有其他程序占用 11111 端口
- 确保有执行权限（macOS: `chmod +x FutuOpenD`）
- 查看日志文件排查错误

### Q2: 扫码登录失败

**解决**:
- 确保富途牛牛 APP 是最新版本
- 检查网络连接
- 重启 FutuOpenD 后重试

### Q3: 获取数据为空

**解决**:
- 检查股票代码格式是否正确
- 确认市场代码（SZ/SH/HK/US）
- 检查时间范围是否合理

### Q4: 连接超时

**解决**:
- 检查防火墙设置
- 确认 FutuOpenD 正在运行
- 检查端口是否正确

---

## 🔗 相关资源

- **Futu API 官方文档**: https://openapi.futunn.com/futu-api-doc/
- **GitHub**: https://github.com/FutunnOpen/futu-api
- **社区论坛**: https://www.futunn.com/community
- **Python SDK**: `pip install futu-api`

---

## 📞 技术支持

如遇到问题：

1. 查看 FutuOpenD 日志文件
2. 检查官方文档
3. 在 GitHub 提交 Issue
4. 联系富途客服

---

**最后更新**: 2026年4月19日  
**Futu API 版本**: 10.3.6308  
**Python 版本**: 3.13
