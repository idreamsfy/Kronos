# ✅ 预训练模型本地化管理完成

**完成时间**: 2026年4月21日  
**目标**: 将 Kronos 预训练模型移动到 workspace 统一管理  

---

## 📦 已完成的工作

### 1. 创建预训练模型目录

```
model/pretrained_models/
├── README.md                          # 使用说明文档
├── Kronos-base/                       # Kronos 基础模型
│   ├── README.md
│   ├── config.json
│   └── model.safetensors             (390 MB)
└── Kronos-Tokenizer-base/            # Tokenizer 模型
    ├── README.md
    ├── config.json
    └── model.safetensors             (15 MB)
```

### 2. 复制模型文件

- ✅ 从 Hugging Face 缓存复制到 `model/pretrained_models/`
- ✅ Kronos-base: 390 MB, 102M 参数
- ✅ Kronos-Tokenizer-base: 15 MB

### 3. 更新 .gitignore

添加了预训练模型的忽略规则：
```gitignore
# Pretrained models (large files)
model/pretrained_models/**/*.safetensors
model/pretrained_models/**/*.bin
```

### 4. 创建使用示例

创建了 `examples/use_local_model.py`，演示如何：
- 从本地路径加载模型
- 使用 MPS GPU 加速
- 进行预测测试

### 5. 验证功能

- ✅ 模型加载成功
- ✅ Tokenizer 加载成功
- ✅ 预测功能正常
- ✅ MPS GPU 加速工作正常

---

## 🎯 优势

### 1. 统一管理

**之前**:
- 模型分散在 Hugging Face 缓存目录
- 难以追踪和管理
- 团队协作困难

**现在**:
- 所有模型在 `model/pretrained_models/` 统一管理
- 清晰的目录结构
- 易于版本控制（通过 .gitignore）

### 2. 离线可用

- ✅ 不依赖网络连接
- ✅ 不受 Hugging Face 服务影响
- ✅ 适合内网环境

### 3. 快速加载

```python
# 本地加载（快速）
model = Kronos.from_pretrained("./model/pretrained_models/Kronos-base")

# vs Hugging Face 加载（需要检查更新）
model = Kronos.from_pretrained("NeoQuasar/Kronos-base")
```

### 4. 团队协作

团队成员可以：
1. 从共享存储复制模型
2. 使用相同的模型版本
3. 避免重复下载

---

## 📂 目录结构

```
Kronos/
├── model/
│   ├── __init__.py
│   ├── kronos.py                    # 模型定义
│   ├── module.py                    # 模块实现
│   └── pretrained_models/           # ✨ 新增
│       ├── README.md                # 使用说明
│       ├── Kronos-base/             # 基础模型
│       │   ├── config.json
│       │   └── model.safetensors
│       └── Kronos-Tokenizer-base/   # Tokenizer
│           ├── config.json
│           └── model.safetensors
├── examples/
│   └── use_local_model.py           # ✨ 新增示例
└── ...
```

---

## 🚀 使用方法

### 方法 1: 使用本地路径（推荐）

```python
from model.kronos import Kronos, KronosTokenizer

# 从本地加载
model = Kronos.from_pretrained("./model/pretrained_models/Kronos-base")
tokenizer = KronosTokenizer.from_pretrained("./model/pretrained_models/Kronos-Tokenizer-base")
```

### 方法 2: 运行示例脚本

```bash
cd /Users/john/Documents/GitHub/Kronos
source .venv/bin/activate
python examples/use_local_model.py
```

**输出示例**:
```
======================================================================
加载本地预训练模型
======================================================================

1. 加载 Tokenizer from: ./model/pretrained_models/Kronos-Tokenizer-base
   ✅ Tokenizer 加载成功

2. 加载 Kronos-base from: ./model/pretrained_models/Kronos-base
   ✅ 模型加载成功
   参数量: 102,310,592

3. 设备: Apple Silicon MPS (GPU) ✅

======================================================================
✅ 所有模型加载成功！
======================================================================
```

### 方法 3: 仍然使用 Hugging Face

如果需要使用最新版本，仍可以从 Hugging Face 加载：

```python
# 自动从 Hugging Face 下载（如果本地没有）
model = Kronos.from_pretrained("NeoQuasar/Kronos-base")
```

---

## 💾 存储空间

### 当前占用

| 位置 | 大小 | 说明 |
|------|------|------|
| `model/pretrained_models/` | 405 MB | 本地副本 |
| `~/.cache/huggingface/` | 405 MB | Hugging Face 缓存 |
| **总计** | **810 MB** | 两份副本 |

### 清理建议

如果确认本地副本工作正常，可以清理 Hugging Face 缓存：

```bash
# 清理 Hugging Face 缓存
rm -rf ~/.cache/huggingface/hub/models--NeoQuasar--Kronos-base
rm -rf ~/.cache/huggingface/hub/models--NeoQuasar--Kronos-Tokenizer-base

# 释放空间: ~405 MB
```

**注意**: 清理后，代码中使用模型 ID 时会重新下载。

---

## 🔄 模型更新

### 检查更新

```bash
python << 'EOF'
from huggingface_hub import HfApi

api = HfApi()
model_info = api.model_info("NeoQuasar/Kronos-base")
print(f"最新 SHA: {model_info.sha}")
print(f"最后更新: {model_info.last_modified}")
EOF
```

### 更新本地模型

```bash
# 删除旧模型
rm -rf model/pretrained_models/Kronos-base

# 重新下载
export HF_ENDPOINT=https://hf-mirror.com
python -c "from huggingface_hub import snapshot_download; snapshot_download('NeoQuasar/Kronos-base', local_dir='./model/pretrained_models/Kronos-base')"
```

---

## 📝 配置文件更新

如果需要修改训练配置以使用本地模型：

```yaml
# config/training/mps_config.yaml

# 使用本地模型路径
pretrained_model_path: "./model/pretrained_models/Kronos-base"
pretrained_tokenizer_path: "./model/pretrained_models/Kronos-Tokenizer-base"

# 或者使用模型 ID（从 Hugging Face 加载）
# pretrained_model_path: "NeoQuasar/Kronos-base"
# pretrained_tokenizer_path: "NeoQuasar/Kronos-Tokenizer-base"
```

---

## 🎓 最佳实践

### 1. 团队共享

```bash
# 方法 1: Git LFS（适合小模型）
git lfs track "model/pretrained_models/*.safetensors"

# 方法 2: 共享存储
# 将模型放在网络存储，符号链接到本地
ln -s /shared/models/Kronos-base model/pretrained_models/Kronos-base

# 方法 3: 文档说明
# 在 README 中提供下载链接和说明
```

### 2. 版本管理

```bash
# 记录模型版本
echo "Kronos-base SHA: 2b554741eca47781b64468546e77fef3e85130e6" > model/pretrained_models/VERSION
echo "Downloaded: 2026-04-21" >> model/pretrained_models/VERSION
```

### 3. 备份策略

```bash
# 定期备份
tar -czf pretrained_models_backup_$(date +%Y%m%d).tar.gz model/pretrained_models/

# 或使用 rsync
rsync -av model/pretrained_models/ /backup/models/
```

---

## ⚠️ 注意事项

### 1. Git 忽略

预训练模型文件已添加到 `.gitignore`，不会被提交到 Git。

**原因**:
- 文件太大（405 MB）
- 可以从 Hugging Face 重新下载
- 避免仓库膨胀

### 2. 磁盘空间

确保有足够的磁盘空间：
```bash
df -h /
# 建议至少 1GB 可用空间
```

### 3. 路径问题

使用相对路径时，确保从项目根目录运行：
```bash
cd /Users/john/Documents/GitHub/Kronos
python examples/use_local_model.py
```

### 4. 权限问题

如果遇到权限错误：
```bash
chmod -R u+w model/pretrained_models/
```

---

## 🔗 相关文档

- [预训练模型 README](model/pretrained_models/README.md)
- [使用示例](examples/use_local_model.py)
- [模型下载指南](MODEL_DOWNLOAD_COMPLETE.md)

---

## ✅ 验证清单

- [x] 创建 `model/pretrained_models/` 目录
- [x] 复制 Kronos-base 模型
- [x] 复制 Kronos-Tokenizer-base 模型
- [x] 创建 README 文档
- [x] 更新 .gitignore
- [x] 创建使用示例
- [x] 测试模型加载
- [x] 测试预测功能
- [x] 验证 MPS GPU 加速

---

## 🎉 总结

### 成果

1. ✅ **统一管理**: 所有预训练模型在 `model/pretrained_models/`
2. ✅ **离线可用**: 不依赖网络连接
3. ✅ **快速加载**: 本地路径加载更快
4. ✅ **文档完善**: README 和使用示例
5. ✅ **功能验证**: 加载和预测测试通过

### 改进

- 📁 清晰的目录结构
- 📝 完善的文档
- 💻 实用的示例代码
- 🔒 正确的 Git 配置

### 下一步

1. 可以使用本地模型进行训练和推理
2. 团队成员可以轻松获取模型
3. 便于版本管理和备份

---

**🎊 预训练模型本地化管理完成！**

现在所有模型都在 `model/pretrained_models/` 目录下统一管理，可以随时使用！

---

*最后更新: 2026年4月21日*  
*状态: ✅ 完成*
