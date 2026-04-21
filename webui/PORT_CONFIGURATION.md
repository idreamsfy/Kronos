# ⚠️ 端口配置说明

**更新时间**: 2026年4月21日  
**问题**: 5000 端口被 macOS 系统占用  

---

## 🔍 问题描述

在 macOS 上，端口 **5000** 被系统进程 `ControlCenter` 占用，导致 Flask 应用无法在该端口启动。

### 错误症状

```bash
# 检查 5000 端口
lsof -i :5000

# 输出:
COMMAND     PID USER   FD   TYPE             DEVICE SIZE/OFF NODE NAME
ControlCe   797 john   11u  IPv4 ... TCP *:commplex-main (LISTEN)
```

**ControlCenter** 是 macOS 的控制中心服务，它默认监听 5000 端口。

---

## ✅ 解决方案

### 方案 1: 使用其他端口（推荐）

已将 Web UI 端口更改为 **8080**。

**访问地址**:
```
http://localhost:8080
```

**修改位置**:
- `webui/app.py`: `app.run(debug=True, host='0.0.0.0', port=8080)`
- `webui/start.sh`: 提示信息更新为 8080

### 方案 2: 禁用 macOS AirPlay 接收器

如果必须使用 5000 端口，可以禁用 AirPlay 接收器：

1. 打开 **系统设置** > **通用** > **AirDrop 与接力**
2. 关闭 **AirPlay 接收器**
3. 重启电脑

**注意**: 这会影响 AirPlay 功能。

### 方案 3: 使用其他常用端口

可用的替代端口：
- **8080** ✅ (当前使用)
- **3000** (常用于开发)
- **8000** (Django 默认)
- **9000** (不常用)

---

## 🌐 当前配置

### Web UI 端口

| 项目 | 值 |
|------|-----|
| **端口** | 8080 |
| **本地访问** | http://localhost:8080 |
| **局域网访问** | http://192.168.31.137:8080 |
| **协议** | HTTP |

### 服务器信息

```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8080
 * Running on http://192.168.31.137:8080
```

---

## 🔧 如何更改端口

### 方法 1: 修改 app.py

编辑 `webui/app.py` 最后一行：

```python
# 将端口改为任意可用端口
app.run(debug=True, host='0.0.0.0', port=8080)  # 改为 3000, 8000 等
```

### 方法 2: 命令行指定

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python webui/app.py --port 3000
```

需要修改 app.py 支持参数：

```python
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    
    app.run(debug=True, host='0.0.0.0', port=args.port)
```

### 方法 3: 环境变量

```bash
export FLASK_PORT=3000
python webui/app.py
```

需要在代码中读取：

```python
import os
port = int(os.environ.get('FLASK_PORT', 8080))
app.run(debug=True, host='0.0.0.0', port=port)
```

---

## 📊 端口占用检查

### 检查特定端口

```bash
# 检查 8080 端口
lsof -i :8080

# 检查 5000 端口
lsof -i :5000

# 查看所有 Python 进程
lsof -i | grep Python
```

### 查找可用端口

```bash
# 扫描常用端口
for port in 3000 5000 8000 8080 9000; do
    if ! lsof -i :$port > /dev/null 2>&1; then
        echo "Port $port is available"
    else
        echo "Port $port is in use"
    fi
done
```

---

## 🛡️ 防火墙配置

### macOS 防火墙

如果从其他设备无法访问，检查防火墙设置：

1. **系统设置** > **网络** > **防火墙**
2. 确保允许 Python 或 Flask 应用
3. 或临时关闭防火墙测试

### 允许外部访问

Flask 已配置为监听所有接口：
```python
app.run(host='0.0.0.0', port=8080)
```

**host='0.0.0.0'** 表示接受所有网络接口的连接。

---

## 🔗 相关资源

- [Flask 部署文档](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [macOS 端口冲突](https://developer.apple.com/forums/thread/682332)
- [常用端口列表](https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers)

---

## 📝 总结

### 问题原因
- macOS ControlCenter 占用 5000 端口
- 用于 AirPlay 接收器功能

### 解决方案
- ✅ 使用 8080 端口（已实施）
- 备选：3000, 8000, 9000 等

### 访问地址
- **本地**: http://localhost:8080
- **局域网**: http://192.168.31.137:8080

---

**提示**: 8080 是常用的 Web 开发端口，不会与系统服务冲突。

---

*最后更新: 2026年4月21日*
