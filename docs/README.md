# 📚 Kronos 文档

## 📖 使用指南

- [安装指南](guides/installation.md) - 环境配置和依赖安装
- [MPS GPU 训练](guides/mps_gpu_guide.md) - Apple Silicon GPU 加速训练
- [快速开始](guides/quick_start_mps.md) - 快速上手指南
- [训练继续](guides/training_continue.md) - 如何继续中断的训练
- [训练总结](guides/training_summary.md) - 训练过程和结果总结

## 🔧 开发文档

### API 参考

查看 [API 文档](api/)（待完善）

### 架构说明

- **model/**: 核心模型代码
  - `kronos.py`: Kronos 主模型
  - `tokenizer.py`: Tokenizer 实现
  - `predictor.py`: Predictor 实现

- **finetune/**: 微调模块
  - `train_tokenizer_mps.py`: MPS 专用训练脚本
  - `dataset.py`: 数据集处理
  - `config.py`: 配置管理

## 📝 教程

查看 [教程目录](tutorials/)（待完善）

## 🗂️ 归档文档

历史文档和临时笔记存放在 [archive/](archive/) 目录。

## 🔗 外部资源

- [Kronos GitHub](https://github.com/shiyu-coder/Kronos)
- [PyTorch MPS 文档](https://pytorch.org/docs/stable/notes/mps.html)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)

## 📞 获取帮助

如有问题，请：
1. 查阅相关指南
2. 检查 [archive](archive/) 中是否有类似问题
3. 提交 Issue
