# 🚀 Kronos Web UI 部署指南

**更新时间**: 2026年4月21日  
**版本**: v2.0 (支持本地模型)  

---

## 📋 概述

Kronos Web UI 是一个基于 Flask 的 Web 应用，提供：
- 📊 交互式股票数据可视化
- 🔮 AI 驱动的金融时序预测
- 🎯 支持多个 Kronos 模型（mini/small/base）
- 💻 本地模型支持（离线可用）
- ⚡ MPS GPU 加速（Apple Silicon）

---

## ✨ 新功能

### 1. 本地模型支持

现在默认使用本地预训练模型：
- ✅ **Kronos-base**: 102M 参数，本地路径 `./model/pretrained_models/Kronos-base`
- ✅ 无需网络连接
- ✅ 加载速度更快
- ✅ 适合生产环境

### 2. 自动设备检测

- 自动检测并使用 Apple Silicon MPS (GPU)
- 如果没有 MPS，回退到 CPU
- 支持手动选择设备

### 3. 多数据源支持

自动扫描以下目录的数据文件：
- `data/raw/akshare/` (新结构)
- `data/` (旧结构)
- `akshare_data/` (兼容)

---

## 🚀 快速启动

### 方法 1: 使用启动脚本（推荐）

```bash
cd /Users/john/Documents/GitHub/Kronos
./webui/start.sh
```

### 方法 2: 使用 Python

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python webui/run.py
```

### 方法 3: 直接运行 Flask

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
export FLASK_APP=webui/app.py
flask run --host=0.0.0.0 --port=5000
```

---

## 🌐 访问应用

启动后，在浏览器中访问：

```
http://localhost:8080
```

或者如果是远程服务器：

```
http://YOUR_SERVER_IP:8080
```

---

## 📦 依赖安装

如果还没有安装依赖：

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
pip install flask flask-cors plotly
```

或者使用 requirements 文件：

```bash
pip install -r webui/requirements.txt
```

---

## 🎯 使用流程

### 1. 启动应用

```bash
./webui/start.sh
```

**输出示例**:
```
======================================================================
🚀 Starting Kronos Prediction Web UI
======================================================================

✅ Environment check passed
✅ Model directory exists
✅ Data directory exists

 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

### 2. 打开浏览器

访问 `http://localhost:8080`

### 3. 加载模型

- 点击 "Load Model" 按钮
- 默认加载 **Kronos-base** (本地模型)
- 等待加载完成（约 5-10 秒）

**成功提示**:
```
✅ Model loaded successfully: Kronos-base (102.3M) on mps
Source: local
```

### 4. 选择数据

- 从下拉列表选择股票数据
- 或上传自定义 CSV 文件

**可用数据**:
- daily_300033.csv (同花顺)
- daily_000001.csv (平安银行)
- daily_600519.csv (贵州茅台)
- ...

### 5. 配置预测参数

- **Lookback Window**: 历史数据长度 (默认 100)
- **Prediction Length**: 预测天数 (默认 20)
- **Temperature**: 预测温度 (默认 1.0)
- **Top-p**: 采样参数 (默认 0.9)

### 6. 执行预测

点击 "Predict" 按钮，等待预测完成。

### 7. 查看结果

- 📈 K 线图显示历史和预测数据
- 📊 成交量和成交额图表
- 💾 可下载预测结果为 JSON

---

## ⚙️ 配置选项

### 模型配置

编辑 `webui/app.py` 中的 `AVAILABLE_MODELS`:

```python
AVAILABLE_MODELS = {
    'kronos-base': {
        'name': 'Kronos-base',
        'model_id': 'NeoQuasar/Kronos-base',
        'local_model_path': './model/pretrained_models/Kronos-base',  # 本地路径
        'local_tokenizer_path': './model/pretrained_models/Kronos-Tokenizer-base',
        'context_length': 512,
        'params': '102.3M',
        'description': 'Base model (Local)'
    }
}
```

### 服务器配置

编辑 `webui/run.py`:

```python
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',  # 监听所有接口
        port=5000,       # 端口号
        debug=True       # 调试模式
    )
```

---

## 🔧 故障排除

### 问题 1: 端口被占用

**错误**:
```
OSError: [Errno 48] Address already in use
```

**解决**:
```bash
# 查找占用端口的进程
lsof -i :5000

# 杀死进程
kill -9 <PID>

# 或使用不同端口
python webui/run.py --port 5001
```

### 问题 2: 模型加载失败

**错误**:
```
Model loading failed: No such file or directory
```

**解决**:
```bash
# 检查模型文件是否存在
ls -lh model/pretrained_models/Kronos-base/

# 如果不存在，重新下载
export HF_ENDPOINT=https://hf-mirror.com
python -c "from huggingface_hub import snapshot_download; snapshot_download('NeoQuasar/Kronos-base', local_dir='./model/pretrained_models/Kronos-base')"
```

### 问题 3: 数据文件未找到

**解决**:
```bash
# 检查数据目录
ls -lh data/raw/akshare/

# 确保有 CSV 文件
# 如果没有，获取数据
python scripts/data/fetch_futu.py
```

### 问题 4: MPS 不可用

**检查**:
```python
python -c "import torch; print(torch.backends.mps.is_available())"
```

**如果返回 False**:
- 确保使用 Apple Silicon Mac (M1/M2/M3)
- 更新 PyTorch 到最新版本
- 应用会自动回退到 CPU

---

## 📊 性能优化

### 1. 使用 MPS GPU

确保 MPS 启用：
```python
import torch
if torch.backends.mps.is_available():
    device = 'mps'
else:
    device = 'cpu'
```

### 2. 调整批次大小

对于大模型，减小批次大小以避免内存不足：
```python
# 在 app.py 中修改
predictor = KronosPredictor(model, tokenizer, device=device, max_context=512)
```

### 3. 缓存模型

模型加载后会在内存中缓存，后续预测无需重新加载。

---

## 🔒 安全建议

### 生产环境部署

1. **关闭调试模式**:
   ```python
   app.run(debug=False)
   ```

2. **使用 HTTPS**:
   ```bash
   # 使用 Nginx 反向代理
   # 或使用 Let's Encrypt 证书
   ```

3. **添加认证**:
   ```python
   from flask_httpauth import HTTPBasicAuth
   auth = HTTPBasicAuth()
   
   @auth.verify_password
   def verify_password(username, password):
       # 验证逻辑
   ```

4. **限制访问**:
   ```python
   # 只允许特定 IP
   @app.before_request
   def limit_remote_addr():
       if request.remote_addr not in ['127.0.0.1', 'YOUR_IP']:
           abort(403)
   ```

---

## 📁 目录结构

```
webui/
├── app.py                    # Flask 应用主文件
├── run.py                    # 启动脚本
├── start.sh                  # Shell 启动脚本
├── requirements.txt          # Python 依赖
├── templates/
│   └── index.html           # Web 界面
├── prediction_results/      # 预测结果保存目录
└── DEPLOYMENT_GUIDE.md      # 本文档
```

---

## 🎓 高级用法

### API 调用

可以通过 REST API 进行预测：

```bash
# 加载模型
curl -X POST http://localhost:5000/api/load-model \
  -H "Content-Type: application/json" \
  -d '{"model_key": "kronos-base", "device": "mps"}'

# 执行预测
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "./data/raw/akshare/daily_300033.csv",
    "lookback": 100,
    "pred_len": 20,
    "temperature": 1.0,
    "top_p": 0.9
  }'
```

### 自定义模型

添加自己的微调模型：

```python
AVAILABLE_MODELS['my-finetuned'] = {
    'name': 'My Finetuned Model',
    'model_id': None,
    'local_model_path': './outputs/models/my_model',
    'local_tokenizer_path': './outputs/models/my_tokenizer',
    'context_length': 512,
    'params': '102.3M',
    'description': 'Custom finetuned model'
}
```

---

## 🔗 相关资源

- [Kronos GitHub](https://github.com/shiyu-coder/Kronos)
- [Hugging Face Models](https://huggingface.co/NeoQuasar)
- [Flask 文档](https://flask.palletsprojects.com/)
- [Plotly 文档](https://plotly.com/python/)

---

## 📞 获取帮助

如有问题，请：
1. 检查日志输出
2. 查看故障排除部分
3. 提交 Issue 到 GitHub

---

**祝您使用愉快！** 🎉

---

*最后更新: 2026年4月21日*  
*版本: v2.0*
